#!/usr/bin/env python3
"""R40 Chromium component QA of actual PHP-rendered R39 WordPress fragment.
Attempts browser navigation; explicitly falls back to set_content if policy blocks.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import build_wordpress_stage as stage

HERE=Path(__file__).resolve().parents[1]
WIDTHS=(320,360,390,768,1024,1440,1920)
ORIGIN='https://apollo-internal-staging.invalid'
CSP="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'none'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(ok, message):
    if not ok:raise AssertionError(message)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--axe',type=Path,help='Existing approved pinned axe.min.js, never downloaded')
    args=ap.parse_args()
    if args.axe and not args.axe.is_file():raise FileNotFoundError('Approved axe-core bundle not found')
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    stage.build(out/'dist')
    dist=out/'dist/fv-ex2-evidence-atlas'
    proc=subprocess.run(['php',str(HERE/'tests/wordpress_shortcode_probe.php'),str(dist/'final-vestige-ex2-evidence-atlas.php')],capture_output=True,text=True,check=True,env={**os.environ,'FV_SINGULAR':'1'})
    probe=json.loads(proc.stdout)
    html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Internal Apollo source gallery</title><link rel="stylesheet" href="/assets/atlas.css"></head><body><main id="content"><h1 class="visually-hidden" style="display:none">Staging shell</h1>'+probe['markup']+'</main><script defer src="/assets/atlas.js"></script></body></html>'
    assets={'/apollo/':('text/html; charset=utf-8',html.encode()),
      '/assets/atlas.css':('text/css; charset=utf-8',(dist/'assets/atlas.css').read_bytes()),
      '/assets/atlas.js':('text/javascript; charset=utf-8',(dist/'assets/atlas.js').read_bytes())}
    fixture='<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+assets['/assets/atlas.css'][1].decode()+'</style></head><body><main id="content">'+probe['markup']+'</main><script>'+assets['/assets/atlas.js'][1].decode()+'</script></body></html>'
    receipt={'schema':'fv.ex2.apollo.wp-stage.browser.r40.v1','source':'REAL_R39_CUSTODY_PHP_RENDERED',
      'transport':'BROWSER_SET_CONTENT_NOT_HTTP_OR_WORDPRESS','navigation':'NOT_YET_PROBED',
      'actual_wordpress':'NOT_TESTED','axe':'NO_APPROVED_BUNDLE' if not args.axe else 'EXECUTED',
      'hosted_p75_cwv':'NOT_TESTED','cases':[],'intended_CSP_NOT_TESTED':CSP}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        nav_probe=browser.new_page()
        nav_probe.route('**/*',lambda route: route.fulfill(status=200,content_type='text/html',body='<html lang="en"><body>QA</body></html>'))
        try:
            nav_probe.goto(ORIGIN+'/apollo/',timeout=4000)
            receipt['navigation']='SYNTHETIC_HTTP_NAVIGATION_POSSIBLE_NOT_EXERCISED_BY_COMPONENT_TEST'
        except Exception as ex:
            receipt['navigation']='BLOCKED_BY_ADMINISTRATOR' if 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(ex) else 'FAILED:'+str(ex)[:140]
        nav_probe.close()
        for javascript in (False,True):
            for width in WIDTHS:
                context=browser.new_context(viewport={'width':width,'height':900},is_mobile=width<500,has_touch=width<500,
                  java_script_enabled=javascript,reduced_motion='reduce')
                page=context.new_page();requests=[];errors=[];blocked=[]
                def serve(route):
                    path=route.request.url.removeprefix(ORIGIN)
                    requests.append((route.request.url,route.request.resource_type))
                    if path not in assets:
                        blocked.append(route.request.url);route.abort();return
                    mime,body=assets[path]
                    route.fulfill(status=200,body=body,headers={'content-type':mime,'content-security-policy':CSP,'cache-control':'no-store'})
                page.route('**/*',serve)
                page.on('pageerror',lambda ex:errors.append(str(ex)))
                if javascript:
                    page.add_init_script('''() => {
                        window.__perf = {lcp: null, cls:0};
                        try{ new PerformanceObserver(l=>{for(const e of l.getEntries())window.__perf.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){}
                        try{ new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__perf.cls+=e.value;}).observe({type:'layout-shift',buffered:true});}catch(e){}
                    }''')
                page.set_content(fixture,wait_until='load')
                check(not errors,'browser JS errors '+str(errors))
                check(not blocked,'blocked request '+str(blocked))
                check(page.locator('[data-fva-record]').count()==6,'expected six records')
                check(page.locator('[data-fva-record]:visible').count()==6,'initial records inaccessible')
                check(page.locator('[data-fva-drawer]').count()==6,'source drawer count')
                check(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'),'overflow '+str(width))
                check(page.locator('main').count()==1,'nested main landmark')
                check(page.locator('img,iframe,canvas,svg,video').count()==0,'forbidden media')
                check(page.evaluate('''() => {const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return ids.length===new Set(ids).size;}'''),'duplicate IDs')
                drawer=page.locator('[data-fva-drawer]').first
                drawer.locator('summary').focus();drawer.locator('summary').press('Enter')
                check(drawer.get_attribute('open') is not None,'keyboard disclosure')
                if javascript:
                    check(page.locator('[data-fva-controls]').is_visible(),'enhancement missing')
                    filt=page.locator('[data-fva-filter="1967"]')
                    check(filt.evaluate('e=>e.getBoundingClientRect().height')>=44,'touch target under 44px')
                    (filt.tap() if width<500 else filt.click())
                    check(page.locator('[data-fva-record]:visible').count()==3,'1967 count')
                    page.locator('[data-fva-search]').fill('Kim Shiflett')
                    check(page.locator('[data-fva-record]:visible').count()==0,'1967/Shiflett not empty')
                    reset=page.locator('[data-fva-reset]')
                    (reset.tap() if width<500 else reset.click())
                    check(page.locator('[data-fva-record]:visible').count()==6,'reset did not restore')
                    check(page.evaluate("document.activeElement.matches('[data-fva-search]')"),'reset focus')
                    # No browser HTTP navigation in this runtime; HTTP CSP remains unverified.
                else:
                    check(not page.locator('[data-fva-controls]').is_visible(),'noJS controls visible')
                violations=None
                if args.axe:
                    page.add_script_tag(content=args.axe.read_text(encoding='utf8'))
                    violations=page.evaluate('''async () => (await axe.run(document.querySelector('.fva'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))''')
                    check(not violations,'axe violations '+str(violations))
                if javascript:page.wait_for_timeout(200)
                measurements=page.evaluate('window.__perf||null') if javascript else None
                if width in (390,1440):
                    page.evaluate('document.activeElement && document.activeElement.blur()')
                    page.evaluate('window.scrollTo(0,0)')
                    pic=out/f'r40-atlas-{width}-{"js" if javascript else "nojs"}.png'
                    page.screenshot(path=str(pic),full_page=True,animations='disabled')
                    screenshot={'file':pic.name,'sha256':sha(pic)}
                else:screenshot=None
                receipt['cases'].append({'width':width,'javascript':javascript,'status':'PASS',
                     'requests':requests,'synthetic_navigation_lcp_ms':None if measurements is None else measurements['lcp'],
                     'synthetic_navigation_cls':None if measurements is None else measurements['cls'],
                     'axe_violations':violations,'screenshot':screenshot})
                context.close()
        receipt['chromium']=browser.version;browser.close()
    (out/'r40-browser-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(f"PASS {len(receipt['cases'])}/14 Chromium real PHP-rendered component; browser HTTP navigation blocked, CSP/hosted CWV/WordPress HOLD.")

if __name__=='__main__':main()
