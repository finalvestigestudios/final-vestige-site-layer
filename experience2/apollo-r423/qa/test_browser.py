#!/usr/bin/env python3
"""Chromium offline markup fixture QA; no claim of installed WP, axe, real navigation or LCP/CLS."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'QA/fixture.html').read_text()
SHOTS = ROOT / 'QA/screenshots'
SHOTS.mkdir(parents=True, exist_ok=True)
results=[]

def verify(condition, label):
    if not condition: raise AssertionError(label)
    results.append({'check':label,'pass':True})

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width in (320,360,390,768,1024,1440,1920):
        page=browser.new_page(viewport={'width':width,'height':850},java_script_enabled=False)
        page.set_content(HTML)
        verify(page.locator('[data-fv-r423-bridge]').count()==2,f'{width} two distinct reader instances')
        verify(page.locator('[data-fv-r423-bridge] details').count()==24,f'{width} six custody and six source disclosures per instance')
        verify(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),f'{width} zero horizontal overflow')
        verify(page.evaluate('(()=>{const ids=[...document.querySelectorAll("[id]")].map(x=>x.id);return new Set(ids).size===ids.length})()'),f'{width} unique IDs')
        verify(page.locator('img,iframe,script,form,[data-geo-pin]').count()==0,f'{width} no extra media scripts forms pins')
        page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True)
        page.close()
    # Keyboard operation of native summary without JS
    page=browser.new_page(viewport={'width':390,'height':850},java_script_enabled=False)
    page.set_content(HTML)
    summary=page.locator('summary').first
    summary.focus()
    page.keyboard.press('Enter')
    verify(page.locator('details').first.get_attribute('open') is not None,'keyboard Enter expands native source limitation')
    page.keyboard.press('Enter')
    verify(page.locator('details').first.get_attribute('open') is None,'keyboard Enter collapses native source limitation')
    page.emulate_media(reduced_motion='reduce')
    verify(page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches'),'reduced-motion setting')
    print('reduced shot',flush=True); page.screenshot(path=str(SHOTS/'390-reduced.png'),full_page=False)
    page.emulate_media(forced_colors='active')
    verify(page.evaluate('matchMedia("(forced-colors: active)").matches'),'forced-colors setting')
    print('forced shot',flush=True); page.screenshot(path=str(SHOTS/'390-forced.png'),full_page=False)
    page.emulate_media(forced_colors='none')
    page.close()
    zoom=browser.new_page(viewport={'width':390,'height':850},java_script_enabled=False)
    zoom.set_content(HTML.replace('</head>','<style>html{font-size:200%!important}</style></head>'))
    verify(zoom.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),'390 200% text no overflow')
    zoom.screenshot(path=str(SHOTS/'390-zoom.png'),full_page=False)
    zoom.close()
    touch=browser.new_page(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,java_script_enabled=False)
    touch.set_content(HTML)
    print('touch start',flush=True); touch.locator('summary').first.tap()
    verify(touch.locator('details').first.get_attribute('open') is not None,'touch expands native disclosure')
    touch.screenshot(path=str(SHOTS/'390-touch.png'),full_page=False)
    touch.close()
    browser.close()
output={'suite':'R423 PHP-shaped offline fixture browser acceptance','passed':len(results),'failed':0,'navigation':'BLOCKED_BY_ADMINISTRATOR (file: navigation inspected separately)','axe_core':'NOT_EXECUTED','lcp_cls':'NOT_MEASURED (requires navigated installed staging)','results':results}
(ROOT/'QA/browser-results.json').write_text(json.dumps(output,indent=2)+'\n')
print(f"PASS {len(results)} Chromium offline fixture assertions; screenshots {len(list(SHOTS.glob('*.png')))}")
