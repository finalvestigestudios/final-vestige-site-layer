#!/usr/bin/env python3
"""EX2 read-only, anonymous, image-delivery acceptance probe.

Never logs in, submits a form, or modifies WP. Existing site analytics may
count anonymous pageviews; this script installs no new analytics. Production use
needs an internet-enabled browser: a synthetic mock test is not live evidence.
Playwright request.sizes().responseBodySize is encoded response-body bytes (when
available); len(response.body()) is decoded body bytes and is NOT wire size.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit, parse_qs, urlencode
import re
import shutil
from playwright.sync_api import sync_playwright

ASSETS = {
    "apollo": "s67-19766.webp",
    "franklin": "Franklinexpeditionnote.jpg",
    "malbone": "edit-017-v02-nypl-5003296-original.jpg",
}
WIDTHS = (320, 360, 390, 768, 1440, 1920)
ALLOWED_HOSTS = {"finalvestige.com", "i0.wp.com", "i1.wp.com", "i2.wp.com"}

def asset_for(url):
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_HOSTS or "/wp-content/uploads/" not in parsed.path:
        return None
    return next((key for key, filename in ASSETS.items() if filename in parsed.path), None)

def safe_url(url):
    p = urlsplit(url)
    # Preserve only Jetpack resize hints for responsive selection evidence.
    # Never serialize arbitrary query values, user identifiers or signatures.
    allowed = {}
    for key in ("fit", "resize", "ssl"):
        value = parse_qs(p.query).get(key, [""])[0]
        if value and re.fullmatch(r"[0-9,]{1,16}", value):
            allowed[key] = value
    suffix = "?" + urlencode(allowed) if allowed else ""
    return f"{p.hostname or ''}{p.path}{suffix}"

def classify(record, dom):
    """Fail closed on status, image decoding, missing bytes, or unverifiable transfer."""
    errors = []
    if not dom.get("exists"):
        return ["DOM_IMAGE_MISSING"]
    if not dom.get("alt"):
        errors.append("ALT_MISSING")
    if dom.get("naturalWidth", 0) < 16 or dom.get("naturalHeight", 0) < 16 or not dom.get("complete"):
        errors.append("IMAGE_NOT_DECODED")
    if dom.get("display") == "none" or dom.get("visibility") == "hidden" or dom.get("rectWidth", 0) <= 0 or dom.get("ancestorHidden"):
        errors.append("IMAGE_HIDDEN")
    if not record:
        errors.append("NETWORK_RESPONSE_NOT_OBSERVED")
        return errors
    if record.get("status") != 200:
        errors.append("HTTP_NOT_200")
    if not str(record.get("mime", "")).lower().startswith("image/"):
        errors.append("NON_IMAGE_CONTENT_TYPE")
    if (record.get("decoded_body_bytes") or 0) <= 0:
        errors.append("EMPTY_RESPONSE_BODY")
    if record.get("wire_body_bytes") is None or record.get("wire_body_bytes", -1) < 0:
        errors.append("WIRE_BYTES_NOT_MEASURED")
    if record.get("request_failed"):
        errors.append("REQUEST_FAILED")
    return errors

def probe(browser, width, dpr, js_enabled, url, screenshot_dir=None, fixture=None):
    context = browser.new_context(viewport={"width": width, "height": 900},
                                  device_scale_factor=dpr, java_script_enabled=js_enabled,
                                  reduced_motion="reduce", service_workers="block")
    page = context.new_page()
    if fixture is not None:
        # SYNTHETIC TEST ONLY. This path never navigates to a live host.
        def mock(route):
            asset = asset_for(route.request.url)
            spec = fixture.get("responses", {}).get(asset, {})
            route.fulfill(status=spec.get("status", 200),
                          content_type=spec.get("mime", "image/jpeg"),
                          body=spec.get("body", b""))
        page.route("**/*", mock)
    receipts = {name: [] for name in ASSETS}
    failures = []
    def completed(request):
        key = asset_for(request.url)
        if not key:
            return
        response = request.response()
        out = {"url": safe_url(request.url), "status": None, "mime": "",
               "decoded_body_bytes": None, "wire_body_bytes": None,
               "request_failed": False}
        if response:
            out["status"] = response.status
            out["mime"] = response.headers.get("content-type", "")
            try:
                out["decoded_body_bytes"] = len(response.body())
            except Exception:
                pass
            try:
                encoded = request.sizes().get("responseBodySize")
                out["wire_body_bytes"] = encoded if isinstance(encoded, int) and encoded >= 0 else None
            except Exception:
                pass
        receipts[key].append(out)
    def failed(request):
        key = asset_for(request.url)
        if key:
            failures.append({"asset": key, "url": safe_url(request.url), "error": "REQUEST_FAILED"})
    page.on("requestfinished", completed)
    page.on("requestfailed", failed)
    visit_error = None
    try:
        if fixture is None:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
        else:
            page.set_content(fixture["html"], wait_until="load")
    except Exception as e:
        msg = str(e)
        visit_error = "ERR_BLOCKED_BY_ADMINISTRATOR" if "ERR_BLOCKED_BY_ADMINISTRATOR" in msg else "NAVIGATION_ERROR"
    outcomes = {}
    for key in ASSETS:
        if js_enabled:
            button = page.locator(f'[data-fv-case-button="{key}"]')
            if button.count() > 0:
                try:
                    button.first.click(timeout=4500)
                except Exception:
                    pass
        img = page.locator(f'[data-fv-case="{key}"] img[data-fv-archive-img]')
        if img.count() == 0:
            dom = {"exists": False}
        else:
            try:
                img.first.scroll_into_view_if_needed(timeout=4500)
            except Exception:
                pass
            try:
                img.first.evaluate("el=>el.loading='eager'")
                page.wait_for_function("sel=>{let e=document.querySelector(sel);return !!e && e.complete}",
                                       f'[data-fv-case="{key}"] img[data-fv-archive-img]',timeout=8500)
            except Exception:
                pass
            dom = img.first.evaluate("""el=>({exists:true,alt:el.alt,complete:el.complete,
                naturalWidth:el.naturalWidth,naturalHeight:el.naturalHeight,
                currentSrc:el.currentSrc,display:getComputedStyle(el).display,
                visibility:getComputedStyle(el).visibility,ancestorHidden:!!el.closest("[hidden]"),
                responsive:!!el.getAttribute('srcset'),rectWidth:Math.round(el.getBoundingClientRect().width)})""")
            dom["currentSrc"] = safe_url(dom.get("currentSrc", ""))
        selected = dom.get("currentSrc", "")
        relevant = [r for r in receipts[key] if r.get("url") == selected]
        record = relevant[-1] if relevant else None
        errors = classify(record, dom)
        if dom.get("exists") and asset_for("https://" + selected) != key:
            errors.append("SELECTED_SOURCE_NOT_EXPECTED_ARCHIVE")
        if receipts[key] and not relevant:
            errors.append("SELECTED_URL_RESPONSE_NOT_OBSERVED")
        if any(f["asset"] == key for f in failures):
            errors.append("REQUEST_FAILED")
        outcomes[key] = {"dom": dom, "response": record, "errors": sorted(set(errors)),
                         "result": "PASS" if not errors else "FAIL"}
    if screenshot_dir:
        Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(Path(screenshot_dir) / f"home_{width}_dpr{dpr}_{'js' if js_enabled else 'nojs'}.png"),
                        full_page=True, timeout=25000)
    result = {"width":width,"dpr":dpr,"javascript":js_enabled,"visit_error":visit_error,
              "synthetic_fixture":fixture is not None,"assets":outcomes,"pass":visit_error is None and all(x["result"]=="PASS" for x in outcomes.values())}
    context.close()
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--url",default="https://finalvestige.com/")
    ap.add_argument("--out",required=True)
    ap.add_argument("--screenshots")
    ap.add_argument("--widths",default="320,360,390,768,1440,1920")
    ap.add_argument("--dprs",default="1,2")
    ap.add_argument("--nojs",action="store_true")
    ap.add_argument("--chromium",default=shutil.which("chromium"))
    args=ap.parse_args()
    if args.url != "https://finalvestige.com/":
        ap.error("Only approved public homepage URL is allowed in the live probe")
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path=args.chromium, args=["--no-sandbox"] if args.chromium else [])
        results=[]
        for width in map(int,args.widths.split(",")):
            for dpr in map(int,args.dprs.split(",")):
                for js in ([True,False] if args.nojs else [True]):
                    results.append(probe(browser,width,dpr,js,args.url,args.screenshots))
        browser.close()
    receipt={"scope":"LIVE_HOST_ANONYMOUS_READ_ONLY_IF_VISIT_SUCCEEDS",
             "note":"wire_body_bytes=Playwright encoded responseBodySize, not full transfer including headers; decoded_body_bytes is NOT network transfer.",
             "acceptance":"FAIL_CLOSED","results":results,"passed":sum(bool(r['pass']) for r in results),
             "total":len(results),"site_writes":0,"form_submissions":0}
    Path(args.out).write_text(json.dumps(receipt,indent=2))
    print(json.dumps({"passed":receipt["passed"],"total":receipt["total"],"receipt":args.out}))
    if receipt["passed"] != receipt["total"]:
        raise SystemExit(1)

if __name__=="__main__":
    main()
