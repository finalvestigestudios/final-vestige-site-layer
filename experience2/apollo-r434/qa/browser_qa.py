"""Real Chromium, exact PHP-generated offline HTML; NOT an HTTP staging run."""
import json
from pathlib import Path
import subprocess
from urllib.parse import urlparse,parse_qs
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parents[1]
QA = HERE/'QA'
SHOTS = QA/'screenshots'
SHOTS.mkdir(parents=True,exist_ok=True)
WIDTHS = (320,360,390,768,1024,1440,1920)
checks=0

def ok(value,message):
    global checks
    assert value,message
    checks+=1

def main():
    html=subprocess.run(['php',str(HERE/'qa/fixture.php')],capture_output=True,check=True).stdout.decode()
    (QA/'fixture.html').write_text(html)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        try:
            for width in WIDTHS:
                context=browser.new_context(viewport={'width':width,'height':900},accept_downloads=True)
                page=context.new_page()
                page.set_content(html)
                ok(page.locator('[data-fv-r434]').count()==2,f'{width} real PHP-rendered routes')
                ok(page.locator('[data-fv-r434] .fv-r434__row').count()==6,f'{width} 3 source rows each')
                ok(page.locator('[data-fv-r434] .fv-r429__cta').count()==2,f'{width} one CTA each')
                ok(page.locator('[data-fv-r434] .fv-r430__question').count()==6,f'{width} underlying questions')
                ok(page.locator('[data-fv-r434] [data-fv-r431-actions]:not([hidden])').count()==2,f'{width} JS export ready')
                ok(page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),f'{width} no horizontal overflow')
                ok(page.evaluate("() => {const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return ids.length===new Set(ids).size}"), f'{width} unique IDs')
                ok(page.locator('[data-fv-r434] .fv-r429__cta').first.evaluate('(x)=>!!x.offsetParent'),f'{width} free CTA visible above closed deep-dive')
                ok(page.locator('a[href*=payhip],a[href*=checkout]').count()==0,f'{width} no merchant link')
                href=page.locator('[data-fv-r434] .fv-r429__cta').first.get_attribute('href')
                ok(parse_qs(urlparse(href).query).get('utm_content') == ['fixture_not_a_published_asset'],f'{width} safe test UTM continuity')
                page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True)
                context.close()
            context=browser.new_context(viewport={'width':390,'height':900},accept_downloads=True)
            page=context.new_page();page.set_content(html)
            deep=page.locator('[data-fv-r434] details.fv-r434__deep').first
            ok(not deep.evaluate('(x)=>x.open'),'deep source content collapsed initially')
            deep.locator('summary').first.focus();page.keyboard.press('Enter')
            ok(deep.evaluate('(x)=>x.open'),'keyboard opens exact-source desk')
            limit=page.locator('[data-fv-r434] .fv-r433__claim details').first
            limit.locator('summary').focus();page.keyboard.press('Enter')
            ok(limit.evaluate('(x)=>x.open'),'keyboard expands NASA boundary')
            note=page.locator('[data-fv-r434] textarea').first
            note.fill('NASA Board reports probable arc; no exact initiating spark proven.')
            ok('1 of 3' in page.locator('[data-fv-r434] [data-fv-r431-progress]').first.inner_text(),'note updates')
            with page.expect_download() as dl:
                page.locator('[data-fv-r434] [data-fv-r431-export]').first.click()
            note_file=QA/'sample-notes.txt';dl.value.save_as(str(note_file))
            ok('no exact initiating spark' in note_file.read_text(),'actual browser-generated text download')
            ok('nasa.gov' in note_file.read_text().lower(),'export includes source citation')
            page.screenshot(path=str(SHOTS/'390-source-and-notes.png'),full_page=True)
            page.emulate_media(media='print')
            ok(page.locator('.fv-r434__boundary').first.evaluate("(x)=>getComputedStyle(x).display!=='none'"),'claim limitations visible in print')
            page.screenshot(path=str(SHOTS/'390-print.png'),full_page=True)
            context.close()
            context=browser.new_context(viewport={'width':390,'height':900},java_script_enabled=False)
            page=context.new_page();page.set_content(html)
            ok(page.locator('.fv-r429__cta').count()==2,'no-JS two free article links')
            ok(page.locator('[data-fv-r431-actions]:visible').count()==0,'no-JS hidden JS-only export actions')
            deep=page.locator('details.fv-r434__deep').first
            deep.locator('summary').first.click()
            ok(deep.evaluate('(x)=>x.open'),'no-JS full historical record accessible')
            ok(page.locator('.fv-r433__claim').count()==6,'no-JS exact source inherited')
            page.screenshot(path=str(SHOTS/'390-nojs.png'),full_page=True)
            context.close()
            context=browser.new_context(viewport={'width':320,'height':900},has_touch=True,is_mobile=True,reduced_motion='reduce',forced_colors='active')
            page=context.new_page();page.set_content(html)
            page.locator('details.fv-r434__deep').first.locator('summary').first.tap()
            ok(page.locator('details.fv-r434__deep').first.evaluate('(x)=>x.open'),'touch opens native full source')
            page.add_style_tag(content='html{font-size:200%!important}')
            ok(page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),'200% text / forced-colors / reduced-motion fit')
            page.screenshot(path=str(SHOTS/'320-touch-forced-colors-200text.png'),full_page=True)
            context.close()
        finally:
            browser.close()
    report={'status':'PASS_ACTUAL_PHP_OFFLINE_CHROMIUM_ONLY','assertions':checks,'screenshot_count':len(list(SHOTS.glob('*.png'))), 'browser':'/usr/bin/chromium','source':'PHP R429-R434 exact local files', 'actual_navigated_http':'NOT_PASSED_ADMINISTRATOR_BLOCK','installed_wordpress_staging':'NOT_EXECUTED','axe_core':'NOT_AVAILABLE_SHA_REVIEWED_BUNDLE','navigated_lcp_ms':None,'navigated_cls':None,'field_p75':None,'commercial_conversions':'NOT_VERIFIED'}
    (QA/'browser-report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(f'PASS {checks} offline Chromium assertions, {report["screenshot_count"]} screenshots; real navigated staging/axe/CWV HOLD')
if __name__=='__main__':main()
