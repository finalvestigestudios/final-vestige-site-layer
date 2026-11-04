"""Chromium in-memory screenshot gate; does not contact production or certify WP."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

P = Path(__file__).resolve().parent
HTML = (P / 'observer_bridge_review.html').read_text(encoding='utf-8')
results = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width in (320, 390, 768, 1440, 1920):
        page = browser.new_page(viewport={'width': width, 'height': 900}, device_scale_factor=1, java_script_enabled=False)
        errors = []
        page.on('pageerror', lambda err: errors.append(str(err)))
        page.set_content(HTML, wait_until='load')
        primary = page.locator('a[data-fv-destination="focus"]')
        box = primary.bounding_box()
        observed = page.evaluate('''() => ({overflow: document.documentElement.scrollWidth > innerWidth, scrollWidth: document.documentElement.scrollWidth, viewport: innerWidth, links: document.querySelectorAll('a').length})''')
        assert not observed['overflow'], f'horizontal overflow at {width}: {observed}'
        assert box and box['height'] >= 44 and box['width'] >= 44, (width, box)
        assert primary.get_attribute('href') == 'https://finalvestige.com/focus/'
        page.locator('#variant').screenshot(path=str(P / f'variant-{width}.png'))
        results.append({'width': width, 'overflow': observed['overflow'], 'cta_width': round(box['width'], 1), 'cta_height': round(box['height'], 1), 'links': observed['links'], 'page_errors': errors, 'screenshot': f'variant-{width}.png'})
        page.close()
    page = browser.new_page(viewport={'width': 390, 'height': 844}, java_script_enabled=False)
    page.set_content(HTML)
    page.keyboard.press('Tab')
    focused = page.evaluate('document.activeElement?.tagName')
    assert focused == 'A'
    page.screenshot(path=str(P / 'full-comparison-390.png'), full_page=True)
    browser.close()
print(json.dumps({'browser': 'Chromium', 'scope': 'offline fixture only', 'js': False, 'widths': results, 'keyboard_first_tab': focused, 'lighthouse': 'NOT_RUN', 'axe': 'NOT_RUN', 'wordPress': 'NOT_RUN'}, indent=2))
