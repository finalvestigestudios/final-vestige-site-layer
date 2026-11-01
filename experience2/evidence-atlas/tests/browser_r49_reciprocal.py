#!/usr/bin/env python3
"""R49 Chromium co-host contract: actual PR158 Research Desk HTML/CSS/JS source blobs
plus PHP-rendered Atlas. No installed WordPress, HTTP navigation, axe or field CWV.
"""
import json,sys,hashlib,argparse
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
    html=(BASE/'tests/fixtures/source-ledger.pr158.html').read_bytes()
    css=(BASE/'tests/fixtures/source-ledger.pr158.css').read_bytes()
    assert build_atlas.git_blob(html)=='403d128c57b9bc82dac7c619651689070edef86c'
    assert build_atlas.git_blob(css)=='b8cf00afeceba115a9e9d19044fc11dcf2890cbe'
    assert html.count(b'data-fvx-record ')==6
    assert html.count(b'fv-ex2-ledger__recordlinks')==6
    assert b'data-fvx-photo-record' not in html  # PR158 original, not synthetic R38 custody.
    return fixture().replace('</head>','<style>'+css.decode()+'</style></head>',1).replace(
        '<body>','<body>'+html.decode()+'<script>'+js.decode()+'</script>',1)

def main(output: Path):
    output.mkdir(parents=True,exist_ok=True)
    page_html=document();counts=[];screenshots={};metrics=[]
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
                assert pg.locator('[data-fvx-to-atlas]').count()==(6 if enabled else 0)
                if enabled:
                    assert min(pg.locator('[data-fvx-to-atlas]').evaluate_all('(a)=>a.map(x=>x.getBoundingClientRect().height)'))>=44
                assert not pg.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                if enabled:
                    pg.locator('input[data-fvx-search]').fill('S67-19766')
                    assert pg.locator('[data-fvx-record]:visible').count()==1
                    (pg.locator('[data-fva-to-desk]').nth(3).tap() if width<=390 else pg.locator('[data-fva-to-desk]').nth(3).click())
                    pg.wait_for_timeout(40)
                    assert pg.locator('[data-fvx-record]:visible').count()==6
                    assert pg.evaluate('document.activeElement.id')=='fv-ex2-ledger-apollo1-record-04'
                    assert pg.evaluate('location.hash')=='#fv-ex2-ledger-apollo1-record-04'
                    pg.locator('[data-fva-filter="2017"]').click()
                    assert pg.locator('[data-fva-record]:visible').count()==2
                    backlink=pg.locator('[data-fvx-to-atlas]').nth(2)
                    (backlink.tap() if width<=390 else backlink.click())
                    pg.wait_for_timeout(70)
                    assert pg.locator('[data-fva-record]:visible').count()==6
                    assert pg.evaluate('location.hash')=='#fva-record-03'
                    assert pg.evaluate('document.activeElement.id')=='fva-record-03'
                    if width in (390,1440):
                        snapshot=pg.screenshot(full_page=True,animations='disabled')
                        assert snapshot==pg.screenshot(full_page=True,animations='disabled')
                        path=output/f'r49-{width}-actual-pr158.png'
                        path.write_bytes(snapshot)
                        screenshots[str(width)]=hashlib.sha256(snapshot).hexdigest()
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
        ctx.close()
        ctx=browser.new_context();pg=ctx.new_page();pg.set_content(page_html)
        pg.locator('[data-fvx-record]').nth(2).locator('a').first.evaluate(
            "a=>a.href='https://www.nasa.gov/image-detail/bad-source/'")
        pg.locator('[data-fvx-to-atlas]').nth(2).click()
        assert pg.locator('[data-fvx-to-atlas]').count()==0
        assert pg.locator('[data-fva-desk-status]').is_visible()
        assert pg.locator('[data-fva-record]:visible').count()==6
        ctx.close();browser.close()
    receipt={'schema':'fv.ex2.apollo.r49.original-pr158-browser.v1','release':'STAGING_HOLD',
      'research_desk':'ACTUAL_PR158_TEMPLATE_CSS_AND_JS_EXACT_GIT_BLOBS',
      'atlas':'ACTUAL_PHP_SHORTCODE_MARKUP','transport':'PLAYWRIGHT_SET_CONTENT_NO_HTTP',
      'axe':'NOT_AVAILABLE_NOT_EXECUTED','hosted_core_web_vitals':'NOT_MEASURED',
      'viewport_modes':len(counts),'adversarial_cases':6,'screenshots_sha256':screenshots}
    (output/'R49_ACTUAL_PR158_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('PASS R49: 14 Chromium modes, six adversarial cases, actual PR158 legacy source blobs; not WordPress')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)
