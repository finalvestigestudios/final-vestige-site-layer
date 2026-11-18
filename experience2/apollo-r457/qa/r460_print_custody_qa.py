#!/usr/bin/env python3
"""R460 browser regression: print a COMPLETE NASA source list after an on-screen filter.

Offline rendered PHP is not WordPress staging navigation or legitimate LCP/CLS data.
"""
from pathlib import Path
import json, os, subprocess, hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'/'r460'; QA.mkdir(parents=True,exist_ok=True)
html=subprocess.check_output(['php','-r',f'require {json.dumps(str(ROOT / "apollo_rights_gallery.php"))};echo fv457_render();'],text=True)
passed=[];failed=[]
def run(label,check):
 try: check();passed.append(label)
 except Exception as e:failed.append({'name':label,'error':str(e)[:750]})
with sync_playwright() as playwright:
 browser=playwright.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'), args=['--no-sandbox'])
 for width in [320,360,390,768,1024,1440,1920]:
  for js in [False,True]:
   context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js)
   page=context.new_page();page.set_content(html, wait_until='load')
   def baseline():
    assert page.locator('[data-fv457-card]').count()==6
    assert page.locator('[data-fv457-card]:visible').count()==6
    assert page.locator('.fv457__print-custody:visible').count()==0
    assert page.locator('.fv457__print-note:visible').count()==0
    assert page.locator('a[href*="the-hatch-opened-inward"]').count()==1
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),f'overflow {width}'
   run(f'{width}-js{int(js)}-screen-full', baseline)
   if js:
    page.get_by_role('button',name='Confirmed homepage (1)').click()
    run(f'{width}-js1-filter-has-one',lambda: (page.locator('[data-fv457-card]:visible').count()==1) or (_ for _ in ()).throw(AssertionError('filter not applied')))
   page.emulate_media(media='print')
   def printed():
    assert page.locator('[data-fv457-card]:visible').count()==6,'filtered records missing from print'
    assert page.locator('.fv457__print-custody:visible').count()==6,'print source reference missing'
    assert page.locator('.fv457__print-note:visible').count()==1
    assert page.locator('.fv457__card details').count()==6, 'all six archive custody drawers retained'
    assert page.locator('.fv457__source-hold').is_visible()
    assert not page.locator('[data-fv457-controls]').is_visible()
    assert page.locator('.fv457__print-custody').first.evaluate('(e)=>getComputedStyle(e).color')=='rgb(0, 0, 0)'
    assert page.locator('.fv457__print-custody').first.evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(255, 255, 255)'
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+2'),f'print overflow {width}'
   run(f'{width}-js{int(js)}-all-six-print',printed)
   if width in (320,390,768,1440,1920) and js:
    page.screenshot(path=str(QA/f'{width}-print-after-filter.png'),full_page=True,animations='disabled')
   page.emulate_media(media='screen')
   if js:
    run(f'{width}-js1-screen-filter-restored',lambda: (page.locator('[data-fv457-card]:visible').count()==1) or (_ for _ in ()).throw(AssertionError('screen filter lost after print')))
   context.close()
 for label,kwargs in [('reduced-motion',{'reduced_motion':'reduce'}),('forced-colors',{'forced_colors':'active'}),('touch',{'is_mobile':True,'has_touch':True})]:
  context=browser.new_context(viewport={'width':390,'height':844},**kwargs);page=context.new_page();page.set_content(html)
  if label=='touch':page.get_by_role('button',name='Not in Atlas (3)').tap()
  else:page.get_by_role('button',name='Not in Atlas (3)').click()
  page.emulate_media(media='print')
  run(label+'-print-all-six',lambda: (page.locator('[data-fv457-card]:visible').count()==6 and page.locator('.fv457__print-custody:visible').count()==6) or (_ for _ in ()).throw(AssertionError('not complete')))
  context.close()
 browser.close()
report={'sprint':'R460','execution':'real Chromium and PHP-generated HTML via Playwright set_content (NOT navigated WordPress)','passed':len(passed),'failed':failed,'pass_cases':passed,'screenshots':sorted(p.name for p in QA.glob('*.png')),'axe_core':'HOLD_NOT_RUN','navigated_LCP_CLS':'HOLD_NOT_RUN','real_staging':'HOLD_NOT_RUN','manual_screen_reader':'HOLD_NOT_RUN','field_CWV':'HOLD_NOT_RUN','exact_head_CI':'NOT_CHECKED_BY_THIS_RUN'}
(QA/'REPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'passed':len(passed),'failed':failed,'screenshots':report['screenshots']},indent=2))
if failed:raise SystemExit(1)
