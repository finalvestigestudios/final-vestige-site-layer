#!/usr/bin/env python3
"""R48 Chromium co-host contract: real Atlas PHP, synthetic Desk HTML, exact PR158 JS.
No installed WordPress, real HTTP, axe-core or hosted CWV claim is made.
"""
import json,sys,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_r46_pair_smoke import fixture
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
import build_atlas
JSP=BASE/'tests/fixtures/source-ledger.pr158.js'

def document():
    js=JSP.read_bytes()
    assert build_atlas.git_blob(js)=='32e757cc4dc8708397ff65ac21e89dd319781d78'
    rows=[]
    for r in build_atlas.validate_custody()['records']:
        rows.append('<article data-fvx-record data-fvx-search="'+r['catalog']+'" '
          'id="fv-ex2-ledger-apollo1-record-'+r['id']+'">'
          '<div class="fv-ex2-ledger__recordid">NASA '+r['catalog']+' · NASA</div>'
          '<a href="'+r['photo_url']+'">NASA original</a>'
          '<details data-fvx-photo-record="'+r['id']+'"><summary>Source custody</summary></details></article>')
    desk='<section data-fvx-ledger><div data-fvx-tools hidden><input type="search" data-fvx-search><span data-fvx-status></span></div>'+''.join(rows)+'<p data-fvx-empty hidden>Empty</p></section>'
    return fixture().replace('<body>','<body>'+desk+'<script>'+js.decode()+'</script>')

def main():
    page_html=document();counts=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in (320,360,390,768,1024,1440,1920):
            for enabled in (False,True):
                ctx=browser.new_context(viewport={'width':width,'height':900},
                     java_script_enabled=enabled,is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce')
                pg=ctx.new_page();errors=[];requests=[]
                pg.on('pageerror',lambda e:errors.append(str(e)))
                pg.on('request',lambda r:requests.append(r.url))
                pg.set_content(page_html)
                assert not errors and not requests
                assert pg.locator('[data-fva-record]:visible').count()==6
                assert pg.locator('[data-fvx-record]:visible').count()==6
                assert pg.locator('[data-fva-to-desk]:visible').count()==(6 if enabled else 0)
                assert not pg.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                if enabled:
                    pg.locator('input[data-fvx-search]').fill('S67-19766')
                    assert pg.locator('[data-fvx-record]:visible').count()==1
                    (pg.locator('[data-fva-to-desk]').nth(3).tap() if width<=390 else pg.locator('[data-fva-to-desk]').nth(3).click())
                    pg.wait_for_timeout(40)
                    assert pg.locator('[data-fvx-record]:visible').count()==6
                    assert pg.evaluate('document.activeElement.id')=='fv-ex2-ledger-apollo1-record-04'
                    assert pg.evaluate('location.hash')=='#fv-ex2-ledger-apollo1-record-04'
                counts.append((width,enabled));ctx.close()
        for attack,markup in (
           ('altered_catalog',page_html.replace('NASA S67-19766 · NASA','NASA FAKE · NASA',1)),
           ('duplicate_desk',page_html.replace('<section class="fva"','<section data-fvx-ledger></section><section class="fva"',1)),
           ('altered_source',page_html.replace('https://www.nasa.gov/image-detail/apollo-1-crew-honored/','https://www.nasa.gov/image-detail/other/',1)),
        ):
            ctx=browser.new_context();pg=ctx.new_page();pg.set_content(markup)
            assert pg.locator('[data-fva-to-desk]:visible').count()==0,attack
            assert pg.locator('[data-fva-record]:visible').count()==6,attack
            ctx.close()
        ctx=browser.new_context();pg=ctx.new_page()
        pg.set_content(page_html.replace('https://www.nasa.gov/image-detail/amf-s67-15717/','https://www.nasa.gov/image-detail/changed/',3))
        assert not pg.locator('[data-fva-controls]').is_visible()
        assert pg.locator('[data-fva-record]:visible').count()==6
        ctx.close()
        ctx=browser.new_context();pg=ctx.new_page();pg.set_content(page_html)
        pg.locator('[data-fvx-record] a').first.evaluate("a=>a.href='https://www.nasa.gov/image-detail/other/'")
        pg.locator('[data-fva-to-desk]').first.click()
        assert not pg.locator('[data-fva-to-desk]').first.is_visible()
        assert pg.locator('[data-fva-desk-status]').is_visible()
        ctx.close();browser.close()
    print('PASS R48: 14 Chromium configurations, five adversarial cases, no external requests')

if __name__=='__main__':main()
