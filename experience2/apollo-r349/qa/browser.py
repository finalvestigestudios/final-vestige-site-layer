#!/usr/bin/env python3
"""Apollo R349 real Chromium source-policy regression. Run from any directory.
Fixture-only: not installed WordPress, axe-core certification or field Web Vitals.
"""
import json
import subprocess
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'apollo-r349'/'QA'
OUT.mkdir(exist_ok=True)
php="define('ABSPATH',true);require "+json.dumps(str(ROOT/'apollo-r348/source-custody.php'))+";echo fv_apollo_r348_experience_shortcode();"
html=subprocess.check_output(['php','-r',php],text=True)
css='\n'.join((ROOT/p).read_text() for p in [
'apollo-r339/assets/chronology-rail.css','apollo-r340/assets/accession-gallery.css',
'apollo-r345/evidence-plate.css','apollo-r347/assets/source-index.css',
'apollo-r348/assets/source-custody.css'])
js=(ROOT/'apollo-r347/assets/source-index.js').read_text()
assert html.count('data-fv-custody-source')==8
assert html.count('data-fv-r339-cta="editorial"')==1
assert 'data-fv-source-review-required' not in html
cases=[(320,True,16,False,False,False),(390,True,16,True,False,False),
(768,False,16,False,False,False),(1440,True,16,False,False,False),
(1920,True,16,False,True,False),(320,True,64,False,False,False),
(390,False,16,False,False,False),(768,True,16,False,False,True)]
rows=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,enabled,font,touch,reduced,forced in cases:
  ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,
     is_mobile=touch,has_touch=touch,reduced_motion='reduce' if reduced else 'no-preference',
     forced_colors='active' if forced else 'none')
  page=ctx.new_page();errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
  page.set_content('<html lang="en"><head><meta charset="UTF-8"><style>html{font-size:'+str(font)+'px}body{margin:0}'+css+'</style></head><body>'+html+'</body></html>')
  page.evaluate('''() => {window.__fvperf={lcp:null,cls:0};try{new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__fvperf.lcp=e.startTime)).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__fvperf.cls+=e.value})).observe({type:'layout-shift',buffered:true});}catch(e){window.__fvperf.error=String(e)}}''')
  if enabled:page.add_script_tag(content=js)
  assert not errors,errors
  for selector,n in [('[data-fv-custody-source]',8),('[data-fv-r339-source]',6),
    ('[data-fv-r340-source]',4),('[data-fv-apollo-primary-source]',3),
    ('[data-fv-apollo-source-link]',13),('[data-fv-r339-cta="editorial"]',1)]:
    assert page.locator(selector).count()==n,(selector,width)
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),('overflow',width,font)
  summary=page.locator('.fv-apollo-r348__detail summary').first
  detail=page.locator('.fv-apollo-r348__detail').first
  summary.focus();page.keyboard.press('Enter');assert detail.get_attribute('open') is not None
  page.keyboard.press('Enter');assert detail.get_attribute('open') is None
  if touch:summary.tap();assert detail.get_attribute('open') is not None;summary.tap()
  if enabled:
   assert page.locator('.fv-apollo-r347__filters button').count()==5
   page.locator('.fv-apollo-r347__filters button').last.click()
   assert page.locator('.fv-apollo-r347__group:visible').count()==1
  else:assert page.locator('.fv-apollo-r347__group:visible').count()==4
  if width==390 and enabled:
   pdf=page.pdf(format='A4',print_background=True)
   (OUT/'r349-390-source.pdf').write_bytes(pdf)
   doc=fitz.open(stream=pdf,filetype='pdf');txt=' '.join(x.get_text() for x in doc)
   assert txt.count('Evidence boundary:')>=13 and txt.count('Source status:')==8
   assert sum('www.nasa.gov/' in x.get('uri','') for pg in doc for x in pg.get_links() if x.get('kind')==2)>=8
   doc.close()
  if width in (320,390,1440) and font==16 and not forced:
   page.screenshot(path=str(OUT/f'r349-{width}-{ "js" if enabled else "nojs"}.png'),full_page=True)
  if font==64:page.screenshot(path=str(OUT/'r349-320-font64.png'),full_page=True)
  page.wait_for_timeout(175)
  perf=page.evaluate('window.__fvperf')
  rows.append({'viewport':width,'javascript':enabled,'font_px':font,'touch':touch,
    'forced_colors':forced,'reduced_motion':reduced,'local_fixture_lcp_ms':perf['lcp'],
    'observed_fixture_cls':perf['cls'],'result':'PASS'})
  ctx.close()
 browser.close()
(OUT/'r349-browser.json').write_text(json.dumps({'results':rows,'production_accepted':False},indent=2)+'\n')
print(f'PASS: {len(rows)} genuine Chromium viewport/keyboard/touch/no-JS/print contexts (fixture only)')
