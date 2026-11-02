#!/usr/bin/env python3
"""R73: real Chromium and generated-PDF verification of closed rights disclosure custody.

This is a standalone source document, not an installed WordPress/Assembler test.
"""
from __future__ import annotations
import argparse, hashlib, io, json, re, sys, tempfile
from pathlib import Path
from pypdf import PdfReader
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_atlas import build_rights_matrix_r71, validate_custody

WIDTHS = (320, 360, 390, 428, 768, 1024, 1440, 1920)


def run(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    custody = validate_custody()
    with tempfile.TemporaryDirectory() as td:
        provenance = build_rights_matrix_r71(Path(td))
        document = (Path(td) / 'apollo-r71-media-rights-STAGING-ONLY.html').read_text()
    receipt = {'schema': 'fv.apollo.r73.print-custody.chromium.v1',
               'release': 'STAGING_HOLD', 'actual_wordpress': False,
               'rights_cleared': 0, 'hosted_CWV': False, 'builder': provenance,
               'cases': [], 'screenshots': {}, 'pdf': None}
    with sync_playwright() as playwright:
        options = {'headless': True, 'args': ['--no-sandbox']}
        if Path('/usr/bin/chromium').exists():
            options['executable_path'] = '/usr/bin/chromium'
        browser = playwright.chromium.launch(**options)
        for width in WIDTHS:
            for enabled in (False, True):
                context = browser.new_context(
                    viewport={'width': width, 'height': 850},
                    java_script_enabled=enabled, reduced_motion='reduce',
                    has_touch=width <= 390, is_mobile=width <= 390,
                    forced_colors='active' if width == 390 else 'none')
                page = context.new_page()
                errors, requests = [], []
                page.on('pageerror', lambda exc: errors.append(str(exc)))
                page.on('request', lambda req: requests.append(req.url))
                page.set_content(document, wait_until='load')
                assert page.locator('[data-r71-rights-row]:visible').count() == 6
                assert page.locator('[data-r73-print-proof]').count() == 6
                assert page.locator('[data-r73-print-proof]:visible').count() == 0
                assert page.locator('[data-r71-rights] details[open]').count() == 0

                # Normal browser mode: disclosure is genuinely usable without JS.
                first = page.locator('[data-r71-rights] summary').first
                first.focus()
                page.keyboard.press('Enter')
                assert first.evaluate('(el) => el.parentElement.open')
                page.keyboard.press('Enter')
                assert not first.evaluate('(el) => el.parentElement.open')

                if enabled:
                    button = page.locator('[data-fva-filter="2017"]')
                    button.tap() if width <= 390 else button.click()
                    assert page.locator('[data-fva-record]:visible').count() == 2
                assert page.locator('[data-r71-rights-row]:visible').count() == 6
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')
                if width in (390, 1440) and enabled:
                    screenshot = page.screenshot(full_page=True, animations='disabled')
                    assert screenshot == page.screenshot(full_page=True, animations='disabled')
                    name = f'R73_RIGHTS_SCREEN_{width}.png'
                    (out / name).write_bytes(screenshot)
                    receipt['screenshots'][name] = hashlib.sha256(screenshot).hexdigest()

                # Real print CSS: every record must render even with <details> closed.
                page.emulate_media(media='print')
                assert page.locator('[data-r71-rights] details:visible').count() == 0
                panels = page.locator('[data-r73-print-proof]:visible')
                assert panels.count() == 6, (width, enabled, panels.count())
                for index, source in enumerate(custody['records']):
                    panel = panels.nth(index)
                    rendered = panel.inner_text()
                    assert source['catalog'] in rendered
                    assert source['date_label'] in rendered
                    assert 'Individual photo review outstanding' in rendered
                    assert panel.locator('[data-r73-print-url]').inner_text() == source['photo_url']
                    assert 'Credit:' in rendered and 'Producing center:' in rendered
                    assert 'Catalog verification:' in rendered
                    assert 'Documentary boundary:' in rendered
                assert page.locator('[data-fva-record]:visible').count() == 6
                if width in (390, 1440) and enabled:
                    picture = page.screenshot(full_page=True, animations='disabled')
                    assert picture == page.screenshot(full_page=True, animations='disabled')
                    name = f'R73_RIGHTS_PRINT_{width}.png'
                    (out / name).write_bytes(picture)
                    receipt['screenshots'][name] = hashlib.sha256(picture).hexdigest()

                if width == 1440 and not enabled:
                    # Actual Chromium PDF output, not merely CSS visibility.
                    pdf = page.pdf(format='A4', print_background=True)
                    text = ' '.join((page.extract_text() or '')
                                    for page in PdfReader(io.BytesIO(pdf)).pages)
                    normalized = re.sub(r'\s+', ' ', text)
                    exact = re.findall(r'Individual photo review outstanding', normalized)
                    assert len(exact) == 6, ('PRINT_PDF_CUSTODY_INCOMPLETE', len(exact))
                    for source in custody['records']:
                        assert source['catalog'] in normalized, ('PRINT_PDF_ID_MISSING', source['id'])
                    pdf_name = 'R73_CLOSED_RIGHTS_PRINT_1440.pdf'
                    (out / pdf_name).write_bytes(pdf)
                    receipt['pdf'] = {
                        'sha256': hashlib.sha256(pdf).hexdigest(),
                        'pages': len(PdfReader(io.BytesIO(pdf)).pages),
                        'individual_rights_statements': len(exact),
                        'source_catalogs': 6}
                assert not requests and not errors, (width, enabled, requests, errors)
                receipt['cases'].append({'width': width, 'javascript_enabled': enabled,
                                         'print_panels': 6, 'screen_panels': 0, 'passed': True})
                context.close()
        browser.close()
    assert len(receipt['cases']) == 16
    assert receipt['pdf'] is not None
    (out / 'R73_PRINT_CUSTODY_BROWSER_RECEIPT.json').write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print('PASS', len(result['cases']), 'Chromium cases, six PDF rights statements; STAGING_HOLD')
