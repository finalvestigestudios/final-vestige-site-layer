#!/usr/bin/env python3
"""R18 Playwright: source-custody disagreement remains visible, keyboard and no-JS.

Uses source-pinned PHP with stubbed WordPress response and in-memory Chromium;
NOT actual WordPress host, HTTP CSP, axe-core, Safari, or production CWV.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_exact import get_fixture

HERE=Path(__file__).resolve().parent
OUT=HERE/'r18-screenshots'
WIDTHS=(320,360,390,768,1024,1440,1920)

def run():
    fixture,php_sha=get_fixture()
    OUT.mkdir(exist_ok=True)
    result={'status':'PASS_CHROMIUM_IN_MEMORY_ONLY','exact_pinned_php_sha256':php_sha,
            'browser':'Chromium Playwright / actual source-pinned PHP fixture',
            'not_hosted_wordpress_or_axe':True,'responsive':[],'screenshots':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={'width':width,'height':900},
                                    reduced_motion='reduce' if width==320 else 'no-preference')
            page=ctx.new_page();page.set_content(fixture,wait_until='load')
            cross=page.locator('#fv-ex2-research-desk-crosswalk')
            assert cross.count()==1
            assert cross.locator('[data-crosswalk-id]').count()==6
            assert cross.locator('[data-crosswalk-review="hold"]').count()==1
            assert not cross.evaluate('(el)=>el.open')
            cross.locator('summary').focus();page.keyboard.press('Enter')
            assert cross.evaluate('(el)=>el.open'),(width,'keyboard disclosure failed')
            labels=cross.locator('[data-crosswalk-id="01"]').inner_text()
            assert 'NASA S67-19766' in labels and 'Apollo 1 crew training portrait' in labels
            assert 'CATALOG IDENTIFIER REVIEW NEEDED' in labels
            assert cross.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==6
            assert cross.locator('a[href^="#source-"]').count()==6
            assert cross.locator('a[href*="/blob/250d7f05a4de037e73826dcf0cfaef0ec4c29383/"]').count()==1
            assert cross.locator('img,script,iframe').count()==0
            assert page.locator('img').count()==0
            docw=page.evaluate('document.documentElement.scrollWidth')
            assert docw<=width+1,(width,'horizontal overflow',docw)
            if width in (390,1440):
                shot=OUT/f'r18-pr158-source-custody-{width}.png'
                cross.screenshot(path=str(shot),animations='disabled')
                result['screenshots'].append({'name':shot.name,'sha256':sha256(shot.read_bytes()).hexdigest()})
            assert cross.locator('summary').evaluate('e=>e.getBoundingClientRect().height')>=44
            cross.locator('summary').click();assert not cross.evaluate('(el)=>el.open')
            result['responsive'].append({'viewport':width,'document_width':docw,
              'matched_source_urls':6,'identifier_holds':1,'native_keyboard_disclosure':True})
            ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':844},java_script_enabled=False)
        pg=ctx.new_page();pg.set_content(fixture,wait_until='load')
        c=pg.locator('#fv-ex2-research-desk-crosswalk')
        c.locator('summary').click()
        assert c.evaluate('el=>el.open')
        assert c.locator('[data-crosswalk-id]:visible').count()==6
        assert c.locator('[data-crosswalk-review="hold"]:visible').count()==1
        result['no_js_mobile_390']=True
        ctx.close()
        ctx=browser.new_context(viewport={'width':1920,'height':900},java_script_enabled=False)
        pg=ctx.new_page();pg.set_content(fixture,wait_until='load')
        parent=pg.locator('#source-concordance')
        parent.evaluate('el=>{el.style.width="420px";el.style.maxWidth="420px"}')
        c=pg.locator('#fv-ex2-research-desk-crosswalk');c.locator('summary').click()
        columns=c.locator('.fv-ex2-crosswalk__list').evaluate('el=>getComputedStyle(el).gridTemplateColumns.split(" ").length')
        assert columns==1,('narrow CMS container must reflow',columns)
        result['narrow_420px_wordpress_column_no_js']={'columns':columns,'status':'PASS'}
        ctx.close();browser.close()
    (HERE/'R18_CROSSWALK_BROWSER_RESULTS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('R18_CROSSWALK_BROWSER_PASS',len(result['responsive']),'widths, no-JS 390, nested 420, screenshots',len(result['screenshots']))
    return result

if __name__=='__main__':run()
