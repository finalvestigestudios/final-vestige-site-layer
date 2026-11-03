#!/usr/bin/env python3
"""10 real Chromium contexts: accessible no-JS Atlas filtering, touch, axe, PDF and lab vitals."""
import argparse,hashlib,json
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from threading import Thread
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(src,out,axe):
    src=src.resolve();out.mkdir(parents=True,exist_ok=True)
    receipt=json.loads((src/"R94_ATLAS_RECEIPT.json").read_text())
    assert receipt["release"]=="STAGING_HOLD" and receipt["photo_rights_cleared"]==0 and receipt["geo_pins"]==0
    for f,h in receipt["files"].items():assert sha(src/f)==h
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(src)))
    Thread(target=server.serve_forever,daemon=True).start()
    base="http://127.0.0.1:"+str(server.server_port)
    result={"cases":[],"axe":[],"screenshots":{},"pdf":None,"external_requests":[],"release":"STAGING_HOLD"}
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
        try:
          for width in (320,390,768,1440,1920):
            for js in (False,True):
              ctx=browser.new_context(viewport={"width":width,"height":900},java_script_enabled=js,
                has_touch=width==390,is_mobile=width==390,reduced_motion="reduce" if width==768 else "no-preference")
              case={"width":width,"javascript":js,"errors":[]}
              try:
                page=ctx.new_page()
                page.on("pageerror",lambda e,case=case:case["errors"].append(str(e)))
                page.on("request",lambda r:result["external_requests"].append(r.url) if urlparse(r.url).netloc!=urlparse(base).netloc else None)
                if js:page.add_init_script('''window.__cwv={lcp:0,cls:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__cwv.lcp=Math.max(window.__cwv.lcp,e.startTime)}).observe({type:"largest-contentful-paint",buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cwv.cls+=e.value}).observe({type:"layout-shift",buffered:true})}catch(_){}''')
                assert page.goto(base+"/R94_CURATED_ATLAS.html",wait_until="load").status==200
                page.wait_for_timeout(80)
                assert page.locator(".card").count()==6
                assert page.locator(".card:visible").count()==6
                assert page.locator(".source").count()==6
                assert page.locator("img,iframe,canvas,video").count()==0
                assert page.locator("#filters").is_visible()==js
                assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
                page.locator("#atlas-01 summary").focus();page.keyboard.press("Enter")
                assert page.locator("#atlas-01 details").get_attribute("open") is not None
                page.keyboard.press("Space")
                assert page.locator("#atlas-01 details").get_attribute("open") is None
                if js:
                    page.get_by_role("button",name="Month only (1)").click()
                    assert page.locator(".card:visible").count()==1
                    page.get_by_role("button",name="Specific-day records (5)").click()
                    assert page.locator(".card:visible").count()==5
                    page.locator("#query").fill("S67-15717")
                    assert page.locator(".card:visible").count()==1
                    page.locator("#query").fill("no-match-xxx")
                    assert page.locator(".card:visible").count()==0 and page.locator("#empty").is_visible()
                    page.get_by_role("button",name="All six").click();page.locator("#query").fill("")
                    assert page.locator(".card:visible").count()==6
                    # R96: a native anchor clicked again must reveal a filtered-out
                    # evidence record even if the URL fragment does not change.
                    page.locator('nav.jump a[href="#atlas-01"]').click()
                    page.wait_for_function("document.activeElement.id==='atlas-01'")
                    page.get_by_role("button",name="Specific-day records (5)").click()
                    page.locator("#query").fill("no-match-xxx")
                    assert page.locator("#atlas-01").is_hidden()
                    page.locator('nav.jump a[href="#atlas-01"]').click()
                    assert page.locator("#atlas-01").is_visible()
                    assert page.locator(".card:visible").count()==6
                    assert page.locator("#query").input_value()==""
                    assert page.evaluate('document.activeElement.id')=="atlas-01"
                    # Navigation/history to a different hidden source also resets
                    # filters without altering the archival claim or target URL.
                    page.get_by_role("button",name="Month only (1)").click()
                    page.locator("#query").fill("not-found")
                    page.evaluate("location.hash='#atlas-05'")
                    page.wait_for_function("document.activeElement.id==='atlas-05'")
                    assert page.locator("#atlas-05").is_visible()
                    assert page.locator(".card:visible").count()==6
                    assert page.locator("#query").input_value()==""
                    assert page.url.endswith("#atlas-05")
                    page.go_back()
                    page.wait_for_function("document.activeElement.id==='atlas-01'")
                    assert page.locator("#atlas-01").is_visible()
                assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
                if js and width==390:
                    page.locator("#atlas-02 summary").tap()
                    assert page.locator("#atlas-02 details").get_attribute("open") is not None
                if js and width in (390,1440):
                    page.add_script_tag(path=str(axe))
                    verdict=page.evaluate('''async()=>{const r=await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa","wcag22aa"]}});return {violations:r.violations.map(v=>({id:v.id,nodes:v.nodes.length})),passes:r.passes.length}}''')
                    assert not verdict["violations"],verdict
                    result["axe"].append({"width":width,**verdict})
                    shot=out/("R94_ATLAS_"+str(width)+".png")
                    page.screenshot(path=str(shot),full_page=True);result["screenshots"][shot.name]=sha(shot)
                if js and width==390:
                    page.emulate_media(forced_colors="active")
                    shot=out/"R94_FORCED_390.png"
                    page.screenshot(path=str(shot),full_page=True);result["screenshots"][shot.name]=sha(shot)
                if js and width==1440:
                    page.emulate_media(media="print")
                    assert page.locator("#atlas-01 .print").evaluate("(e)=>getComputedStyle(e).color")=="rgb(0, 0, 0)"
                    pdf=out/"R94_PRINT.pdf";pdf.write_bytes(page.pdf(format="A4",print_background=True))
                    import fitz
                    doc=fitz.open(pdf);text="".join("".join(x.get_text().split()) for x in doc)
                    book=json.loads((src/"R93_SOURCE_PASSPORTS.json").read_text())
                    for item in book["records"]:assert item["url"] in text,item["id"]
                    assert text.count("INDIVIDUALREVIEWREQUIRED")>=6
                    result["pdf"]={"pages":len(doc),"sha256":sha(pdf)};doc.close()
                assert not case["errors"],case
                case["lcp_lab_ms"]=page.evaluate("window.__cwv?.lcp||0") if js else None
                case["cls_lab"]=page.evaluate("window.__cwv?.cls||0") if js else None
                result["cases"].append(case)
              finally:ctx.close()
        finally:browser.close()
      assert len(result["cases"])==10 and len(result["axe"])==2 and len(result["screenshots"])==3
      assert result["pdf"] and not result["external_requests"],result
      (out/"R94_CHROMIUM_RECEIPT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
      return result
    finally:server.shutdown();server.server_close()
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--src",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True);ap.add_argument("--axe",type=Path,required=True)
    a=ap.parse_args();print(json.dumps(run(a.src,a.out,a.axe),sort_keys=True))
