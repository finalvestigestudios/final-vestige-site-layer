"""Real Chromium execution of PHP-generated HTML via set_content (offline, not staging navigation)."""
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA';SHOTS=OUT/'screenshots'
WIDTHS=(320,360,390,768,1024,1440,1920)
def html(*args):
    return subprocess.run(['php',str(ROOT/'qa/fixture.php'),*args],capture_output=True,text=True,check=True).stdout

def main():
    SHOTS.mkdir(parents=True,exist_ok=True)
    results=[];errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for js in (True,False):
            for w in WIDTHS:
                ctx=browser.new_context(viewport={'width':w,'height':900},java_script_enabled=js,reduced_motion='reduce')
                page=ctx.new_page();case=f'{w}-'+('js' if js else 'nojs')
                try:
                    page.set_content(html(),wait_until='load')
                    cards=page.locator('[data-fv-r448-card]')
                    assert cards.count()==4
                    assert page.locator('a[href*="the-hatch-opened-inward"]').count()==1
                    assert page.locator('a[href*="www.nasa.gov"]').count()==5
                    assert page.locator('img').count()==0
                    assert all(cards.nth(i).is_visible() for i in range(4))
                    if js:
                        button=page.get_by_role('button',name='1967 inquiry');button.focus();page.keyboard.press('Enter')
                        assert sum(cards.nth(i).is_visible() for i in range(4))==1
                        assert button.get_attribute('aria-pressed')=='true'
                        page.get_by_role('button',name='Later history').click()
                        assert sum(cards.nth(i).is_visible() for i in range(4))==2
                        page.get_by_role('button',name='All evidence').click()
                        assert all(cards.nth(i).is_visible() for i in range(4))
                    else: assert not page.locator('[data-fv-r448-controls]').is_visible()
                    source=page.locator('.fv-r448__card summary').first
                    source.focus();page.keyboard.press('Enter')
                    assert page.locator('.fv-r448__card details').first.get_attribute('open') is not None
                    scroll=page.evaluate('document.documentElement.scrollWidth');width=page.evaluate('window.innerWidth')
                    assert scroll<=width+1,(scroll,width)
                    page.screenshot(path=str(SHOTS/(case+'.png')),full_page=True,animations='disabled')
                    results.append({'case':case,'status':'PASS','cards':4,'overflow_px':max(0,scroll-width),'screenshot':f'screenshots/{case}.png'})
                except Exception as exc:errors.append({'case':case,'error':repr(exc)})
                finally:ctx.close()
        for name,options in [('touch',{'viewport':{'width':390,'height':844},'is_mobile':True,'has_touch':True}),('forced-colors',{'viewport':{'width':390,'height':844},'forced_colors':'active'}),('200pct',{'viewport':{'width':390,'height':844},'device_scale_factor':2})]:
            ctx=browser.new_context(**options);page=ctx.new_page()
            try:
                page.set_content(html('--duplicate'),wait_until='load')
                if name=='touch':
                    page.get_by_role('button',name='Later history').first.tap()
                    assert sum(page.locator('[data-fv-r448]').first.locator('[data-fv-r448-card]').nth(i).is_visible() for i in range(4))==2
                    assert all(page.locator('[data-fv-r448]').nth(1).locator('[data-fv-r448-card]').nth(i).is_visible() for i in range(4))
                if name=='200pct':
                    page.evaluate("document.documentElement.style.fontSize='200%'")
                    assert page.locator('a[href*="the-hatch-opened-inward"]').count()==2
                scroll=page.evaluate('document.documentElement.scrollWidth');width=page.evaluate('window.innerWidth');assert scroll<=width+1,(scroll,width)
                page.screenshot(path=str(SHOTS/(name+'.png')),full_page=True,animations='disabled')
                results.append({'case':name,'status':'PASS','overflow_px':max(0,scroll-width)})
            except Exception as exc:errors.append({'case':name,'error':repr(exc)})
            finally:ctx.close()
        browser.close()
    report={'sprint':'R448','mode':'local offline PHP markup via Chromium page.set_content','results':results,'errors':errors,'passed':len(results),'failed':len(errors),
            'axe':'NOT_RUN: no independently vetted local axe-core bundle','navigated_lcp':'NOT_RUN: browser navigation blocked','navigated_cls':'NOT_RUN: browser navigation blocked','screen_reader':'NOT_RUN','wordpress_staging':'NOT_RUN','field_cwv':'NOT_RUN'}
    (OUT/'browser_results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':len(results),'failed':len(errors),'errors':errors}))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
