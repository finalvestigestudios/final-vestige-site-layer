"""R184: actual Chromium Playwright fixture verification, NOT installed WordPress acceptance.

Run:
  python experience2/apollo-r184/build_wp_atlas.py
  python experience2/apollo-r184/qa/browser_acceptance.py --out /tmp/apollo-r184-browser
No network, paid services, or publication. Missing axe-core is reported, never silently passed.
"""
from pathlib import Path
import argparse, hashlib, json, sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT/"dist/templates/atlas-fragment.html").read_text()
CSS = (ROOT/"dist/assets/atlas-scoped.css").read_text()
SHELL = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{margin:0;background:rgb(232,238,241);color:rgb(30,60,90);font:20px Arial,sans-serif}
#site-header{padding:8px;background:#f0f5f8}#wp-main{max-width:none;padding:0}</style>
<style>__CSS__</style></head><body><header id="site-header">WordPress shell control</header><main id="wp-main">__HTML__</main>
<footer id="site-footer">WordPress shell footer</footer></body></html>""".replace("__CSS__",CSS).replace("__HTML__",HTML)
PERF = """<script>window.__lab={lcp:null,cls:0};
try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lab.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__lab.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}</script>"""
CONFIGS=[("320",320,True,{}),("360",360,True,{}),("390",390,True,{}),("768",768,True,{}),("1440",1440,True,{}),
         ("1920",1920,True,{}),("320-no-js",320,False,{}),("390-no-js-no-css",390,False,{"no_css":True}),
         ("390-forced-colors",390,True,{"forced":True}),("390-touch",390,True,{"touch":True}),
         ("390-reduced-motion",390,True,{"reduced":True})]

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    checks=[];pics={};metrics=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
        for name,width,js,options in CONFIGS:
            ctx=browser.new_context(viewport={"width":width,"height":900},
                java_script_enabled=js,device_scale_factor=1,
                has_touch=bool(options.get("touch")),is_mobile=bool(options.get("touch")),
                forced_colors="active" if options.get("forced") else "none",
                reduced_motion="reduce" if options.get("reduced") else "no-preference")
            page=ctx.new_page();failures=[];requests=[]
            page.on("pageerror",lambda err:failures.append(str(err)))
            page.on("request",lambda req:requests.append(req.url))
            page.set_content(SHELL.replace("</head>",PERF+"</head>") if js else SHELL,wait_until="load")
            if options.get("no_css"):
                from bs4 import BeautifulSoup
                naked=BeautifulSoup(SHELL,"html.parser")
                for style in naked.select("style"):style.decompose()
                page.set_content(str(naked),wait_until="load")
            def require(ok,label):
                checks.append({"context":name,"check":label,"pass":bool(ok)})
                if not ok:raise AssertionError(name+" / "+label)
            require(page.locator(".fv-apollo-atlas .plate").count()==4,"4 evidence plates")
            require(page.locator(".fv-apollo-atlas .source-card").count()==4,"4 archival records")
            require(page.locator(".fv-apollo-atlas .rail li").count()==4,"4 dates")
            require(page.locator(".fv-apollo-atlas details").count()==8,"8 native source disclosures")
            require(page.locator(".fv-apollo-atlas a.cta").count()==1,"1 contextual reading CTA")
            require(page.locator("main#wp-main").count()==1,"host main preserved")
            require(page.locator(".fv-apollo-atlas main").count()==0,"no duplicate main")
            require(not requests and not failures,"no remote requests or browser errors")
            size=page.evaluate("({scroll:document.documentElement.scrollWidth,viewport:document.documentElement.clientWidth})")
            require(size["scroll"]<=size["viewport"]+2,"no horizontal overflow")
            ids=page.locator(".fv-apollo-atlas a[href^='#']").evaluate_all("(links)=>links.map(a=>a.hash.slice(1))")
            require(all(page.locator('[id="'+x+'"]').count()==1 for x in ids),"all internal anchors resolve")
            if name=="390":
                page.locator('a[href="#fv-apollo-photo-aftermath"]').click()
                require(page.url.endswith("#fv-apollo-photo-aftermath"),"timeline deep link")
                d=page.locator("#fv-apollo-photo-aftermath details")
                d.locator("summary").click()
                require(d.evaluate("(e)=>e.open"),"click opens source")
                page.locator("#fv-apollo-finding-fire details summary").focus()
                page.keyboard.press("Enter")
                require(page.locator("#fv-apollo-finding-fire details").evaluate("(e)=>e.open"),"keyboard opens source")
                page.set_content(SHELL.replace("</head>",PERF+"</head>"),wait_until="load")
            if options.get("touch"):
                d=page.locator("#fv-apollo-photo-aftermath details")
                d.locator("summary").tap()
                require(d.evaluate("(e)=>e.open"),"touch opens source")
                page.set_content(SHELL.replace("</head>",PERF+"</head>"),wait_until="load")
            if options.get("reduced"):
                require(page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"),"reduced motion")
            if options.get("forced"):
                require(page.evaluate("matchMedia('(forced-colors: active)').matches"),"forced colors")
            target=out/(name+".png");page.screenshot(path=str(target),animations="disabled",full_page=True)
            pics[name]=hashlib.sha256(target.read_bytes()).hexdigest()
            if js:
                page.wait_for_timeout(100)
                metrics.append({"context":name,**page.evaluate("window.__lab||{}")})
            ctx.close()
        browser.close()
    receipt={"assertions":checks,"passed":len(checks),"screenshots":pics,"lab_only_lcp_cls":metrics,
             "axe_core":"NOT_EXECUTED; missing vetted library",
             "actual_wordpress":"NOT_TESTED; fixture does not prove installation",
             "commercial_offer":"NOT_VERIFIED","live_site":"UNMODIFIED"}
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    return receipt

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--out",required=True)
    x=run(a.parse_args().out);print(json.dumps({"passed":x["passed"],"screenshots":len(x["screenshots"])},indent=2))
