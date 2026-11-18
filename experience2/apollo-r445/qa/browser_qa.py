#!/usr/bin/env python3
"""Real Chromium layout/interaction testing on actual PHP HTML via set_content; NOT navigated staging or axe."""
from pathlib import Path
import json,os,subprocess
from urllib.parse import urlsplit,parse_qs
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA/screenshots'; OUT.mkdir(parents=True,exist_ok=True)
WIDTHS=[320,360,390,768,1024,1440,1920]
QUERY='utm_source=youtube&utm_medium=organic_social&utm_campaign=apollo_pilot_2026_11&utm_content=EXAMPLE_ASSET_123'
DEST='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def main():
    html=subprocess.check_output(['php',str(ROOT/'qa/fixture.php'),QUERY],text=True)
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.getenv('FV_CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
        try:
            for w in WIDTHS:
                for enabled in (True,False):
                    context=browser.new_context(viewport={'width':w,'height':850},has_touch=w<=390,java_script_enabled=enabled,reduced_motion='reduce')
                    page=context.new_page();page.set_content(html,wait_until='load')
                    roots=page.locator('[data-r444-root]');assert roots.count()==2
                    first=roots.first; second=roots.nth(1)
                    assert first.locator('a[href^="https://www.nasa.gov/"]').count()==5
                    assert first.locator('.fv-r444__next a').count()==1
                    assert first.locator('[data-r444-record]').count()==5
                    assert first.get_by_text('Historical interpretation: review pending').count()==1
                    assert first.get_by_text('Commercial image rights: not cleared').count()==1
                    assert not page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1'),f'overflow: {w}'
                    a=first.locator('.fv-r444__next a');u=urlsplit(a.get_attribute('href'))
                    assert u.scheme+'://'+u.netloc+u.path==DEST
                    assert parse_qs(u.query)=={'utm_source':['youtube'],'utm_medium':['organic_social'],'utm_campaign':['apollo_pilot_2026_11'],'utm_content':['EXAMPLE_ASSET_123']}
                    assert second.locator('.fv-r444__next a').get_attribute('href').endswith('utm_content=VIDEOEXAMPLE123')
                    first.locator('summary').first.focus();page.keyboard.press('Enter')
                    assert first.locator('details').first.get_attribute('open') is not None
                    if enabled:
                        assert first.locator('[data-r444-controls]:visible').count()==1
                        control=first.get_by_role('button',name='Later account')
                        (control.tap() if w<=390 else control.click())
                        assert first.locator('[data-r444-record]:visible').count()==1
                        assert second.locator('[data-r444-record]:visible').count()==5
                        assert first.locator('[data-r444-count]').inner_text()=='1 of 5 source records shown'
                        first.get_by_role('button',name='All five').click()
                        assert first.locator('[data-r444-record]:visible').count()==5
                    else:
                        assert first.locator('[data-r444-controls]:visible').count()==0
                        assert first.locator('[data-r444-record]:visible').count()==5
                    screenshot=f'{w}-{"js" if enabled else "nojs"}.png'
                    page.screenshot(path=str(OUT/screenshot),full_page=True)
                    results.append({'viewport':w,'javascript':enabled,'result':'PASS','php_fixture':True,'navigation':'set_content','screenshot':screenshot,'axe_core':'NOT_RUN','navigated_lcp_cls':'NOT_RUN'})
                    context.close()
            for label,kwargs in [('forced-colors',{'forced_colors':'active'}),('hi-dpi',{'device_scale_factor':2})]:
                ctx=browser.new_context(viewport={'width':390,'height':850},**kwargs)
                pg=ctx.new_page();pg.set_content(html,wait_until='load')
                assert not pg.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
                pg.screenshot(path=str(OUT/f'390-{label}.png'),full_page=True);ctx.close()
            ctx=browser.new_context(viewport={'width':900,'height':900})
            pg=ctx.new_page();pg.set_content(html,wait_until='load');pg.emulate_media(media='print')
            pg.screenshot(path=str(OUT/'900-print.png'),full_page=True);ctx.close()
            ctx=browser.new_context();pg=ctx.new_page()
            try:
                pg.goto('https://localhost.invalid/apollo-staging',wait_until='domcontentloaded',timeout=3000)
                nav={'result':'UNEXPECTED_NAVIGATION_ALLOWED','note':'This is not the approved WordPress staging URL'}
            except Exception as exc: nav={'result':'BLOCKED','error':str(exc).splitlines()[0][:220]}
            ctx.close()
        finally: browser.close()
    record={'cases':results,'count':len(results),'extra_screenshots':['390-forced-colors.png','390-hi-dpi.png','900-print.png'],'navigation_probe':nav,'genuine_axe':'NOT_RUN','navigated_lcp_cls':'NOT_RUN','staging_wordpress':'NOT_RUN','commercial_sales':'UNKNOWN'}
    (ROOT/'QA/browser_results.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(f'PASS {len(results)}/{len(results)} real Chromium PHP-rendered JS/noJS viewport cases; staging/axe/LCP/CLS NOT RUN; navigation {nav["result"]}')

if __name__=='__main__':main()
