#!/usr/bin/env python3
"""R341 local Chromium gate; rendered source from real R340 PHP, no WP installation.
CHROMIUM defaults to /usr/bin/chromium. Screenshots/receipt go to FV_R341_OUT.
"""
import importlib.util, json, os, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parents[2]
BASE=HERE/'apollo-r340/qa/browser_acceptance.py'
OUT=Path(os.environ.get('FV_R341_OUT','/tmp/fv-apollo-r341'))
OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('apollo_r340_qa',BASE)
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
body,html,handles=q.php_fixture()
assert not q.contract(body)
assert len(handles)==2
results=[]; shots=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
    for w,js,forced in [(320,False,False),(390,True,False),(768,False,False),(1440,True,False),(1920,True,True)]:
        page=browser.new_page(viewport={'width':w,'height':950},java_script_enabled=js,
            reduced_motion='reduce',forced_colors='active' if forced else 'none',has_touch=w<=390)
        try:
            if js:
                page.add_init_script("window.__fvCLS=0;new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__fvCLS+=e.value})).observe({type:'layout-shift',buffered:true});")
            page.set_content(html,wait_until='load')
            data=page.evaluate('''() => ({overflow:document.documentElement.scrollWidth-innerWidth,
              ids:[...document.querySelectorAll('[id]')].map(x=>x.id),
              nasa:document.querySelectorAll('[data-fv-r340-source]').length,
              rails:document.querySelectorAll('[data-fv-r339]').length,
              galleries:document.querySelectorAll('[data-fv-r340-gallery]').length,
              ctas:document.querySelectorAll('[data-fv-r339-cta="editorial"]').length,
              cls:window.__fvCLS||0,
              lcp:(performance.getEntriesByType('largest-contentful-paint').at(-1)||{}).startTime||null})''')
            assert data['overflow']<=1 and len(data['ids'])==len(set(data['ids'])),(w,data)
            assert (data['nasa'],data['rails'],data['galleries'],data['ctas'])==(8,2,2,2)
            summary=page.locator('[data-fv-r340-gallery]').first.locator('summary').first
            summary.focus();page.keyboard.press('Enter')
            assert page.locator('[data-fv-r340-gallery]').first.locator('details').first.evaluate('(e)=>e.open')
            if w in (320,1440):
                filename=f'r341-browser-{w}-'+('js' if js else 'nojs')+'.png'
                page.screenshot(path=str(OUT/filename),full_page=True)
                shots.append(filename)
            results.append({'width':w,'js':js,'forcedColors':forced,'overflowPx':data['overflow'],
                            'observedInitialCLS':data['cls'],'fixtureLCPms':data['lcp'],'result':'PASS'})
        finally:page.close()
    browser.close()
receipt={'scope':'actual Chromium rendering of locally PHP-generated HTML; NOT WP/CSP/production Core Web Vitals',
         'cases':results,'screenshots':shots,'release':'HARD HOLD',
         'unverified':['genuine axe-core','installed WordPress reusable blocks','non-Chromium/screen readers','production revenue']}
(OUT/'r341-browser.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(results),'real Playwright Chromium contexts; screenshot and JSON artifacts saved')
