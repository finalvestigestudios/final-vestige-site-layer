"""Opt-in, read-only, authentic HTTPS WordPress staging gate for R450.
Requires explicit nonproduction FV origin & independently reviewed local axe-core SHA.
Never auto-installs, posts, signs up, checks out, changes WordPress or deploys.
"""
import argparse,hashlib,json,re
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
WIDTHS=(320,360,390,768,1024,1440,1920)
ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
PERF="""(()=>{window.__fvLCP=null;window.__fvCLS=0;try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__fvLCP=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__fvCLS+=e.value;}).observe({type:'layout-shift',buffered:true})}catch(e){}})();"""

def normalized(url,subpath=False):
    try:v=urlsplit(url)
    except ValueError:return None
    try:valid=(v.scheme=='https' and v.hostname and not v.username and not v.password and not v.port and not v.query and not v.fragment)
    except ValueError:return None
    if not valid or not re.search(r'(^|[-.])(staging|stage|preview|test)([-.]|$)',v.hostname):return None
    if not v.hostname.endswith('.finalvestige.com'):return None
    if subpath and (not v.path or v.path=='/'):return None
    if not subpath and v.path not in ('','/'):return None
    return v

def preflight(args):
    issues=[];o=normalized(args.approved_origin);u=normalized(args.url,True)
    if o is None or u is None or u.netloc!=o.netloc:issues.append('approved nonproduction FV HTTPS origin and exact nonroot path required')
    axe=Path(args.axe_js) if args.axe_js else None
    if not axe or not axe.is_file() or axe.stat().st_size<25000 or not re.fullmatch('[0-9a-f]{64}',args.axe_sha256) or hashlib.sha256(axe.read_bytes()).hexdigest()!=args.axe_sha256:
        issues.append('reviewed genuine local axe-core JavaScript and exact SHA-256 required')
    return issues

def run(args):
    issues=preflight(args)
    if issues:
        print(json.dumps({'status':'HOLD_NOT_RUN','reasons':issues},indent=2));return 2
    base=urlsplit(args.approved_origin);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    checks=[];errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (True,False):
                ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce',accept_downloads=True)
                page=ctx.new_page();blocked=[]
                def route_cb(route):
                    u=urlsplit(route.request.url)
                    if route.request.method.upper()!='GET' or u.scheme!='https' or u.netloc!=base.netloc:
                        blocked.append({'method':route.request.method,'url':route.request.url});route.abort()
                    else:route.continue_()
                page.route('**/*',route_cb)
                page.on('dialog',lambda dialog:dialog.dismiss())
                try:
                    if js:page.add_init_script(PERF)
                    response=page.goto(args.url,wait_until='load',timeout=30000)
                    page.wait_for_timeout(1500)
                    row={'width':width,'javascript':js,'status':response.status if response else None,'url':page.url,
                      'blocked_requests':blocked,'journeys':page.locator('[data-fv-r449]').count(),
                      'receipts':page.locator('[data-fv-r450]').count(), 'receipt_records':page.locator('[data-r450-claim]').count(),
                      'history_cards':page.locator('[data-fv-r448-card]').count(),
                      'free_ctas':page.locator(f'a[href="{ARTICLE}"]').count(),
                      'commerce_actions':page.locator('a[href*="checkout"],a[href*="payhip"],form').count(),
                      'overflow':page.evaluate('document.documentElement.scrollWidth>innerWidth+1')}
                    if row['status']!=200 or urlsplit(row['url']).netloc!=base.netloc:errors.append(f'{width}/{js}: origin/status failure')
                    if (row['journeys'],row['receipts'],row['receipt_records'],row['history_cards'],row['free_ctas'],row['commerce_actions'])!=(1,1,4,4,1,0) or row['overflow'] or blocked:
                        errors.append(f'{width}/{js}: source, privacy or CTA contract failure')
                    if js:
                        page.add_script_tag(path=args.axe_js)
                        findings=page.evaluate("async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})")
                        row['axe_violations']=[{'id':v['id'],'impact':v.get('impact'),'nodes':len(v.get('nodes',[]))} for v in findings['violations']]
                        if row['axe_violations']:errors.append(f'{width}: axe accessibility violations')
                        row['lab_metrics']=page.evaluate('({lcp:window.__fvLCP,cls:window.__fvCLS})')
                        if row['lab_metrics']['lcp'] is None or row['lab_metrics']['lcp']>2500:errors.append(f'{width}: missing/slow LAB LCP')
                        if row['lab_metrics']['cls'] is None or row['lab_metrics']['cls']>0.1:errors.append(f'{width}: excessive LAB CLS')
                        if page.get_by_role('button',name='Download original four-source receipt (.txt)').count()!=1:errors.append(f'{width}: missing source receipt download')
                    else:
                        if page.get_by_role('button',name='Download original four-source receipt (.txt)').count()!=0:errors.append(f'{width}: no-JS incorrectly enhanced')
                    page.screenshot(path=str(out/f'{width}-{"js" if js else "nojs"}.png'),full_page=True)
                    checks.append(row)
                except Exception as e:errors.append(f'{width}/{js}: navigation/runtime failed: {str(e)[:300]}')
                finally:ctx.close()
        browser.close()
    receipt={'status':'PASS' if not errors else 'FAIL','checks':checks,'errors':errors,'mode':'real approved HTTPS nonproduction WordPress navigation',
             'measurements':'LCP/CLS are Chromium LAB diagnostics, not field p75 CWV or INP',
             'independent_screen_reader':'NOT_REPLACED_BY_AXE','commercial_acceptance':'HARD_HOLD'}
    (out/'staging-results.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'completed':len(checks),'errors':errors}));return 1 if errors else 0

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for key in ('url','approved-origin','axe-js','axe-sha256'):parser.add_argument('--'+key,default='')
    parser.add_argument('--out',default='QA/staging')
    raise SystemExit(run(parser.parse_args()))
