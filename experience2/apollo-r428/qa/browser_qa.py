"""Real Chromium interaction checks of PHP-generated R428 HTML; NOT navigated WordPress staging.

The executive control explicitly distinguishes offline page.set_content from true HTTP navigation,
axe-core results, and LCP/CLS. All unrun gates remain HOLD. No fake scores.
"""
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'QA'
SCREENS = QA / 'screenshots'
SCREENS.mkdir(parents=True, exist_ok=True)
SOURCE = subprocess.run(['php', str(ROOT/'qa'/'fixture.php')], check=True, capture_output=True, text=True).stdout
passes = []


def assert_check(name, ok):
    if not ok:
        raise AssertionError(name)
    passes.append(name)


def page_setup(browser, width, **kwargs):
    context = browser.new_context(viewport={'width':width,'height':900}, device_scale_factor=1, **kwargs)
    page = context.new_page()
    page.set_content(SOURCE, wait_until='domcontentloaded')
    return page, context


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    browser_version = browser.version
    for width in (320, 360, 390, 768, 1024, 1440, 1920):
        page, ctx = page_setup(browser, width)
        assert_check(f'{width}:two-executed-php-instances', page.locator('[data-fv-r428]').count()==2)
        assert_check(f'{width}:all-source-drawers', page.locator('details').count()==8)
        assert_check(f'{width}:no-overflow', page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        assert_check(f'{width}:visible-article-ctas', page.locator('.fv-r428__next a').count()==2)
        if width == 390:
            page.locator('summary').first.focus()
            page.keyboard.press('Enter')
            assert_check('keyboard-open-disclosure',page.locator('details').first.evaluate('(el)=>el.open'))
            page.keyboard.press('Enter')
            assert_check('keyboard-close-disclosure',not page.locator('details').first.evaluate('(el)=>el.open'))
        page.screenshot(path=str(SCREENS/f'{width}.png'),full_page=True)
        ctx.close()

    page, ctx=page_setup(browser, 390, java_script_enabled=False)
    assert_check('no-js-native-text', 'electrical arc' in page.locator('[data-fv-r428]').first.inner_text())
    page.locator('summary').first.click()
    assert_check('no-js-native-disclosure',page.locator('details').first.evaluate('(el)=>el.open'))
    page.screenshot(path=str(SCREENS/'no-js.png'),full_page=True)
    ctx.close()

    page,ctx=page_setup(browser,390,has_touch=True,is_mobile=True)
    page.locator('summary').first.tap()
    assert_check('touch-disclosure',page.locator('details').first.evaluate('(el)=>el.open'))
    page.screenshot(path=str(SCREENS/'touch.png'),full_page=True)
    ctx.close()

    page,ctx=page_setup(browser,390,reduced_motion='reduce')
    assert_check('reduced-motion-media',page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches'))
    page.screenshot(path=str(SCREENS/'reduced-motion.png'),full_page=True)
    ctx.close()

    page,ctx=page_setup(browser,390,forced_colors='active')
    assert_check('forced-colors-media',page.evaluate('matchMedia("(forced-colors: active)").matches'))
    page.screenshot(path=str(SCREENS/'forced-colors.png'),full_page=True)
    ctx.close()

    page,ctx=page_setup(browser,390)
    page.evaluate('document.documentElement.style.fontSize="32px"')
    assert_check('200percent-text-no-overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    page.screenshot(path=str(SCREENS/'200pct-text.png'),full_page=True)
    ctx.close()

    page,ctx=page_setup(browser,390)
    page.emulate_media(media='print')
    assert_check('print-css',page.evaluate('getComputedStyle(document.querySelector(".fv-r428")).backgroundColor')=='rgb(255, 255, 255)')
    assert_check('print-limits-actually-visible',page.locator('.fv-r428__print-only').first.evaluate('(el)=>el.getBoundingClientRect().height > 0'))
    page.screenshot(path=str(SCREENS/'print.png'),full_page=True)
    ctx.close()

    browser.close()

qa_status = {
    'component': 'Apollo R428 evidence-to-investigation bridge',
    'browser_version':browser_version,
    'engine':'real Chromium with playwright; executable /usr/bin/chromium',
    'html_source':'actual php qa/fixture.php executed output; NOT installed WordPress',
    'browser_mode':'page.set_content (offline fixture)',
    'checks_passed':len(passes),'check_names':passes,
    'screenshot_count':len(list(SCREENS.glob('*.png'))),
    'gates':{
        'offline_php_html_chromium':'PASS',
        'real_http_navigation':'HOLD: browser navigation prohibited by runtime administrator',
        'axe_core':'HOLD: reviewed pinned axe-core bundle not available locally',
        'navigated_LCP':'HOLD: navigation blocked; no fabricated metric',
        'navigated_CLS':'HOLD: navigation blocked; no fabricated metric',
        'WordPress_staging':'HOLD: not installed or activated',
        'screen_reader':'HOLD: independent AT review not done',
        'paid_sale_attribution':'HOLD: merchant settlement and campaign sessions not available'
    }
}
(QA/'browser_qa.json').write_text(json.dumps(qa_status,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in qa_status.items() if k not in ('check_names',)},indent=2))
