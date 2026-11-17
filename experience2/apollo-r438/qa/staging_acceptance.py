"""Read-only navigated HTTPS staging gate. Fail closed without approved host + genuine SHA-pinned axe."""
import os,json,hashlib,sys
from pathlib import Path
from urllib.parse import urlparse
HERE=Path(__file__).resolve().parents[1]
url=os.getenv('FV_R438_STAGING_URL','');host=os.getenv('FV_R438_APPROVED_HOST','')
axe=os.getenv('FV_R438_AXE_BUNDLE','');digest=os.getenv('FV_R438_AXE_SHA256','')
u=urlparse(url)
if not (host and axe and len(digest)==64 and u.scheme=='https' and u.hostname==host and not u.username and not u.password and u.port in (None,443) and not u.fragment):
 print('HOLD (2): approved staging HTTPS URL / host / genuine verified axe-core required');sys.exit(2)
bundle=Path(axe)
if bundle.is_symlink() or not bundle.is_file() or hashlib.sha256(bundle.read_bytes()).hexdigest()!=digest:
 print('HOLD (2): absent or SHA-mismatched genuine axe-core');sys.exit(2)
from playwright.sync_api import sync_playwright
instrument="""(()=>{window.__fvR438={lcp:null,cls:0};new PerformanceObserver(l=>{for(const e of l.getEntries())window.__fvR438.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__fvR438.cls+=e.value}).observe({type:'layout-shift',buffered:true})})();"""
results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for width in [320,360,390,768,1024,1440,1920]:
  context=browser.new_context(viewport={'width':width,'height':900});page=context.new_page();page.add_init_script(instrument)
  resp=page.goto(url,timeout=30000,wait_until='load')
  if not resp or resp.status!=200:raise RuntimeError(f'HTTP failed at {width}')
  if page.locator('[data-r438-atlas-root]').count()!=1 or page.locator('[data-r438-card]').count()!=5 or page.locator('.fv-r429__cta').count()!=1:raise RuntimeError(f'content gate failed at {width}')
  if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):raise RuntimeError(f'overflow {width}')
  page.add_script_tag(path=str(bundle))
  violations=page.evaluate("""async()=>{if(!window.axe?.run)throw Error('genuine axe missing');const r=await axe.run(document.querySelector('[data-r438-atlas-root]'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.length}))}""")
  page.wait_for_timeout(1400);metric=page.evaluate('window.__fvR438')
  if violations or metric['lcp'] is None or metric['lcp']>2500 or metric['cls']>0.1:raise RuntimeError(f'axe/CWV budget hold {width}: {violations} {metric}')
  results.append({'viewport':width,'axe':violations,**metric});context.close()
 browser.close()
(HERE/'QA/staging.json').write_text(json.dumps({'kind':'NAVIGATED_STAGING_LAB_NOT_FIELD_P75','results':results},indent=2)+'\n')
print('PASS navigated staging lab; does not replace screen-reader QD, field CWV or founder approval')
