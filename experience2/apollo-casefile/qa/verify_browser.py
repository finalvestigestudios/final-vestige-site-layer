#!/usr/bin/env python3
"""Real Chromium smoke, fail-open, responsive, screenshot and synthetic perf evidence."""
from pathlib import Path
import hashlib
import json
import sys
import time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/'screenshots'
OUT.mkdir(parents=True,exist_ok=True)
HTML=(ROOT/'index.html').read_text(encoding='utf-8')
WIDTHS=[320,360,390,768,1024,1440,1920]
results={'method':'headless local Chromium Playwright with set_content() (navigation blocked by sandbox); no external photos/fonts, not field CWV', 'widths':{}, 'fail_open':{}, 'interactions':{}, 'assets':{}, 'synthetic_perf':{}, 'axe':'not run; axe-core not installed; manual screen-reader/Safari QA pending', 'source_hashes':{}}

def require(test,message):
    if not test:raise AssertionError(message)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for w in WIDTHS:
        page=browser.new_page(viewport={'width':w,'height':900},device_scale_factor=1)
        req=[]
        page.on('request',lambda request:req.append(request.url))
        page.evaluate("""window.__fvPerf={lcp:null,cls:0};try{new PerformanceObserver(l=>{for(let x of l.getEntries()) window.__fvPerf.lcp=x.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(let x of l.getEntries()) if(!x.hadRecentInput)window.__fvPerf.cls+=x.value}).observe({type:'layout-shift',buffered:true})}catch(e){window.__fvPerf.error=String(e)}""")
        page.set_content(HTML,wait_until='load')
        page.wait_for_timeout(150)
        summary=page.evaluate("""()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,stages:document.querySelectorAll('[data-ex2-stage]').length,atlas:document.querySelectorAll('[data-ex2-atlas-item]').length,images:document.querySelectorAll('img').length,main:!!document.querySelector('main'),toolsHidden:document.querySelector('[data-ex2-atlas-tools]').hidden})""")
        require(summary['scroll']<=summary['width']+1,f'horizontal overflow {w}: {summary}')
        require(summary['stages']==6 and summary['atlas']==6 and summary['images']==0,f'incomplete {w}: {summary}')
        require(not summary['toolsHidden'],f'filter not active {w}')
        path=OUT/f'apollo-atlas-{w}.png'
        page.screenshot(path=str(path),full_page=True,animations='disabled')
        results['widths'][str(w)]={**summary,'screenshot':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':path.stat().st_size}
        requests=[r for r in req if not r.startswith('data:')]
        require(not requests,f'unexpected remote asset request {requests}')
        results['assets'][str(w)]={'requested_external_assets':len(requests)}
        if w==1440:
            page.evaluate("document.querySelector('#source-05 summary').focus()")
            page.keyboard.press('Enter')
            require(page.locator('#source-05').evaluate('(el)=>el.open'),'Native source drawer keyboard opening failed')
            page.keyboard.press('Enter')
            require(not page.locator('#source-05').evaluate('(el)=>el.open'),'Native source drawer keyboard closing failed')
            page.locator('#atlas-search').fill('Franklin')
            require(page.locator('[data-ex2-atlas-item]:visible').count()==1,'Atlas search should find 1 Franklin case')
            require('1 of 6' in page.locator('[data-ex2-atlas-status]').inner_text(),'Live count did not update')
            page.locator('#atlas-search').fill('')
            page.locator('#atlas-filter').select_option('disasters')
            require(page.locator('[data-ex2-atlas-item]:visible').count()==3,'Disasters filter should show three cases')
            page.locator('#atlas-search').fill('zzzz-no-such-entry')
            require(page.locator('[data-ex2-atlas-item]:visible').count()==0,'Empty search should show zero')
            require(page.locator('[data-ex2-atlas-empty]').is_visible(),'Empty-state not visible')
            page.locator('#atlas-filter').select_option('all')
            page.locator('#atlas-search').fill('')
            require(page.locator('[data-ex2-atlas-item]:visible').count()==6,'Clear filters should restore six')
            page.locator('a[href="#stage-04"]').click()
            require(page.evaluate('location.hash')=='#stage-04','Chronology anchor failed')
            results['interactions']={'native_source_keyboard_open_close':True,'filter_disasters':3,'search_franklin':1,'empty_state':True,'reset':6,'chronology_anchor':True}
            perf=page.evaluate('window.__fvPerf||{lcp:null,cls:null}')
            results['synthetic_perf']={'synthetic_headless_chromium_lcp_ms':perf.get('lcp'),'synthetic_headless_chromium_cls':perf.get('cls'),'not_field_metric':True,'notes':'set_content() no network/photos/remote fonts; these synthetic results do not estimate WordPress p75 LCP/INP/CLS.'}
        page.close()
    # no-JS fallback: complete content, no broken/misleading filtered views
    page=browser.new_page(viewport={'width':390,'height':900},java_script_enabled=False)
    page.set_content(HTML,wait_until='load')
    require(page.locator('[data-ex2-stage]').count()==6,'No JS lost chapters')
    require(page.locator('[data-ex2-atlas-item]:visible').count()==6,'No JS lost atlas entries')
    require(not page.locator('[data-ex2-atlas-tools]').is_visible(),'No JS exposes inactive controls')
    page.locator('#source-03 summary').click()
    require(page.locator('#source-03').get_attribute('open') is not None,'No-JS native source disclosure failed')
    results['fail_open']['javascript_disabled']='pass';page.close()
    for label,script in [('observer_missing','window.IntersectionObserver=undefined'),('observer_throws',"window.IntersectionObserver=class{constructor(){throw new Error('injected')}}")]:
        page=browser.new_page(viewport={'width':768,'height':900})
        page.evaluate("() => {"+script+";}")
        page.set_content(HTML,wait_until='load')
        require(page.locator('[data-ex2-stage]:visible').count()==6,f'{label} hid stages')
        require(page.locator('[data-ex2-atlas-item]:visible').count()==6,f'{label} hid atlas')
        require(page.locator('[data-ex2-rail-link][aria-current]').count()==0,f'{label} left a stale location marker')
        results['fail_open'][label]='pass';page.close()
    # 200% CSS zoom on an intended wide viewport, preserving readable stage controls
    page=browser.new_page(viewport={'width':1440,'height':900})
    page.set_content(HTML,wait_until='load')
    page.evaluate("document.documentElement.style.zoom='2'")
    page.wait_for_timeout(100)
    zoom=page.evaluate("({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth})")
    require(zoom['scroll']<=zoom['width']+1,f'200% zoom overflow: {zoom}')
    results['fail_open']['css_zoom_200pct']='pass';page.close()
    # reduced motion; proves CSS preference is in effect, not actual screen reader behavior
    page=browser.new_page(viewport={'width':360,'height':900},reduced_motion='reduce')
    page.set_content(HTML,wait_until='load')
    behavior=page.evaluate('getComputedStyle(document.documentElement).scrollBehavior')
    require(behavior=='auto','Reduced-motion scroll remains smooth')
    results['fail_open']['prefers_reduced_motion']='pass';page.close()
    browser.close()
for f in [ROOT/'render.py',ROOT/'records.json',ROOT/'assets'/'app.css',ROOT/'assets'/'app.js',ROOT/'index.html']:
    results['source_hashes'][str(f.relative_to(ROOT))]=hashlib.sha256(f.read_bytes()).hexdigest()
(OUT.parent/'QA_RESULTS.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print('REAL BROWSER QA PASS',json.dumps({k:results[k] for k in ('interactions','fail_open','synthetic_perf')},indent=2))
print('SCREENSHOTS',len(results['widths']),'WIDTHS',WIDTHS)
