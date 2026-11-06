#!/usr/bin/env python3
"""Read-only browser admission for published FV homepage and isolated clones.

No form submissions, purchases, CMS writes or deployment.
Axe is mandatory for release admission: missing axe is a BLOCK, not a pass.
Lab observations cannot certify field CWV or WP.com environment parity.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from fv_ex2_archival_transfer_gate_20261106 import audit_archival_transfers

CHAPTER_IDS = (
    'fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence', 'fv-hf-inquiry',
    'fv-hf-method-title', 'fv-hf-observer', 'fv-hf-mind-title',
)
WIDTHS = (320, 360, 390, 768, 1440, 1920)
ANALYTICS = ('analytics.ahrefs.com', 'google-analytics.com',
             'googletagmanager.com', 'stats.wp.com', 'pixel.wp.com',
             'facebook.com/tr', 'connect.facebook.net')


def inspect(page):
    """Accessible DOM and conversion-path checks; no offsite CTA clicks."""
    return page.evaluate('''(ids) => {
      const root = document.querySelector('[data-fv-home-flagship]');
      const margins = document.querySelectorAll('.fv-margin-strip__item');
      const chapters = ids.map(id => ({id, exists: !!document.getElementById(id)}));
      const html = document.documentElement;
      const hero = root && root.querySelector('.fv-hf__opening-actions');
      const actions = hero ? [...hero.querySelectorAll('a')].map(a => ({
        text: a.textContent.trim(), href: a.href, visible: !!a.getClientRects().length,
        y: Math.round(a.getBoundingClientRect().y)
      })) : [];
      const focus = [...document.querySelectorAll('a[href*="/focus/"]')].map(a => ({
        text: a.textContent.trim(), href: a.href,
        y: Math.round(a.getBoundingClientRect().y),
        visible: !!a.getClientRects().length
      }));
      const marginsInLayout = [...margins].filter(n => getComputedStyle(n).display !== 'none' &&
          getComputedStyle(n).visibility !== 'hidden').length;
      return {root: !!root, margins: margins.length, marginsInLayout, chapters,
        documentWidth: html.scrollWidth, viewportWidth: window.innerWidth,
        horizontalOverflow: html.scrollWidth > window.innerWidth + 2,
        heroActions: actions, focusLinks: focus, h1: document.querySelectorAll('h1').length,
        reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches};
    }''', list(CHAPTER_IDS))


def run_axe_all_widths(page, widths=WIDTHS):
    # Audit every layout; test doubles never establish WCAG conformance.
    receipts = {}
    for width in widths:
        page.set_viewport_size({'width': width, 'height': 844})
        page.wait_for_timeout(90)  # allow media queries / layout to settle
        try:
            response = page.evaluate('''async () => {
              if (!window.axe || typeof window.axe.run !== 'function')
                return {status:'BLOCKED_AXE_MISSING'};
              const audit = await window.axe.run(document, {runOnly:{type:'tag',values:
                ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
              return {status:audit.violations.length ? 'VIOLATIONS' : 'NO_AUTOMATED_VIOLATIONS',
                violations:audit.violations.map(v => ({id:v.id,impact:v.impact,nodes:v.nodes.length}))};
            }''')
            if not isinstance(response, dict) or response.get('status') not in (
                    'VIOLATIONS', 'NO_AUTOMATED_VIOLATIONS'):
                response = {'status': 'BLOCKED_AXE_MISSING',
                            'reason': 'axe did not provide a valid result'}
            if response['status'] == 'VIOLATIONS' and not response.get('violations'):
                response = {'status': 'BLOCKED_AXE_MISSING',
                            'reason': 'violation result without evidence'}
        except Exception as exc:
            response = {'status': 'BLOCKED_AXE_RUNTIME', 'error': type(exc).__name__}
        receipts[str(width)] = response
    passed = len(receipts) == len(widths) and all(
        item['status'] == 'NO_AUTOMATED_VIOLATIONS' for item in receipts.values())
    blocked = any(item['status'].startswith('BLOCKED') for item in receipts.values())
    return {'status': ('BLOCKED_AXE_RUNTIME' if blocked else
                       'NO_AUTOMATED_VIOLATIONS' if passed else 'VIOLATIONS'),
            'widths': receipts, 'tested_widths': list(widths),
            'all_widths_pass': passed,
            'note': 'Automated axe is not full WCAG 2.2 AA or human accessibility review.'}


def run(target, output, axe_path=None, live_readonly=False, browser_path='/usr/bin/chromium'):
    parsed = urlparse(target)
    if parsed.scheme not in ('http', 'https', 'file'):
        raise ValueError('Only http(s) and file:/// targets are accepted')
    if parsed.hostname == 'finalvestige.com' and not live_readonly:
        raise ValueError('Production requires explicit --live-readonly opt-in')
    if live_readonly and parsed.hostname != 'finalvestige.com':
        raise ValueError('--live-readonly is reserved for finalvestige.com')
    safe_target = parsed._replace(query='', fragment='', params='').geturl()
    dest = Path(output)
    dest.mkdir(parents=True, exist_ok=True)
    axe = Path(axe_path) if axe_path else None
    axe_available = bool(axe and axe.is_file())
    report = {'target': safe_target, 'mode': 'LIVE_READ_ONLY' if live_readonly else 'ISOLATED',
              'widths': {}, 'no_js': {}, 'interactions': {}, 'checks': {},
              'reduced_motion': {}, 'image_network': [], 'archival_delivery': {},
              'axe': {'status': 'NOT_RUN'}, 'lab': {}, 'release_ready': False,
              'known_limits': ['Playground is not WordPress.com Atomic',
                               'No real Jetpack signup or email submission',
                               'No native browser zoom or Safari qualification',
                               'No field Core Web Vitals or paid conversion evidence']}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=browser_path,
                          headless=True, args=['--no-sandbox'])
        try:
            context = browser.new_context(viewport={'width': 390, 'height': 844},
                                          reduced_motion='reduce', device_scale_factor=1)
            if live_readonly:
                def block_analytics(route):
                    url = route.request.url.lower()
                    if any(host in url for host in ANALYTICS) or route.request.method not in ('GET', 'HEAD'):
                        route.abort()
                    else:
                        route.continue_()
                context.route('**/*', block_analytics)
            context.add_init_script('''(() => {
              window.__fvLab = {lcp: null, cls: 0};
              try {new PerformanceObserver(list => {for(const e of list.getEntries())
                window.__fvLab.lcp = e.startTime}).observe({type:'largest-contentful-paint', buffered:true})} catch(e) {}
              try {new PerformanceObserver(list => {for(const e of list.getEntries())
                if (!e.hadRecentInput) window.__fvLab.cls += e.value}).observe({type:'layout-shift', buffered:true})} catch(e) {}
            })();''')
            page = context.new_page()
            transfers = {}
            def collect_response(response):
                if response.request.resource_type != 'image':
                    return
                image_url = urlparse(response.url)._replace(query='', fragment='', params='').geturl()
                entry = {'url': image_url, 'status': response.status,
                         'declared_bytes': response.headers.get('content-length')}
                try:
                    image_body = response.body()
                    entry['actual_body_bytes'] = len(image_body)
                    entry['sha256'] = hashlib.sha256(image_body).hexdigest()
                except Exception as err:
                    entry['error'] = type(err).__name__
                transfers[response.url] = entry
            page.on('response', collect_response)
            try:
                if parsed.scheme == 'file':
                    page.set_content(Path(parsed.path).read_text(encoding='utf-8'), wait_until='load')
                else:
                    page.goto(target, wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(500)
                for width in WIDTHS:
                    page.set_viewport_size({'width': width, 'height': 844})
                    page.wait_for_timeout(120)
                    result = inspect(page)
                    path = dest / f'homepage_{width}.png'
                    page.screenshot(path=str(path), full_page=True, animations='disabled', timeout=30000)
                    result['screenshot'] = path.name
                    result['chapter_pass'] = all(x['exists'] for x in result['chapters'])
                    result['margins_pass'] = result['margins'] == 72
                    result['focus_above_fold'] = any(x['visible'] and 0 <= x['y'] < 844 for x in result['focusLinks'])
                    report['widths'][str(width)] = result
                report['checks']['structure'] = all(
                    d['root'] and d['chapter_pass'] and d['margins_pass'] and
                    not d['horizontalOverflow'] for d in report['widths'].values())
                report['checks']['reduced_motion_all_72_in_layout'] = all(
                    data['reducedMotion'] and data['marginsInLayout'] == 72
                    for data in report['widths'].values())
                report['checks']['mobile_contextual_focus'] = all(
                    report['widths'][str(w)]['focus_above_fold'] for w in (320,360,390))
                for name, selector in (
                    ('chronicle_original', '[data-fv-chronicle-view="original"]'),
                    ('case_franklin', '[data-fv-case-button="franklin"]'),
                    ('observer_b', '[data-fv-observer-switch="b"]')):
                    button = page.locator(selector).first
                    if button.count() and button.is_visible():
                        button.click(timeout=4000)
                        report['interactions'][name] = {'status': 'PASS' if button.get_attribute('aria-pressed') == 'true' else 'FAIL',
                                                        'after_aria_pressed': button.get_attribute('aria-pressed')}
                    else:
                        report['interactions'][name] = {'status': 'BLOCKED_NOT_VISIBLE'}
                evidence = page.locator('.fv-hf__opening-actions a[href="#fv-hf-evidence"]').first
                if evidence.count() and evidence.is_visible():
                    evidence.click(timeout=4000)
                    report['interactions']['evidence_nav'] = {'status': 'PASS' if page.evaluate('location.hash') == '#fv-hf-evidence' else 'FAIL'}
                else:
                    report['interactions']['evidence_nav'] = {'status':'BLOCKED_NOT_VISIBLE'}
                report['lab'] = page.evaluate('''() => ({
                    lcp_ms_observed: window.__fvLab?.lcp ?? null,
                    cls_observed: window.__fvLab?.cls ?? null,
                    navigation: performance.getEntriesByType('navigation').map(e => ({
                      domContentLoaded_ms: Math.round(e.domContentLoadedEventEnd),
                      transferSize: e.transferSize, responseEnd_ms: Math.round(e.responseEnd)
                    }))})''')
                if axe_available:
                    try:
                        page.add_script_tag(path=str(axe))
                        report['axe'] = run_axe_all_widths(page)
                    except Exception as exc:
                        report['axe'] = {'status': 'BLOCKED_AXE_RUNTIME',
                                         'reason': type(exc).__name__,
                                         'all_widths_pass': False}
                else:
                    report['axe'] = {'status':'BLOCKED_AXE_MISSING',
                                     'all_widths_pass': False,
                                     'reason':'Provide a local verified axe-core bundle via --axe'}
                report['checks']['axe_all_widths'] = report['axe'].get('all_widths_pass') is True
                report['archival_delivery'] = audit_archival_transfers(page, transfers)
                report['checks']['archival_delivery'] = report['archival_delivery']['passed']
                report['image_network'] = list(transfers.values())
                for width in (390, 1440):
                    no_js = browser.new_context(viewport={'width':width,'height':844},
                                                java_script_enabled=False)
                    if live_readonly:
                        no_js.route('**/*', block_analytics)
                    p = no_js.new_page()
                    if parsed.scheme == 'file':
                        p.set_content(Path(parsed.path).read_text(encoding='utf-8'), wait_until='load')
                    else:
                        p.goto(target, wait_until='domcontentloaded', timeout=30000)
                    no_js_result = inspect(p)
                    no_js_result['screenshot'] = f'nojs_{width}.png'
                    p.screenshot(path=str(dest / no_js_result['screenshot']),
                                 full_page=True, timeout=30000)
                    report['no_js'][str(width)] = no_js_result
                    no_js.close()
                report['checks']['no_js_meaning'] = all(
                    x['root'] and x['margins'] == 72 and all(y['exists'] for y in x['chapters'])
                    for x in report['no_js'].values())
                report['checks']['four_interactions'] = all(
                    x['status'] == 'PASS' for x in report['interactions'].values()) and len(report['interactions']) == 4
                report['reduced_motion']['requested'] = True
                report['reduced_motion']['matched'] = page.evaluate(
                    "matchMedia('(prefers-reduced-motion: reduce)').matches")
                report['status'] = 'AUDITED_INCOMPLETE' if not axe_available else 'AUDITED_REQUIRES_REVIEW'
                if not all(report['checks'].values()):
                    report['status'] = 'FAIL_QUALIFICATION_CHECKS'
            except Exception as err:
                report['status'] = 'BLOCKED_BROWSER_RUNTIME'
                report['error'] = f'{type(err).__name__}: {str(err).replace(target, safe_target)[:500]}'
        finally:
            browser.close()
    (dest/'results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--axe', help='Local axe-core minified JavaScript; mandatory for release admission')
    parser.add_argument('--live-readonly', action='store_true')
    parser.add_argument('--chromium', default='/usr/bin/chromium')
    args = parser.parse_args()
    report = run(args.target, args.output, args.axe, args.live_readonly, args.chromium)
    print(json.dumps({'status':report.get('status'), 'axe':report['axe']['status'],
                      'widths':len(report['widths']), 'no_js':len(report['no_js']),
                      'output':args.output, 'release_ready':False}, indent=2))
    return 2 if report.get('status') not in ('AUDITED_REQUIRES_REVIEW',) or report['axe']['status'] != 'NO_AUTOMATED_VIOLATIONS' else 0

if __name__ == '__main__':
    raise SystemExit(main())
