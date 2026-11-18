#!/usr/bin/env python3
"""Actual local Chromium checks of committed reviewer.html using set_content.
Does NOT claim navigated WordPress staging, axe-core, LCP or CLS measurements.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, hashlib
HERE=Path(__file__).resolve().parents[1]
SCREEN=HERE/'QA/screenshots';SCREEN.mkdir(parents=True,exist_ok=True)
HTML=(HERE/'reviewer.html').read_text()
ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
checks=[];errors=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in (320,360,390,768,1024,1440,1920):
        for js in (True,False):
            ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce',has_touch=True)
            page=ctx.new_page();page.set_content(HTML,wait_until='load')
            try:
                assert page.get_by_role('heading',level=1).count()==1
                assert page.locator('details').count()==2
                assert page.locator(f'a[href="{ARTICLE}"]').count()==1
                assert page.locator('form,iframe,[data-lat],[data-lon]').count()==0
                assert page.locator('a[href*="checkout"],a[href*="payhip"]').count()==0
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                assert page.get_by_text('No verified payable Apollo SKU').count()==1
                if width==390 and js:
                    s=page.get_by_text('1967 · The Review Board\'s finding')
                    s.focus();page.keyboard.press('Enter');assert page.locator('details').first.get_attribute('open') is not None
                    s.focus();page.keyboard.press('Enter');assert page.locator('details').first.get_attribute('open') is None
                if width==360 and js:
                    page.locator('details summary').last.tap();assert page.locator('details').last.get_attribute('open') is not None
                out=SCREEN/f'{width}-{"js" if js else "nojs"}.png'
                page.screenshot(path=str(out),full_page=True)
                checks.append({'width':width,'js':js,'status':'PASS','screenshot':out.name,
                              'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
            except Exception as exc:errors.append({'width':width,'js':js,'error':str(exc)})
            ctx.close()
    browser.close()
result={'status':'PASS' if not errors and len(checks)==14 else 'FAIL','cases':len(checks),
        'results':checks,'errors':errors,'mode':'real Chromium page.set_content against committed reviewer.html, local/offline only',
        'actual_WordPress_staging':'NOT_RUN','axe_core':'NOT_RUN','navigated_LCP_CLS':'NOT_RUN',
        'creator_and_commerce':'NOT_VERIFIED'}
(HERE/'QA/BROWSER.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps({'status':result['status'],'cases':len(checks),'errors':errors}))
raise SystemExit(bool(errors))
