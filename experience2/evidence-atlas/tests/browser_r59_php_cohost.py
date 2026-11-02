#!/usr/bin/env python3
"""R59 exact-source R38 Desk + Atlas PHP shortcode and Chromium acceptance (NOT WordPress).

Requires a COMPLETE repo checkout containing experience2/research-desk; the
standalone R52/R53 ZIP deliberately does not include its original files.
Fails with code 2 if unavailable: never substitutes synthetic Desk markup.
"""
from __future__ import annotations
import argparse
import os
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parents[1]
DESK = HERE.parent / 'research-desk'
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE/'tests'))
import build_wordpress_stage
from test_desk_profiles_r52 import EXPECTED,blob


def make_document():
    profile = EXPECTED['r38-custody-search']
    missing = [x for x in profile if not (DESK/x).is_file()]
    if missing:
        raise FileNotFoundError('REAL R38 SOURCE ABSENT: ' + ', '.join(missing))
    for file,expected in profile.items():
        actual=blob((DESK/file).read_bytes())
        if actual != expected:
            raise ValueError(f'EXACT R38 SOURCE DRIFT: {file}: {actual} != {expected}')
    with tempfile.TemporaryDirectory() as tmp:
        stage=Path(tmp)
        manifest=build_wordpress_stage.build(stage)
        atlas=(stage/'fv-ex2-evidence-atlas/templates/atlas-fragment.html').read_text()
        env=dict(os.environ,FV_R59_DESK_ROOT=str(DESK),FV_R59_ATLAS_ROOT=str(stage/'fv-ex2-evidence-atlas'))
        probe_path=str(HERE/'tests/php_real_cohost_r59.php')
        reports={}
        for mode in ('nested','top-level','not-allowed','non-singular'):
            report=json.loads(subprocess.run(['php',probe_path,mode],env=env,
                capture_output=True,text=True,check=True).stdout)
            assert report['original_r38_pinned'] and report['built_atlas_pinned']
            assert report['suite_rendered'] and report['desk_records']==6 and report['atlas_records']==6
            if mode in ('nested','top-level'):
                assert len(report['prehead_styles'])==3 and len(report['prehead_scripts'])==2
            elif mode=='not-allowed':
                assert report['prehead_styles']==['fv-ex2-research-desk']
            else:
                assert report['prehead_styles']==[] and report['prehead_scripts']==[]
            reports[mode]=report
        suite=subprocess.run(['php',probe_path,'nested','--html'],env=env,
            capture_output=True,text=True,check=True).stdout
        assert hashlib.sha256(suite.encode()).hexdigest()==reports['nested']['markup_sha256']
    styles='\n'.join([
        (DESK/'assets/source-ledger.css').read_text(),
        (HERE/'atlas.css').read_text(),
        (HERE/'integration/apollo-suite.css').read_text()])
    scripts='\n'.join([
        (DESK/'assets/source-ledger.js').read_text(),
        (HERE/'atlas.js').read_text()])
    pre='''<script>window.__fv_r53_lab={lcp:null,cls:0};try{
      new PerformanceObserver(a=>a.getEntries().forEach(e=>window.__fv_r53_lab.lcp=e.startTime))
        .observe({type:'largest-contentful-paint',buffered:true});
      new PerformanceObserver(a=>a.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__fv_r53_lab.cls+=e.value}))
        .observe({type:'layout-shift',buffered:true});
    }catch(e){window.__fv_r53_lab.error=String(e)}</script>'''
    html=('<!doctype html><html lang="en"><head><meta charset="utf-8">'
          '<meta name="viewport" content="width=device-width,initial-scale=1">'
          +pre+'<style>'+styles+'</style></head><body>'+suite+'<script>'+scripts+'</script></body></html>')
    return html,manifest


def run(output:Path,axe_path:Path|None=None,axe_sha256:str|None=None):
    html,manifest=make_document()
    output.mkdir(parents=True,exist_ok=True)
    if axe_path and (not axe_sha256 or hashlib.sha256(axe_path.read_bytes()).hexdigest()!=axe_sha256):
        raise ValueError('axe-core local bundle SHA-256 must be supplied and must match')
    receipt={'schema':'fv.ex2.r59.original-php-cohost-browser.v1','scope':'ORIGINAL_R38_PHP_SHORTCODE_AND_SOURCE_BUILT_ATLAS_PHP_IN_CLI_WP_MOCK_NOT_INSTALLED_WORDPRESS',
      'release':'STAGING_HOLD','hosted_cwv':'NOT_TESTED','wordPress':'NOT_TESTED',
      'axe':'NOT_EXECUTED_NO_VERIFIED_LOCAL_BUNDLE' if axe_path is None else 'RUN',
      'r38_pins':EXPECTED['r38-custody-search'],'atlas_crosswalk':manifest['source_crosswalk_blob'],
      'screenshots':{},'tests':[],'lab_metrics':[],'print_regressions':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for w in (320,360,390,428,768,1024,1440,1920):
            for js in (False,True):
                context=browser.new_context(viewport={'width':w,'height':900},
                    java_script_enabled=js,reduced_motion='reduce',
                    is_mobile=w<=390,has_touch=w<=390)
                page=context.new_page(); errors=[]; outgoing=[]
                page.on('pageerror',lambda error: errors.append(str(error)))
                page.on('request',lambda request: outgoing.append(request.url))
                page.set_content(html)
                page.wait_for_timeout(70)
                assert not errors,(w,js,errors)
                assert not outgoing,(w,js,outgoing)
                assert page.locator('[data-fvx-record]:visible').count()==6,(w,js,'Desk')
                assert page.locator('[data-fva-record]:visible').count()==6,(w,js,'Atlas')
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),w
                assert page.locator('#fv-ex2-ledger-apollo1-title').count()==1
                assert page.locator('#fva-title').count()==1
                assert page.locator('.fv-ex2-apollo-suite__provenance').count()==1
                if js:
                    page.locator('input[data-fvx-search]').fill('S67-19766')
                    assert page.locator('[data-fvx-record]:visible').count()==1
                    page.locator('[data-fva-to-desk]').nth(3).click()
                    page.wait_for_timeout(55)
                    assert page.locator('[data-fvx-record]:visible').count()==6
                    assert page.evaluate('document.activeElement.id')=='fv-ex2-ledger-apollo1-record-04'
                    # The R38 Desk filter is a screen convenience, NOT permission
                    # to silently discard five source records from printed pages.
                    page.locator('input[data-fvx-search]').fill('S67-19766')
                    page.emulate_media(media='print')
                    assert page.locator('[data-fvx-record]:visible').count()==6,(w,'Desk print source loss')
                    assert page.locator('.fv-ex2-ledger__custody dd:visible').count()==30,(w,'Desk print provenance')
                    assert page.locator('.fv-ex2-ledger__fulltext p:visible').count()==6
                    assert page.locator('[data-fva-record]:visible').count()==6
                    assert page.locator('[data-fva-drawer] dd:visible').count()==54
                    assert page.locator('[data-fva-cite-id]:visible').count()==6
                    assert page.locator('.fv-ex2-ledger').evaluate('(e)=>getComputedStyle(e).color')=='rgb(17, 17, 17)'
                    receipt['print_regressions'].append({'width':w,'desk_records':6,'desk_custody_fields':30,'atlas_records':6,'atlas_custody_fields':54})
                    page.emulate_media(media='screen')
                    page.locator('input[data-fvx-search]').fill('')
                    page.locator('[data-fva-filter="2017"]').click()
                    assert page.locator('[data-fva-record]:visible').count()==2
                    if w<=390:page.locator('[data-fvx-to-atlas]').first.tap()
                    else:page.locator('[data-fvx-to-atlas]').first.click()
                    page.wait_for_timeout(55)
                    assert page.locator('[data-fva-record]:visible').count()==6
                    assert page.evaluate('document.activeElement.id')=='fva-record-01'
                    if axe_path:
                        page.add_script_tag(path=str(axe_path))
                        violations=page.evaluate('axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa","wcag22aa"]}}).then(r=>r.violations)')
                        assert not violations,(w,violations)
                    receipt['lab_metrics'].append({'width':w,**page.evaluate('window.__fv_r53_lab')})
                    if w in (390,1440):
                        page.wait_for_timeout(240)
                        shot=page.screenshot(full_page=True,animations='disabled')
                        assert shot==page.screenshot(full_page=True,animations='disabled')
                        filename=f'r59-real-r38-{w}.png'
                        (output/filename).write_bytes(shot)
                        receipt['screenshots'][filename]=hashlib.sha256(shot).hexdigest()
                receipt['tests'].append({'width':w,'js':js,'pass':True})
                context.close()
        browser.close()
    (output/'R59_REAL_R38_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('PASS',len(receipt['tests']),'ACTUAL R38+Atlas PHP-cohost cases; WordPress NOT installed')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--axe-file',type=Path)
    parser.add_argument('--axe-sha256')
    args=parser.parse_args()
    try: run(args.output,args.axe_file,args.axe_sha256)
    except FileNotFoundError as exc:
        print('BLOCKED',str(exc),file=sys.stderr)
        sys.exit(2)
