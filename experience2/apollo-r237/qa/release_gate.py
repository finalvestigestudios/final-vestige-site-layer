#!/usr/bin/env python3
"""Apollo R237 source/commerce/browser gate. Offline STAGING ONLY; never a production signoff."""
import argparse, hashlib, json, re, shutil, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

PIN="f9169870eb3c02415feaf70eed9bbefdca5b194c6ddb27a92a0b80102ef1ce95"
HTML_PIN="50dbe79bbb223762a01614e52fd7a5098784a7d2bd04ceadd2ac69cdf43d3bb6"
CTA="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"
SOURCES=(
 ("Apollo 204 Review Board","Apollo 204 Review Board report","https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/","#fv-apollo-finding-fire"),
 ("S66-58038","NASA photograph S66-58038","https://www.nasa.gov/image-detail/amf-s66-58038/","#fv-apollo-photo-1966"),
 ("S67-15717","NASA photograph S67-15717","https://www.nasa.gov/image-detail/amf-s67-15717/","#fv-apollo-photo-prep"),
 ("S67-21294","NASA photograph S67-21294","https://www.nasa.gov/image-detail/amf-s67-21294/","#fv-apollo-photo-aftermath"),
)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def validate(root):
 assert sha(root/"manifest.json")==PIN,"R236 artifact manifest changed"
 manifest=json.loads((root/"manifest.json").read_text())
 for rel,hash_value in manifest["files"].items():
  assert sha(root/rel)==hash_value,"Protected artifact drift: "+rel
 assert sha(root/"templates/atlas-fragment.html")==HTML_PIN
 html=(root/"templates/atlas-fragment.html").read_text()
 custody=json.loads((root/"source-context-plates.json").read_text())
 commerce=json.loads((root/"commercial-offer-gate.json").read_text())
 sales=json.loads((root/"conversion-validation.json").read_text())
 assert commerce["activation"]=="disabled" and commerce["paid_cta_rendered"] is False
 for field in ("seller_verified","rights_clearance_verified","price_verified","checkout_fulfillment_verified","founder_production_approval"):
  assert commerce[field] is False,field
 assert commerce["confirmed_orders"] is None and commerce["realized_net_revenue"] is None
 assert sales["merchant_confirmed_orders"] is None and sales["realized_net_revenue"] is None
 assert sales["published_grok_apollo_asset_id"] is None
 assert custody["paid_offer_approved"] is False and custody["rights_clearance"]=="NOT_CERTIFIED"
 assert [s["source_id"] for s in custody["source_records"]]==[s[0] for s in SOURCES]
 for record,(_,label,url,target) in zip(custody["source_records"],SOURCES):
  assert record["url"]==url and record["context_anchor"]==target
  assert record["supports"] and record["limitation"] and record["date_role"]
  assert f'aria-label="Verify at NASA: {label}"' in html
  assert f'aria-label="Find {label} in the investigation"' in html
 assert len(re.findall(r'<a\b[^>]*class="cta"',html))==1
 assert re.search(r'<a\b[^>]*class="cta"[^>]*href="'+re.escape(CTA)+'"',html)
 assert not re.search(r'<(?:script|iframe|form)\b|\bon(?:click|load|error)\s*=|awin1\.com|payhip\.com|utm_campaign|data-latitude|data-longitude',html,re.I)
 return html,(root/"assets/atlas-scoped.css").read_text()

def mutations(root):
 tests={
  "fake_orders":("commercial-offer-gate.json",'"confirmed_orders": null','"confirmed_orders": 5'),
  "fake_seller":("commercial-offer-gate.json",'"seller_verified": false','"seller_verified": true'),
  "fake_grok_asset":("conversion-validation.json",'"published_grok_apollo_asset_id": null','"published_grok_apollo_asset_id": "unverified"'),
  "fake_source":("source-context-plates.json",'"source_id": "S66-58038"','"source_id": "FALSE_TELEMETRY"'),
  "missing_limit":("source-context-plates.json",'"limitation": "Not a photograph of the January 1967 fire."','"limitation": ""'),
  "redirect_cta":("templates/atlas-fragment.html",CTA,"https://merchant.example/buy"),
  "insert_script":("templates/atlas-fragment.html",'class="fv-apollo-atlas"','class="fv-apollo-atlas"><script></script>'),
  "fake_nasa_url":("templates/atlas-fragment.html","https://www.nasa.gov/image-detail/amf-s67-15717/","https://fake.example/")
 }
 for label,(rel,old,new) in tests.items():
  with tempfile.TemporaryDirectory(prefix="apollo-r237-") as temp:
   p=Path(temp)/"stage";shutil.copytree(root,p)
   f=p/rel;src=f.read_text();assert old in src,label;f.write_text(src.replace(old,new,1))
   try:validate(p)
   except AssertionError:pass
   else:raise AssertionError("Undetected mutation: "+label)
 return list(tests)

def browser(html,css,qa,axe_path):
 doc='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style><body>'+html+"</body>"
 hashes={};times={};axe_runs={}
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path="/usr/bin/chromium",headless=True,args=["--no-sandbox"])
  for width in (320,390,768,1440,1920):
   for js in (False,True):
    context=b.new_context(viewport={"width":width,"height":900},java_script_enabled=js,is_mobile=width<=390,has_touch=width<=390,reduced_motion="reduce",forced_colors="active" if width==768 else "none")
    page=context.new_page();requests=[];page.on("request",lambda r:requests.append(r.url))
    page.set_content(doc,wait_until="load")
    assert not requests and page.evaluate("document.documentElement.scrollWidth<=innerWidth"),(width,js,"network or overflow")
    assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
    cta=page.locator("a.cta");assert cta.count()==1 and cta.get_attribute("href")==CTA
    rect=cta.bounding_box();assert rect and rect["height"]>=44 and rect["width"]>=44
    drawer=page.locator("details.fv-apollo-source-drawer");assert drawer.count()==1
    if width<=390:drawer.locator("summary").tap()
    else:drawer.locator("summary").press("Enter")
    assert drawer.get_attribute("open") is not None
    for sid,label,url,target in SOURCES:
     plate=page.locator('[data-fv-plate-source="'+sid+'"]')
     assert plate.count()==1
     assert plate.get_by_role("link",name="Verify at NASA: "+label,exact=True).get_attribute("href")==url
     assert plate.get_by_role("link",name="Find "+label+" in the investigation",exact=True).get_attribute("href")==target
    assert page.evaluate("""() => {let ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return ids.length===new Set(ids).size && [...document.querySelectorAll('a[href^="#"]')].every(a=>document.getElementById(a.hash.slice(1))) }""")
    if js:
     perf=page.evaluate("""async () => {
      let l=[],s=[];new PerformanceObserver(x=>x.getEntries().forEach(e=>l.push(e.startTime))).observe({type:'largest-contentful-paint',buffered:true});
      new PerformanceObserver(x=>x.getEntries().forEach(e=>{if(!e.hadRecentInput)s.push(e.value)})).observe({type:'layout-shift',buffered:true});
      await new Promise(r=>setTimeout(r,450));return {lcp_ms:l.length?Math.round(Math.max(...l)):null,cls_observed:s.reduce((a,b)=>a+b,0)}
     }""")
     assert perf["lcp_ms"] is not None;times[str(width)]=perf
     if axe_path:
      page.add_script_tag(content=axe_path.read_text())
      result=page.evaluate("""async ()=>{if(!window.axe?.version)throw Error('Missing real axe-core');let r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return {version:axe.version,violations:r.violations.map(v=>v.id),incomplete:r.incomplete.length}}""")
      axe_runs[str(width)]=result
      assert not result["violations"],result
    name=str(width)+("-js" if js else "-nojs")+".png";shot=qa/name
    page.screenshot(path=str(shot),full_page=True,animations="disabled");hashes[name]=sha(shot)
    context.close()
  b.close()
 return hashes,times,axe_runs

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",required=True,type=Path);ap.add_argument("--qa",required=True,type=Path);ap.add_argument("--axe-core",type=Path)
 a=ap.parse_args();assert not a.qa.exists(),"No evidence overwrites"
 if a.axe_core:assert a.axe_core.is_file(),"Supply an authentic, locally reviewed axe-core bundle"
 html,css=validate(a.out);cases=mutations(a.out);a.qa.mkdir(parents=True)
 shots,times,axe=browser(html,css,a.qa,a.axe_core)
 receipt={"run":"R237","source_manifest_sha256":PIN,"template_sha256":HTML_PIN,"mutations_rejected":cases,"screenshots_sha256":shots,
  "contexts":10,"axe_executed":bool(a.axe_core),"http_navigation_tested":False,"installed_wordpress_tested":False,
  "production_lcp_cls_tested":False,"release":"STAGING_HOLD"}
 (a.qa/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
 (a.qa/"fixture_performance_not_field.json").write_text(json.dumps({"local_fixture_metrics":times,"axe_details":axe},indent=2,sort_keys=True)+"\n")
 print(json.dumps({"receipt_sha256":sha(a.qa/"receipt.json"),"contexts":10,"mutations_rejected":len(cases),"axe_executed":bool(a.axe_core),"release":"STAGING_HOLD"}))
if __name__=="__main__":main()
