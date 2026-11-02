#!/usr/bin/env python3
"""R65 Chromium: measure EVERY native Apollo suite control, not select links.
Real R38 PHP + source-built Atlas in WP-API simulation; NOT installed WordPress.
Includes 320–1920px, JS off/on, forced colors, filtered print and LCP/CLS lab.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from browser_r59_php_cohost import make_document
from playwright.sync_api import sync_playwright

WIDTHS=(320,360,390,428,768,1024,1440,1920)
EXPECTED_URLS=(
 'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
 'https://www.nasa.gov/image-detail/amf-s67-15717/',
 'https://www.nasa.gov/image-detail/amf-s66-58038/',
 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
 'https://www.nasa.gov/image-detail/amf-s67-21294/',
 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
)

def target_measurement(page):
    return page.evaluate('''() => [...document.querySelectorAll(
      '.fv-ex2-apollo-suite a, .fv-ex2-apollo-suite button, .fv-ex2-apollo-suite summary, .fv-ex2-apollo-suite input')]
      .filter(e => {const r=e.getBoundingClientRect(),s=getComputedStyle(e);
        return r.width>0 && r.height>0 && s.visibility!=='hidden' && !e.closest('[hidden]');})
      .map(e => {const r=e.getBoundingClientRect();return {
        tag:e.tagName, css:typeof e.className==='string'?e.className:'',
        name:e.getAttribute('aria-label')||e.textContent.trim().slice(0,65)||e.type,
        w:+r.width.toFixed(2), h:+r.height.toFixed(2) };})''')

def run(output:Path):
    output.mkdir(parents=True,exist_ok=True)
    html,manifest=make_document()
    receipt={'schema':'fv.apollo.r65.all-targets.v1',
      'scope':'original-R38-and-built-Atlas/PHP-WordPress-API-simulator',
      'wordpress':'NOT_INSTALLED','axe':'NOT_EXECUTED_NO_VERIFIED_BUNDLE',
      'assistive_technology':'NOT_EXECUTED','hosted_cwv':'NOT_MEASURED',
      'source_crosswalk_git_blob':manifest['source_crosswalk_blob'],
      'cases':[],'screenshots':{},'lab_metrics':[],
      'all_six_nasa_image_rights':'UNREVIEWED','geo_pins':0}
    with sync_playwright() as p:
      browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
      for width in WIDTHS:
        for js in (False,True):
          for forced in (False,True):
            context=browser.new_context(viewport={'width':width,'height':850},
              java_script_enabled=js, forced_colors='active' if forced else 'none',
              reduced_motion='reduce', is_mobile=width<=390,has_touch=width<=390)
            page=context.new_page();errors=[];network=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:network.append(r.url))
            page.set_content(html)
            assert not errors and not network,(width,js,forced,errors,network)
            assert page.locator('[data-fvx-record]').count()==6
            assert page.locator('[data-fva-record]').count()==6
            assert page.locator('img').count()==0
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
            controls=target_measurement(page)
            too_small=[x for x in controls if x['h']<43.5 or x['w']<23.5]
            assert len(controls)>=50,(width,js,forced,len(controls))
            assert not too_small,(width,js,forced,'SMALL_INTERACTIVE_CONTROLS',too_small)
            anchors=page.locator('.fva-card__external')
            assert anchors.count()==6
            for i,expected in enumerate(EXPECTED_URLS):
              item=anchors.nth(i)
              assert item.get_attribute('href')==expected
              assert item.get_attribute('target')=='_blank'
              assert 'noopener' in (item.get_attribute('rel') or '').split()
              item.focus()
              focus=item.evaluate('''e=>({isActive:document.activeElement===e,
                focusVisible:e.matches(':focus-visible'),outline:parseFloat(getComputedStyle(e).outlineWidth),
                style:getComputedStyle(e).outlineStyle})''')
              assert focus['isActive'] and focus['focusVisible'] and focus['outline']>=2 and focus['style']!='none',(width,i,focus)
            page.emulate_media(media='print')
            assert page.locator('[data-fvx-record]:visible').count()==6
            assert page.locator('[data-fva-record]:visible').count()==6
            assert page.locator('[data-fva-drawer] dd:visible').count()==54
            assert page.locator('.fv-ex2-ledger__custody dd:visible').count()==30
            # All six real NASA archive URLs survive on paper even if filters
            # previously concealed the evidence cards on screen.
            for i,url in enumerate(EXPECTED_URLS):
              printed=anchors.nth(i).evaluate('(e)=>getComputedStyle(e,"::after").content')
              assert url in printed,(width,i,printed)
            page.emulate_media(media='screen')
            if js:
              assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')=='yes'
              page.locator('input[data-fvx-search]').fill('S67-19766')
              page.locator('[data-fva-filter="2017"]').click()
              assert page.locator('[data-fvx-record]:visible').count()==1
              assert page.locator('[data-fva-record]:visible').count()==2
              page.emulate_media(media='print')
              assert page.locator('[data-fvx-record]:visible').count()==6
              assert page.locator('[data-fva-record]:visible').count()==6
              page.emulate_media(media='screen')
              page.locator('input[data-fvx-search]').fill('')
              page.locator('[data-fva-reset]').click()
              if not forced:
                # 200% *text enlargement* checks layout without viewport trickery.
                page.evaluate("document.documentElement.style.setProperty('font-size','200%','important')")
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                page.evaluate("document.documentElement.style.removeProperty('font-size')")
                page.wait_for_timeout(90)
                receipt['lab_metrics'].append({'width':width,**page.evaluate('window.__fv_r53_lab||{}')})
                if width in (390,1440):
                  png=page.screenshot(full_page=True,animations='disabled')
                  assert png==page.screenshot(full_page=True,animations='disabled')
                  name=f'R65_ALL_TARGETS_{width}.png';(output/name).write_bytes(png)
                  receipt['screenshots'][name]=hashlib.sha256(png).hexdigest()
            else:
              assert page.locator('[data-fvx-record]:visible').count()==6
              assert page.locator('[data-fva-record]:visible').count()==6
              assert page.locator('[data-fva-controls]').is_hidden()
            assert not errors and not network,(width,js,forced,errors,network)
            receipt['cases'].append({'width':width,'js':js,'forced_colors':forced,'pass':True,
              'measured_controls':len(controls),
              'minimum_target_height_px':min(x['h'] for x in controls),
              'minimum_target_width_px':min(x['w'] for x in controls)})
            context.close()
      browser.close()
    (output/'R65_ALL_TARGETS_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('PASS',len(receipt['cases']),'real Chromium configurations, exhaustive interactive control dimensions')
    return receipt

if __name__=='__main__':
  ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
  run(ap.parse_args().output)
