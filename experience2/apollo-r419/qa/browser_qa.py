"""Chromium-on-PHP fixture QA. Real navigated site/axe/p75 are separately gated."""
import json,os,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA';(OUT/'screenshots').mkdir(parents=True,exist_ok=True)
RESULT=[]
def fixture(mode='staging'):
    return subprocess.run(['php',str(ROOT/'qa/render_fixture.php')],env=dict(os.environ,FV_R419_MODE=mode),text=True,capture_output=True,check=True).stdout
def log(name, passed, **details):
    RESULT.append(dict(scenario=name,status='PASS' if passed else 'FAIL',**details))
    if not passed:raise AssertionError(f'{name} {details}')
def geometry(page):
    return page.evaluate('''() => ({doc: document.documentElement.scrollWidth, viewport: document.documentElement.clientWidth, sections:document.querySelectorAll('[data-fv-r419-concordance]').length, cards:document.querySelectorAll('.fv-r419__card').length, stages:document.querySelectorAll('.fv-r419__rail > li').length, ctas:document.querySelectorAll('.fv-r419__next').length})''')
def run():
    html=fixture()
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        for w in (320,360,390,768,1024,1440,1920):
            page=browser.new_page(viewport={'width':w,'height':950},device_scale_factor=1)
            page.set_content(html,wait_until='load')
            g=geometry(page)
            log(f'layout-{w}',g['doc']<=g['viewport'] and g['cards']==6 and g['stages']==3 and g['ctas']==1,**g)
            page.screenshot(path=str(OUT/f'screenshots/{w}.png'),full_page=True)
            page.close()
        page=browser.new_page(viewport={'width':390,'height':850},java_script_enabled=False)
        page.set_content(html)
        disclosure=page.locator('.fv-r419__card details').first
        disclosure.locator('summary').click()
        log('no-js-native-disclosure',disclosure.evaluate('(e)=>e.open'))
        page.screenshot(path=str(OUT/'screenshots/390-nojs.png'),full_page=True)
        page.close()
        page=browser.new_page(viewport={'width':390,'height':850})
        page.set_content(html)
        page.locator('.fv-r419__card summary').first.focus()
        page.keyboard.press('Enter')
        log('keyboard-enter-native-details',page.locator('.fv-r419__card details').first.evaluate('(e)=>e.open'))
        page.keyboard.press('Enter')
        log('keyboard-second-enter-closes',not page.locator('.fv-r419__card details').first.evaluate('(e)=>e.open'))
        page.locator('.fv-r419__nav a').first.click()
        log('fragment-nav-matches-real-target',page.evaluate('location.hash')=='#fv-r419-1-chronology')
        page.screenshot(path=str(OUT/'screenshots/390-keyboard.png'),full_page=True)
        page.close()
        page=browser.new_page(viewport={'width':390,'height':850},has_touch=True,is_mobile=True)
        page.set_content(html)
        page.locator('.fv-r419__card summary').first.tap()
        log('touch-disclosure',page.locator('.fv-r419__card details').first.evaluate('(e)=>e.open'))
        page.screenshot(path=str(OUT/'screenshots/390-touch.png'),full_page=True)
        page.close()
        page=browser.new_page(viewport={'width':320,'height':800},reduced_motion='reduce',forced_colors='active')
        page.set_content(html)
        page.evaluate('document.documentElement.style.fontSize="400%"')
        g=geometry(page)
        log('320-400pct-forcedcolors-reducedmotion',g['doc']<=g['viewport'],**g)
        page.screenshot(path=str(OUT/'screenshots/320-400pct-forcedcolors.png'),full_page=True)
        page.close()
        page=browser.new_page(viewport={'width':1440,'height':900})
        page.set_content(html)
        page.emulate_media(media='print')
        page.screenshot(path=str(OUT/'screenshots/1440-print.png'),full_page=True)
        log('print-removes-nav',page.locator('.fv-r419__nav').evaluate('(e)=>getComputedStyle(e).display')=='none')
        page.close()
        # A real browser accessibility tree, not an axe-core result.
        page=browser.new_page(viewport={'width':768,'height':1000})
        page.set_content(html)
        session=page.context.new_cdp_session(page)
        tree=session.send('Accessibility.getFullAXTree')['nodes']
        meaningful=[n.get('name',{}).get('value','') for n in tree]
        log('chrome-ax-tree',any('Six sources' in a for a in meaningful) and any('Read the NASA textual publication' in a for a in meaningful),ax_nodes=len(tree))
        (OUT/'chrome_accessibility_extract.json').write_text(json.dumps({'node_count':len(tree),'selected_names':[n for n in meaningful if 'NASA' in n or 'source' in n.lower()][:25]},indent=2))
        page.close()
        browser.close()
    # Missing instruments are NOT a pass. Always report absent signals independently.
    blockers={'installed_wordpress_staging':'NOT TESTED','axe_core':'NOT AVAILABLE','navigation_lcp':'NOT MEASURED',
              'navigation_cls':'NOT MEASURED','independent_screen_reader':'NOT TESTED','p75_real_users':'NOT MEASURED'}
    (OUT/'browser_results.json').write_text(json.dumps({'schema':1,'fixture':'offline PHP-generated HTML via page.set_content; not live WordPress',
              'scenarios':RESULT,'release_blockers':blockers},sort_keys=True,indent=2)+'\n')
    print(f'Chromium scenarios: {sum(r["status"]=="PASS" for r in RESULT)}/{len(RESULT)} PASS; staging/axe/navigated CWV HOLD')
if __name__=='__main__':run()
