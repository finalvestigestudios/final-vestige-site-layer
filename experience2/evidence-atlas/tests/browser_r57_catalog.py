#!/usr/bin/env python3
"""Real R37/R55 source-built NASA-page catalog facet, 8 widths x JS on/off; NOT WordPress or axe-core."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parent))
from browser_r54_real_atlas import document
SIZES=(320,360,390,428,768,1024,1440,1920)

def run(folder:Path):
    folder.mkdir(parents=True,exist_ok=True)
    html,manifest=document()
    monitor="""<script>window.__r57={lcp_ms:null,cls:0};try{
      new PerformanceObserver(o=>o.getEntries().forEach(e=>window.__r57.lcp_ms=e.startTime))
        .observe({type:'largest-contentful-paint',buffered:true});
      new PerformanceObserver(o=>o.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__r57.cls+=e.value;}))
        .observe({type:'layout-shift',buffered:true});
    }catch(e){window.__r57.error=String(e)}</script>"""
    html=html.replace('<head>','<head>'+monitor,1)
    result={'schema':'fv.ex2.apollo.r57.custody.browser.v1','release':'STAGING_HOLD',
        'scope':'ACTUAL_R37_R55_SOURCE_BUILT_ATLAS_NOT_WORDPRESS',
        'r37_crosswalk_blob':manifest['source_crosswalk_blob'],
        'axe':'NOT_EXECUTED','screen_reader':'NOT_EXECUTED','hosted_cwv':'NOT_MEASURED',
        'r38_research_desk':'NOT_EXECUTED_ORIGINAL_ASSETS_ABSENT',
        'cases':[],'screenshots':{},'local_fragment_metrics':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in SIZES:
            for enabled in (False,True):
                ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,
                    reduced_motion='reduce',has_touch=width<=390,is_mobile=width<=390)
                page=ctx.new_page();errors=[];requests=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('request',lambda r:requests.append(r.url))
                page.set_content(html);page.wait_for_timeout(100)
                assert not errors and not requests,(width,enabled,errors,requests)
                assert page.locator('[data-fva-record]:visible').count()==6
                assert page.locator('[data-fva-custody-status]:visible').count()==1
                assert page.locator('[data-fva-catalog-status]').count()==6
                assert page.locator('[data-fva-catalog-unconfirmed]:visible').count()==1
                assert page.locator('[data-fva-atlas] img,[data-fva-atlas] iframe').count()==0
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),width
                page.locator('[data-fva-drawer] summary').first.focus()
                page.keyboard.press('Enter')
                assert page.locator('[data-fva-drawer]').first.evaluate('(e)=>e.open')
                assert page.locator('[data-fva-drawer]').first.locator('dd[data-fva-catalog-status]').is_visible()
                assert 'provisional' in page.locator('[data-fva-drawer]').first.locator('[data-fva-catalog-status]').inner_text()
                assert page.evaluate('document.activeElement.tagName')=='SUMMARY'
                assert page.locator('[data-fva-catalog-state="provisional"]').count()==1
                assert page.locator('[data-fva-catalog-state="page-displayed"]').count()==5
                assert page.locator('[data-fva-proof-filter]').count()==3
                if enabled:
                    proof=page.locator('[data-fva-proof-filter="provisional"]')
                    proof.tap() if width<=390 else proof.click()
                    assert page.locator('[data-fva-record]:visible').count()==1
                    assert page.locator('[data-fva-cite-id]:visible').count()==6
                    assert proof.get_attribute('aria-pressed')=='true'
                    page.locator('[data-fva-proof-filter="page-displayed"]').click()
                    assert page.locator('[data-fva-record]:visible').count()==5
                    page.locator('[data-fva-proof-filter="provisional"]').click()
                    page.locator('[data-fva-filter="2017"]').click()
                    assert page.locator('[data-fva-record]:visible').count()==0
                    assert page.locator('[data-fva-empty]').is_visible()
                    page.locator('[data-fva-reset]').click()
                    assert page.locator('[data-fva-record]:visible').count()==6
                    assert page.locator('[data-fva-proof-filter="all"]').get_attribute('aria-pressed')=='true'
                    page.locator('[data-fva-filter="2017"]').click()
                    assert page.locator('[data-fva-record]:visible').count()==2
                    assert page.locator('[data-fva-custody-status]:visible').count()==1
                else:
                    assert page.locator('[data-fva-controls]').is_hidden()
                page.emulate_media(media='print')
                assert page.locator('[data-fva-record]:visible').count()==6
                assert page.locator('[data-fva-drawer] dl:visible').count()==6
                assert page.locator('[data-fva-custody-status]:visible').count()==1
                page.emulate_media(media='screen')
                if enabled:
                    assert page.locator('[data-fva-record]:visible').count()==2
                    # Jump from the static index to a filtered source. Must restore
                    # all six without losing the newly disclosed source status.
                    link=page.locator('[data-fva-jump]').first
                    link.tap() if width<=390 else link.click()
                    page.wait_for_timeout(65)
                    assert page.locator('[data-fva-record]:visible').count()==6
                    assert page.evaluate('document.activeElement.id')=='fva-record-01'
                    # Proof filter must also release a hidden source on native jump.
                    page.locator('[data-fva-proof-filter="page-displayed"]').click()
                    assert page.locator('[data-fva-record]:visible').count()==5
                    page.locator('[data-fva-jump]').first.click()
                    page.wait_for_timeout(65)
                    assert page.locator('[data-fva-record]:visible').count()==6
                    assert page.locator('[data-fva-proof-filter="all"]').get_attribute('aria-pressed')=='true'
                    # Print must not inherit proof filtering and omit any references.
                    page.locator('[data-fva-proof-filter="provisional"]').click()
                    page.emulate_media(media='print')
                    assert page.locator('[data-fva-record]:visible').count()==6
                    assert page.locator('[data-fva-drawer] dl:visible').count()==6
                    page.emulate_media(media='screen')
                    page.locator('[data-fva-reset]').click()
                    result['local_fragment_metrics'].append({'width':width,**page.evaluate('window.__r57')})
                    if width in (390,1440):
                        page.wait_for_timeout(200)
                        page.evaluate('window.scrollTo(0, 0)')
                        page.wait_for_timeout(100)
                        data=page.screenshot(full_page=True,animations='disabled')
                        assert data==page.screenshot(full_page=True,animations='disabled')
                        name=f'r57-custody-{width}.png'
                        (folder/name).write_bytes(data)
                        result['screenshots'][name]=hashlib.sha256(data).hexdigest()
                result['cases'].append({'width':width,'javascript':enabled,'pass':True,
                    'six_drawers':True,'print_full_custody':True,'no_external_requests':True})
                ctx.close()
        browser.close()
    receipt=folder/'R57_CUSTODY_BROWSER_RECEIPT.json'
    receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS',len(result['cases']),'real-source R57 custody UI browser combinations')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
