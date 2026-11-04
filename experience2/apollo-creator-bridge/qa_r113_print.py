#!/usr/bin/env python3
"""Apollo actual-source offline Chromium regression. Full PASS requires axe, touch, performance and print."""
import argparse, hashlib, json, math
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
WIDTHS=(320,360,390,768,1024,1440,1920)
PERF_INIT="""() => {
window.__fv_perf={lcp:null,cls:0};
new PerformanceObserver(l=>{for(const e of l.getEntries())
 if(e.startTime>0)window.__fv_perf.lcp=e.startTime;})
.observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries())
 if(!e.hadRecentInput)window.__fv_perf.cls+=e.value;})
.observe({type:'layout-shift',buffered:true});
}"""
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def require(ok,message):
    if not ok:raise AssertionError(message)
def run(html,out,exe,axe=None):
    body=html.read_text(encoding='utf-8');out.mkdir(parents=True,exist_ok=True)
    record=dict(source_sha256=sha(html),source=str(html),classification='actual-source' if html.name=='landing-preview.html' else 'fixture',
                browser=None,modes=[],screenshots={},pdf=None,performance=[],axe_scans=[],axe_bundle_status='NOT_SUPPLIED',
                complete=False,failure_code=None)
    journal=out/'R113_BROWSER_RECEIPT.json'
    def checkpoint():journal.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    checkpoint()
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=exe,headless=True,args=['--no-sandbox'])
        record['browser']=browser.version
        try:
            for w in WIDTHS:
                for js in (False,True):
                    label=f'{w}px-js-{int(js)}'
                    ctx=browser.new_context(viewport={'width':w,'height':850},java_script_enabled=js,reduced_motion='reduce',has_touch=True)
                    page=ctx.new_page();page.set_content(body,wait_until='load')
                    require(page.locator('[data-fv-claim]').count()==4,label+': four claims')
                    require(not page.locator('.print-custody').is_visible(),label+': print-only rights notice leaked onto screen')
                    require(page.locator('[data-fv-photo-record]').count()==6,label+': six source rail links')
                    require(page.locator("[id^='photo-source-']").count()==6,label+': six photo rows')
                    # Verify exact NASA source identities and visible credit/producer custody on actual HTML.
                    for rid, credit in (('01','Image Credit: NASA'),('02','Producer: JSC'),
                                        ('03','Producer: JSC'),('04','NASA/Kim Shiflett'),
                                        ('05','Producer: JSC'),('06','NASA/Kim Shiflett')):
                        row=page.locator('#photo-source-'+rid)
                        require(row.count()==1 and credit in row.inner_text(),
                                label+': NASA custody credit missing '+rid)
                        require(row.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==1,
                                label+': NASA photograph source link mismatch '+rid)
                    require(page.locator('[data-fv-primary-cta]').count()==1,label+': one classroom CTA')
                    require(page.locator("a[href^='https://www.nasa.gov/']").count()>=6,label+': NASA source links')
                    require(page.locator('form').count()==0 and page.locator("a[href*='payhip']").count()==0,
                            label+': unapproved form or commerce')
                    page.locator('[data-fv-primary-cta]').focus();page.keyboard.press('Enter')
                    require(page.evaluate('location.hash')=='#classroom-preview',label+': classroom CTA keyboard navigation')
                    require(page.locator('#classroom-preview').evaluate('(e)=>document.activeElement===e'),
                            label+': classroom destination did not receive focus')
                    require(page.locator('#classroom-preview').is_visible(),label+': classroom exercise not visible')
                    require(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),
                            label+': document horizontally overflows; table must scroll independently')
                    require(page.evaluate("getComputedStyle(document.documentElement).scrollBehavior")=='auto',
                            label+': reduced-motion scroll override missing')
                    page.locator('[data-fv-photo-record="05"]').focus();page.keyboard.press('Enter')
                    require(page.evaluate('location.hash')=='#photo-source-05',label+': photo source keyboard navigation')
                    page.locator('[data-fv-primary-cta]').tap()
                    require(page.evaluate('location.hash')=='#classroom-preview',
                            label+': real touch activation did not reach classroom')
                    if js:
                        require(page.locator('[data-fv-lens]').is_visible(),label+': lens missing')
                        page.locator('[data-fv-mode="limit"]').click()
                        require(page.locator('[data-fv-claim]:visible').count()==2,label+': screen filter incorrect')
                    else:
                        require(page.locator('[data-fv-claim]:visible').count()==4,label+': no-JS content missing')
                    if js and w in (390,1440):
                        img=out/f'R113_WEB_{w}.png';page.screenshot(path=str(img),full_page=True)
                        record['screenshots'][img.name]=sha(img)
                    page.emulate_media(media='print')
                    require(page.locator('.print-custody').count()==1 and page.locator('.print-custody').is_visible(),label+': PRINT RIGHTS NOTICE MISSING')
                    rights=page.locator('.print-custody').inner_text()
                    require('0/6' in rights and 'S67-19766' in rights and 'not NASA-endorsed' in rights,label+': PRINT RIGHTS NOTICE INCOMPLETE')
                    require(page.locator('[data-fv-claim]:visible').count()==4,label+': PRINT EVIDENCE LOSS')
                    require('NASA/Kim Shiflett' in page.locator('#photo-source-04').inner_text() and
                            'NASA/Kim Shiflett' in page.locator('#photo-source-06').inner_text(),
                            label+': PRINT PHOTO CREDIT LOSS')
                    require(page.locator('table').evaluate('(t)=>getComputedStyle(t).minWidth')=='0px',
                            label+': printed source register too wide')
                    require(page.locator('.table-scroll').evaluate('(t)=>getComputedStyle(t).overflowX')=='visible',
                            label+': printed source register clipped')
                    if js and w==390:
                        pdf=out/'R113_CLASSROOM_PRINT_390.pdf'
                        page.pdf(path=str(pdf),format='Letter',print_background=False,
                                 margin={'top':'10mm','bottom':'10mm','left':'10mm','right':'10mm'})
                        require(pdf.read_bytes().startswith(b'%PDF-'),'invalid PDF')
                        record['pdf']={'name':pdf.name,'sha256':sha(pdf)}
                    record['modes'].append(label);checkpoint();ctx.close()
            for w in (390,1440):
                for trial in (1,2,3):
                    ctx=browser.new_context(viewport={'width':w,'height':850},reduced_motion='reduce')
                    page=ctx.new_page();page.evaluate(PERF_INIT)
                    page.set_content(body,wait_until='load');page.wait_for_timeout(500)
                    m=page.evaluate('window.__fv_perf');lcp,cls=m['lcp'],m['cls']
                    require(isinstance(lcp,(int,float)) and math.isfinite(lcp) and lcp>=0,
                            f'unobserved LCP {w}/{trial}')
                    require(isinstance(cls,(int,float)) and math.isfinite(cls) and cls>=0,
                            f'invalid CLS {w}/{trial}')
                    record['performance'].append({'width':w,'trial':trial,'lcp_ms':round(lcp,1),
                                                  'cls':round(cls,5),'lab_only':True})
                    checkpoint();require(lcp<=2500 and cls<=0.1,f'lab budget failed {w}/{trial}')
                    ctx.close()
            # An incomplete accessibility scan must never produce a green acceptance receipt.
            if not axe or not axe.is_file():
                record['failure_code']='AXE_BUNDLE_REQUIRED'
                checkpoint()
                raise AssertionError('approved local axe bundle required for full acceptance')
            record['axe_bundle_status']='LOCAL_APPROVED_BUNDLE_PROVIDED'
            for width in (390,1440):
                ctx=browser.new_context(viewport={'width':width,'height':850})
                page=ctx.new_page()
                page.set_content(body,wait_until='load')
                page.add_script_tag(content=axe.read_text(encoding='utf-8'))
                for state in ('all','limit'):
                    if state=='limit':
                        require(page.locator('[data-fv-lens]').is_visible(),
                                f'axe {width}: enhancement missing')
                        page.locator('[data-fv-mode="limit"]').click()
                    result=page.evaluate('async()=>await axe.run(document)')
                    violations=[str(x['id']) for x in result['violations']]
                    record['axe_scans'].append({'width':width,'state':state,
                                                'violations':len(violations),'ids':violations})
                    checkpoint()
                    require(not violations,f'axe violations {width}/{state}')
                ctx.close()
            require(len(record['modes'])==14 and len(record['performance'])==6 and
                    len(record['axe_scans'])==4,'incomplete matrix')
            require(len(record['screenshots'])==2 and record['pdf'] is not None,
                    'missing reproducible screenshots or printable PDF')
            record['complete']=True
        except Exception:
            record['failure_code']=record['failure_code'] or 'ACCEPTANCE_FAILED';checkpoint();raise
        finally:
            checkpoint();browser.close()
    return record
if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--html',type=Path,default=ROOT/'landing-preview.html')
    a.add_argument('--out',type=Path,default=ROOT/'qa-r113-evidence')
    a.add_argument('--chromium',default='/usr/bin/chromium')
    a.add_argument('--axe',type=Path,default=None)
    opts=a.parse_args()
    print(json.dumps(run(opts.html,opts.out,opts.chromium,opts.axe),indent=2))
