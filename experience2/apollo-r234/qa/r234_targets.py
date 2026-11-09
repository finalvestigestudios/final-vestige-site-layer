#!/usr/bin/env python3
"""R234 exact-output Atlas touch-action repair and offline Chromium acceptance.

Pinned parent artifact is R228 (referenced and tested by R233). This deliberately
makes no WordPress installation, rights, or field-performance claims.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

PARENT = '28f1427da6d096c801927ac8e1e8dd8a53f14ff3f6fcb014089ada2bdd662413'
URL = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
WIDTHS = (320, 390, 768, 1440, 1920)
SELECTORS = ('.mast nav > a', '#fv-apollo-chronology .rail > li > a',
             'footer.end p.small > a', '#fv-apollo-evidence .plate > details > a',
             '#fv-apollo-gallery details > a')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def jsonwrite(path, data):
    path.write_text(json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + '\n', encoding='utf8')


def verify(directory):
    assert digest((directory / 'manifest.json').read_bytes()) == PARENT, 'parent manifest drift'
    manifest = json.loads((directory / 'manifest.json').read_text())
    for name, sha in manifest['files'].items():
        assert digest((directory / name).read_bytes()) == sha, f'parent file drift: {name}'
    return manifest


def build(directory, patch, target):
    manifest = verify(directory)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(directory, target)
    src = target / 'assets/atlas-scoped.css'
    previous = manifest['files']['assets/atlas-scoped.css']
    assert previous == digest(src.read_bytes())
    newcss = src.read_bytes() + b'\n' + patch.read_bytes()
    src.write_bytes(newcss)
    sha = digest(newcss)
    php = target / 'fv-ex2-apollo-r224.php'
    content = php.read_text()
    assert content.count(previous) == 1, 'CSS pin must occur exactly once'
    content = content.replace(previous, sha).replace("'8e7fef7fa158'", f"'{sha[:12]}'")
    php.write_text(content)
    manifest['files']['assets/atlas-scoped.css'] = sha
    manifest['files']['fv-ex2-apollo-r224.php'] = digest(php.read_bytes())
    manifest['r234_parent_manifest_sha256'] = PARENT
    manifest['r234_change'] = 'Noninline navigation and expanded evidence source-action targets >=44px'
    manifest['release'] = 'R234_STAGING_HOLD'
    manifest['axe_core'] = 'NOT_EXECUTED'
    jsonwrite(target / 'manifest.json', manifest)
    return digest((target / 'manifest.json').read_bytes())


def accept(directory, out):
    out.mkdir(parents=True, exist_ok=True)
    html = (directory / 'templates/atlas-fragment.html').read_text()
    css = (directory / 'assets/atlas-scoped.css').read_text()
    doc = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>' + css + '</style></head><body>' + html + '</body></html>'
    selector = ','.join('.fv-apollo-atlas ' + x for x in SELECTORS)
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        for width in (*WIDTHS, 256):
            for js in ((True, False) if width != 256 else (False,)):
                context = browser.new_context(viewport={'width': width, 'height': 900}, java_script_enabled=js,
                    is_mobile=width <= 390, has_touch=width <= 390, reduced_motion='reduce')
                page = context.new_page()
                requests = []
                page.on('request', lambda req: requests.append(req.url))
                page.set_content(doc, wait_until='load')
                page.evaluate("() => document.querySelectorAll('details').forEach(d => d.open=true)")
                audit = page.evaluate('''sel=>{
                    const links=[...document.querySelectorAll(sel)];
                    const targets=links.filter(e=>e.getClientRects().length).map(e=>{
                        const r=e.getBoundingClientRect();return {h:r.height,w:r.width,href:e.getAttribute('href')}
                    });
                    const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
                    return {targets:targets.length,under44:targets.filter(e=>e.h<43.99).length,
                      min_height:Math.round(Math.min(...targets.map(e=>e.h))*100)/100,
                      overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
                      duplicate_ids:ids.length-new Set(ids).size,
                      sources:document.querySelectorAll('[data-source-record]').length,
                      disclosure_count:document.querySelectorAll('details>summary').length,
                      cta:document.querySelectorAll('a[href="''' + URL + '''"]').length,
                      scripts:document.querySelectorAll('script').length,
                      geocoordinates:document.querySelectorAll('[data-lat],[data-lng],[data-latitude],[data-longitude]').length,
                      bad_fragments:[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.getElementById(a.hash.slice(1))).length
                    }
                }''', selector)
                assert not requests and audit['targets'] == 27 and audit['under44'] == 0, audit
                assert audit['overflow'] <= 1 and audit['duplicate_ids'] == 0 and audit['bad_fragments'] == 0, audit
                assert audit['sources'] == 4 and audit['disclosure_count'] >= 10, audit
                assert audit['cta'] == 1 and audit['scripts'] == 0 and audit['geocoordinates'] == 0
                # Real native keyboard interaction even when JS is disabled.
                page.locator('details>summary').first.focus()
                initial = page.locator('details').first.evaluate('(e)=>e.open')
                page.keyboard.press('Enter')
                assert page.locator('details').first.evaluate('(e)=>e.open') != initial
                if width <= 390:
                    page.locator('details>summary').first.tap()
                    assert page.locator('details').first.evaluate('(e)=>e.open') == initial
                page.set_content(doc, wait_until='load')
                image = out / f'{width}-{"js" if js else "nojs"}.png'
                page.screenshot(path=str(image), full_page=True, animations='disabled')
                results.append({'width': width, 'js': js, 'audit': audit,
                                'screenshot_sha256': digest(image.read_bytes())})
                context.close()
        version = browser.version
        browser.close()
    receipt = {'scope': 'SHA-pinned R228 generated Atlas + R234 CSS; offline Chromium only',
        'parent_manifest_sha256': PARENT, 'browser': version, 'contexts': results,
        'not_tested': ['genuine axe-core', 'screen readers', 'installed WordPress',
                       'real browser UI zoom', 'hosted CI', 'field LCP/CLS', 'media rights']}
    jsonwrite(out / 'receipt.json', receipt)
    return digest((out / 'receipt.json').read_bytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dist', type=Path, required=True)
    ap.add_argument('--patch', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--qa', type=Path, required=True)
    args = ap.parse_args()
    manifest = build(args.dist, args.patch, args.out)
    receipt = accept(args.out, args.qa)
    print(json.dumps({'status': 'LOCAL_PASS', 'generated_manifest_sha256': manifest,
                      'qa_receipt_sha256': receipt, 'contexts': 11}, indent=2))


if __name__ == '__main__':
    main()
