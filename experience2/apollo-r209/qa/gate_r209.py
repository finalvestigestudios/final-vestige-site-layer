#!/usr/bin/env python3
"""R209 local PHP/Chromium audit. Not axe, installed WP or production performance."""
from __future__ import annotations
import hashlib,json,re,subprocess,sys
from pathlib import Path
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
def sha(b):return hashlib.sha256(b).hexdigest()
class Audit(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.refs=[];self.hrefs=[];self.duplicate=[]
 def handle_starttag(self,t,attrs):
  if sum(k=="id" for k,v in attrs)>1:self.duplicate.append(t)
  d=dict(attrs)
  if d.get("id"):self.ids.append(d["id"])
  for a in ("aria-labelledby","aria-describedby"):
   if d.get(a):self.refs+=d[a].split()
  if t=="a" and d.get("href"):self.hrefs.append(d["href"])
def check(html):
 a=Audit();a.feed(html)
 assert not a.duplicate and len(a.ids)==len(set(a.ids))
 assert all(x in a.ids for x in a.refs)
 assert all(h[1:] in a.ids for h in a.hrefs if h.startswith("#"))
 assert html.count('class="cta"')==1
 assert "The claim the photograph cannot settle." in html
 assert 'datetime="1967-04"' in html and 'datetime="1967-01-27"' in html
 assert 'datetime="1967-01-28"' in html
 assert "NASA does not endorse Final Vestige" in html
 assert not re.search(r"(buy now|add to cart|limited time)",html,re.I)
 return a
def run(out):
 out.mkdir(parents=True,exist_ok=True)
 man=json.loads((DIST/"manifest.json").read_text())
 assert man["upstream_R198_reconciled"] is False
 for p,h in man["files"].items():assert sha((DIST/p).read_bytes())==h,p
 assert subprocess.run(["php","-l",str(DIST/"fv-ex2-apollo-r209.php")],capture_output=True).returncode==0
 shim=DIST/"wp-render-shim-r209.php";plugin=DIST/"fv-ex2-apollo-r209.php"
 def render(mode):return json.loads(subprocess.check_output(["php",str(shim),str(plugin),mode]))
 normal=render("normal");late=render("late");printed=render("printed")
 assert not normal["fallback"] and normal["css"]=="enqueued"
 assert late["fallback"] and not printed["fallback"]
 html=normal["html"];a=check(html)
 negative={
  "bad_target":html.replace('href="#fv-apollo-chronology"','href="#missing"',1),
  "fake_sale":html.replace("Independent original teaching prompt","Buy now. Independent original teaching prompt"),
  "false_rights":html.replace("NASA does not endorse Final Vestige","NASA endorses Final Vestige"),
  "duplicate_id":html.replace('id="fv-apollo-source-test"','id="fv-apollo-source-test" id="fv-apollo-source-test"'),
 }
 rejected=[]
 for label,m in negative.items():
  try:check(m)
  except AssertionError:rejected.append(label)
 assert len(rejected)==len(negative),set(negative)-set(rejected)
 css=(DIST/"assets/atlas-scoped.css").read_text()
 body='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>'
 tests=[("320",320,{}),("390",390,{}),("768",768,{}),("1440",1440,{}),("1920",1920,{}),("390-nojs",390,{"java_script_enabled":False}),("390-touch",390,{"has_touch":True,"is_mobile":True}),("390-reduced",390,{"reduced_motion":"reduce"}),("390-forced",390,{"forced_colors":"active"})]
 receipts=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path="/usr/bin/chromium",args=["--no-sandbox"])
  for label,width,opts in tests:
   context=browser.new_context(viewport={"width":width,"height":900},**opts)
   page=context.new_page();errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
   page.set_content(body,wait_until="domcontentloaded")
   details=page.locator(".fv-apollo-lesson-key");details.locator("summary").focus()
   page.keyboard.press("Enter");assert details.evaluate("(e)=>e.open")
   page.keyboard.press("Enter");assert not details.evaluate("(e)=>e.open")
   assert page.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth+1")
   assert page.locator(".fv-apollo-atlas a.cta").count()==1 and not errors
   shot=page.screenshot(path=str(out/(label+".png")),full_page=True,animations="disabled")
   receipts.append({"case":label,"width":width,"sha256":sha(shot),"errors":errors})
   context.close()
  version=browser.version;browser.close()
 result={"source":"R209", "chromium":version,"screenshots":receipts,"negative_mutations_rejected":rejected,
 "axe_executed":False,"installed_WordPress":False,"CI_verified":False,"R198_reconciled":False}
 (out/"receipt.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 return result
if __name__=="__main__":print(json.dumps(run(Path(sys.argv[1] if len(sys.argv)>1 else "/tmp/apollo-r209-qa")),indent=2))
