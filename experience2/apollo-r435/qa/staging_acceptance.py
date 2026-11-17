"""A real HTTPS WordPress/axe/LCP/CLS acceptance gate. Fails closed without approvals."""
import os, sys, json, hashlib
from pathlib import Path
from urllib.parse import urlparse

URL=os.environ.get('FV_R435_STAGING_URL','')
APPROVED=os.environ.get('FV_R435_APPROVED_HOST','')
AXE=os.environ.get('FV_R435_AXE_BUNDLE','')
AXE_HASH=os.environ.get('FV_R435_AXE_SHA256','')
HERE=Path(__file__).resolve().parents[1]
if not URL or not APPROVED or not AXE or not AXE_HASH:
 print('HOLD (2): requires approved HTTPS staging URL+host and exact SHA-reviewed authentic axe bundle')
 sys.exit(2)
parsed=urlparse(URL)
if parsed.scheme!='https' or parsed.hostname!=APPROVED or parsed.username or parsed.password or parsed.fragment or parsed.port not in (None,443):
 print('HOLD (2): host/scheme mismatch')
 sys.exit(2)
p=Path(AXE)
if not p.is_file() or p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=AXE_HASH:
 print('HOLD (2): missing or unreviewed axe bundle')
 sys.exit(2)
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 results=[]
 for width in (320,360,390,768,1440,1920):
  page=browser.new_page(viewport={'width':width,'height':880})
  page.add_init_script('''(() => {window.__fvCWV={lcp:null,cls:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__fvCWV.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__fvCWV.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){window.__fvCWV.error=String(e)}})();''')
  response=page.goto(URL,wait_until='load',timeout=25000)
  if not response or response.status>=400 or page.locator('[data-fv-r435]').count()!=1:
   raise RuntimeError('staging HTTP/component gate failed at '+str(width))
  if page.evaluate('document.documentElement.scrollWidth>innerWidth'):
   raise RuntimeError('staging horizontal overflow '+str(width))
  page.add_script_tag(path=str(p))
  axe=page.evaluate('''async () => {if (!window.axe || typeof axe.run!=="function")throw Error('missing authentic axe');const r=await axe.run(document.querySelector('[data-fv-r435]'), {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return {violations:r.violations.map(x=>({id:x.id,impact:x.impact,nodes:x.nodes.length}))}}''')
  page.wait_for_timeout(1500)
  cwv=page.evaluate('window.__fvCWV')
  if axe['violations'] or cwv['lcp'] is None or cwv['cls'] is None:
   raise RuntimeError('axe/CWV not accepted '+str(width)+': '+str(axe)+str(cwv))
  results.append({'viewport':width,'axe':axe,'lab_lcp_ms':cwv['lcp'],'lab_cls':cwv['cls'],'http_status':response.status})
  page.close()
 browser.close()
(HERE/'QA/staging.json').write_text(json.dumps({'kind':'REAL_STAGING_LAB_NOT_FIELD_P75','tests':results},sort_keys=True,indent=2)+'\n')
print('STAGING QA results captured; independent QD and release gate still required')
