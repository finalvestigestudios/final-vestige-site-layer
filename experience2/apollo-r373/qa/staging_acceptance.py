#!/usr/bin/env python3
"""R373 read-only Apollo WordPress staging acceptance. Never visit production.

Fixture mode is separately labeled and cannot satisfy staging acceptance. Axe is
mandatory for real staging. No third-party requests, submissions, or CTA clicks.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

EXPECTED_NASA = {
    'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
    'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
    'https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/',
    'https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/',
}
FREE_URL = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
CASES = [
    ('mobile-320', 320, False, False, False, False, False),
    ('mobile-390', 390, False, False, False, False, False),
    ('tablet-768', 768, False, False, False, False, False),
    ('desktop-1440', 1440, False, False, False, False, False),
    ('wide-1920', 1920, False, False, False, False, False),
    ('nojs-320', 320, True, False, False, False, False),
    ('root4x-320', 320, False, True, False, False, False),
    ('reduced-390', 390, False, False, True, False, False),
    ('forced-320', 320, False, False, False, True, False),
    ('touch-390', 390, False, False, False, False, True),
]
PERF_INIT = """(() => {
 window.__fv_r373={lcp:null,cls:0,lcpObserver:false,clsObserver:false};
 try {new PerformanceObserver(l=>{for(const x of l.getEntries())window.__fv_r373.lcp=x.startTime})
  .observe({type:'largest-contentful-paint',buffered:true});window.__fv_r373.lcpObserver=true}catch(e){}
 try {new PerformanceObserver(l=>{for(const x of l.getEntries())if(!x.hadRecentInput)window.__fv_r373.cls+=x.value})
  .observe({type:'layout-shift',buffered:true});window.__fv_r373.clsObserver=true}catch(e){}
 document.addEventListener('securitypolicyviolation',e=>{
  (window.__fv_r373.cspViolations??=[]).push({directive:e.violatedDirective})
 });
})();"""


def validate_staging(url, host):
    if not isinstance(url, str) or not isinstance(host, str):
        raise ValueError('staging URL and exact hostname are mandatory')
    p = urlsplit(url)
    bad_host = host in {'finalvestige.com', 'www.finalvestige.com', 'localhost', '127.0.0.1'}
    if (p.scheme != 'https' or bad_host or p.hostname != host or p.username or p.password
            or p.port not in (None, 443) or p.query or p.fragment
            or not re.fullmatch(r'[a-z0-9.-]+', host)
            or p.path.startswith(('/wp-admin', '/wp-login', '/wp-json'))):
        raise ValueError('Refusing anything except a clean HTTPS URL on the explicitly approved nonproduction hostname')
    return p


def fixture_html():
    root = Path(__file__).resolve().parents[2]
    fixture = root / 'apollo-r372/qa/fixture.php'
    if not fixture.is_file():
        raise RuntimeError('R372 PHP fixture not present; need checked-out parent source')
    return subprocess.check_output(['php', str(fixture)], text=True)


def inspect_dom(page):
    return page.evaluate("""(freeUrl) => {
      const root=document.querySelector('[data-fv-apollo-path]');
      const urls=[...document.querySelectorAll('[data-fv-nasa-source],[data-fv-nasa-context]')].map(a=>a.href);
      const ctas=[...document.querySelectorAll('[data-fv-free-cta]')].map(a=>a.href);
      const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
      return {component:!!root,stages:root?.querySelectorAll('[data-fv-evidence-stage]').length??0,
        drawers:root?.querySelectorAll('[data-fv-source-drawer]').length??0,
        nasa_urls:[...new Set(urls)].sort(), ctas, unique_ids:ids.length===new Set(ids).size,
        overflow:document.documentElement.scrollWidth>innerWidth+1,
        jumps:[...document.querySelectorAll('.fv-apollo-r372__jump a')].every(a=>document.getElementById(a.hash.slice(1))),
        css_color:root?getComputedStyle(root).backgroundColor:null,
        css_token:root?getComputedStyle(root).getPropertyValue('--ar-bg').trim():null,
        styles:[...document.querySelectorAll('head link[rel=stylesheet]')].map(e=>e.href),
        perf:window.__fv_r373||null,
        site_url:location.href.split('?')[0]
      };
    }""", FREE_URL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['fixture', 'staging'], required=True)
    ap.add_argument('--url', help='approved HTTPS WordPress staging route only')
    ap.add_argument('--host', help='exact approved nonproduction host, no wildcards')
    ap.add_argument('--axe-js', type=Path, help='locally pinned axe-core distributable; mandatory in staging')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.mode == 'staging':
        validate_staging(args.url, args.host)
        if not args.axe_js or not args.axe_js.is_file():
            ap.error('STAGING BLOCKED: genuine local axe-core distributable required (no CDN, no fake PASS)')
    elif args.url or args.host:
        ap.error('fixture mode never accepts a URL or host')
    args.out.mkdir(parents=True, exist_ok=True)
    fixture = fixture_html() if args.mode == 'fixture' else None
    rows = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        for name, width, nojs, root4x, reduced, forced, touch in CASES:
            ctx = browser.new_context(viewport={'width':width, 'height':860},
                java_script_enabled=not nojs, has_touch=touch,
                reduced_motion='reduce' if reduced else 'no-preference',
                forced_colors='active' if forced else 'none')
            page = ctx.new_page()
            requests, errors = [], []
            page.on('requestfailed', lambda r: errors.append({'url':r.url.split('?')[0],'failure':r.failure}))
            page.on('response', lambda r: requests.append({'url':r.url.split('?')[0],'status':r.status,'kind':r.request.resource_type}))
            if not nojs:
                page.add_init_script(script=PERF_INIT)
            if args.mode == 'staging':
                # No traffic to unrelated vendors/trackers: read-only first-party staging only.
                page.route('**/*',lambda route:route.continue_() if urlsplit(route.request.url).hostname==args.host else route.abort())
                response = page.goto(args.url, wait_until='domcontentloaded', timeout=45000)
                page.wait_for_load_state('load', timeout=45000)
                headers = response.headers if response else {}
                if not headers.get('content-security-policy'):
                    errors.append({'error':'HTTP Content-Security-Policy header missing'})
                if not page.locator('[data-fv-apollo-path]').count():
                    errors.append({'error':'Apollo shortcode missing; not accepted as WordPress staging'})
                if not any('evidence-path.css' in x['url'] and x['status']==200 for x in requests):
                    errors.append({'error':'R372 stylesheet not observed as HTTP 200 response'})
            else:
                page.set_content(fixture, wait_until='load')
                headers = {}
            if root4x:
                page.add_style_tag(content='html{font-size:64px!important}')
            page.wait_for_timeout(250)
            dom = inspect_dom(page)
            checks = {
                'four_stages':dom['stages']==4,
                'four_native_drawers':dom['drawers']==4,
                'four_distinct_approved_nasa_sources':set(dom['nasa_urls'])==EXPECTED_NASA,
                'single_free_editorial_cta':dom['ctas']==[FREE_URL],
                'unique_ids':dom['unique_ids'],
                'jump_targets_present':dom['jumps'],
                'no_horizontal_overflow':not dom['overflow'],
                'component_stylesheet_token_applied':dom['css_token']=='#0d1011',
            }
            if args.mode=='staging' and not nojs:
                perf=dom['perf'] or {}
                checks['layout_shift_observer_started']=perf.get('clsObserver') is True
                checks['layout_shift_within_lab_budget']=isinstance(perf.get('cls'),(int,float)) and perf['cls']<=0.1
                if name in ('mobile-320','desktop-1440'):
                    checks['lcp_observer_started']=perf.get('lcpObserver') is True
                    checks['lcp_observed_within_lab_budget']=isinstance(perf.get('lcp'),(int,float)) and 0<perf['lcp']<=2500
            summary = page.locator('[data-fv-source-drawer] summary').first
            if summary.count():
                summary.focus(); page.keyboard.press('Enter')
                checks['native_keyboard_open'] = page.locator('[data-fv-source-drawer]').first.evaluate('(e)=>e.open')
                page.keyboard.press('Enter')
                checks['native_keyboard_close'] = not page.locator('[data-fv-source-drawer]').first.evaluate('(e)=>e.open')
                summary.click()
                checks['pointer_or_touch_open']=page.locator('[data-fv-source-drawer]').first.evaluate('(e)=>e.open')
                summary.click()
            else:
                checks.update(native_keyboard_open=False,native_keyboard_close=False,pointer_or_touch_open=False)
            axe = {'state':'NOT_EXECUTED_FIXTURE' if args.mode=='fixture' else 'NOT_EXECUTED_NO_JS'}
            if args.mode=='staging' and not nojs:
                try:
                    page.add_script_tag(path=str(args.axe_js))
                    axe=page.evaluate("""async () => {
                        if(!window.axe?.run)throw new Error('genuine axe-core missing or CSP blocked');
                        const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag22aa']}});
                        return {state:'EXECUTED',version:axe.version,violations:r.violations.map(v=>({id:v.id,impact:v.impact,affected:v.nodes.length}))};
                    }""")
                    checks['axe_no_violations']=len(axe['violations'])==0
                except Exception as e:
                    axe={'state':'BLOCKED','reason':str(e)[:400]}; checks['axe_no_violations']=False
            page.screenshot(path=str(args.out/(name+'.png')),full_page=True,animations='disabled')
            if name=='desktop-1440':
                page.emulate_media(media='print')
                page.pdf(path=str(args.out/'apollo-source-print.pdf'),format='A4',print_background=True)
            rows.append({'case':name,'width':width,'nojs':nojs,'checks':checks,'axe':axe,
                'local_lab_perf_not_field':dom['perf'],'http_csp_present':bool(headers.get('content-security-policy')),
                'network':requests if args.mode=='staging' else [],'errors':errors})
            ctx.close()
        browser.close()
    print_links=[]
    for pg in PdfReader(str(args.out/'apollo-source-print.pdf')).pages:
        for ann in pg.get('/Annots',[]):
            obj=ann.get_object(); target=obj.get('/A')
            if target and target.get('/URI'): print_links.append(str(target['/URI']))
    print_ok=EXPECTED_NASA.issubset(set(print_links)) and FREE_URL in print_links
    success=print_ok and all(all(x['checks'].values()) and not x['errors'] for x in rows)
    report={'mode':args.mode,'status':('STAGING_PASS' if args.mode=='staging' and success else
            'FIXTURE_SMOKE_PASS_NOT_STAGING' if success else 'FAIL'),
            'not_field_core_web_vitals':True,'axe_fixture_not_run':args.mode=='fixture',
            'never_follows_cta_or_merchant':True,
            'native_print_links_verified':print_ok,'native_print_unique_nasa_urls':len(set(print_links)&EXPECTED_NASA),
            'cases':rows}
    (args.out/'results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(report['status'],len(rows),'cases',sum(sum(x['checks'].values()) for x in rows),'checks passed')
    sys.exit(0 if success else 1)

if __name__=='__main__':
    main()
