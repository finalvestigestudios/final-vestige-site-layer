#!/usr/bin/env python3
"""R54 original R37 source-built Evidence Atlas in Chromium; NO synthetic Desk or WP install.

Every record is generated from the git-blob-pinned R37 custody file. The runner
refuses to operate with a missing/changed source register. Distinguishes offline
fragment lab measurements from hosted WordPress/Core Web Vitals.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
import sys
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import build_wordpress_stage

SIZES=(320,360,390,428,768,1024,1440,1920)

def document():
    with tempfile.TemporaryDirectory() as temp:
        manifest=build_wordpress_stage.build(Path(temp))
        atlas=(Path(temp)/'fv-ex2-evidence-atlas/templates/atlas-fragment.html').read_text(encoding='utf-8')
    css=(HERE/'atlas.css').read_text(encoding='utf-8')
    js=(HERE/'atlas.js').read_text(encoding='utf-8')
    performance='''<script>
    window.__fvaR54={lcp:null,cls:0};
    try {
      new PerformanceObserver(list=>list.getEntries().forEach(e=>{window.__fvaR54.lcp=e.startTime;}))
       .observe({type:'largest-contentful-paint',buffered:true});
      new PerformanceObserver(list=>list.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__fvaR54.cls+=e.value;}))
       .observe({type:'layout-shift',buffered:true});
    }catch(e){window.__fvaR54.observer_error=String(e)}
    </script>'''
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width,initial-scale=1">'
      +performance+'<style>'+css+'</style></head><body>'+atlas+'<script>'+js+'</script></body></html>'),manifest

def run(out:Path):
    out.mkdir(parents=True,exist_ok=True)
    html,manifest=document()
    receipt={'schema':'fv.ex2.apollo.r54.real-atlas-browser.v1',
      'scope':'EXACT_R37_ATLAS_SOURCE_AND_ASSETS__NO_DESK__NOT_WORDPRESS',
      'release':'STAGING_HOLD','crosswalk_blob':manifest['source_crosswalk_blob'],
      'media_rights_unreviewed':6,'embedded_nasa_images':0,
      'geo_pins':0,'axe_core':'NOT_EXECUTED_VERIFIED_BUNDLE_UNAVAILABLE',
      'hosted_cwv':'NOT_TESTED','wordpress':'NOT_TESTED','original_r38_desk':'NOT_TESTED',
      'cases':[],'lab':[],'screenshots':{}}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in SIZES:
            for js in (False,True):
                ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                 is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce',accept_downloads=True)
                page=ctx.new_page();errors=[];outgoing=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('request',lambda req:outgoing.append(req.url))
                page.set_content(html)
                page.wait_for_timeout(90)
                assert not errors,(width,js,errors)
                assert not outgoing,(width,js,outgoing)
                assert page.locator('[data-fva-record]:visible').count()==6,(width,js,'cards')
                assert page.locator('[data-fva-cite-id]').count()==6
                assert page.locator('[data-fva-timejump]').count()==6
                assert page.locator('[data-fva-drawer]').count()==6
                assert page.locator('[data-fva-atlas] img, [data-fva-atlas] iframe').count()==0
                assert page.locator('[data-fva-catalog-unconfirmed]').count()==1
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),(width,js,'overflow')
                assert page.locator('[data-fva-atlas] h1').count()==1
                assert page.locator('[data-fva-atlas] nav').count()>=1
                # Native details and original external citations do not depend on scripts.
                page.locator('[data-fva-drawer] summary').first.focus()
                page.keyboard.press('Enter')
                assert page.locator('[data-fva-drawer]').first.evaluate('(e)=>e.open')
                page.locator('[data-fva-drawer] summary').first.press('Enter')
                if js:
                    assert page.locator('[data-fva-controls]').is_visible()
                    page.locator('[data-fva-filter="2017"]').click()
                    assert page.locator('[data-fva-record]:visible').count()==2
                    (page.locator('[data-fva-jump]').first.tap() if width<=390 else page.locator('[data-fva-jump]').first.click())
                    page.wait_for_timeout(50)
                    assert page.locator('[data-fva-record]:visible').count()==6
                    assert page.evaluate('document.activeElement.id')=='fva-record-01'
                    page.locator('[data-fva-search]').fill('UNMATCHED-999999')
                    assert page.locator('[data-fva-record]:visible').count()==0
                    page.locator('[data-fva-search]').press('Escape')
                    assert page.locator('[data-fva-record]:visible').count()==6
                    # Export always contains all records independent of filtered cards.
                    page.locator('[data-fva-filter="2017"]').click()
                    with page.expect_download() as dl:
                        page.locator('[data-fva-export]').click()
                    download=dl.value
                    assert download.suggested_filename=='apollo-1-nasa-source-register.txt'
                    data=Path(download.path()).read_text(encoding='utf-8')
                    assert all(x in data for x in ['S67-19766','S66-58038','KSC-20170124-PH_KLS01_0090','unconfirmed'])
                    assert data.count('https://www.nasa.gov/image-detail/')==6
                    page.locator('[data-fva-reset]').click()
                    page.locator('[data-fva-select="01"]').click()
                    page.locator('[data-fva-select="02"]').click()
                    assert 'Two NASA records selected' in page.locator('[data-fva-compare-status]').inner_text()
                    page.locator('[data-fva-compare-clear]').click()
                    assert 'No records selected' in page.locator('[data-fva-compare-status]').inner_text()
                    receipt['lab'].append({'width':width,**page.evaluate('window.__fvaR54'),
                                          'scope':'SET_CONTENT_FRAGMENTS_NOT_HOSTED'})
                    if width in (390,1440):
                        # Independent screenshot bytes on identical, static viewport.
                        shot=page.screenshot(full_page=True,animations='disabled')
                        again=page.screenshot(full_page=True,animations='disabled')
                        assert shot==again,(width,'unstable screenshot')
                        name=f'r54-atlas-real-{width}.png'
                        (out/name).write_bytes(shot)
                        receipt['screenshots'][name]=hashlib.sha256(shot).hexdigest()
                    # Late DOM mutation must disable enhancements and restore all records.
                    page.locator('.fva-card__external').first.evaluate("(e)=>e.setAttribute('href','https://invalid.test/fake')")
                    page.locator('[data-fva-filter="2017"]').click()
                    assert page.locator('[data-fva-record]:visible').count()==6
                    assert page.locator('[data-fva-controls]').is_hidden()
                    assert page.locator('[data-fva-export]').is_hidden()
                else:
                    assert page.locator('[data-fva-controls]').is_hidden()
                    assert page.locator('[data-fva-record]').count()==6
                    assert page.locator('[data-fva-export]').is_hidden()
                # Browser print emulation cannot remove source links or source warnings.
                page.emulate_media(media='print')
                assert page.locator('[data-fva-cite-id]').count()==6
                assert page.locator('[data-fva-catalog-unconfirmed]').count()==1
                receipt['cases'].append({'viewport':width,'js':js,'passed':True,
                                         'print_citations':6,'no_external_requests':True})
                ctx.close()
        browser.close()
    (out/'R54_REAL_ATLAS_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('PASS',len(receipt['cases']),'exact-R37 Atlas browser viewport/mode cases')
    return receipt

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True)
    run(a.parse_args().output)
