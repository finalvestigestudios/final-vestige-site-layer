#!/usr/bin/env python3
"""Read-only, real-navigation staging acceptance; NEVER tests production routes.

Requires explicit staging host and an actual, vendored axe-core JS library.
This does not instrument production analytics or claim field Core Web Vitals.
"""
import argparse
import json
import hashlib
import sys
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, Error as PlaywrightError

ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
OBSERVER='''(() => {
 window.__fvVitals={lcp:null,cls:0,shifts:[]};
 try {new PerformanceObserver(list=>{for(const e of list.getEntries()){window.__fvVitals.lcp=e.startTime;}}).observe({type:'largest-contentful-paint', buffered:true});} catch(e){window.__fvVitals.lcpError=String(e)}
 try {new PerformanceObserver(list=>{for(const e of list.getEntries()){if(!e.hadRecentInput){window.__fvVitals.cls+=e.value;window.__fvVitals.shifts.push(e.value);}}}).observe({type:'layout-shift', buffered:true});} catch(e){window.__fvVitals.clsError=String(e)}
})();'''


def verify_target(url,host):
    u=urlparse(url)
    return (u.scheme=='https' and u.hostname==host and bool(host) and
            host not in {'finalvestige.com','www.finalvestige.com'} and
            not host.endswith('.finalvestige.com.evil.invalid') and
            not u.username and not u.password and not u.fragment)


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--url',required=True)
    ap.add_argument('--approved-staging-host',required=True)
    ap.add_argument('--axe-js',type=Path,required=True)
    ap.add_argument('--axe-sha256',required=True,help='Reviewed SHA-256 of genuine axe-core bundle')
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args(argv)
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    report={'status':'HOLD','scope':'READ_ONLY_STAGING_ONLY','url':args.url,'screenshots':[], 'errors':[]}
    def finish(code):
        (out/'staging-acceptance.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
        print(json.dumps({'status':report['status'],'errors':report['errors'],'screenshots':len(report['screenshots'])}))
        return code
    if not verify_target(args.url,args.approved_staging_host):
        report['errors'].append('invalid or production hostname; HTTPS staging allowlist required')
        return finish(2)
    if not args.axe_js.is_file() or args.axe_js.stat().st_size<100_000:
        report['errors'].append('genuine axe-core JS file missing; do not substitute CDP tree')
        return finish(2)
    if len(args.axe_sha256)!=64 or any(c not in '0123456789abcdef' for c in args.axe_sha256.lower()) or hashlib.sha256(args.axe_js.read_bytes()).hexdigest()!=args.axe_sha256.lower():
        report['errors'].append('axe-core bundle has not matched its independent reviewed SHA-256')
        return finish(2)
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            for width in (320,360,390,768,1024,1440,1920):
                context=browser.new_context(viewport={'width':width,'height':880},reduced_motion='reduce')
                context.route('**/*', lambda route: route.continue_() if urlparse(route.request.url).hostname==args.approved_staging_host or urlparse(route.request.url).scheme in ('data','blob') else route.abort())
                context.add_init_script(OBSERVER)
                page=context.new_page()
                response=page.goto(args.url,wait_until='domcontentloaded',timeout=15000)
                if response is None or response.status>=400: raise AssertionError(f'HTTP failure at {width}: {response.status if response else "none"}')
                if urlparse(page.url).hostname!=args.approved_staging_host: raise AssertionError('staging redirected to an unapproved host')
                page.wait_for_timeout(1500)
                evidence=page.locator('[data-fv-r421-receipts]')
                if evidence.count()!=1: raise AssertionError(f'R421 not installed at {width}')
                if evidence.locator('.fv-r421__card').count()!=3: raise AssertionError('missing three source receipts')
                if evidence.locator(f'a[href="{ARTICLE}"]').count()!=1: raise AssertionError('missing/duplicated free CTA')
                if evidence.locator('form,iframe,img,canvas,svg,map').count(): raise AssertionError('unauthorized media, forms or map')
                if evidence.locator('a[href^="https://www.nasa.gov/"]').count()<6: raise AssertionError('NASA source custody links missing')
                if evidence.locator('a[href*="payhip"],a[href*="checkout"],a[href*="utm_"]').count(): raise AssertionError('unapproved paid/tracked CTA')
                if not page.evaluate('document.documentElement.scrollWidth<=innerWidth'): raise AssertionError(f'horizontal overflow at {width}')
                page.add_script_tag(path=str(args.axe_js))
                axe=page.evaluate('''async()=>{if(!window.axe || !axe.version)throw Error('genuine axe-core unavailable'); const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return {version:axe.version,violations:r.violations.map(v=>({id:v.id,impact:v.impact,count:v.nodes.length}))}}''')
                if axe['violations']: raise AssertionError('axe violations '+json.dumps(axe['violations']))
                vitals=page.evaluate('window.__fvVitals')
                if vitals.get('lcp') is None or vitals.get('clsError') or vitals.get('lcpError'):raise AssertionError('missing navigated LCP/CLS observer evidence')
                if vitals['lcp']>2500 or vitals['cls']>0.1:raise AssertionError('laboratory CWV budget exceeded')
                shot=out/f'staging-{width}.png';page.screenshot(path=str(shot),full_page=True,animations='disabled')
                report['screenshots'].append(str(shot.name))
                report.setdefault('results',[]).append({'width':width,'http_status':response.status,'axe':axe,'lab_lcp_ms':vitals['lcp'],'lab_cls':vitals['cls']})
                page.close();context.close()
            # Additional independent navigated interaction contexts: no-JS, touch,
            # keyboard, forced colors, 400% zoom and reduced motion.
            modes=[('nojs',dict(java_script_enabled=False,viewport={'width':390,'height':850})),
                   ('touch',dict(is_mobile=True,has_touch=True,viewport={'width':390,'height':850})),
                   ('keyboard',dict(viewport={'width':390,'height':850})),
                   ('forced',dict(forced_colors='active',viewport={'width':390,'height':850})),
                   ('reduced',dict(reduced_motion='reduce',viewport={'width':320,'height':850})),
                   ('zoom400',dict(viewport={'width':320,'height':850}))]
            for label,options in modes:
                context=browser.new_context(**options)
                context.route('**/*', lambda route: route.continue_() if urlparse(route.request.url).hostname==args.approved_staging_host or urlparse(route.request.url).scheme in ('data','blob') else route.abort())
                page=context.new_page();response=page.goto(args.url,wait_until='domcontentloaded',timeout=15000)
                if not response or response.status>=400: raise AssertionError(label+' navigation failed')
                element=page.locator('[data-fv-r421-receipts] details').first
                if label=='touch': element.locator('summary').tap()
                if label=='keyboard': element.locator('summary').focus();page.keyboard.press('Enter')
                if label=='nojs': element.locator('summary').click()
                if label in ('touch','keyboard','nojs') and element.get_attribute('open') is None: raise AssertionError(label+' native disclosure inaccessible')
                if label=='nojs' and page.locator('button[data-fv-r421-copy]:visible').count(): raise AssertionError('copy button is not progressive enhancement')
                if label=='zoom400': page.evaluate('document.documentElement.style.fontSize="64px"')
                if not page.evaluate('document.documentElement.scrollWidth<=innerWidth'):raise AssertionError(label+' horizontal overflow')
                shot=out/f'staging-{label}.png';page.screenshot(path=str(shot),full_page=True,animations='disabled')
                report['screenshots'].append(shot.name)
                report.setdefault('interactions',[]).append({'scenario':label,'result':'PASS'})
                page.close();context.close()
            browser.close()
        report['status']='STAGING_QA_PASS_NOT_RELEASE_APPROVAL'
        return finish(0)
    except (PlaywrightError,AssertionError,ValueError) as e:
        report['errors'].append(str(e).splitlines()[0][:400])
        return finish(2)

if __name__=='__main__':
    sys.exit(main())
