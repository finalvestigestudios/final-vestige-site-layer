#!/usr/bin/env python3
"""R50 PHP-assembled co-host Chromium QA; synthetic Desk (not PR158 HTML or WP HTTP)."""
from __future__ import annotations
import argparse,hashlib,json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_r49_reciprocal import fixture as source_fixture
HERE=Path(__file__).resolve().parents[1]

def make_document():
    allhtml=source_fixture()
    head,body=allhtml.split('<body>',1)
    desk,rest=body.split('<script>',1)
    deskjs,rest=rest.split('</script>',1)
    atlas,rest=rest.split('<script>',1)
    atlasjs=rest.split('</script>',1)[0]
    # Synthetic Desk's only missing semantic is the source heading; the real
    # PR158 template includes the exact same native destination already.
    desk=desk.replace('<section data-fvx-ledger class="fv-ex2-ledger"',
       '<section data-fvx-ledger class="fv-ex2-ledger"')
    desk=desk.replace('<div data-fvx-tools hidden>',
      '<h2 id="fv-ex2-ledger-apollo1-title">Research Desk</h2><div data-fvx-tools hidden>')
    input=json.dumps({'mode':'markup','desk':desk,'atlas':atlas})
    run=subprocess.run(['php',str(HERE/'tests/php_suite_r50_probe.php')],input=input,
                       capture_output=True,text=True,check=True)
    suite_css=(HERE/'integration/apollo-suite.css').read_text()
    return head.replace('</head>','<style>'+suite_css+'</style></head>')+'<body>'+run.stdout+'<script>'+deskjs+'</script><script>'+atlasjs+'</script></body></html>'

def run(output:Path):
    output.mkdir(parents=True,exist_ok=True)
    html=make_document()
    receipt={'schema':'fv.ex2.apollo.r50.suite-php-browser.v1','release':'STAGING_HOLD',
      'research_desk_markup':'SYNTHETIC CONTRACT; ACTUAL PR158 CSS/HTML NOT INCLUDED',
      'atlas_markup':'ACTUAL PHP SHORTCODE','wrapper':'ACTUAL PHP MARKUP FUNCTION',
      'navigation':'SET_CONTENT: LOCAL HTTP BLOCKED','hosted_cwv':'NOT_MEASURED',
      'axe_core':'NOT_EXECUTED_NO_VERIFIED_LOCAL_BUNDLE','tests':[],
      'component_lab_metrics':[],'screenshots':{}}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for w in (320,360,390,428,768,1024,1440,1920):
            for js in (False,True):
                ctx=browser.new_context(viewport={'width':w,'height':900},java_script_enabled=js,
                   is_mobile=w<=390,has_touch=w<=390,reduced_motion='reduce')
                pg=ctx.new_page();errors=[];requests=[]
                pg.on('pageerror',lambda e:errors.append(str(e)))
                pg.on('request',lambda r:requests.append(r.url))
                perf='''<script>window.__perf={lcp:null,cls:0};try{
                  new PerformanceObserver(a=>a.getEntries().forEach(e=>window.__perf.lcp=e.startTime))
                    .observe({type:'largest-contentful-paint',buffered:true});
                  new PerformanceObserver(a=>a.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__perf.cls+=e.value}))
                    .observe({type:'layout-shift',buffered:true});}catch(e){window.__perf.error=String(e)}</script>'''
                pg.set_content(html.replace('<head>','<head>'+perf,1));pg.wait_for_timeout(75)
                assert not errors and not requests,(w,js,errors,requests)
                assert pg.locator('[data-fva-record]:visible').count()==6
                assert pg.locator('[data-fvx-record]:visible').count()==6
                assert not pg.evaluate('document.documentElement.scrollWidth>innerWidth+2'),w
                assert pg.locator('.fv-ex2-apollo-suite__head nav a').count()==2
                assert pg.locator('.fv-ex2-apollo-suite__head nav a').first.get_attribute('href')=='#fv-ex2-ledger-apollo1-title'
                assert pg.locator('.fv-ex2-apollo-suite__head nav a').last.get_attribute('href')=='#fva-title'
                if js:
                    pg.locator('[data-fva-filter="2017"]').click()
                    assert pg.locator('[data-fva-record]:visible').count()==2
                    (pg.locator('[data-fvx-to-atlas]').first.tap() if w<=390 else pg.locator('[data-fvx-to-atlas]').first.click())
                    pg.wait_for_timeout(70)
                    assert pg.locator('[data-fva-record]:visible').count()==6
                    assert pg.evaluate('document.activeElement.id')=='fva-record-01'
                    pg.locator('input[data-fvx-search]').fill('S67-19766')
                    assert pg.locator('[data-fvx-record]:visible').count()==1
                    pg.locator('[data-fva-to-desk]').nth(3).click()
                    pg.wait_for_timeout(60)
                    assert pg.locator('[data-fvx-record]:visible').count()==6
                    assert pg.evaluate('document.activeElement.id')=='fv-ex2-ledger-apollo1-record-04'
                    metric=pg.evaluate('window.__perf')
                    receipt['component_lab_metrics'].append({'width':w,'lcp_ms':metric.get('lcp'),
                          'cls':metric.get('cls'),'scope':'PHP_FRAGMENT_SET_CONTENT_NOT_HOSTED'})
                    if w in (390,1440):
                        image=pg.screenshot(full_page=True,animations='disabled')
                        again=pg.screenshot(full_page=True,animations='disabled')
                        assert image==again,'Screenshot not reproducible'
                        path=output/f'r50-suite-{w}.png';path.write_bytes(image)
                        receipt['screenshots'][str(w)]={'sha256':hashlib.sha256(image).hexdigest(),'bytes':len(image)}
                receipt['tests'].append({'width':w,'javascript':js,'pass':True})
                ctx.close()
        browser.close()
    (output/'R50_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('PASS',len(receipt['tests']),'PHP-assembled suite Chromium viewport/mode runs')
    return receipt
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True)
    run(a.parse_args().output)
