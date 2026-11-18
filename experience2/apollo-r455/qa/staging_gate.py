#!/usr/bin/env python3
"""Real navigated staging-only WCAG / LCP / CLS gate for an APPROVED QA runner.

No live-site writes. Caller must supply a reviewed local axe-core bundle and approved
HTTPS staging page. Never treat offline page.set_content() as navigated performance QA.
"""
import argparse,hashlib,json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser()
parser.add_argument('--staging-url',required=True)
parser.add_argument('--axe-core',required=True,type=Path)
parser.add_argument('--output',type=Path,default=Path('staging-qa'))
args=parser.parse_args()
url=urlsplit(args.staging_url)
if url.scheme!='https' or not url.hostname or url.hostname in ['finalvestige.com','www.finalvestige.com'] or not ('staging' in url.hostname or 'preview' in url.hostname):
    parser.error('Explicit HTTPS staging/preview host required. Production and local file URLs prohibited.')
if not args.axe_core.is_file():parser.error('HOLD: independently reviewed axe-core JS bundle not provided')
args.output.mkdir(parents=True,exist_ok=True)
axe_sha=hashlib.sha256(args.axe_core.read_bytes()).hexdigest()
results=[]
init_js="""window.__fvCWV={lcp:0,cls:0};try{
new PerformanceObserver(list=>{for(const e of list.getEntries())window.__fvCWV.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__fvCWV.cls+=e.value}).observe({type:'layout-shift',buffered:true});
}catch(e){window.__fvCWV.error=String(e)}"""
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for width in [320,360,390,768,1024,1440,1920]:
        for js in [False,True]:
            context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js)
            context.add_init_script(init_js)
            page=context.new_page()
            case={'width':width,'javascript':js,'status':'HOLD'}
            try:
                response=page.goto(args.staging_url,wait_until='networkidle',timeout=30000)
                if not response or response.status>=400:raise RuntimeError('Staging response failed')
                if page.locator('section.fv455').count()!=1:raise RuntimeError('Staging shortcode missing/duplicate')
                if page.locator('section.fv455 .fv455__plate:visible').count()!=4:raise RuntimeError('Not all source cards accessible')
                if not page.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth+1'):raise RuntimeError('Horizontal overflow')
                case['status']='PASS'
                if js:
                    page.add_script_tag(path=str(args.axe_core))
                    axe=page.evaluate("async()=>await axe.run(document.querySelector('.fv455'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag22aa']}})")
                    case['axe_violations']=[{'id':v['id'],'impact':v['impact'],'nodes':len(v['nodes'])} for v in axe['violations']]
                    case['lab_cwv']=page.evaluate('window.__fvCWV')
                    if case['axe_violations'] or case['lab_cwv']['lcp']<=0 or case['lab_cwv']['lcp']>2500 or case['lab_cwv']['cls']>0.1:case['status']='FAIL'
                page.screenshot(path=str(args.output/f'{width}-'+('js' if js else 'nojs')+'.png'),full_page=True)
            except Exception as e:
                case['status']='HOLD_NOT_RUN' if 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(e) else 'FAIL'
                case['error']=str(e)[:400]
            results.append(case)
            context.close()
    browser.close()
receipt={'url':args.staging_url,'axe_bundle_sha256':axe_sha,'results':results,'note':'Lab LCP/CLS on hosted staging only; not CrUX p75. No INP or screen-reader result claimed.'}
(args.output/'staging-results.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
if not all(x['status']=='PASS' for x in results):raise SystemExit(2)
