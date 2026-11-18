"""Strict genuine *approved* staging QA for R449.
No allowed target/independently reviewed axe => HOLD_NOT_RUN before launching a browser.
No remote scripts, no outbound writes; all browser requests restricted to staging origin.
Actual environment may block network navigation; do not interpret an offline pass as staging.
"""
import argparse, hashlib, json, re
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

WIDTHS=(320,360,390,768,1024,1440,1920)
ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
PERF="""(()=>{window.__apolloLCP=null;window.__apolloCLS=0;
try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__apolloLCP=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__apolloCLS+=e.value;}).observe({type:'layout-shift',buffered:true})}catch(e){}
})();"""

def normalize(url,allow_path=False):
    try:v=urlsplit(url)
    except ValueError:return None
    try:
        valid=(v.scheme=='https' and v.hostname and not v.username and not v.password and not v.port and not v.query and not v.fragment)
    except ValueError:return None
    if not valid:return None
    if v.hostname in ('finalvestige.com','www.finalvestige.com','localhost','127.0.0.1') or v.hostname.endswith('.finalvestige.com') is False:return None
    if not re.search(r'(^|[-.])(staging|preview|stage|test)([-.]|$)',v.hostname):return None
    if not allow_path and v.path not in ('','/'):return None
    if allow_path and not v.path.startswith('/'):return None
    return v

def approved(url,origin):
    a=normalize(url,True);o=normalize(origin,False)
    return bool(a and o and a.netloc==o.netloc and a.path not in ('','/'))

def preflight(args):
    errors=[]
    if not approved(args.url,args.approved_origin):errors.append('approved exact HTTPS FV staging hostname and nonroot path required')
    axe=Path(args.axe_js) if args.axe_js else None
    if not axe or not axe.is_file() or axe.stat().st_size < 25000 or not re.fullmatch('[0-9a-f]{64}',args.axe_sha256) or hashlib.sha256(axe.read_bytes()).hexdigest()!=args.axe_sha256:
        errors.append('genuine, independently reviewed local axe-core file with exact SHA-256 required')
    return errors

def run(args):
    errors=preflight(args);out=Path(args.out)
    if errors:
        # Don't open a browser, issue HTTP calls or write public content when approval is missing.
        print(json.dumps({'status':'HOLD_NOT_RUN','reason':errors},indent=2));return 2
    out.mkdir(parents=True,exist_ok=True);rows=[]
    axe=Path(args.axe_js)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (True,False):
                ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce',accept_downloads=False)
                page=ctx.new_page();blocked=[]
                def safe(route):
                    u=urlsplit(route.request.url)
                    if route.request.method.upper() != 'GET' or u.scheme!='https' or u.netloc!=urlsplit(args.approved_origin).netloc:
                        blocked.append({'method':route.request.method,'url':route.request.url});route.abort()
                    else:route.continue_()
                page.route('**/*',safe)
                page.on('dialog',lambda dlg:dlg.dismiss())
                try:
                    if js:page.add_init_script(PERF)
                    resp=page.goto(args.url,wait_until='load',timeout=25000)
                    page.wait_for_timeout(1600)
                    row={'width':width,'js':js,'response':resp.status if resp else None,'url':page.url,'blocked_requests':blocked,
                         'claims':page.locator('[data-fv-r448-card]').count(),
                         'educator_previews':page.locator('[data-r440-root]').count(),
                         'journeys':page.locator('[data-fv-r449]').count(),
                         'investigation_ctas':page.locator(f'a[href="{ARTICLE}"]').count(),
                         'paid_ctas':page.locator('a[href*="payhip"],a[href*="checkout"],form[action*="payment"]').count(),
                         'overflow':page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1')}
                    if row['response']!=200 or urlsplit(page.url).netloc!=urlsplit(args.approved_origin).netloc:errors.append(f'{width}/{js}: status/redirect failed')
                    if row['claims']!=4 or row['educator_previews']!=1 or row['journeys']!=1 or row['investigation_ctas']!=1 or row['paid_ctas'] or row['overflow']:
                        errors.append(f'{width}/{js}: content or conversion contract failed')
                    if blocked:errors.append(f'{width}/{js}: prohibited outgoing requests')
                    if js:
                        page.add_script_tag(path=str(axe))
                        result=page.evaluate("async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})")
                        row['axe_violations']=[{'id':v['id'],'impact':v.get('impact'),'nodes':len(v.get('nodes',[]))} for v in result['violations']]
                        if row['axe_violations']:errors.append(f'{width}: axe violations')
                        row['lab_cwv']=page.evaluate('({lcp:window.__apolloLCP,cls:window.__apolloCLS})')
                        if row['lab_cwv']['lcp'] is None or row['lab_cwv']['lcp']>2500:errors.append(f'{width}: missing / slow lab LCP')
                        if row['lab_cwv']['cls'] is None or row['lab_cwv']['cls']>0.1:errors.append(f'{width}: excessive / missing lab CLS')
                    else:
                        row['no_js_claims_visible']=page.locator('[data-fv-r448-card]:visible').count()
                        if row['no_js_claims_visible']!=4:errors.append(f'{width}: no-JS evidence not fully available')
                    page.screenshot(path=str(out/f"{width}-{'js' if js else 'nojs'}.png"),full_page=True)
                    rows.append(row)
                except Exception as exc:errors.append(f'{width}/{js}: browser error {str(exc)[:250]}')
                finally:ctx.close()
        browser.close()
    result={'status':'PASS' if not errors else 'FAIL','results':rows,'errors':errors,'metric_scope':'navigated Chromium LAB only; field p75 CWV not tested'}
    (out/'staging_results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'cases':len(rows),'errors':errors}));return 1 if errors else 0

def main():
    p=argparse.ArgumentParser()
    for name in ('url','approved-origin','axe-js','axe-sha256'):p.add_argument('--'+name,default='')
    p.add_argument('--out',default='QA/staging')
    return run(p.parse_args())
if __name__=='__main__':raise SystemExit(main())
