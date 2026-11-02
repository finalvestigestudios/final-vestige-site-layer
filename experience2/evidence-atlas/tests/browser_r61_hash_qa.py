#!/usr/bin/env python3
"""R61 Playwright regression: original SHA-pinned R38 + Atlas PHP cohost, not real WP."""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_r59_php_cohost import make_document

WIDTHS=(320,360,390,428,768,1024,1440,1920)

def run(output):
    output.mkdir(parents=True,exist_ok=True)
    html,source=make_document()  # exact five R38 files, compiled NASA Atlas, PHP APIs
    rows=[]; shots={}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (False,True):
                context=browser.new_context(viewport={'width':width,'height':900},
                    java_script_enabled=js,reduced_motion='reduce',
                    is_mobile=width<=390,has_touch=width<=390)
                page=context.new_page();errors=[];network=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('request',lambda r:network.append(r.url))
                page.set_content(html)
                assert page.locator('[data-fvx-record]').count()==6
                assert page.locator('[data-fva-record]').count()==6
                assert page.locator('[data-fva-cite-id]').count()==6
                assert page.locator('.fv-ex2-apollo-suite img').count()==0
                if js:
                    query=page.locator('input[data-fvx-search]')
                    query.fill('S67-19766')
                    assert page.locator('[data-fvx-record]:visible').count()==1
                    page.evaluate('location.hash="#fv-ex2-ledger-apollo1-record-05"')
                    page.wait_for_function('document.activeElement?.id==="fv-ex2-ledger-apollo1-record-05"')
                    assert query.input_value()==''
                    assert page.locator('[data-fvx-record]:visible').count()==6
                    page.locator('[data-fva-filter="2017"]').click()
                    assert page.locator('[data-fva-record]:visible').count()==2
                    page.evaluate('location.hash="#fva-record-03"')
                    page.wait_for_function('document.activeElement?.id==="fva-record-03"')
                    assert page.locator('[data-fva-record]:visible').count()==6
                    page.evaluate('history.back()')
                    page.wait_for_function('location.hash==="#fv-ex2-ledger-apollo1-record-05"')
                    assert page.locator('#fv-ex2-ledger-apollo1-record-05').is_visible()
                    query.fill('S67-19766')
                    page.emulate_media(media='print')
                    assert page.locator('[data-fvx-record]:visible').count()==6
                    assert page.locator('.fv-ex2-ledger__custody dd:visible').count()==30
                    assert page.locator('[data-fva-drawer] dd:visible').count()==54
                    page.emulate_media(media='screen');query.fill('')
                else:
                    page.evaluate('location.hash="#fv-ex2-ledger-apollo1-record-05"')
                    assert page.locator('#fv-ex2-ledger-apollo1-record-05').is_visible()
                    assert page.locator('[data-fvx-record]:visible').count()==6
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                assert not errors and not network,(width,js,errors,network)
                if js and width in (390,1440):
                    page.wait_for_timeout(160)
                    png=page.screenshot(full_page=True,animations='disabled')
                    assert png==page.screenshot(full_page=True,animations='disabled')
                    name=f'r61-source-history-{width}.png'
                    (output/name).write_bytes(png)
                    shots[name]=hashlib.sha256(png).hexdigest()
                rows.append({'width':width,'js':js,'passed':True})
                context.close()
        browser.close()
    receipt={'schema':'fv.apollo.r61.history.v1','release':'STAGING_HOLD',
        'source_crosswalk_blob':source['source_crosswalk_blob'],
        'wordPress':'SIMULATED_NOT_INSTALLED','axe':'NOT_EXECUTED_NO_VERIFIED_BUNDLE',
        'hosted_cwv':'NOT_MEASURED','screenshots':shots,'cases':rows}
    (output/'R61_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('PASS',len(rows),'original-R38+Atlas Chromium cases; exact original PHP API simulator')
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
