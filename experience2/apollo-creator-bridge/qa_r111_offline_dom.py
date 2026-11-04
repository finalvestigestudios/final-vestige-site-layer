#!/usr/bin/env python3
"""Genuine Chromium DOM acceptance of a LOCAL Apollo HTML copy.

This is supplemental browser evidence only: set_content() does not measure
HTTP, CDN, WordPress, hosted Core Web Vitals, merchant outcomes, or rights.
No network calls, user events, forms, cookies, or analytics are sent.
"""
import argparse
import hashlib
import json
from pathlib import Path

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--html', type=Path, default=Path(__file__).with_name('landing-preview.html'))
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--axe', type=Path, help='Already available approved local axe.min.js; never fetched')
    parser.add_argument('--chromium-path', type=Path, help='Already installed Chromium executable, no browser download')
    args = parser.parse_args()
    source_bytes = args.html.read_bytes()
    source = source_bytes.decode('utf-8')
    require(source.count('data-fv-primary-cta') == 1, 'ambiguous primary action')
    require('<img' not in source and '<iframe' not in source, 'uncleared image/embed')
    require('tabindex="-1" aria-labelledby="classroom-title"' in source, 'no native fragment focus target')
    require('#classroom-preview:target' in source, 'no visible target location')
    if args.axe:
        require(args.axe.is_file(), 'offline axe file is missing')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = {'schema': 'fv.apollo.r111.offline-dom.v1',
              'status': 'INCOMPLETE_STAGING_HOLD',
              'html_sha256': sha(source_bytes),
              'execution': 'LOCAL_CHROMIUM_IN_MEMORY_NOT_HTTP_OR_WORDPRESS',
              'measurements': {'lcp': 'NOT_MEASURED_IN_MEMORY', 'cls': 'NOT_MEASURED_IN_MEMORY',
                               'qualified_sessions': 'NOT_OBSERVABLE', 'paid_orders': 'NOT_OBSERVABLE'},
              'modes': [], 'screenshots': [], 'axe': 'NOT_EXECUTED_NO_APPROVED_BUNDLE'}
    def receipt():
        temp = out/'r111-offline-dom.partial.tmp'
        temp.write_text(json.dumps(report, sort_keys=True, indent=2)+'\n', encoding='utf8')
        temp.replace(out/'r111-offline-dom.partial.json')
    receipt()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=str(args.chromium_path) if args.chromium_path else None)
        report['chromium'] = browser.version
        try:
            for width in WIDTHS:
                for js in (False, True):
                    context = browser.new_context(viewport={'width':width,'height':900},
                            java_script_enabled=js, has_touch=width <=390,
                            is_mobile=width <=390, reduced_motion='reduce')
                    page = context.new_page()
                    external = []
                    page.on('request', lambda req: external.append(req.url))
                    # No HTTP/browser navigation. The actual local HTML is executed in Chromium.
                    page.set_content(source, wait_until='load')
                    label = f'{width}px js={js}'
                    require(not external, label+': external request was attempted')
                    require(page.locator('a[data-fv-primary-cta]').count()==1, label+': CTA missing')
                    require(page.locator('table tbody tr').count()==6, label+': NASA register must have six rows')
                    require(page.locator('[data-fv-claim]').count()==4, label+': four bounded plates missing')
                    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'),label+': page overflow')
                    require(page.locator('[data-fv-lens]').is_visible()==js,label+': no-JS failure')
                    require(page.locator("a[href*='payhip.com'],form,[data-fv-checkout]").count()==0,
                            label+': paid/lead action without verified offer')
                    primary = page.locator('a[data-fv-primary-cta]')
                    if width<=390 and js: primary.tap()
                    else:
                        primary.focus()
                        primary.press('Enter')
                    require(page.evaluate('location.hash')=='#classroom-preview',label+': fragment not navigated')
                    target = page.locator('#classroom-preview')
                    require(target.get_attribute('tabindex')=='-1',label+': focus target missing')
                    require(target.evaluate('(e) => document.activeElement === e'),label+': target not focused')
                    require(target.evaluate('(e) => {const r=e.getBoundingClientRect();return r.top >= -5 && r.top < innerHeight}'),
                            label+': target not in viewport')
                    require(target.locator('details').count()>=2,label+': classroom evidence incomplete')
                    require(target.locator("a[href='#source-custody']").count()==1,label+': source trail missing')
                    source_summary = page.locator('#source-custody details summary').first
                    source_summary.focus()
                    source_summary.press('Enter')
                    require(source_summary.evaluate('(e)=>e.parentElement.open'),label+': source disclosure not keyboard-operable')
                    if js:
                        limits=page.locator('[data-fv-mode="limit"]')
                        limits.click()
                        require(page.locator('[data-fv-claim]:visible').count()==2,label+': bounded lens failed')
                        page.locator('[data-fv-mode="all"]').click()
                        require(page.locator('[data-fv-claim]:visible').count()==4,label+': reset failed')
                        if args.axe and width in (390,1440):
                            page.add_script_tag(content=args.axe.read_text(encoding='utf8'))
                            violations=page.evaluate("""async () => (await axe.run(document.querySelector('main'),{
                                runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}
                            })).violations.map(v=>({id:v.id,count:v.nodes.length}))""")
                            require(not violations,label+': axe violations '+str(violations))
                            report['axe']='EXECUTED_SELECTED_STATE_ZERO_VIOLATIONS'
                    if (width,js) in ((390,True),(1440,False)):
                        path=out/f'r111-offline-{width}-js-{int(js)}.png'
                        page.screenshot(path=str(path),full_page=True,animations='disabled')
                        report['screenshots'].append({'file':path.name,'sha256':sha(path.read_bytes())})
                    report['modes'].append({'width':width,'javascript':js,'result':'PASS',
                                             'action':'FREE_EXERCISE_REACHED_NOT_A_SALE'})
                    receipt()
                    context.close()
        finally:
            browser.close()
    require(len(report['modes'])==14 and len(report['screenshots'])==2,
            'incomplete browser evidence')
    report['status']='OFFLINE_DOM_PASS_RELEASE_STILL_HOLD'
    receipt()
    (out/'r111-offline-dom-complete.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print('14 Chromium DOM modes PASSED; WordPress, HTTP, performance, rights and merchant: NOT VERIFIED')

if __name__=='__main__':
    main()
