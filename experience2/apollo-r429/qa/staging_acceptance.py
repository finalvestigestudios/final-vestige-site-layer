"""Read-only real-navigation acceptance; cannot pass without authorized staging + locally pinned axe."""
import argparse, hashlib, json, sys
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--staging-url',required=True,help='Founder-approved staging page using HTTPS')
    ap.add_argument('--axe-js',required=True, type=Path,help='Locally reviewed, version-pinned axe-core min.js')
    ap.add_argument('--axe-sha256',required=True,help='Exact reviewed axe-core SHA256')
    ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args()
    u=urlparse(args.staging_url)
    # No unsuspected production, localhost, or external endpoint. Explicit staging hostname is mandatory.
    if u.scheme!='https' or not u.hostname or 'staging' not in u.hostname.lower() or u.username or u.password or u.fragment:
        sys.exit('HOLD: HTTPS staging hostname required; public production not eligible')
    if not args.axe_js.is_file() or hashlib.sha256(args.axe_js.read_bytes()).hexdigest()!=args.axe_sha256.lower():
        sys.exit('HOLD: missing or altered reviewed axe-core bundle')
    args.out.mkdir(parents=True,exist_ok=True)
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in (320,360,390,768,1024,1440,1920):
            context=browser.new_context(viewport={'width':width,'height':900})
            page=context.new_page()
            page.add_init_script('''(() => {window.__fvCwv={lcp:null,cls:0};
                new PerformanceObserver(list=>{for(const e of list.getEntries()){if(!e.hadRecentInput)window.__fvCwv.cls+=e.value;}}).observe({type:'layout-shift',buffered:true});
                new PerformanceObserver(list=>{for(const e of list.getEntries())window.__fvCwv.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});})()''')
            response=page.goto(args.staging_url,wait_until='networkidle',timeout=30000)
            if not response or response.status!=200: raise RuntimeError('HOLD: staging response not HTTP 200')
            page.wait_for_timeout(3500)
            if page.locator('[data-fv-r429]').count()!=1: raise RuntimeError('HOLD: exactly one genuine installed component required')
            if page.evaluate('document.documentElement.scrollWidth>innerWidth'): raise RuntimeError('HOLD: horizontal overflow')
            page.add_script_tag(path=str(args.axe_js))
            axe=page.evaluate('''async () => await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})''')
            if axe['violations']: raise RuntimeError('HOLD: axe accessibility violations')
            cwv=page.evaluate('window.__fvCwv')
            if cwv['lcp'] is None: raise RuntimeError('HOLD: no navigated LCP observation')
            page.screenshot(path=str(args.out/f'{width}.png'),full_page=True)
            results.append({'width':width,'http':response.status,'lcp_ms':cwv['lcp'],'cls':cwv['cls'],'axe_violations':0,'url':page.url})
            context.close()
        browser.close()
    (args.out/'navigated_acceptance.json').write_text(json.dumps({'results':results,'scope':'Lab-only, not real-user p75 CWV','axe_sha256':args.axe_sha256},sort_keys=True,indent=2)+'\n')
    print('PASS 7 real navigation scenarios; field p75 and screen-reader gates still require independent review')
if __name__=='__main__':main()
