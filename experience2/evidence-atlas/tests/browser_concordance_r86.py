#!/usr/bin/env python3
"""R86 real Chromium proof: no-JS, keyboard, touch, axe, print, performance."""
import argparse, hashlib, json
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
WIDTHS=(320,390,768,1440,1920)
CATALOG=('S67-19766','S67-15717','S66-58038',
         'KSC-20170124-PH_KLS01_0164','S67-21294','KSC-20170124-PH_KLS01_0090')
LINKS=('https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
       'https://www.nasa.gov/image-detail/amf-s67-15717/',
       'https://www.nasa.gov/image-detail/amf-s66-58038/',
       'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
       'https://www.nasa.gov/image-detail/amf-s67-21294/',
       'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(src,out,axe):
    out.mkdir(parents=True,exist_ok=True)
    assert axe.is_file(),'R86_AXE_NOT_INSTALLED'
    assert (src/'R86_EVIDENCE_CONCORDANCE.html').is_file(),'R86_SOURCE_NOT_BUILT'
    cases,screens,problems=[],{},[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for width in WIDTHS:
            for enabled in (False,True):
                context=browser.new_context(viewport={'width':width,'height':900},
                    java_script_enabled=enabled,reduced_motion='reduce',
                    is_mobile=width<=390,has_touch=width<=390)
                if enabled:
                    context.add_init_script("""(()=>{window.__r86={lcp:null,cls:0};
                        try{new PerformanceObserver(l=>{let a=l.getEntries();
                            if(a.length)window.__r86.lcp=a[a.length-1].startTime})
                            .observe({type:'largest-contentful-paint',buffered:true})}catch(_){}
                        try{new PerformanceObserver(l=>{for(const e of l.getEntries())
                            if(!e.hadRecentInput)window.__r86.cls+=e.value})
                            .observe({type:'layout-shift',buffered:true})}catch(_){}
                    })();""")
                page=context.new_page()
                outbound,errors=[],[]
                page.on('pageerror',lambda _:errors.append('JS_ERROR'))
                def restrict(route):
                    if route.request.url.startswith(('http:','https:')):
                        outbound.append('OUTSIDE_REQUEST')
                        route.abort()
                    else: route.continue_()
                page.route('**/*',restrict)
                page.goto((src/'R86_EVIDENCE_CONCORDANCE.html').resolve().as_uri(),wait_until='load')
                page.wait_for_timeout(150)
                assert not outbound and not errors,'R86_NETWORK_OR_SCRIPT'
                assert page.locator('article.evidence').count()==6,'R86_MISSING_PLATES'
                assert page.locator('summary').count()==6,'R86_NO_JS_DISCLOSURES'
                assert page.locator('table tbody tr').count()==6,'R86_MATRIX_LOST'
                assert page.locator('img,iframe,picture,video,[data-lat],[data-lon],[data-geo-edge]').count()==0,'R86_MEDIA_OR_GEO'
                links=page.locator('a.primary').evaluate_all('(a)=>a.map(n=>n.getAttribute("href"))')
                assert tuple(links)==LINKS,'R86_NASA_LINK_IDENTITY'
                text=page.locator('body').inner_text()
                assert all(x in text for x in CATALOG),'R86_CATALOG'
                assert '0 of 6 photographs cleared' in text and 'provisional' in text.lower(),'R86_HOLD_REMOVED'
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),'R86_OVERFLOW'
                page.locator('summary').first.focus()
                page.keyboard.press('Enter')
                assert page.locator('details').first.evaluate('(n)=>n.open'),'R86_KEY_OPEN'
                page.keyboard.press('Enter')
                assert not page.locator('details').first.evaluate('(n)=>n.open'),'R86_KEY_CLOSE'
                page.locator('tbody a').nth(2).click()
                assert page.evaluate('location.hash')=='#r86-03','R86_MATRIX_NAV'
                bounds=page.locator('a.primary').evaluate_all(
                    '(nodes)=>nodes.map(n=>({h:n.getBoundingClientRect().height,w:n.getBoundingClientRect().width}))')
                assert all(b['h']>=43.5 and b['w']>=43.5 for b in bounds),'R86_TOUCH_TARGET'
                assert page.locator('.evidence').first.evaluate(
                    '(n)=>getComputedStyle(n).backgroundColor')!='rgba(0, 0, 0, 0)','R86_CSS_MISSING'
                c={'width':width,'js':enabled,'off_origin_requests':0,'no_overflow':True,
                   'native_keyboard':True,'touch_44px':True,'axe_violations':None,
                   'lab_lcp_ms':None,'lab_cls':None}
                if enabled:
                    page.add_script_tag(path=str(axe))
                    audit=page.evaluate("""async()=>{const r=await axe.run(document,{
                        runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                        return {violations:r.violations.map(v=>({id:v.id,count:v.nodes.length,impact:v.impact})),
                                passed:r.passes.length}}""")
                    c['axe_violations']=audit['violations']
                    c['axe_rules_passed']=audit['passed']
                    problems.extend(audit['violations'])
                    perf=page.evaluate('window.__r86||null')
                    if perf:
                        c['lab_lcp_ms']=perf['lcp']
                        c['lab_cls']=perf['cls']
                        assert perf['cls']<=0.1,'R86_LAB_CLS'
                if enabled and width in (390,1440):
                    snap=out/f'R86_CONCORDANCE_{width}.png'
                    page.screenshot(path=str(snap),full_page=True,animations='disabled')
                    screens[str(width)]=sha(snap)
                    if width==1440:
                        pdf=out/'R86_CONCORDANCE_PRINT.pdf'
                        page.pdf(path=str(pdf),format='A4',print_background=True)
                        assert pdf.stat().st_size>5000,'R86_PDF_MISSING'
                        with fitz.open(pdf) as doc:
                            text=''.join(pg.get_text() for pg in doc)
                            compact=''.join(text.split())
                            assert all(x in compact for x in CATALOG),'R86_PDF_CATALOGS'
                            assert all(''.join(x.split()) in compact for x in LINKS),'R86_PDF_SOURCE_URLS'
                            assert '0of6photographs' in compact,'R86_PDF_RIGHTS_HOLD'
                            c['pdf_pages']=len(doc)
                cases.append(c)
                context.close()
        forced=browser.new_context(viewport={'width':390,'height':850},
            forced_colors='active',reduced_motion='reduce')
        f=forced.new_page()
        f.goto((src/'R86_EVIDENCE_CONCORDANCE.html').resolve().as_uri())
        f.locator('summary').first.focus();f.keyboard.press('Enter')
        assert f.locator('details').first.evaluate('(e)=>e.open'),'R86_FORCED_KEYBOARD'
        f.screenshot(path=str(out/'R86_FORCED_390.png'),full_page=True)
        screens['forced_390']=sha(out/'R86_FORCED_390.png')
        forced.close();browser.close()
    assert not problems,'R86_AXE_FAILURES'
    receipt={'schema':'fv.apollo.r86.real-chromium.v1','release':'STAGING_HOLD',
        'cases':cases,'axe_gate':'PASS','screenshots_sha256':screens,
        'media_reuse_cleared':0,'hosted_wordpress_tested':False,
        'production_cwv':False,'site_writes':False}
    (out/'R86_BROWSER_RECEIPT.json').write_text(
        json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return receipt
if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--src',type=Path,required=True)
    a.add_argument('--out',type=Path,required=True)
    a.add_argument('--axe',type=Path,required=True)
    z=a.parse_args()
    result=run(z.src,z.out,z.axe)
    print('R86 Chromium:',len(result['cases']),'cases, staging HOLD, axe PASS')
