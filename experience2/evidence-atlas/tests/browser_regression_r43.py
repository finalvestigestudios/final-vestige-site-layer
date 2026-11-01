#!/usr/bin/env python3
"""R43 Playwright: actual PHP-rendered NASA custody, filtered chronology and no-JS.

This is real Chromium on set_content, not a localhost navigation, a WordPress
installation, axe-core, or hosted Core Web Vitals certification.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import build_wordpress_stage as stage
WIDTHS=(320,360,390,768,1024,1440,1920)

def check(value,label):
    if not value:raise AssertionError(label)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    out=ap.parse_args().output;out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        stage.build(Path(tmp))
        package=Path(tmp)/'fv-ex2-evidence-atlas'
        run=subprocess.run(['php',str(HERE/'tests/wordpress_shortcode_probe.php'),str(package/'final-vestige-ex2-evidence-atlas.php')],env={**os.environ,'FV_SINGULAR':'1'},capture_output=True,text=True,check=True)
        frag=json.loads(run.stdout)['markup']
        css=(package/'assets/atlas.css').read_text()
        js=(package/'assets/atlas.js').read_text()
    def fixture(before_js=''):
        return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body><main>'+frag+'</main>'+before_js+'<script>'+js+'</script></body></html>'
    receipt={'schema':'fv.ex2.apollo.r43.qa.v1','release':'STAGING_HOLD','transport':'PHP_RENDERED_PLAYWRIGHT_SET_CONTENT_NOT_HTTP','axe':'NOT_EXECUTED_NO_PINNED_BUNDLE','hosted_lcp_cls_inp':'NOT_MEASURED','authentic_wordpress':'NOT_TESTED','screenshots':[],'cases':[],'adversarial':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for enabled in (False,True):
            for width in WIDTHS:
                ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,has_touch=width<=390,is_mobile=width<=390,reduced_motion='reduce')
                page=ctx.new_page();errors=[];requests=[]
                page.on('pageerror',lambda error: errors.append(str(error)))
                page.on('request',lambda request: requests.append(request.url))
                page.set_content(fixture())
                check(not errors and not requests,f'no errors/network at {width}/{enabled}: {errors} {requests}')
                check(page.locator('[data-fva-record]').count()==6,'six real custody records')
                check(page.locator('[data-fva-chronology] [data-fva-era]').count()==3,'three verified year eras')
                check(page.locator('[data-fva-timejump]').count()==6,'six chronology links')
                check(page.locator('time[datetime="1967-01"]').count()==1,'month-level precision retained')
                check(page.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==6,'six original links')
                check(page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),f'no horizontal overflow at {width}')
                # Test native navigation by year rail under no-JS and enhanced modes.
                link=page.locator('[data-fva-time-id="03"]');link.focus();link.press('Enter')
                check(page.evaluate('location.hash')=='#fva-record-03','native hash destination')
                if enabled:
                    page.wait_for_timeout(50)
                    check(page.evaluate('document.activeElement.id')=='fva-record-03','chronology jump focus')
                    button=page.locator('[data-fva-filter="2017"]')
                    (button.tap() if width<=390 else button.click())
                    check(page.locator('[data-fva-record]:visible').count()==2,'2017 only')
                    link=page.locator('[data-fva-time-id="02"]');link.focus();link.press('Enter')
                    page.wait_for_timeout(50)
                    check(page.locator('[data-fva-record]:visible').count()==6,'chronology restores six records')
                    check(page.evaluate('document.activeElement.id')=='fva-record-02','restore target focus')
                    # Fragment hash changes simulate history navigation to a filtered record.
                    page.locator('[data-fva-filter="2017"]').click()
                    check(page.locator('[data-fva-record]:visible').count()==2,'history setup')
                    page.evaluate("window.location.hash='#fva-record-05'")
                    page.wait_for_timeout(50)
                    check(page.locator('[data-fva-record]:visible').count()==6,'fragment change unhides targeted record')
                    check(page.evaluate('document.activeElement.id')=='fva-record-05','fragment target focus')
                    # Search based on actual source custody notes, not invented copy.
                    page.locator('[data-fva-search]').fill('Kim Shiflett')
                    check(page.locator('[data-fva-record]:visible').count()==2,'NASA credit searchable')
                    page.locator('[data-fva-reset]').click()
                    check(page.locator('[data-fva-record]:visible').count()==6,'reset restores six records')
                else:
                    check(not page.locator('[data-fva-controls]').is_visible(),'no-JS controls unavailable')
                    check(page.locator('[data-fva-record]:visible').count()==6,'no-JS all sources')
                summary=page.locator('[data-fva-drawer] summary').first
                summary.focus();summary.press('Enter')
                check(page.locator('[data-fva-drawer]').first.get_attribute('open') is not None,'keyboard disclosure')
                screenshot=None
                if width in (390,1440):
                    page.evaluate('document.activeElement&&document.activeElement.blur()')
                    page.evaluate('window.scrollTo(0,0)')
                    name=f'r43-chronology-{width}-{("js" if enabled else "nojs")}.png'
                    path=out/name;page.screenshot(path=str(path),full_page=True,animations='disabled')
                    screenshot={'file':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
                    receipt['screenshots'].append(screenshot)
                receipt['cases'].append({'width':width,'javascript':enabled,'status':'PASS','screenshot':screenshot})
                ctx.close()
        # Corrupt timeline-link metadata BEFORE JS initialization; fail-open.
        pre='''<script>document.querySelector('[data-fva-time-id="03"]').setAttribute('href','#invented-coordinate');</script>'''
        page=browser.new_page();page.set_content(fixture(pre))
        check(page.locator('[data-fva-record]:visible').count()==6,'malformed timeline remains readable')
        check(not page.locator('[data-fva-controls]').is_visible(),'corrupted timeline disables enhancement')
        receipt['adversarial'].append('PASS: invented permalink rejects enhancement without hiding any records')
        page.close()
        pre='''<script>document.querySelector('[data-fva-era="1966"]').setAttribute('data-fva-era','1957');</script>'''
        page=browser.new_page();page.set_content(fixture(pre))
        check(page.locator('[data-fva-record]:visible').count()==6,'tampered year retains sources')
        check(not page.locator('[data-fva-controls]').is_visible(),'corrupted year disables enhancement')
        receipt['adversarial'].append('PASS: altered year grouping rejects enhancement without losing records')
        page.close()
        page=browser.new_page(viewport={'width':768,'height':900});page.set_content(fixture())
        page.locator('[data-fva-filter="2017"]').click()
        check(page.locator('[data-fva-record]:visible').count()==2,'print filter setup')
        page.emulate_media(media='print')
        check(page.locator('[data-fva-record]:visible').count()==6,'print six original source records')
        check(page.locator('[data-fva-drawer] dl').first.is_visible(),'print full custody')
        check('nasa.gov/image-detail' in page.evaluate("getComputedStyle(document.querySelector('.fva-card__external'),'::after').content"),'print NASA original URLs')
        receipt['adversarial'].append('PASS: print restores six records and original URLs after 2017-only filter')
        page.close();browser.close()
    (out/'R43_QA_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print('PASS R43 browser: %d/14 responsive cases and %d adversarial/print checks' %(len(receipt['cases']),len(receipt['adversarial'])))
    print('HOLD: localhost navigation blocked; axe/WordPress/hosted CWV not verified')

if __name__=='__main__':main()
