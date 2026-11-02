#!/usr/bin/env python3
"""R55 real-R37-Atlas Chromium: print visibility, source custody, keyboard/touch, no-JS.
Not WordPress, axe-core, screen reader or hosted Core Web Vitals evidence.
"""
import argparse, hashlib, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parent))
from browser_r54_real_atlas import document
SIZES=(320,360,390,428,768,1024,1440,1920)

def run(out):
    out.mkdir(parents=True,exist_ok=True)
    html,manifest=document() # Exact R37 blob required by deterministic stage builder.
    # Observe local fragment paint and shifts. Never call these hosted/p75 CWV.
    monitor="""<script>window.__r55={lcp:null,cls:0};try{
      new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__r55.lcp=e.startTime))
        .observe({type:'largest-contentful-paint',buffered:true});
      new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__r55.cls+=e.value}))
        .observe({type:'layout-shift',buffered:true});
      }catch(e){window.__r55.observer_error=String(e)}</script>"""
    html=html.replace('<head>','<head>'+monitor,1)
    receipt={'schema':'fv.ex2.apollo.r55.deep-browser.v1','scope':'ACTUAL_R37_ATLAS_NOT_WORDPRESS',
      'source_blob':manifest['source_crosswalk_blob'],'axe':'NOT_RUN',
      'screen_reader':'NOT_RUN','original_r38_cohost':'NOT_RUN','hosted_cwv':'NOT_RUN',
      'cases':[],'screenshots':{},'lab_metrics':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in SIZES:
            for js in (False,True):
                ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                    reduced_motion='reduce',has_touch=width<=390,is_mobile=width<=390)
                page=ctx.new_page();errors=[];network=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('request',lambda r:network.append(r.url))
                page.set_content(html);page.wait_for_timeout(80)
                assert not errors and not network,(width,js,errors,network)
                assert page.locator('[data-fva-record]:visible').count()==6
                assert page.locator('[data-fva-cite-id]').count()==6
                assert page.locator('[data-fva-catalog-unconfirmed]:visible').count()==1
                assert page.locator('[data-fva-atlas] img,[data-fva-atlas] iframe').count()==0
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),width
                missing=page.evaluate('''() => {const ids=new Set([...document.querySelectorAll('[id]')].map(e=>e.id));return [...document.querySelectorAll('[aria-labelledby],[aria-describedby],[aria-controls]')].flatMap(e=>['aria-labelledby','aria-describedby','aria-controls'].flatMap(a=>(e.getAttribute(a)||'').split(/\\s+/).filter(id=>id&&!ids.has(id))))}''')
                assert not missing,(width,js,missing)
                page.locator('[data-fva-drawer] summary').first.focus();page.keyboard.press('Enter')
                assert page.locator('[data-fva-drawer]').first.evaluate('(e)=>e.open')
                assert page.evaluate('document.activeElement.tagName')=='SUMMARY'
                if js:
                    page.locator('[data-fva-filter="2017"]').click()
                    assert page.locator('[data-fva-record]:visible').count()==2
                else: assert page.locator('[data-fva-controls]').is_hidden()
                page.emulate_media(media='print')
                assert page.locator('[data-fva-record]:visible').count()==6,(width,js,'print sources')
                assert page.locator('[data-fva-drawer] dl:visible').count()==6
                page.emulate_media(media='screen')
                if js:
                    assert page.locator('[data-fva-record]:visible').count()==2
                    link=page.locator('[data-fva-jump]').first
                    link.tap() if width<=390 else link.click()
                    page.wait_for_timeout(60)
                    assert page.locator('[data-fva-record]:visible').count()==6
                    assert page.evaluate('document.activeElement.id')=='fva-record-01'
                    page.locator('[data-fva-select="01"]').click()
                    page.locator('[data-fva-select="02"]').click()
                    assert page.locator('[data-fva-compare-slot] h3').count()==2
                    page.locator('[data-fva-compare-clear]').click()
                    receipt['lab_metrics'].append({'width':width,**page.evaluate('window.__r55'), 'scope':'SET_CONTENT_NOT_HOSTED'})
                    if width in (390,1440):
                        shot=page.screenshot(full_page=True,animations='disabled')
                        assert shot==page.screenshot(full_page=True,animations='disabled')
                        name=f'r55-atlas-{width}.png';(out/name).write_bytes(shot)
                        receipt['screenshots'][name]=hashlib.sha256(shot).hexdigest()
                    page.locator('.fva-card__external').first.evaluate("e=>e.setAttribute('href','https://wrong.invalid/')")
                    page.locator('[data-fva-filter="2017"]').click()
                    assert page.locator('[data-fva-controls]').is_hidden()
                    assert page.locator('[data-fva-record]:visible').count()==6
                receipt['cases'].append({'width':width,'javascript':js,'passed':True,'print_six_visible':True})
                ctx.close()
        browser.close()
    (out/'R55_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('PASS',len(receipt['cases']),'actual-Atlas Chromium combinations')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
