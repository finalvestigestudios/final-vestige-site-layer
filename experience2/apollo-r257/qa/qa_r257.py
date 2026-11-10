#!/usr/bin/env python3
"""R257 source-matched original Apollo Atlas print/native-details parity QA.

Offline Chromium, verified sealed R238 PHP, print custody regressions; NOT axe,
installed WordPress, genuine browser-UI zoom, production HTTP/CSP or field CWV.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

SEAL = 'f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
WIDTHS = (320, 390, 768, 1440, 1920)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def plain_text(pdf):
    return subprocess.run(['pdftotext', str(pdf), '-'], capture_output=True,
                          check=True, text=True).stdout

def normalize(s):
    return re.sub(r'\s+', ' ', s).strip()

def run(a):
    a.out.mkdir(parents=True, exist_ok=True)
    sealed = a.atlas / 'manifest.json'
    assert digest(sealed.read_bytes()) == SEAL, 'Sealed R238 manifest identity mismatch'
    for path, expected in json.loads(sealed.read_text())['files'].items():
        assert digest((a.atlas / path).read_bytes()) == expected, path
    proc = subprocess.run(['php', str(a.atlas / 'wp-render-shim-r224.php'),
                           str((a.atlas / 'fv-ex2-apollo-r224.php').resolve()), 'normal'],
                          capture_output=True, check=True, text=True)
    raw_html = json.loads(proc.stdout)['html']
    assert raw_html == (a.atlas / 'templates/atlas-fragment.html').read_text(), 'PHP fixture drift'
    upstream = [a.atlas / 'assets/atlas-scoped.css', a.r253, a.r254, a.r255, a.r256]
    css = '\n'.join(p.read_text() for p in upstream)
    extra = a.overlay.read_text()
    assert '@media print' in extra and 'details::details-content' in extra
    assert not any(s in extra.lower() for s in ('payhip', 'checkout', '@import', 'url('))
    def doc(style):
        return ('<!doctype html><html lang="en"><head><meta name="viewport" '
                'content="width=device-width,initial-scale=1"><style>' + style +
                '</style></head><body>' + raw_html + '</body></html>')
    before, after = doc(css), doc(css + '\n' + extra)
    receipt = {'r238_manifest_sha256': SEAL, 'overlay_sha256': digest(a.overlay.read_bytes()),
               'contexts': [], 'print': {}, 'limitations':
               'Offline original PHP markup via set_content, not installed WP/axe/field CWV.'}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        for width in WIDTHS:
            for enabled in (False, True):
                context = browser.new_context(viewport={'width': width, 'height': 900},
                                              java_script_enabled=enabled,
                                              reduced_motion='reduce' if not enabled else 'no-preference',
                                              is_mobile=width <= 390, has_touch=width <= 390)
                page = context.new_page()
                requests = []
                page.on('request', lambda r: requests.append(r.url))
                page.set_content(after)
                drawer = page.locator('#fv-apollo-source-drawer')
                assert page.locator('.fv-apollo-atlas details').count() == 13
                assert not drawer.evaluate('e=>e.open'), 'drawer must stay closed on screen'
                assert page.locator('.fv-apollo-atlas [data-fv-plate-source]').count() == 4
                assert page.locator('a.cta').count() == 1
                assert page.locator('a.cta').get_attribute('href') == FREE
                assert page.evaluate('document.documentElement.scrollWidth - innerWidth') <= 1
                assert not requests, 'unexpected network request'
                if width in (390, 1440):
                    screenshot = page.screenshot(full_page=False)
                    page.set_content(before)
                    assert screenshot == page.screenshot(full_page=False), 'screen view changed'
                    (a.out / f'{width}-{int(enabled)}.png').write_bytes(screenshot)
                    page.set_content(after)
                summary = page.locator('#fv-apollo-source-drawer > summary')
                summary.focus()
                summary.press('Enter')
                assert drawer.evaluate('e=>e.open'), 'Enter should open drawer'
                summary.press('Space')
                assert not drawer.evaluate('e=>e.open'), 'Space should close drawer'
                if width <= 390:
                    summary.tap()
                    assert drawer.evaluate('e=>e.open'), 'mobile tap must open drawer'
                    summary.tap()
                    assert not drawer.evaluate('e=>e.open'), 'mobile tap must close drawer'
                receipt['contexts'].append({'width': width, 'js': enabled,
                                            'source_count': 4, 'details_count': 13,
                                            'screen_unchanged': width in (390, 1440), 'pass': True})
                context.close()
        page = browser.new_page()
        seen = {}
        for state, document, expand in (('baseline_closed', before, False),
                                        ('baseline_open', before, True),
                                        ('fixed_closed', after, False),
                                        ('fixed_open', after, True)):
            page.set_content(document)
            if expand:
                page.locator('details').evaluate_all('els=>els.forEach(e=>e.open=true)')
            page.emulate_media(media='print')
            pdf = a.out / (state + '.pdf')
            pdf_bytes = page.pdf(path=str(pdf), print_background=True)
            txt = plain_text(pdf)
            seen[state] = normalize(txt)
            receipt['print'][state] = {'normalized_text_sha256': digest(normalize(txt).encode('utf-8')),
                                       'pdf_sha256_observation_only': digest(pdf_bytes),
                                       'characters': len(seen[state]),
                                       'source_kind_count': txt.count('Source kind')}
            assert txt.count('Source kind') == 4, 'source drawer custody lost'
            assert 'Explore the complete investigation free of charge' in normalize(txt)
            assert 'S66-58038' in txt and 'S67-15717' in txt and 'S67-21294' in txt
        # Negative control: sealed baseline closed-state output is NOT the same
        # research packet as manually expanding all 13 source/evidence details.
        assert seen['baseline_closed'] != seen['baseline_open'], 'negative control no longer reproduces'
        # R257 should print identical evidence text regardless of prior disclosure state.
        if seen['fixed_closed'] != seen['fixed_open']:
            from difflib import SequenceMatcher
            ratio = SequenceMatcher(None, seen['fixed_closed'], seen['fixed_open']).ratio()
            raise AssertionError(f'closed/open print content differs after R257 (similarity={ratio:.4f})')
        pdf_bytes_by_state = {key: receipt['print'][key].pop('pdf_sha256_observation_only')
                              for key in ('baseline_closed','baseline_open','fixed_closed','fixed_open')}
        (a.out / 'pdf-binary-sha256.json').write_text(json.dumps(pdf_bytes_by_state, indent=2, sort_keys=True) + '\n')
        receipt['print']['negative_control_missing_chars'] = len(seen['baseline_open']) - len(seen['baseline_closed'])
        receipt['print']['fixed_closed_equals_open'] = True
        assert receipt['print']['negative_control_missing_chars'] >= 500
        browser.close()
    (a.out / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'contexts': len(receipt['contexts']), 'print': receipt['print']}, sort_keys=True))

if __name__ == '__main__':
    arg = argparse.ArgumentParser()
    for n in ('atlas', 'r253', 'r254', 'r255', 'r256', 'overlay', 'out'):
        arg.add_argument('--'+n, type=Path, required=True)
    run(arg.parse_args())
