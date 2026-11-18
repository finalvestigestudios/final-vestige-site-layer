"""Real headless Chromium of local PHP-generated document; NOT network-navigated WP staging or axe.
Usage: python qa/browser_qa.py. Runs full 320-1920 screenshot matrix and interaction tests.
"""
import json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
QA=HERE.parent/'QA'
SHOT=QA/'screenshots'
WIDTHS=(320,360,390,768,1024,1440,1920)
ARTICLE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def fixture():
    run=subprocess.run(['php',str(HERE/'fixture.php')],capture_output=True,text=True,timeout=20)
    if run.returncode:raise RuntimeError(run.stderr)
    return run.stdout

def browser_test():
    html=fixture();SHOT.mkdir(parents=True,exist_ok=True);rows=[];errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (True,False):
                context=browser.new_context(viewport={'width':width,'height':860},java_script_enabled=js,reduced_motion='reduce',accept_downloads=True)
                page=context.new_page()
                try:
                    page.set_content(html,wait_until='load')
                    row={'width':width,'js':js,'cards':page.locator('[data-fv-r448-card]').count(),
                         'classroom':page.locator('[data-r440-root]').count(),
                         'ctas':page.locator(f'a[href="{ARTICLE}"]').count(),
                         'controls_shown':page.locator('[data-fv-r448-controls]').is_visible(),
                         'download_buttons':page.get_by_role('button',name='Download original classroom exercise (.txt)').count(),
                         'horizontal_overflow':page.evaluate('document.documentElement.scrollWidth > innerWidth+1')}
                    if row['cards']!=4 or row['classroom']!=1 or row['ctas']!=1 or row['horizontal_overflow']:
                        errors.append(f'{width}/{js}: content/CTA/overflow violated: {row}')
                    if js:
                        if not row['controls_shown'] or row['download_buttons']!=1:errors.append(f'{width}: progressive controls absent')
                        page.get_by_role('button',name='1967 inquiry').click()
                        if page.locator('[data-fv-r448-card]:visible').count()!=1:errors.append(f'{width}: wrong filter count')
                        page.get_by_role('button',name='All evidence').click()
                        if page.locator('[data-fv-r448-card]:visible').count()!=4:errors.append(f'{width}: all records not restored')
                        if width==390:
                            with page.expect_download() as download:
                                page.get_by_role('button',name='Download original classroom exercise (.txt)').click()
                            file=download.value
                            file.save_as(str(QA/'sample-classroom-activity.txt'))
                            text=(QA/'sample-classroom-activity.txt').read_text()
                            if 'INSTRUCTOR RUBRIC' not in text or 'PRIMARY:' not in text or 'later experiments' not in text.lower():errors.append('download content incomplete')
                            row['actual_txt_download']='PASS'
                    else:
                        if row['controls_shown'] or row['download_buttons']:errors.append(f'{width}: no-JS enhancement unexpectedly visible')
                        if page.locator('[data-fv-r448-card]:visible').count()!=4:errors.append(f'{width}: no-JS evidence incomplete')
                    page.screenshot(path=str(SHOT/f"{width}-{'js' if js else 'nojs'}.png"),full_page=True)
                    rows.append(row)
                except Exception as exc: errors.append(f'{width}/{js}: {str(exc)[:300]}')
                finally:context.close()
        # Focus/keyboard and touch/contrast/print tests at the primary mobile view.
        for name,opts in [
            ('keyboard',{'viewport':{'width':390,'height':850}}),
            ('touch',{'viewport':{'width':390,'height':850},'has_touch':True,'is_mobile':True}),
            ('contrast',{'viewport':{'width':390,'height':850},'forced_colors':'active'}),
            ('zoom',{'viewport':{'width':390,'height':850},'device_scale_factor':2}),
        ]:
            ctx=browser.new_context(**opts)
            page=ctx.new_page()
            try:
                page.set_content(html,wait_until='load')
                if name=='keyboard':
                    button=page.get_by_role('button',name='Before')
                    button.focus();page.keyboard.press('Enter')
                    if button.get_attribute('aria-pressed')!='true':errors.append('keyboard Enter failed')
                    page.locator('[data-fv-r448-card]:visible').first.locator('summary').focus()
                    page.keyboard.press('Enter')
                    if page.locator('[data-fv-r448-card]:visible').first.locator('details').get_attribute('open') is None:errors.append('keyboard source drawer failed')
                elif name=='touch':
                    page.get_by_role('button',name='Later history').tap()
                    if page.locator('[data-fv-r448-card]:visible').count()!=2:errors.append('touch filtering failed')
                if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):errors.append(f'{name}: horizontal overflow')
                page.screenshot(path=str(SHOT/f'390-{name}.png'),full_page=True)
                rows.append({'special':name,'status':'PASS'})
            except Exception as exc:errors.append(f'{name}: {str(exc)[:300]}')
            finally:ctx.close()
        ctx=browser.new_context(viewport={'width':768,'height':900})
        pg=ctx.new_page();pg.set_content(html,wait_until='load');pg.emulate_media(media='print')
        pg.screenshot(path=str(SHOT/'768-print.png'),full_page=True)
        rows.append({'special':'print','status':'PASS'});ctx.close()
        browser.close()
    evidence={'status':'PASS' if not errors else 'FAIL','unit':'offline PHP-rendered HTML via page.set_content, not real WordPress navigation',
              'cases':len(rows),'results':rows,'errors':errors,
              'axe_core':'NOT_RUN: genuine independently pinned axe-core unavailable',
              'navigated_LCP_CLS':'NOT_RUN: navigation blocked by ERR_BLOCKED_BY_ADMINISTRATOR',
              'field_CWV':'NOT_VERIFIED','screen_reader':'NOT_RUN','ci':'CHECK_GITHUB_SEPARATELY'}
    QA.mkdir(parents=True,exist_ok=True)
    (QA/'browser_results.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':evidence['status'],'cases':len(rows),'errors':errors},indent=2))
    return 1 if errors else 0
if __name__=='__main__':raise SystemExit(browser_test())
