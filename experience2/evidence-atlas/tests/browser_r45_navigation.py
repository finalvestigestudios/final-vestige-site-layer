#!/usr/bin/env python3
"""R45 actual PHP-rendered, six-record Atlas Playwright QA. NOT navigated WordPress.

Never claim that `page.set_content` results certify hosted CWV or axe. Optional
`--axe-script <local licensed axe-core .js>` runs real axe.run on this fixture.
Captures deterministic screenshots separately; captures realistic interaction
receipts, target-size observations and layout-shift/LCP probes as synthetic only.
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
METRICS='<script>window.fvaPerf={lcp:null,cls:0};try{new PerformanceObserver(l=>l.getEntries().forEach(e=>{window.fvaPerf.lcp=e.startTime})).observe({type:"largest-contentful-paint",buffered:true});new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.fvaPerf.cls+=e.value})).observe({type:"layout-shift",buffered:true});}catch(e){window.fvaPerf.error=String(e)}</script>'

def main(out, axe_script=None):
    out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        build_wordpress_stage.build(Path(td))
        plugin=Path(td)/'fv-ex2-evidence-atlas'
        call=subprocess.run(['php',str(HERE/'tests/wordpress_shortcode_probe.php'),str(plugin/'final-vestige-ex2-evidence-atlas.php')],env={**os.environ,'FV_SINGULAR':'1'},capture_output=True,text=True,check=True)
        frag=json.loads(call.stdout)['markup']
        css=(plugin/'assets/atlas.css').read_text()
        js=(plugin/'assets/atlas.js').read_text()
    page_html=f'<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1">{METRICS}<style>{css}</style></head><body><main>{frag}</main><script>{js}</script></body></html>'
    receipt={'schema':'fv.ex2.apollo.qa.r45.v1','release':'STAGING_HOLD','transport':'PLAYWRIGHT_SET_CONTENT_NO_HTTP','authentic_wordpress':'NOT_TESTED','axe':'NOT_EXECUTED','hosted_CWV':'NOT_MEASURED','cases':[],'adversarial':[],'screenshots':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for js_enabled in (False,True):
            for width in WIDTHS:
                ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js_enabled,has_touch=width<=390,is_mobile=width<=390,reduced_motion='reduce')
                pg=ctx.new_page()
                errors=[];network=[]
                pg.on('pageerror',lambda e:errors.append(str(e)))
                pg.on('request',lambda req:network.append(req.url))
                pg.set_content(page_html)
                pg.wait_for_timeout(70)
                assert not errors and not network, (errors,network)
                assert pg.locator('[data-fva-record]:visible').count()==6
                assert pg.locator('[data-fva-citation-text]:visible').count()==6
                assert pg.locator('[data-fva-to-citation]').count()==6
                assert pg.locator('[data-fva-back-record]').count()==6
                assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+2'), width
                targets=pg.locator('[data-fva-back-record]').evaluate_all('(nodes)=>nodes.map(n=>Math.round(n.getBoundingClientRect().height))')
                assert min(targets)>=44,(width,targets)
                if js_enabled:
                    pg.locator('[data-fva-filter="2017"]').tap() if width<=390 else pg.locator('[data-fva-filter="2017"]').click()
                    assert pg.locator('[data-fva-record]:visible').count()==2
                    # Bidirectional provenance navigation reopens filtered source.
                    pg.locator('[data-fva-back-record]').first.click()
                    pg.wait_for_timeout(80)
                    assert pg.locator('[data-fva-record]:visible').count()==6
                    assert pg.evaluate('location.hash')=='#fva-record-01'
                    assert pg.evaluate('document.activeElement.id')=='fva-record-01'
                    assert pg.locator('[data-fva-controls]').is_visible()
                pg.locator('[data-fva-to-citation]').first.click()
                assert pg.evaluate('location.hash')=='#fva-citation-01'
                assert pg.locator('#fva-citation-01').is_visible()
                pg.locator('[data-fva-back-record]').first.click()
                pg.wait_for_timeout(60)
                assert pg.evaluate('location.hash')=='#fva-record-01'
                if width in (390,1440):
                    # Screenshot neutral baseline, not an interactive state affected by hash.
                    pg.set_content(page_html);pg.wait_for_timeout(70)
                    pg.evaluate('document.activeElement?.blur();window.scrollTo(0,0)')
                    name=f'r45-{width}-'+('js' if js_enabled else 'nojs')+'.png'
                    file=out/name;pg.screenshot(path=str(file),animations='disabled',full_page=True)
                    receipt['screenshots'].append({'name':name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
                receipt['cases'].append({'width':width,'javascript':js_enabled,'source_backlinks':'PASS','overflow':'NONE','min_backlink_height_px':min(targets),'synthetic_performance':pg.evaluate('window.fvaPerf') if js_enabled else None})
                ctx.close()
        # Fail-open: altered citation destinations disable enhanced filtering but preserve links and source text.
        pg=browser.new_page();bad=page_html.replace('<script>'+js+'</script>', '<script>document.querySelector(\'[data-fva-back-record]\').setAttribute(\'href\',\'#fabricated-destination\')</script><script>'+js+'</script>')
        pg.set_content(bad)
        assert not pg.locator('[data-fva-controls]').is_visible()
        assert pg.locator('[data-fva-record]:visible').count()==6
        assert pg.locator('[data-fva-citation-text]:visible').count()==6
        receipt['adversarial'].append('tampered source backlink: enhancement withheld; all source text preserved')
        pg.close()
        # Print after filter: none of the six referenced sources disappear.
        pg=browser.new_page();pg.set_content(page_html)
        pg.locator('[data-fva-filter="2017"]').click();pg.emulate_media(media='print')
        assert pg.locator('[data-fva-record]:visible').count()==6
        assert pg.locator('[data-fva-citation-text]:visible').count()==6
        receipt['adversarial'].append('filtered print shows all six source records and citations')
        if axe_script:
            axe=Path(axe_script)
            if not axe.is_file():raise FileNotFoundError(axe)
            pg.emulate_media(media='screen');pg.add_script_tag(path=str(axe))
            result=pg.evaluate('''async()=>({version:window.axe?.version,results:await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})})''')
            violations=[{'id':v['id'],'impact':v['impact'],'nodes':len(v['nodes'])} for v in result['results']['violations']]
            receipt['axe']={'version':result['version'],'violations':violations,'passes':len(result['results']['passes'])}
            assert not violations,violations
        pg.close();browser.close()
    (out/'R45_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print('PASS: 14 actual PHP-rendered responsive cases, 2 adversarial checks, 4 screenshots; real WordPress and hosted CWV remain HOLD; axe:',receipt['axe'])

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('--output',type=Path,required=True);cli.add_argument('--axe-script',type=Path)
    args=cli.parse_args();main(args.output,args.axe_script)
