#!/usr/bin/env python3
"""R42 actual-custody, PHP-rendered Atlas: Chromium fail-open and print regression.

Browser navigation is blocked in the current runner. set_content is NOT HTTP,
WordPress, axe, LCP, CLS, or production accessibility certification.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import build_wordpress_stage as stage

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)

def check(condition, name):
    if not condition:
        raise AssertionError(name)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,help='Optional screenshot and deterministic QA receipt directory')
    args=ap.parse_args()
    out=args.output
    if out:out.mkdir(parents=True,exist_ok=True)
    receipt={'schema':'fv.ex2.apollo.r42.qa.v1','release':'STAGING_HOLD',
        'transport':'ACTUAL_PHP_RENDERED_PLAYWRIGHT_SET_CONTENT_NOT_HTTP',
        'axe':'NOT_EXECUTED_APPROVED_BUNDLE_UNAVAILABLE','hosted_lcp_cls_inp':'NOT_MEASURED',
        'authentic_wordpress':'NOT_TESTED','performance_scope':'SYNTHETIC_SET_CONTENT_NOT_HOSTED',
        'cases':[],'regression_checks':[]}
    from tempfile import TemporaryDirectory
    with TemporaryDirectory(prefix='fv-r42-') as tmp:
        destination = Path(tmp)
        stage.build(destination)
        if out:
            (out/'stage').mkdir(exist_ok=True)
            shutil.copyfile(destination/'STAGING-MANIFEST.json',out/'stage/STAGING-MANIFEST.json')
        plugin = destination / 'fv-ex2-evidence-atlas'
        proc = subprocess.run(['php', str(HERE/'tests/wordpress_shortcode_probe.php'),
            str(plugin/'final-vestige-ex2-evidence-atlas.php')],
            capture_output=True, text=True, check=True,
            env={**os.environ, 'FV_SINGULAR':'1'})
        fragment = json.loads(proc.stdout)['markup']
        css = (plugin/'assets/atlas.css').read_text()
        js = (plugin/'assets/atlas.js').read_text()
        def fixture(inject=''):
            return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width,initial-scale=1">'
                    '<style>'+css+'</style></head><body><main>'+fragment+'</main>'
                    +inject+'<script>'+js+'</script></body></html>')
        cases=0
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/usr/bin/chromium',
                headless=True, args=['--no-sandbox'])
            for enabled in (False, True):
                for width in WIDTHS:
                    context=browser.new_context(viewport={'width':width,'height':900},
                        java_script_enabled=enabled, has_touch=width<500,
                        is_mobile=width<500, reduced_motion='reduce')
                    page=context.new_page()
                    errors=[];requests=[]
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.on('request', lambda request: requests.append(request.url))
                    page.evaluate("""() => {
                      window.__fvPerf={lcp:[],shifts:[]};
                      try {new PerformanceObserver(list => window.__fvPerf.lcp.push(...list.getEntries().map(x => x.startTime)))
                           .observe({type:'largest-contentful-paint',buffered:true});} catch (_) {}
                      try {new PerformanceObserver(list => window.__fvPerf.shifts.push(...list.getEntries().map(x => ({value:x.value,hadRecentInput:x.hadRecentInput}))))
                           .observe({type:'layout-shift',buffered:true});} catch (_) {}
                    }""")
                    page.set_content(fixture())
                    check(not errors and not requests, 'no JS errors/external assets')
                    check(page.locator('[data-fva-record]:visible').count()==6,'six sources')
                    check(page.locator('[data-fva-jump]').count()==6,'six source-index links')
                    check(page.locator('[data-fva-jump]').nth(2).get_attribute('href')=='#fva-record-03',
                        'source index anchors based on custody')
                    check(page.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==6,
                        'six NASA citations')
                    check(page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),
                        'responsive reflow '+str(width))
                    summary=page.locator('[data-fva-drawer] summary').first
                    summary.focus(); summary.press('Enter')
                    check(page.locator('[data-fva-drawer]').first.get_attribute('open') is not None,
                        'keyboard source drawer')
                    if enabled:
                        button=page.locator('[data-fva-filter="1967"]')
                        check(button.evaluate('e=>e.getBoundingClientRect().height')>=44,
                            'touch target')
                        (button.tap() if width<500 else button.click())
                        check(page.locator('[data-fva-record]:visible').count()==3,
                            'year filter')
                        jump=page.locator('[data-fva-jump]').nth(2)
                        jump.focus();jump.press('Enter')
                        page.wait_for_timeout(50)
                        check(page.locator('[data-fva-record]:visible').count()==6,
                            'source jump restores filtered evidence')
                        check(page.evaluate('document.activeElement.id')=='fva-record-03',
                            'source jump transfers keyboard focus')
                        check(page.evaluate("location.hash==='#fva-record-03'"),
                            'source jump preserves permalink fragment')
                    else:
                        check(not page.locator('[data-fva-controls]').is_visible(),
                            'no-JS hidden controls')
                    page.wait_for_timeout(200)
                    perf=page.evaluate("""() => ({
                       synthetic_lcp_ms:window.__fvPerf.lcp.length ? Math.round(Math.max(...window.__fvPerf.lcp)) : null,
                       synthetic_cls: Number(window.__fvPerf.shifts.filter(x=>!x.hadRecentInput)
                         .reduce((sum,x)=>sum+x.value,0).toFixed(5)),
                       observed_shift_entries:window.__fvPerf.shifts.length
                    })""")
                    screenshot=None
                    if out and width in (390,1440):
                        page.evaluate('document.activeElement && document.activeElement.blur()')
                        page.evaluate('window.scrollTo(0,0)')
                        path=out/('r42-evidence-%d-%s.png' % (width,'js' if enabled else 'nojs'))
                        page.screenshot(path=str(path),full_page=True,animations='disabled')
                        screenshot={'name':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
                    receipt['cases'].append({'width':width,'javascript':enabled,'status':'PASS','screenshot':screenshot, 'synthetic_web_vitals':perf})
                    cases+=1;context.close()
            # Fail-open after listeners attach but before the first application finishes.
            corruption='''<script>(()=>{const x=document.querySelector('[data-fva-record]');
              const data=x.dataset;let reads=0;Object.defineProperty(x,'dataset',{
              configurable:true,get(){if(++reads===3)data.fvaYear='9999';return data;}})})();</script>'''
            page=browser.new_page();page.set_content(fixture(corruption))
            check(page.locator('[data-fva-record]:visible').count()==6,
                  'all custody must survive failure')
            check(not page.locator('[data-fva-controls]').is_visible(),
                  'no dead controls after rollback')
            receipt['regression_checks'].append('PASS: post-preflight corruption rolls back controls while retaining six sources')
            page.close()
            # Client-side source index tampering must leave every record accessible.
            tamper='''<script>document.querySelector('[data-fva-jump]').setAttribute('href','#invented-location');</script>'''
            page=browser.new_page();page.set_content(fixture(tamper))
            check(page.locator('[data-fva-record]:visible').count()==6,
                  'tampered source jump keeps six records')
            check(not page.locator('[data-fva-controls]').is_visible(),
                  'tampered source jump refuses enhancement')
            receipt['regression_checks'].append('PASS: invalid index target rejects JS enhancement; six records remain')
            page.close()
            # Printing must restore filtered records and show provenance + source URLs.
            page=browser.new_page(viewport={'width':768,'height':900})
            page.set_content(fixture())
            page.locator('[data-fva-filter="1967"]').click()
            check(page.locator('[data-fva-record]:visible').count()==3,'print setup')
            page.emulate_media(media='print')
            check(page.locator('[data-fva-record]:visible').count()==6,
                  'print all six, regardless of active filter')
            check(page.locator('[data-fva-drawer] dl').first.is_visible(),
                  'print closed source drawer contents')
            check('nasa.gov/image-detail' in page.evaluate(
                  "getComputedStyle(document.querySelector('.fva-card__external'),'::after').content"),
                  'print exact NASA destination')
            check(not page.locator('[data-fva-controls]').is_visible(),
                  'hide interactive controls on paper')
            check(not page.locator('[data-fva-jump]').first.is_visible(),
                  'print omits redundant interactive source index')
            receipt['regression_checks'].append('PASS: print mode restores 6 sources, expands provenance and prints original NASA URLs')
            if out:page.pdf(path=str(out/'r42-evidence-custody-print.pdf'),print_background=True)
            page.close();browser.close()
        if out:(out/'R42_QA_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        print('PASS R42: %d/14 real Chromium component cases; fail-open and print custody checks' % cases)
        print('HOLD: no navigated HTTP, WordPress install, axe, Safari, hosted LCP/CLS/INP')

if __name__=='__main__':
    main()
