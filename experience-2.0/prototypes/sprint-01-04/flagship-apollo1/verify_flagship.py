from pathlib import Path
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parent
HTML=(ROOT/'index.html').read_text(encoding='utf-8')
results={}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(360,800),(390,844),(768,1024),(1024,900),(1440,900),(1920,1080)]:
  page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,reduced_motion='reduce')
  page.set_content(HTML,wait_until='domcontentloaded')
  page.wait_for_timeout(400)
  stats=page.evaluate('''() => ({scrollWidth:document.documentElement.scrollWidth,innerWidth:innerWidth,chapters:document.querySelectorAll('.chapter').length,enhanced:document.documentElement.classList.contains('enhanced'),images:[...document.querySelectorAll('.chapter__figure img')].every(i=>!!i.alt),focusableOpeners:[...document.querySelectorAll('[data-source]')].filter(e=>!e.hidden).length})''')
  assert stats['scrollWidth']<=stats['innerWidth'],f'horizontal overflow width {width}: {stats}'
  assert stats['chapters']==6 and stats['enhanced'] and stats['images'] and stats['focusableOpeners']==6,stats
  if width==1440:
   page.locator('[data-source="0"]').click()
   assert page.locator('#source-dialog').evaluate('(e)=>e.open')
   assert page.locator('#source-dialog').get_attribute('aria-labelledby')=='dialog-title'
   assert page.locator('#dialog-title').inner_text()=='Three men. One ground test.'
   assert page.locator('#dialog-ledger-link').get_attribute('href')=='../source-ledger/index.html#fv-ex2-ledger-apollo1-record-01'
   page.keyboard.press('Escape')
   assert not page.locator('#source-dialog').evaluate('(e)=>e.open')
   assert page.evaluate('document.activeElement.getAttribute("data-source")')=='0','focus not restored after close'
   page.locator('[data-jump="4"]').click()
   page.wait_for_timeout(300)
   assert page.locator('#record-05').is_visible()
  page.screenshot(path=str(ROOT/f'flagship-{width}.png'),full_page=(width in (390,1440)),animations='disabled')
  results[str(width)]={'enhanced':stats,'screenshot':f'flagship-{width}.png'}
  page.close()
 page=browser.new_page(java_script_enabled=False,viewport={'width':390,'height':844})
 page.set_content(HTML,wait_until='domcontentloaded')
 js=page.evaluate('''() => ({enhanced:document.documentElement.classList.contains('enhanced'),chapters:document.querySelectorAll('.chapter').length,sources:[...document.querySelectorAll('.chapter__figure a')].length,sourceLinks:document.querySelectorAll('a[href*="nasa.gov"]').length,visibleFigures:[...document.querySelectorAll('.chapter__figure')].filter(el=>getComputedStyle(el).display!=='none').length,modalButtons:[...document.querySelectorAll('[data-source]')].filter(e=>!e.hidden).length,touch: getComputedStyle(document.querySelector('.chapter-shell')).touchAction,overflow:document.documentElement.scrollWidth>innerWidth})''')
 assert not js['enhanced'] and js['chapters']==6 and js['visibleFigures']==6 and js['modalButtons']==0 and js['sourceLinks']>=6 and not js['overflow'],js
 page.screenshot(path=str(ROOT/'flagship-nojs-390.png'),full_page=False,animations='disabled')
 results['nojs390']=js
 # Missing IntersectionObserver: do not reveal a stale sticky viewer that hides chapter figures.
 absent=browser.new_page(viewport={'width':1440,'height':900})
 no_observer=HTML.replace('<script>\n(()=>', '<script>window.IntersectionObserver = undefined; delete window.IntersectionObserver;</script><script>\n(()=>',1)
 absent.set_content(no_observer)
 static_fallback=absent.evaluate("() => ({enhanced:document.documentElement.classList.contains('enhanced'),figures:[...document.querySelectorAll('.chapter__figure')].filter(x=>getComputedStyle(x).display!=='none').length,sourceLinks:document.querySelectorAll('.chapter__figure a[href*=nasa]').length})")
 assert not static_fallback['enhanced'] and static_fallback['figures']==6 and static_fallback['sourceLinks']>=6,static_fallback
 results['missing_observer']=static_fallback
 absent.close()
 # Fault injection: if an enhancement dependency crashes, the full narrative stays readable.
 broken=browser.new_page(viewport={'width':390,'height':844})
 fault=HTML.replace('<script>\n(()=>', '<script>window.IntersectionObserver = class { constructor(){ throw new Error("simulated enhancement failure"); } };</script><script>\n(()=>',1)
 broken.set_content(fault)
 degraded=broken.evaluate("() => ({enhanced:document.documentElement.classList.contains('enhanced'), visibleFigures:[...document.querySelectorAll('.chapter__figure')].filter(x=>getComputedStyle(x).display!=='none').length, openers:[...document.querySelectorAll('[data-source]')].filter(x=>!x.hidden).length})")
 assert degraded['enhanced'] is False and degraded['visibleFigures']==6 and degraded['openers']==0,degraded
 results['fault_injection']=degraded
 broken.close()
 browser.close()
(ROOT/'QA_RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS',json.dumps(results,indent=2))
