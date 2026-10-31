#!/usr/bin/env python3
"""R23 real Chromium: source-identity hold, keyboard, touch, no JS, seven widths.

Exact PHP staging output via WordPress auth stub; no real WP, HTTP navigation, axe,
or field Web Vitals certification. Photographs remain link-only.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_exact import get_fixture, INIT

HERE=Path(__file__).resolve().parent
OUT=HERE/'r23-screenshots'
WIDTHS=(320,360,390,768,1024,1440,1920)

def run():
    fixture,sha=get_fixture();OUT.mkdir(parents=True,exist_ok=True)
    report={'test':'R23 NASA catalog identity adjudication','source':'Real PHP stub HTML, Playwright Chromium page.set_content',
            'generated_php_sha256':sha,'not_wp_installed':True,'not_axe_or_field_cwv':True,
            'viewports':[],'no_js':[],'screenshots':[],'touch':{}}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={'width':width,'height':930},reduced_motion='reduce' if width==320 else 'no-preference')
            page=ctx.new_page();page.add_init_script(INIT);page.set_content(fixture,wait_until='load');page.evaluate(INIT)
            cross=page.locator('#fv-ex2-research-desk-crosswalk')
            assert cross.count()==1
            cross.locator(':scope > summary').click()
            hold=page.locator('#fv-ex2-catalog-identity')
            assert hold.count()==1 and hold.is_visible()
            assert hold.get_attribute('data-catalog-review')=='hold'
            assert 'S67-19766' in hold.inner_text() and 'not been verified' in hold.inner_text()
            disclosure=hold.locator('details')
            assert disclosure.count()==1 and disclosure.get_attribute('open') is None
            summary=disclosure.locator('summary');summary.focus()
            page.keyboard.press('Enter')
            assert disclosure.evaluate('(x)=>x.open') is True
            assert hold.locator('a[href="https://www.nasa.gov/image-detail/apollo-1-crew-honored/"]').count()==1
            assert hold.locator('a[href="https://www.nasa.gov/image-article/apollo-1-prime-crew-portrait/"]').count()==1
            assert hold.locator('a[href="#source-01"]').count()==1
            assert hold.locator('a[href="#stage-01"]').count()==1
            assert hold.locator('img,script,iframe,canvas').count()==0
            assert 'not the original linked image' in hold.inner_text()
            assert page.evaluate('document.documentElement.scrollWidth')<=width+1
            assert hold.locator('a').first.evaluate('(el)=>el.getBoundingClientRect().height')>=44
            cards=hold.locator('ol').evaluate('(x)=>getComputedStyle(x).gridTemplateColumns.split(" ").length')
            if width<=390: assert cards==1,(width,cards)
            page.wait_for_timeout(120)
            timing=page.evaluate('({lcp:window.__fv_cwv?.lcp??null,cls:window.__fv_cwv?.cls??null})')
            if width in (390,1440):
                path=OUT/f'r23-catalog-identity-{width}.png'
                hold.screenshot(path=str(path),animations='disabled',timeout=17000)
                report['screenshots'].append({'filename':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
            report['viewports'].append({'width':width,'columns':cards,'document_scrollwidth':page.evaluate('document.documentElement.scrollWidth'),
                                        'nested_disclosure_keyboard':'PASS','hold_visible':'PASS','synthetic_lcp_ms':timing['lcp'],
                                        'synthetic_cls':timing['cls']})
            ctx.close()
        for width in (320,1920):
            ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=False)
            page=ctx.new_page();page.set_content(fixture,wait_until='load')
            page.locator('#fv-ex2-research-desk-crosswalk > summary').click()
            hold=page.locator('#fv-ex2-catalog-identity'); disclosure=hold.locator('details')
            disclosure.locator('summary').click()
            assert disclosure.evaluate('(x)=>x.open') and hold.locator('a').count()==4
            assert hold.locator('a[href="#source-01"]').is_visible()
            report['no_js'].append({'width':width,'native_details':'PASS','links':4})
            ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':900},has_touch=True,is_mobile=True,device_scale_factor=1)
        page=ctx.new_page();page.set_content(fixture)
        page.locator('#fv-ex2-research-desk-crosswalk > summary').tap()
        page.locator('#fv-ex2-catalog-identity summary').tap()
        assert page.locator('#fv-ex2-catalog-identity details').evaluate('(x)=>x.open')
        page.locator('#fv-ex2-catalog-identity a[href="#stage-01"]').tap()
        assert page.evaluate('location.hash')=='#stage-01'
        report['touch']={'status':'PASS_NATIVE_DETAILS_AND_ANCHOR','target':'#stage-01'}
        ctx.close()
        ctx=browser.new_context(viewport={'width':1920,'height':900},java_script_enabled=False)
        page=ctx.new_page();page.set_content(fixture)
        container=page.locator('#source-concordance'); container.evaluate('(x)=>{x.style.width="420px";x.style.maxWidth="420px"}')
        page.locator('#fv-ex2-research-desk-crosswalk > summary').click()
        page.locator('#fv-ex2-catalog-identity summary').click()
        assert page.locator('#fv-ex2-catalog-identity ol').evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ").length')==1
        report['nested_420px_no_js']='PASS'
        ctx.close();browser.close()
    (HERE/'R23_NASA_IDENTITY_BROWSER_RESULTS.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('R23_CHROMIUM_PASS',len(report['viewports']),'viewports',len(report['screenshots']),'screenshots')
    return report

if __name__=='__main__':run()
