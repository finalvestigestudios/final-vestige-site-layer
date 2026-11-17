"""Read-only installed WordPress acceptance, STRICT HOLD without approved staging.
Unlike qa/browser_qa.py, this MUST use a genuine HTTPS page.goto and pinned axe.
Local HTTP / set_content / preview HTML are NOT accepted as staging evidence.
Never treats lab CWV as field p75 or outbound clicks as purchases.
"""
import argparse, hashlib, json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

SIZES=(320,360,390,768,1024,1440,1920)
BOOT="""(() => {
 window.__r432Vitals={lcp:null,cls:0,unsupported:[]};
 try{new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__r432Vitals.lcp=e.startTime)).observe({type:'largest-contentful-paint',buffered:true});}catch(e){window.__r432Vitals.unsupported.push('lcp:'+e);}
 try{new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__r432Vitals.cls+=e.value})).observe({type:'layout-shift',buffered:true});}catch(e){window.__r432Vitals.unsupported.push('cls:'+e);}
})();"""

def stop(msg): raise SystemExit('HOLD: '+msg)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--staging-url',required=True)
    p.add_argument('--approved-host',required=True,help='Exact founder-approved staging host')
    p.add_argument('--axe-js',required=True,type=Path,help='Reviewed pinned axe-core source')
    p.add_argument('--axe-sha256',required=True)
    p.add_argument('--out',required=True,type=Path)
    a=p.parse_args()
    url=urlsplit(a.staging_url)
    if url.scheme!='https' or url.hostname!=a.approved_host or 'staging' not in a.approved_host.lower() or url.username or url.password or url.port not in (None,443) or url.fragment:stop('exact approved HTTPS staging host required')
    if not a.axe_js.is_file() or len(a.axe_sha256)!=64 or hashlib.sha256(a.axe_js.read_bytes()).hexdigest()!=a.axe_sha256.lower():stop('reviewed SHA-pinned axe-core missing or altered')
    a.out.mkdir(parents=True,exist_ok=True)
    evidence=[]
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for width in SIZES:
                context=browser.new_context(viewport={'width':width,'height':900})
                page=context.new_page();page.add_init_script(BOOT)
                response=page.goto(a.staging_url,wait_until='load',timeout=30000)
                if response is None or response.status!=200 or urlsplit(page.url).hostname!=a.approved_host:stop('staging redirect/HTTP not approved')
                if page.locator('[data-fv-r432]').count()!=1:stop('one real, installed R432 shortcode required')
                if page.locator('[data-fv-r432] .fv-r432__rights summary').count()!=1:stop('source/rights disclosure absent')
                if page.locator('[data-fv-r432] .fv-r430__question').count()!=3 or page.locator('[data-fv-r432] .fv-r429__plate').count()!=3:stop('source-custodied parent components absent')
                if page.locator('[data-fv-r432] .fv-r429__cta').count()!=1:stop('one real investigation CTA required')
                if 'finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/' not in page.locator('[data-fv-r432] .fv-r429__cta').get_attribute('href'):stop('CTA target mismatch')
                if page.locator('[data-fv-r432] [data-fv-r432-actions]:not([hidden])').count()!=1:stop('notebook JS initialization failed')
                if page.evaluate('document.documentElement.scrollWidth>innerWidth'):stop(f'horizontal overflow at {width}px')
                page.add_script_tag(path=str(a.axe_js))
                axe=page.evaluate("""async()=>{if(typeof axe==='undefined')throw Error('axe absent');return axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})}""")
                if axe['violations']:stop('axe WCAG findings '+json.dumps([{'id':v['id'],'impact':v['impact'],'nodes':len(v['nodes'])} for v in axe['violations']]))
                page.wait_for_timeout(1600)
                vitals=page.evaluate('window.__r432Vitals')
                if not vitals or vitals['lcp'] is None or vitals['unsupported']:stop(f'LCP/CLS navigation observer unavailable at {width}')
                page.screenshot(path=str(a.out/f'{width}.png'),full_page=True)
                evidence.append({'width_px':width,'actual_staging_http':200,'lab_lcp_ms':vitals['lcp'],'lab_cls':vitals['cls'],'axe_violations':0})
                context.close()
            context=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':900})
            page=context.new_page();page.goto(a.staging_url,wait_until='domcontentloaded',timeout=30000)
            if page.locator('[data-fv-r432] .fv-r430__question').count()!=3 or page.locator('[data-fv-r432-actions]:visible').count()!=0:stop('no-JS fallback not readable/controls inert')
            page.locator('[data-fv-r432] .fv-r430__reason summary').first.click()
            if not page.locator('[data-fv-r432] .fv-r430__reason').first.evaluate('(x)=>x.open'):stop('no-JS disclosure not keyboard/touch compatible')
            page.screenshot(path=str(a.out/'390-nojs.png'),full_page=True)
            context.close()
        finally:browser.close()
    result={'status':'PASS_STAGING_LAB_ONLY','entries':evidence,'axe_sha256':a.axe_sha256.lower(),'field_p75':'NOT MEASURED','real_sales':'NOT MEASURED','source_integrity':'R432 seven-pin gate (installed staging must be verified independently)','QD_review':'REQUIRED','founder_release':'REQUIRED'}
    (a.out/'staging-acceptance.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS staged WordPress navigation + axe + lab LCP/CLS (NOT field p75); QD/launch still HOLD')
if __name__=='__main__': main()
