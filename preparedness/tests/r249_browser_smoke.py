"""Optional offline Chromium smoke for UNAPPROVED reader copy; not original Tool #104 QA."""
from pathlib import Path
from playwright.sync_api import sync_playwright
p=Path(__file__).resolve().parents[1]/'audits/r249_family_card_reader_disclosure_draft.html'
with sync_playwright() as playwright:
 b=playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 total=0
 for js in (False,True):
  for width in (320,360,390,768,1440):
   page=b.new_page(viewport={'width':width,'height':800},java_script_enabled=js)
   requests=[]
   page.on('request',lambda req:requests.append(req.url))
   page.set_content(p.read_text(encoding="utf-8"),wait_until="load")
   assert page.locator('h2').count()==1
   assert page.locator('a').count()==1
   assert page.locator('a').first.get_attribute('href')=='/preparedness/'
   assert page.locator('input,form,script,button').count()==0
   assert page.get_by_text('six filled-in fields',exact=False).is_visible()
   assert page.get_by_text('No paid kit',exact=False).is_visible()
   assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1'),width
   assert len(requests)==0,requests
   page.emulate_media(media='print')
   assert page.get_by_text('six filled-in fields',exact=False).is_visible()
   assert page.get_by_text('No paid kit',exact=False).is_visible()
   total+=2
   page.close()
 print('Offline authored-preview Chromium checks:',total,'PASS across JS on/off; 320/360/390/768/1440px and print')
 b.close()
