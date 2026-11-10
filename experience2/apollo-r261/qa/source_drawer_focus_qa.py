#!/usr/bin/env python3
"""R261 original-PHP offline focus check. Does NOT assert installed WP / axe."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

SEAL = 'f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
CSS = ('apollo-r253/atlas-source-actions.css', 'apollo-r254/provenance-tap-continuity.css',
       'apollo-r255/evidence-path-touch.css', 'apollo-r256/print-custody.css',
       'apollo-r257/print-full-evidence.css', 'apollo-r260/hash-target-orientation.css')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def insist(condition, message):
    if not condition:
        raise AssertionError(message)

def run(a):
    source, overlays, out = a.atlas.resolve(), a.overlays.resolve(), a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    insist(digest((source / 'manifest.json').read_bytes()) == SEAL, 'fixture manifest changed')
    for name, expected in json.loads((source / 'manifest.json').read_text())['files'].items():
        insist(digest((source / name).read_bytes()) == expected, 'source changed: ' + name)
    html = json.loads(subprocess.run(['php', str(source / 'wp-render-shim-r224.php'),
            str(source / 'fv-ex2-apollo-r224.php'), 'normal'], capture_output=True,
            text=True, check=True).stdout)['html']
    insist(html == (source / 'templates/atlas-fragment.html').read_text(), 'PHP HTML drift')
    script = (overlays / 'apollo-r261/source-drawer-focus.js').read_text()
    insist(all(s not in script for s in ('fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage',
                                       'sendBeacon', 'location.assign', 'history.pushState')),
           'unexpected network/storage/history API')
    css = '\n'.join([(source / 'assets/atlas-scoped.css').read_text()] +
                    [(overlays / name).read_text() for name in CSS])
    doc = ('<!doctype html><html lang="en"><head><meta name="viewport" '
           'content="width=device-width,initial-scale=1"><style>' + css + '</style></head><body>'
           + html + '</body></html>')
    receipt = {'manifest_sha256': SEAL, 'script_sha256': digest(script.encode()),
               'php_html_sha256': digest(html.encode()), 'cases': [], 'screenshots': {},
               'axe': 'NOT EXECUTED', 'installed_wordpress': 'NOT TESTED',
               'real_http_csp': 'NOT TESTED', 'field_lcp_cls': 'NOT MEASURED'}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=a.chromium, args=['--no-sandbox'])
        for width in (320, 390, 768, 1440, 1920):
            for js in (False, True):
                ctx = browser.new_context(viewport={'width': width, 'height': 900},
                     java_script_enabled=js, is_mobile=width <= 390,
                     has_touch=width <= 390, reduced_motion='reduce')
                page = ctx.new_page()
                requests = []
                page.on('request', lambda request: requests.append(request.url))
                page.set_content(doc)
                if js:
                    page.add_script_tag(content=script)
                selector = 'a[href="#fv-apollo-source-drawer"]'
                insist(page.locator(selector).count() == 1, 'source drawer link changed')
                insist(page.locator('a[href="' + FREE + '"]').count() == 1, 'free CTA changed')
                insist(page.locator('a[href^="https://www.nasa.gov/"]').count() == 55,
                       'NASA source hyperlinks changed')
                insist(page.locator('a[href^="#"]').count() == 31, 'fragment links changed')
                insist(not requests, 'unexpected network request: ' + repr(requests))
                link = page.locator(selector)
                drawer = page.locator('#fv-apollo-source-drawer')
                summary = drawer.locator('summary')
                insist(not drawer.evaluate('(el) => el.open'), 'initial drawer should be collapsed')
                link.focus()
                link.press('Enter')
                page.wait_for_timeout(65)
                state = page.evaluate('''() => ({
                  hash: location.hash, isTarget: document.querySelector('#fv-apollo-source-drawer').matches(':target'),
                  open: document.querySelector('#fv-apollo-source-drawer').open,
                  focus: document.activeElement === document.querySelector('#fv-apollo-source-drawer summary'),
                  noOverflow: document.documentElement.scrollWidth <= innerWidth + 1
                })''')
                insist(state['hash'] == '#fv-apollo-source-drawer' and state['isTarget'],
                       'native fragment navigation lost: ' + str(state))
                insist(state['noOverflow'], 'horizontal overflow: ' + str(width))
                if js:
                    insist(state['open'] and state['focus'], 'focus bridge failed: ' + str(state))
                    summary.press('Enter')
                    insist(not drawer.evaluate('(el) => el.open'), 'native collapse broken')
                    link.click()  # Repeat navigation to the same hash must reopen/focus.
                    page.wait_for_timeout(65)
                    insist(drawer.evaluate('(el) => el.open') and
                           summary.evaluate('(el) => el === document.activeElement'),
                           'same-hash repeat link did not reveal/focus summary')
                else:
                    insist(not state['open'], 'no-JS native drawer unexpectedly autoexpanded')
                    summary.focus()
                    summary.press('Enter')
                    insist(drawer.evaluate('(el) => el.open'), 'no-JS native disclosure broken')
                if width in (390, 1440):
                    image = page.screenshot(animations='disabled')
                    name = f'{width}-{"js" if js else "nojs"}.png'
                    (out / name).write_bytes(image)
                    receipt['screenshots'][name] = digest(image)
                receipt['cases'].append({'width': width, 'js': js, 'status': 'PASS'})
                ctx.close()
        # Fragment visited by direct URL before enhancement loads: reveal, no unsolicited focus.
        ctx = browser.new_context(viewport={'width': 390, 'height': 900})
        page = ctx.new_page()
        page.set_content(doc)
        page.evaluate("location.hash = '#fv-apollo-source-drawer'")
        page.wait_for_timeout(60)
        page.add_script_tag(content=script)
        insist(page.locator('#fv-apollo-source-drawer').evaluate('(el) => el.open'),
               'direct deep link should reveal source records')
        insist(not page.locator('#fv-apollo-source-drawer summary').evaluate(
               '(el) => el === document.activeElement'), 'initial load stole focus')
        receipt['cases'].append({'direct_hash': True, 'status': 'PASS'})
        ctx.close()
        # Forced-colors accessibility and native visibility are checked separately.
        ctx = browser.new_context(viewport={'width': 390, 'height': 900},
                                  forced_colors='active', reduced_motion='reduce')
        page = ctx.new_page()
        page.set_content(doc)
        page.add_script_tag(content=script)
        page.locator('a[href="#fv-apollo-source-drawer"]').click()
        page.wait_for_timeout(65)
        insist(page.locator('#fv-apollo-source-drawer summary').evaluate(
               '(el) => el === document.activeElement'), 'forced-colors focus lost')
        insist(page.locator('#fv-apollo-source-drawer').evaluate(
               '(el) => getComputedStyle(el).outlineWidth') == '3px', 'target outline lost')
        receipt['cases'].append({'forced_colors': True, 'status': 'PASS'})
        ctx.close()
        browser.close()
    receipt['stable_sha256'] = digest(json.dumps(receipt, sort_keys=True,
                                               separators=(',', ':')).encode())
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'passed': True, 'contexts': len(receipt['cases']),
                      'sha256': receipt['stable_sha256']}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--atlas', type=Path, required=True)
    parser.add_argument('--overlays', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--chromium', default='/usr/bin/chromium')
    run(parser.parse_args())
