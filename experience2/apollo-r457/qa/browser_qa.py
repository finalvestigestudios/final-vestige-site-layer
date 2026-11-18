#!/usr/bin/env python3
"""Local Chromium DOM interaction QA; page.set_content is NOT hosted navigation or LCP evidence."""
import json,subprocess,os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA';SHOTS=QA/'screenshots';SHOTS.mkdir(exist_ok=True,parents=True)
html=subprocess.check_output(['php','-r',f'require "{ROOT}/apollo_rights_gallery.php"; echo fv457_render();'],text=True)
fail=[];passes=[]
def case(name,fn):
 print("CASE",name,flush=True)
 try:fn();passes.append(name)
 except Exception as e:fail.append({'name':name,'error':str(e)[:300]})
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
 for width in [320,360,390,768,1024,1440,1920]:
  for js in [False,True]:
   context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js)
   page=context.new_page();page.set_default_timeout(2500);page.set_content(html,wait_until='load')
   def check(w=width,j=js,pg=page):
    assert pg.locator('[data-fv457-card]').count()==6
    assert pg.locator('a[href*="the-hatch-opened-inward"]').count()==1
    assert pg.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'),f'overflow {w}'
    assert pg.locator('[data-fv457-controls]').is_visible()==j
    if w in [390,1440]:pg.screenshot(path=str(SHOTS/f'{w}-{ "js" if j else "nojs"}.png'),full_page=True,animations='disabled',timeout=8000)
   case(f'{width}-{ "js" if js else "nojs"}',check)
   if width==390 and js:
    def filter_check():
     page.get_by_role('button',name='Atlas chronology (3)').click()
     assert page.locator('[data-fv457-card]:visible').count()==3
     assert page.get_by_role('button',name='Atlas chronology (3)').get_attribute('aria-pressed')=='true'
     page.get_by_role('button',name='Not in Atlas (3)').click()
     assert page.locator('[data-fv457-card]:visible').count()==3
     page.get_by_role('button',name='Confirmed homepage (1)').click()
     assert page.locator('[data-fv457-card]:visible').count()==1
     assert page.locator('[data-fv457-card]:visible h3').inner_text()=='S67-19766'
     page.get_by_role('button',name='All six').click()
     assert page.locator('[data-fv457-card]:visible').count()==6
    case('filter-and-aria',filter_check)
    def keyboard_check():
     btn=page.get_by_role('button',name='Not in Atlas (3)');btn.focus();page.keyboard.press('Enter');assert btn.get_attribute('aria-pressed')=='true'
    case('keyboard-enter',keyboard_check)
    def details_check():
     page.get_by_role('button',name='All six').click();item=page.locator('details').first;item.locator('summary').click();assert item.get_attribute('open') is not None
    case('native-source-details',details_check)
    case('no-embedded-media',lambda: (page.locator('img,iframe,video').count()==0 or (_ for _ in ()).throw(AssertionError('embedded media'))))
   context.close()
 context=browser.new_context(has_touch=True,is_mobile=True,viewport={'width':390,'height':844},device_scale_factor=1)
 page=context.new_page();page.set_default_timeout(2500);page.set_content(html);case('touch-tap',lambda:(page.get_by_role('button',name='Not in Atlas (3)').tap(),page.locator('[data-fv457-card]:visible').count()==3 or (_ for _ in ()).throw(Exception('touch failed'))));context.close()
 context=browser.new_context(reduced_motion='reduce',viewport={'width':390,'height':800});page=context.new_page();page.set_content(html);case('reduced-motion',lambda:page.locator('[data-fv457-card]').count()==6 or (_ for _ in ()).throw(Exception('missing records')));context.close()
 context=browser.new_context(forced_colors='active',viewport={'width':390,'height':800});page=context.new_page();page.set_content(html);case('forced-colors',lambda:page.locator('[data-fv457-card]').count()==6 or (_ for _ in ()).throw(Exception('missing records')));context.close()
 browser.close()
report={'sprint':'R458','render':'PHP generated HTML / Chromium page.set_content; no hosted navigation','local_cases_passed':len(passes),'local_cases_failed':len(fail),'passed_names':passes,'failures':fail,'hosted_WordPress':'HOLD_NOT_RUN','navigated_LCP':'HOLD_NOT_RUN','navigated_CLS':'HOLD_NOT_RUN','axe_core':'HOLD_NOT_RUN','manual_screen_reader':'HOLD_NOT_RUN','field_CWV':'HOLD_NOT_RUN'}
(QA/'BROWSER_RESULTS.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'passed':len(passes),'failed':fail},indent=2))
if fail:raise SystemExit(1)
