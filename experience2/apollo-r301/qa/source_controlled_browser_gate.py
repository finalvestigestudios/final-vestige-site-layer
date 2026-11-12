#!/usr/bin/env python3
"""R301 source-controlled offline QA: real PHP, Chromium, no external requests.
Requires php, Python playwright, local Chromium. No WordPress or axe claims.
"""
import re
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[2]
php = root / 'apollo-r281/apollo-source-experience.php'
css = (root / 'apollo-r281/assets/apollo-source-experience.css').read_text()
fixture = root / 'apollo-r301/qa/local_http_fixture.php'
subprocess.run(['php', '-l', str(php)], check=True, capture_output=True)
html = subprocess.check_output(['php', '-r', 'parse_str("instances=2",$_GET);include $argv[1];', str(fixture)], text=True)
assert html.count('data-fv-evidence-status=') == 2
assert '<script' not in html.lower()
html = re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>', '', html)
html = html.replace('</head>', '<style>' + css + '</style></head>')
url = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
passes = 0
negative_controls = 0
def require_editorial(cta):
    assert cta.get_attribute('data-fv-conversion-kind') == 'editorial-continuation', 'non-editorial event category'
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width in (320, 390, 768, 1440, 1920):
        for js in (False, True):
            page = browser.new_page(viewport={'width':width, 'height':850}, java_script_enabled=js,
                                    reduced_motion='reduce', has_touch=True)
            page.set_content(html)
            sections = page.locator('section.fv-r281')
            assert sections.count() == 2
            names = []
            for section in sections.all():
                assert section.get_attribute('data-fv-experience') == 'apollo-1'
                assert section.get_attribute('data-fv-funnel-scope') == 'editorial-evidence'
                assert section.get_attribute('data-fv-evidence-status') == 'editorial-review-pending'
                assert section.locator('[data-fv-funnel-step="evidence-to-investigation"]').count() == 1
                cta = section.locator('[data-fv-cta]')
                assert cta.count() == 1
                assert cta.get_attribute('data-fv-cta') == 'apollo-read-free-investigation'
                require_editorial(cta)
                assert cta.get_attribute('href') == url
                assert section.locator('a[href*="nasa.gov/"]').count() >= 12
                assert section.locator('script,form').count() == 0
                names.append(section.locator('h2').inner_text())
                drawer = section.locator('.fv-r281__drawer').first
                drawer.locator('summary').focus()
                page.keyboard.press('Enter')
                assert drawer.get_attribute('open') is not None
                page.keyboard.press('Space')
                assert drawer.get_attribute('open') is None
                section.locator('.fv-r281__source-jump a').first.click()
                assert section.locator('.fv-r281__source-list li').first.evaluate('(e)=>document.activeElement===e')
                passes += 1
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            ids = page.locator('[id]').evaluate_all('(xs)=>xs.map(x=>x.id)')
            assert len(ids) == len(set(ids))
            ax = page.context.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
            regions = [n.get('name', {}).get('value') for n in ax if n.get('role', {}).get('value') == 'region'
                       and 'What the record establishes' in (n.get('name', {}).get('value') or '')]
            assert len(regions) == 2 and len(set(regions)) == 2
            # Deliberate policy failure: never count an editorial click as a sale.
            cta = sections.first.locator('[data-fv-cta]')
            cta.evaluate("e=>e.setAttribute('data-fv-conversion-kind','paid-order')")
            try:
                require_editorial(cta)
            except AssertionError as exc:
                assert str(exc) == 'non-editorial event category'
                negative_controls += 1
            else:
                raise AssertionError('false paid-order event was accepted')
            page.close()
    browser.close()
assert passes == 20 and negative_controls == 10
print('R301: 10/10 Chromium contexts, 20/20 CTA + keyboard/source routes PASS; 10/10 false-paid-order controls REJECTED')
