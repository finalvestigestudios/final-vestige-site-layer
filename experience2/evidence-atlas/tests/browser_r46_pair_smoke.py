#!/usr/bin/env python3
"""R46 real Chromium QA of PHP-shortcode markup via set_content; NOT WordPress HTTP."""
from pathlib import Path
import json,os,subprocess,sys,tempfile
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import build_wordpress_stage

def fixture():
    with tempfile.TemporaryDirectory() as temp:
        build_wordpress_stage.build(Path(temp))
        plugin=Path(temp)/'fv-ex2-evidence-atlas'
        response=subprocess.run(['php',str(HERE/'tests/wordpress_shortcode_probe.php'),
            str(plugin/'final-vestige-ex2-evidence-atlas.php')],env={**os.environ,'FV_SINGULAR':'1'},
            capture_output=True,text=True,check=True)
        frag=json.loads(response.stdout)['markup']
        css=(plugin/'assets/atlas.css').read_text()
        js=(plugin/'assets/atlas.js').read_text()
    return '<html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+frag+'<script>'+js+'</script></body></html>'

def main():
    html=fixture();count=0
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in (320,360,390,768,1024,1440,1920):
            for enabled in (False,True):
                ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,
                    has_touch=width<=390,is_mobile=width<=390,reduced_motion='reduce')
                page=ctx.new_page()
                errors=[];requests=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('request',lambda req:requests.append(req.url))
                page.set_content(html);page.wait_for_timeout(60)
                assert not errors and not requests,(width,errors,requests)
                assert page.locator('[data-fva-record]:visible').count()==6
                assert page.locator('[data-fva-citation-text]:visible').count()==6
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2')
                assert page.locator('[data-fva-compare]').is_visible()==enabled
                if enabled:
                    buttons=page.locator('[data-fva-select]')
                    assert min(buttons.evaluate_all('(a)=>a.map(x=>x.getBoundingClientRect().height)'))>=44
                    for index in (0,3):
                        buttons.nth(index).tap() if width<=390 else buttons.nth(index).click()
                    assert page.locator('[data-fva-compare-slot] h3').count()==2
                    assert 'S67-19766' in page.locator('[data-fva-compare-slot]').first.inner_text()
                    page.locator('[data-fva-filter="2017"]').click()
                    assert page.locator('[data-fva-record]:visible').count()==2
                    page.locator('[data-fva-compare-slot] a').first.click();page.wait_for_timeout(55)
                    assert page.locator('[data-fva-record]:visible').count()==6
                    assert page.evaluate('document.activeElement.id')=='fva-record-01'
                    page.emulate_media(media='print')
                    assert not page.locator('[data-fva-compare]').is_visible()
                    assert page.locator('[data-fva-record]:visible').count()==6
                count+=1;ctx.close()
        pg=browser.new_page();pg.set_content(html)
        pg.evaluate("document.querySelector('[data-fva-select]').dataset.fvaSelect='bad'")
        pg.locator('[data-fva-select="bad"]').click()
        assert not pg.locator('[data-fva-compare]').is_visible()
        assert pg.locator('[data-fva-record]:visible').count()==6
        pg.close();browser.close()
    print('PASS',count,'real Chromium configurations; no-JS/touch/keyboard/filter/print/fail-open')

if __name__=='__main__':main()
