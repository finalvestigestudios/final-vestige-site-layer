#!/usr/bin/env python3
"""R93 genuine Chromium/axe, responsive, no-JS, touch, PDF and web-vitals lab gates."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from pathlib import Path
from playwright.sync_api import sync_playwright

def sha(p:Path):return hashlib.sha256(p.read_bytes()).hexdigest()

def run(src:Path,out:Path,axe:Path,chromium:str|None=None):
    src=src.resolve();out.mkdir(parents=True,exist_ok=True)
    data=json.loads((src/'R93_SOURCE_PASSPORTS.json').read_text())
    rec=json.loads((src/'R93_PASSPORT_RECEIPT.json').read_text())
    assert rec['release']=='STAGING_HOLD' and rec['photographic_rights_cleared']==0
    assert len(data['records'])==6 and data['photo_reuse_approved'] is False
    for f,d in rec['files'].items():assert sha(src/f)==d
    assert axe.is_file()
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(src)))
    Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}/'
    cases=[];screens={};pdfs={};scans=0
    try:
        with sync_playwright() as pw:
            opts={'headless':True}
            if chromium:opts.update(executable_path=chromium,args=['--no-sandbox'])
            browser=pw.chromium.launch(**opts)
            for width in (320,390,768,1440,1920):
                for js in (False,True):
                    ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                        is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce')
                    if js:
                        ctx.add_init_script('''window.__fvPerf={lcp:null,cls:0};
                        try{new PerformanceObserver(v=>{for(const e of v.getEntries())window.__fvPerf.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(_){}
                        try{new PerformanceObserver(v=>{for(const e of v.getEntries())if(!e.hadRecentInput)window.__fvPerf.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(_){}''')
                        ctx.add_init_script('''Object.defineProperty(navigator,"clipboard",{configurable:true,value:{writeText:async t=>{window.__copied=t}}})''')
                    page=ctx.new_page();errors=[]
                    page.on('pageerror',lambda _:errors.append('JS_ERROR'))
                    def route(r):
                        if r.request.url.startswith(base):r.continue_()
                        else:errors.append('UNEXPECTED_EXTERNAL_REQUEST');r.abort()
                    page.route(re.compile('^https?://'),route)
                    response=page.goto(base+'R93_SOURCE_PASSPORTS.html',wait_until='load')
                    assert response and response.status==200
                    assert page.locator('article.card').count()==6
                    assert not page.locator('img,svg,canvas,video,iframe,[data-lat],[data-lon],[data-geo-edge]').count()
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),f'OVERFLOW:{width}/{js}'
                    assert 'Zero of six' in page.locator('.hold').inner_text()
                    for r in data['records']:
                        c=page.locator('#passport-'+r['id'])
                        assert c.count()==1
                        assert r['title'] in c.inner_text() and r['cannot'] in c.inner_text()
                        nasa=c.locator('a[href^="https://www.nasa.gov/image-detail/"]')
                        assert nasa.count()==2 and all(a.get_attribute('href')==r['url'] for a in nasa.all())
                        links=c.locator('nav.routes a')
                        assert links.count()==4
                        assert all(l.evaluate('(e)=>e.getBoundingClientRect().height')>=42 for l in links.all())
                    summary=page.locator('#passport-02 summary')
                    summary.focus();page.keyboard.press('Enter')
                    assert page.locator('#passport-02 details').evaluate('(e)=>e.open')
                    page.keyboard.press('Space')
                    assert not page.locator('#passport-02 details').evaluate('(e)=>e.open')
                    link=page.locator('a[href="#passport-06"]').first
                    if width<=390:link.tap()
                    else:link.click()
                    assert page.evaluate('location.hash')=='#passport-06'
                    obs={'width':width,'js':js,'passports':6,'lcp_ms':None,'cls':None,'axe_violations':None}
                    if js:
                        page.locator('#passport-03 button.copy').click()
                        page.wait_for_function('document.querySelector("#passport-03 .copy-state").textContent.includes("Reference copied")')
                        assert data['records'][2]['url'] in page.evaluate('window.__copied')
                        page.wait_for_timeout(250)
                        metric=page.evaluate('window.__fvPerf')
                        assert metric['lcp'] is not None and 0<metric['lcp']<=2500,'LCP_LAB'
                        assert 0<=metric['cls']<=.1,'CLS_LAB'
                        obs['lcp_ms']=round(metric['lcp'],2);obs['cls']=metric['cls']
                        if width in (390,1440):
                            page.add_script_tag(path=str(axe))
                            a=page.evaluate('''async()=>{const x=await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa","wcag22aa"]}});return {bad:x.violations.map(v=>v.id),passes:x.passes.length}}''')
                            assert not a['bad'],a
                            scans+=1;obs['axe_violations']=0;obs['axe_passes']=a['passes']
                            png=out/f'R93_SOURCE_PASSPORTS_{width}.png'
                            page.screenshot(path=str(png),full_page=True,animations='disabled')
                            screens[png.name]=sha(png)
                            if width==1440:
                                pdf=out/'R93_SOURCE_PASSPORTS_PRINT.pdf'
                                page.pdf(path=str(pdf),format='A4',print_background=True)
                                import fitz
                                with fitz.open(pdf) as doc:
                                    text=''.join(''.join(p.get_text().split()) for p in doc)
                                    assert all(''.join(r['url'].split()) in text for r in data['records']),'PDF_NASA_SOURCES'
                                    assert text.count('INDIVIDUALREVIEWREQUIRED')>=6,'PDF_RIGHTS_HOLD'
                                    pdfs[pdf.name]={'pages':len(doc),'sha256':sha(pdf)}
                    assert not errors,errors
                    cases.append(obs);ctx.close()
            ctx=browser.new_context(viewport={'width':390,'height':900},forced_colors='active',reduced_motion='reduce')
            page=ctx.new_page();page.goto(base+'R93_SOURCE_PASSPORTS.html',wait_until='load')
            page.locator('#passport-01 summary').focus()
            assert page.locator('#passport-01 summary').evaluate('(e)=>document.activeElement===e')
            png=out/'R93_SOURCE_PASSPORTS_FORCED_390.png'
            page.screenshot(path=str(png),full_page=True,animations='disabled')
            screens[png.name]=sha(png);ctx.close();browser.close()
    finally:
        server.shutdown();server.server_close()
    assert len(cases)==10 and scans==2 and len(screens)==3 and len(pdfs)==1
    receipt={'schema':'fv.apollo.r93.chromium.v1','release':'STAGING_HOLD','cases':cases,
      'axe_scans':scans,'screenshots':screens,'pdfs':pdfs,
      'hosted_wordpress_verified':False,'manual_screen_reader_verified':False}
    (out/'R93_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--src',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--axe',type=Path,required=True);p.add_argument('--chromium');a=p.parse_args()
    try:
        r=run(a.src,a.out,a.axe,a.chromium)
        print('R93',len(r['cases']),'Chromium contexts,',r['axe_scans'],'axe scans / STAGING HOLD')
    except Exception as e:
        print('R93_BROWSER_HOLD:'+str(e),file=sys.stderr);raise
