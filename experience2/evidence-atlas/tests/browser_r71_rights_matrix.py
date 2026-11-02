#!/usr/bin/env python3
"""R71: exact-source Playwright of six-photo rights matrix, staging only."""
from __future__ import annotations
import argparse,hashlib,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_atlas import build_rights_matrix_r71
from playwright.sync_api import sync_playwright

WIDTHS=(320,360,390,428,768,1024,1440,1920)

def run(out:Path,axe:Path|None=None,axe_sha:str|None=None)->dict:
    out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        proof=build_rights_matrix_r71(Path(td))
        doc=(Path(td)/'apollo-r71-media-rights-STAGING-ONLY.html').read_text()
    js=None
    if axe is not None:
        raw=axe.read_bytes()
        if not axe_sha or hashlib.sha256(raw).hexdigest()!=axe_sha or len(raw)<100000:
            raise ValueError('AXE_SHA256_MISMATCH')
        js=raw.decode('utf-8')
    receipt={'schema':'fv.apollo.r71.browser.v1','release':'STAGING_HOLD',
      'actual_wordpress':False,'photo_rights_cleared':False,'hosted_cwv':False,
      'build':proof,'cases':[],'screenshots':{},'axe':[]}
    with sync_playwright() as p:
        options={'headless':True,'args':['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():options['executable_path']='/usr/bin/chromium'
        browser=p.chromium.launch(**options)
        for width in WIDTHS:
            for javascript in (False,True):
                ctx=browser.new_context(viewport={'width':width,'height':850},
                    java_script_enabled=javascript,reduced_motion='reduce',
                    has_touch=width<=390,is_mobile=width<=390,
                    forced_colors='active' if width==390 else 'none')
                page=ctx.new_page();errors=[];requests=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('request',lambda r:requests.append(r.url))
                page.set_content(doc)
                assert page.locator('[data-r71-rights-row]').count()==6
                assert page.locator('[data-r71-rights-row]:visible').count()==6
                assert page.locator('[data-fva-record]:visible').count()==6
                assert page.locator('[data-r71-rights] img,iframe,video,svg,canvas').count()==0
                assert page.locator('[data-r71-rights] a[href^="https://www.nasa.gov/image-detail/"]').count()==6
                assert page.locator('[data-lat],[data-lon],[data-geo-edge]').count()==0
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                summary=page.locator('[data-r71-rights] summary').first
                summary.focus();page.keyboard.press('Enter')
                assert summary.evaluate('e=>e.parentNode.open')
                if javascript:
                    assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')=='yes'
                    button=page.locator('[data-fva-filter="2017"]')
                    button.tap() if width<=390 else button.click()
                    assert page.locator('[data-fva-record]:visible').count()==2
                    assert page.locator('[data-r71-rights-row]:visible').count()==6
                else:
                    assert page.locator('[data-fva-controls]').is_hidden()
                page.emulate_media(media='print')
                assert page.locator('[data-r71-rights-row]:visible').count()==6
                assert page.locator('[data-fva-record]:visible').count()==6
                page.emulate_media(media='screen')
                if javascript and width in (390,1440):
                    page.evaluate('window.scrollTo(0,0)')
                    picture=page.screenshot(full_page=True,animations='disabled')
                    assert picture==page.screenshot(full_page=True,animations='disabled')
                    name=f'R71_MEDIA_RIGHTS_{width}.png';(out/name).write_bytes(picture)
                    receipt['screenshots'][name]=hashlib.sha256(picture).hexdigest()
                    if js:
                        page.emulate_media(forced_colors='none')
                        page.add_script_tag(content=js)
                        report=page.evaluate("""async()=>{const r=await axe.run(document.querySelector('[data-r71-rights]'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return {violations:r.violations.map(v=>({id:v.id,nodes:v.nodes.length})),passes:r.passes.length}}""")
                        receipt['axe'].append({'width':width,'color_mode':'normal',**report})
                        assert not report['violations'],report
                assert not errors and not requests,(width,errors,requests)
                receipt['cases'].append({'width':width,'javascript_enabled':javascript,'passed':True})
                ctx.close()
        browser.close()
    (out/'R71_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--axe',type=Path);cli.add_argument('--axe-sha256')
    args=cli.parse_args()
    result=run(args.output,args.axe,args.axe_sha256)
    print('PASS',len(result['cases']),'Chromium cases; STAGING_HOLD')
