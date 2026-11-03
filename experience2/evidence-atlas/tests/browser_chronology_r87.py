#!/usr/bin/env python3
"""Actual Chromium staging checks: 320–1920, no-JS, keyboard/touch, axe, lab LCP/CLS and native PDF."""
import argparse
import hashlib
import json
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
WIDTHS=(320,390,768,1440,1920)
EXPECTED=('https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
          'https://www.nasa.gov/image-detail/amf-s67-15717/',
          'https://www.nasa.gov/image-detail/amf-s66-58038/',
          'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
          'https://www.nasa.gov/image-detail/amf-s67-21294/',
          'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/')
CATALOG=('S67-19766','S67-15717','S66-58038',
         'KSC-20170124-PH_KLS01_0164','S67-21294','KSC-20170124-PH_KLS01_0090')

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def run(src,out,axe=None,chromium_path=None):
    out.mkdir(parents=True,exist_ok=True)
    origin=src/'R87_PHOTOGRAPH_DATE_RAIL.html'
    assert origin.is_file(),'R87_HTML_NOT_BUILT'
    if axe is not None: assert axe.is_file(),'R87_AXE_NOT_INSTALLED'
    cases,screens=[],{}
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(src.resolve())))
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    with sync_playwright() as p:
        opts={'headless':True}
        if chromium_path:opts.update(executable_path=chromium_path,args=['--no-sandbox'])
        browser=p.chromium.launch(**opts)
        for width in WIDTHS:
            for js in (False,True):
                ctx=browser.new_context(viewport={'width':width,'height':900},
                     java_script_enabled=js,reduced_motion='reduce',
                     has_touch=width<=390,is_mobile=width<=390)
                if js:
                    ctx.add_init_script('''(()=>{window.__r87={lcp:null,cls:0};
                    try{new PerformanceObserver(l=>{const a=l.getEntries();
                    if(a.length)window.__r87.lcp=a[a.length-1].startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(_){}
                    try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__r87.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(_){}
                    })();''')
                page=ctx.new_page()
                errors,outbound=[],[]
                page.on('pageerror',lambda _:errors.append('SCRIPT_ERROR'))
                def route(r):
                    if not r.request.url.startswith(base+'/'):
                        outbound.append('REMOTE_REQUEST');r.abort()
                    else:r.continue_()
                page.route(re.compile(r'^https?://'),route)
                page.goto(base+'/R87_PHOTOGRAPH_DATE_RAIL.html',wait_until='load')
                page.wait_for_timeout(150)
                assert not errors and not outbound,'R87_SCRIPT_OR_EXTERNAL_NETWORK'
                assert page.locator('article.plate').count()==6,'R87_MISSING_PLATES'
                assert page.locator('details').count()==6,'R87_MISSING_SOURCE_DRAWERS'
                assert page.locator('time[datetime]').count()==4,'R87_INVENTED_DATE_OR_MISSING_MILESTONE'
                days=page.locator('time[datetime]').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("datetime"))')
                assert days==['1966-10-18','1967-01-03','1967-01-28','2017-01-24'],'R87_CHRONOLOGY_SORT'
                assert page.locator('#r87-unplaced .plate').count()==1,'R87_MONTH_ONLY_NOT_SEPARATED'
                assert page.locator('#r87-day-4 .plate').count()==2,'R87_SAME_DAY_NOT_GROUPED'
                assert page.locator('img,iframe,picture,video,[data-lat],[data-lon],[data-geo-edge]').count()==0,'R87_GEO_OR_MEDIA'
                links=page.locator('a.source').evaluate_all('(a)=>a.map(x=>x.getAttribute("href"))')
                assert set(links)==set(EXPECTED) and len(links)==6,'R87_NASA_SOURCE_SET'
                text=page.locator('body').inner_text()
                assert all(x in text for x in CATALOG),'R87_CATALOG_MISSING'
                assert '0/6 media reuse cleared' in text and 'provisional' in text.lower(),'R87_RIGHTS_HOLD_MISSING'
                assert 'Same date, no verified sequence' in text,'R87_SAME_DAY_WARNING'
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'),'R87_HORIZONTAL_OVERFLOW'
                page.locator('details summary').first.focus();page.keyboard.press('Enter')
                assert page.locator('details').first.evaluate('(el)=>el.open'),'R87_NATIVE_KEY_OPEN'
                page.keyboard.press('Enter')
                assert not page.locator('details').first.evaluate('(el)=>el.open'),'R87_NATIVE_KEY_CLOSE'
                page.locator('.rail-jumps a').last.click()
                assert page.evaluate('location.hash')=='#r87-unplaced','R87_JUMP_NAVIGATION'
                sizes=page.locator('a.source').evaluate_all('(nodes)=>nodes.map(n=>({h:n.getBoundingClientRect().height,w:n.getBoundingClientRect().width}))')
                assert all(x['h']>=43.5 and x['w']>=43.5 for x in sizes),'R87_TOUCH_TARGET'
                style=page.locator('.plate').first.evaluate('(n)=>getComputedStyle(n).backgroundColor')
                assert style!='rgba(0, 0, 0, 0)','R87_STYLESHEET_MISSING'
                case={'width':width,'js':js,'responsive':True,'no_horizontal_overflow':True,
                    'native_keyboard':True,'touch_target_44px':True,'source_set_preserved':True,
                    'axe_violations':None,'lab_lcp_ms':None,'lab_cls':None}
                if js:
                    if axe:
                        page.add_script_tag(path=str(axe))
                        report=page.evaluate('''async()=>{const r=await axe.run(document,{runOnly:{type:'tag',
                        values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                        return {violations:r.violations.map(v=>({id:v.id,nodes:v.nodes.length,impact:v.impact})),passes:r.passes.length}}''')
                        case['axe_violations']=report['violations'];case['axe_rules_passed']=report['passes']
                        assert not report['violations'],'R87_AXE_VIOLATIONS'
                    perf=page.evaluate('window.__r87')
                    case['lab_lcp_ms']=perf['lcp']
                    case['lab_cls']=perf['cls']
                    assert perf['cls']<=0.1,'R87_EXCESS_CLS'
                if js and width in (390,1440):
                    snap=out/f'R87_RAIL_{width}.png'
                    page.screenshot(path=str(snap),full_page=True,animations='disabled')
                    screens[str(width)]=digest(snap)
                    if width==1440:
                        pdf=out/'R87_RAIL_PRINT.pdf'
                        page.pdf(path=str(pdf),format='A4',print_background=True)
                        assert pdf.stat().st_size>5000,'R87_NATIVE_PDF_MISSING'
                        with fitz.open(pdf) as doc:
                            rendered=''.join(pg.get_text() for pg in doc)
                            combined=''.join(rendered.split())
                            assert all(''.join(url.split()) in combined for url in EXPECTED),'R87_PRINT_SOURCE_URL'
                            assert all(c in combined for c in CATALOG),'R87_PRINT_CATALOG'
                            assert '0/6mediareusecleared' in combined,'R87_PRINT_HOLD'
                            case['native_pdf_pages']=len(doc)
                        page.emulate_media(media='print')
                        assert page.locator('.hold').evaluate('(el)=>getComputedStyle(el).backgroundColor')=='rgb(255, 255, 255)','R87_PRINT_WARNING_CONTRAST'
                        page.emulate_media(media='screen')
                cases.append(case);ctx.close()
        forced=browser.new_context(viewport={'width':390,'height':850},forced_colors='active',reduced_motion='reduce')
        pforced=forced.new_page();pforced.goto(base+'/R87_PHOTOGRAPH_DATE_RAIL.html')
        pforced.locator('details summary').first.focus();pforced.keyboard.press('Enter')
        assert pforced.locator('details').first.evaluate('(n)=>n.open'),'R87_FORCED_COLOR_KEYBOARD'
        pforced.screenshot(path=str(out/'R87_RAIL_FORCED_390.png'),full_page=True)
        screens['forced_390']=digest(out/'R87_RAIL_FORCED_390.png')
        forced.close();browser.close()
    server.shutdown();server.server_close()
    receipt={'schema':'fv.apollo.r87.real-chromium.v1','release':'STAGING_HOLD','cases':cases,
        'screenshots_sha256':screens,'axe_status':'PASS' if axe else 'NOT_RUN_LOCAL',
        'production_cwv':False,'hosted_wordpress_tested':False,'site_writes':False}
    (out/'R87_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt

if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('--src',required=True,type=Path)
    cli.add_argument('--out',required=True,type=Path)
    cli.add_argument('--axe',type=Path)
    cli.add_argument('--chromium',type=str)
    a=cli.parse_args()
    r=run(a.src,a.out,a.axe,a.chromium)
    print('R87 genuine Chromium',len(r['cases']),'cases, STAGING HOLD')
