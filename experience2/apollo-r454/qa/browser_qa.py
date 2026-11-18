#!/usr/bin/env python3
"""Offline set_content Chromium acceptance. Does NOT represent navigated staging or field web vitals."""
from pathlib import Path
import subprocess, json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'QA';EVIDENCE.mkdir(exist_ok=True)
SHOTS=EVIDENCE/'screenshots';SHOTS.mkdir(exist_ok=True)
html=subprocess.run(['php','-r',f'require {json.dumps(str(ROOT/"apollo_evidence_lab.php"))};echo fv454_render();'],check=True,capture_output=True,text=True).stdout
results=[]
def check(label, fn):
 try:fn();results.append({'case':label,'status':'PASS'})
 except Exception as e:results.append({'case':label,'status':'FAIL','error':str(e)[:450]})
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for js in (True,False):
  for width in (320,360,390,768,1024,1440,1920):
   ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce')
   page=ctx.new_page()
   def one():
    page.set_content(html,wait_until='load')
    assert page.locator('.fv454__plate').count()==4
    assert page.locator('.fv454__cta a').count()==1
    assert page.locator('.fv454__drawer').count()==4
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),f'Overflow width {width}'
    if js:
     assert page.locator('.fv454--enhanced').count()==1
     page.get_by_role('button',name='Later interpretation').click()
     assert page.locator('.fv454__plate:visible').count()==2
     assert page.get_by_role('button',name='Later interpretation').get_attribute('aria-pressed')=='true'
     page.get_by_role('button',name='All four records').click()
     assert page.locator('.fv454__plate:visible').count()==4
    else:
     assert page.locator('.fv454__plate:visible').count()==4
    page.screenshot(path=str(SHOTS/f'{width}-js-{int(js)}.png'),full_page=True)
   check(f'chromium-{width}-js-{int(js)}',one)
   ctx.close()
 ctx=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
 page=ctx.new_page()
 def touch():
  page.set_content(html);page.get_by_role('button',name='1966–67 evidence').tap();assert page.locator('.fv454__plate:visible').count()==2
  page.locator('.fv454__plate:visible').first.locator('summary').tap();assert page.locator('details[open]').count()==1
 check('touch-390',touch);ctx.close()
 ctx=browser.new_context(viewport={'width':390,'height':844})
 page=ctx.new_page()
 def keyboard():
  page.set_content(html);btn=page.get_by_role('button',name='Later interpretation');btn.focus();page.keyboard.press('Enter');assert btn.get_attribute('aria-pressed')=='true';assert page.locator('.fv454__plate:visible').count()==2
  source=page.locator('.fv454__plate:visible').first.locator('summary');source.focus();page.keyboard.press('Enter');assert page.locator('details[open]').count()==1
 check('keyboard-390',keyboard)
 def forced():
  page.emulate_media(forced_colors='active',reduced_motion='reduce');assert page.locator('.fv454__plate').count()==4
  page.screenshot(path=str(SHOTS/'390-forced-colors.png'),full_page=True)
 check('forced-colors',forced)
 def print_case():
  page.emulate_media(media='print');assert page.locator('.fv454__plate:visible').count()==4
  page.screenshot(path=str(SHOTS/'390-print.png'),full_page=True)
 check('print-shows-all',print_case)
 ctx.close();browser.close()
report={'browser':'Chromium local page.set_content offline','navigated_staging':'NOT_RUN','axe_core':'NOT_RUN','lab_LCP_CLS':'NOT_MEASURED_NO_NAVIGATION','p75_CWV':'NOT_RUN','results':results,'pass':sum(x['status']=='PASS' for x in results),'fail':sum(x['status']=='FAIL' for x in results)}
(EVIDENCE/'BROWSER.json').write_text(json.dumps(report,indent=2)+'\n')
print('Browser',report['pass'],'PASS',report['fail'],'FAIL');raise SystemExit(bool(report['fail']))
