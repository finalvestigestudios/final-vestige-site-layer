#!/usr/bin/env python3
"""Real HTTPS navigation gate. Missing URL or real axe-core is HOLD, never a synthetic pass."""
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
PERFORMANCE_PROBE = '''(() => {
 window.__fvCWV = {lcp:null, cls:0, shifts:0};
 try {new PerformanceObserver(list=>{for(const e of list.getEntries()){window.__fvCWV.lcp=e.startTime}}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){}
 try {new PerformanceObserver(list=>{for(const e of list.getEntries()){if(!e.hadRecentInput){window.__fvCWV.cls+=e.value; window.__fvCWV.shifts++}}}).observe({type:'layout-shift',buffered:true});}catch(e){}
})();'''

def main():
    p = argparse.ArgumentParser(description='Staging-only, read-only browser acceptance; never visits production')
    p.add_argument('--url', default=os.environ.get('FV_APOLLO_STAGING_URL',''))
    p.add_argument('--approved-origin', default=os.environ.get('FV_APOLLO_APPROVED_ORIGIN',''))
    p.add_argument('--axe-js', default=os.environ.get('FV_AXE_CORE_JS',''))
    p.add_argument('--out', default='QA/staging')
    args = p.parse_args()
    output = Path(args.out)
    failures = []
    parsed = urlparse(args.url)
    origin = f'{parsed.scheme}://{parsed.netloc}'
    accepted = (parsed.scheme=='https' and bool(parsed.netloc) and origin == args.approved_origin
                and not parsed.username and not parsed.password
                and parsed.hostname not in ('finalvestige.com','www.finalvestige.com')
                and not parsed.fragment and not parsed.query)
    if not accepted: failures.append('HOLD: a reviewed HTTPS staging URL and matching exact approved origin are required; production and query strings are prohibited')
    axe = Path(args.axe_js) if args.axe_js else None
    if not axe or not axe.is_file() or axe.stat().st_size < 25000:
        failures.append('HOLD: an independently verified full local axe-core bundle is required; no stub or CDN fetch')
    if failures:
        print(json.dumps({'status':'HOLD_NOT_RUN', 'failures':failures},indent=2))
        raise SystemExit(2)
    output.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for width in WIDTHS:
            for js in (True,False):
                context = browser.new_context(viewport={'width':width,'height':900},is_mobile=width<=390,
                                              has_touch=width<=390,java_script_enabled=js,reduced_motion='reduce')
                page=context.new_page()
                if js: page.add_init_script(PERFORMANCE_PROBE)
                try:
                    response=page.goto(args.url, wait_until='load',timeout=25000)
                    page.wait_for_timeout(1500)  # Allow buffered LCP and delayed shift samples.
                    row={'width':width,'js':js,'http_status':response.status if response else None}
                    row['record_count']=page.locator('[data-r438-card]').count()
                    row['educator_count']=page.locator('[data-r440-root]').count()
                    row['paid_cta_count']=page.locator('a[href*="payhip.com"],a[href*="checkout"],form[action*="payment"]').count()
                    row['free_cta_count']=page.locator('.fv-r429__cta a').count()
                    row['horizontal_overflow']=page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
                    row['nasa_source_links']=page.locator('a[href^="https://www.nasa.gov/"]').count()
                    row['violations']=[]
                    if js:
                        page.add_script_tag(path=str(axe))
                        accessibility=page.evaluate("async () => await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})")
                        row['violations']=[{'id':v['id'],'impact':v.get('impact'),'nodes':len(v['nodes'])} for v in accessibility['violations']]
                        row['cwv']=page.evaluate('window.__fvCWV')
                        if row['cwv']['lcp'] is None:failures.append(f'{width}: browser LCP not measurable')
                        elif row['cwv']['lcp'] > 2500:failures.append(f'{width}: LCP over 2500ms')
                        if row['cwv']['cls'] > .1:failures.append(f'{width}: CLS over 0.1')
                        if row['violations']: failures.append(f'{width}: axe WCAG violations')
                    if row['http_status'] != 200:failures.append(f'{width}/{js}: HTTPS not 200')
                    if row['record_count'] < 5:failures.append(f'{width}/{js}: five NASA-linked records not present')
                    if row['educator_count'] != 1:failures.append(f'{width}/{js}: expected exactly one educator component')
                    if row['free_cta_count'] != 1:failures.append(f'{width}/{js}: one contextual free CTA required')
                    if row['paid_cta_count'] != 0:failures.append(f'{width}/{js}: unauthorized commercial CTA')
                    if row['nasa_source_links'] < 2:failures.append(f'{width}/{js}: source links missing')
                    if row['horizontal_overflow']:failures.append(f'{width}/{js}: horizontal overflow')
                    page.screenshot(path=str(output / f"{width}-{'js' if js else 'nojs'}.png"), full_page=True)
                    results.append(row)
                except Exception as exc:
                    failures.append(f'{width}/{js}: navigation or browser check failed: {str(exc)[:250]}')
                finally:
                    context.close()
        browser.close()
    report={'status':'PASS_BROWSER_STAGING' if not failures else 'HOLD_BROWSER_FAILURE',
            'kind':'read-only Chromium navigated staging, lab LCP/CLS; NOT field Core Web Vitals',
            'origin':args.approved_origin,'results':results,'failures':failures,
            'commercial_status':'HOLD_NOT_SELLABLE','release_authorized':False}
    (output/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':report['status'],'screenshots':len(results),'failures':failures},indent=2))
    raise SystemExit(bool(failures))

if __name__ == '__main__':main()
