"""Real Chromium on exact PHP-generated fixture. No installed WordPress, no navigated CWV claims."""
import json,os,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA';(OUT/'screenshots').mkdir(parents=True,exist_ok=True)
results=[]
def fixture(mode='staging'):
 return subprocess.run(['php',str(ROOT/'qa/render_fixture.php')],env=dict(os.environ,FV_R420_MODE=mode),capture_output=True,text=True,check=True).stdout
def check(name,condition,**extra):
 results.append({'scenario':name,'status':'PASS' if condition else 'FAIL',**extra})
 if not condition:raise AssertionError(f'{name} failed: {extra}')
def geo(page):
 return page.evaluate('''() => ({doc:document.documentElement.scrollWidth,viewport:document.documentElement.clientWidth,cards:document.querySelectorAll('.fv-r420__card').length,details:document.querySelectorAll('details').length,ctas:document.querySelectorAll('.fv-r420__next').length})''')
def run():
 html=fixture()
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for w in (320,360,390,768,1024,1440,1920):
   page=browser.new_page(viewport={'width':w,'height':850},device_scale_factor=1)
   page.set_content(html,wait_until='load')
   g=geo(page)
   check(f'layout-{w}',g['doc']<=g['viewport'] and g['cards']==3 and g['details']==3 and g['ctas']==1,**g)
   page.screenshot(path=str(OUT/'screenshots'/f'{w}.png'),full_page=True)
   page.close()
  page=browser.new_page(viewport={'width':390,'height':800},java_script_enabled=False)
  page.set_content(html)
  page.locator('details > summary').first.click()
  check('no-js-native-details',page.locator('details').first.evaluate('(n)=>n.open'))
  page.screenshot(path=str(OUT/'screenshots/390-nojs.png'),full_page=True)
  page.close()
  page=browser.new_page(viewport={'width':390,'height':800})
  page.set_content(html)
  page.locator('details > summary').first.focus()
  page.keyboard.press('Enter')
  check('keyboard-enter-open',page.locator('details').first.evaluate('(n)=>n.open'))
  page.keyboard.press('Enter')
  check('keyboard-enter-close',not page.locator('details').first.evaluate('(n)=>n.open'))
  page.locator('nav.fv-r420__map a').last.click()
  check('anchor-nav',page.evaluate('location.hash')=='#fv-r420-1-case-03')
  page.screenshot(path=str(OUT/'screenshots/390-keyboard.png'),full_page=True)
  page.close()
  page=browser.new_page(viewport={'width':390,'height':800},has_touch=True,is_mobile=True)
  page.set_content(html)
  page.locator('details > summary').first.tap()
  check('touch-native-details',page.locator('details').first.evaluate('(n)=>n.open'))
  page.screenshot(path=str(OUT/'screenshots/390-touch.png'),full_page=True)
  page.close()
  page=browser.new_page(viewport={'width':320,'height':850},forced_colors='active',reduced_motion='reduce')
  page.set_content(html)
  page.evaluate('document.documentElement.style.fontSize="400%"')
  g=geo(page)
  check('320-400pct-forcedcolors-reducedmotion',g['doc']<=g['viewport'],**g)
  page.screenshot(path=str(OUT/'screenshots/320-400pct.png'),full_page=True)
  page.close()
  page=browser.new_page(viewport={'width':1440,'height':950})
  page.set_content(html)
  page.emulate_media(media='print')
  check('print-readable-cards',page.locator('.fv-r420__card').count()==3 and page.locator('.fv-r420__next').evaluate('(n)=>getComputedStyle(n).display')=='none')
  page.screenshot(path=str(OUT/'screenshots/1440-print.png'),full_page=True)
  page.close()
  page=browser.new_page(viewport={'width':768,'height':900})
  page.set_content(html)
  cdp=page.context.new_cdp_session(page);tree=cdp.send('Accessibility.getFullAXTree')['nodes']
  names=[x.get('name',{}).get('value','') for x in tree]
  check('chromium-accessibility-tree',any('Could the evidence' in x for x in names) and any('Reveal instructor' in x for x in names),ax_nodes=len(tree))
  (OUT/'chrome_accessibility_extract.json').write_text(json.dumps({'ax_nodes':len(tree),'selected_names':[n for n in names if 'NASA' in n or 'source' in n.lower() or 'instructor' in n][:35]},indent=2)+'\n')
  page.close()
  browser.close()
 missing={'actual_wordpress':'NOT TESTED','axe_core':'NOT INSTALLED','navigated_http_lcp':'NOT MEASURED','navigated_http_cls':'NOT MEASURED','independent_screen_reader':'NOT TESTED','p75_field_cwv':'NOT MEASURED'}
 (OUT/'browser_results.json').write_text(json.dumps({'fixture':'PHP-generated markup inserted via page.set_content; not a navigated website','scenarios':results,'release_blockers':missing},indent=2,sort_keys=True)+'\n')
 print(f'R420 Chromium fixture: {len(results)}/{len(results)} scenarios PASS. Actual WordPress/axe/navigated CWV HOLD.')
if __name__=='__main__':run()
