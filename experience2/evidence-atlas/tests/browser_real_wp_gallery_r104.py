#!/usr/bin/env python3
"""R104 actual WordPress HTTP acceptance for R103 Source Gallery interactions.

Deliberate boundary: only disposable WordPress at 127.0.0.1:8955. No
production/hosted WordPress contact, content writes, or media downloads.
Ordinary browser contexts honor CSP; axe uses a separate diagnostic context.
Performance observations are lab samples, not field Core Web Vitals.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote, urlparse

from playwright.sync_api import sync_playwright
from qa_receipt_r105 import EvidenceJournal

WIDTHS = (320, 390, 768, 1440, 1920)
VIEW = 'R97_SOURCE_GALLERY.html'


def require(ok, reason):
    if not ok:
        raise AssertionError(reason)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_base(base):
    parsed = urlparse(base)
    require(parsed.scheme == 'http'
            and parsed.netloc in ('127.0.0.1:8955', 'localhost:8955')
            and parsed.path in ('', '/')
            and not parsed.query and not parsed.fragment
            and not parsed.username and not parsed.password,
            'R104: disposable localhost WordPress only')
    return base.rstrip('/') + '/'


def run(base, out, axe_path, user, password):
    base = verify_base(base)
    require(axe_path.is_file(), 'R104: local axe bundle required')
    out.mkdir(parents=True, exist_ok=True)
    url = base + '?fv_apollo_r99=' + quote(VIEW)
    receipt = {
        'schema': 'fv.apollo.r104.real-wp-gallery.v1',
        'release': 'STAGING_HOLD',
        'real_wordpress_core_http': True,
        'hosted_wordpress_or_assembler_verified': False,
        'production_core_web_vitals': False,
        'r103_interaction_cases': [],
        'axe': [],
        'performance_lab_samples': [],
        'screenshots_sha256': {},
        'pdf_sha256': {},
        'constraints': [
            'six NASA records; zero photographic-use clearances',
            'no photographs, geographic pins or inferred source connections',
            'read-only temporary WordPress; no production or content writes',
        ],
    }
    journal = EvidenceJournal(out)
    journal.checkpoint(receipt, 'started')
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
        login_ctx = browser.new_context()
        login = login_ctx.new_page()
        response = login.goto(base + 'wp-login.php', wait_until='domcontentloaded')
        require(response is not None and response.status == 200
                and login.locator('#user_login').count() == 1,
                'R104: genuine WordPress login required')
        login.locator('#user_login').fill(user)
        login.locator('#user_pass').fill(password)
        login.locator('#wp-submit').click()
        login.wait_for_url(re.compile(r'.*/wp-admin/.*'), timeout=20000)
        storage = login_ctx.storage_state()
        login_ctx.close()

        for width in WIDTHS:
            for js in (False, True):
                journal.checkpoint(receipt, f'browser:{width}:js{int(js)}')
                ctx = browser.new_context(
                    viewport={'width': width, 'height': 900},
                    storage_state=storage,
                    java_script_enabled=js,
                    is_mobile=width <= 390,
                    has_touch=width <= 390,
                    reduced_motion='reduce',
                    forced_colors='active' if width == 320 else 'none',
                )
                page = ctx.new_page()
                remote = []
                errors = []
                page.on('request', lambda request: remote.append(request.url)
                        if urlparse(request.url).netloc not in
                        ('127.0.0.1:8955', 'localhost:8955') else None)
                page.on('pageerror', lambda error: errors.append(str(error)[:180]))
                res = page.goto(url, wait_until='load')
                require(res is not None and res.status == 200,
                        f'R104: WordPress gallery HTTP {width}/js{js}')
                headers = {k.lower(): v for k, v in res.headers.items()}
                require('no-store' in headers.get('cache-control', '')
                        and 'noindex' in headers.get('x-robots-tag', '')
                        and 'frame-ancestors' in headers.get('content-security-policy', ''),
                        'R104: private hold cache/CSP/robots headers absent')
                require(page.locator('[data-card]').count() == 6
                        and page.locator('a[href^="https://www.nasa.gov/image-detail/"]').count() == 6,
                        'R104: six source records/NASA links required')
                require(page.locator('img,[data-lat],[data-lon],[data-geo-edge]').count() == 0,
                        'R104: images or inferred geography added')
                require(page.locator('main').count() == 1
                        and 'STAGING HOLD' in page.locator('body').inner_text(),
                        'R104: source meaning or hold flag absent')
                require(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'),
                        f'R104: horizontal document overflow {width}/js{js}')
                if js:
                    require(page.locator('[data-compare-controls]:visible').count() == 7,
                            'R104: source-selection controls were not progressively enhanced')
                    require(page.locator('[data-jump-compare]:visible').count() == 0,
                            'R104: hidden comparison jump visible prematurely')
                    require(page.locator('#comparison').is_hidden(),
                            'R104: comparison initially visible')
                    for n in ('01', '02'):
                        box = page.locator('#compare-' + n)
                        (box.tap() if width <= 390 else box.check())
                    require(page.locator('[data-jump-compare]:visible').count() == 6
                            and page.locator('#comparison').is_visible()
                            and page.locator('[data-heading]').all_text_contents() ==
                                ['Source 01', 'Source 02'],
                            'R104: two-source comparison or jump failed')
                    require(all(v.strip() for v in page.locator('[data-value]').all_text_contents()),
                            'R104: comparison custody values missing')
                    # Native fragment navigation must work on real WordPress HTTP
                    # with CSP enforced, not merely through an inline DOM harness.
                    jump = page.locator('[data-jump-compare]:visible').first
                    (jump.tap() if width <= 390 else jump.click())
                    require(page.evaluate("location.hash === '#comparison'"),
                            'R104: native comparison fragment navigation failed')
                    region = page.locator('.compare-viewport')
                    require(region.count() == 1
                            and region.get_attribute('role') == 'region'
                            and region.get_attribute('tabindex') == '0',
                            'R104: comparison region keyboard contract changed')
                    if width <= 390:
                        require(region.evaluate('(el) => el.scrollWidth > el.clientWidth'),
                                'R104: mobile region cannot scroll horizontally')
                        region.focus()
                        page.keyboard.press('ArrowRight')
                        page.wait_for_timeout(350)
                        require(region.evaluate('(el) => el.scrollLeft > 0'),
                                'R104: mobile comparison lacks keyboard horizontal scroll')
                    if width in (390, 1440) or width == 320:
                        shot = out / f'R104_REAL_WP_SELECTED_{width}.png'
                        page.screenshot(path=str(shot), full_page=True, animations='disabled')
                        receipt['screenshots_sha256'][shot.name] = digest(shot)
                    third = page.locator('#compare-03')
                    (third.tap() if width <= 390 else third.click())
                    require(not third.is_checked()
                            and 'Only two records' in page.locator('#compare-status').inner_text(),
                            'R104: third-source limit not announced')
                    reset = page.locator('#compare-reset')
                    (reset.tap() if width <= 390 else reset.click())
                    require(page.locator('#comparison').is_hidden()
                            and page.locator('[data-select]:checked').count() == 0
                            and page.locator('[data-jump-compare]:visible').count() == 0,
                            'R104: comparison reset did not restore source state')
                    require(page.evaluate("document.activeElement?.id === 'compare-01'"),
                            'R104: reset did not restore keyboard focus')
                else:
                    require(page.locator('[data-compare-controls]:visible').count() == 0
                            and page.locator('[data-jump-compare]:visible').count() == 0
                            and page.locator('[data-card]:visible').count() == 6,
                            'R104: no-JS must retain all source evidence without dead controls')
                    if width == 390:
                        shot = out / 'R104_REAL_WP_NOJS_390.png'
                        page.screenshot(path=str(shot), full_page=True, animations='disabled')
                        receipt['screenshots_sha256'][shot.name] = digest(shot)
                require(not remote and not errors,
                        f'R104: unexpected remote requests or JavaScript errors: {remote} {errors}')
                receipt['r103_interaction_cases'].append({
                    'width': width, 'javascript_enabled': js,
                    'reduced_motion': True, 'forced_colors': width == 320,
                    'actual_wordpress_http': True, 'passed': True,
                })
                ctx.close()
                journal.checkpoint(receipt, f'browser-done:{width}:js{int(js)}')

        # Test the *selected* state with real HTTP, with CSP bypass restricted to
        # diagnostic axe injection. Baseline functional contexts above retain CSP.
        for width in (390, 1440):
            journal.checkpoint(receipt, f'axe:{width}')
            ctx = browser.new_context(
                viewport={'width': width, 'height': 900},
                storage_state=storage, bypass_csp=True,
                reduced_motion='reduce',
            )
            page = ctx.new_page()
            page.goto(url, wait_until='load')
            page.locator('#compare-01').check()
            page.locator('#compare-02').check()
            require(page.locator('#comparison').is_visible(),
                    'R104: selected comparison not visible during accessibility scan')
            page.add_script_tag(path=str(axe_path))
            outcome = page.evaluate('''async () => {
                const r = await axe.run(document, {
                    runOnly: { type: 'tag', values:
                        ['wcag2a','wcag2aa','wcag21aa','wcag22aa'] }
                });
                return { passes: r.passes.length, violations:
                    r.violations.map(v => ({ id: v.id, impact: v.impact,
                                            nodes: v.nodes.length })) };
            }''')
            receipt['axe'].append({'width': width, 'state': 'selected_two_sources',
                                   **outcome})
            require(not outcome['violations'],
                    f'R104: selected-state axe violations: {outcome["violations"]}')
            ctx.close()
            journal.checkpoint(receipt, f'axe-done:{width}')

        # Repeat measurements on fresh navigations so variability is visible.
        # Instrument before navigation. No production/field CWV claim is permitted.
        for width in (390, 1440):
            recorded = 0
            for trial in range(1, 4):
                journal.checkpoint(receipt, f'performance:{width}:trial{trial}')
                ctx = browser.new_context(
                    viewport={'width': width, 'height': 900},
                    storage_state=storage, reduced_motion='reduce')
                page = ctx.new_page()
                page.add_init_script('''(() => {
                    window.__r104_perf = {lcp_ms: null, cls: 0};
                    try { new PerformanceObserver(list => {
                        for (const entry of list.getEntries())
                            window.__r104_perf.lcp_ms = entry.startTime;
                    }).observe({type:'largest-contentful-paint', buffered:true}); } catch(e) {}
                    try { new PerformanceObserver(list => {
                        for (const entry of list.getEntries())
                            if (!entry.hadRecentInput)
                                window.__r104_perf.cls += entry.value;
                    }).observe({type:'layout-shift', buffered:true}); } catch(e) {}
                })();''')
                response = page.goto(url, wait_until='load')
                require(response is not None and response.status == 200,
                        'R104: repeated local WordPress navigation failed')
                page.wait_for_timeout(300)
                perf = page.evaluate('window.__r104_perf')
                receipt['performance_lab_samples'].append({
                    'width': width, 'trial': trial,
                    'lcp_ms': perf['lcp_ms'], 'cls': perf['cls'],
                    'scope': 'disposable WordPress core, not Assembler/production',
                })
                # Persist the raw lab measurement *before* the budget assertion.
                # Even a 2.5s LCP failure leaves a reproducible partial receipt.
                journal.checkpoint(receipt, f'performance-observed:{width}:trial{trial}')
                require(perf['cls'] is not None and perf['cls'] <= 0.1,
                        f'R104: CLS budget exceeded on {width} trial {trial}')
                if perf['lcp_ms'] is not None:
                    recorded += 1
                    require(perf['lcp_ms'] <= 2500,
                            f'R104: isolated WP LCP exceeded unchanged 2500ms gate at {width} trial {trial}')
                if width == 1440 and trial == 1:
                    pdf = out / 'R104_REAL_WP_PRINT.pdf'
                    page.pdf(path=str(pdf), format='A4', print_background=True)
                    receipt['pdf_sha256'][pdf.name] = digest(pdf)
                    import fitz
                    with fitz.open(pdf) as doc:
                        text = ''.join(p.get_text() for p in doc)
                        collapsed = re.sub(r'\s+', '', text.lower())
                        for marker in ('apollo-1-crew-honored',
                                       'amf-s67-15717',
                                       'amf-s66-58038',
                                       'amf-ksc-20170124',
                                       'amf-s67-21294'):
                            require(marker in collapsed,
                                    'R104: source omitted from research PDF: ' + marker)
                        require(text.count('INDIVIDUAL REVIEW REQUIRED') >= 6,
                                'R104: print rights restrictions missing')
                        receipt['printed_pages'] = len(doc)
                ctx.close()
            require(recorded > 0,
                    f'R104: no LCP observations available at viewport {width}')
        browser.close()

    require(len(receipt['r103_interaction_cases']) == 10
            and len(receipt['axe']) == 2
            and len(receipt['performance_lab_samples']) == 6,
            'R104: incomplete acceptance matrix')
    receipt['screenshots_sha256'] = dict(sorted(receipt['screenshots_sha256'].items()))
    # The secondary human-readable QA report is emitted only AFTER the strict
    # R106 journal gate accepts every viewport, scan, LCP/CLS and artifact.
    # Failure leaves only the sanitized, explicitly incomplete progress journal.
    journal.complete(receipt)
    receipt['r106_isolated_core_contract'] = 'verified; production/hosted release HOLD'
    (out / 'R104_REAL_WP_GALLERY_QA.json').write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='http://127.0.0.1:8955/')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--axe', type=Path, required=True)
    parser.add_argument('--user', required=True)
    parser.add_argument('--password', required=True)
    args = parser.parse_args()
    try:
        result = run(args.base, args.out, args.axe, args.user, args.password)
    except Exception as exc:
        # Preserve only the exception type in the journal. A raw Playwright
        # traceback may contain private HTTP URLs, page HTML or login fields;
        # never echo it into public CI logs. Last checkpoint gives triage context.
        EvidenceJournal(args.out).fail(type(exc).__name__)
        raise SystemExit('R106_WORDPRESS_QA_FAILED: inspect sanitized R105_QA_PROGRESS.json (STAGING HOLD)') from None
    print(json.dumps({
        'schema': result['schema'], 'cases': len(result['r103_interaction_cases']),
        'axe_scans': len(result['axe']),
        'lab_performance_samples': len(result['performance_lab_samples']),
        'screenshots': result['screenshots_sha256'],
        'pdf': result['pdf_sha256'],
        'release': result['release'],
    }, sort_keys=True))
