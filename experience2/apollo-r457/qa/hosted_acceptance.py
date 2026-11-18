#!/usr/bin/env python3
"""R457 read-only navigated WordPress staging acceptance; fail-closed axe and vitals.
Usage only on approved runner:
 FV_APPROVED_STAGING_HOST=staging.example.com FV_APPROVED_AXE_SHA256=<digest> \
 python qa/hosted_acceptance.py https://staging.example.com/apollo-gallery/ /approved/axe.min.js
"""
import hashlib,json,os,sys
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'QA'/'HOSTED_ACCEPTANCE.json'
report={'status':'HOLD_NOT_RUN','navigation':'HOLD_NOT_RUN','axe_core':'HOLD_NOT_RUN','navigated_lcp_ms':'HOLD_NOT_RUN','navigated_cls':'HOLD_NOT_RUN','checks':{}}
def stop(msg):
 report['blocker']=msg;OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,sort_keys=True));sys.exit(2)
url=sys.argv[1] if len(sys.argv)>1 else ''
axe=Path(sys.argv[2]) if len(sys.argv)>2 else None
parsed=urlsplit(url)
host=os.environ.get('FV_APPROVED_STAGING_HOST','')
if not host or parsed.scheme!='https' or parsed.hostname!=host or not parsed.path.startswith('/') or parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment:stop('Missing clean HTTPS URL for exact founder-approved staging host')
if not axe or not axe.is_file():stop('Missing independently reviewed local axe-core bundle')
sha=hashlib.sha256(axe.read_bytes()).hexdigest()
if not os.environ.get('FV_APPROVED_AXE_SHA256') or sha!=os.environ['FV_APPROVED_AXE_SHA256']:stop('axe-core SHA-256 does not match approved reviewed bundle')
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
  for width in [320,390,768,1440,1920]:
   context=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
   page=context.new_page()
   page.add_init_script('''window.__fv457Vitals={lcp:[],cls:0};
      new PerformanceObserver(l=>{for(const e of l.getEntries())window.__fv457Vitals.lcp.push(e.startTime)}).observe({type:'largest-contentful-paint',buffered:true});
      new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__fv457Vitals.cls+=e.value}).observe({type:'layout-shift',buffered:true});''')
   response=page.goto(url,wait_until='networkidle',timeout=25000)
   if not response or response.status>=400 or urlsplit(page.url).hostname!=host:raise RuntimeError('Non-success / redirect off approved staging host')
   if page.locator('[data-fv457-root]').count()!=1 or page.locator('[data-fv457-card]').count()!=6:raise RuntimeError('R457 component not installed or missing catalogue records')
   if page.locator('[data-fv457-root] a[href*="the-hatch-opened-inward"]').count()!=1:raise RuntimeError('One free article CTA contract broken')
   page.add_script_tag(path=str(axe))
   violations=page.evaluate('''async()=>{const a=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return a.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))}''')
   metrics=page.evaluate('''()=>({lcp_ms:window.__fv457Vitals.lcp.at(-1)??null,cls:window.__fv457Vitals.cls,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1})''')
   page.screenshot(path=str(BASE/'QA'/f'hosted-{width}.png'),full_page=True,animations='disabled')
   report['checks'][str(width)]={'http':response.status,'axe_violations':violations,**metrics}
   context.close()
  browser.close()
 report.update(navigation='RUN',axe_core='RUN',navigated_lcp_ms='MEASURED',navigated_cls='MEASURED',axe_sha256=sha)
 report['status']='FAIL_REVIEW_REQUIRED' if any(c['axe_violations'] or c['overflow'] or c['lcp_ms'] is None or c['lcp_ms']>2500 or c['cls']>0.1 for c in report['checks'].values()) else 'MEASURED_NEEDS_INDEPENDENT_ACCEPTANCE'
except Exception as exc:
 report['status']='HOLD_NOT_RUN';report['blocker']=str(exc)
OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,sort_keys=True))
if report['status']=='HOLD_NOT_RUN':sys.exit(2)
if report['status']=='FAIL_REVIEW_REQUIRED':sys.exit(1)
