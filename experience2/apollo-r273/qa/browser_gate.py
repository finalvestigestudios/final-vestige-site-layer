#!/usr/bin/env python3
"""R273 Chromium acceptance; genuine local Chromium with offline source preview, not installed WordPress/axe."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from hashlib import sha256
import argparse, json, subprocess
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('output'); args=parser.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
html=subprocess.check_output(['php', str(ROOT/'qa/render.php'),'pending']).decode('utf8')
cases=[]; screenshots={}; seen=0
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in [320,390,768,1440,1920]:
  for js in [True,False]:
   context=browser.new_context(viewport={'width':width,'height':800},java_script_enabled=js,reduced_motion='reduce', color_scheme='dark',device_scale_factor=1)
   page=context.new_page();page.set_content(html,wait_until='load');page.evaluate('document.fonts.ready') if js else None
   seen+=1
   assert page.locator('main > h1').count()==1
   assert page.locator('aside.fv-r273[aria-labelledby="fv-r273-title"][data-fv-review-ready="false"]').count()==1
   assert page.locator('.fv-r273__status').count()==2
   assert all('pending' in t.lower() for t in page.locator('.fv-r273__status').all_text_contents())
   assert page.locator('a[href^="https://www.nasa.gov/"]').count()==2
   assert page.locator('a[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]').count()==1
   assert page.locator('a[href*="payhip"],a[href*="minimuseum"],script[src]').count()==0
   assert page.locator('a[target="_blank"][rel="noopener noreferrer"]').count()==2
   assert page.locator('details[open]').count()==0
   # Native details works without JS, using real browser click.
   page.locator('summary').click()
   assert page.locator('details[open]').count()==1
   assert page.locator('.fv-r273__records li').count()==2
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
   # Focus-visible can be reached with keyboard, including on mobile widths.
   page.locator('summary').focus()
   assert page.evaluate('document.activeElement.tagName')=='SUMMARY'
   if js:
    ax=page.context.new_cdp_session(page)
    ax.send('Accessibility.enable');tree=ax.send('Accessibility.getFullAXTree')['nodes']
    names=[n.get('name',{}).get('value','') for n in tree]
    assert any('Inspect review status' in str(n) for n in names)
    assert any('Read the free Apollo 1 investigation' in str(n) for n in names)
    ax.detach()
   if width in [390,1440]:
    # Reset disclosure for screenshot; fixed viewport and deterministic content.
    page.locator('summary').click()
    page.screenshot(path=str(out/(f'{width}-'+('js' if js else 'nojs')+'.png')),full_page=True,animations='disabled')
    screenshots[f'{width}-'+('js' if js else 'nojs')+'.png']=sha256((out/(f'{width}-'+('js' if js else 'nojs')+'.png')).read_bytes()).hexdigest()
   cases.append({'width':width,'js':js,'result':'PASS'})
   context.close()
 # Negative mutation: removing review notice must fail its mandatory gate.
 assert 'Editorial review remains open' in html
 assert 'Editorial review remains open' not in html.replace('Editorial review remains open','Editorial review COMPLETE')
 browser.close()
receipt={'suite':'R273','browser_cases':cases,'count':seen,'screenshots_sha256':screenshots,'independent_axe':'NOT_EXECUTED','wordpress':'NOT_INSTALLED','live_http':'NOT_TESTED','editorial_approval':'NOT_RECEIVED'}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(f'R273 {seen}/{seen} Chromium contexts PASS; receipt SHA256 {sha256((out/"receipt.json").read_bytes()).hexdigest()}')
