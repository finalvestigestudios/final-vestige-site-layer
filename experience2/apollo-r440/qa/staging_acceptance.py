"""Read-only real staging browser gate; cannot pretend local set_content is navigated staging."""
import os,hashlib,json,sys
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'QA';QA.mkdir(exist_ok=True)
url=os.environ.get('FV_R440_STAGING_URL','');host=os.environ.get('FV_R440_APPROVED_HOST','')
axe=os.environ.get('FV_R440_AXE_BUNDLE','');sha=os.environ.get('FV_R440_AXE_SHA256','');u=urlparse(url)
result={'kind':'REAL_NAVIGATED_STAGING_GENUINE_AXE_CORE_LCP_CLS_GATE','status':'HOLD','reason':'approved HTTPS staging URL/host and vetted axe bundle required; no installation or live writes'}
if not (host and u.scheme=='https' and u.hostname==host and u.port in (None,443) and not u.username and not u.password and not u.fragment and len(sha)==64 and axe):
 (QA/'staging.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result));sys.exit(2)
p=Path(axe)
if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
 result['reason']='axe-core bundle absent, symlinked or digest mismatch'
 (QA/'staging.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result));sys.exit(2)
from playwright.sync_api import sync_playwright
instrument="""(()=>{window.__fvR440={lcp:null,cls:0};new PerformanceObserver(x=>{for(const e of x.getEntries())window.__fvR440.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(x=>{for(const e of x.getEntries())if(!e.hadRecentInput)window.__fvR440.cls+=e.value}).observe({type:'layout-shift',buffered:true})})()"""
results=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for w in [320,360,390,768,1024,1440,1920]:
   ctx=browser.new_context(viewport={'width':w,'height':900});page=ctx.new_page();page.add_init_script(instrument)
   response=page.goto(url,wait_until='load',timeout=20000)
   if not response or response.status!=200 or page.locator('[data-r440-root]').count()!=1:raise RuntimeError(f'HTTP/component missing at {w}')
   page.add_script_tag(path=str(p));viols=page.evaluate("""async()=>{if(!window.axe?.run)throw Error('axe absent');let r=await axe.run(document.querySelector('[data-r440-root]'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return r.violations.map(v=>({id:v.id,nodes:v.nodes.length}))}""")
   page.wait_for_timeout(1600);m=page.evaluate('window.__fvR440')
   if viols or m['lcp'] is None or m['lcp']>2500 or m['cls']>0.1 or page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):
    raise RuntimeError(f'axe/LCP/CLS/overflow gate at {w}: {viols} {m}')
   results.append({'viewport':w,'axe_violations':viols,**m});ctx.close()
  browser.close()
 result={'kind':'REAL_NAVIGATED_STAGING_GENUINE_AXE_CORE_LCP_CLS_GATE','status':'PASS_LOCAL_LAB_NOT_FIELD_P75','results':results}
except Exception as e:result['reason']=str(e);result['status']='HOLD'
(QA/'staging.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result));sys.exit(0 if result['status'].startswith('PASS') else 2)
