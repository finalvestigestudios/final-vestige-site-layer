#!/usr/bin/env python3
"""R97 genuine Chromium HTTP acceptance; screenshots, PDF, optional axe, lab CWV."""
import argparse
import hashlib
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run(src,out,axe):
    src=src.resolve()
    out.mkdir(parents=True,exist_ok=True)
    receipt=json.loads((src/"R97_GALLERY_RECEIPT.json").read_text())
    assert receipt["release"]=="STAGING_HOLD"
    assert receipt["photo_rights_cleared"]==receipt["geo_pins"]==receipt["images_embedded"]==0
    for name,h in receipt["files"].items():
        assert sha(src/name)==h,name
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(src)))
    Thread(target=server.serve_forever,daemon=True).start()
    url=f"http://127.0.0.1:{server.server_port}/R97_SOURCE_GALLERY.html"
    results={"release":"STAGING_HOLD","transport":"REAL_HTTP_CHROMIUM",
             "cases":[],"axe":[],"screenshots":{},"pdf":None,"external_requests":[]}
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            try:
                for width in (320,390,768,1440,1920):
                    for js in (False,True):
                        context=browser.new_context(
                            viewport={"width":width,"height":900},java_script_enabled=js,
                            has_touch=width==390,is_mobile=width==390,
                            reduced_motion="reduce" if width==768 else "no-preference")
                        try:
                            page=context.new_page()
                            page.set_default_timeout(12000)
                            errors=[]
                            page.on("pageerror",lambda e:errors.append(str(e)))
                            page.on("request",lambda r:results["external_requests"].append(r.url)
                                    if urlparse(r.url).netloc!=urlparse(url).netloc else None)
                            if js:
                                page.add_init_script("""window.__cwv={lcp:0,cls:0};
                                  try{
                                    new PerformanceObserver(list=>{for(const e of list.getEntries())window.__cwv.lcp=Math.max(window.__cwv.lcp,e.startTime)}).observe({type:'largest-contentful-paint',buffered:true});
                                    new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__cwv.cls+=e.value}).observe({type:'layout-shift',buffered:true});
                                  }catch(_){}""")
                            assert page.goto(url,wait_until="load").status==200
                            page.wait_for_timeout(120)
                            assert page.locator(".card").count()==6
                            assert page.locator("img,video,canvas,iframe").count()==0
                            assert page.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==6
                            assert page.locator("[data-compare-controls]:visible").count()==(7 if js else 0)
                            assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),width
                            page.locator("#gallery-01 summary").focus()
                            page.keyboard.press("Enter")
                            assert page.locator("#gallery-01 details").get_attribute("open") is not None
                            page.keyboard.press("Space")
                            assert page.locator("#gallery-01 details").get_attribute("open") is None
                            if js:
                                one=page.locator("#compare-01")
                                two=page.locator("#compare-06")
                                three=page.locator("#compare-04")
                                one.focus()
                                page.keyboard.press("Space")
                                assert one.is_checked()
                                two.check()
                                assert page.locator("#comparison").is_visible()
                                assert page.locator("[data-value]").nth(0).inner_text()=="Apollo 1 Crew Honored"
                                assert page.locator("[data-value]").nth(1).inner_text()=="Apollo 1 Tribute — Redesigned Hatch"
                                assert "January 24, 2017" in page.locator("[data-value]").nth(5).inner_text()
                                three.click()
                                assert not three.is_checked() and page.locator("#comparison").is_visible()
                                if width==1440:
                                    shot=out/"R97_COMPARISON_1440.png"
                                    page.screenshot(path=str(shot),full_page=True)
                                    results["screenshots"][shot.name]=sha(shot)
                                page.locator("#compare-reset").click()
                                assert page.locator("#comparison").is_hidden()
                                assert page.evaluate("document.activeElement.id")=="compare-01"
                                if width==390:
                                    page.locator("#gallery-02 summary").tap()
                                    assert page.locator("#gallery-02 details").get_attribute("open") is not None
                                if width in (390,1440):
                                    page.add_script_tag(path=str(axe))
                                    outcome=page.evaluate("""async()=>{let r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                                      return {violations:r.violations.map(v=>({id:v.id,nodes:v.nodes.length})),passing:r.passes.length}}""")
                                    assert not outcome["violations"],outcome
                                    results["axe"].append({"width":width,**outcome})
                                    shot=out/f"R97_GALLERY_{width}.png"
                                    page.screenshot(path=str(shot),full_page=True)
                                    results["screenshots"][shot.name]=sha(shot)
                                if width==390:
                                    page.emulate_media(forced_colors="active")
                                    shot=out/"R97_FORCED_390.png"
                                    page.screenshot(path=str(shot),full_page=True)
                                    results["screenshots"][shot.name]=sha(shot)
                                if width==1440:
                                    page.emulate_media(media="print")
                                    pdf=out/"R97_GALLERY_PRINT.pdf"
                                    pdf.write_bytes(page.pdf(format="A4",print_background=True))
                                    import fitz
                                    book=json.loads((src/"R93_SOURCE_PASSPORTS.json").read_text())
                                    doc=fitz.open(pdf)
                                    text="".join("".join(p.get_text().split()) for p in doc)
                                    for record in book["records"]:
                                        assert record["url"] in text,record["id"]
                                    assert text.count("INDIVIDUALREVIEWREQUIRED")>=6
                                    results["pdf"]={"pages":len(doc),"sha256":sha(pdf)}
                                    doc.close()
                            assert not errors,errors
                            results["cases"].append({"width":width,"javascript":js,"errors":errors,
                                "lcp_lab_ms":page.evaluate("window.__cwv?.lcp||0") if js else None,
                                "cls_lab":page.evaluate("window.__cwv?.cls||0") if js else None})
                        finally:
                            context.close()
            finally:
                browser.close()
        assert len(results["cases"])==10
        assert len(results["axe"])==2
        assert len(results["screenshots"])==4
        assert results["pdf"] and not results["external_requests"]
        (out/"R97_BROWSER_RECEIPT.json").write_text(json.dumps(results,sort_keys=True,indent=2)+"\n")
        return results
    finally:
        server.shutdown()
        server.server_close()

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--src",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--axe",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.src,args.out,args.axe),sort_keys=True))
