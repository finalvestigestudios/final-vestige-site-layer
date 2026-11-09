#!/usr/bin/env python3
"""Offline staging-only Apollo AX-tree / print / no-JS acceptance.

Uses SHA-pinned R238 inputs and invokes the actual R224 PHP shortcode shim.
CDP's live Chromium accessibility tree is not axe-core or a screen-reader audit.
No WordPress, site, merchant, telemetry or social changes are made.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

MANIFEST = 'f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
RECORDS = ('Apollo 204 Review Board', 'S66-58038', 'S67-15717', 'S67-21294')
WIDTHS = (320, 390, 768, 1440, 1920)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(root):
    assert digest(root / 'manifest.json') == MANIFEST, 'unexpected Apollo source manifest'
    manifest = json.loads((root / 'manifest.json').read_text())
    assert manifest['status'] == 'STAGING_HOLD' and manifest['not_live'] is True
    for path, expected in sorted(manifest['files'].items()):
        assert digest(root / path) == expected, 'source file drift: ' + path
    result = subprocess.run(['php', str(root / 'wp-render-shim-r224.php'),
        str((root / 'fv-ex2-apollo-r224.php').resolve()), 'normal'],
        capture_output=True, text=True, check=True, timeout=20)
    parsed = json.loads(result.stdout)
    assert parsed['css'] == 'enqueued' and not parsed['fallback'] and not parsed['js']
    fragment = parsed['html']
    assert fragment == (root / 'templates/atlas-fragment.html').read_text()
    assert fragment.count('class="cta"') == 1 and fragment.count('href="'+FREE+'"') == 1
    assert all(record in fragment for record in RECORDS)
    assert not re.search(r'<script\b|<iframe\b|data-(?:latitude|longitude)|payhip|awin1', fragment, re.I)
    return fragment, (root / 'assets/atlas-scoped.css').read_text()


def live_ax(page):
    session = page.context.new_cdp_session(page)
    nodes = session.send('Accessibility.getFullAXTree')['nodes']
    return [(n.get('role', {}).get('value', ''), n.get('name', {}).get('value', ''))
            for n in nodes if not n.get('ignored')]


def assert_accessibility(page):
    assert page.get_by_role('heading', name=re.compile('A fire.*A record')).count() == 1
    links = page.locator('a')
    assert links.count() >= 50
    assert page.locator('a.cta').count() == 1
    assert page.locator('a.cta').get_attribute('href') == FREE
    assert page.locator('details.fv-apollo-source-drawer').count() == 1
    assert page.locator('[data-fv-plate-source]').count() == 4
    assert page.locator('section#fv-apollo-chronology time[datetime]').count() >= 5
    # Accessibility names come from Chromium's actual computed AX tree, not raw aria-label text.
    drawer = page.locator('details.fv-apollo-source-drawer')
    drawer.locator('summary').click()
    assert drawer.evaluate('(e) => e.open')
    pairs = live_ax(page)
    names = [name for role, name in pairs if role == 'link']
    assert len([name for name in names if name.startswith('Verify at NASA:')]) == 4, names
    assert len([name for name in names if name.startswith('Find ') and 'in the investigation' in name]) == 4
    for record in RECORDS:
        assert any(record in name for name in names if name.startswith('Verify at NASA:')), record
    assert not [name for role, name in pairs if role == 'link' and not name.strip()], 'unnamed AX links'
    ids = page.evaluate('''() => [...document.querySelectorAll('[id]')].map(n=>n.id)''')
    assert len(ids) == len(set(ids)), 'duplicate ids'
    unresolved = page.evaluate('''() => [...document.querySelectorAll('a[href^="#"]')]
       .map(a=>a.getAttribute('href').slice(1)).filter(id=>id && !document.getElementById(id))''')
    assert not unresolved, unresolved
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
    return len(names)


def test_print(page):
    page.emulate_media(media='print')
    state = page.evaluate('''() => {
       const e=document.querySelector('.fv-apollo-print-custody');
       return {visible:getComputedStyle(e).display!='none',
       text:e.textContent, links:[...e.querySelectorAll('a')].map(a=>a.href),
       color:getComputedStyle(e).color}; }''')
    assert state['visible'] and 'S67-21294' in state['text'] and 'S66-58038' in state['text']
    assert 'Apollo 204 Review Board' in state['text'] and len(state['links']) >= 6
    assert state['color'] == 'rgb(0, 0, 0)', 'print text must be legible on paper'
    page.emulate_media(media='screen')
    assert page.locator('.fv-apollo-print-custody').evaluate(
        '(e)=>getComputedStyle(e).display') == 'none'
    return len(state['links'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--atlas', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    root = args.atlas.resolve()
    assert not args.out.exists(), 'never overwrite existing receipts'
    fragment, css = identity(root)
    doc = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+fragment+'</body></html>'
    args.out.mkdir(parents=True)
    captures = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                                     args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (False, True):
                ctx = browser.new_context(viewport={'width':width, 'height':900},
                    java_script_enabled=js, is_mobile=width<=390, has_touch=width<=390,
                    reduced_motion='reduce', forced_colors='active' if width==768 else 'none')
                page = ctx.new_page()
                requests = []
                page.on('request', lambda request: requests.append(request.url))
                page.set_content(doc, wait_until='load')
                named = assert_accessibility(page)
                print_links = test_print(page)
                assert not requests, 'external request'
                keyboard_page = ctx.new_page()
                keyboard_page.set_content(doc, wait_until='load')
                keyboard_page.keyboard.press('Tab')
                assert keyboard_page.evaluate('document.activeElement.getAttribute("href")') == '#fv-apollo-main'
                keyboard_page.keyboard.press('Enter')
                assert keyboard_page.evaluate('document.activeElement.id') == 'fv-apollo-main'
                keyboard_page.close()
                # Capture from a clean browser page to avoid transient focus/hover states.
                shot = ctx.new_page()
                shot.set_content(doc, wait_until='load')
                shot.mouse.move(0,0)
                shot.wait_for_timeout(80)
                filename=f'{width}-{"js" if js else "nojs"}.png'
                shot.screenshot(path=str(args.out / filename), full_page=True, animations='disabled')
                captures.append({'width':width, 'js':js, 'computed_ax_link_names':named,
                    'printed_custody_links':print_links, 'screenshot_sha256':digest(args.out / filename)})
                ctx.close()
        # Optical zoom surrogate. This is NOT authenticated browser-interface zoom.
        ctx=browser.new_context(viewport={'width':1280,'height':900})
        page=ctx.new_page()
        page.set_content(doc)
        page.evaluate("document.querySelector('.fv-apollo-atlas').style.zoom='200%'")
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), '200% CSS zoom horizontal overflow'
        assert page.locator('a.cta').is_visible()
        ctx.close()
        version=browser.version
        browser.close()
    receipt={'run':'Apollo R240','source_manifest_sha256':MANIFEST,'php_render':'PASS',
        'chromium_version':version,'contexts':len(captures),'captures':captures,
        'cdp_accessibility_tree':'PASS (live Chromium AX node names)',
        'print_custody':'PASS (native Chromium print media)',
        'css_zoom_200_percent':'PASS (approximation; NOT browser interface zoom)',
        'axe_core':'NOT_EXECUTED (unavailable offline)','screen_reader':'NOT_TESTED',
        'wordPress_assembler':'NOT_TESTED','field_cwv':'NOT_TESTED','commercial_media_rights':'NOT_CLEARED',
        'verified_sales':'NOT_OBSERVABLE','release':'STAGING_HOLD'}
    (args.out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'contexts':len(captures),'chromium_version':version,
         'receipt_sha256':digest(args.out/'receipt.json'),'release':'STAGING_HOLD'}))


if __name__ == '__main__':
    main()
