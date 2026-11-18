"""Actual Chromium DOM testing; page.set_content OFFLINE, not navigated staging.
Saves screenshots and manifest. Does not claim axe, LCP, CLS, field CWV.
"""
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'
SHOTS=OUT/'screenshots'
WIDTHS=[320,360,390,768,1024,1440,1920]
def html(*args):
    p=subprocess.run(['php',str(ROOT/'qa/fixture.php'),*args],capture_output=True,text=True,check=True)
    return p.stdout

def main():
    SHOTS.mkdir(parents=True,exist_ok=True)
    results=[]; errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for enabled in (True,False):
            for width in WIDTHS:
                ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,reduced_motion='reduce' if width==390 else 'no-preference')
                page=ctx.new_page();page.set_content(html(),wait_until='load');page.wait_for_timeout(80)
                case=f'{width}-'+('js' if enabled else 'nojs')
                try:
                    cards=page.locator('[data-fv-r447-card]');assert cards.count()==4
                    assert page.locator('img').count()==0
                    assert page.locator('a[href*="the-hatch-opened-inward"]').count()==1
                    assert page.locator('a[href^="https://www.nasa.gov"],a[href^="https://images.nasa.gov"]').count()==5
                    assert all(cards.nth(i).is_visible() for i in range(4))
                    if enabled:
                        page.get_by_role('button',name='Before the fire').click()
                        assert sum(cards.nth(i).is_visible() for i in range(4))==2
                        assert page.locator('[data-fv-r447-count]').inner_text()=='2 of 4 source records'
                        page.get_by_role('button',name='Later exhibit').focus()
                        page.keyboard.press('Enter')
                        assert sum(cards.nth(i).is_visible() for i in range(4))==1
                        page.get_by_role('button',name='All four records').click()
                        assert sum(cards.nth(i).is_visible() for i in range(4))==4
                    else:assert not page.locator('[data-fv-r447-controls]').is_visible()
                    summary=page.locator('.fv-r447__card details summary').first
                    summary.focus();page.keyboard.press('Enter');assert page.locator('.fv-r447__card details').first.get_attribute('open') is not None
                    scroll=page.evaluate('document.documentElement.scrollWidth');viewport=page.evaluate('window.innerWidth');assert scroll<=viewport+1,(scroll,viewport)
                    if width==390 and enabled:
                        assert page.locator('[data-fv-r447-controls]').is_visible()
                    page.screenshot(path=str(SHOTS/(case+'.png')),full_page=True,animations='disabled')
                    results.append({'case':case,'status':'PASS','cards':4,'horizontal_overflow_px':max(0,scroll-viewport),'screenshot':f'screenshots/{case}.png'})
                except Exception as e:
                    errors.append({'case':case,'error':repr(e)})
                finally:
                    ctx.close()
        # Additional two cases: keyboard/touch equivalent and forced colors.
        ctx=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,device_scale_factor=2)
        page=ctx.new_page();page.set_content(html(),wait_until='load');page.wait_for_timeout(80)
        btn=page.get_by_role('button',name='Board record');btn.tap()
        assert sum(page.locator('[data-fv-r447-card]').nth(i).is_visible() for i in range(4))==1
        page.screenshot(path=str(SHOTS/'touch-390.png'),full_page=True,animations='disabled');results.append({'case':'touch-390','status':'PASS'})
        ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':900},forced_colors='active',reduced_motion='reduce')
        page=ctx.new_page();page.set_content(html(),wait_until='load');page.screenshot(path=str(SHOTS/'forced-colors-390.png'),full_page=True,animations='disabled')
        assert page.locator('[data-fv-r447-card]').count()==4
        results.append({'case':'forced-colors-390','status':'PASS'})
        ctx.close();browser.close()
    report={'component':'apollo-r447','mode':'offline-php-html-in-real-chromium-page.set_content','qa_date':'2026-11-17',
            'results':results,'errors':errors,'checks_passed':len(results),'checks_failed':len(errors),
            'axescan':'NOT_RUN_NO_TRUSTED_BUNDLE','lcp':'NOT_RUN_NO_NAVIGATION','cls':'NOT_RUN_NO_NAVIGATION',
            'screen_reader':'NOT_RUN','wordpress_staging':'NOT_RUN','field_cwv':'NOT_RUN',
            'reproduction':'python qa/browser_qa.py; screenshots and this JSON; without site navigation'}
    (OUT/'browser_results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passes':len(results),'failures':len(errors),'errors':errors}))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
