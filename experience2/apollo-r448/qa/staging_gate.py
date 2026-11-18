"""Read-only *actual HTTPS staging* gate. HOLD when approved staging/axe unavailable.
Run python qa/staging_gate.py --url https://STAGING/preview --approved-origin https://STAGING
     --axe-js /PATH/TO/REVIEWED/axe.min.js --axe-sha256 EXACT_HASH --out QA/staging
No production target, outgoing POST or analytics writes are permitted.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
WIDTHS=(320,360,390,768,1024,1440,1920)
PERF="""(()=>{window.fvQA={lcp:null,cls:0,shiftCount:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.fvQA.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput){window.fvQA.cls+=e.value;window.fvQA.shiftCount++}}).observe({type:'layout-shift',buffered:true})}catch(e){}})();"""
def approved(url,origin):
    a=urlsplit(url);o=urlsplit(origin)
    return (a.scheme=='https' and a.netloc==o.netloc and o.scheme=='https' and not o.path.rstrip('/') and not o.query and not o.fragment
            and a.hostname not in ('finalvestige.com','www.finalvestige.com') and not a.username and not a.password and not a.port
            and not a.query and not a.fragment and a.path.startswith('/'))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='');parser.add_argument('--approved-origin',default='');parser.add_argument('--axe-js',default='');parser.add_argument('--axe-sha256',default='');parser.add_argument('--out',default='QA/staging')
    args=parser.parse_args();errors=[]
    if not approved(args.url,args.approved_origin):errors.append('HOLD: approved HTTPS nonproduction same-origin URL required; no query, production, port or credentials')
    axe=Path(args.axe_js) if args.axe_js else None
    if not axe or not axe.is_file() or axe.stat().st_size < 25000 or len(args.axe_sha256)!=64 or hashlib.sha256(axe.read_bytes()).hexdigest()!=args.axe_sha256: errors.append('HOLD: reviewed local genuine axe-core asset plus matching SHA-256 required')
    if errors:
        print(json.dumps({'status':'HOLD_NOT_RUN','errors':errors},indent=2));raise SystemExit(2)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True);rows=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for w in WIDTHS:
            for js in (True,False):
                ctx=browser.new_context(viewport={'width':w,'height':900},java_script_enabled=js,reduced_motion='reduce')
                page=ctx.new_page();blocked=[]
                def protect(route):
                    request=route.request
                    if request.method.upper()!='GET' or not request.url.startswith(args.approved_origin+'/'):
                        blocked.append({'method':request.method,'url':request.url});route.abort()
                    else: route.continue_()
                page.route('**/*',protect)
                page.on('dialog',lambda dialog:dialog.dismiss())
                try:
                    if js:page.add_init_script(PERF)
                    response=page.goto(args.url,wait_until='load',timeout=25000)
                    page.wait_for_timeout(1500)
                    row={'width':w,'javascript':js,'status':response.status if response else None,'url':page.url,'blocked_requests':blocked}
                    if not page.url.startswith(args.approved_origin+'/'):
                        errors.append(f'{w}/{js}: redirect off approved staging origin')
                    if row['status']!=200:errors.append(f'{w}/{js}: non-200 response')
                    row['claim_cards']=page.locator('[data-fv-r448-card]').count()
                    row['free_cta']=page.locator('a[href*="the-hatch-opened-inward"]').count()
                    row['paid_links']=page.locator('a[href*="payhip"],a[href*="checkout"],form[action*="payment"]').count()
                    row['overflow']=page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1')
                    if row['claim_cards']!=4 or row['free_cta']!=1 or row['paid_links'] or row['overflow']:
                        errors.append(f'{w}/{js}: content/CTA/overflow contract failed')
                    if js:
                        page.add_script_tag(path=str(axe))
                        findings=page.evaluate("async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})")
                        row['axe_violations']=[{'id':v['id'],'impact':v.get('impact'),'nodes':len(v.get('nodes',[]))} for v in findings['violations']]
                        row['lab_cwv']=page.evaluate('window.fvQA')
                        if row['axe_violations']:errors.append(f'{w}: axe violations')
                        if row['lab_cwv']['lcp'] is None or row['lab_cwv']['lcp']>2500:errors.append(f'{w}: missing/slow LCP')
                        if row['lab_cwv']['cls']>.1:errors.append(f'{w}: excessive CLS')
                    if blocked:errors.append(f'{w}/{js}: off-origin or non-GET requests encountered')
                    page.screenshot(path=str(out/f"{w}-{'js' if js else 'nojs'}.png"),full_page=True)
                    rows.append(row)
                except Exception as exc:errors.append(f'{w}/{js}: {exc}')
                finally:ctx.close()
        browser.close()
    (out/'staging_results.json').write_text(json.dumps({'status':'PASS' if not errors else 'FAIL','results':rows,'errors':errors},indent=2)+'\n')
    print(json.dumps({'status':'PASS' if not errors else 'FAIL','cases':len(rows),'errors':errors}))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
