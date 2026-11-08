"""R219 OFFLINE board QA. No website access, tracking, merchant links, or newsletter sends."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(__file__).parent.joinpath('review_board.html').read_text(encoding='utf-8')
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for w, h, zoom in [(320, 740, 1), (360, 740, 1), (390, 844, 1),
                       (768, 1024, 1), (1024, 768, 1), (1440, 900, 1), (390, 844, 2)]:
        page = browser.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
        # Use set_content: this environment's Chromium blocks file:// navigation.
        page.set_content(HTML, wait_until='load')
        if zoom != 1:
            page.evaluate('(z) => document.body.style.zoom = z', zoom)
        stats = page.evaluate('''() => ({
            width: document.documentElement.clientWidth,
            docScroll: document.documentElement.scrollWidth,
            heading: document.querySelector('h1')?.textContent,
            cards: document.querySelectorAll('.card').length,
            links: document.querySelectorAll('a[href]').length,
            scripts: document.querySelectorAll('script').length,
            forms: document.querySelectorAll('form').length,
            inputs: document.querySelectorAll('input').length,
            merchantLinks: [...document.querySelectorAll('a[href]')].filter(
                a => /zen12|hypnosislive|awin/i.test(a.href)).length
        })''')
        assert stats['cards'] == 4
        assert stats['scripts'] == stats['forms'] == stats['inputs'] == stats['merchantLinks'] == 0
        assert stats['docScroll'] <= stats['width'] + 1
        assert 'One confirmed reader' in stats['heading']
        page.keyboard.press('Tab')
        assert page.evaluate('document.activeElement.tagName') == 'A'
        print('PASS', w, h, 'zoom', zoom, 'docWidth', stats['docScroll'], 'links', stats['links'])
        page.close()
    browser.close()
