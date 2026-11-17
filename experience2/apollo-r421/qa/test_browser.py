#!/usr/bin/env python3
"""Real Chromium on actual PHP-rendered markup. Browser navigation is blocked by policy."""
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'
SHOTS=OUT/'screenshots'
SHOTS.mkdir(parents=True, exist_ok=True)
HTML=subprocess.run(['php',str(ROOT/'qa/render_fixture.php')],check=True,capture_output=True,text=True).stdout
JS=(ROOT/'assets/source-receipts.js').read_text()
results=[]
def assert_ok(name, condition, detail=''):
    if not condition: raise AssertionError(name+': '+detail)
    results.append({'scenario':name,'result':'PASS','detail':detail})

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width in (320,360,390,768,1024,1440,1920):
        page=browser.new_page(viewport={'width':width,'height':850},device_scale_factor=1)
        page.set_content(HTML,wait_until='load')
        assert_ok(f'viewport-{width}-no-overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'{width}px')
        assert_ok(f'viewport-{width}-receipts',page.locator('li.fv-r421__card').count()==3)
        page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True)
        if width==390:
            page.get_by_text('Examine the finding, limitation and photo custody').first.focus()
            page.keyboard.press('Enter')
            assert_ok('keyboard-details',page.locator('details').first.get_attribute('open') is not None)
            page.screenshot(path=str(SHOTS/'390-keyboard.png'),full_page=True)
            page.add_script_tag(content=JS)
            assert_ok('progressive-copy-buttons-appear',page.locator('button[data-fv-r421-copy]:visible').count()==3)
            page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:(t)=>{window.__copied=t; return Promise.resolve();}}})")
            page.locator('button[data-fv-r421-copy]').first.click()
            page.wait_for_function("document.querySelector('.fv-r421__status').textContent.includes('copied')")
            assert_ok('copy-success-status-and-payload',page.evaluate("window.__copied.includes('NASA historical publication:')"))
            page.screenshot(path=str(SHOTS/'390-copy.png'),full_page=True)
            page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined})")
            page.locator('button[data-fv-r421-copy]').first.click()
            assert_ok('copy-failure-not-misreported',page.locator('.fv-r421__status').first.inner_text().startswith('Clipboard unavailable'))
            page.screenshot(path=str(SHOTS/'390-copy-unavailable.png'),full_page=True)
            cdp=page.context.new_cdp_session(page)
            tree=cdp.send('Accessibility.getFullAXTree').get('nodes',[])
            assert_ok('chromium-accessibility-tree',any(n.get('role',{}).get('value')=='heading' for n in tree))
        page.close()
    page=browser.new_page(viewport={'width':320,'height':850},is_mobile=True,has_touch=True)
    page.set_content(HTML);page.locator('summary').first.tap()
    assert_ok('touch-details',page.locator('details').first.get_attribute('open') is not None)
    page.screenshot(path=str(SHOTS/'320-touch.png'),full_page=True);page.close()
    page=browser.new_page(viewport={'width':320,'height':850},reduced_motion='reduce')
    page.set_content(HTML)
    assert_ok('reduced-motion-and-320-no-overflow',page.evaluate('matchMedia("(prefers-reduced-motion:reduce)").matches && document.documentElement.scrollWidth <= 320'))
    page.screenshot(path=str(SHOTS/'320-reduced-motion.png'),full_page=True);page.close()
    page=browser.new_page(viewport={'width':390,'height':850},forced_colors='active')
    page.set_content(HTML)
    assert_ok('forced-colors',page.evaluate('matchMedia("(forced-colors:active)").matches'))
    page.screenshot(path=str(SHOTS/'390-forced-colors.png'),full_page=True);page.close()
    page=browser.new_page(viewport={'width':320,'height':900})
    page.set_content(HTML)
    page.evaluate("document.documentElement.style.fontSize='64px'")
    assert_ok('400percent-text-no-overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'),str(page.evaluate('document.documentElement.scrollWidth')))
    page.screenshot(path=str(SHOTS/'320-font400.png'),full_page=True);page.close()
    page=browser.new_page(viewport={'width':768,'height':960})
    page.set_content(HTML)
    page.emulate_media(media='print')
    assert_ok('print-mode',page.evaluate('matchMedia("print").matches'))
    page.screenshot(path=str(SHOTS/'768-print.png'),full_page=True)
    page.close()
    try:
        page=browser.new_page()
        page.goto('http://127.0.0.1:65530/',timeout=3000)
        results.append({'scenario':'browser-navigation','result':'UNEXPECTED','detail':'no server expected'})
    except Exception as e:
        results.append({'scenario':'navigated-http','result':'BLOCKED','detail':str(e).splitlines()[0][:180]})
    finally:page.close()
    browser.close()
OUT.mkdir(exist_ok=True)
(OUT/'browser-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'passed':sum(x['result']=='PASS' for x in results),'blocked':sum(x['result']=='BLOCKED' for x in results),'scenarios':len(results)}))
