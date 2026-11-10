#!/usr/bin/env python3
"""R259: source-matched Apollo browser acceptance, offline only; never a WP/field pass.

Use the sealed R238 fixture from the founder's staging archive. No third-party requests,
merchant destinations, new analytics scripts, credentials, or live changes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from playwright.sync_api import sync_playwright

SEAL = 'f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
WIDTHS = (320, 390, 768, 1440, 1920)
OVERLAYS = ('apollo-r253/atlas-source-actions.css', 'apollo-r254/provenance-tap-continuity.css',
            'apollo-r255/evidence-path-touch.css', 'apollo-r256/print-custody.css',
            'apollo-r257/print-full-evidence.css')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def main(a):
    atlas = a.atlas.resolve()
    require(digest((atlas / 'manifest.json').read_bytes()) == SEAL, 'sealed R238 manifest mismatch')
    for path, expected in json.loads((atlas / 'manifest.json').read_text())['files'].items():
        require(digest((atlas / path).read_bytes()) == expected, 'sealed R238 file drift: '+path)
    shim = subprocess.run(['php', str(atlas / 'wp-render-shim-r224.php'),
                           str(atlas / 'fv-ex2-apollo-r224.php'), 'normal'],
                          capture_output=True, text=True, check=True)
    html = json.loads(shim.stdout)['html']
    require(html == (atlas / 'templates/atlas-fragment.html').read_text(), 'original PHP output drift')
    css_files = [atlas / 'assets/atlas-scoped.css'] + [a.overlays / p for p in OVERLAYS]
    css = '\n'.join(f.read_text() for f in css_files)
    require(not any(x in css.lower() for x in ('@import', 'url(', 'javascript:')), 'unreviewed CSS dependency')
    require(html.count('href="'+FREE+'"') == 1, 'original free-CTA changed')
    doc = '<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>' + css + '</style></head><body>' + html + '</body></html>'
    axe = None
    if a.axe_bundle:
        require(bool(a.axe_sha256) and len(a.axe_sha256)==64, 'axe must have a 64-character preverified SHA-256')
        require(digest(a.axe_bundle.read_bytes()) == a.axe_sha256, 'axe third-party bundle hash mismatch')
        axe = a.axe_bundle.read_text()
        require('axe.version' in axe or 'axe-core' in axe or 'axeCore' in axe, 'axe bundle does not appear to be axe-core')
    if a.require_axe:
        require(axe is not None, 'release axe gate unavailable: supply a provenance-verified axe-core bundle')
    a.out.mkdir(parents=True, exist_ok=True)
    receipt = {'source_manifest_sha256': SEAL, 'php_html_sha256': digest(html.encode()),
               'css_sha256': digest(css.encode()), 'axe_status': 'executed' if axe else 'NOT EXECUTED',
               'contexts': [], 'screenshot_sha256': {}, 'environment': 'local Chromium set_content; not installed WordPress, HTTP/CSP, or field CWV'}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=a.chromium, args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (False, True):
                context = browser.new_context(viewport={'width':width,'height':900},
                                              java_script_enabled=js, is_mobile=width<=390,
                                              has_touch=width<=390, reduced_motion='reduce')
                page = context.new_page()
                requests = []
                page.on('request', lambda request: requests.append(request.url))
                page.set_content(doc)
                require(not requests, 'unexpected network request '+str(requests))
                require(page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'), 'horizontal overflow '+str(width))
                require(page.locator('article.fv-apollo-atlas').count() == 1, 'missing original article')
                require(page.locator('h1').count() == 1 and page.locator('details').count() == 13, 'heading/disclosure drift')
                require(page.locator('a[href="'+FREE+'"]').count() == 1, 'free next action lost')
                require(page.locator('[data-fv-plate-source]').count() == 4, 'NASA source plates drift')
                require(page.locator('a[href^="https://www.nasa.gov/"]').count() == 55, 'NASA source link drift')
                require(page.locator('a[href^="#"]').count() == 31, 'local navigation drift')
                targets = page.evaluate('''() => Array.from(document.querySelectorAll('.fv-apollo-atlas a, .fv-apollo-atlas summary')).filter(el => {
                    let r=el.getBoundingClientRect(), s=getComputedStyle(el);
                    return r.width>0 && r.height>0 && s.visibility!=='hidden' && !el.closest('details:not([open]) :not(summary)');
                  }).map(el => ({text:el.textContent.trim().slice(0,35),h:el.getBoundingClientRect().height,w:el.getBoundingClientRect().width}))''')
                small = [t for t in targets if t['h']<44 or t['w']<44]
                require(not small, 'visible interactive target under 44px '+str(small[:3]))
                summary = page.locator('#fv-apollo-source-drawer > summary')
                require(not page.locator('#fv-apollo-source-drawer').evaluate('(d)=>d.open'), 'source drawer must start closed')
                summary.focus()
                summary.press('Enter')
                require(page.locator('#fv-apollo-source-drawer').evaluate('(d)=>d.open'), 'Enter cannot expand SourceDrawer')
                require(page.locator('[data-fv-plate-source]:visible').count() == 4, 'opened drawer hides source records')
                summary.press('Space')
                require(not page.locator('#fv-apollo-source-drawer').evaluate('(d)=>d.open'), 'Space cannot collapse SourceDrawer')
                if width <= 390:
                    summary.tap()
                    require(page.locator('#fv-apollo-source-drawer').evaluate('(d)=>d.open'), 'mobile touch cannot open drawer')
                    summary.tap()
                page.evaluate('document.querySelectorAll("details").forEach(d=>d.open=true)')
                expanded = page.evaluate('''() => [...document.querySelectorAll('.fv-apollo-atlas a, .fv-apollo-atlas summary')]
                  .filter(e=>{let r=e.getBoundingClientRect();return r.width>0&&r.height>0})
                  .map(e=>({w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height}))''')
                require(len(expanded) == 92 and all(t['w']>=44 and t['h']>=44 for t in expanded),
                        'expanded accessibility continuity: count='+str(len(expanded))+' min='+str(min(t['h'] for t in expanded)))
                page.evaluate('document.querySelectorAll("details").forEach(d=>d.open=false)')
                if axe is not None and js:
                    page.add_script_tag(content=axe)
                    results = page.evaluate('''async () => {
                        if (!window.axe || !axe.version || !axe.run) throw Error('genuine axe missing');
                        const r=await axe.run(document.querySelector('.fv-apollo-atlas'), {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
                        return {version:axe.version,violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))};
                    }''')
                    require(not results['violations'], 'genuine axe failures '+str(results['violations']))
                    receipt['axe_version'] = results['version']
                if width in (390,1440):
                    page.evaluate('scrollTo(0,0)')
                    screenshot = page.screenshot(full_page=False, animations='disabled')
                    name = f'{width}-hero-{int(js)}.png'
                    (a.out / name).write_bytes(screenshot)
                    receipt['screenshot_sha256'][name] = digest(screenshot)
                    summary.focus()
                    screenshot = page.screenshot(full_page=False, animations='disabled')
                    name = f'{width}-drawer-{int(js)}.png'
                    (a.out / name).write_bytes(screenshot)
                    receipt['screenshot_sha256'][name] = digest(screenshot)
                perf=page.evaluate('''() => ({lcp:performance.getEntriesByType('largest-contentful-paint').at(-1)?.startTime??null,
                                          shifts:performance.getEntriesByType('layout-shift').map(x=>({value:x.value,hadRecentInput:x.hadRecentInput}))})''')
                receipt['contexts'].append({'width':width,'js':js,'visible_target_count':len(targets),
                                            'sub_44_px_targets':len(small),'lcp_ms':perf['lcp'],
                                            'observed_cls':sum(x['value'] for x in perf['shifts'] if not x['hadRecentInput']),
                                            'passed':True})
                context.close()
        for width in (390,1440):
            ctx=browser.new_context(viewport={'width':width,'height':900},forced_colors='active',reduced_motion='reduce')
            page=ctx.new_page();page.set_content(doc)
            el=page.locator('#fv-apollo-source-drawer > summary');el.focus()
            outline=el.evaluate('(e)=>getComputedStyle(e).outlineStyle')
            require(outline not in ('none','hidden'), 'forced-colors missing keyboard outline')
            require(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'forced-colors overflow')
            receipt['contexts'].append({'width':width,'forced_colors':True,'focus_outline':outline,'passed':True})
            ctx.close()
        browser.close()
    stable={k:v for k,v in receipt.items() if k not in ('contexts','environment')}
    stable['contexts']=[{k:v for k,v in c.items() if k not in ('lcp_ms','observed_cls')} for c in receipt['contexts']]
    receipt['stable_receipt_sha256']=digest(json.dumps(stable,sort_keys=True,separators=(',',':')).encode())
    (a.out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'pass':True,'contexts':len(receipt['contexts']),'axe':receipt['axe_status'],
                      'stable_sha256':receipt['stable_receipt_sha256']},sort_keys=True))

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--atlas',type=Path,required=True)
    parser.add_argument('--overlays',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--chromium',default='/usr/bin/chromium')
    parser.add_argument('--axe-bundle',type=Path)
    parser.add_argument('--axe-sha256')
    parser.add_argument('--require-axe',action='store_true')
    main(parser.parse_args())
