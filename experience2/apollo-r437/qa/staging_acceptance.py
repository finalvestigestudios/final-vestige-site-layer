"""Authentic, read-only, navigated HTTPS WP staging + SHA-reviewed axe + lab LCP/CLS gate.
No submission, no page write, no merchant calls. Missing access/bundle => HOLD exit 2.
"""
import hashlib, json, os, sys
from pathlib import Path
from urllib.parse import urlparse
HERE=Path(__file__).resolve().parents[1]
url=os.environ.get('FV_R437_STAGING_URL','')
host=os.environ.get('FV_R437_APPROVED_HOST','')
axe=os.environ.get('FV_R437_AXE_BUNDLE','')
expected=os.environ.get('FV_R437_AXE_SHA256','')
parsed=urlparse(url)
if (not host or not axe or not expected or parsed.scheme!='https' or parsed.hostname!=host
    or parsed.username or parsed.password or parsed.port not in (None,443) or parsed.fragment):
 print('HOLD (2): explicit approved HTTPS staging URL/host and authentic axe bundle SHA required')
 sys.exit(2)
bundle=Path(axe)
if bundle.is_symlink() or not bundle.is_file() or hashlib.sha256(bundle.read_bytes()).hexdigest()!=expected:
 print('HOLD (2): missing or SHA-mismatched authentic axe bundle')
 sys.exit(2)
from playwright.sync_api import sync_playwright
measure='''(()=>{window.__FV_R437_METRICS={lcp_ms:null,cls:0};new PerformanceObserver(l=>{for(const e of l.getEntries())window.__FV_R437_METRICS.lcp_ms=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__FV_R437_METRICS.cls+=e.value}).observe({type:'layout-shift',buffered:true})})();'''
results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for width in [320,360,390,768,1024,1440,1920]:
  context=browser.new_context(viewport={'width':width,'height':900})
  page=context.new_page();page.add_init_script(measure)
  response=page.goto(url,wait_until='load',timeout=30000)
  if response is None or response.status!=200:raise RuntimeError(f'staging HTTP status not 200 at {width}')
  if page.locator('[data-fv-r437]').count()!=1:raise RuntimeError(f'expected exactly one R437 instance at {width}')
  if page.locator('[data-fv-r437] [data-period]').count()!=4:raise RuntimeError(f'missing source records at {width}')
  if page.locator('.fv-r429__cta').count()!=1:raise RuntimeError(f'missing or duplicate original CTA at {width}')
  if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):raise RuntimeError(f'overflow at {width}')
  page.add_script_tag(path=str(bundle))
  ax=page.evaluate('''async()=>{if(!window.axe || !window.axe.run)throw Error('authentic axe missing');const r=await axe.run(document.querySelector('[data-fv-r437]'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return r.violations.map(x=>({id:x.id,impact:x.impact,nodes:x.nodes.length}))}''')
  page.wait_for_timeout(1300)
  m=page.evaluate('window.__FV_R437_METRICS')
  if ax:raise RuntimeError(f'axe WCAG violations at {width}: {ax}')
  if m['lcp_ms'] is None or m['lcp_ms']>2500 or m['cls']>0.1:raise RuntimeError(f'lab LCP/CLS outside budget at {width}: {m}')
  results.append({'viewport':width,'http_status':response.status,'axe_violations':ax,'lab_lcp_ms':m['lcp_ms'],'lab_cls':m['cls']})
  context.close()
 browser.close()
(HERE/'QA').mkdir(exist_ok=True)
(HERE/'QA/staging.json').write_text(json.dumps({'kind':'AUTHENTIC_NAVIGATED_WP_STAGING_LAB_NOT_FIELD_P75','results':results},indent=2,sort_keys=True)+'\n')
print('Staging lab gate PASS; independent QD, field p75 and founder release approval still required')
