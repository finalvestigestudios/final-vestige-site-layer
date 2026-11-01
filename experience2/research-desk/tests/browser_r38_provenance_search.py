"""R38 browser gate for the ORIGINAL six-record NASA Research Desk template.

Runs only on local source; does not navigate to production or fetch images.
Chromium page.set_content is a DOM/CSS/JS test, NOT an HTTP CSP, hosted LCP
or CLS measurement. Synthetic --fixture runs are never release acceptance.

    python tests/browser_r38_source_custody.py --output /tmp/r38-qa
    python tests/browser_r38_source_custody.py --fixture /tmp/synthetic.html \
        --css /tmp/synthetic.css --js /tmp/synthetic.js --output /tmp/r38-synthetic
"""
import argparse
import hashlib
import json
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def ensure(value, reason):
    if not value:
        raise AssertionError(reason)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fixture', type=pathlib.Path)
    ap.add_argument('--css', type=pathlib.Path)
    ap.add_argument('--js', type=pathlib.Path)
    ap.add_argument('--output', type=pathlib.Path, required=True)
    ap.add_argument('--axe', type=pathlib.Path, help='Preinstalled pinned axe-core; never runtime-fetched')
    options = ap.parse_args()
    source = options.fixture or ROOT / 'templates/ledger.html'
    stylesheet = options.css or ROOT / 'assets/source-ledger.css'
    script = options.js or ROOT / 'assets/source-ledger.js'
    for p in (source, stylesheet, script):
        ensure(p.is_file(), 'Missing source: ' + str(p))
    if options.axe:
        ensure(options.axe.is_file(), 'Pinned axe-core file missing')
    options.output.mkdir(parents=True, exist_ok=True)
    raw = source.read_text(encoding='utf8')
    css = stylesheet.read_text(encoding='utf8')
    js = script.read_text(encoding='utf8')
    mode = 'SYNTHETIC_FIXTURE_NOT_RELEASE' if options.fixture else 'ORIGINAL_NASA_TEMPLATE'
    ensure(raw.count('data-fvx-photo-record=') == 6, 'Six custody panels required')
    ensure(raw.count('data-fvx-chrono-link') == 6, 'Six source chronology links required')
    ensure(raw.count('data-fvx-clear') == 1, 'Accessible clear-search action required')
    document = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>Apollo 1 R38 source custody, staging only</title><style>'
                + css + '</style></head><body style="margin:0">' + raw + '</body></html>')
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium',
                                     headless=True, args=['--no-sandbox'])
        version = browser.version
        for enabled in (False, True):
            for width in WIDTHS:
                ctx = browser.new_context(viewport={'width': width, 'height': 900},
                                          is_mobile=width < 500, has_touch=width < 500,
                                          java_script_enabled=enabled, reduced_motion='reduce')
                page = ctx.new_page()
                page.set_content(document, wait_until='load')
                if enabled:
                    page.add_script_tag(content=js)
                prefix = f'{width} JS={enabled}: '
                ensure(page.locator('[data-fvx-record]').count() == 6, prefix+'lost records')
                ensure(page.locator('[data-fvx-photo-record]').count() == 6, prefix+'lost custody')
                ensure(page.locator('[data-fvx-chrono-link]').count() == 6, prefix+'lost chronology')
                ensure(page.locator('[data-fvx-record]:visible').count() == 6, prefix+'hidden on load')
                ensure(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'),
                       prefix+'horizontal overflow')
                ensure(page.evaluate("""() => {
                    const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
                    return ids.length === new Set(ids).size;
                }"""), prefix+'duplicate IDs')
                ensure(page.evaluate("""() => [...document.querySelectorAll('[data-fvx-chrono-link]')]
                    .every(a => document.getElementById(a.hash.slice(1)))"""),
                    prefix+'broken chronology anchor')
                detail = page.locator('[data-fvx-photo-record="03"]')
                detail.locator('summary').focus()
                detail.locator('summary').press('Enter')
                ensure(detail.get_attribute('open') is not None, prefix+'keyboard detail not opened')
                if enabled:
                    search = page.locator('input[data-fvx-search]')
                    ensure(search.is_visible(), prefix+'missing search enhancement')
                    clear = page.locator('button[data-fvx-clear]')
                    ensure(clear.is_hidden(), prefix+'clear visible without query')
                    search.fill('kim shiflett')
                    ensure(page.locator('[data-fvx-record]:visible').count() == 2,
                           prefix+'photo credits missing from provenance search')
                    ensure(clear.is_visible(), prefix+'clear not available')
                    (clear.tap() if width < 500 else clear.click())
                    ensure(search.input_value()=='' and
                           page.locator('[data-fvx-record]:visible').count()==6,
                           prefix+'clear failed to restore records')
                    ensure(page.evaluate("document.activeElement.matches('input[data-fvx-search]')"),
                           prefix+'clear did not restore keyboard focus')
                    search.fill('zz-unmatched-record')
                    search.press('Escape')
                    ensure(search.input_value()=='' and
                           page.locator('[data-fvx-record]:visible').count()==6,
                           prefix+'Escape did not clear search')
                    search.fill('zz-unmatched-record')
                    ensure(page.locator('[data-fvx-record]:visible').count() == 0,
                           prefix+'search did not filter')
                    (page.locator('[data-fvx-chrono-link]').first.tap() if width < 500 else
                     page.locator('[data-fvx-chrono-link]').first.click())
                    ensure(search.input_value() == '', prefix+'chronology failed to clear search')
                    ensure(page.locator('[data-fvx-record]:visible').count() == 6,
                           prefix+'chronology failed to restore hidden evidence')
                    # Malformed search metadata must NEVER leave the evidence inaccessible.
                    page.locator('[data-fvx-record]').nth(2).evaluate(
                        "el => el.removeAttribute('data-fvx-search')")
                    search.fill('malformed-index')
                    ensure(page.locator('[data-fvx-record]:visible').count() == 6,
                           prefix+'malformed search did not fail open')
                    ensure(not page.locator('[data-fvx-tools]').is_visible(),
                           prefix+'failed enhancement not disabled')
                else:
                    ensure(not page.locator('[data-fvx-tools]').is_visible(),
                           prefix+'no-JS controls unexpectedly visible')
                    ensure(page.locator('button[data-fvx-clear]').is_hidden(),
                           prefix+'no-JS clear unexpectedly visible')
                    (page.locator('[data-fvx-chrono-link]').first.tap() if width < 500 else
                     page.locator('[data-fvx-chrono-link]').first.click())
                    ensure(page.locator('[data-fvx-record]:visible').count() == 6,
                           prefix+'no-JS chronology lost evidence')
                if options.axe:
                    page.add_script_tag(content=options.axe.read_text(encoding='utf8'))
                    violations = page.evaluate("""async () => {
                        const r = await axe.run(document.querySelector('[data-fvx-ledger]'),
                          {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
                        return r.violations.map(v => ({id:v.id,impact:v.impact,nodes:v.nodes.length}));
                    }""")
                    ensure(not violations, prefix+'axe: '+repr(violations))
                name = f'r38-source-{width}-{"js" if enabled else "nojs"}.png'
                screenshot = options.output / name
                # Normalize touch hover and focused elements before immutable screenshot capture.
                page.evaluate('document.activeElement && document.activeElement.blur()')
                page.mouse.move(1,1)
                if width < 500 and enabled:
                    page.locator('h1').tap() # reset persistent mobile :hover state
                page.evaluate('window.scrollTo(0,0)')
                page.screenshot(path=str(screenshot), full_page=True, animations='disabled')
                results.append({'width':width,'javascript':enabled,'passed':True,
                                'screenshot':name,'sha256':digest(screenshot)})
                ctx.close()
        browser.close()
    receipt = {
        'schema':'fv.ex2.apollo.r38.browser.v1','source_kind':mode,
        'chromium':version,'scenarios':results,
        'axe':'EXECUTED' if options.axe else 'BLOCKED_NO_PINNED_AXE_CORE',
        'http_csp':'NOT_MEASURED_SET_CONTENT','hosted_lcp':'NOT_MEASURED',
        'hosted_cls':'NOT_MEASURED','hosted_inp':'NOT_MEASURED',
        'sha256':{'template':digest(source),'css':digest(stylesheet),'js':digest(script)}
    }
    (options.output/'r38-browser-receipt.json').write_text(
        json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(f'R38 {len(results)}/14 Chromium scenarios PASS ({mode}); axe: {receipt["axe"]}')

if __name__ == '__main__':
    main()
