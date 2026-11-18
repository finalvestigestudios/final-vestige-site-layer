#!/usr/bin/env python3
"""Read-only, explicitly authorized HTTPS WordPress staging Playwright + genuine pinned axe-core + navigated LCP/CLS.
Never claims PASS on missing authorization, missing bundle, blocked navigation, or incomplete performance evidence.
"""
import hashlib,json,os,sys
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'QA/HOSTED_ACCEPTANCE.json'
SHOTS=ROOT/'QA/hosted_screenshots'
def result(status,reason,details=None):
    OUTPUT.write_text(json.dumps({'sprint':'R458','status':status,'reason':reason,'details':details or [],'field_CWV':'UNVERIFIED','manual_screen_reader':'NOT_RUN'},indent=2,sort_keys=True)+'\n')
    print(f'{status}: {reason}')
    return 0 if status=='PASS_LAB_ONLY' else 2
url=os.getenv('FV_R458_APPROVED_STAGING_URL','').strip()
host=os.getenv('FV_R458_APPROVED_HOST','').strip().lower()
axe_path=Path(os.getenv('FV_R458_AXE_CORE_PATH','/nonexistent'))
axe_sha=os.getenv('FV_R458_AXE_SHA256','').strip().lower()
if not url or not host:returncode=result('HOLD_NOT_RUN','Approved staging URL and exact host are required');sys.exit(returncode)
u=urlparse(url)
if u.scheme!='https' or u.hostname!=host or u.username or u.password or u.port or u.fragment:
    sys.exit(result('HOLD_NOT_RUN','HTTPS staging URL / host identity mismatch'))
if not axe_path.is_file() or len(axe_sha)!=64 or hashlib.sha256(axe_path.read_bytes()).hexdigest()!=axe_sha:
    sys.exit(result('HOLD_NOT_RUN','Reviewed local axe-core bundle with exact SHA-256 is mandatory'))
axe=axe_path.read_text(encoding='utf-8')
metrics_script='''
(()=>{window.__fv458Lab={lcp:null,cls:0,observer_ready:false};try{
new PerformanceObserver(list=>{for(const e of list.getEntries())window.__fv458Lab.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__fv458Lab.cls+=e.value}).observe({type:'layout-shift',buffered:true});
window.__fv458Lab.observer_ready=true;
}catch(e){window.__fv458Lab.error=String(e)}})();'''
all_results=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
  for width in [320,360,390,768,1024,1440,1920]:
   for js in [True,False]:
    ctx=browser.new_context(viewport={'width':width,'height':850},java_script_enabled=js,service_workers='block')
    pg=ctx.new_page();pg.set_default_timeout(10000)
    if js:pg.add_init_script(metrics_script)
    response=pg.goto(url,wait_until='domcontentloaded',timeout=25000)
    if urlparse(pg.url).hostname!=host:raise RuntimeError('Unexpected cross-host redirect')
    if response is None or response.status!=200:raise RuntimeError(f'Unexpected staging HTTP {response.status if response else "none"}')
    pg.locator('[data-fv458-root]').first.wait_for(timeout=10000)
    pg.wait_for_timeout(1100)
    overflow=pg.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
    count=pg.locator('[data-fv458-card]').count()
    controls=pg.locator('[data-fv458-tools]').is_visible()
    row={'width':width,'javascript':js,'overflow_ok':overflow,'records':count,'filters_visible':controls,'status':'PASS'}
    if not overflow or count!=6 or controls!=js:raise RuntimeError('Incomplete or overflowing staging component: '+str(row))
    if js:
     pg.add_script_tag(content=axe)
     audit=pg.evaluate('async () => {if(typeof axe=== "undefined" || typeof axe.run!=="function") throw Error("axe core absent"); const r=await axe.run(document.querySelector("[data-fv458-root]"),{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa","wcag22aa"]}});return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),incomplete:r.incomplete.map(v=>v.id)}}')
     row['axe']=audit
     if audit['violations'] or audit['incomplete']:raise RuntimeError('axe review not clean; inspect report '+str(audit))
     lab=pg.evaluate('window.__fv458Lab')
     row['lab_metrics']=lab
     if not lab.get('observer_ready') or lab.get('lcp') is None:raise RuntimeError('No navigated LCP entry: not a performance pass')
     if lab['lcp']>2500 or lab['cls']>0.1:raise RuntimeError('LCP/CLS budget miss '+str(lab))
    SHOTS.mkdir(exist_ok=True,parents=True)
    pg.screenshot(path=str(SHOTS/f'{width}-{"js" if js else "nojs"}.png'),full_page=True,animations='disabled')
    all_results.append(row)
    ctx.close()
  browser.close()
except Exception as e:
    sys.exit(result('HOLD_NOT_RUN',f'Hosted acceptance incomplete: {str(e)[:350]}',all_results))
sys.exit(result('PASS_LAB_ONLY','Authorized hosted navigation, axe and lab LCP/CLS passed; field CWV and manual screen-reader gates remain open',all_results))
