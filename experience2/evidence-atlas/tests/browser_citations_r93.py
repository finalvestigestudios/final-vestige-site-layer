#!/usr/bin/env python3
"""Genuine Chromium acceptance for source-register and CSV export (isolated only)."""
from __future__ import annotations
import argparse
import csv
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from pathlib import Path
import hashlib,io,json,re,sys
from playwright.sync_api import sync_playwright

WIDTHS=(320,390,768,1440,1920)
TRACE={'case':'START','gate':'START'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run(src:Path,out:Path,axe:Path,chromium:str|None=None):
    src=src.resolve();out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((src/'R93_CITATION_RECEIPT.json').read_text())
    assert manifest['record_count']==6 and manifest['source_view_bindings']==24
    assert all(sha(src/f)==d for f,d in manifest['generated_files'].items())
    assert axe.is_file()
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*a):pass
    http=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(src)))
    Thread(target=http.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{http.server_port}/'
    reports=[];images={};pdfs={};scans=0;downloads=0
    try:
        with sync_playwright() as p:
            opts={'headless':True}
            if chromium:opts.update(executable_path=chromium,args=['--no-sandbox'])
            browser=p.chromium.launch(**opts)
            for width in WIDTHS:
                for js in (False,True):
                    TRACE.update(case=f'{width}/JS={js}',gate='LOAD')
                    ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                        is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce',accept_downloads=True)
                    if js:
                        ctx.add_init_script('''(() => {window.__metrics={lcp:0,cls:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__metrics.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(_){}try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__metrics.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(_){}})()''')
                    page=ctx.new_page();errors=[]
                    page.on('pageerror',lambda _:errors.append('JS_EXCEPTION'))
                    def route(r):
                        if r.request.url.startswith(base):r.continue_()
                        else:errors.append('OUTBOUND_REQUEST');r.abort()
                    page.route(re.compile('^https?://'),route)
                    resp=page.goto(base+'R93_SOURCE_REGISTER.html',wait_until='load');assert resp.status==200
                    TRACE['gate']='SOURCE_AND_LAYOUT'
                    assert page.locator('article.item').count()==6
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2')
                    assert not page.locator('img,svg,video,iframe,canvas,[data-lat],[data-lon],[data-geo-edge]').count()
                    assert page.locator('#r93-filter').is_visible()==js
                    for n in range(1,7):
                        rid=f'{n:02}';card=page.locator('#r93-source-'+rid)
                        assert card.count()==1 and card.locator('.view-links a').count()==4
                        assert card.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==1
                        for link in card.locator('.view-links a').all():
                            assert link.evaluate('(e)=>e.getBoundingClientRect().height')>=42
                    TRACE['gate']='CSV_DOWNLOAD'
                    with page.expect_download() as event:
                        page.locator('a.download').click()
                    download=event.value
                    assert download.suggested_filename=='apollo-1-source-register-STAGING-HOLD.csv'
                    lines=list(csv.DictReader(io.StringIO(Path(download.path()).read_text('utf8'))))
                    assert len(lines)==6 and lines[0]['catalog_id']=='S67-19766'
                    assert all(x['image_rights_status']=='INDIVIDUAL REVIEW REQUIRED' for x in lines)
                    downloads+=1
                    TRACE['gate']='FILTER_AND_KEYBOARD'
                    if js:
                        for group,count in [('contemporary',3),('retrospective',2),('uncertain',1),('all',6)]:
                            radio=page.locator(f'input[name="r93-period"][value="{group}"]')
                            radio.focus();page.keyboard.press('Space')
                            assert radio.is_checked(),('RADIO_CHANGE',group)
                            assert page.locator('article.item:visible').count()==count,('FILTER_COUNT',group)
                            assert f'{count} of 6' in page.locator('#r93-count').inner_text()
                    else:
                        assert page.locator('article.item:visible').count()==6
                    TRACE['gate']='PERFORMANCE_AXE_PRINT'
                    result={'width':width,'javascript':js,'source_records':6,'csv_download':True,'lcp_ms':None,'cls':None,'axe_violations':None}
                    if js:
                        page.wait_for_timeout(350)
                        metrics=page.evaluate('window.__metrics')
                        assert 0<metrics['lcp']<=2500,('LCP_LAB',metrics)
                        assert 0<=metrics['cls']==.1,('CLS_LAB',metrics)
                        result.update(lcp_ms=round(metrics['lcp'],1),cls=metrics['cls'])
                        if width in (390,1440):
                            page.add_script_tag(path=str(axe))
                            a=page.evaluate('''async()=>{const x=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return{x:x.violations.map(y=>y.id),passes:x.passes.length}}''')
                            assert not a['x'],('AXE',a['x']);result['axe_violations']=0;result['axe_passes']=a['passes'];scans+=1
                            shot=out/f'R93_SOURCE_REGISTER_{width}.png'
                            page.screenshot(path=str(shot),full_page=True,animations='disabled');images[shot.name]=sha(shot)
                            if width==1440:
                                pdf=out/'R93_SOURCE_REGISTER.pdf';page.pdf(path=str(pdf),format='A4',print_background=True)
                                import fitz
                                with fitz.open(pdf) as doc:
                                    txt=''.join(p.get_text() for p in doc)
                                    compact=re.sub(r'\s+','',txt)
                                    assert all(re.sub(r'\s+','',v['nasa_source_url']) in compact for v in lines), 'PRINT_COMPLETE_URLS'
                                    assert txt.count('INDIVIDUAL REVIEW REQUIRED')>=6,'PRINT_RIGHTS_HOLD'
                                    pdfs[pdf.name]={'pages':len(doc),'sha256':sha(pdf)}
                    assert not errors,errors
                    reports.append(result);ctx.close()
            TRACE.update(case='forced-colors',gate='FORCED_CONTRAST')
            ctx=browser.new_context(viewport={'width':390,'height':844},forced_colors='active',reduced_motion='reduce')
            page=ctx.new_page();page.goto(base+'R93_SOURCE_REGISTER.html')
            target=page.locator('.view-links a').first;target.focus()
            assert target.evaluate('(e)=>document.activeElement===e')
            path=out/'R93_SOURCE_REGISTER_FORCED_390.png';page.screenshot(path=str(path),full_page=True)
            images[path.name]=sha(path);ctx.close();browser.close()
    finally:http.shutdown();http.server_close()
    assert len(reports)==10 and scans==2 and downloads==10 and len(images)==3 and len(pdfs)==1
    receipt={'schema':'fv.apollo.r93.chromium.v1','release':'STAGING_HOLD','local_cases':len(reports),
        'csv_downloads':downloads,'axe_scans':scans,'screenshots':images,'pdfs':pdfs,
        'observations':reports,'hosted_wordpress_verified':False,'manual_screen_reader_verified':False}
    (out/'R93_BROWSER_RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--src',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    a.add_argument('--axe',type=Path,required=True);a.add_argument('--chromium');args=a.parse_args()
    try:print('R93 browser:',run(args.src,args.out,args.axe,args.chromium)['local_cases'])
    except Exception:
        import traceback
        print('R93_BROWSER_HOLD:'+':'.join(TRACE.values()),file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise SystemExit(1)
