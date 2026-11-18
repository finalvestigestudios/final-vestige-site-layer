"""Source-controlled read-only browser smoke. Locally rendered PHP, not hosted WordPress."""
import json, os, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
script='require '+json.dumps(str(ROOT/'apollo_rights_gallery.php'))+'; echo fv457_render();'
html=subprocess.check_output(['php','-r',script],text=True)
assert 'month-only' in html and '27 January 1967' in html and '27 January 2017' in html
assert 'not a fabricated photograph-by-photograph sequence' in html
assert html.count('the-hatch-opened-inward-apollo-1/')==1
count=0
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
 for width in (320,360,390,768,1024,1440,1920):
  for js in (True,False):
   ctx=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js)
   page=ctx.new_page();page.set_content(html)
   assert page.locator('.fv457__moment:visible').count()==3
   assert page.locator('.fv457__card:visible').count()==6
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
   drawer=page.locator('.fv457__moment details').nth(1)
   drawer.locator('summary').focus();page.keyboard.press('Enter')
   assert drawer.evaluate('(e)=>e.open') and drawer.get_by_role('link').is_visible()
   if js:
    page.get_by_role('button',name='Confirmed homepage (1)').click()
    assert page.locator('.fv457__card:visible').count()==1
    assert page.locator('.fv457__moment:visible').count()==3
   count+=1;ctx.close()
 b.close()
print(f'R463 chronology source-controlled Chromium smoke: {count}/14 contexts PASS (not hosted/axe/CWV)')

