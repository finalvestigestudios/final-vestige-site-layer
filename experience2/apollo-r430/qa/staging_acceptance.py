"""Founder-approved staging-only REAL navigation with pinned axe and lab CWV.

Never treats page.set_content, a screenshot, or lab metrics as real-user p75.
Refuses public production, unapproved hosts, altered axe and missing component.
Read-only: no form submission, cookies, purchases, emails or WP writes.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

SIZES = (320, 360, 390, 768, 1024, 1440, 1920)
VITALS_BOOT = '''(() => {window.__apollo430={lcp:null,cls:0};
try {new PerformanceObserver(list=>{for(const entry of list.getEntries())
if (!entry.hadRecentInput) window.__apollo430.cls+=entry.value;
}).observe({type:'layout-shift',buffered:true});
new PerformanceObserver(list=>{for(const entry of list.getEntries())
window.__apollo430.lcp=entry.startTime;
}).observe({type:'largest-contentful-paint',buffered:true});
} catch(err) {window.__apollo430.error=String(err);} })();'''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--staging-url',required=True)
    ap.add_argument('--approved-host',required=True,help='Exact founder-approved staging hostname')
    ap.add_argument('--axe-js',type=Path,required=True,help='Locally reviewed axe-core version file')
    ap.add_argument('--axe-sha256',required=True,help='Reviewed axe-core SHA-256')
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    parsed=urlparse(args.staging_url)
    if parsed.scheme!='https' or parsed.hostname!=args.approved_host or 'staging' not in args.approved_host or parsed.username or parsed.password or parsed.fragment:
        raise SystemExit('HOLD: exact approved HTTPS staging host required, not production')
    if parsed.port not in (None,443):
        raise SystemExit('HOLD: nonstandard staging port requires separate acceptance')
    if not args.axe_js.is_file() or len(args.axe_sha256)!=64 or hashlib.sha256(args.axe_js.read_bytes()).hexdigest()!=args.axe_sha256.lower():
        raise SystemExit('HOLD: reviewed, SHA-256-pinned axe-core missing or altered')
    args.out.mkdir(parents=True,exist_ok=True)
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for width in SIZES:
                ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1)
                page=ctx.new_page()
                page.add_init_script(VITALS_BOOT)
                response=page.goto(args.staging_url,wait_until='networkidle',timeout=30000)
                if not response or response.status!=200 or page.url.split('/')[2]!=args.approved_host:
                    raise RuntimeError('HOLD: HTTP staging response/redirect not approved')
                page.wait_for_timeout(1800)
                if page.locator('[data-fv-r430]').count()!=1:
                    raise RuntimeError('HOLD: one installed real R430 shortcode required')
                if page.locator('.fv-r430__question').count()!=3 or page.locator('.fv-r429__plate').count()!=3:
                    raise RuntimeError('HOLD: missing actual source records/worksheet')
                if page.locator('.fv-r429__cta').count()!=1:
                    raise RuntimeError('HOLD: single historical next-action CTA required')
                if page.evaluate('document.documentElement.scrollWidth>innerWidth'):
                    raise RuntimeError(f'HOLD: horizontal overflow at {width}px')
                page.add_script_tag(path=str(args.axe_js))
                axe=page.evaluate('''async () => await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})''')
                if axe['violations']:
                    raise RuntimeError('HOLD: axe violations '+json.dumps([{'id':x['id'],'impact':x['impact'],'nodes':len(x['nodes'])} for x in axe['violations']]))
                vitals=page.evaluate('window.__apollo430')
                if not vitals or vitals.get('lcp') is None or vitals.get('error') is not None:
                    raise RuntimeError('HOLD: no genuine navigation LCP observation')
                page.screenshot(path=str(args.out/f'{width}.png'),full_page=True)
                results.append({'width_px':width,'http_status':response.status,'lab_lcp_ms':vitals['lcp'],'lab_cls':vitals['cls'],'axe_violations':0})
                ctx.close()
            ctx=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':900})
            page=ctx.new_page()
            page.goto(args.staging_url,wait_until='domcontentloaded')
            if page.locator('.fv-r430__question').count()!=3:
                raise RuntimeError('HOLD: no-JS source meaning not present')
            page.locator('.fv-r430__reason summary').first.click()
            if not page.locator('.fv-r430__reason').first.evaluate('(e)=>e.open'):
                raise RuntimeError('HOLD: no-JS interaction failed')
            page.screenshot(path=str(args.out/'no-js-navigation.png'),full_page=True)
            ctx.close()
        finally:
            browser.close()
    (args.out/'navigated_acceptance.json').write_text(json.dumps({'result':'PASS lab staging only','entries':results,'axe_sha256':args.axe_sha256,'field_p75':'NOT MEASURED','real_checkout':'NOT MEASURED','independent_QD':'REQUIRED'},sort_keys=True,indent=2)+'\n')
    print('PASS: staged HTTP navigation, pinned axe and lab CWV; field p75 and QD still required')

if __name__=='__main__':main()
