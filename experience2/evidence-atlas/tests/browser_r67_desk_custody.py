#!/usr/bin/env python3
"""R67 Chromium acceptance: untouched R38 Desk custody and safe Atlas bridge.

Runs real PHP callbacks in the existing local WordPress-API simulator. It does
NOT claim genuine WordPress, axe-core, screen-reader or hosted CWV acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_r59_php_cohost import make_document
from playwright.sync_api import sync_playwright

WIDTHS=(320,360,390,428,768,1024,1440,1920)
FIELDS=('Photograph date','What the linked NASA photograph documents',
        'Support for the historical interpretation','Catalog and identity notes',
        'Photograph reuse')


def check_sources(page):
    assert page.locator('[data-fvx-record]').count()==6
    assert page.locator('[data-fva-record]').count()==6
    assert page.locator('[data-fva-cite-id]').count()==6
    assert page.locator('.fv-ex2-ledger__custody dd').count()==30
    assert page.locator('[data-fva-drawer] dd').count()==54
    assert page.locator('img').count()==0
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')


def run(output:Path):
    output.mkdir(parents=True,exist_ok=True)
    html,manifest=make_document()
    receipt={'schema':'fv.apollo.r67.desk-custody-browser.v1',
       'environment':'SHA-verified-R38-Desk-and-Atlas-real-PHP-in-local-WordPress-API-simulator',
       'installed_wordpress':False,'axe_core_verified':False,
       'screen_reader_tested':False,'hosted_cwv':False,
       'photograph_rights_cleared':False,'photographs_embedded':0,
       'geographic_pins':0,'crosswalk_blob':manifest['source_crosswalk_blob'],
       'responsive':[],'field_mutations':[],'structural_mutations':[],
       'screenshots':{},'local_lcp_cls':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in WIDTHS:
            print('width',width,flush=True)
            for js in (False,True):
                for forced in ((False,True) if width in (390,1440) else (False,)):
                    ctx=browser.new_context(viewport={'width':width,'height':880},
                      java_script_enabled=js,forced_colors='active' if forced else 'none',
                      reduced_motion='reduce',is_mobile=width<=390,has_touch=width<=390)
                    page=ctx.new_page();errors=[];network=[]
                    page.on('pageerror',lambda e:errors.append(str(e)))
                    page.on('request',lambda req:network.append(req.url))
                    page.set_content(html);check_sources(page)
                    assert not errors and not network,(width,js,forced,errors,network)
                    if js:
                        assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')=='yes'
                        assert page.locator('[data-fva-to-desk]:visible').count()==6
                        assert page.locator('[data-fvx-to-atlas]').count()==6
                        page.locator('input[data-fvx-search]').fill('S67-19766')
                        assert page.locator('[data-fvx-record]:visible').count()==1
                        if width==390 and not forced:page.locator('[data-fva-to-desk]').nth(3).tap()
                        elif width==1440 and not forced:page.locator('[data-fva-to-desk]').nth(3).click()
                        else:page.locator('[data-fva-to-desk]').nth(3).dispatch_event('click')
                        page.wait_for_timeout(20)
                        assert page.locator('[data-fvx-record]:visible').count()==6
                        assert page.evaluate('document.activeElement.id')=='fv-ex2-ledger-apollo1-record-04'
                        page.locator('input[data-fvx-search]').fill('S67-19766')
                        if not forced and width in (390,1440):
                            page.evaluate("document.documentElement.style.setProperty('font-size','200%','important')")
                            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                            page.evaluate("document.documentElement.style.removeProperty('font-size')")
                        if width==1440 and not forced:
                            page.locator('[data-fva-to-desk]').nth(1).focus()
                            page.keyboard.press('Enter')
                            page.wait_for_timeout(20)
                            assert page.evaluate('document.activeElement.id')=='fv-ex2-ledger-apollo1-record-02'
                    else:
                        assert page.locator('[data-fva-to-desk]:visible').count()==0
                        assert page.locator('[data-fvx-record]:visible').count()==6
                    if width in (320,390,1440,1920):page.emulate_media(media='print')
                    if width in (320,390,1440,1920):assert page.locator('[data-fvx-record]:visible').count()==6
                    if width in (320,390,1440,1920):
                        assert page.locator('.fv-ex2-ledger__custody dd:visible').count()==30
                        assert page.locator('[data-fva-record]:visible').count()==6
                        assert page.locator('[data-fva-drawer] dd:visible').count()==54
                        page.emulate_media(media='screen')
                    assert not errors and not network,(width,js,forced,errors,network)
                    if js and not forced and width in (390,1440):
                        page.locator('input[data-fvx-search]').fill('')
                        page.wait_for_timeout(180)
                        png=page.screenshot(full_page=True,animations='disabled')
                        assert png==page.screenshot(full_page=True,animations='disabled')
                        name=f'R67_DESK_CUSTODY_{width}.png'
                        (output/name).write_bytes(png)
                        receipt['screenshots'][name]=hashlib.sha256(png).hexdigest()
                        receipt['local_lcp_cls'].append({'width':width,
                          **page.evaluate('window.__fv_r53_lab||{}')})
                    receipt['responsive'].append({'width':width,'js':js,
                      'forced_colors':forced,'reduced_motion':True,'pass':True})
                    ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':880},
          reduced_motion='reduce',is_mobile=True,has_touch=True)
        page=ctx.new_page();errors=[];network=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda req:network.append(req.url))
        for i in range(6):
            for j in range(5):
                print('mutation',i,j,flush=True)
                page.set_content(html);check_sources(page)
                assert page.locator('[data-fva-to-desk]:visible').count()==6
                page.locator('.fv-ex2-ledger__custody').nth(i).locator('dd').nth(j).evaluate(
                    "e=>e.textContent='UNREVIEWED EDITORIAL ALTERATION'")
                page.locator('[data-fva-to-desk]').first.dispatch_event('click')
                assert page.locator('[data-fva-to-desk]:visible').count()==0,(i,j)
                assert page.locator('[data-fvx-to-atlas]').count()==0,(i,j)
                assert page.locator('[data-fva-desk-status]:visible').count()==1
                assert page.locator('[data-fva-record]:visible').count()==6
                assert page.locator('[data-fvx-record]:visible').count()==6
                assert page.locator('[data-fva-cite-id]').count()==6
                receipt['field_mutations'].append({'record_id':f'{i+1:02d}',
                   'field':FIELDS[j],'shortcuts_withdrawn':True,'native_sources_preserved':True})
        for original,replacement in (
            ('<dt>Photograph reuse</dt>','<dt>Photograph license cleared</dt>'),
            ('data-fvx-photo-record="01"','data-fvx-photo-record="99"'),
            ('<dd>January 3, 1967</dd>','<dd>January 3, 1968</dd>'),
            ('<dt>Photograph date</dt>','<dt>Photograph dat</dt>')):
            assert original in html
            page.set_content(html.replace(original,replacement,1));check_sources(page)
            assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')=='yes'
            assert page.locator('[data-fva-to-desk]:visible').count()==0,original
            assert page.locator('[data-fvx-to-atlas]').count()==0
            receipt['structural_mutations'].append({'original':original,'shortcuts_withdrawn':True})
        assert not errors and not network,(errors,network)
        ctx.close();browser.close()
    (output/'R67_DESK_CUSTODY_BROWSER_RECEIPT.json').write_text(
        json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('PASS',len(receipt['responsive']),'responsive configurations,',
         len(receipt['field_mutations']),'custody edits,',
         len(receipt['structural_mutations']),'pre-init edits')
    return receipt

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
    run(ap.parse_args().output)
