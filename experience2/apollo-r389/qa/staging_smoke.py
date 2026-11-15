#!/usr/bin/env python3
"""READ-ONLY real installed staging smoke, deliberately refuses production.

Usage:
  python qa/staging_smoke.py --url https://staging.example.test/apollo-review/ \
    --approved-staging-host staging.example.test --axe-script /path/to/axe.min.js \
    --axe-sha256 <reviewed axe-core SHA256> --output-dir /tmp/apollo-r389-stage

The axe script must be a separately sourced, checksum-reviewed genuine axe-core build.
It is not bundled, downloaded, or loaded by visitor-facing WordPress code.
This script cannot run from the unapproved local fixture as staging acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

VIEWPORTS=(320,390,768,1440,1920)
PRODUCTION={'finalvestige.com','www.finalvestige.com'}

def guard(url, allowed):
    dest=urlparse(url)
    if dest.scheme!='https' or not dest.hostname or dest.hostname.lower()!=allowed.lower() or dest.hostname.lower() in PRODUCTION:
        raise ValueError('HARD STOP: explicit HTTPS non-production staging host must match --approved-staging-host')
    if dest.username or dest.password or dest.fragment:
        raise ValueError('HARD STOP: no URL credentials or fragments')
    return dest.hostname.lower()

def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--url',required=True)
    a.add_argument('--approved-staging-host',required=True)
    a.add_argument('--axe-script',required=True)
    a.add_argument('--axe-sha256',required=True)
    a.add_argument('--output-dir',required=True)
    a.add_argument('--chromium',default='/usr/bin/chromium')
    args=a.parse_args()
    host=guard(args.url,args.approved_staging_host)
    axe_path=Path(args.axe_script)
    if not axe_path.is_file() or len(args.axe_sha256)!=64 or sha_file(axe_path)!=args.axe_sha256.lower():
        raise ValueError('HARD STOP: genuine axe-core bundle must be present and pinned to a reviewed SHA256')
    folder=Path(args.output_dir)
    folder.mkdir(parents=True,exist_ok=True)
    output={'kind':'REAL_INSTALLED_STAGING_CANDIDATE','url':args.url,'approved_host':host,'axe_bundle_sha256':args.axe_sha256,
            'contexts':[], 'production_changes':False,'release_allowed':False}
    failures=[]
    vitals_script="""window.__fvVitals={lcp:null,cls:0};try{
    new PerformanceObserver(l=>{for(const e of l.getEntries())window.__fvVitals.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
    new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__fvVitals.cls+=e.value}).observe({type:'layout-shift',buffered:true});
    }catch(e){window.__fvVitals.error=String(e)}"""
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=args.chromium,args=['--no-sandbox'])
        try:
            for width in VIEWPORTS:
                ctx=browser.new_context(viewport={'width':width,'height':880},java_script_enabled=True)
                page=ctx.new_page()
                page.add_init_script(vitals_script)
                response=page.goto(args.url,wait_until='load',timeout=30000)
                page.wait_for_timeout(500)
                item={'width':width,'http_status':response.status if response else None,'csp_header':response.headers.get('content-security-policy') if response else None}
                item['gallery_present']=page.locator('[data-fv-r384-gallery]').count()==1
                item['card_count']=page.locator('[data-fv-r384-record]').count()
                item['publication_count']=page.locator('[data-fv-r384-publication]').count()
                item['nasa_card_links']=page.locator('[data-fv-r384-nasa]').count()
                item['free_ctas']=page.locator('[data-fv-free-cta]').count()
                item['overflow']=page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1')
                item['computed_background']=page.locator('[data-fv-r384-gallery]').evaluate('(el)=>getComputedStyle(el).backgroundColor') if item['gallery_present'] else None
                item['stylesheets']=page.evaluate("[...document.styleSheets].map(x=>x.href).filter(Boolean)")
                item['local_vitals']=page.evaluate('window.__fvVitals')
                page.add_script_tag(path=str(axe_path))
                item['axe_version']=page.evaluate('window.axe&&window.axe.version')
                if not item['axe_version']:
                    failures.append(f'{width}: supplied bundle failed genuine axe.version guard')
                    item['axe_violations']=['axe.js missing or invalid']
                else:
                    axe=page.evaluate("""async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
                      return r.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.length}))}""")
                    item['axe_violations']=axe
                if not (response and response.ok and item['gallery_present'] and item['card_count']==6
                      and item['publication_count']==2 and item['nasa_card_links']==6 and item['free_ctas']==1
                      and not item['overflow'] and item['computed_background']=='rgb(21, 27, 32)' and not item['axe_violations']):
                    failures.append(f'{width}: staging structural/stylesheet/axe acceptance incomplete')
                if not item['csp_header']:
                    failures.append(f'{width}: CSP response header not established (manual governance required)')
                page.screenshot(path=str(folder/f'{width}-installed-staging.png'),full_page=True,animations='disabled')
                if width==1440:
                    page.pdf(path=str(folder/'installed-staging-document.pdf'),format='A4',print_background=True)
                ctx.close()
                # No action beyond read-only page navigation and fixture capture.
                ctx2=browser.new_context(viewport={'width':width,'height':880},java_script_enabled=False)
                nojs=ctx2.new_page()
                nojs.goto(args.url,wait_until='load',timeout=30000)
                item['nojs_cards']=nojs.locator('[data-fv-r384-record]').count()
                item['nojs_disclosures']=nojs.locator('details').count()
                if item['nojs_cards']!=6 or item['nojs_disclosures']!=6:
                    failures.append(f'{width}: no-JavaScript evidence incomplete')
                ctx2.close()
                output['contexts'].append(item)
        finally:
            browser.close()
    output['blockers']=failures
    output['status']='LOCAL_STAGING_TESTS_PASSED_BUT_NO_RELEASE_APPROVAL' if not failures else 'HOLD_STAGING_QA_FAILED'
    (folder/'staging-browser-evidence.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(json.dumps({'status':output['status'],'widths':VIEWPORTS,'blockers':failures},indent=2))
    if failures:
        raise SystemExit(1)

if __name__=='__main__':main()
