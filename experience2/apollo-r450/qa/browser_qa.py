"""Real Chromium interaction/screenshots on PHP-rendered HTML via set_content.
NOT navigated WordPress staging; no axe or real LCP/CLS claims permitted.
"""
import json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SHOT=ROOT/'QA/screenshots'
WIDTHS=(320,360,390,768,1024,1440,1920)
ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
def browser():
    p=subprocess.run(['php',str(HERE/'fixture.php')],capture_output=True,text=True,timeout=30)
    if p.returncode:raise RuntimeError(p.stderr)
    html=p.stdout
    SHOT.mkdir(parents=True,exist_ok=True)
    rows=[];errors=[]
    with sync_playwright() as pw:
        b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (True,False):
                ctx=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce',accept_downloads=True)
                page=ctx.new_page();tag=f'{width}-'+('js' if js else 'nojs')
                try:
                    page.set_content(html,wait_until='load')
                    counts={'journal':page.locator('[data-fv-r449]').count(), 'receipt':page.locator('[data-fv-r450]').count(),
                      'records':page.locator('[data-r450-claim]').count(), 'claim_cards':page.locator('[data-fv-r448-card]').count(),
                      'ctas':page.locator(f'a[href="{ARTICLE}"]').count(), 'paid':page.locator('a[href*="payhip"],a[href*="checkout"],form').count()}
                    if counts!={'journal':1,'receipt':1,'records':4,'claim_cards':4,'ctas':1,'paid':0}:errors.append(f'{tag}: content {counts}')
                    if page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1'):errors.append(f'{tag}: horizontal overflow')
                    button=page.get_by_role('button',name='Download original four-source receipt (.txt)')
                    if js:
                        if button.count()!=1:errors.append(f'{tag}: receipt export button missing')
                        if width==390:
                            page.locator('[data-fv-r450] summary').click()
                            with page.expect_download() as expected:button.click()
                            download=expected.value
                            dest=ROOT/'QA/original-four-source-receipt.txt';download.save_as(dest)
                            text=dest.read_text()
                            if text.count('SOURCE URL: https://www.nasa.gov/')!=4 or 'Not established:' not in text or 'NOT a NASA publication or endorsement' not in text:
                                errors.append('source receipt download missing citations/limitations or disclosure')
                    elif button.count()!=0:errors.append(f'{tag}: JS-only button visible without JS')
                    if page.locator('[data-r450-claim]').count()!=4:errors.append(f'{tag}: no-JS receipt data incomplete')
                    page.screenshot(path=str(SHOT/f'{tag}.png'),full_page=True)
                    rows.append({'case':tag,'status':'PASS','content':counts})
                except Exception as e:errors.append(f'{tag}: {str(e)[:300]}')
                finally:ctx.close()
        for tag,opts in [('keyboard',{'viewport':{'width':390,'height':850}}),
                         ('touch',{'viewport':{'width':390,'height':850},'has_touch':True,'is_mobile':True}),
                         ('forced-colors',{'viewport':{'width':390,'height':850},'forced_colors':'active'}),
                         ('zoom',{'viewport':{'width':390,'height':850},'device_scale_factor':2}),
                         ('reduced-motion',{'viewport':{'width':390,'height':850},'reduced_motion':'reduce'})]:
            ctx=b.new_context(**opts);page=ctx.new_page()
            try:
                page.set_content(html)
                details=page.locator('[data-fv-r450] details')
                summary=details.locator('summary')
                if tag=='keyboard':
                    summary.focus();page.keyboard.press('Enter')
                    if not details.evaluate('(d)=>d.open'):errors.append('keyboard receipt disclosure did not open')
                    page.keyboard.press('Enter')
                    if details.evaluate('(d)=>d.open'):errors.append('keyboard disclosure did not close')
                    button=page.get_by_role('button',name='Download original four-source receipt (.txt)')
                    button.focus()
                    if not button.evaluate('(el)=>el===document.activeElement'):errors.append('keyboard export not focusable')
                if tag=='touch':
                    summary.tap()
                    if not details.evaluate('(d)=>d.open'):errors.append('touch receipt disclosure failed')
                if page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1'):errors.append(f'{tag}: overflow')
                page.screenshot(path=str(SHOT/f'390-{tag}.png'),full_page=True)
                rows.append({'case':tag,'status':'PASS'})
            except Exception as e:errors.append(f'{tag}: {str(e)[:300]}')
            finally:ctx.close()
        ctx=b.new_context(viewport={'width':768,'height':900});page=ctx.new_page()
        page.set_content(html);page.locator('[data-fv-r450] details').evaluate('(d)=>d.open=true')
        page.emulate_media(media='print');page.screenshot(path=str(SHOT/'768-print.png'),full_page=True)
        rows.append({'case':'print','status':'PASS'});ctx.close();b.close()
    report={'status':'PASS' if not errors else 'FAIL','cases':len(rows),'rows':rows,'errors':errors,
            'mode':'actual PHP-generated markup in Chromium via page.set_content; NOT HTTP navigation or installed WordPress',
            'axe_core':'NOT_RUN','navigated_LCP_CLS':'NOT_RUN','screen_reader':'NOT_RUN','field_CWV':'NOT_VERIFIED'}
    (ROOT/'QA/BROWSER.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'cases':len(rows),'errors':errors}))
    return int(bool(errors))
if __name__=='__main__':raise SystemExit(browser())
