#!/usr/bin/env python3
"""R51 real-Chromium provenance-disclosure QA, PHP-assembled Atlas + synthetic Desk.

Does NOT assert genuine WordPress or original PR158 HTML/CSS integration.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_r50_suite import make_document

WIDTHS=(320,360,390,428,768,1024,1440,1920)
NOTICE='Catalog-to-photograph identity remains unconfirmed pending archival review.'

def run(output:Path):
    output.mkdir(parents=True,exist_ok=True)
    receipt={'schema':'fv.ex2.apollo.r51.provenance-browser.v1','release':'STAGING_HOLD',
        'source':'PINNED_R37_FILENAME_ASSOCIATION_NOT_PRIMARY_CATALOG_PROOF',
        'desk_html':'SYNTHETIC_PR158_CONTRACT_NOT_ORIGINAL','atlas_markup':'ACTUAL_PHP_ASSEMBLED',
        'browser':'CHROMIUM_SET_CONTENT_NOT_WORDPRESS_OR_HTTP',
        'axe':'NOT_EXECUTED_NO_VERIFIED_LOCAL_BUNDLE', 'hosted_cwv':'NOT_MEASURED',
        'checks':[], 'screenshots':{},'component_lab_metrics':[]}
    html=make_document()
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (False,True):
                ctx=browser.new_context(viewport={'width':width,'height':900},
                    java_script_enabled=js,has_touch=width<=390,is_mobile=width<=390,
                    reduced_motion='reduce',accept_downloads=True)
                pg=ctx.new_page(); errors=[];requests=[]
                pg.on('pageerror',lambda error:errors.append(str(error)))
                pg.on('request',lambda req:requests.append(req.url))
                pg.set_content(html)
                assert not errors and not requests,(width,js,errors,requests)
                assert not pg.evaluate('document.documentElement.scrollWidth>innerWidth+2'),width
                first=pg.locator('[data-fva-record]').first
                assert first.locator('[data-fva-catalog-unconfirmed]').count()==1
                assert NOTICE in first.locator('[data-fva-catalog-unconfirmed]').inner_text()
                assert pg.locator('[data-fva-catalog-unconfirmed]').count()==1
                assert pg.locator('.fv-ex2-apollo-suite__provenance').count()==1
                assert pg.locator('.fva-provenance-note').count()==1
                assert NOTICE in pg.locator('[data-fva-cite-id="01"] [data-fva-citation-text]').inner_text()
                assert pg.locator('[data-fva-cite-id]:visible').count()==6
                assert pg.locator('[data-fva-record]:visible').count()==6
                assert pg.locator('.fv-ex2-apollo-suite__provenance').is_visible()
                assert pg.locator('.fva-provenance-note').is_visible()
                assert pg.locator('[data-fva-record]').first.locator('a.fva-card__external').get_attribute('href')=='https://www.nasa.gov/image-detail/apollo-1-crew-honored/'
                if js:
                    pg.locator('[data-fva-filter="2017"]').click()
                    assert pg.locator('[data-fva-record]:visible').count()==2
                    assert pg.locator('[data-fva-cite-id]:visible').count()==6
                    with pg.expect_download() as event:
                        pg.locator('[data-fva-export]').click()
                    data=event.value.path().read_bytes()
                    content=data.decode('utf-8-sig')
                    assert NOTICE in content,(width,'provenance missing in download')
                    assert content.count('image reuse: individual review required.')==6,(width,'incomplete register')
                    assert content.count('Catalog-to-photograph identity remains unconfirmed')==1
                    pg.locator('[data-fva-reset]').click()
                    assert first.locator('[data-fva-catalog-unconfirmed]').is_visible()
                    if width in (390,1440):
                        pg.locator('[data-fva-record]').first.locator('[data-fva-drawer]').evaluate('(el)=>el.open=true')
                        screenshot=pg.screenshot(full_page=True,animations='disabled')
                        assert screenshot==pg.screenshot(full_page=True,animations='disabled')
                        fn=output/f'r51-{width}-provenance.png';fn.write_bytes(screenshot)
                        receipt['screenshots'][str(width)]={'filename':fn.name,'bytes':len(screenshot),
                            'sha256':hashlib.sha256(screenshot).hexdigest()}
                    receipt['component_lab_metrics'].append({'width':width,'cls':'NOT_MEASURED_FOR_R51',
                        'lcp':'NOT_MEASURED_FOR_R51','scope':'SET_CONTENT_BROWSER'})
                receipt['checks'].append({'viewport':width,'javascript':js,'pass':True})
                ctx.close()
        browser.close()
    (output/'R51_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('PASS',len(receipt['checks']),'R51 Chromium provenance, export, no-JS, touch-width QA')
    return receipt
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True)
    run(a.parse_args().output)
