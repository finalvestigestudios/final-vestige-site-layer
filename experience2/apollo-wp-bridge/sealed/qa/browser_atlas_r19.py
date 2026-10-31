#!/usr/bin/env python3
"""R19 Atlas browser/keyboard/touch/no-JS: exact source-pinned PHP fixture.

Chromium `page.set_content`; NOT real WordPress, HTTP CSP, axe-core, or field CWV.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_exact import get_fixture

HERE=Path(__file__).resolve().parent
OUT=HERE/'r19-screenshots'
REPORT=HERE/'R19_ATLAS_BROWSER_RESULTS.json'
WIDTHS=(320,360,390,768,1024,1440,1920)

def run():
    fixture, php_hash=get_fixture()
    OUT.mkdir(exist_ok=True)
    report={'status':'PASS_IN_MEMORY_CHROMIUM_ONLY','exact_php_sha256':php_hash,
            'not_real_wordpress':True,'not_browser_enforced_http_headers':True,
            'axe_status':'NOT_RUN_BUNDLE_UNAVAILABLE',
            'field_cwv_status':'NOT_MEASURED','responsive':[],'screenshots':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            context=browser.new_context(viewport={'width':width,'height':930},
                reduced_motion='reduce' if width==320 else 'no-preference')
            page=context.new_page();page.set_content(fixture,wait_until='load')
            atlas=page.locator('#atlas')
            assert atlas.count()==1
            assert atlas.locator('[data-ex2-atlas-item]').count()==6
            custody=atlas.locator('#fv-ex2-atlas-custody')
            assert custody.count()==1
            assert custody.locator('[data-atlas-custody-id]').count()==6
            assert not custody.evaluate('(e)=>e.open')
            custody.locator('summary').focus();page.keyboard.press('Enter')
            assert custody.evaluate('(e)=>e.open'),(width,'keyboard disclosure failed')
            assert custody.locator('[data-atlas-custody-id]:visible').count()==6
            assert custody.locator('a[href^="https://finalvestige.com/"]').count()==6
            assert custody.locator('a[download="apollo-atlas-custody.json"]').count()==1
            assert custody.locator('img,svg,canvas,iframe,script').count()==0
            assert 'zero verified map points' in custody.inner_text().lower()
            assert page.locator('img').count()==0
            assert page.locator('[data-map-pin], [data-geo-edge], [data-map-edge]').count()==0
            height=custody.locator('summary').evaluate('(e)=>e.getBoundingClientRect().height')
            assert height>=44,(width,'summary tap target too short',height)
            if width in (390,1440):
                shot=OUT/f'r19-atlas-custody-{width}.png'
                atlas.screenshot(path=str(shot),animations='disabled')
                report['screenshots'].append({'name':shot.name,'sha256':sha256(shot.read_bytes()).hexdigest()})
            sizes=custody.locator('a').evaluate_all('(nodes)=>nodes.map(e=>e.getBoundingClientRect().height)')
            assert sizes and all(n>=44 for n in sizes), (width,'undersized link',sizes)
            docw=page.evaluate('document.documentElement.scrollWidth')
            assert docw<=width+1,(width,'root overflow',docw)
            custody.locator('summary').focus();page.keyboard.press('Enter')
            assert not custody.evaluate('(e)=>e.open'),(width,'native disclosure failed to close')
            report['responsive'].append({'width':width,'document_width':docw,
                'publication_references':6,'geopins':0,'edges':0,
                'keyboard_native_disclosure':True,'touch_height_px':round(height,2)})
            context.close()
        # No-JS: the original Atlas (6) and the custody disclosure (6) remain readable.
        context=browser.new_context(viewport={'width':390,'height':844},java_script_enabled=False)
        page=context.new_page();page.set_content(fixture,wait_until='load')
        c=page.locator('#fv-ex2-atlas-custody');c.locator('summary').click()
        assert c.evaluate('(el)=>el.open')
        assert c.locator('[data-atlas-custody-id]:visible').count()==6
        assert page.locator('[data-ex2-atlas-item]:visible').count()==6
        report['no_js_390']={'all_evidence_preserved':True,'native_disclosure_operable':True}
        context.close()
        # Typical constrained WordPress column needs one-column layout.
        context=browser.new_context(viewport={'width':1920,'height':900},java_script_enabled=False)
        page=context.new_page();page.set_content(fixture,wait_until='load')
        page.locator('#atlas').evaluate('e=>{e.style.width="420px";e.style.maxWidth="420px"}')
        c=page.locator('#fv-ex2-atlas-custody');c.locator('summary').click()
        cols=c.locator('.fv-ex2-atlas-custody__list').evaluate(
          'e=>getComputedStyle(e).gridTemplateColumns.split(" ").length')
        assert cols==1,('420px embedded block has overlapping columns',cols)
        report['no_js_420_embedded_column']={'columns':cols,'passed':True}
        context.close()
        # Real touch-capable browser context, no simulated DOM clicks.
        context=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        page=context.new_page();page.set_content(fixture,wait_until='load')
        c=page.locator('#fv-ex2-atlas-custody');c.locator('summary').tap()
        assert c.evaluate('(el)=>el.open')
        report['touch_390']={'native_disclosure_tap':True}
        context.close();browser.close()
    REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('R19_ATLAS_BROWSER_PASS',len(report['responsive']),'widths, noJS, 420px embed, touch')
    return report

if __name__=='__main__':run()
