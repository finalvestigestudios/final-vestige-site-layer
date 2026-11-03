#!/usr/bin/env python3
"""Apollo R92 genuine Chromium 40-case route, NASA custody, axe, LCP/CLS, print QA."""
from __future__ import annotations
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
import hashlib,json,re,sys

PAGES={'R89_REVIEW_HUB.html':'r89-source-','R88_READING_ROOM.html':'r88-',
       'R87_PHOTOGRAPH_DATE_RAIL.html':'r87-record-','R85_NASA_SOURCE_REVIEW.html':'r85-source-'}
WIDTHS=(320,390,768,1440,1920)
TRACE={'view':'NONE','case':'INIT','gate':'INIT'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run(src:Path,out:Path,axe:Path,chromium:str|None=None)->dict:
    src=src.resolve();out=out.resolve()
    custody=json.loads((src/'R92_RECIPROCAL_ROUTES_RECEIPT.json').read_text('utf8'))
    urls=json.loads((src/'R89_INTEGRITY_RECEIPT.json').read_text('utf8'))['source_urls_by_id']
    assert custody['release']=='STAGING_HOLD' and custody['verified_new_reciprocal_routes']==54
    assert len(urls)==6 and axe.is_file()
    out.mkdir(parents=True,exist_ok=True)
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(src)))
    Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}/'
    report=[];screenshots={};pdfs={};scans=0;clicks=0
    try:
        with sync_playwright() as p:
            conf={'headless':True}
            if chromium:conf.update(executable_path=chromium,args=['--no-sandbox'])
            browser=p.chromium.launch(**conf)
            for view,prefix in PAGES.items():
                for width in WIDTHS:
                    for js in (False,True):
                        TRACE.update(view=view,case=f'{width}/JS={js}',gate='INIT')
                        ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                            is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce')
                        if js:
                            ctx.add_init_script("""(() => {
                              window.__fvMetrics={lcp:null,cls:0};
                              try{new PerformanceObserver(x=>{for(const e of x.getEntries())window.__fvMetrics.lcp=e.startTime})
                                 .observe({type:'largest-contentful-paint',buffered:true})}catch(_){}
                              try{new PerformanceObserver(x=>{for(const e of x.getEntries())if(!e.hadRecentInput)window.__fvMetrics.cls+=e.value})
                                 .observe({type:'layout-shift',buffered:true})}catch(_){}
                            })();""")
                        page=ctx.new_page();errors=[]
                        page.on('pageerror',lambda _:errors.append('SCRIPT_ERROR'))
                        def route(r):
                            if r.request.url.startswith(base):r.continue_()
                            else:errors.append('UNEXPECTED_OUTBOUND');r.abort()
                        page.route(re.compile('^https?://'),route)
                        TRACE['gate']='SOURCE_AND_LAYOUT'
                        response=page.goto(base+view,wait_until='load')
                        assert response and response.status==200,'HTTP_200'
                        assert page.locator('article').count()==6,'SIX_RECORDS'
                        assert not page.locator('img,svg,video,iframe,canvas,[data-lat],[data-lon],[data-geo-edge]').count(),'NO_MEDIA_GEO'
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),'NO_OVERFLOW'
                        for n in range(1,7):
                            rid=f'{n:02}';card=page.locator('#'+prefix+rid)
                            assert card.count()==1,'UNIQUE_RECORD'
                            nasa=card.locator('a[href^="https://www.nasa.gov/image-detail/"]')
                            assert nasa.count()==1 and nasa.get_attribute('href')==urls[rid],'NASA_SOURCE_CUSTODY'
                            routes=card.locator('nav.per-source a[href$="'+rid+'"]') if view=='R89_REVIEW_HUB.html' else card.locator('nav.r92-evidence-routes a')
                            assert routes.count()==3,'THREE_OTHER_VIEWS'
                            for link in routes.all():
                                target=link.get_attribute('href')
                                assert '#' in target,'ANCHOR_PRESENT'
                                file,anchor=target.split('#',1)
                                assert file in PAGES and file!=view and anchor==PAGES[file]+rid,'SAME_RECORD_ONLY'
                                assert link.evaluate('(e)=>e.getBoundingClientRect().height')>=42,'TOUCH_TARGET'
                        assert not errors,'NO_NETWORK_JS_ERRORS'
                        TRACE['gate']='DISCLOSURE_KEYBOARD'
                        details=page.locator('article details').first
                        original=details.evaluate('(e)=>e.open')
                        details.locator('summary').focus()
                        page.keyboard.press('Enter')
                        assert details.evaluate('(e)=>e.open')!=original,'ENTER'
                        page.keyboard.press('Space')
                        assert details.evaluate('(e)=>e.open')==original,'SPACE'
                        TRACE['gate']='REAL_ROUTE_NAVIGATION'
                        source=page.locator('#'+prefix+'03')
                        link=(source.locator('nav.per-source a[href^="R88_READING_ROOM.html#"]').first
                              if view=='R89_REVIEW_HUB.html' else source.locator('nav.r92-evidence-routes a').first)
                        target=link.get_attribute('href');dest,frag=target.split('#',1)
                        TRACE['gate']='NAV_ACTIVATE_TOUCH_OR_POINTER'
                        if width<=390:link.tap()
                        else:link.click()
                        TRACE['gate']='NAV_WAIT_FOR_TARGET_URL'
                        page.wait_for_url('**/'+dest+'#'+frag,wait_until='load',timeout=12000)
                        TRACE['gate']='NAV_TARGET_PATH'
                        assert urlparse(page.url).path.endswith('/'+dest),'NAVIGATION_DESTINATION'
                        TRACE['gate']='NAV_TARGET_FRAGMENT'
                        assert page.evaluate('location.hash')=='#'+frag,'NAVIGATION_FRAGMENT'
                        TRACE['gate']='NAV_TARGET_ELEMENT'
                        assert page.locator('#'+frag).count()==1,'FRAGMENT_EXISTS'
                        clicks+=1
                        TRACE['gate']='AXE_PERFORMANCE_PRINT'
                        page.goto(base+view,wait_until='load')
                        observation={'view':view,'width':width,'javascript':js,'source_cards_checked':6,
                                     'routes_checked':18,'real_navigation':True,'unexpected_requests':0,
                                     'lcp_ms':None,'cls':None,'axe_violations':None}
                        if js:
                            page.wait_for_timeout(250)
                            metrics=page.evaluate('window.__fvMetrics')
                            assert metrics and metrics['lcp'] and 0<metrics['lcp']<=2500,'LCP_LAB'
                            assert 0<=metrics['cls']<=.1,'CLS_LAB'
                            observation['lcp_ms']=round(metrics['lcp'],2)
                            observation['cls']=metrics['cls']
                            if width in (390,1440):
                                page.add_script_tag(path=str(axe))
                                a=page.evaluate("""async()=>{const x=await axe.run(document,{runOnly:{type:'tag',values:
                                    ['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return {bad:x.violations.map(v=>v.id),good:x.passes.length}}""")
                                assert not a['bad'],'AXE_VIOLATION'
                                observation['axe_violations']=0;observation['axe_passes']=a['good'];scans+=1
                                shot=out/('R92_'+view[:-5]+f'_{width}.png')
                                page.screenshot(path=str(shot),full_page=True,animations='disabled')
                                screenshots[shot.name]=sha(shot)
                                if width==1440:
                                    pdf=out/('R92_'+view[:-5]+'.pdf')
                                    page.pdf(path=str(pdf),format='A4',print_background=True)
                                    import fitz
                                    with fitz.open(pdf) as document:
                                        extracted=re.sub(r'\s+','', ''.join(x.get_text() for x in document))
                                        assert all(url in extracted for url in urls.values()),'PDF_NASA_URLS'
                                        assert 'INDIVIDUALREVIEWREQUIRED' in extracted,'PDF_RIGHTS_HOLD'
                                        pdfs[pdf.name]={'pages':len(document),'sha256':sha(pdf)}
                        assert not errors,'NO_OUTBOUND_OR_JS_ERRORS'
                        report.append(observation);ctx.close()
                TRACE.update(view=view,case='FORCED_390',gate='FORCED_COLORS')
                ctx=browser.new_context(viewport={'width':390,'height':900},forced_colors='active',reduced_motion='reduce')
                page=ctx.new_page();page.goto(base+view,wait_until='load')
                if view!='R89_REVIEW_HUB.html':
                    focus=page.locator('nav.r92-evidence-routes a').first
                    focus.focus()
                    assert focus.evaluate('(e)=>document.activeElement===e'),'FORCED_FOCUS'
                path=out/('R92_'+view[:-5]+'_FORCED_390.png')
                page.screenshot(path=str(path),full_page=True,animations='disabled')
                screenshots[path.name]=sha(path);ctx.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()
    assert len(report)==40 and clicks==40 and scans==8 and len(screenshots)==12 and len(pdfs)==4
    receipt={'schema':'fv.apollo.r92.real-chromium.v1','release':'STAGING_HOLD',
        'hosted_wordpress_verified':False,'manual_screen_reader_verified':False,
        'local_cases':len(report),'real_route_navigations':clicks,'axe_scans':scans,
        'screenshots':screenshots,'pdfs':pdfs,'observations':report}
    (out/'R92_REAL_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--src',type=Path,required=True)
    a.add_argument('--out',type=Path,required=True)
    a.add_argument('--axe',type=Path,required=True)
    a.add_argument('--chromium')
    args=a.parse_args()
    try:
        result=run(args.src,args.out,args.axe,args.chromium)
        print('R92:',result['local_cases'],'contexts,',result['real_route_navigations'],'navigations; STAGING HOLD')
    except Exception:
        print('R92_BROWSER_HOLD:'+':'.join(TRACE.values()),file=sys.stderr)
        raise SystemExit(1)
