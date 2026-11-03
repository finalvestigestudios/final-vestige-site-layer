#!/usr/bin/env python3
"""Apollo R79 real Chromium QA: source-custody interaction, 320-1920, axe and PDF.

Runs a local http fixture only; NOT a hosted WordPress or field-CWV audit.
No production writes or remote requests. Strict CI requires navigation and axe.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, Error as PlaywrightError

from build_nasa_gallery_r79 import render_html, validate

WIDTHS = (320, 390, 768, 1440, 1920)

def run(repo: Path, out: Path, axe: Path | None = None,
        chromium: str | None = None, require_navigation: bool = False, require_axe: bool = False) -> dict:
    assert len(validate(repo)) == 6
    markup = render_html(repo)
    out.mkdir(parents=True, exist_ok=True)
    if require_axe and (axe is None or not axe.is_file()):
        raise RuntimeError("R79_AXE_REQUIRED_BUT_MISSING")
    class Fixture(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/r79":
                self.send_error(404)
                return
            data = markup.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
        def log_message(self, *args): pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    host = f"http://127.0.0.1:{server.server_port}/r79"
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        return _browse(markup, out, axe, chromium, host, require_navigation, require_axe)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

def _browse(markup, out, axe, chromium, host, require_navigation, require_axe):
    report = {"schema": "fv.apollo.r79.chromium.v1", "release": "STAGING_HOLD",
              "genuine_wordpress": False, "hosted_cwv": False, "media_rights_cleared": 0,
              "axes_executed": False, "cases": [], "screenshots_sha256": {}, "errors": []}
    with sync_playwright() as pw:
        launch = {"headless": True, "args": ["--no-sandbox"]}
        if chromium:
            launch["executable_path"] = chromium
        browser = pw.chromium.launch(**launch)
        try:
            for width in WIDTHS:
                for js in ((True, False) if width in (320, 390, 1440) else (True,)):
                    ctx = browser.new_context(
                        viewport={"width": width, "height": 900}, device_scale_factor=1,
                        is_mobile=width < 500, has_touch=width < 500, java_script_enabled=js,
                        reduced_motion="reduce" if width == 320 else "no-preference",
                        color_scheme="dark")
                    try:
                        page = ctx.new_page()
                        external, errors = [], []
                        page.on("pageerror", lambda error: errors.append(str(error)))
                        page.route("**/*", lambda route: route.continue_() if route.request.url == host
                            else (route.abort(), external.append(route.request.url)))
                        if js:
                            page.add_init_script("""(() => {window.__r79lab={lcp:null,cls:0};
                              try {new PerformanceObserver(l=>{for(const e of l.getEntries())window.__r79lab.lcp=e.startTime;})
                                  .observe({type:'largest-contentful-paint',buffered:true});}catch(e){}
                              try {new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)
                                  window.__r79lab.cls+=e.value;})
                                  .observe({type:'layout-shift',buffered:true});}catch(e){}
                            })();""")
                        navigated = True
                        try:
                            page.goto(host, wait_until="load")
                        except PlaywrightError as error:
                            # Only a locally disallowed browser-navigation fixture may use fallback,
                            # and then no LCP/CLS score is claimed.
                            if require_navigation or "ERR_BLOCKED_BY_ADMINISTRATOR" not in str(error):
                                raise
                            navigated = False
                            page.close()
                            page = ctx.new_page()
                            page.set_content(markup, wait_until="load")
                        assert page.locator(".card").count() == 6
                        # R80: a month-only image must never appear between dated
                        # sources in an ordered chronology, on screen OR with JS off.
                        rail_dates = page.locator(".rail > ol > li.rail-event > time").evaluate_all(
                            "(items) => items.map(t => t.getAttribute('datetime'))")
                        assert rail_dates == ["1966-10-18", "1967-01-03", "1967-01-28", "2017-01-24"], "R80_DAY_LEVEL_CHRONOLOGY_DRIFT"
                        ordered_links = page.locator(".rail > ol a[href^='#record-']").evaluate_all(
                            "(items) => items.map(a => a.getAttribute('href'))")
                        assert ordered_links == ["#record-03", "#record-02", "#record-05", "#record-04", "#record-06"], "R80_ORDERED_SOURCE_ID_DRIFT"
                        assert page.locator('.rail > ol a[href="#record-01"]').count() == 0, "R80_INVENTED_PORTRAIT_POSITION"
                        assert page.locator('.rail-unplaced time[datetime="1967-01"]').count() == 1, "R80_UNKNOWN_DATE_SUPPRESSED"
                        assert page.locator('.rail-unplaced a[href="#record-01"]').count() == 1, "R80_PROVISIONAL_SOURCE_NAV_MISSING"
                        assert page.locator('.rail > ol > li.rail-event').last.locator('a[href^="#record-"]').count() == 2, "R80_FALSE_2017_SEQUENCE"
                        assert page.locator("details.source-drawer").count() == 6
                        assert page.locator("a.source-link").count() == 6
                        assert page.locator("img,script,iframe,video,canvas").count() == 0
                        assert page.locator("[data-lat],[data-lon],[data-geo-edge]").count() == 0
                        assert page.locator('meta[name="robots"]').get_attribute("content") == "noindex,nofollow"
                        assert not external and not errors, (external, errors)
                        assert not page.evaluate("document.documentElement.scrollWidth > innerWidth + 2"), f"overflow {width}"
                        assert "not verified" in page.locator(".card").first.locator(".topline").inner_text().lower()
                        assert "pia catalog" in page.locator(".card").nth(1).locator(".topline").inner_text().lower()
                        case = {"browser_navigation": navigated, "width": width,
                                "javascript_enabled": js, "no_js_fully_readable": True,
                                "chronology_day_checkpoints": rail_dates,
                                "month_only_portrait_outside_ordered_rail": True,
                                "same_day_tributes_grouped": True,
                                "horizontal_overflow": False, "external_requests": 0,
                                "uncleared_media_embeds": 0, "unverified_geo": 0}
                        if js:
                            disclosure = page.locator(".card").first.locator("summary")
                            if width < 500:
                                disclosure.tap()
                            else:
                                disclosure.click()
                            assert page.locator(".card").first.locator("details").get_attribute("open") is not None
                            assert page.locator(".card").first.locator("dd").count() == 10
                            disclosure.focus()
                            page.keyboard.press("Enter")
                            assert page.locator(".card").first.locator("details").get_attribute("open") is None
                            source = page.locator(".source-link").first
                            assert source.evaluate("(e)=>new URL(e.href).hostname") == "www.nasa.gov"
                            assert source.bounding_box()["height"] >= 44
                            if axe and axe.is_file():
                                page.add_script_tag(path=str(axe))
                                result = page.evaluate("""async()=>{const a=await axe.run(document.querySelector('main'),
                                  {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                                  return {violations:a.violations.map(x=>({id:x.id,nodes:x.nodes.length})),
                                  passes:a.passes.length};}""")
                                assert not result["violations"], result
                                case["axe"] = result
                                report["axes_executed"] = True
                            page.wait_for_timeout(300)
                            lab = page.evaluate("window.__r79lab") if navigated else None
                            case["local_chromium_lab"] = {
                                "lcp_ms": lab["lcp"] if lab else None, "cls": lab["cls"] if lab else None,
                                "limitations": "Lab navigation, NOT field CWV" if navigated else
                                "Navigation disallowed: LCP/CLS NOT measured"}
                            if lab is not None:
                                assert lab["cls"] <= 0.1
                                if lab["lcp"] is not None:
                                    assert lab["lcp"] <= 2500
                            if require_navigation:
                                assert lab is not None and lab["lcp"] is not None, "R79_MISSING_LCP_OBSERVATION"
                            if width in (320, 390, 1440, 1920):
                                name = f"R79_NASA_SOURCE_{width}.png"
                                data = page.screenshot(full_page=True, animations="disabled")
                                (out / name).write_bytes(data)
                                report["screenshots_sha256"][name] = hashlib.sha256(data).hexdigest()
                        if not js and width == 1440:
                            page.emulate_media(media="print")
                            pdf = page.pdf(format="A4", print_background=True, prefer_css_page_size=True)
                            (out / "R79_NASA_SOURCE_PRINT.pdf").write_bytes(pdf)
                            import fitz
                            doc = fitz.open(stream=pdf, filetype="pdf")
                            text = re.sub(r"\s+", " ", "\n".join(p.get_text() for p in doc))
                            for catalog in ("S67-19766","S67-15717","S66-58038",
                                            "KSC-20170124-PH_KLS01_0164",
                                            "S67-21294","KSC-20170124-PH_KLS01_0090"):
                                assert catalog in text, f"Missing print source: {catalog}"
                            assert text.count("Individual media-rights assessment NOT completed") >= 6
                            case["printed_pdf_pages"] = len(doc)
                            case["printed_rights_warnings"] = 6
                        case["passed"] = True
                        report["cases"].append(case)
                    finally:
                        ctx.close()
            ctx = browser.new_context(viewport={"width": 390, "height": 844},
                                      forced_colors="active", reduced_motion="reduce")
            try:
                page = ctx.new_page()
                try:
                    page.goto(host, wait_until="load")
                except PlaywrightError as error:
                    if require_navigation or "ERR_BLOCKED_BY_ADMINISTRATOR" not in str(error):
                        raise
                    page.close()
                    page = ctx.new_page()
                    page.set_content(markup)
                page.locator(".card").first.locator("summary").focus()
                page.keyboard.press("Enter")
                assert page.locator(".card").first.locator("details").get_attribute("open") is not None
                image = page.screenshot(full_page=True, animations="disabled")
                name = "R79_NASA_SOURCE_FORCED_390.png"
                (out / name).write_bytes(image)
                report["screenshots_sha256"][name] = hashlib.sha256(image).hexdigest()
                report["forced_colors_keyboard_disclosure"] = True
            finally:
                ctx.close()
        finally:
            browser.close()
    assert len(report["cases"]) == 8 and all(case["passed"] for case in report["cases"])
    if require_axe:
        assert report["axes_executed"] and all("axe" in x for x in report["cases"] if x["javascript_enabled"])
    if require_navigation:
        assert all(case["browser_navigation"] for case in report["cases"])
    (out / "R79_CHROMIUM_RECEIPT.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    return report

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--axe", type=Path, default=None)
    p.add_argument("--chromium", default=None)
    p.add_argument("--require-navigation", action="store_true")
    p.add_argument("--require-axe", action="store_true")
    args = p.parse_args()
    print(json.dumps(run(args.repo, args.out, args.axe, args.chromium,
                         args.require_navigation, args.require_axe), sort_keys=True))
