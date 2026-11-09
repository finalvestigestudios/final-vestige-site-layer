#!/usr/bin/env python3
"""Exact-checkout Chromium masthead reflow gate. NO WordPress/publishing writes.
Requires Playwright Python and installed Chromium. Do not confuse with staging,
axe/WCAG acceptance, Lighthouse/CWV or a measured commercial conversion.
"""
import argparse, json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS=(160,200,256,320,390,768,1440)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--checkout",type=Path,default=Path.cwd())
    ap.add_argument("--expected-head",required=True)
    ap.add_argument("--chromium",default="/usr/bin/chromium")
    ap.add_argument("--out",type=Path,default=Path("reflow-evidence"))
    args=ap.parse_args()
    actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=args.checkout,text=True).strip()
    if actual!=args.expected_head or len(actual)!=40:
        raise SystemExit("FAIL CLOSED: exact checkout HEAD does not match")
    root=args.checkout/"experience2/home-flagship"
    html=root/"index.html"
    css=root/"flagship.css"
    if not html.is_file() or not css.is_file():
        raise SystemExit("FAIL CLOSED: exact source files missing")
    if 'EX2 review: preserve the direct Focus action' not in css.read_text():
        raise SystemExit("FAIL CLOSED: reflow patch absent")
    args.out.mkdir(parents=True,exist_ok=True)
    rows=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.chromium,args=["--no-sandbox"])
        for width in WIDTHS:
            for js in (False,True):
                page=browser.new_page(viewport={"width":width,"height":850},
                                      java_script_enabled=js,reduced_motion="reduce")
                page.route("http://**/*",lambda r:r.abort())
                page.route("https://**/*",lambda r:r.abort())
                page.goto(html.resolve().as_uri(),wait_until="domcontentloaded")
                menu=page.locator(".fv-hf__mobile-menu")
                if width<=920:menu.locator("summary").click()
                state=page.evaluate("""() => {
                  const box=s=>document.querySelector(s).getBoundingClientRect();
                  const cta=box('.fv-hf__mast-cta'),brand=box('.fv-hf__brand'),
                        menu=box('.fv-hf__mobile-menu'),summary=box('.fv-hf__mobile-menu summary');
                  const intersection=(a,b)=>Math.max(0,Math.min(a.right,b.right)-Math.max(a.left,b.left))
                    *Math.max(0,Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top));
                  const safe=r=>r.left>=-0.5&&r.right<=innerWidth+0.5;
                  return {
                    docOverflow:document.documentElement.scrollWidth>innerWidth+0.5,
                    ctaHeight:cta.height, summaryHeight:summary.height,
                    ctaSafe:safe(cta), brandSafe:safe(brand), summarySafe:safe(summary),
                    menuOverlapsCTA:intersection(menu,cta)>0,
                    brandOverlapsMenu:intersection(brand,menu)>0,
                    focusHref:document.querySelector('.fv-hf__mast-cta').getAttribute('href'),
                    destinations:[...document.querySelectorAll('.fv-hf__mobile-links a')].map(a=>a.href),
                    chapters:document.querySelectorAll('.fv-hf__chapter-nav a[href^="#"]').length
                  };
                }""")
                faults=[]
                if state["ctaHeight"]<43.5:faults.append("Focus CTA below 44px")
                if not state["ctaSafe"] or not state["brandSafe"]:faults.append("masthead clipped")
                if width<=920:
                    if not state["summarySafe"] or state["summaryHeight"]<43.5:
                        faults.append("Explore site target clipped/undersized")
                    if state["menuOverlapsCTA"] or state["brandOverlapsMenu"]:
                        faults.append("navigation overlays CTA/brand")
                    menu.locator("summary").press("Enter")
                    if menu.evaluate("(x)=>x.open"):faults.append("Enter did not close menu")
                    menu.locator("summary").press("Space")
                    if not menu.evaluate("(x)=>x.open"):faults.append("Space did not reopen menu")
                if width>=320 and state["docOverflow"]:faults.append("page horizontal overflow")
                if state["chapters"]!=7:faults.append("chapter navigation missing")
                if len(state["destinations"])!=3:faults.append("editorial destinations missing")
                if state["focusHref"]!="https://finalvestige.com/focus/":
                    faults.append("Focus route changed")
                if js and width in (160,320,390,768,1440):
                    page.screenshot(path=str(args.out/f"home_{width}_js.png"))
                rows.append({"width":width,"js":js,"pass":not faults,"faults":faults,**state})
                page.close()
        browser.close()
    (args.out/"report.json").write_text(json.dumps({
      "head":actual,"browser":"Chromium","local_exact_checkout":True,
      "wordpress":False,"axe":False,"lighthouse":False,"results":rows
    },indent=2))
    passed=sum(int(r["pass"]) for r in rows)
    print(f"Exact-source Chromium reflow: {passed}/{len(rows)} PASS")
    if passed<len(rows):
        print(json.dumps([x for x in rows if not x["pass"]],indent=2))
        raise SystemExit(1)
if __name__=="__main__":main()
