#!/usr/bin/env python3
"""Playwright/real Chromium: R66 full custody rollback, no-JS, accessible controls.

The browser runs the SHA-pinned original R38 Desk and R66 Atlas in an actual
PHP-powered WordPress-API simulator. This is NOT installed WordPress/Assembler.
Verified axe-core and OS screen-reader certification are not claimed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from browser_r59_php_cohost import make_document
from playwright.sync_api import sync_playwright

WIDTHS=(320,360,390,428,768,1024,1440,1920)
LABELS=('Catalog reference','Record identity note','Catalog verification on NASA page',
        'Credit displayed by NASA','Producing center displayed by NASA',
        'NASA page last updated','Editorial source check','Reuse status',
        'Documentary boundary')

def source_integrity(page):
    assert page.locator('[data-fvx-record]').count()==6
    assert page.locator('[data-fva-record]').count()==6
    assert page.locator('[data-fva-cite-id]').count()==6
    assert page.locator('img').count()==0
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth+2')

def run(output:Path):
    output.mkdir(parents=True,exist_ok=True)
    html,source=make_document()
    receipt={'schema':'fv.apollo.r66.custody-matrix-browser.v1',
      'environment':'original-R38-Desk-and-source-built-Atlas-PHP-WP-API-simulator',
      'installed_wordpress':False,'verified_axe':False,'screen_readers':False,
      'hosted_core_web_vitals':False,'source_crosswalk_git_blob':source['source_crosswalk_blob'],
      'copyright_assessments_pending':6,'embedded_nasa_photographs':0,'geographic_pins':0,
      'responsive_cases':[],'tampering_cases':[],'structural_mutations':[],
      'local_performance_observations':[],'screenshots':{}}
    with sync_playwright() as playwright:
      browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
      for width in WIDTHS:
        for js in (False,True):
          for forced in (False,True):
            context=browser.new_context(viewport={'width':width,'height':880},
              java_script_enabled=js,forced_colors='active' if forced else 'none',
              reduced_motion='reduce',has_touch=width<=390,is_mobile=width<=390)
            page=context.new_page();issues=[];requests=[]
            page.on('pageerror',lambda e:issues.append(str(e)))
            page.on('request',lambda request:requests.append(request.url))
            page.set_content(html);source_integrity(page)
            assert not issues and not requests,(width,js,forced,issues,requests)
            if js:
              assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')=='yes'
              page.locator('[data-fva-filter="2017"]').click()
              assert page.locator('[data-fva-record]:visible').count()==2
              page.locator('[data-fva-reset]').click()
              assert page.locator('[data-fva-record]:visible').count()==6
              if not forced:
                page.evaluate("document.documentElement.style.setProperty('font-size','200%','important')")
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                page.evaluate("document.documentElement.style.removeProperty('font-size')")
                page.wait_for_timeout(70)
                receipt['local_performance_observations'].append({'width':width,
                  **page.evaluate('window.__fv_r53_lab||{}')})
                if width in (390,1440):
                  png=page.screenshot(full_page=True,animations='disabled')
                  assert png==page.screenshot(full_page=True,animations='disabled')
                  filename=f'R66_CUSTODY_{width}.png'
                  (output/filename).write_bytes(png)
                  receipt['screenshots'][filename]=hashlib.sha256(png).hexdigest()
            else:
              assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')!='yes'
              assert page.locator('[data-fva-controls]').is_hidden()
            page.emulate_media(media='print')
            assert page.locator('[data-fvx-record]:visible').count()==6
            assert page.locator('[data-fva-record]:visible').count()==6
            assert page.locator('[data-fva-drawer] dd:visible').count()==54
            assert page.locator('.fv-ex2-ledger__custody dd:visible').count()==30
            page.emulate_media(media='screen')
            assert not issues and not requests,(width,js,forced,issues,requests)
            receipt['responsive_cases'].append({'width':width,'javascript':js,'forced_colors':forced,
                'reduced_motion':True,'pass':True})
            context.close()
      # Every one of 54 independent disclosure values must withdraw the
      # optional controls on drift. No source card or citation may disappear.
      context=browser.new_context(viewport={'width':390,'height':900},
                                   reduced_motion='reduce',has_touch=True,is_mobile=True)
      page=context.new_page();network=[];errors=[]
      page.on('request',lambda request:network.append(request.url))
      page.on('pageerror',lambda e:errors.append(str(e)))
      for row in range(6):
        for field in range(9):
          page.set_content(html)
          source_integrity(page)
          assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')=='yes'
          dd=page.locator('[data-fva-drawer]').nth(row).locator('dd').nth(field)
          before=dd.text_content()
          dd.evaluate("e=>e.textContent='UNVERIFIED RECORD METADATA'")
          page.locator('input[data-fva-search]').fill('hatch')
          assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')!='yes',(row,field,before)
          assert page.locator('[data-fva-controls]').is_hidden(),(row,field)
          assert page.locator('[data-fva-export]').is_hidden(),(row,field)
          assert page.locator('[data-fva-record]:visible').count()==6,(row,field)
          assert page.locator('[data-fva-cite-id]').count()==6,(row,field)
          assert page.locator('[data-fva-drawer] dd').count()==54
          receipt['tampering_cases'].append({'record_id':f'{row+1:02d}',
            'field':LABELS[field],'optional_enhancement_disabled':True,'pass':True})
      # A modified field *before* source initialization must never enable JS.
      for original,spoof in (
          ('NASA/Kim Shiflett','NASA expressly grants commercial reuse'),
          ('No producing center displayed in reviewed metadata.', 'Unknown company'),
          ('Individual review required. No photograph is reproduced here.', 'Rights cleared.')):
        changed=html.replace(original,spoof,1)
        page.set_content(changed)
        source_integrity(page)
        assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')!='yes',original
        assert page.locator('[data-fva-controls]').is_hidden()
        receipt['structural_mutations'].append({'before':original,'pass':True})
      assert not network and not errors,(errors,network)
      context.close();browser.close()
    (output/'R66_CUSTODY_MATRIX_BROWSER_RECEIPT.json').write_text(
      json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('PASS',len(receipt['responsive_cases']),'responsive Chromium configurations;',
          len(receipt['tampering_cases']),'field mutations;',
          len(receipt['structural_mutations']),'pre-init mutations')
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
