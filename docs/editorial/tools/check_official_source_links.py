#!/usr/bin/env python3
"""Anonymous Chromium check of four publication-blocking documentary references.

Requirements: pip install playwright; python -m playwright install chromium
Run with --out /private/link-qa [--browser-bin /usr/bin/chromium], or with
--cdp http://127.0.0.1:9222 to reuse an authorized local Chromium process.

No WordPress credentials, site writes, newsletter operations or social actions.
This is an evidence capture helper, NOT an automatic publication PASS: a human
must review the screenshots, particularly Chrome's PDF viewer / downloads.
Never attach local browser screenshots containing sensitive information publicly.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, Error as PlaywrightError

SOURCES = {
    'USACE_bonnet_carre_legacy': 'https://www.mvn.usace.army.mil/Portals/56/docs/PAO/Brochures/BCspillwaybooklet.pdf',
    'USACE_bonnet_carre_2018': 'https://www.mvn.usace.army.mil/Portals/56/docs/Recreation/BCS/Brochures/BC%20spillway%20booklet%20Dec%202018%20.pdf',
    'USGS_extraordinary_floods': 'https://pubs.usgs.gov/publication/sir20085164',
    'USGS_Louisiana_wetlands_1994': 'https://pubs.usgs.gov/publication/ofr94275',
}
OFFICIAL_HOSTS = frozenset({'www.mvn.usace.army.mil', 'pubs.usgs.gov'})
DENIAL_MARKERS = ('403 forbidden', 'access denied', 'request blocked', 'error 403', 'bot verification', 'verify you are human')


def is_approved_url(url):
    """Refuse arbitrary endpoints / lookalike domains in link check tool."""
    try:
        p = urlsplit(url)
        return p.scheme == 'https' and (p.hostname or '').lower() in OFFICIAL_HOSTS and not p.username and not p.password
    except ValueError:
        return False


def classify(status, content_type, body, navigated):
    """Never claim a PDF has rendered merely because HTTP returned 200."""
    if status in (401, 403, 429):
        return 'ACCESS_RESTRICTED_IN_BROWSER'
    if status is not None and status >= 400:
        return 'HTTP_ERROR_IN_BROWSER'
    if status != 200:
        return 'INDETERMINATE'
    if 'pdf' in content_type.lower():
        return 'PDF_HTTP_200_READER_RENDER_UNVERIFIED'
    if any(m in body.lower() for m in DENIAL_MARKERS):
        return 'DENIAL_PAGE_DESPITE_HTTP_200'
    if navigated and len(body.strip()) > 100:
        return 'HTML_VISIBLE_NEEDS_MANUAL_REVIEW'
    return 'INDETERMINATE'


def check_page(browser, key, url, out, timeout_ms):
    """New isolated browser context = anonymous visitor, no editor cookies."""
    ctx = browser.new_context(viewport={'width': 1280, 'height': 900}, accept_downloads=True)
    page = ctx.new_page()
    seen = []
    page.on('response', lambda r: seen.append({'url': r.url, 'status': r.status, 'type': r.headers.get('content-type', '')})
            if r.request.is_navigation_request() else None)
    result = {'source': key, 'url': url, 'status': None, 'contentType': '',
              'finalHost': None, 'decision': 'INDETERMINATE', 'screenshot': None,
              'navigationError': None, 'manualReaderPass': False}
    try:
        nav = None
        try:
            nav = page.goto(url, wait_until='domcontentloaded', timeout=timeout_ms)
            page.wait_for_timeout(900)
        except PlaywrightError as exc:
            # PDF downloads may abort navigation in headless Chromium; collect
            # response metadata but never turn that into a reader-visual PASS.
            result['navigationError'] = str(exc).splitlines()[0][:180]
        relevant = [r for r in seen if is_approved_url(r['url'])]
        if nav:
            status = nav.status
            ctype = nav.headers.get('content-type', '')
        elif relevant:
            status, ctype = relevant[-1]['status'], relevant[-1]['type']
        else:
            status, ctype = None, ''
        try:
            body = page.locator('body').inner_text(timeout=1500)[:1000]
        except PlaywrightError:
            body = ''
        result.update(status=status, contentType=ctype, finalHost=urlsplit(page.url).hostname)
        result['decision'] = classify(status, ctype, body, nav is not None)
        if nav and result['finalHost'] in OFFICIAL_HOSTS:
            try:
                filename = key + '.png'
                page.screenshot(path=str(out / filename), full_page=False, timeout=10000)
                result['screenshot'] = filename
            except PlaywrightError:
                pass
        if (status is not None and result['finalHost'] not in OFFICIAL_HOSTS
                and 'pdf' not in ctype.lower()):
            result['decision'] = 'UNEXPECTED_REDIRECT_OR_BROWSER_VIEWER'
        return result
    finally:
        ctx.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--browser-bin', default=None)
    parser.add_argument('--cdp', default=None)
    parser.add_argument('--timeout-ms', type=int, default=25000)
    args = parser.parse_args()
    if args.cdp:
        p = urlsplit(args.cdp)
        if p.scheme != 'http' or p.hostname not in ('127.0.0.1', 'localhost', '::1'):
            parser.error('--cdp must be a loopback-only local browser (never a remote CDP host)')
    if not all(is_approved_url(u) for u in SOURCES.values()):
        parser.error('Non-official URL found in immutable source manifest')
    args.out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = (p.chromium.connect_over_cdp(args.cdp) if args.cdp
                   else p.chromium.launch(headless=True, executable_path=args.browser_bin))
        try:
            entries = [check_page(browser, key, url, args.out, args.timeout_ms)
                       for key, url in SOURCES.items()]
        finally:
            if not args.cdp:
                browser.close()
    report = {'checkedUtc': datetime.now(timezone.utc).isoformat(),
              'visitorMode': 'anonymous_fresh_context',
              'releaseGate': 'MANUAL_READER_REVIEW_REQUIRED', 'entries': entries}
    (args.out / 'source-check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    for e in entries:
        print(e['source'], e['status'], e['decision'], 'screenshot=' + str(e['screenshot']))
    print('No publication PASS asserted; inspect screenshots and actual PDF in an ordinary browser.')


if __name__ == '__main__':
    main()
