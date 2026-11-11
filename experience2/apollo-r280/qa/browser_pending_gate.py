#!/usr/bin/env python3
"""R280 real Chromium acceptance of actual PHP-rendered pending review; offline, not WP/CSP/field CWV."""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r280-qa')
OUT.mkdir(parents=True,exist_ok=True)
PHP=ROOT/'experience2/apollo-r280/qa/pending_contract_gate.php'
CSS=ROOT/'experience2/apollo-r273/assets/review-custody.css'
p=subprocess.run(['php',str(PHP),str(OUT)],capture_output=True,text=True,check=True,timeout=15)
html=(OUT/'rendered.html').read_text()
css=CSS.read_text()
nasa='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
free='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
checks=[];shots={}
with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width in (320,390,768,1440,1920):
    for js in (False,True):
      ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                  has_touch=width<=390,reduced_motion='reduce',forced_colors='active' if width==320 else 'none')
      page=ctx.new_page();req=[];errors=[]
      page.on('request',lambda r:req.append(r.url))
      page.on('pageerror',lambda e:errors.append(str(e)))
      doc=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>{css}</style></head><body>{html}</body></html>'
      page.set_content(doc)
      assert page.locator('aside.fv-r273[data-fv-review-ready="false"]').count()==1,(width,js)
      assert page.get_by_role('heading',name='Editorial review remains open').count()==1
      assert page.get_by_role('link',name='Read the free Apollo 1 investigation').count()==1
      assert page.locator('a[href="'+nasa+'"]').count()==2
      assert page.locator('a[href="'+free+'"]').count()==1
      assert page.locator('details').count()==1
      assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),width
      assert not req and not errors,(width,js,req,errors)
      page.locator('summary').focus();page.keyboard.press('Enter')
      assert page.locator('details[open]').count()==1
      assert page.locator('a[href="'+nasa+'"]').first.is_visible()
      assert page.get_by_text('two editorial record categories',exact=False).is_visible()
      page.keyboard.press('Enter')
      assert page.locator('details[open]').count()==0
      page.emulate_media(media='print')
      assert page.locator('a[href="'+nasa+'"]').first.is_visible()
      page.emulate_media(media='screen')
      if width in (390,1440) and not js:
         path=OUT/f'{width}-nojs.png';page.screenshot(path=str(path),full_page=True,animations='disabled')
         shots[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
      checks.append({'viewport':width,'js':js,'result':'PASS','requests':0,'page_errors':0,'horizontal_overflow':False,'note':'offline browser behavior only'})
      ctx.close()
  # Browser-interface zoom/root-text enlargement is a separate unresolved gate.
  browser.close()
receipt={'suite':'R280 actual PHP pending-only WordPress-adapter browser regression',
'contexts':checks,'screenshots':shots,'php_scenarios':17,
'limits':['Chromium page.set_content, not HTTP/CSP','No installed WordPress/Assembler','Genuine axe-core not installed/executed','No independent screen reader','No field LCP/CLS','No native UI zoom'],
'release':'HARD_HOLD'}
(OUT/'browser_receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print('R280 Chromium',len(checks),'/',len(checks),'PASS; receipt sha256',hashlib.sha256((OUT/'browser_receipt.json').read_bytes()).hexdigest())
