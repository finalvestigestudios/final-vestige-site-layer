#!/usr/bin/env python3
"""Apollo R352: executable semantic acceptance on locally rendered PHP, not WordPress/axe."""
import json, re, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[3]/'experience2'
entry=root/'apollo-r348/source-custody.php'
code='define("ABSPATH",true);require '+json.dumps(str(entry))+';echo fv_apollo_r348_experience_shortcode();'
html=subprocess.check_output(['php','-r',code],text=True)
assert 'role="group" aria-label="Filter evidence types"' in html
assert html.count('data-fv-custody-source')==8
assert html.count('data-fv-r339-cta="editorial"')==1
css='\n'.join((root/path).read_text() for path in (
 'apollo-r339/assets/chronology-rail.css','apollo-r340/assets/accession-gallery.css',
 'apollo-r345/evidence-plate.css','apollo-r347/assets/source-index.css',
 'apollo-r348/assets/source-custody.css'))
js=(root/'apollo-r347/assets/source-index.js').read_text()
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,scripting,zoom in ((320,True,4),(390,False,1),(768,True,1),(1440,True,1),(1920,True,1)):
  ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=scripting)
  page=ctx.new_page()
  page.set_content('<html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style><body>'+html+'</body></html>')
  if scripting:page.add_script_tag(content=js)
  if zoom!=1:page.evaluate('(z)=>document.documentElement.style.fontSize=(16*z)+"px"',zoom)
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
  names=[v.strip() for v in page.locator('summary').all_text_contents()]
  assert len(names)==len(set(names))==21 and all(' for ' in v for v in names)
  links=[v.strip() for v in page.locator('[data-fv-custody-source]').all_text_contents()]
  assert len(set(links))==8 and all(v.startswith('Open institutional source record — ') for v in links)
  if scripting:
   assert page.get_by_role('group',name='Filter evidence types').count()==1
   page.locator('.fv-apollo-r347__filters button').last.click()
   assert page.locator('.fv-apollo-r347__group:visible').count()==1
  else:assert page.locator('.fv-apollo-r347__group:visible').count()==4
  summary=page.locator('.fv-apollo-r348__detail summary').first
  summary.focus();page.keyboard.press('Enter')
  assert page.locator('.fv-apollo-r348__detail').first.get_attribute('open') is not None
  ctx.close()
 browser.close()
print('PASS 5/5 Chromium semantic navigation/viewport cases; axe-core NOT executed')
