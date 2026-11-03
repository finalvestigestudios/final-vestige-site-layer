#!/usr/bin/env python3
"""Genuine Chromium 320-1920, JS/no-JS, keyboard, touch, axe, CLS/LCP and print."""
import argparse
import hashlib
import json
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
import fitz
WIDTHS=(320,390,768,1440,1920)
TRACE={'case':'START','gate':'SETUP'}
NASA=('https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
      'https://www.nasa.gov/image-detail/amf-s67-15717/',
      'https://www.nasa.gov/image-detail/amf-s66-58038/',
      'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
      'https://www.nasa.gov/image-detail/amf-s67-21294/',
      'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/')
def checksum(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(root,out,axe=None,chromium=None):
    out.mkdir(parents=True,exist_ok=True)
    assert (root/'R88_READING_ROOM.html').is_file(),'R88_MISSING_BUILD'
    if axe:assert axe.is_file(),'R88_MISSING_AXE'
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*a):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root.resolve())))
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    cases=[];shots={};base=f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as p:
            opts={'headless':True}
            if chromium:opts.update(executable_path=chromium,args=['--no-sandbox'])
            browser=p.chromium.launch(**opts)
            for width in WIDTHS:
                for js in (False,True):
                    TRACE.update(case=str(width)+'px/'+('JS' if js else 'NOJS'),gate='CONTEXT')
                    context=browser.new_context(viewport={'width':width,'height':860},java_script_enabled=js,
                        reduced_motion='reduce',has_touch=width<=390,is_mobile=width<=390)
                    if js:context.add_init_script('''(()=>{window.__lab={lcp:null,cls:0};
                      try{new PerformanceObserver(l=>{const a=l.getEntries();if(a.length)window.__lab.lcp=a.at(-1).startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
                      try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__lab.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}
                      })()''')
                    page=context.new_page();errors=[];external=[]
                    page.on('pageerror',lambda _:errors.append('R88_SCRIPT_ERROR'))
                    def route(r):
                        if not r.request.url.startswith(base+'/'):
                            external.append('UNEXPECTED_OUTBOUND');r.abort()
                        else:r.continue_()
                    page.route(re.compile('^https?://'),route)
                    TRACE['gate']='LOAD'
                    page.goto(base+'/R88_READING_ROOM.html',wait_until='load')
                    TRACE['gate']='STATIC_SOURCE'
                    page.wait_for_timeout(120)
                    assert not errors and not external,'R88_BROWSER_NETWORK_OR_JS'
                    assert page.locator('article.record').count()==6,'R88_WRONG_RECORD_COUNT'
                    assert page.locator('.record details').count()==6,'R88_MISSING_NATIVE_DRAWERS'
                    assert set(page.locator('.record a.source').evaluate_all('(a)=>a.map(x=>x.href)'))==set(NASA),'R88_UNVERIFIED_NASA_LINKS'
                    assert page.locator('img,iframe,picture,video,[data-lat],[data-lon],[data-geo-edge]').count()==0,'R88_MEDIA_GEO'
                    assert 'S67-19766' in page.locator('body').inner_text(),'R88_PROVISIONAL_ID_MISSING'
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),'R88_HORIZONTAL_OVERFLOW'
                    TRACE['gate']='NATIVE_KEYBOARD'
                    page.locator('details summary').first.focus();page.keyboard.press('Enter')
                    assert page.locator('details').first.evaluate('n=>n.open'),'R88_NATIVE_ENTER_OPEN'
                    page.keyboard.press('Enter')
                    assert not page.locator('details').first.evaluate('n=>n.open'),'R88_NATIVE_ENTER_CLOSE'
                    case={'width':width,'js':js,'real_chromium':True,'drawer_keyboard':True,
                          'no_overflow':True,'source_links':6,'compare':None,'axe':None,'lcp_ms':None,'cls':None}
                    if js:
                        TRACE['gate']='TWO_SOURCE_COMPARE'
                        inputs=page.locator('label.compare-choice input')
                        assert inputs.count()==6 and inputs.first.is_visible(),'R88_COMPARE_NOT_ENHANCED'
                        inputs.nth(0).check();inputs.nth(1).check()
                        assert page.locator('.comparison-card').count()==2,'R88_COMPARE_PAIR'
                        assert 'S67-19766' in page.locator('.comparison').inner_text(),'R88_COMPARE_CUSTODY'
                        inputs.nth(2).check()
                        assert page.locator('.comparison-card').count()==2,'R88_THIRD_SELECTION_OVERFLOW'
                        assert not inputs.nth(0).is_checked(),'R88_OLDEST_NOT_DISPLACED'
                        page.locator('button.clear').click()
                        assert page.locator('.comparison-card').count()==0 and not inputs.nth(2).is_checked(),'R88_CLEAR'
                        case['compare']='PASS'
                        if axe:
                            TRACE['gate']='AXE_ACCESSIBILITY'
                            page.add_script_tag(path=str(axe))
                            result=page.evaluate('''async()=>{const x=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return {violations:x.violations.map(v=>({id:v.id,count:v.nodes.length})),passes:x.passes.length}}''')
                            assert not result['violations'],'R88_AXE_VIOLATIONS'
                            case['axe']=result
                        TRACE['gate']='PERFORMANCE_OBSERVERS'
                        lab=page.evaluate('window.__lab');case['lcp_ms']=lab['lcp'];case['cls']=lab['cls']
                        assert lab['cls'] is not None and lab['cls']<=0.1,'R88_CLS_GATE'
                        if width in (390,1440):
                            TRACE['gate']='SCREENSHOT_PRINT'
                            snap=out/f'R88_READER_{width}.png';page.screenshot(path=str(snap),full_page=True,animations='disabled')
                            shots[str(width)]=checksum(snap)
                            if width==1440:
                                pdf=out/'R88_READER_PRINT.pdf'
                                page.pdf(path=str(pdf),format='A4',print_background=True)
                                with fitz.open(pdf) as d:
                                    text='\n'.join(p.get_text() for p in d)
                                    assert all(url in text for url in NASA),'R88_NASA_URLS_LOST_IN_PRINT'
                                    assert 'INDIVIDUAL REVIEW REQUIRED' in text,'R88_RIGHTS_LOST_IN_PRINT'
                                    pages=len(d)
                    else:
                        TRACE['gate']='NOJS_FALLBACK'
                        assert page.locator('.compare-choice:visible').count()==0,'R88_NOJS_COMPARE_CONFUSION'
                        assert page.locator('.record a.source:visible').count()==6,'R88_NOJS_SOURCE_LOSS'
                    case['nojs_content']='PASS' if not js else 'N/A'
                    cases.append(case);context.close()
            TRACE.update(case='390px/FORCED',gate='FORCED_COLORS')
            context=browser.new_context(viewport={'width':390,'height':900},forced_colors='active',reduced_motion='reduce')
            p2=context.new_page();p2.goto(base+'/R88_READING_ROOM.html')
            p2.locator('label.compare-choice input').first.check()
            assert p2.locator('label.compare-choice input').first.is_checked(),'R88_FORCED_COLORS_COMPARE'
            p2.screenshot(path=str(out/'R88_READER_FORCED_390.png'),full_page=True)
            shots['forced_390']=checksum(out/'R88_READER_FORCED_390.png');context.close();browser.close()
    finally:server.shutdown();server.server_close()
    receipt={'schema':'fv.apollo.r88.browser.v1','release':'STAGING_HOLD',
         'cases':cases,'case_count':len(cases),'screenshots':shots,
         'printed_pages':pages,'pdf_sha256':checksum(out/'R88_READER_PRINT.pdf')}
    (out/'R88_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--src',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path);parser.add_argument('--axe',type=Path)
    parser.add_argument('--chromium',type=str)
    args=parser.parse_args()
    try:
        x=run(args.src,args.out,args.axe,args.chromium)
        print('R88: Chromium',x['case_count'],'configs passed, STAGING_HOLD')
    except Exception:
        print('R88_BROWSER_HOLD:'+TRACE['case']+':'+TRACE['gate'],file=__import__('sys').stderr)
        raise SystemExit(1)
