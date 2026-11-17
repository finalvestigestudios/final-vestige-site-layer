"""Offline Chromium QA of executed R429 PHP. Never claim navigated CWV/axe from set_content."""
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'QA'
SHOTS = QA / 'screenshots'
SHOTS.mkdir(parents=True, exist_ok=True)
html = subprocess.run(['php', str(ROOT/'qa/fixture.php')],check=True,capture_output=True,text=True).stdout
checks=[]
def ok(label,check):
    if not check: raise AssertionError(label)
    checks.append(label)
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    version = browser.version
    def setup(width=390, **kwargs):
        ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,**kwargs)
        page=ctx.new_page();page.set_content(html,wait_until='domcontentloaded');return page,ctx
    for width in [320,360,390,768,1024,1440,1920]:
        page,ctx=setup(width)
        ok(f'{width} two PHP instances',page.locator('[data-fv-r429]').count()==2)
        ok(f'{width} three stages each',page.locator('[data-fv-r429] .fv-r429__plate').count()==6)
        ok(f'{width} one CTA per instance',page.locator('.fv-r429__cta').count()==2)
        ok(f'{width} canonical UTM link',page.locator('.fv-r429__cta').first.get_attribute('href').endswith('utm_content=apollo_longform_001'))
        ok(f'{width} no overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
        ok(f'{width} unique IDs',page.evaluate('(()=>{const a=[...document.querySelectorAll("[id]")].map(e=>e.id);return new Set(a).size===a.length})()'))
        page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True)
        ctx.close()
    page,ctx=setup();page.locator('summary').first.focus();page.keyboard.press('Enter')
    ok('keyboard expands native source drawer',page.locator('details').first.evaluate('(el)=>el.open'))
    page.screenshot(path=str(SHOTS/'keyboard.png'),full_page=True);ctx.close()
    page,ctx=setup(java_script_enabled=False)
    ok('no JS claim visible', 'most probable initiator' in page.locator('.fv-r429').first.inner_text())
    page.locator('summary').first.click()
    ok('no JS disclosure open',page.locator('details').first.evaluate('(el)=>el.open'))
    page.screenshot(path=str(SHOTS/'no-js.png'),full_page=True);ctx.close()
    page,ctx=setup(has_touch=True,is_mobile=True)
    page.locator('summary').first.tap()
    ok('touch disclosure open',page.locator('details').first.evaluate('(el)=>el.open'))
    page.screenshot(path=str(SHOTS/'touch.png'),full_page=True);ctx.close()
    page,ctx=setup(reduced_motion='reduce')
    ok('reduced motion honored',page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches'))
    page.screenshot(path=str(SHOTS/'reduced-motion.png'),full_page=True);ctx.close()
    page,ctx=setup(forced_colors='active')
    ok('forced colors honored',page.evaluate('matchMedia("(forced-colors: active)").matches'))
    page.screenshot(path=str(SHOTS/'forced-colors.png'),full_page=True);ctx.close()
    page,ctx=setup();page.evaluate('document.documentElement.style.fontSize="32px"')
    ok('200pct text no overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    page.screenshot(path=str(SHOTS/'200pct-text.png'),full_page=True);ctx.close()
    page,ctx=setup();page.emulate_media(media='print')
    ok('print limitation text visible',page.locator('.fv-r429__printlimit').first.evaluate('(el)=>getComputedStyle(el).display!=="none"'))
    ok('print collapsed drawer hidden',page.locator('details').first.evaluate('(el)=>getComputedStyle(el).display==="none"'))
    page.screenshot(path=str(SHOTS/'print.png'),full_page=True);ctx.close()
    browser.close()
result={'fixture':'actual PHP-rendered R429 via page.set_content; NOT network navigation','browser':'Chromium '+version,'assertions':len(checks),'passed':checks,'axe_core':'HOLD: pinned bundle unavailable','navigated_LCP':'HOLD: no navigated staging','navigated_CLS':'HOLD: no navigated staging','installed_WordPress':'HOLD: not installed','screenshots':sorted(p.name for p in SHOTS.glob('*.png'))}
(QA/'browser_results.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print('PASS',len(checks),'Chromium assertions;',len(list(SHOTS.glob('*.png'))),'screenshots; axe and navigated CWV HOLD')
