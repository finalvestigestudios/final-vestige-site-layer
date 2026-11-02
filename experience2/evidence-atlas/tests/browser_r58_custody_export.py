#!/usr/bin/env python3
"""R58 source-built actual Atlas custody export and failure QA, not WP/axe/hosted CWV."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parent))
from browser_r54_real_atlas import document
SIZES=(320,360,390,428,768,1024,1440,1920)
FIELDS=('Catalog reference','Record identity note','Catalog verification on NASA page',
        'Credit displayed by NASA','Producing center displayed by NASA',
        'NASA page last updated','Editorial source check','Reuse status','Documentary boundary')

def run(folder:Path):
    folder.mkdir(parents=True,exist_ok=True)
    html,manifest=document()
    monitor="""<script>window.__r58={lcp:null,cls:0};try{
     new PerformanceObserver(o=>o.getEntries().forEach(e=>window.__r58.lcp=e.startTime)).observe({type:'largest-contentful-paint',buffered:true});
     new PerformanceObserver(o=>o.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__r58.cls+=e.value})).observe({type:'layout-shift',buffered:true});
     }catch(e){window.__r58.error=String(e)}</script>"""
    html=html.replace('<head>','<head>'+monitor,1)
    receipt={'schema':'fv.ex2.apollo.r58.custody-export.browser.v1','status':'STAGING_HOLD',
             'scope':'ACTUAL_SOURCE_BUILT_ATLAS_LOCAL_SET_CONTENT_NOT_WORDPRESS',
             'wordpress':'NOT_TESTED','r38_research_desk':'NOT_TESTED',
             'axe':'NOT_TESTED_NO_VERIFIED_BUNDLE','screen_reader':'NOT_TESTED',
             'hosted_core_web_vitals':'NOT_TESTED',
             'r37_crosswalk_blob':manifest['source_crosswalk_blob'],
             'cases':[],'screenshots':{},'lab_metrics':[],'tampering':[]}
    with sync_playwright() as p:
      browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
      for width in SIZES:
        for enabled in (False,True):
          ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,
             reduced_motion='reduce',is_mobile=width<=390,has_touch=width<=390,accept_downloads=True)
          page=ctx.new_page();errors=[];outgoing=[]
          page.on('pageerror',lambda err:errors.append(str(err)))
          page.on('request',lambda req:outgoing.append(req.url))
          page.set_content(html);page.wait_for_timeout(85)
          assert not errors and not outgoing,(width,enabled,errors,outgoing)
          assert page.locator('[data-fva-record]:visible').count()==6
          assert page.locator('[data-fva-drawer]').count()==6
          assert page.locator('[data-fva-cite-id]').count()==6
          assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),width
          if enabled:
            page.locator('[data-fva-filter="2017"]').click()
            assert page.locator('[data-fva-record]:visible').count()==2
            with page.expect_download() as dl:
              page.locator('[data-fva-export]').click()
            data=Path(dl.value.path()).read_text()
            assert data.count('https://www.nasa.gov/image-detail/')==6
            assert data.count('Source custody disclosure (editorial metadata; NOT rights clearance):')==6
            assert all(data.count(field+':')==6 for field in FIELDS),width
            assert data.count('Individual review required. No photograph is reproduced here.')==6
            assert '0 of 6 photographs cleared' not in data
            assert 'S67-19766 has no independently verified day or confirmed catalog-to-photo match' in data
            assert 'NASA/Kim Shiflett' in data
            assert 'No producing center displayed in reviewed metadata.' in data
            assert 'human link or image-rights check' in data
            # Source index remains complete after filtering/download.
            assert page.locator('[data-fva-cite-id]:visible').count()==6
            page.emulate_media(media='print')
            assert page.locator('[data-fva-record]:visible').count()==6
            assert page.locator('[data-fva-drawer] dl:visible').count()==6
            page.emulate_media(media='screen')
            page.locator('[data-fva-reset]').click()
            if width in (390,1440):
              page.wait_for_timeout(95)
              screenshot=page.screenshot(full_page=True,animations='disabled')
              assert screenshot==page.screenshot(full_page=True,animations='disabled')
              name=f'r58-custody-{width}.png'
              (folder/name).write_bytes(screenshot)
              receipt['screenshots'][name]=hashlib.sha256(screenshot).hexdigest()
            receipt['lab_metrics'].append({'width':width,**page.evaluate('window.__r58')})
            # Tampered rights/custody text must never download a misleading packet.
            page.locator('[data-fva-drawer] dd').nth(7).evaluate("e=>e.textContent='Cleared for reuse'")
            page.locator('[data-fva-export]').click()
            assert 'Download unavailable' in page.locator('[data-fva-export-status]').inner_text()
            assert page.locator('[data-fva-record]:visible').count()==6
            receipt['tampering'].append({'width':width,'blocked':True})
          else:
            assert page.locator('[data-fva-export]').is_hidden()
            page.locator('[data-fva-drawer] summary').first.focus()
            page.keyboard.press('Enter')
            assert page.locator('[data-fva-drawer]').first.evaluate('(e)=>e.open')
            assert page.locator('[data-fva-drawer] dd:visible').count()==9
          receipt['cases'].append({'width':width,'javascript':enabled,'pass':True,'requests':0})
          ctx.close()
      browser.close()
    (folder/'R58_CUSTODY_EXPORT_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('PASS',len(receipt['cases']),'actual-source custody-export browser cases;'
          ' 8 tamper cases; no WordPress, axe, or hosted CWV claims')
    return receipt
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output',required=True,type=Path)
    run(a.parse_args().output)
