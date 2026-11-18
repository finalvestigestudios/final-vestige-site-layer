#!/usr/bin/env python3
"""Fail-closed *navigated* read-only WordPress staging acceptance; no unauthorised host.
Usage on approved staging runner only:
 FV_APPROVED_STAGING_HOST=staging.example.com FV_APPROVED_AXE_SHA256=<reviewed digest> \
  python qa/hosted_acceptance.py https://staging.example.com/apollo-bridge/ /approved/axe.min.js
No field p75 CWV claimed from a lab navigation. A browser policy block is HOLD_NOT_RUN.
"""
import hashlib,json,os,sys
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1];OUT=BASE/'QA/HOSTED_ACCEPTANCE.json'
report={'status':'HOLD_NOT_RUN','navigation':'HOLD_NOT_RUN','axe_core':'HOLD_NOT_RUN','navigated_LCP':'HOLD_NOT_RUN','navigated_CLS':'HOLD_NOT_RUN','field_CWV':'NOT_OBSERVED','checks':{}}
def stop(msg):
 report['blocker']=msg;OUT.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps(report,sort_keys=True));sys.exit(2)
url=sys.argv[1] if len(sys.argv)>1 else '';axe=Path(sys.argv[2]) if len(sys.argv)>2 else None
host=os.environ.get('FV_APPROVED_STAGING_HOST','');parts=urlsplit(url)
if not host or parts.scheme!='https' or parts.hostname!=host or not parts.path.startswith('/') or parts.username or parts.password or parts.port or parts.query or parts.fragment:stop('Founder-approved staging hostname and clean HTTPS path required')
if not axe or not axe.is_file():stop('Reviewed local axe-core file absent')
sha=hashlib.sha256(axe.read_bytes()).hexdigest()
if not os.environ.get('FV_APPROVED_AXE_SHA256') or sha!=os.environ['FV_APPROVED_AXE_SHA256']:stop('Reviewed axe-core SHA256 mismatch')
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
  for width in [320,390,768,1440,1920]:
   context=b.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');page=context.new_page()
   page.add_init_script('''window.__fv458Metrics={lcp:null,cls:0};
   try{new PerformanceObserver(list=>{for(const e of list.getEntries())window.__fv458Metrics.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){}
   try{new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__fv458Metrics.cls+=e.value;}).observe({type:'layout-shift',buffered:true});}catch(e){}''')
   resp=page.goto(url,wait_until='domcontentloaded',timeout=20000)
   page.wait_for_timeout(1400)
   if not resp or resp.status>=400 or urlsplit(page.url).hostname!=host:raise RuntimeError('Host/HTTP navigation rejected')
   if page.locator('[data-fv458-root]').count()!=1 or page.locator('[data-fv458-record]').count()!=5:raise RuntimeError('R458 component not installed with five records')
   if page.locator('a[href*="the-hatch-opened-inward"]').count()!=1:raise RuntimeError('One free-investigation link requirement failed')
   page.add_script_tag(path=str(axe))
   violations=page.evaluate('''async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))}''')
   metrics=page.evaluate('''()=>({lcp_ms:window.__fv458Metrics.lcp,cls:window.__fv458Metrics.cls,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1})''')
   page.screenshot(path=str(BASE/'QA'/f'hosted-{width}.png'),full_page=True,animations='disabled')
   report['checks'][str(width)]={'http':resp.status,'axe_violations':violations,**metrics};context.close()
  b.close()
 report.update(navigation='RUN',axe_core='RUN',navigated_LCP='MEASURED',navigated_CLS='MEASURED',axe_sha256=sha)
 report['status']='FAIL_REVIEW_REQUIRED' if any(c['axe_violations'] or c['overflow'] or c['lcp_ms'] is None or c['lcp_ms']>2500 or c['cls']>0.1 for c in report['checks'].values()) else 'LAB_MEASURED_NEEDS_QD_REVIEW'
except Exception as err:report['status']='HOLD_NOT_RUN';report['blocker']=str(err)
OUT.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps(report,sort_keys=True))
sys.exit(2 if report['status']=='HOLD_NOT_RUN' else (1 if report['status']=='FAIL_REVIEW_REQUIRED' else 0))
