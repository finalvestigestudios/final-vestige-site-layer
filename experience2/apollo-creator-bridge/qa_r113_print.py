#!/usr/bin/env python3
"""Apollo actual-source offline Chromium regression. Full PASS requires axe, touch, performance and print."""
import argparse, hashlib, json, math, subprocess
from datetime import datetime, timezone
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
def source_identity(html):
    """Release-acceptance evidence must correspond to the tracked HEAD bytes, not a renamed fixture."""
    if html.resolve() != (ROOT/'landing-preview.html').resolve():
        return 'NOT_CANONICAL_LANDING'
    try:
        result=subprocess.run(['git','show','HEAD:experience2/apollo-creator-bridge/landing-preview.html'],
                              cwd=ROOT,capture_output=True,check=False,timeout=10)
    except (OSError,subprocess.TimeoutExpired):
        return 'GIT_HEAD_UNAVAILABLE'
    if result.returncode:
        return 'GIT_HEAD_UNAVAILABLE'
    return ('EXACT_GIT_HEAD' if hashlib.sha256(result.stdout).hexdigest()==sha(html)
            else 'HEAD_SOURCE_MISMATCH')
def require(ok,message):
    if not ok:raise AssertionError(message)
def run(html,out,exe,axe=None):
    body=html.read_text(encoding='utf-8');out.mkdir(parents=True,exist_ok=True)
    record=dict(source_sha256=sha(html),source=str(html),classification='actual-source' if html.name=='landing-preview.html' else 'fixture',
                browser=None,modes=[],screenshots={},pdf=None,performance=[],axe_scans=[],axe_bundle_status='NOT_SUPPLIED',
                source_identity='UNCHECKED',
                complete=False,failure_code=None,worksheet_pdf=None)
    journal=out/'R113_BROWSER_RECEIPT.json'
    def checkpoint():journal.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    record['source_identity']=source_identity(html)
    if record['source_identity']!='EXACT_GIT_HEAD':
        record['failure_code']='UNVERIFIED_SOURCE_IDENTITY'
        checkpoint()
        raise AssertionError('actual-source release QA requires canonical file identical to git HEAD; '+record['source_identity'])
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
                    # R123: validate the ACTUAL NASA Board timeline, precision and epistemic boundaries.
                    rail=page.locator('[data-fv-board-clock-rail]')
                    points=rail.locator('li[data-fv-board-time]')
                    require(points.count()==5,label+': five Board clock points required')
                    expected=('power-interruption','fire-report','intense-fire','rupture','telemetry-loss')
                    names=points.evaluate_all('(a)=>a.map(n=>n.dataset.fvBoardTime)')
                    require(tuple(names)==expected,label+': historical clock order/IDs changed')
                    times=points.locator('time').evaluate_all('(a)=>a.map(n=>n.dateTime)')
                    require(len(times)==5,label+': missing machine-readable times')
                    moments=[datetime.fromisoformat(x.replace('Z','+00:00')) for x in times]
                    require(all(t.tzinfo is not None and t.utcoffset().total_seconds()==0 for t in moments)
                            and moments==sorted(moments),label+': not monotonically increasing UTC')
                    seconds=(moments[3]-moments[1]).total_seconds()
                    require(13.5<=seconds<=15.0,label+': fire-report-to-rupture interval contradicts source')
                    require(points.nth(1).get_attribute('data-fv-event-status')=='observed'
                            and points.nth(3).get_attribute('data-fv-event-status')=='approximate'
                            and points.nth(4).get_attribute('data-fv-event-status')=='bounded',
                            label+': timeline certainty labels inaccurate')
                    clock_custody=page.locator('[data-fv-clock-custody]')
                    require(clock_custody.is_visible()
                            and 'approximately 15 seconds' in clock_custody.inner_text()
                            and 'ignition' in clock_custody.inner_text().lower(),
                            label+': clock-precision caveat absent')
                    require(page.locator('#event-sequence a[href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/"]').count()==1,
                            label+': technical chronology missing its NASA primary source link')
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
                    require(page.locator('[data-fv-print-student]').count()==1,label+': one opt-in print utility')
                    photo_index=page.locator('[data-fv-student-photo-index]')
                    require(photo_index.count()==1 and
                            photo_index.locator('[data-fv-student-photo]').count()==6,
                            label+': standalone worksheet needs six photograph records')
                    require(not photo_index.is_visible(),
                            label+': print-only photographic index leaked onto screen')
                    require(photo_index.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==6,
                            label+': standalone photo index must carry six NASA links')
                    require(page.locator('[data-fv-print-student]').is_visible()==js,
                            label+': print utility must fail open with no JavaScript')
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
                    require(page.locator('[data-fv-student-print]').count()==1 and
                            not page.locator('[data-fv-student-print]').is_visible(),
                            label+': student handout leaked into screen rendering')
                    # Simulate a teacher opening the answer before printing; it must not leak.
                    page.locator('#classroom-preview .callout details').first.evaluate('(e)=>e.open=true')
                    page.emulate_media(media='print')
                    require(page.locator('[data-fv-student-print]').is_visible(),
                            label+': printable student worksheet missing')
                    require(not page.locator('#classroom-preview .callout').is_visible(),
                            label+': teacher answer/notes leaked into student handout')
                    require(page.locator('[data-fv-student-prompts] > li').count()==3,
                            label+': student prompts incomplete')
                    require(photo_index.is_visible() and
                            photo_index.locator('[data-fv-student-photo]').count()==6,
                            label+': printed handout lost photographic source index')
                    require('not a fire-event timeline' in photo_index.inner_text() and
                            'unconfirmed' in photo_index.inner_text() and
                            'NASA/Kim Shiflett' in photo_index.inner_text(),
                            label+': printed photo-index chronology or provenance missing')
                    require(page.locator('[data-fv-student-print] .response-lines span').count()==9,
                            label+': written response space missing')
                    worksheet=page.locator('[data-fv-student-print]').inner_text()
                    require('Apollo 204 Review Board' in worksheet and
                            'January 27' in worksheet and 'Two independently identified sources' in worksheet,
                            label+': worksheet source or uncertainty prompt missing')
                    require(page.locator('.print-custody').count()==1 and page.locator('.print-custody').is_visible(),label+': PRINT RIGHTS NOTICE MISSING')
                    rights=page.locator('.print-custody').inner_text()
                    require('0/6' in rights and 'S67-19766' in rights and 'not NASA-endorsed' in rights,label+': PRINT RIGHTS NOTICE INCOMPLETE')
                    require(page.locator('[data-fv-claim]:visible').count()==4,label+': PRINT EVIDENCE LOSS')
                    require('NASA/Kim Shiflett' in page.locator('#photo-source-04').inner_text() and
                            'NASA/Kim Shiflett' in page.locator('#photo-source-06').inner_text(),
                            label+': PRINT PHOTO CREDIT LOSS')
                    require(page.locator('#photo-source-04 small').evaluate(
                            '(e)=>getComputedStyle(e).color')=='rgb(17, 17, 17)',
                            label+': PRINT PHOTO CREDIT CONTRAST LOSS')
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
                    # R120: ordinary Print contains the complete register. Opt-in Print
                    # must produce only the student worksheet, with its own source-custody notice.
                    if js and w in (390,1440):
                        page.emulate_media(media='screen')
                        page.evaluate("window.__fv_print_calls=0;window.print=()=>{window.__fv_print_calls++};null")
                        page.locator('[data-fv-print-student]').click()
                        require(page.evaluate("document.body.classList.contains('fv-worksheet-only')") and
                                page.evaluate("window.__fv_print_calls") == 1,
                                label+': student-only print mode did not activate')
                        page.emulate_media(media='print')
                        require(page.locator('[data-fv-student-print]').is_visible(),
                                label+': standalone worksheet missing')
                        require(not page.locator('#source-custody').is_visible() and
                                not page.locator('.hero').is_visible() and
                                not page.locator('#classroom-preview .callout').is_visible(),
                                label+': source packet or teacher answer leaked into student print')
                        require(page.locator('.worksheet-standalone-rights').is_visible(),
                                label+': standalone rights notice absent')
                        rights=page.locator('.worksheet-standalone-rights').inner_text()
                        require('0/6' in rights and 'S67-19766' in rights and
                                'not NASA-endorsed' in rights and 'Review Board' in rights,
                                label+': standalone source custody incomplete')
                        require(photo_index.is_visible() and
                                photo_index.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==6,
                                label+': standalone PDF must carry six original photographic record links')
                        require('The complete source register is available on the investigation page' in
                                page.locator('[data-fv-student-print]').inner_text(),
                                label+': standalone handout falsely claims hidden register is printed')
                        require(page.locator('[data-fv-student-print] a[href^="https://www.nasa.gov/"]').count()>=2,
                                label+': standalone worksheet missing its source URLs')
                        if w==390:
                            student_pdf=out/'R120_STUDENT_ONLY_PRINT_390.pdf'
                            page.pdf(path=str(student_pdf),format='Letter',print_background=False,
                                     margin={'top':'10mm','bottom':'10mm','left':'10mm','right':'10mm'})
                            require(student_pdf.read_bytes().startswith(b'%PDF-'),'invalid worksheet PDF')
                            record['worksheet_pdf']={'name':student_pdf.name,'sha256':sha(student_pdf)}
                        page.evaluate("window.dispatchEvent(new Event('afterprint'))")
                        require(not page.evaluate("document.body.classList.contains('fv-worksheet-only')"),
                                label+': afterprint left worksheet-only mode active')
                        # Simulate a cancelled print sheet that emits no afterprint or media event.
                        page.emulate_media(media='screen')
                        page.locator('[data-fv-print-student]').click()
                        page.locator('[data-fv-print-student]').click()
                        require(page.evaluate("window.__fv_print_calls")==3 and
                                page.evaluate("document.body.classList.contains('fv-worksheet-only')"),
                                label+': omitted afterprint blocked second deliberate print')
                        page.evaluate("""document.dispatchEvent(new KeyboardEvent('keydown',
                             {key:'p',ctrlKey:true,bubbles:true}))""")
                        require(not page.evaluate("document.body.classList.contains('fv-worksheet-only')"),
                                label+': native Ctrl+P did not reset prior worksheet mode')
                        page.locator('[data-fv-print-student]').click()
                        page.evaluate("window.dispatchEvent(new Event('pagehide'))")
                        require(not page.evaluate("document.body.classList.contains('fv-worksheet-only')"),
                                label+': pagehide left stale worksheet mode')
                        page.locator('[data-fv-print-student]').click()
                        page.evaluate("window.dispatchEvent(new Event('focus'))")
                        page.wait_for_timeout(850)
                        require(not page.evaluate("document.body.classList.contains('fv-worksheet-only')"),
                                label+': focus recovery failed after abandoned print')
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
            require(len(record['screenshots'])==2 and record['pdf'] is not None and
                    record['worksheet_pdf'] is not None,
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
