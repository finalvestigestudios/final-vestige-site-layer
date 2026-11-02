#!/usr/bin/env python3
"""R62 source-date adversarial browser acceptance against exact R38 + PHP Atlas.

Uses real original SHA-pinned Research Desk PHP files and reviewed generated Atlas
through a deterministic WordPress API simulator; NOT an installed WordPress site.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_r59_php_cohost import make_document

WIDTHS=(320,360,390,428,768,1024,1440,1920)
YEAR_FORGERY='''() => {
  const first=document.querySelector('[data-fva-record][data-fva-id="01"]');
  const link=document.querySelector('[data-fva-time-id="01"]');
  const destination=document.querySelector('[data-fva-era="1966"] ol');
  if(!first||!link||!destination)throw new Error('Unreviewed DOM structure');
  first.dataset.fvaYear='1966';
  destination.appendChild(link.closest('li'));
}'''
DATE_FORGERY='''() => {
  const card=document.querySelector('[data-fva-record][data-fva-id="02"]');
  const time=document.querySelector('[data-fva-time-id="02"] time');
  const cite=document.querySelector('[data-fva-cite-id="02"] [data-fva-citation-text]');
  if(!card||!time||!cite)throw new Error('Unreviewed DOM structure');
  card.querySelector('.fva-card__date span').textContent='January 4, 1967';
  time.textContent='January 4, 1967';
  time.setAttribute('datetime','1967-01-04');
  cite.textContent=cite.textContent.replaceAll('January 3, 1967','January 4, 1967');
}'''

def check_no_enhancement(page):
    assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')!='yes'
    assert page.locator('[data-fva-controls]').is_hidden()
    assert page.locator('[data-fva-record]:visible').count()==6
    assert page.locator('[data-fva-cite-id]').count()==6
    assert page.locator('img').count()==0

def run(output:Path):
    output.mkdir(parents=True,exist_ok=True)
    html,source=make_document()
    receipt={'schema':'fv.apollo.r62.date-identity-browser.v1',
      'release':'STAGING_HOLD','wordpress':'SIMULATED_NOT_INSTALLED',
      'axe':'NOT_EXECUTED_NO_VERIFIED_OFFLINE_BUNDLE',
      'hosted_cwv':'NOT_MEASURED','source_crosswalk_blob':source['source_crosswalk_blob'],
      'screenshots':{},'cases':[],'adversarial_gate_cases':[],'lab_fragment_metrics':[]}
    with sync_playwright() as p:
      browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
      for width in WIDTHS:
       for js in (False,True):
        context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
          reduced_motion='reduce',has_touch=width<=390,is_mobile=width<=390)
        page=context.new_page();errors=[];network=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        page.on('request',lambda req:network.append(req.url))
        page.set_content(html)
        assert page.locator('[data-fvx-record]').count()==6
        assert page.locator('[data-fva-record]').count()==6
        assert page.locator('[data-fva-timejump]').count()==6
        assert page.locator('img').count()==0
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),(width,js)
        if js:
          # Reviewed source years and provenance filters retain correct pairing.
          page.locator('[data-fva-filter="1967"]').click()
          assert page.locator('[data-fva-record]:visible').count()==3
          page.locator('[data-fva-proof-filter="provisional"]').click()
          assert page.locator('[data-fva-record]:visible').count()==1
          page.locator('[data-fva-reset]').click()
          assert page.locator('[data-fva-record]:visible').count()==6
          # Two mutually consistent HTML edits previously bypassed chronology checks.
          page.evaluate(YEAR_FORGERY)
          page.locator('[data-fva-filter="1966"]').click()
          check_no_enhancement(page)
          receipt['adversarial_gate_cases'].append({'width':width,'mutation':'coordinated-year-and-era-forgery','blocked':True})
          page.set_content(html)
          page.evaluate(DATE_FORGERY)
          page.locator('[data-fva-filter="1967"]').click()
          check_no_enhancement(page)
          receipt['adversarial_gate_cases'].append({'width':width,'mutation':'coordinated-date-caption-time-and-citation-forgery','blocked':True})
          page.set_content(html)
          page.evaluate(DATE_FORGERY)
          page.evaluate('location.hash="#fva-record-02"')
          page.wait_for_function("document.querySelector('[data-fva-atlas]').dataset.fvaReady!== 'yes'")
          check_no_enhancement(page)
          receipt['adversarial_gate_cases'].append({'width':width,'mutation':'visible-record-hash-after-date-forgery','blocked':True})
          page.set_content(html)
          assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')=='yes'
          page.locator('input[data-fvx-search]').fill('S67-19766')
          page.locator('[data-fva-filter="2017"]').click()
          page.emulate_media(media='print')
          assert page.locator('[data-fvx-record]:visible').count()==6
          assert page.locator('.fv-ex2-ledger__custody dd:visible').count()==30
          assert page.locator('[data-fva-record]:visible').count()==6
          assert page.locator('[data-fva-drawer] dd:visible').count()==54
          page.emulate_media(media='screen')
          if width in (390,1440):
            page.locator('[data-fva-reset]').click()
            page.locator('input[data-fvx-search]').fill('')
            page.wait_for_timeout(170)
            png=page.screenshot(full_page=True,animations='disabled')
            assert png==page.screenshot(full_page=True,animations='disabled')
            name=f'r62-date-identity-{width}.png'
            (output/name).write_bytes(png)
            receipt['screenshots'][name]=hashlib.sha256(png).hexdigest()
          receipt['lab_fragment_metrics'].append({'width':width,**page.evaluate('window.__fv_r53_lab||{}')})
        else:
          assert page.locator('[data-fvx-record]:visible').count()==6
          assert page.locator('[data-fva-record]:visible').count()==6
          assert page.locator('[data-fva-drawer]').count()==6
          assert page.locator('[data-fva-chronology]').count()==1
          page.emulate_media(media='print')
          assert page.locator('[data-fvx-record]:visible').count()==6
          assert page.locator('[data-fva-record]:visible').count()==6
          page.emulate_media(media='screen')
        assert not network and not errors,(width,js,network,errors)
        receipt['cases'].append({'width':width,'js':js,'passed':True})
        context.close()
      browser.close()
    (output/'R62_DATE_CUSTODY_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('PASS',len(receipt['cases']),'exact-source Chromium cases; 24 adversarial date/year/history gates')
    return receipt

if __name__=='__main__':
  parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
  run(parser.parse_args().output)
