#!/usr/bin/env python3
"""Real HTTP Chromium on PHP WordPress-hook CONTRACT SHIM, not actual WordPress or hosted Assembler."""
import argparse, hashlib, json, os, subprocess, time
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import quote
from playwright.sync_api import sync_playwright

BASE='http://127.0.0.1:8941/'
VIEWS=('R85_NASA_SOURCE_REVIEW.html','R87_PHOTOGRAPH_DATE_RAIL.html',
       'R88_READING_ROOM.html','R89_REVIEW_HUB.html','R93_SOURCE_PASSPORTS.html',
       'R94_CURATED_ATLAS.html','R97_SOURCE_GALLERY.html')
WIDTHS=(320,390,768,1440,1920)
def url(name):return BASE+'?fv_apollo_r99='+quote(name)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(stage,fixture,axe,out):
    out.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,APOLLO_R99_STAGE=str(stage),APOLLO_R99_AXE=str(axe) if axe else '')
    php=subprocess.Popen(['php','-S','127.0.0.1:8941',str(fixture)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(80):
            if php.poll() is not None:raise RuntimeError('R99_PHP_STARTUP_FAILED')
            try:
                urlopen(BASE,timeout=1).read(64);break
            except HTTPError:break
            except Exception:time.sleep(.1)
        else:raise RuntimeError('R99_PHP_STARTUP_TIMEOUT')
        for name in (VIEWS[-1],'../../wp-config.php'):
            try:
                urlopen(url(name),timeout=3)
                raise AssertionError('R99_UNAUTHENTICATED_ROUTE_OPEN:'+name)
            except HTTPError as exc:assert exc.code==404,exc.code
        receipt={'schema':'fv.apollo.r99.browser.contract.v1','environment':'PHP contract shim; NOT WordPress or hosted WordPress.com',
                 'release':'STAGING_HOLD','authenticated_preview':True,'configurations':[],
                 'axe':[],'screenshots':{},'no_external_requests':True}
        with sync_playwright() as play:
            browser=play.chromium.launch(headless=True)
            try:
                for view in VIEWS:
                    for width in WIDTHS:
                        for js in (False,True):
                            context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js)
                            context.add_cookies([{'name':'apollo_r99_fixture_auth','value':'contract-only','url':BASE}])
                            page=context.new_page()
                            external=[]
                            page.on('request',lambda r:external.append(r.url) if not r.url.startswith(BASE) else None)
                            if js:
                                page.add_init_script("""window.__r99_lcp=null;window.__r99_cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries())window.__r99_lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__r99_cls+=e.value}).observe({type:'layout-shift',buffered:true});""")
                            response=page.goto(url(view),wait_until='load',timeout=20000)
                            assert response.status==200,(view,width,js,response.status)
                            assert page.locator('nav.r98-route').count()==6,(view,width,js)
                            assert 'NASA' in page.locator('body').inner_text()
                            assert page.locator('img').count()==0
                            overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')
                            assert not overflow,(view,width,js)
                            if external:raise AssertionError('R99_UNEXPECTED_EXTERNAL_REQUESTS:'+str(external))
                            if view in (VIEWS[-1],'R94_CURATED_ATLAS.html') and width in (390,1440) and js:
                                filename=f'R99_{view.removesuffix(".html")}_{width}.png'
                                page.screenshot(path=str(out/filename),full_page=True)
                                receipt['screenshots'][filename]=sha(out/filename)
                            metrics=page.evaluate('({lcp:window.__r99_lcp ?? null,cls:window.__r99_cls ?? null})') if js else None
                            receipt['configurations'].append({'view':view,'width':width,'js':js,'overflow':False,'metrics':metrics})
                            if view==VIEWS[-1] and width in (390,1440) and js and axe:
                                page.add_script_tag(url=BASE+'?fv_r99_axe=1')
                                report=page.evaluate("""async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),passes:r.passes.length}}""")
                                receipt['axe'].append({'width':width,**report})
                                assert not report['violations'],report
                            if view==VIEWS[-1] and width==1440 and js:
                                page.pdf(path=str(out/'R99_GALLERY_CONTRACT.pdf'),print_background=True)
                            context.close()
                context=browser.new_context(viewport={'width':390,'height':844})
                context.add_cookies([{'name':'apollo_r99_fixture_auth','value':'contract-only','url':BASE}])
                page=context.new_page();page.goto(url('R97_SOURCE_GALLERY.html'))
                link=page.locator('nav.r98-route a').first
                link.focus()
                with page.expect_navigation(url='**fv_apollo_r99=R85_NASA_SOURCE_REVIEW.html#r85-source-01',wait_until='commit'):
                    page.keyboard.press('Enter')
                page.wait_for_load_state('domcontentloaded')
                assert page.locator('#r85-source-01').count()==1
                context.close()
                context=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
                context.add_cookies([{'name':'apollo_r99_fixture_auth','value':'contract-only','url':BASE}])
                page=context.new_page();page.goto(url('R97_SOURCE_GALLERY.html'))
                with page.expect_navigation(url='**fv_apollo_r99=R85_NASA_SOURCE_REVIEW.html#r85-source-01',wait_until='commit'):
                    page.locator('nav.r98-route a').first.tap()
                page.wait_for_load_state('domcontentloaded')
                receipt['keyboard_roundtrip']=True;receipt['touch_roundtrip']=True
                context.close()
            finally:browser.close()
        assert len(receipt['configurations'])==70
        receipt['artifacts']={p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()}
        (out/'R99_BROWSER_CONTRACT_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        return receipt
    finally:
        php.terminate()
        try:php.wait(timeout=4)
        except subprocess.TimeoutExpired:php.kill()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',type=Path,required=True)
    parser.add_argument('--fixture',type=Path,required=True)
    parser.add_argument('--axe',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.stage,args.fixture,args.axe,args.out),sort_keys=True))
