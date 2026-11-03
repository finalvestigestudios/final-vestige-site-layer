#!/usr/bin/env python3
"""R89 true Chromium cross-document, no-JS, axe, print, LCP/CLS review."""
import argparse
import hashlib
import json
import re
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

WIDTHS = (320, 390, 768, 1440, 1920)
PAGES = ("R89_REVIEW_HUB.html", "R88_READING_ROOM.html",
         "R87_PHOTOGRAPH_DATE_RAIL.html", "R85_NASA_SOURCE_REVIEW.html")
TRACE = {"case": "NOT_STARTED", "gate": "INIT"}

def checksum(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()

def run(root: Path, out: Path, axe: Path, chromium: str | None = None):
    assert all((root / name).is_file() for name in PAGES), "R89_BUILD_INCOMPLETE"
    assert axe.is_file(), "R89_AXE_MISSING"
    out.mkdir(parents=True, exist_ok=True)
    class Silent(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0),
        partial(Silent, directory=str(root.resolve())))
    Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    cases, shots = [], {}
    errors, external = [], []
    try:
        with sync_playwright() as p:
            opts = {"headless": True}
            if chromium:
                opts.update(executable_path=chromium, args=["--no-sandbox"])
            browser = p.chromium.launch(**opts)
            for width in WIDTHS:
                for js in (False, True):
                    TRACE.update(case=f"{width}/JS={js}", gate="CONTEXT")
                    context = browser.new_context(viewport={"width": width, "height": 900},
                        java_script_enabled=js, reduced_motion="reduce",
                        has_touch=width <= 390, is_mobile=width <= 390)
                    if js:
                        context.add_init_script("""(() => {
                          window.__fvLab = {lcp: null, cls: 0};
                          try {new PerformanceObserver(list => {
                            for(const x of list.getEntries()) window.__fvLab.lcp=x.startTime;
                          }).observe({type:'largest-contentful-paint',buffered:true});} catch(e) {}
                          try {new PerformanceObserver(list => {
                            for(const x of list.getEntries()) if(!x.hadRecentInput) window.__fvLab.cls+=x.value;
                          }).observe({type:'layout-shift',buffered:true});} catch(e) {}
                        })();""")
                    page = context.new_page()
                    page.on("pageerror", lambda _: errors.append("PAGE_SCRIPT_FAILURE"))
                    def route(r):
                        if not r.request.url.startswith(base + "/"):
                            external.append("UNEXPECTED_OUTBOUND")
                            r.abort()
                        else:
                            r.continue_()
                    page.route(re.compile("^https?://"), route)
                    TRACE["gate"] = "LOAD_HUB"
                    page.goto(base + "/" + PAGES[0], wait_until="load")
                    page.wait_for_timeout(220)
                    assert not errors and not external, "R89_NETWORK_OR_SCRIPT_ERROR"
                    assert page.locator("main article.source").count() == 6, "R89_SIX_SOURCES"
                    assert page.locator("article.source details").count() == 6, "R89_SOURCE_DRAWERS"
                    assert page.locator("article.source a[href^='https://www.nasa.gov/image-detail/']").count()==6, "R89_NASA_SOURCE_CUSTODY"
                    assert page.locator("img,iframe,picture,video,[data-lat],[data-lon],[data-geo-edge]").count()==0, "R89_MEDIA_OR_GEO"
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+2"), "R89_OVERFLOW_HUB"
                    TRACE["gate"] = "NATIVE_KEYBOARD"
                    summary = page.locator("article.source summary").first
                    summary.focus()
                    page.keyboard.press("Enter")
                    assert page.locator("article.source details").first.evaluate("(d)=>d.open"), "R89_ENTER_OPEN"
                    page.keyboard.press("Enter")
                    assert not page.locator("article.source details").first.evaluate("(d)=>d.open"), "R89_ENTER_CLOSE"
                    case = {"width":width, "js":js, "cross_document_links": 0, "axe":None,
                            "lcp_ms":None,"cls":None,"keyboard":True,"no_overflow":True}
                    TRACE["gate"] = "CROSS_DOCUMENT_NAVIGATION"
                    for name, anchor in (("R88_READING_ROOM.html", "r88-01"),
                                         ("R87_PHOTOGRAPH_DATE_RAIL.html", "r87-record-01"),
                                         ("R85_NASA_SOURCE_REVIEW.html", "r85-source-01")):
                        page.goto(base + "/" + PAGES[0], wait_until="load")
                        page.locator(f'a[href="{name}#{anchor}"]').click()
                        assert page.url.endswith(name + "#" + anchor), "R89_WRONG_NAV_TARGET"
                        assert page.locator("#" + anchor).count()==1, "R89_MISSING_RECORD_AT_TARGET"
                        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+2"), "R89_DESTINATION_OVERFLOW"
                        case["cross_document_links"] += 1
                    TRACE["gate"] = "A11Y_PERFORMANCE"
                    page.goto(base + "/" + PAGES[0], wait_until="load")
                    page.wait_for_timeout(350)
                    if js:
                        page.add_script_tag(path=str(axe))
                        report = page.evaluate("""async () => {
                          const v=await axe.run(document,{runOnly:{type:'tag',values:
                           ['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
                          return {violations:v.violations.map(x=>x.id),passes:v.passes.length};
                        }""")
                        assert not report["violations"], "R89_AXE:" + ",".join(report["violations"])
                        case["axe"]=report
                        perf=page.evaluate("window.__fvLab")
                        case["lcp_ms"]=perf["lcp"]
                        case["cls"]=perf["cls"]
                        assert perf["lcp"] is not None and 0 < perf["lcp"] <= 2500, "R89_MISSING_OR_SLOW_LCP"
                        assert 0 <= perf["cls"] <= .1, "R89_EXCESS_CLS"
                    if width in (390,1440) and js:
                        TRACE["gate"] = "SCREENSHOT_AND_PDF"
                        shot=out / f"R89_HUB_{width}.png"
                        page.screenshot(path=str(shot),full_page=True,animations="disabled")
                        shots[str(width)]=checksum(shot)
                        if width == 1440:
                            page.pdf(path=str(out / "R89_HUB_PRINT.pdf"),
                                format="A4",print_background=True)
                            import fitz
                            with fitz.open(out / "R89_HUB_PRINT.pdf") as pdf:
                                text="\n".join(p.get_text() for p in pdf)
                                assert all(x in text for x in (
                                    "S67-19766", "INDIVIDUAL REVIEW REQUIRED", "NOT FOR PUBLICATION")), "R89_PRINT_CUSTODY_MISSING"
                                assert text.count("https://www.nasa.gov/image-detail/") == 6, "R89_PRINT_NASA_LINK_COUNT"
                                printed=len(pdf)
                    cases.append(case)
                    context.close()
            TRACE.update(case="390/FORCED",gate="FORCED_COLOR")
            context=browser.new_context(viewport={"width":390,"height":900},
                forced_colors="active",reduced_motion="reduce")
            page=context.new_page()
            page.goto(base + "/" + PAGES[0])
            page.locator("article.source summary").first.click()
            assert page.locator("article.source details").first.evaluate("(d)=>d.open"),"R89_FORCED_DISCLOSURE"
            shot=out / "R89_HUB_FORCED_390.png"
            page.screenshot(path=str(shot),full_page=True)
            shots["forced_390"]=checksum(shot)
            context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    receipt={"schema":"fv.apollo.r89.real-chromium.v1","release":"STAGING_HOLD",
             "cases":cases,"case_count":len(cases),"screenshots":shots,
             "printed_pages":printed,
             "pdf_sha256":checksum(out / "R89_HUB_PRINT.pdf")}
    (out / "R89_BROWSER_RECEIPT.json").write_text(
        json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    return receipt

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--src",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    a.add_argument("--axe",required=True,type=Path)
    a.add_argument("--chromium")
    args=a.parse_args()
    try:
        result=run(args.src,args.out,args.axe,args.chromium)
        print("R89: REAL CHROMIUM",result["case_count"],"CONFIGURATIONS PASS / STAGING HOLD")
    except Exception:
        print("R89_BROWSER_HOLD:"+TRACE["case"]+":"+TRACE["gate"],file=sys.stderr)
        sys.exit(1)
