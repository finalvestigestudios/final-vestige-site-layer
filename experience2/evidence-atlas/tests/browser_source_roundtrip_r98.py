#!/usr/bin/env python3
"""Real-HTTP Chromium verification of seven R98 source views and 54 native routes."""
import argparse
import hashlib
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

VIEWS={
 'R85_NASA_SOURCE_REVIEW.html':'r85-source-',
 'R87_PHOTOGRAPH_DATE_RAIL.html':'r87-record-',
 'R88_READING_ROOM.html':'r88-',
 'R89_REVIEW_HUB.html':'r89-source-',
 'R93_SOURCE_PASSPORTS.html':'passport-',
 'R94_CURATED_ATLAS.html':'atlas-',
 'R97_SOURCE_GALLERY.html':'gallery-',
}

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run(src,out,axe=None,chromium=None):
    src=src.resolve();out.mkdir(parents=True,exist_ok=True)
    receipt=json.loads((src/'R98_ROUNDTRIP_RECEIPT.json').read_text())
    assert receipt['schema']=='fv.apollo.r98.roundtrip.v1'
    assert receipt['release']=='STAGING_HOLD' and receipt['publication_approved'] is False
    assert receipt['reciprocal_gallery_links']==54
    for f,h in receipt['files'].items():assert digest(src/f)==h,f
    book=json.loads((src/'R93_SOURCE_PASSPORTS.json').read_text())
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(src)))
    Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}'
    data={'release':'STAGING_HOLD','transport':'REAL_HTTP_CHROMIUM','cases':[],
          'cross_document_navigations':0,'touch_navigations':0,'axe':[],'screenshots':{},'pdf':None,
          'external_requests':[],'errors':[]}
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,executable_path=chromium if chromium else None,args=['--no-sandbox'])
            try:
                for filename,prefix in VIEWS.items():
                    for width in (320,390,768,1440,1920):
                        for js in (False,True):
                            context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                                has_touch=width==390,is_mobile=width==390,
                                reduced_motion='reduce' if width==768 else 'no-preference')
                            try:
                                page=context.new_page()
                                page.set_default_timeout(15000)
                                errors=[]
                                page.on('pageerror',lambda e:errors.append(str(e)))
                                page.on('request',lambda r:data['external_requests'].append(r.url)
                                    if urlparse(r.url).netloc!=urlparse(origin).netloc else None)
                                if js:
                                    page.add_init_script('''window.__cwv={lcp:0,cls:0};try{
                                      new PerformanceObserver(l=>{for(const e of l.getEntries())window.__cwv.lcp=Math.max(window.__cwv.lcp,e.startTime)}).observe({type:'largest-contentful-paint',buffered:true});
                                      new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cwv.cls+=e.value}).observe({type:'layout-shift',buffered:true})
                                      }catch(e){window.__cwv.error=String(e)}''')
                                response=page.goto(origin+'/'+filename,wait_until='load')
                                assert response and response.status==200,(filename,width,js)
                                page.wait_for_timeout(90)
                                assert page.locator('.r98-route').count()==6,(filename,'route count')
                                assert page.locator('a[href="r98_crosslinks.css"]').count()==0
                                assert page.locator('link[href="r98_crosslinks.css"]').count()==1
                                assert page.locator('img,iframe,video,canvas').count()==0
                                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),(filename,width,js,'overflow')
                                for record in book['records']:
                                    n=record['id']
                                    card=page.locator('[id="'+prefix+n+'"]')
                                    assert card.count()==1,(filename,n,'card missing')
                                    nav=card.locator('.r98-route')
                                    assert nav.count()==1 and nav.locator('a').count()==(3 if filename=='R97_SOURCE_GALLERY.html' else 1)
                                    assert nav.get_attribute('aria-label')=='Alternate views of NASA source '+n
                                    if filename!='R97_SOURCE_GALLERY.html':
                                        assert nav.locator('a').first.get_attribute('href')=='R97_SOURCE_GALLERY.html#gallery-'+n
                                metrics=page.evaluate('window.__cwv||null') if js else None
                                data['cases'].append({'page':filename,'width':width,'javascript':js,
                                    'lcp_lab_ms':metrics['lcp'] if metrics else None,
                                    'cls_lab':metrics['cls'] if metrics else None})
                                if js and axe and ((filename=='R97_SOURCE_GALLERY.html' and width in (390,1440))
                                        or (filename=='R94_CURATED_ATLAS.html' and width==390)):
                                    page.add_script_tag(path=str(axe))
                                    audit=page.evaluate('''async()=>{let a=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                                      return {violations:a.violations.map(v=>({id:v.id,count:v.nodes.length})),passing:a.passes.length}}''')
                                    assert not audit['violations'],(filename,audit)
                                    data['axe'].append({'page':filename,'width':width,**audit})
                                if js and (filename=='R97_SOURCE_GALLERY.html' and width in (390,1440) or filename=='R94_CURATED_ATLAS.html' and width==390):
                                    f=out/f'R98_{filename.split(".")[0]}_{width}.png'
                                    page.screenshot(path=str(f),full_page=True)
                                    data['screenshots'][f.name]=digest(f)
                                if js and filename=='R97_SOURCE_GALLERY.html' and width==390:
                                    page.emulate_media(forced_colors='active')
                                    f=out/'R98_GALLERY_FORCED_390.png'
                                    page.screenshot(path=str(f),full_page=True)
                                    data['screenshots'][f.name]=digest(f)
                                if js and filename=='R97_SOURCE_GALLERY.html' and width==1440:
                                    page.emulate_media(media='print')
                                    f=out/'R98_GALLERY_PRINT.pdf'
                                    f.write_bytes(page.pdf(format='A4',print_background=True))
                                    import fitz
                                    doc=fitz.open(f)
                                    printed=''.join(''.join(pg.get_text().split()) for pg in doc)
                                    for record in book['records']:
                                        assert record['url'] in printed,record['id']
                                    assert printed.count('INDIVIDUALREVIEWREQUIRED')>=6
                                    data['pdf']={'pages':len(doc),'sha256':digest(f)}
                                    doc.close()
                                if width==390:
                                    for record in book['records']:
                                        n=record['id']
                                        page.goto(origin+'/'+filename,wait_until='load')
                                        locator=page.locator('[id="'+prefix+n+'"] .r98-route a').first
                                        locator.focus()
                                        page.keyboard.press('Enter')
                                        dest=('R85_NASA_SOURCE_REVIEW.html#r85-source-'+n if filename=='R97_SOURCE_GALLERY.html'
                                              else 'R97_SOURCE_GALLERY.html#gallery-'+n)
                                        page.wait_for_url(origin+'/'+dest)
                                        assert page.locator('[id="'+dest.split('#')[1]+'"]').count()==1
                                        assert page.evaluate('location.hash')=='#'+dest.split('#')[1]
                                        data['cross_document_navigations']+=1
                                    page.goto(origin+'/'+filename,wait_until='load')
                                    page.locator('[id="'+prefix+'02"] .r98-route a').first.tap()
                                    touch_dest=('R85_NASA_SOURCE_REVIEW.html#r85-source-02' if filename=='R97_SOURCE_GALLERY.html'
                                                else 'R97_SOURCE_GALLERY.html#gallery-02')
                                    page.wait_for_url(origin+'/'+touch_dest)
                                    assert page.locator('[id="'+touch_dest.split('#')[1]+'"]').count()==1
                                    data['touch_navigations']+=1
                                    if filename=='R97_SOURCE_GALLERY.html' and js:
                                        page.goto(origin+'/R94_CURATED_ATLAS.html',wait_until='load')
                                        query=page.locator('#query')
                                        query.fill('S67-19766')
                                        assert page.locator('#atlas-06').is_hidden()
                                        page.goto(origin+'/R97_SOURCE_GALLERY.html',wait_until='load')
                                        page.locator('a[href="R94_CURATED_ATLAS.html#atlas-06"]').click()
                                        page.wait_for_url(origin+'/R94_CURATED_ATLAS.html#atlas-06')
                                        assert page.locator('#atlas-06').is_visible()
                                assert not errors,(filename,width,js,errors)
                            finally:
                                context.close()
            finally:
                browser.close()
        assert len(data['cases'])==70,len(data['cases'])
        assert data['cross_document_navigations']==84,data['cross_document_navigations']
        assert data['touch_navigations']==14,data['touch_navigations']
        assert len(data['screenshots'])==4
        assert data['pdf'] and not data['external_requests']
        if axe:assert len(data['axe'])==3
        (out/'R98_BROWSER_RECEIPT.json').write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
        return data
    finally:
        server.shutdown()
        server.server_close()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--src',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--axe',type=Path)
    parser.add_argument('--chromium',type=str)
    x=parser.parse_args()
    print(json.dumps(run(x.src,x.out,x.axe,x.chromium),sort_keys=True))
