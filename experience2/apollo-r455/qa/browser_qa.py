#!/usr/bin/env python3
"""Offline real Chromium interaction QA; honest explicit holds for navigated staging, axe, LCP and CLS."""
import json
from pathlib import Path
import subprocess
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent
SCREEN=ROOT/'QA'/'screenshots'
SCREEN.mkdir(parents=True,exist_ok=True)
PHP=ROOT/'apollo_crosswalk.php'
HTML=subprocess.check_output(['php','-r',f"require '{PHP}';echo fv455_render();"],text=True)
WIDTHS=[320,360,390,768,1024,1440,1920]
CASES=[]

def result(name,fn):
    try:fn();CASES.append({'case':name,'status':'PASS'})
    except Exception as e:
        CASES.append({'case':name,'status':'FAIL','error':str(e)[:400]})

def base_check(page, js, width):
    assert page.locator('.fv455__plate').count()==4
    assert page.locator('.fv455__plate:visible').count()==4
    assert page.locator('.fv455__cta a').count()==1
    assert page.locator('a[href^="https://www.nasa.gov/"]').count()==4
    assert page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1'),f'overflow at {width} JS={js}'
    if js: assert page.locator('.fv455__tools button:visible').count()==4
    else: assert page.locator('.fv455__tools button:visible').count()==0

def screenshot(page,name):page.screenshot(path=str(SCREEN/name),full_page=True,animations='disabled')

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in WIDTHS:
        for js in [False,True]:
            name=f'{width}-'+('js' if js else 'nojs')
            def check(width=width,js=js,name=name):
                ctx=browser.new_context(viewport={'width':width,'height':870},java_script_enabled=js,device_scale_factor=1,locale='en-US')
                page=ctx.new_page();page.set_content(HTML,wait_until='load')
                base_check(page,js,width)
                if js:
                    page.locator('[data-fv455-filter="investigation"]').click()
                    assert page.locator('.fv455__plate:visible').count()==1
                    page.locator('[data-fv455-filter="all"]').click()
                    assert page.locator('.fv455__plate:visible').count()==4
                else:
                    page.locator('.fv455__plate details summary').first.click()
                    assert page.locator('.fv455__plate details').first.evaluate('(d)=>d.open')
                screenshot(page,name+'.png');ctx.close()
            result(name,check)
    def keyboard():
        ctx=browser.new_context(viewport={'width':390,'height':870});page=ctx.new_page();page.set_content(HTML)
        button=page.locator('[data-fv455-filter="later"]');button.focus();page.keyboard.press('Enter')
        assert page.locator('.fv455__plate:visible').count()==2
        assert button.get_attribute('aria-pressed')=='true'
        page.locator('.fv455__plate:visible summary').first.focus();page.keyboard.press('Enter')
        assert page.locator('.fv455__plate:visible details').first.evaluate('(d)=>d.open')
        screenshot(page,'keyboard-later.png');ctx.close()
    result('keyboard',keyboard)
    def touch():
        ctx=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
        page=ctx.new_page();page.set_content(HTML)
        page.locator('[data-fv455-filter="context"]').tap()
        assert page.locator('.fv455__plate:visible').count()==1
        page.locator('.fv455__plate:visible summary').tap()
        assert page.locator('.fv455__plate:visible details').first.evaluate('(d)=>d.open')
        screenshot(page,'touch-context.png');ctx.close()
    result('touch',touch)
    def forced_colors():
        ctx=browser.new_context(viewport={'width':390,'height':870},forced_colors='active')
        page=ctx.new_page();page.set_content(HTML);base_check(page,True,390)
        screenshot(page,'forced-colors.png');ctx.close()
    result('forced-colors',forced_colors)
    def reduced_motion():
        ctx=browser.new_context(viewport={'width':390,'height':870},reduced_motion='reduce')
        page=ctx.new_page();page.set_content(HTML);base_check(page,True,390)
        assert page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches')
        screenshot(page,'reduced-motion.png');ctx.close()
    result('reduced-motion',reduced_motion)
    def print_view():
        ctx=browser.new_context(viewport={'width':768,'height':1024})
        page=ctx.new_page();page.set_content(HTML);page.emulate_media(media='print')
        assert page.locator('.fv455__plate').count()==4
        assert page.locator('.fv455__tools button:visible').count()==0
        assert page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1')
        screenshot(page,'print.png');ctx.close()
    result('print',print_view)
    def zoom200():
        ctx=browser.new_context(viewport={'width':390,'height':870})
        page=ctx.new_page();page.set_content(HTML)
        page.evaluate("document.body.style.zoom='200%'")
        assert page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1'),'overflow at 200%'
        screenshot(page,'zoom-200.png');ctx.close()
    result('zoom-200',zoom200)
    def download():
        ctx=browser.new_context(viewport={'width':1024,'height':768},accept_downloads=True)
        page=ctx.new_page();page.set_content(HTML)
        with page.expect_download() as item: page.locator('[data-fv455-export]').click()
        d=item.value
        assert d.suggested_filename=='fv-apollo-evidence-study.txt'
        b=Path(d.path()).read_bytes().decode('utf-8')
        assert 'NASA' in b and 'does not establish' in b and 'https://www.nasa.gov/' in b
        assert b.count('Source: https://www.nasa.gov/')==4
        ctx.close()
    result('local-text-download',download)
    def independent_instances():
        text=subprocess.check_output(['php','-r',f"require '{PHP}';echo fv455_render();echo fv455_render();"],text=True)
        ctx=browser.new_context(viewport={'width':1024,'height':768});page=ctx.new_page();page.set_content(text)
        roots=page.locator('.fv455');assert roots.count()==2
        roots.nth(0).locator('[data-fv455-filter="investigation"]').click()
        assert roots.nth(0).locator('.fv455__plate:visible').count()==1
        assert roots.nth(1).locator('.fv455__plate:visible').count()==4
        ctx.close()
    result('independent-instance',independent_instances)
    def no_js_source_depth():
        ctx=browser.new_context(viewport={'width':320,'height':720},java_script_enabled=False)
        page=ctx.new_page();page.set_content(HTML)
        for i in range(4):
            details=page.locator('.fv455__plate details').nth(i)
            details.locator('summary').click()
            assert details.evaluate('(d)=>d.open')
            assert details.locator('a').count()==1
        assert page.locator('.fv455__plate:visible').count()==4
        ctx.close()
    result('nojs-source-depth',no_js_source_depth)
    browser.close()

# Browser navigation access checked separately by the approved hosted runner, NOT synthetic set_content.
summary={'component':'apollo-r455','engine':'Chromium / Playwright real browser with PHP-rendered page.set_content()','cases':CASES,'passed':sum(c['status']=='PASS' for c in CASES),'failed':sum(c['status']=='FAIL' for c in CASES),'navigation':'HOLD_NOT_RUN','axe_core':'HOLD_NOT_RUN','lcp':'HOLD_NOT_RUN','cls':'HOLD_NOT_RUN','independent_screen_reader':'HOLD_NOT_RUN','production':'NOT_INSTALLED'}
(ROOT/'QA'/'BROWSER_RESULTS.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
print('BROWSER_QA',summary['passed'],'PASS',summary['failed'],'FAIL')
for c in CASES:
 if c['status']!='PASS':print(c)
if summary['failed']:raise SystemExit(1)
