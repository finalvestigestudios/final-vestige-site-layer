#!/usr/bin/env python3
"""Apollo R262 original-PHP component acceptance, not an installed WordPress or axe test."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
SEAL="f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68"
FREE="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"
def sha(x):return hashlib.sha256(x).hexdigest()
def check(v,m):
 if not v:raise AssertionError(m)
def run(a):
 s,f,o=a.source.resolve(),a.fixture.resolve(),a.out.resolve();o.mkdir(parents=True,exist_ok=True)
 check(sha((f/"manifest.json").read_bytes())==SEAL,"fixture seal")
 for n,h in json.loads((f/"manifest.json").read_text())["files"].items():check(sha((f/n).read_bytes())==h,"fixture "+n)
 ids=json.loads((s/"integrity.json").read_text())
 for n,h in ids["generated_asset_sha256"].items():check(sha((s/"assets"/n).read_bytes())==h,"staged asset "+n)
 css=(s/"assets/apollo-overlays.css").read_text();js=(s/"assets/source-drawer-focus.js").read_text()
 check(css.count("/* START ")==6,"CSS integrity chain")
 def mock(e):
  return json.loads(subprocess.run(["php",str(s/"qa/wp-hook-mock.php")],env=dict(os.environ,**e),capture_output=True,text=True,check=True).stdout)
 good=mock({"SIM_MODE":"original"})
 check(good["hook_priority"]==25 and good["assets_ok"] and "fv-apollo-r262-overlays" in good["styles"] and "fv-apollo-r262-drawer-focus" in good["scripts"],"staging hook")
 for e in [{},{"SIM_MODE":"original","BASE_VALID":"0"},{"SIM_MODE":"original","SIM_ADMIN":"1"},{"SIM_MODE":"original","SIM_SINGULAR":"0"}]:
  st=mock(e);check(not st["scripts"] and not any("r262" in k for k in st["styles"]),"fail-open guard")
 r=json.loads(subprocess.run(["php",str(f/"wp-render-shim-r224.php"),str(f/"fv-ex2-apollo-r224.php"),"normal"],capture_output=True,text=True,check=True).stdout)
 check(r["html"]==(f/"templates/atlas-fragment.html").read_text(),"PHP source drift")
 doc='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+(f/"assets/atlas-scoped.css").read_text()+css+'</style></head><body>'+r["html"]+'</body></html>'
 report={"cases":[],"screenshots":{},"manifest":SEAL,"css_sha256":sha(css.encode()),"js_sha256":sha(js.encode()),"axe":"NOT EXECUTED","wordpress":"NOT TESTED","http_csp":"NOT TESTED"}
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=a.chromium,args=["--no-sandbox"])
  for width in (320,390,768,1440,1920):
   for enabled in (False,True):
    ctx=b.new_context(viewport={"width":width,"height":900},java_script_enabled=enabled,is_mobile=width<=390,has_touch=width<=390,reduced_motion="reduce")
    page=ctx.new_page();requests=[];page.on("request",lambda q:requests.append(q.url));page.set_content(doc)
    if enabled:page.add_script_tag(content=js)
    check(page.locator('a[href^="https://www.nasa.gov/"]').count()==55,"NASA provenance")
    check(page.locator('a[href^="#"]').count()==31,"internal provenance")
    check(page.locator('a[href="'+FREE+'"]').count()==1,"single free next action")
    link=page.locator('a[href="#fv-apollo-source-drawer"]');link.focus();link.press("Enter");page.wait_for_timeout(55)
    state=page.evaluate("() => ({hash:location.hash,open:document.querySelector('#fv-apollo-source-drawer').open,focused:document.activeElement===document.querySelector('#fv-apollo-source-drawer summary'),overflow:document.documentElement.scrollWidth>innerWidth+1})")
    check(state["hash"]=="#fv-apollo-source-drawer" and not state["overflow"] and not requests,"navigation layout")
    if enabled:check(state["open"] and state["focused"],"keyboard focus")
    else:
     check(not state["open"],"native no-JS")
     summary=page.locator("#fv-apollo-source-drawer summary");summary.focus();summary.press("Enter")
     check(page.locator("#fv-apollo-source-drawer").evaluate("(d)=>d.open"),"no-JS details")
    if width in (390,1440):
     name=str(width)+("-js" if enabled else "-nojs")+".png";shot=page.screenshot(animations="disabled");(o/name).write_bytes(shot);report["screenshots"][name]=sha(shot)
    report["cases"].append({"width":width,"js":enabled,"pass":True});ctx.close()
  ctx=b.new_context(viewport={"width":390,"height":900},forced_colors="active",reduced_motion="reduce");page=ctx.new_page();page.set_content(doc);page.add_script_tag(content=js);page.locator('a[href="#fv-apollo-source-drawer"]').click();page.wait_for_timeout(55)
  check(page.locator("#fv-apollo-source-drawer summary").evaluate("(e)=>e===document.activeElement"),"forced colors focus")
  report["cases"].append({"forced_colors":True,"pass":True});ctx.close();b.close()
 report["stable_sha256"]=sha(json.dumps(report,sort_keys=True,separators=(",",":")).encode());(o/"receipt.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"pass":True,"contexts":len(report["cases"]),"receipt_sha256":report["stable_sha256"]}))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--fixture",type=Path,required=True);p.add_argument("--source",type=Path,required=True);p.add_argument("--out",type=Path,required=True);p.add_argument("--chromium",default="/usr/bin/chromium");run(p.parse_args())
