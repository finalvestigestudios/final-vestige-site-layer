#!/usr/bin/env python3
"""Chromium mock WordPress-shell acceptance, not installed WP or genuine axe."""
from pathlib import Path
import argparse, base64, hashlib, json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'dist/assets/atlas-scoped.css').read_bytes()
HTML=(ROOT/'dist/templates/atlas-fragment.html').read_text()
CSS_LINK='data:text/css;base64,'+base64.b64encode(CSS).decode()
CONTEXTS=[('320',320,True,{}),('360',360,True,{}),('390',390,True,{}),('768',768,True,{}),('1440',1440,True,{}),('1920',1920,True,{}),('320-nojs',320,False,{}),('390-nojs-nocss',390,False,{'nocss':True}),('390-forced',390,True,{'forced':True}),('390-reduced',390,True,{'reduced':True}),('390-touch',390,True,{'touch':True}),('640-200zoom',640,True,{'zoom':True})]
PERF='''<script>window.__fv_lab={lcp:null,cls:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__fv_lab.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__fv_lab.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}</script>'''
BASE='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
body{margin:0;color:rgb(30,60,90);background:rgb(235,241,248);font:18px/1.4 Arial}
#host-header,#host-footer{padding:12px;background:rgb(240,245,248)}
</style>__LINK__ __PERF__</head><body><header id="host-header">Simulated WordPress header</header><main id="host-main">__CONTENT__</main><footer id="host-footer">Simulated WordPress footer</footer></body></html>'''

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    tests=[];shots={};metrics=[];errors={}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-background-networking'])
        for name,width,js,opts in CONTEXTS:
            ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,has_touch=bool(opts.get('touch')),is_mobile=bool(opts.get('touch')),reduced_motion='reduce' if opts.get('reduced') else 'no-preference',forced_colors='active' if opts.get('forced') else 'none',device_scale_factor=1)
            p=ctx.new_page();exc=[];p.on('pageerror',lambda e:exc.append(str(e)))
            link='' if opts.get('nocss') else '<link data-fv-r185-style="head" rel="stylesheet" href="'+CSS_LINK+'">'
            shell=BASE.replace('__LINK__',link).replace('__PERF__',PERF if js else '').replace('__CONTENT__',HTML)
            p.set_content(shell,wait_until='load')
            if opts.get('zoom'):p.evaluate("document.getElementById('host-main').style.zoom='2'")
            def chk(c,label):
                tests.append({'case':name,'check':label,'pass':bool(c)})
                if not c:raise AssertionError(name+': '+label)
            chk(p.locator('.fv-apollo-atlas .rail li').count()==4,'four chronology dates')
            chk(p.locator('.fv-apollo-atlas .plate').count()==4,'four source-based evidence plates')
            chk(p.locator('.fv-apollo-atlas .source-card').count()==4,'four catalogued source cards')
            chk(p.locator('.fv-apollo-atlas details').count()==8,'eight native source disclosures')
            chk(p.locator('.fv-apollo-atlas a.cta').count()==1,'single relevant reading CTA')
            chk(p.locator('.fv-apollo-atlas script,.fv-apollo-atlas iframe,.fv-apollo-atlas img').count()==0,'no embedded unlicensed media or scripts')
            chk(p.locator('main').count()==1,'one host main landmark')
            chk('not conclusively' in p.locator('.fv-apollo-atlas').inner_text(),'unproven ignition identified as uncertain')
            chk(p.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth+2'),'no horizontal overflow')
            if not opts.get('forced'):
                chk(p.locator('#host-header').evaluate('(e)=>getComputedStyle(e).color')=='rgb(30, 60, 90)','styles do not leak to host')
            chk(not exc,'no page JavaScript errors')
            if not opts.get('nocss'):
                chk(p.locator('head link[data-fv-r185-style="head"]').count()==1,'CSS link exists before first document content')
                chk(p.locator('.fv-apollo-atlas').evaluate('(e)=>getComputedStyle(e).display')=='block','scoped CSS applied')
            if name=='390':
                p.locator('a[href="#fv-apollo-photo-aftermath"]').click()
                chk(p.url.endswith('#fv-apollo-photo-aftermath'),'dated chronology deep-link works')
                p.locator('#fv-apollo-photo-aftermath summary').click()
                chk(p.locator('#fv-apollo-photo-aftermath details').evaluate('(e)=>e.open'),'click opens source')
                p.locator('#fv-apollo-finding-fire summary').focus();p.keyboard.press('Enter')
                chk(p.locator('#fv-apollo-finding-fire details').evaluate('(e)=>e.open'),'keyboard opens source')
                p.set_content(shell,wait_until='load')
            if name=='390-touch':
                p.locator('#fv-apollo-photo-aftermath summary').tap()
                chk(p.locator('#fv-apollo-photo-aftermath details').evaluate('(e)=>e.open'),'touch opens source')
                p.set_content(shell,wait_until='load')
            if name=='390-forced':chk(p.evaluate("matchMedia('(forced-colors:active)').matches"),'forced color environment')
            if name=='390-reduced':chk(p.evaluate("matchMedia('(prefers-reduced-motion:reduce)').matches"),'reduced motion environment')
            if name=='320-nojs':chk(p.locator('#fv-apollo-finding-fire details').count()==1,'no JS retains disclosure semantics')
            p.screenshot(path=str(out/(name+'.png')),full_page=True,animations='disabled')
            shots[name]=hashlib.sha256((out/(name+'.png')).read_bytes()).hexdigest()
            if js:p.wait_for_timeout(200);metrics.append({'case':name,**p.evaluate('window.__fv_lab||{}')})
            errors[name]=exc;ctx.close()
        browser.close()
    receipt={'context_count':len(CONTEXTS),'passed':sum(x['pass'] for x in tests),'failed':sum(not x['pass'] for x in tests),'assertions':tests,'screenshot_sha256':shots,'lab_metrics':metrics,'page_errors':errors,'wordPress_installed':False,'axe_core_executed':False,'production_cwv':False}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',required=True);opts=a.parse_args();r=run(opts.out)
    print(json.dumps({'contexts':r['context_count'],'assertions':r['passed'],'lab_metrics':r['lab_metrics']},indent=2))
