"""Actual offline Chromium QA: no false claim of installed WordPress, axe or field CWV."""
from pathlib import Path
import subprocess,json
from playwright.sync_api import sync_playwright
here=Path(__file__).resolve().parents[1]
QA=here/'QA';shots=QA/'screenshots';shots.mkdir(parents=True,exist_ok=True)
html=subprocess.check_output(['php',str(here/'qa/fixture.php')]).decode()
(QA/'fixture.html').write_text(html)
checks=0
def ok(cond,detail):
 global checks
 assert cond,detail
 checks+=1
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in (320,360,390,768,1024,1440,1920):
  page=browser.new_page(viewport={'width':width,'height':880},device_scale_factor=1)
  page.set_content(html,wait_until='load')
  ok(page.locator('[data-fv-r436]').count()==2,str(width)+' wrapper')
  ok(page.locator('.fv-r429__cta').count()==2,str(width)+' original CTA')
  ok(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),str(width)+' horizontal overflow')
  ok(page.locator('img').count()==0,str(width)+' no NASA media copied')
  proof=page.locator('[data-fv-r436-proof]').first
  ok(not proof.evaluate('(e)=>e.open'),str(width)+' disclosure initially closed')
  proof.locator('summary').click()
  ok(proof.evaluate('(e)=>e.open'),str(width)+' native disclosure works')
  ok(proof.locator('article').count()==3,str(width)+' three sourced records')
  ok(proof.locator('a').count()==3,str(width)+' three primary / institutional destinations')
  ok('catalogue ID not confirmed' in page.locator('[data-fv-r436]').first.text_content(),str(width)+' uncertain ID removed')
  page.screenshot(path=str(shots/f'{width}.png'),full_page=True)
  page.close()
 page=browser.new_page(viewport={'width':390,'height':880})
 page.set_content(html)
 summary=page.locator('[data-fv-r436-proof] summary').first
 summary.focus();page.keyboard.press('Enter')
 ok(page.locator('[data-fv-r436-proof]').first.evaluate('(e)=>e.open'),'Enter opens details')
 page.keyboard.press('Enter')
 ok(not page.locator('[data-fv-r436-proof]').first.evaluate('(e)=>e.open'),'Enter closes details')
 page.screenshot(path=str(shots/'keyboard.png'),full_page=True);page.close()
 page=browser.new_page(viewport={'width':390,'height':880},has_touch=True,is_mobile=True)
 page.set_content(html);page.locator('[data-fv-r436-proof] summary').first.tap()
 ok(page.locator('[data-fv-r436-proof]').first.evaluate('(e)=>e.open'),'touch opens')
 page.screenshot(path=str(shots/'touch.png'),full_page=True);page.close()
 page=browser.new_page(viewport={'width':390,'height':880},java_script_enabled=False)
 page.set_content(html);page.locator('[data-fv-r436-proof] summary').first.click()
 ok(page.locator('[data-fv-r436-proof] article').count()==6,'no-JS full source records')
 ok(page.locator('.fv-r429__cta').count()==2,'no-JS original CTA')
 page.screenshot(path=str(shots/'no-js.png'),full_page=True);page.close()
 for label,kw in [('reduced-motion',{'reduced_motion':'reduce'}),('forced-colors',{'forced_colors':'active'})]:
  page=browser.new_page(viewport={'width':390,'height':880},**kw)
  page.set_content(html);page.locator('[data-fv-r436-proof] summary').first.click()
  ok(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),label+' no overflow')
  page.screenshot(path=str(shots/f'{label}.png'),full_page=True);page.close()
 page=browser.new_page(viewport={'width':390,'height':880})
 page.set_content(html);page.evaluate("document.documentElement.style.fontSize='32px'")
 page.locator('[data-fv-r436-proof] summary').first.click()
 ok(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),'200% root text size no overflow')
 page.screenshot(path=str(shots/'200-percent-text.png'),full_page=True);page.close()
 page=browser.new_page(viewport={'width':768,'height':900});page.set_content(html)
 page.emulate_media(media='print')
 ok(page.locator('summary').count()>=12,'print source drawers retained')
 page.screenshot(path=str(shots/'print.png'),full_page=True);page.close()
 browser.close()
report={"status":"PASS_OFFLINE_CHROMIUM","assertions":checks,"screenshots":len(list(shots.glob('*.png'))),"genuine_axe":"NOT_TESTED_NO_BUNDLE","navigated_lcp":"NOT_MEASURED_NAVIGATION_BLOCKED","navigated_cls":"NOT_MEASURED_NAVIGATION_BLOCKED","wp_staging":"NOT_TESTED"}
(QA/'browser.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print('PASS',checks,'offline Chromium assertions; screenshots:',report['screenshots'])
