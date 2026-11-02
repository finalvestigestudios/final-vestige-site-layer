#!/usr/bin/env python3
"""R70: executable visitor journeys on original R38 + source-built Atlas PHP.

Component-level real Chromium/Playwright, **not** installed WordPress or
screen-reader certification. No public network access, image binaries, pins,
CMS writes, or supposed photo-rights clearance. Run from an exact source tree.
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
NASA_URLS=(
 'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
 'https://www.nasa.gov/image-detail/amf-s67-15717/',
 'https://www.nasa.gov/image-detail/amf-s66-58038/',
 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
 'https://www.nasa.gov/image-detail/amf-s67-21294/',
 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
)

def source_assertions(page):
    assert page.locator('[data-fvx-record]').count()==6
    assert page.locator('[data-fva-record]').count()==6
    assert page.locator('[data-fva-cite-id]').count()==6
    assert page.locator('.fv-ex2-ledger__custody dd').count()==30
    assert page.locator('[data-fva-drawer] dd').count()==54
    assert page.locator('.fv-ex2-apollo-suite img').count()==0
    assert page.locator('.fv-ex2-apollo-suite [data-lat],[data-lon],[data-geo-edge]').count()==0
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
    assert [e.get_attribute('href') for e in page.locator('.fva-card__external').all()]==list(NASA_URLS)

def activate(locator,width):
    (locator.tap() if width<=390 else locator.click())

def keyboard_drawer(page):
    summary=page.locator('[data-fva-drawer] summary').first
    summary.focus()
    assert summary.evaluate('e=>document.activeElement===e')
    before=summary.evaluate('e=>e.parentElement.open')
    page.keyboard.press('Enter')
    assert summary.evaluate('e=>e.parentElement.open')!=before
    page.keyboard.press('Enter')
    assert summary.evaluate('e=>e.parentElement.open')==before

def exercise(page,width,out,receipt,axe_js=None):
    source_assertions(page)
    assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')=='yes'
    # Combining independent provenance/year filters must never fabricate a hit.
    activate(page.locator('[data-fva-proof-filter="provisional"]'),width)
    assert page.locator('[data-fva-record]:visible').count()==1
    assert page.locator('[data-fva-proof-filter="provisional"]').get_attribute('aria-pressed')=='true'
    activate(page.locator('[data-fva-filter="2017"]'),width)
    assert page.locator('[data-fva-record]:visible').count()==0
    assert page.locator('[data-fva-empty]').is_visible()
    page.locator('input[data-fva-search]').fill('no-real-record-with-this-query')
    page.locator('input[data-fva-search]').press('Escape')
    assert page.locator('[data-fva-record]:visible').count()==6
    assert page.locator('[data-fva-proof-filter="all"]').get_attribute('aria-pressed')=='true'
    assert page.locator('[data-fva-filter="all"]').get_attribute('aria-pressed')=='true'
    assert page.locator('input[data-fva-search]').input_value()==''
    keyboard_drawer(page)
    # Metadata-only comparison cannot imply that two images are the same event.
    activate(page.locator('[data-fva-select="01"]'),width)
    activate(page.locator('[data-fva-select="04"]'),width)
    assert page.locator('[data-fva-compare-slot] h3').count()==2
    assert 'not evidence of a historical connection' in page.locator('[data-fva-compare-status]').inner_text()
    assert page.locator('[data-fva-select="01"]').get_attribute('aria-pressed')=='true'
    activate(page.locator('[data-fva-compare-clear]'),width)
    assert page.locator('[data-fva-compare-slot] h3').count()==0
    assert page.locator('[data-fva-select="01"]').get_attribute('aria-pressed')=='false'
    # Source index and citation export must derive from all six original records.
    with page.expect_download() as item:
        activate(page.locator('[data-fva-export]'),width)
    download=item.value
    assert download.suggested_filename=='apollo-1-nasa-source-register.txt'
    exported=out/f'R70_SOURCE_REGISTER_{width}.txt'
    download.save_as(exported)
    content=exported.read_text(encoding='utf-8')
    assert content.count('Catalog reference:')==6
    assert content.count('Reuse status:')==6
    assert 'rights reviews are outstanding' in content
    assert 'NASA does not endorse this publication.' in content
    for url in NASA_URLS:assert url in content
    # Filtered printed document retains all original custody notes.
    page.locator('input[data-fvx-search]').fill('S67-19766')
    activate(page.locator('[data-fva-filter="2017"]'),width)
    assert page.locator('[data-fvx-record]:visible').count()==1
    assert page.locator('[data-fva-record]:visible').count()==2
    page.emulate_media(media='print')
    assert page.locator('[data-fvx-record]:visible').count()==6
    assert page.locator('[data-fva-record]:visible').count()==6
    assert page.locator('.fv-ex2-ledger__custody dd:visible').count()==30
    assert page.locator('[data-fva-drawer] dd:visible').count()==54
    page.emulate_media(media='screen')
    # Browse to a filtered-out original source: restore, focus, not blind jump.
    page.locator('[data-fva-to-desk]').nth(3).dispatch_event('click')
    page.wait_for_timeout(40)
    assert page.locator('[data-fvx-record]:visible').count()==6
    assert page.evaluate('document.activeElement.id')=='fv-ex2-ledger-apollo1-record-04'
    activate(page.locator('[data-fva-reset]'),width)
    page.locator('input[data-fvx-search]').fill('')
    if width in (390,1440):
        # A screenshot is only reproducible evidence if its bytes are stable.
        page.evaluate('''() => {if(document.activeElement instanceof HTMLElement)document.activeElement.blur(); window.scrollTo(0,0)}''')
        page.add_style_tag(content='*{caret-color:transparent!important;animation:none!important;transition:none!important}')
        page.wait_for_timeout(250)
        image=page.screenshot(full_page=True,animations='disabled')
        assert image==page.screenshot(full_page=True,animations='disabled')
        name=f'R70_EDITORIAL_JOURNEY_{width}.png'
        (out/name).write_bytes(image)
        receipt['screenshots'][name]=hashlib.sha256(image).hexdigest()
    if width in (390,1440) and axe_js:
        page.add_script_tag(content=axe_js)
        audit=page.evaluate("""async () => {
          const r=await axe.run(document.querySelector('.fv-ex2-apollo-suite'),{
            runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
          return {violations:r.violations.map(x=>({id:x.id,impact:x.impact,nodes:x.nodes.length})),passes:r.passes.length};
        }""")
        receipt['axe'].append({'width':width,**audit})
        assert not audit['violations'],audit
    lab=page.evaluate('window.__fv_r53_lab || {}')
    receipt['lab'].append({'width':width,'lcp_ms':lab.get('lcp') if isinstance(lab,dict) else None,'cls':lab.get('cls') if isinstance(lab,dict) else None,'component_not_field_cwv':True})
    exported.unlink()

def run(output:Path,axe_path:Path|None=None,axe_sha256:str|None=None):
    output.mkdir(parents=True,exist_ok=True)
    html,source=make_document()
    axe_js=None
    if axe_path is not None:
        binary=axe_path.read_bytes()
        if not axe_sha256 or hashlib.sha256(binary).hexdigest()!=axe_sha256 or len(binary)<100000:
            raise ValueError('AXE_CONTENT_SHA256_MISMATCH')
        axe_js=binary.decode('utf-8')
    receipt={'schema':'fv.apollo.r70.editorial-journeys.v1','release':'STAGING_HOLD',
      'actual_wordpress_installed':False,'verified_axe_core':False,
      'screen_reader_testing':False,'hosted_cwv':False,'rights_cleared':False,
      'nasa_image_binaries_embedded':False,'source_crosswalk_git_blob':source['source_crosswalk_blob'],
      'cases':[],'screenshots':{},'browser_errors':0,'external_requests':0,
      'axe':[],'axe_bundle_sha256_same_run_only':axe_sha256 if axe_js else None,'lab':[]}
    with sync_playwright() as playwright:
        options={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').is_file():options['executable_path']='/usr/bin/chromium'
        browser=playwright.chromium.launch(**options)
        for width in WIDTHS:
            for javascript in (False,True):
                ctx=browser.new_context(viewport={'width':width,'height':880},
                     java_script_enabled=javascript,reduced_motion='reduce',
                     forced_colors='active' if width in (390,1440) else 'none',
                     accept_downloads=True,has_touch=width<=390,is_mobile=width<=390)
                page=ctx.new_page();issues=[];requests=[]
                page.on('pageerror',lambda error:issues.append('JS_ERROR'))
                page.on('request',lambda req:requests.append('OUTBOUND_REQUEST'))
                page.set_content(html)
                source_assertions(page)
                if javascript:
                    exercise(page,width,output,receipt,axe_js)
                else:
                    assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')!='yes'
                    assert page.locator('[data-fva-controls]').is_hidden()
                    assert page.locator('[data-fvx-record]:visible').count()==6
                    assert page.locator('[data-fva-record]:visible').count()==6
                    keyboard_drawer(page)
                    page.emulate_media(media='print')
                    assert page.locator('.fv-ex2-ledger__custody dd:visible').count()==30
                    assert page.locator('[data-fva-drawer] dd:visible').count()==54
                assert not issues and not requests,(width,javascript,issues,requests)
                receipt['cases'].append({'width':width,'javascript_enabled':javascript,
                     'forced_colors':width in (390,1440),'reduced_motion':True,
                     'real_chromium':True,'pass':True})
                ctx.close()
        browser.close()
    path=output/'R70_EDITORIAL_JOURNEY_RECEIPT.json'
    path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('PASS',len(receipt['cases']),'real Chromium visitor journeys')
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--axe',type=Path);parser.add_argument('--axe-sha256')
    args=parser.parse_args()
    run(args.output,args.axe,args.axe_sha256)
