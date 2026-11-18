#!/usr/bin/env python3
"""Real Chromium against actual PHP output via set_content. NOT a navigated WP test."""
import json,os,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
WIDTHS=[320,360,390,768,1024,1440,1920]

def main():
    rendered=subprocess.run(['php',str(ROOT/'qa/fixture.php')],capture_output=True,text=True,check=True).stdout
    out=ROOT/'QA/screenshots';out.mkdir(parents=True,exist_ok=True)
    results=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('FV_CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
        try:
            for w in WIDTHS:
                for enabled in (True,False):
                    context=browser.new_context(viewport={'width':w,'height':900},java_script_enabled=enabled,has_touch=w<=390,reduced_motion='reduce')
                    page=context.new_page();page.set_content(rendered,wait_until='load')
                    assert page.locator('[data-r444-root]').count()==2
                    assert page.locator('[data-r444-record]:visible').count()==10
                    assert page.locator('details').count()==10
                    assert page.locator('a[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]').count()==2
                    assert page.locator('a[href^="https://www.nasa.gov/"]').count()==10
                    assert page.get_by_text('Historical interpretation: review pending').count()==2
                    assert not page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1'),f'overflow width={w}'
                    page.locator('summary').first.focus();page.keyboard.press('Enter');assert page.locator('details').first.get_attribute('open') is not None
                    if enabled:
                        assert page.locator('[data-r444-controls]:visible').count()==2
                        first=page.locator('[data-r444-root]').first
                        later=first.get_by_role('button',name='Later account')
                        (later.tap() if w<=390 else later.click())
                        assert first.locator('[data-r444-record]:visible').count()==1
                        assert page.locator('[data-r444-root]').nth(1).locator('[data-r444-record]:visible').count()==5
                        assert first.locator('[data-r444-count]').inner_text()=='1 of 5 source records shown'
                        first.get_by_role('button',name='All five').click()
                        assert first.locator('[data-r444-record]:visible').count()==5
                    else:
                        assert page.locator('[data-r444-controls]:visible').count()==0
                        assert page.locator('[data-r444-record]:visible').count()==10
                    img=out/f'{w}-{ "js" if enabled else "nojs" }.png'
                    page.screenshot(path=str(img),full_page=True)
                    results.append({'viewport':w,'javascript':enabled,'php_fixture':True,'navigation':'set_content','assertions':'PASS','screenshot':img.name,'genuine_axe':'NOT_RUN','navigated_lcp_cls':'NOT_RUN'})
                    context.close()
            for name,opts in [('forced-colors',{'forced_colors':'active'}),('zoom-200',{'device_scale_factor':2})]:
                c=browser.new_context(viewport={'width':390,'height':900},**opts)
                p=c.new_page();p.set_content(rendered,wait_until='load')
                assert p.locator('[data-r444-record]').count()==10
                assert not p.evaluate('document.documentElement.scrollWidth>innerWidth+1')
                p.screenshot(path=str(out/f'390-{name}.png'),full_page=True);c.close()
            c=browser.new_context(viewport={'width':900,'height':900});p=c.new_page();p.set_content(rendered,wait_until='load');p.emulate_media(media='print');p.screenshot(path=str(out/'900-print.png'),full_page=True);c.close()
            # Record genuine navigation policy failure separately; cannot substitute set_content.
            c=browser.new_context();p=c.new_page()
            try:
                p.goto('file://'+str(ROOT/'qa/fixture.php'),timeout=3500)
                nav={'attempted':True,'result':'UNEXPECTED_NAVIGATION_ALLOWED','note':'Fixture is PHP and not standalone HTML; not staging'}
            except Exception as e:
                nav={'attempted':True,'result':'BLOCKED','error':str(e).splitlines()[0][:200]}
            c.close()
        finally:browser.close()
    artifact={'cases':results,'total_cases':len(results),'special_screenshots':['390-forced-colors.png','390-zoom-200.png','900-print.png'],'navigation_probe':nav,'staging':'NOT_RUN','axe_core':'NOT_RUN','lcp_cls':'NOT_RUN','field_cwv':'NOT_RUN'}
    (ROOT/'QA/browser_results.json').write_text(json.dumps(artifact,indent=2,sort_keys=True)+'\n')
    print(f'PASS {len(results)}/{len(results)} Chromium JS/noJS viewport cases; 3 supplemental captures; real staging/axe/LCP/CLS NOT RUN; navigation {nav["result"]}')

if __name__=='__main__':main()
