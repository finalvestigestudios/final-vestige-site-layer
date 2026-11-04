#!/usr/bin/env python3
"""Actual Apollo HTML Chromium print regression — offline, no HTTP, no writes to CMS."""
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
                browser=None,modes=[],screenshots={},pdf=None,performance=[],axe='NOT_RUN_NO_APPROVED_BUNDLE',
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
                    ctx=browser.new_context(viewport={'width':w,'height':850},java_script_enabled=js,reduced_motion='reduce')
                    page=ctx.new_page();page.set_content(body,wait_until='load')
                    require(page.locator('[data-fv-claim]').count()==4,label+': four claims')
                    require(not page.locator('.print-custody').is_visible(),label+': print-only rights notice leaked onto screen')
                    require(page.locator('[data-fv-photo-record]').count()==6,label+': six source rail links')
                    require(page.locator("[id^='photo-source-']").count()==6,label+': six photo rows')
                    require(page.locator('[data-fv-primary-cta]').count()==1,label+': one classroom CTA')
                    require(page.locator("a[href^='https://www.nasa.gov/']").count()>=6,label+': NASA source links')
                    require(page.locator('form').count()==0 and page.locator("a[href*='payhip']").count()==0,
                            label+': unapproved form or commerce')
                    page.locator('[data-fv-primary-cta]').focus();page.keyboard.press('Enter')
                    require(page.evaluate('location.hash')=='#classroom-preview',label+': classroom CTA keyboard navigation')
                    page.locator('[data-fv-photo-record="05"]').focus();page.keyboard.press('Enter')
                    require(page.evaluate('location.hash')=='#photo-source-05',label+': photo source keyboard navigation')
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
            if axe and axe.is_file():
                ctx=browser.new_context(viewport={'width':390,'height':850})
                page=ctx.new_page();page.set_content(body);page.add_script_tag(content=axe.read_text())
                result=page.evaluate('async()=>await axe.run(document)')
                record['axe']={'violations':len(result['violations']),
                               'ids':[v['id'] for v in result['violations']]}
                require(not result['violations'],'axe violation');ctx.close()
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
            require(len(record['modes'])==14 and len(record['performance'])==6,'incomplete matrix')
            record['complete']=True
        except Exception:
            record['failure_code']='ACCEPTANCE_FAILED';checkpoint();raise
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
