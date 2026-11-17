"""Actual rendered PHP fixture in real Chromium via page.set_content (NOT navigation)."""
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
SHOTS=QA/'screenshots'
SHOTS.mkdir(parents=True,exist_ok=True)
for old in SHOTS.glob('*.png'): old.unlink()
html=subprocess.run(['php',str(ROOT/'qa'/'fixture.php')],capture_output=True,text=True,check=True).stdout
checks=[]
def ok(name,condition):
    if not condition: raise AssertionError(name)
    checks.append(name)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    version=browser.version
    def setup(width=390,**kwargs):
        ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,**kwargs)
        page=ctx.new_page();page.set_content(html,wait_until='domcontentloaded');return page,ctx
    for width in (320,360,390,768,1024,1440,1920):
        page,ctx=setup(width)
        ok(f'{width}: two genuine R430 instances',page.locator('[data-fv-r430]').count()==2)
        ok(f'{width}: 6 sourced NASA stages',page.locator('.fv-r429__plate').count()==6)
        ok(f'{width}: 6 educator questions',page.locator('.fv-r430__question').count()==6)
        ok(f'{width}: single relevant CTA per instance',page.locator('.fv-r429__cta').count()==2)
        ok(f'{width}: no duplicate ids',page.evaluate('(()=>{const a=[...document.querySelectorAll("[id]")].map(e=>e.id);return new Set(a).size===a.length})()'))
        ok(f'{width}: no horizontal document overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
        ok(f'{width}: labelled answer fields',page.locator('.fv-r430__question textarea').count()==6 and page.locator('label[for]').count()==6)
        page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True);ctx.close()
    page,ctx=setup()
    page.locator('.fv-r430__reason summary').first.focus();page.keyboard.press('Enter')
    ok('keyboard instructor disclosure',page.locator('.fv-r430__reason').first.evaluate('(e)=>e.open'))
    page.locator('.fv-r430__question textarea').first.fill('The Board found no proven single ignition source.')
    ok('textarea permits local reflection',page.locator('.fv-r430__question textarea').first.input_value().startswith('The Board'))
    page.screenshot(path=str(SHOTS/'keyboard-and-answer.png'),full_page=True);ctx.close()
    page,ctx=setup(java_script_enabled=False)
    ok('no JavaScript shows substantive source and questions','The Board found the most probable initiator' in page.locator('.fv-r429').first.inner_text())
    page.locator('.fv-r430__reason summary').first.click()
    ok('native disclosures work with JavaScript disabled',page.locator('.fv-r430__reason').first.evaluate('(e)=>e.open'))
    page.screenshot(path=str(SHOTS/'no-js.png'),full_page=True);ctx.close()
    page,ctx=setup(has_touch=True,is_mobile=True)
    page.locator('.fv-r430__reason summary').first.tap()
    ok('touch instructor disclosure',page.locator('.fv-r430__reason').first.evaluate('(e)=>e.open'))
    page.screenshot(path=str(SHOTS/'touch.png'),full_page=True);ctx.close()
    page,ctx=setup(reduced_motion='reduce')
    ok('reduced-motion media query',page.evaluate('matchMedia("(prefers-reduced-motion:reduce)").matches'))
    page.screenshot(path=str(SHOTS/'reduced-motion.png'),full_page=True);ctx.close()
    page,ctx=setup(forced_colors='active')
    ok('forced-colors media query',page.evaluate('matchMedia("(forced-colors:active)").matches'))
    page.screenshot(path=str(SHOTS/'forced-colors.png'),full_page=True);ctx.close()
    page,ctx=setup(width=320);page.evaluate('document.documentElement.style.fontSize="32px"')
    ok('320px at 200pct root text no overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    page.screenshot(path=str(SHOTS/'320-200pct-text.png'),full_page=True);ctx.close()
    page,ctx=setup();page.emulate_media(media='print')
    ok('print hides instructor answer key',page.locator('.fv-r430__reason').first.evaluate('(e)=>getComputedStyle(e).display==="none"'))
    ok('print shows R429 evidence limits',page.locator('.fv-r429__printlimit').first.evaluate('(e)=>getComputedStyle(e).display!=="none"'))
    page.screenshot(path=str(SHOTS/'print.png'),full_page=True);ctx.close()
    browser.close()
result={'fixture':'Executed PHP R430 with exact-reviewed R429 dependencies, loaded via page.set_content','chromium':version,'assertions':len(checks),'checks':checks,'screenshots':sorted(p.name for p in SHOTS.glob('*.png')),'axe_core':'HOLD: reviewed local axe-core unavailable','navigated_lcp':'HOLD: no authorized staging navigation','navigated_cls':'HOLD: no authorized staging navigation','installed_wordpress':'HOLD: uninstalled','field_p75':'HOLD: no qualified real-user telemetry'}
(QA/'browser_results.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print('PASS',len(checks),'real Chromium assertions;',len(result['screenshots']),'screenshots; axe/staging CWV HOLD')
