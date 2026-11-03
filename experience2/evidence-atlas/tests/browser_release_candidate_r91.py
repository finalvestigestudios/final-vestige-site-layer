#!/usr/bin/env python3
"""Real Chromium four-view Apollo QA: network egress, no-JS, keyboard, axe and print.

This is independent lab acceptance, never hosted WordPress or manual AT proof.
"""
from __future__ import annotations
import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import sys
from threading import Thread
from playwright.sync_api import sync_playwright

PAGES = {
    'R89_REVIEW_HUB.html':'r89-source-',
    'R88_READING_ROOM.html':'r88-',
    'R87_PHOTOGRAPH_DATE_RAIL.html':'r87-record-',
    'R85_NASA_SOURCE_REVIEW.html':'r85-source-',
}
WIDTHS = (320,390,768,1440,1920)
TRACE={'page':'NONE','case':'NOT_STARTED','gate':'INIT'}


def digest(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(src:Path, out:Path, axe:Path, executable:str|None=None)->dict:
    receipt=json.loads((src/'R91_ASSET_BOUNDARY_RECEIPT.json').read_text('utf8'))
    inherited=json.loads((src/'R89_INTEGRITY_RECEIPT.json').read_text('utf8'))
    urls=inherited['source_urls_by_id']
    assert receipt['release']=='STAGING_HOLD' and receipt['network_asset_dependencies']==0
    assert len(urls)==6 and len(inherited['record_source_bindings'])==24
    assert axe.is_file(), 'R91_AXE_BINARY_MISSING'
    out.mkdir(parents=True,exist_ok=True)
    class Silent(SimpleHTTPRequestHandler):
        def log_message(self,*args): pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Silent,directory=str(src.resolve())))
    Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}'
    observations=[]; screenshots={}; pdfs={}
    try:
        with sync_playwright() as p:
            config={'headless':True}
            if executable: config.update(executable_path=executable,args=['--no-sandbox'])
            browser=p.chromium.launch(**config)
            for name, prefix in PAGES.items():
                for width in WIDTHS:
                    for js in (False,True):
                        TRACE.update(page=name,case=f'{width}/JS={js}',gate='CONTEXT')
                        ctx=browser.new_context(viewport={'width':width,'height':900},
                            java_script_enabled=js,reduced_motion='reduce',
                            has_touch=width<=390,is_mobile=width<=390)
                        if js:
                            ctx.add_init_script('''(() => {
                              window.__apolloLab={lcp: null,cls:0};
                              try{new PerformanceObserver(l=>{for(const e of l.getEntries())
                                window.__apolloLab.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});}catch(_){}
                              try{new PerformanceObserver(l=>{for(const e of l.getEntries())
                                if(!e.hadRecentInput)window.__apolloLab.cls+=e.value;}).observe({type:'layout-shift',buffered:true});}catch(_){}
                            })();''')
                        page=ctx.new_page()
                        bad=[]
                        page.on('pageerror',lambda e:bad.append('SCRIPT_ERROR'))
                        def traffic(route):
                            if not route.request.url.startswith(base+'/'):
                                bad.append('UNEXPECTED_OUTBOUND_REQUEST')
                                route.abort()
                            else: route.continue_()
                        page.route(re.compile('^https?://'),traffic)
                        TRACE['gate']='LOAD_AND_CARD_CUSTODY'
                        response=page.goto(base+'/'+name,wait_until='load')
                        assert response and response.status==200,'R91_NOT_HTTP_200'
                        assert page.locator('article').count()==6, 'R91_NOT_SIX_ARTICLES'
                        assert page.locator('article details').count()==6,'R91_MISSING_SOURCE_DRAWER'
                        assert page.locator('img,iframe,picture,video,svg,[data-lat],[data-lon],[data-geo-edge]').count()==0,'R91_UNREVIEWED_MEDIA_GEO'
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+2'), 'R91_HORIZONTAL_OVERFLOW'
                        for rid, href in sorted(urls.items()):
                            card=page.locator('#'+prefix+rid)
                            assert card.count()==1,'R91_SOURCE_ID_MISSING'
                            assert card.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==1,'R91_NASA_LINK_NOT_UNIQUE'
                            assert card.locator('a[href^="https://www.nasa.gov/image-detail/"]').get_attribute('href')==href,'R91_NASA_LINK_MISATTRIBUTED'
                        assert not bad,'R91_NETWORK_OR_SCRIPT_ERROR'
                        TRACE['gate']='NATIVE_KEYBOARD'
                        summary=page.locator('article details summary').first
                        summary.focus()
                        detail=page.locator('article details').first
                        first=detail.evaluate('(d)=>d.open')
                        page.keyboard.press('Enter')
                        assert detail.evaluate('(d)=>d.open') != first,'R91_ENTER_DID_NOT_TOGGLE'
                        page.keyboard.press('Space')
                        assert detail.evaluate('(d)=>d.open') == first,'R91_SPACE_DID_NOT_TOGGLE'
                        observation={'page':name,'width':width,'javascript':js,
                                     'source_cards':6,'keyboard_enter_space':True,
                                     'no_horizontal_overflow':True,'unexpected_outbound':0,
                                     'axe_violations':None,'axe_passes':None,'lcp_ms':None,'cls':None}
                        TRACE['gate']='PROGRESSIVE_ENHANCEMENT'
                        if name=='R88_READING_ROOM.html':
                            compare=page.locator('#r88-compare')
                            if js:
                                assert compare.is_visible(),'R91_JS_COMPARE_NOT_VISIBLE'
                                checkboxes=page.locator('input.compare-choice, .compare-choice input')
                                assert checkboxes.count()==6,'R91_COMPARE_CHOICES_MISSING'
                                checkboxes.nth(0).check()
                                checkboxes.nth(1).check()
                                assert page.locator('.comparison .comparison-card').count()==2,'R91_COMPARISON_NOT_TWO'
                                page.locator('#r88-compare button.clear').click()
                                assert page.locator('.comparison .comparison-card').count()==0,'R91_CLEAR_NOT_EFFECTIVE'
                            else:
                                assert compare.is_hidden(),'R91_NO_JS_COMPARE_NOT_HIDDEN'
                                assert page.locator('article').count()==6,'R91_NO_JS_EVIDENCE_INCOMPLETE'
                        TRACE['gate']='AXE_AND_CORE_WEB_VITALS_LAB'
                        if js:
                            page.reload(wait_until='load')
                            page.wait_for_timeout(250)
                            perf=page.evaluate('window.__apolloLab')
                            assert perf and perf['lcp'] is not None and 0 < perf['lcp']<=2500, 'R91_LOCAL_LCP_LIMIT'
                            assert 0<=perf['cls']<=.1, 'R91_LOCAL_CLS_LIMIT'
                            observation['lcp_ms']=round(perf['lcp'],2)
                            observation['cls']=perf['cls']
                            if width in (390,1440):
                                page.add_script_tag(path=str(axe))
                                results=page.evaluate('''async ()=>{
                                  const a=await axe.run(document,{runOnly:{type:'tag',values:
                                    ['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
                                  return {violations:a.violations.map(x=>x.id),passes:a.passes.length};
                                }''')
                                assert not results['violations'], 'R91_AXE_VIOLATIONS:'+','.join(results['violations'])
                                observation['axe_violations']=0
                                observation['axe_passes']=results['passes']
                                shot=out/f'R91_{name[:-5]}_{width}.png'
                                page.screenshot(path=str(shot),full_page=True,animations='disabled')
                                screenshots[shot.name]=digest(shot)
                                if width==1440:
                                    TRACE['gate']='NATIVE_PRINT_SOURCE_CUSTODY'
                                    document=out/f'R91_{name[:-5]}.pdf'
                                    page.pdf(path=str(document),format='A4',print_background=True)
                                    import fitz
                                    with fitz.open(document) as pdf:
                                        content=re.sub(r'\s+','', ''.join(x.get_text() for x in pdf))
                                        assert len(pdf)>0,'R91_EMPTY_PDF'
                                        assert all(u in content for u in urls.values()),'R91_PRINT_NASA_URL_MISSING'
                                        pdfs[document.name]={'pages':len(pdf),'sha256':digest(document)}
                        assert not bad,'R91_NETWORK_OR_SCRIPT_ERROR'
                        observations.append(observation)
                        ctx.close()
                TRACE.update(page=name,case='390/FORCED',gate='FORCED_COLORS')
                ctx=browser.new_context(viewport={'width':390,'height':900},forced_colors='active',reduced_motion='reduce')
                page=ctx.new_page()
                page.goto(base+'/'+name,wait_until='load')
                page.locator('article details summary').first.click()
                assert page.locator('article details').first.evaluate('(d)=>d.open'),'R91_FORCED_COLOR_SOURCE_NOT_OPEN'
                shot=out/f'R91_{name[:-5]}_FORCED_390.png'
                page.screenshot(path=str(shot),full_page=True,animations='disabled')
                screenshots[shot.name]=digest(shot)
                ctx.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()
    assert len(observations)==40 and len(screenshots)==12 and len(pdfs)==4,'R91_EVIDENCE_COUNT_INCOMPLETE'
    report={'schema':'fv.apollo.r91.full-matrix.chromium.v1','release':'STAGING_HOLD',
            'hosted_wordpress_verified':False,'manual_screen_reader_verified':False,
            'local_browser_cases':len(observations),'axe_scans':8,
            'observations':observations,'screenshots':screenshots,'pdfs':pdfs}
    (out/'R91_BROWSER_MATRIX_RECEIPT.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    return report

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--src',type=Path,required=True)
    a.add_argument('--out',type=Path,required=True)
    a.add_argument('--axe',type=Path,required=True)
    a.add_argument('--chromium')
    v=a.parse_args()
    try:
        r=run(v.src,v.out,v.axe,v.chromium)
        print('R91 REAL CHROMIUM:',r['local_browser_cases'],'cases,',r['axe_scans'],'axe scans, 4 PDFs: STAGING HOLD')
    except Exception:
        print('R91_BROWSER_HOLD:'+TRACE['page']+':'+TRACE['case']+':'+TRACE['gate'],file=sys.stderr)
        raise SystemExit(1)
