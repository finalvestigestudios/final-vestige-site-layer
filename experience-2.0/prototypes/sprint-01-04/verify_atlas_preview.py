from pathlib import Path
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).parent
html=(root/'atlas-preview.html').read_text()
res={}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in (360,390,768,1440,1920):
  page=browser.new_page(viewport={'width':width,'height':900})
  page.set_content(html)
  metrics=page.evaluate('''() => ({documentWidth: document.documentElement.scrollWidth,width:innerWidth, cards:document.querySelectorAll('.case:not([hidden])').length})''')
  assert metrics['documentWidth']<=width,metrics
  assert metrics['cards']==6,metrics
  if width==1440:
   page.locator('[data-filter="Urban systems"]').click()
   assert page.locator('.case:not([hidden])').count()==2
   page.locator('[data-filter="all"]').click()
   page.locator('#search').fill('Petra')
   assert page.locator('.case:not([hidden])').count()==1
   assert 'Petra' in page.locator('.case:not([hidden])').inner_text()
   page.locator('#search').fill('')
   assert page.locator('.case:not([hidden])').count()==6
  page.screenshot(path=str(root/f'atlas-preview-{width}.png'),full_page=(width in [390,1440]),animations='disabled')
  res[width]=metrics
  page.close()
 page=browser.new_page(java_script_enabled=False,viewport={'width':390,'height':850})
 page.set_content(html)
 assert page.locator('.case:not([hidden])').count()==6
 assert page.locator('[data-enhancement]:not([hidden])').count()==0
 assert page.locator('a[href*="finalvestige.com/2026/"]').count()==6
 res['nojs']={'cards':6,'links':6}
 browser.close()
(root/'ATLAS_QA_RESULTS.json').write_text(json.dumps(res,indent=2)+'\n')
print('PASS Atlas UI / filter / search / no-JS / no-overflow',json.dumps(res))
