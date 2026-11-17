"""Read-only real HTTPS staging runner. Fails HOLD if approval, navigation or axe absent."""
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parents[1]
QA = HERE/'QA'
QA.mkdir(parents=True,exist_ok=True)


def main():
    result={'status':'HOLD','target':'not supplied','axe':'NOT_EXECUTED','navigation':'NOT_EXECUTED',
            'lcp_ms':None,'cls':None,'field_p75':'NOT_MEASURED','wordpress_install':'NOT_VERIFIED'}
    url=os.environ.get('FV_R434_APPROVED_STAGING_URL','').strip()
    host=os.environ.get('FV_R434_APPROVED_HOST','').strip().lower()
    axe=os.environ.get('FV_R434_REVIEWED_AXE_PATH','').strip()
    expected=os.environ.get('FV_R434_REVIEWED_AXE_SHA256','').strip().lower()
    target=urlparse(url)
    if not(url.startswith('https://') and host and target.hostname==host
           and host!='finalvestige.com' and host!='www.finalvestige.com' and not target.username and not target.password):
        result['blocker']='Explicit nonproduction HTTPS URL + separately approved hostname required'
    elif not (axe and Path(axe).is_file() and len(expected)==64 and hashlib.sha256(Path(axe).read_bytes()).hexdigest()==expected):
        result['blocker']='Locally reviewed authentic axe-core JS + exact SHA256 required'
    else:
        result['target']=url
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('FV_R434_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
            try:
                page=browser.new_page(viewport={'width':390,'height':850},reduced_motion='reduce')
                page.add_init_script('''(() => {
                  window.__fvVitals={lcp:0,cls:0};
                  new PerformanceObserver(list=>{for(const e of list.getEntries())window.__fvVitals.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
                  new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__fvVitals.cls+=e.value}).observe({type:'layout-shift',buffered:true});
                })()''')
                response=page.goto(url,wait_until='networkidle',timeout=30000)
                assert response and response.ok, 'Staging HTTP response failed'
                assert page.locator('[data-fv-r434]').count()>=1, 'Expected staged R434 not installed'
                page.add_script_tag(path=axe)
                violations=page.evaluate('''async()=> (await window.axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))''')
                result.update({'navigation':'PASS_HTTPS_STAGING','wordpress_install':'R434_RENDERED_ON_APPROVED_URL',
                               'axe':'PASS' if not violations else 'FAIL','axe_violations':violations,
                               'lcp_ms':page.evaluate('window.__fvVitals.lcp'),
                               'cls':page.evaluate('window.__fvVitals.cls')})
                if violations or not (0<result['lcp_ms']<=2500) or result['cls']>0.1:
                    result.update({'status':'FAIL','blocker':'axe violations or local LCP/CLS budget exceeded'})
                else:
                    result.update({'status':'PASS_LAB_ONLY','blocker':'Manual screen reader, CI/QD, field p75 and founder release still pending'})
                page.screenshot(path=str(QA/'approved-staging-390.png'),full_page=True)
            except Exception as e:
                result.update({'status':'HOLD','navigation':'FAILED','blocker':type(e).__name__+': '+str(e)[:350]})
            finally:
                browser.close()
    (QA/'staging-acceptance.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status']+': '+result.get('blocker',''))
    raise SystemExit(0 if result['status']=='PASS_LAB_ONLY' else 2)

if __name__=='__main__':main()
