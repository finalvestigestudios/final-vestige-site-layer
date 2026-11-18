"""Fail-closed hosted QA: requires explicitly approved STAGING URL and vetted local axe bundle.
No URL means HOLD_NOT_RUN. Does not install WP, modify site, subscribe or place orders.
"""
from pathlib import Path
import os,sys,json,urllib.parse,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA/r465-hosted'
url=os.getenv('FV_R465_STAGING_URL','')
host=os.getenv('FV_R465_APPROVED_HOST','')
axe=os.getenv('FV_R465_AXE_PATH','')
axe_sha=os.getenv('FV_R465_AXE_SHA256','')
p=urllib.parse.urlparse(url)
if not (p.scheme=='https' and p.hostname and p.hostname==host and host not in ('finalvestige.com','www.finalvestige.com') and not p.username and not p.password and not p.fragment and not p.query and axe and axe_sha and Path(axe).is_file() and hashlib.sha256(Path(axe).read_bytes()).hexdigest()==axe_sha):
    print(json.dumps({'status':'HOLD_NOT_RUN','reason':'Exact approved nonproduction HTTPS host and SHA-256 pinned local axe-core bundle required; no navigated QA attempted.'}))
    sys.exit(2)
OUT.mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
    for w in (320,390,768,1440,1920):
        context=browser.new_context(viewport={'width':w,'height':900},reduced_motion='reduce')
        page=context.new_page()
        page.add_init_script('''(() => {
            window.__fvWebVitals = {lcp:null,cls:0};
            new PerformanceObserver(list=>{for(const e of list.getEntries()) window.__fvWebVitals.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
            new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput) window.__fvWebVitals.cls+=e.value}).observe({type:'layout-shift',buffered:true});
        })();''')
        page.goto(url,wait_until='load',timeout=30000)
        page.wait_for_timeout(3000)
        assert page.locator('[data-fv457-root]').count()==1,'Staging shortcode missing; cannot pass QA'
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),'Horizontal overflow'
        page.add_script_tag(path=axe)
        violations=page.evaluate('''async () => (await axe.run(document.querySelector('[data-fv457-root]'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))''')
        vitals=page.evaluate('window.__fvWebVitals')
        shot=OUT/f'{w}-navigated.png';page.screenshot(path=str(shot),full_page=True,animations='disabled')
        results.append({'width':w,'navigated_url':url,'axe_violations':violations,'vitals_navigation_observed':vitals,'screenshot':shot.name})
        context.close()
    browser.close()
report={'status':'FAIL' if any(x['axe_violations'] or x['vitals_navigation_observed']['lcp'] is None for x in results) else 'MEASURED_REVIEW_REQUIRED','note':'Navigation lab LCP/CLS are not field p75 and require performance budget review; no claim of CWV pass.','results':results}
(OUT/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report,indent=2))
sys.exit(1 if report['status']=='FAIL' else 0)
