"""Cross-lane browser regression of a supplied unchanged R34 staging HTML artifact.

NOT a WordPress, PR #158, or axe-core certification.
"""
import argparse
import hashlib
import json
import pathlib
from playwright.sync_api import sync_playwright

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)


def audit(html: str, output: pathlib.Path):
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        version = browser.version
        for js_enabled in (True, False):
            for width in WIDTHS:
                context = browser.new_context(
                    viewport={'width': width, 'height': 900},
                    java_script_enabled=js_enabled,
                    is_mobile=(width <= 390),
                    has_touch=(width <= 390),
                    reduced_motion='reduce',
                )
                page = context.new_page()
                requests = []
                page.on('request', lambda req: requests.append(req.url))
                page.set_content(html, wait_until='load')
                page.wait_for_timeout(110)
                cards = page.locator('#apollo-r34-records > article')
                assert cards.count() == 6, (width, js_enabled)
                assert cards.locator('a[href^="https://www.nasa.gov/image-detail/"]').count() == 6
                assert all(cards.nth(i).is_visible() for i in range(6))
                controls = page.locator('[data-r34-controls]')
                if js_enabled:
                    assert controls.is_visible(), (width, 'enhancement control missing')
                    year2017 = page.locator('button[data-r34-year="2017"]')
                    if width <= 390:
                        year2017.tap()
                    else:
                        year2017.focus()
                        page.keyboard.press('Enter')
                    assert sum(cards.nth(i).is_visible() for i in range(6)) == 2
                    assert year2017.get_attribute('aria-pressed') == 'true'
                    page.locator('button[data-r34-year="all"]').click()
                    assert all(cards.nth(i).is_visible() for i in range(6))
                else:
                    assert controls.is_hidden()
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth + 1'), (width, js_enabled, 'overflow')
                assert not requests, (width, js_enabled, requests)
                if width in (390, 1440):
                    target = output / f"r35-r34-{width}-{'js' if js_enabled else 'nojs'}.png"
                    page.screenshot(path=str(target), full_page=True, animations='disabled')
                perf = page.evaluate("""() => ({
                    lcp: performance.getEntriesByType('largest-contentful-paint').map(x=>x.startTime).at(-1)||null,
                    cls: performance.getEntriesByType('layout-shift').filter(x=>!x.hadRecentInput).reduce((a,x)=>a+x.value,0),
                    reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches
                })""")
                assert perf['reducedMotion']
                rows.append({
                    'width': width, 'javascript': js_enabled, 'six_sources': True,
                    'no_overflow': True, 'interactive_filter': bool(js_enabled),
                    'lcp_entry_ms': perf['lcp'], 'observed_cls': perf['cls'], 'reduced_motion': True
                })
                context.close()
        browser.close()
    result = {
        'chromium': version, 'modes_passed': len(rows),
        'source_sha256': hashlib.sha256(html.encode()).hexdigest(),
        'axe_core': 'BLOCKED (verified bundle unavailable)',
        'wordpress_staging': 'NOT TESTED',
        'notes': 'R34 static HTML via set_content only; NOT HTTP-navigation CWV or PR #158 theme integration.',
        'results': rows
    }
    (output / 'r35-regression-receipt.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--html', required=True, type=pathlib.Path)
    parser.add_argument('--out', required=True, type=pathlib.Path)
    args = parser.parse_args()
    summary = audit(args.html.read_text(), args.out)
    print(f"Chromium {summary['chromium']}: {summary['modes_passed']} R34 cross-lane modes passed; NOT WordPress/axe-core certification.")
