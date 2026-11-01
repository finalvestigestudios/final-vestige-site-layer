#!/usr/bin/env python3
"""R44 reproducible Chromium on actual PHP-rendered Atlas, not HTTP/WordPress.

Usage: python tests/browser_r44_review.py --output /tmp/r44-qa
Requires installed Playwright and Chromium. Axe remains a separate release gate.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import build_wordpress_stage
WIDTHS=(320,360,390,768,1024,1440,1920)
COPY_STUB="<script>window.copied=[];Object.defineProperty(navigator,'clipboard',{value:{writeText:async s=>window.copied.push(s)}})</script>"
METRICS="<script>window.fvMetrics={lcp:null,cls:0};try{new PerformanceObserver(x=>x.getEntries().forEach(e=>fvMetrics.lcp=e.startTime)).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(x=>x.getEntries().forEach(e=>{if(!e.hadRecentInput)fvMetrics.cls+=e.value})).observe({type:'layout-shift',buffered:true});}catch(e){fvMetrics.error=String(e)}</script>"

def main(out):
    out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        build_wordpress_stage.build(Path(d))
        path=Path(d)/'fv-ex2-evidence-atlas'
        r=subprocess.run(['php',str(HERE/'tests/wordpress_shortcode_probe.php'),str(path/'final-vestige-ex2-evidence-atlas.php')],env={**os.environ,'FV_SINGULAR':'1'},capture_output=True,text=True,check=True)
        fragment=json.loads(r.stdout)['markup']
        css=(path/'assets/atlas.css').read_text()
        js=(path/'assets/atlas.js').read_text()
    def markup(pre=''):
        return f'<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1">{METRICS}{pre}<style>{css}</style></head><body><main>{fragment}</main><script>{js}</script></body></html>'
    receipt={'transport':'PLAYWRIGHT_SET_CONTENT_NO_HTTP','authentic_wordpress':'NOT_TESTED','axe':'NOT_EXECUTED','hosted_CWV':'NOT_MEASURED','responsive':[],'adversarial':[],'screenshots':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for js_enabled in (False,True):
            for width in WIDTHS:
                ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js_enabled,has_touch=width<=390,is_mobile=width<=390,reduced_motion='reduce')
                page=ctx.new_page();errors=[];requests=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('request',lambda r:requests.append(r.url))
                page.set_content(markup(COPY_STUB))
                page.wait_for_timeout(60)
                assert not errors and not requests,(errors,requests)
                assert page.locator('[data-fva-citation-text]:visible').count()==6
                assert page.locator('[data-fva-record]:visible').count()==6
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+2'),width
                assert page.locator('[data-fva-copy]:visible').count()==(6 if js_enabled else 0)
                if js_enabled:
                    page.locator('[data-fva-copy]').first.focus()
                    page.keyboard.press('Enter')
                    page.wait_for_timeout(35)
                    assert 's67-19766' in page.evaluate('window.copied[0]').lower()
                    filter_button=page.locator('[data-fva-filter="2017"]')
                    filter_button.tap() if width<=390 else filter_button.click()
                    assert page.locator('[data-fva-record]:visible').count()==2
                    assert page.locator('[data-fva-citation-text]:visible').count()==6
                if width in (390,1440):
                    page.evaluate('document.activeElement?.blur();window.scrollTo(0,0)')
                    name=f'r44-{width}-'+('js' if js_enabled else 'nojs')+'.png'
                    image=out/name
                    page.screenshot(path=str(image),full_page=True,animations='disabled')
                    receipt['screenshots'].append({'name':name,'sha256':hashlib.sha256(image.read_bytes()).hexdigest()})
                receipt['responsive'].append({'width':width,'javascript':js_enabled,'pass':True,'synthetic_vitals':page.evaluate('fvMetrics') if js_enabled else None})
                ctx.close()
        page=browser.new_page();page.set_content(markup("<script>Object.defineProperty(navigator,'clipboard',{value:undefined})</script>"))
        assert page.locator('[data-fva-copy]:visible').count()==0
        assert page.locator('[data-fva-citation-text]:visible').count()==6
        receipt['adversarial'].append('unsupported clipboard: copy controls hidden; six citations visible')
        page.close()
        denied="<script>Object.defineProperty(navigator,'clipboard',{value:{writeText:async()=>{throw Error('denied')}}})</script>"
        page=browser.new_page();page.set_content(markup(denied))
        page.locator('[data-fva-copy]').first.click();page.wait_for_timeout(30)
        assert 'Clipboard unavailable' in page.locator('[data-fva-copy-status]').inner_text()
        assert page.locator('[data-fva-citation-text]:visible').count()==6
        receipt['adversarial'].append('clipboard denied: polite fallback, six citations visible')
        page.close()
        before='<script>document.querySelector(\'[data-fva-cite-id="03"]\').dataset.fvaCiteId="99"</script>'
        page=browser.new_page();page.set_content(markup(COPY_STUB).replace('<script>'+js+'</script>',before+'<script>'+js+'</script>'))
        assert page.locator('[data-fva-copy]:visible').count()==0
        assert page.locator('[data-fva-record]:visible').count()==6
        assert page.locator('[data-fva-citation-text]:visible').count()==6
        receipt['adversarial'].append('tampered citation ID: enhancement fails open')
        page.close()
        page=browser.new_page();page.set_content(markup(COPY_STUB))
        page.locator('[data-fva-filter="2017"]').click();page.emulate_media(media='print')
        assert page.locator('[data-fva-record]:visible').count()==6
        assert page.locator('[data-fva-citation-text]:visible').count()==6
        receipt['adversarial'].append('print after filtering: all six records and citations retained')
        page.close();browser.close()
    (out/'R44_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(f'PASS: {len(receipt["responsive"])} responsive Chromium cases, {len(receipt["adversarial"])} adversarial, {len(receipt["screenshots"])} screenshots; HOLD true HTTP/WordPress/axe/CWV')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)
