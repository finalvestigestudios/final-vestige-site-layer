#!/usr/bin/env python3
"""R468 offline Chromium regression. Local markup via set_content, not navigated LCP/CLS or hosted QA."""
from pathlib import Path
import hashlib
import json
import subprocess
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'/'r468'
OUT.mkdir(parents=True,exist_ok=True)
html=subprocess.check_output(['php','-r',f'require {json.dumps(str(ROOT/"apollo_rights_gallery.php"))};echo fv457_render();'],text=True)
assert html.count('data-fv457-card=')==6
page_html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">'+html+'</body></html>'
results={'mode':'local PHP markup injected with Playwright set_content; NOT navigated or hosted WordPress','axe':'HOLD_NOT_RUN: axe-core not installed','lcp':'HOLD_NOT_RUN: no navigation','cls':'HOLD_NOT_RUN: no navigation','cases':[]}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-background-networking'])
    for width in (320,390,768,1920):
        for enabled in (False,True):
            ctx=browser.new_context(viewport={'width':width,'height':860},java_script_enabled=enabled,reduced_motion='reduce',device_scale_factor=1)
            page=ctx.new_page()
            errors=[]
            page.on('pageerror',lambda err:errors.append(str(err)))
            page.set_content(page_html,wait_until='domcontentloaded')
            page.wait_for_timeout(60)
            assert not errors,errors
            assert page.locator('[data-fv457-card]').count()==6
            assert page.locator('[data-fv457-plate]').count()==3
            assert page.locator('.fv457__moment').count()==3
            assert page.locator('.fv457__cta a').count()==1
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'overflow at {width}'
            if enabled:
                page.get_by_role('button',name='NASA ID confirmed (4)').click()
                assert page.locator('[data-fv457-card]:visible').count()==4
                page.get_by_role('button',name='Not in Atlas (3)').click()
                assert page.locator('[data-fv457-card]:visible').count()==3
                page.get_by_role('button',name='All six').focus()
                page.keyboard.press('Enter')
                assert page.locator('[data-fv457-card]:visible').count()==6
            else:
                assert not page.locator('[data-fv457-controls]').is_visible()
                assert page.locator('[data-fv457-card]:visible').count()==6
            page.locator('.fv457__skip').focus();page.keyboard.press('Enter')
            assert page.evaluate('document.activeElement.id')=='fv457-1-records'
            if enabled and width in (390,1920):
                path=OUT/f'{width}-r468.png'
                page.screenshot(path=str(path),full_page=True,animations='disabled')
            results['cases'].append({'viewport':width,'javascript':enabled,'result':'PASS'})
            ctx.close()
    browser.close()
results['screenshot_sha256']={path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob('*.png'))}
(OUT/'results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
print('PASS R468 Chromium:',len(results['cases']),'contexts; four widths 320–1920, JS on/off, key navigation, source filters, overflow')
