#!/usr/bin/env python3
"""Real Chromium/Playwright set_content QA. Does NOT claim navigated staging, axe or field CWV."""
import json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent.parent;OUT=R/'QA';SC=OUT/'screenshots';SC.mkdir(parents=True,exist_ok=True)
HTML=subprocess.check_output(['php','-r',f'require {json.dumps(str(R/"apollo_claim_review.php"))};echo fv456_render();'],text=True)
CASES=[]
def run(name,fn):
    try:fn();CASES.append({'name':name,'status':'PASS'})
    except Exception as e:CASES.append({'name':name,'status':'FAIL','error':str(e)[:400]})
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    def page_in(ctx):
        page=ctx.new_page();page.set_content(HTML,wait_until='load')
        assert page.locator('.fv456__case').count()==3
        assert page.locator('.fv456__next a').count()==1
        assert page.locator('a[href^="https://www.nasa.gov/"]').count()==3
        assert page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth+1')
        return page
    for width in [320,360,390,768,1024,1440,1920]:
        for js in [False,True]:
            def viewport(width=width,js=js):
                ctx=browser.new_context(viewport={'width':width,'height':850},java_script_enabled=js)
                page=page_in(ctx)
                assert page.locator('.fv456__case:visible').count()==3
                if js:
                    page.locator('[data-fv456-select="spark"]').click()
                    assert page.locator('.fv456__case:visible').count()==1
                    page.locator('[data-fv456-select="all"]').click()
                    assert page.locator('.fv456__case:visible').count()==3
                else:
                    assert page.locator('[data-fv456-controls]:visible').count()==0
                    page.locator('summary').first.click()
                    assert page.locator('details').first.evaluate('(e)=>e.open')
                page.screenshot(path=str(SC/(f"{width}-{'js' if js else 'nojs'}.png")),full_page=True,animations='disabled')
                ctx.close()
            run(f'{width}-'+('js' if js else 'nojs'),viewport)
    def keyboard():
        ctx=browser.new_context(viewport={'width':390,'height':850});page=page_in(ctx)
        b=page.locator('[data-fv456-select="tests"]');b.focus();page.keyboard.press('Enter')
        assert b.get_attribute('aria-pressed')=='true';assert page.locator('.fv456__case:visible').count()==1
        summ=page.locator('.fv456__case:visible summary');summ.focus();page.keyboard.press('Enter')
        assert page.locator('.fv456__case:visible details').evaluate('(e)=>e.open')
        page.screenshot(path=str(SC/'keyboard.png'),full_page=True);ctx.close()
    run('keyboard',keyboard)
    def touch():
        ctx=browser.new_context(viewport={'width':390,'height':850},has_touch=True,is_mobile=True)
        page=page_in(ctx);page.locator('[data-fv456-select="memorial"]').tap()
        assert page.locator('.fv456__case:visible').count()==1
        page.locator('.fv456__case:visible summary').tap()
        assert page.locator('.fv456__case:visible details').evaluate('(e)=>e.open')
        page.screenshot(path=str(SC/'touch.png'),full_page=True);ctx.close()
    run('touch',touch)
    def forced():
        ctx=browser.new_context(viewport={'width':390,'height':850},forced_colors='active');p=page_in(ctx)
        p.screenshot(path=str(SC/'forced-colors.png'),full_page=True);ctx.close()
    run('forced-colors',forced)
    def reduce():
        ctx=browser.new_context(viewport={'width':390,'height':850},reduced_motion='reduce');p=page_in(ctx)
        assert p.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches')
        p.screenshot(path=str(SC/'reduced-motion.png'),full_page=True);ctx.close()
    run('reduced-motion',reduce)
    def print_media():
        ctx=browser.new_context(viewport={'width':768,'height':960});p=page_in(ctx);p.emulate_media(media='print')
        assert p.locator('.fv456__case:visible').count()==3
        p.screenshot(path=str(SC/'print.png'),full_page=True);ctx.close()
    run('print',print_media)
    def multi():
        h=subprocess.check_output(['php','-r',f'require {json.dumps(str(R/"apollo_claim_review.php"))};echo fv456_render(),fv456_render();'],text=True)
        ctx=browser.new_context(viewport={'width':1024,'height':900});p=ctx.new_page();p.set_content(h)
        roots=p.locator('[data-fv456-root]');assert roots.count()==2
        roots.nth(0).locator('[data-fv456-select="tests"]').click()
        assert roots.nth(0).locator('.fv456__case:visible').count()==1
        assert roots.nth(1).locator('.fv456__case:visible').count()==3
        ctx.close()
    run('multi-instance',multi)
    def zoom():
        ctx=browser.new_context(viewport={'width':390,'height':850});p=page_in(ctx)
        p.evaluate("document.body.style.zoom='200%'")
        assert p.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth+1')
        p.screenshot(path=str(SC/'zoom-200.png'),full_page=True);ctx.close()
    run('200-percent-zoom',zoom)
    browser.close()
result={'sprint':'R456','render':'PHP rendered HTML / Chromium page.set_content, no hosted navigation','passed':sum(x['status']=='PASS' for x in CASES),'failed':sum(x['status']=='FAIL' for x in CASES),'cases':CASES,'axes':'HOLD_NOT_RUN','axe_core':'HOLD_NOT_RUN','navigated_LCP':'HOLD_NOT_RUN','navigated_CLS':'HOLD_NOT_RUN','hosted_WordPress':'HOLD_NOT_RUN','field_CWV':'HOLD_NOT_RUN'}
(OUT/'BROWSER_RESULTS.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print('Browser cases:',result['passed'],'passed',result['failed'],'failed')
for x in CASES:
 if x['status']=='FAIL':print(x)
if result['failed']:raise SystemExit(1)
