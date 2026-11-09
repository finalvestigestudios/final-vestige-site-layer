#!/usr/bin/env python3
"""R239 staging-only acceptance: browser-rendered output of the exact PHP shortcode.

This bridges PHP adapter -> rendered fragment -> real Chromium DOM. It is NOT
installed WordPress, axe-core, a screen reader, live HTTP, or field CWV.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS = (320, 390, 768, 1440, 1920)
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
NASA = ('Apollo 204 Review Board', 'S66-58038', 'S67-15717', 'S67-21294')
EXPECTED_R238_MANIFEST = 'f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(root):
    assert sha(root / 'manifest.json') == EXPECTED_R238_MANIFEST, 'unapproved manifest'
    manifest = json.loads((root / 'manifest.json').read_text())
    for file, digest in manifest['files'].items():
        assert sha(root / file) == digest, 'source drift: ' + file
    assert manifest['status'] == 'STAGING_HOLD' and manifest['not_live'] is True
    return manifest


def php_run(root, mode):
    cmd = ['php', str(root / 'wp-render-shim-r224.php'),
           str((root / 'fv-ex2-apollo-r224.php').resolve()), mode]
    p = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=12)
    return json.loads(p.stdout)


def semantic_audit(html):
    # Important: this is the PHP-produced string, not a separately copied HTML mock.
    assert html.count('class="cta"') == 1
    assert html.count('href="'+FREE+'"') == 1
    assert all(t in html for t in NASA)
    assert html.count('data-fv-plate-source=') == 4
    assert '<script' not in html and '<iframe' not in html
    assert not re.search(r'\bdata-(?:latitude|longitude)\b', html)
    assert not re.search(r'payhip|awin1|sponsored|confirmed.order', html, re.I)


def browser_test(html, css, out):
    document = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<style>'+css+'</style></head><body>'+html+'</body></html>')
    out.mkdir(parents=True, exist_ok=False)
    results = []
    measurements = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium',
                                     headless=True, args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (False, True):
                context = browser.new_context(viewport={'width':width,'height':900},
                    java_script_enabled=js, is_mobile=width <= 390, has_touch=width <= 390,
                    reduced_motion='reduce', forced_colors='active' if width==768 else 'none')
                page = context.new_page()
                external = []
                page.on('request', lambda request: external.append(request.url))
                page.set_content(document, wait_until='load')
                assert not external, (width, external)
                assert page.locator('a.cta').count() == 1
                assert page.locator('a.cta').get_attribute('href') == FREE
                assert page.locator('details.fv-apollo-source-drawer').count() == 1
                assert page.locator('[data-fv-plate-source]').count() == 4
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
                assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
                assert page.evaluate('document.querySelectorAll("script,iframe,form").length') == 0
                assert page.locator('section#fv-apollo-chronology time[datetime]').count() >= 5
                # Verify real keyboard focus movement, not only CSS source text.
                page.keyboard.press('Tab')
                skip = page.evaluate('''() => {const e=document.activeElement,r=e.getBoundingClientRect(),s=getComputedStyle(e);
                  return {href:e.getAttribute('href'),h:r.height,w:r.width,outline:s.outlineStyle,visible:e.matches(':focus-visible')}}''')
                assert skip['href'] == '#fv-apollo-main' and skip['h'] >= 44 and skip['w'] >= 44, skip
                assert skip['visible'] and skip['outline'] != 'none', skip
                page.keyboard.press('Enter')
                assert page.evaluate('document.activeElement.id') == 'fv-apollo-main'
                drawer = page.locator('details.fv-apollo-source-drawer')
                drawer.locator('summary').focus()
                page.keyboard.press('Enter')
                assert drawer.evaluate('(node)=>node.open')
                if width <= 390:
                    page.keyboard.press('Enter')
                    drawer.locator('summary').tap()
                    assert drawer.evaluate('(node)=>node.open')
                # Preserve CSS effects but remove ephemeral focus/hover before capture.
                page2 = context.new_page()
                page2.set_content(document, wait_until='load')
                page2.mouse.move(0,0)
                page2.wait_for_timeout(100)
                filename=f'{width}-{"js" if js else "nojs"}.png'
                page2.screenshot(path=str(out/filename), full_page=True, animations='disabled')
                # Synthetic performance values are diagnostics only, never production thresholds.
                if js:
                    perf = page2.evaluate('''async () => {
                      let l=[],s=[];
                      new PerformanceObserver(x=>x.getEntries().forEach(e=>l.push(e.startTime))).observe({type:'largest-contentful-paint',buffered:true});
                      new PerformanceObserver(x=>x.getEntries().forEach(e=>{if(!e.hadRecentInput)s.push(e.value)})).observe({type:'layout-shift',buffered:true});
                      await new Promise(resolve=>setTimeout(resolve,400));
                      return {lcp_ms:l.length?Math.round(Math.max(...l)):null,cls:s.reduce((a,b)=>a+b,0)};
                    }''')
                    measurements.append({'width':width, **perf})
                results.append({'width':width,'js':js,'screenshot_sha256':sha(out/filename),
                                'keyboard_skip_px':round(skip['h'],2),'source_drawer':True})
                context.close()
        browser_version=browser.version
        browser.close()
    return {'chromium':browser_version,'contexts':len(results),'results':results}, measurements


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--atlas',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    args=p.parse_args()
    root=args.atlas.resolve()
    assert not args.out.exists(), 'refuse to overwrite QA receipts'
    manifest=verify(root)
    normal=php_run(root,'normal')
    printed=php_run(root,'printed')
    late=php_run(root,'late')
    tamper=php_run(root,'tamper-helper')
    assert normal['css']=='enqueued' and not normal['fallback'] and not normal['js']
    assert printed['css']=='done' and not printed['fallback']
    assert printed['html']==normal['html']
    assert late['fallback'] and FREE in late['html'] and late['css']=='absent'
    assert tamper=={'valid_original':True,'tamper_rejected':True}
    semantic_audit(normal['html'])
    assert normal['html']==(root/'templates/atlas-fragment.html').read_text(), 'rendered-vs-template drift'
    browser,perf=browser_test(normal['html'],(root/'assets/atlas-scoped.css').read_text(),args.out)
    receipt={'run':'R239','source_manifest_sha256':sha(root/'manifest.json'),
        'adapter_sha256':sha(root/'fv-ex2-apollo-r224.php'),
        'php_shortcode':'PASS: exact protected fragment, early-style, already-printed style, late fail-open, tamper reject',
        'browser':browser,'axe_core':'NOT_EXECUTED','installed_wordpress':'NOT_TESTED',
        'real_http_navigation':'NOT_TESTED','screen_reader':'NOT_TESTED','field_cwv':'NOT_TESTED',
        'rights':'NOT_CLEARED_FOR_COMMERCIAL_USE','release':'STAGING_HOLD',
        'paid_orders':'NOT_VERIFIED'}
    (args.out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    (args.out/'fixture_performance_not_field.json').write_text(json.dumps(perf,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'contexts':browser['contexts'],'receipt_sha256':sha(args.out/'receipt.json'),
                      'manifest_sha256':sha(root/'manifest.json'),'php':'PASS','release':'STAGING_HOLD'}))


if __name__=='__main__':
    main()
