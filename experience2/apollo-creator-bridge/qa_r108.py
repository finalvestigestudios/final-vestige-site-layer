#!/usr/bin/env python3
"""R108 offline HTTP Chromium QA for the actual Apollo creator-bridge HTML.

A genuine browser test, but NOT WordPress/Assembler or production telemetry.
No downloads; --axe requires an already approved local bundle.
"""
import argparse
import hashlib
import json
import math
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "landing-preview.html"
WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
EXPECTED_NASA = (
    "https://www.nasa.gov/image-detail/apollo-1-crew-honored/",
    "https://www.nasa.gov/image-detail/amf-s67-15717/",
    "https://www.nasa.gov/image-detail/amf-s66-58038/",
    "https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/",
    "https://www.nasa.gov/image-detail/amf-s67-21294/",
    "https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/",
)

def check(ok, message):
    if not ok:
        raise AssertionError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--axe", type=Path, help="Approved, preinstalled axe-core JS bundle; never fetched at runtime")
    args = parser.parse_args()
    if args.axe:
        check(args.axe.is_file(), "axe bundle not found")
    from playwright.sync_api import sync_playwright  # intentional hard requirement
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    source = HTML.read_text(encoding="utf-8")
    for url in EXPECTED_NASA:
        check(source.count(url) == 1, "NASA source link changed or duplicated")
    check(source.count("data-fv-primary-cta") == 1, "primary CTA must be unique")
    check("<img" not in source and "<iframe" not in source, "external media is not cleared")

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}/landing-preview.html"
    receipts, metrics, screen = [], [], []
    axe_scans = []
    def checkpoint(stage):
        """Atomic partial QA receipt: no credentials, PII, or false PASS on failure."""
        safe = {"schema": "fv.apollo.creator_bridge.r110.partial.v1",
                "status": "INCOMPLETE_STAGING_HOLD", "stage": stage,
                "source_sha256": digest(HTML),
                "completed_modes": list(receipts), "completed_lab_trials": list(metrics),
                "screenshots": list(screen), "axe_scans": list(axe_scans),
                "merchant_orders": "NOT_OBSERVABLE",
                "hosted_wordpress": "NOT_TESTED"}
        final = out / "r110-partial-qa-receipt.json"
        temporary = out / "r110-partial-qa-receipt.tmp"
        temporary.write_text(json.dumps(safe, sort_keys=True, indent=2) + "\n", encoding="utf8")
        temporary.replace(final)
    checkpoint("STARTED")
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            for width in WIDTHS:
                for js in (False, True):
                    context = browser.new_context(viewport={"width": width, "height": 900},
                        java_script_enabled=js, is_mobile=width <= 390, has_touch=width <= 390,
                        reduced_motion="reduce")
                    page = context.new_page()
                    unintended = []
                    page.on("request", lambda req: unintended.append(req.url) if not req.url.startswith(f"http://127.0.0.1:{server.server_port}/") else None)
                    page.goto(base, wait_until="load")
                    label = f"{width}px js={js}"
                    check(not unintended, label + ": unexpected external requests")
                    check(page.locator("[data-fv-claim]").count() == 4, label + ": missing findings")
                    check(page.locator("table tbody tr").count() == 6, label + ": custody six-count")
                    check(page.locator("img,video,iframe,canvas,svg,picture").count() == 0, label + ": media present")
                    check(page.evaluate("document.documentElement.scrollWidth <= innerWidth + 2"), label + ": horizontal page overflow")
                    check(page.evaluate("() => {let a=[...document.querySelectorAll('[id]')].map(x=>x.id);return a.length===new Set(a).size}"), label + ": duplicate IDs")
                    primary = page.locator("[data-fv-primary-cta]")
                    check(primary.count() == 1 and primary.get_attribute("href") == "#classroom-preview",
                        label + ": missing or diverted primary free-exercise CTA")
                    check(page.locator("a[href*='payhip.com'], form, [data-fv-checkout]").count() == 0,
                        label + ": unverified purchase or lead action entered historical preview")
                    check(page.locator("[data-fv-lens]").is_visible() == js, label + ": no-JS progressive enhancement failed")
                    # Test ACTUAL navigation, not merely an href attribute. The only intended
                    # micro-action is a free evidence exercise; this is never a paid conversion.
                    if width <= 390 and js:
                        primary.tap()
                    else:
                        primary.focus()
                        primary.press("Enter")
                    page.wait_for_function("location.hash === '#classroom-preview'")
                    target = page.locator("#classroom-preview")
                    check(target.count() == 1 and target.locator("h2").count() == 1,
                        label + ": free evidence exercise destination missing")
                    # A fragment that scrolls but leaves focus in the hero is not a
                    # reliable keyboard and screen-reader evidence-to-exercise handoff.
                    check(target.get_attribute("tabindex") == "-1" and
                          target.evaluate("(e) => document.activeElement === e"),
                          label + ": fragment destination did not receive keyboard focus")
                    check(target.locator("a[href='#source-custody']").count() == 1,
                          label + ": the classroom activity has no return source trail")
                    check(target.evaluate("(e) => {const r=e.getBoundingClientRect();return r.top >= -4 && r.top < innerHeight}"),
                        label + ": CTA did not reveal destination in viewport")
                    # The native document destination must be meaningful without scripts.
                    check(target.locator("details").count() >= 2,
                        label + ": free source analysis or answer is missing")
                    receipt_action = "free_exercise_fragment_navigated_not_sale"
                    check(page.locator("#source-custody .table-scroll").get_attribute("tabindex") == "0",
                        label + ": mobile source register not keyboard-scrollable")
                    source_disclosure = page.locator("#source-custody details summary").first
                    source_disclosure.focus()
                    source_disclosure.press("Enter")
                    check(source_disclosure.evaluate("(x) => x.parentNode.open"),
                        label + ": NASA rights/source disclosure cannot open by keyboard")
                    check(page.locator("[data-fv-claim]:visible").count() == 4, label + ": initial evidence hidden")
                    summary = page.locator("#classroom-preview summary").first
                    summary.focus()
                    summary.press("Enter")
                    check(summary.evaluate("(x) => x.parentNode.open"), label + ": native keyboard disclosure failed")
                    if js:
                        limits = page.locator('[data-fv-mode="limit"]')
                        check(limits.evaluate("(x)=>x.getBoundingClientRect().height >= 44"), label + ": touch target too small")
                        if width <= 390: limits.tap()
                        else: limits.click()
                        check(page.locator("[data-fv-claim]:visible").count() == 2, label + ": limit lens wrong")
                        check(limits.get_attribute("aria-pressed") == "true", label + ": pressed state wrong")
                        reset = page.locator('[data-fv-mode="all"]')
                        reset.click()
                        check(page.locator("[data-fv-claim]:visible").count() == 4, label + ": lens reset failed")
                        if args.axe and width in (390, 1440):
                            page.add_script_tag(content=args.axe.read_text(encoding="utf8"))
                            faults = page.evaluate("""async () => (await axe.run(document.querySelector('main'),{
                                runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}
                              })).violations.map(x=>({id:x.id,impact:x.impact,nodes:x.nodes.length}))""")
                            check(not faults, label + ": axe violations " + str(faults))
                            axe_scans.append({"width": width, "violations": []})
                    if width in (320, 390, 1440):
                        filename = f"apollo-r108-{width}-{'js' if js else 'nojs'}.png"
                        page.screenshot(path=str(out / filename), full_page=True, animations="disabled")
                        screen.append({"name": filename, "sha256": digest(out / filename)})
                    receipts.append({"width": width, "javascript": js, "passed": True,
                        "first_party_action": receipt_action,
                        "merchant_order_verified": False, "external_requests": 0})
                    context.close()
                    checkpoint("RESPONSIVE_MODE_COMPLETED")
            # Separate repeated lab navs, no JS interception of reader content.
            for width in (390, 1440):
                for trial in (1, 2, 3):
                    ctx = browser.new_context(viewport={"width": width, "height": 900},
                        java_script_enabled=True, reduced_motion="reduce")
                    pg = ctx.new_page()
                    pg.add_init_script("""(() => {
                      window.__fvCLS=0;window.__fvLCP=null;
                      new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__fvCLS+=e.value})).observe({type:'layout-shift',buffered:true});
                      new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__fvLCP=e.startTime)).observe({type:'largest-contentful-paint',buffered:true});
                    })()""")
                    pg.goto(base, wait_until="load")
                    pg.wait_for_timeout(350)
                    result = pg.evaluate("({lcp_ms:window.__fvLCP,cls:window.__fvCLS})")
                    lcp, cls = result["lcp_ms"], result["cls"]
                    check(type(lcp) in (int,float) and math.isfinite(lcp) and 0 < lcp <= 2500,
                        "R108 LCP missing/exceeds unchanged 2500ms lab budget")
                    check(type(cls) in (int,float) and math.isfinite(cls) and 0 <= cls <= 0.1,
                        "R108 CLS missing/exceeds unchanged 0.1 lab budget")
                    metrics.append({"width": width, "trial": trial, "lcp_ms": lcp, "cls": cls})
                    ctx.close()
                    checkpoint("PERFORMANCE_TRIAL_COMPLETED")
            version = browser.version
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    result = {
      "schema": "fv.apollo.creator_bridge.r108.qa.v1", "release": "STAGING_HOLD",
      "chromium": version, "source_sha256": digest(HTML),
      "responsive_modes": receipts, "screenshots": screen,
      "lab_local_http": metrics, "axe_scans": axe_scans,
      "axe_status": "EXECUTED" if args.axe else "NOT_EXECUTED_NO_APPROVED_BUNDLE",
      "wordpress_assembler": "NOT_TESTED", "hosted_cwv": "NOT_TESTED",
      "checkout": "NO_MERCHANT_OFFER_CONFIGURED", "paid_orders": "NOT_OBSERVABLE",
      "photo_rights_cleared": 0, "deployment": "NOT_APPROVED",
    }
    check(len(receipts) == 14 and len(metrics) == 6 and len(screen) == 6,
          "R108 incomplete authoritative browser matrix")
    # Only the complete matrix may emit an authoritative acceptance receipt.
    (out / "r108-local-http-browser-receipt.json").write_text(
         json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    checkpoint("COMPLETE_MATRIX_STILL_STAGING_HOLD")
    print("R110-enhanced R108 browser: 14/14 CTA navigation modes, 6 local HTTP lab trials; release STAGING HOLD")
    return result

if __name__ == "__main__":
    main()
