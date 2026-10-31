#!/usr/bin/env python3
"""Read-only, logged-out Jetpack signup entrypoint browser probe.

NEVER fills a field, submits a form, accepts cookies, or signs up. It examines
only public pages and writes a PII-free result. Safe clicks are restricted to
non-submit subscription disclosure/link elements.
"""
import argparse
import json
import os
import shutil
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

PUBLIC = (
    'https://finalvestige.com/dispatch/',
    'https://finalvestige.com/focus/',
)
SELECTOR = ('main .wp-block-jetpack-subscriptions a, '
            'main .wp-block-jetpack-subscriptions button, '
            'main .jetpack-subscribe-modal a, '
            'main .jetpack-subscribe-modal button, '
            'main .wp-block-jetpack-subscriptions a:has-text("Subscribe"), main .wp-block-jetpack-subscriptions a:has-text("fieldbook")')


def safe_url(url):
    """Never disclose querystrings, fragments, tokens, credentials, or emails."""
    p = urlparse(url)
    return (p.scheme + '://' + p.hostname + ((':' + str(p.port)) if p.port else '')
            + p.path) if p.scheme in ('https', 'http') and p.hostname else '(unrecognized)'


def email_field(page):
    loc = page.locator('input[type="email"]:visible').first
    if not loc.count():
        return {'visible': False, 'labelled': False, 'enabled': False}
    labelled = loc.evaluate('''e => !!(e.getAttribute('aria-label') ||
       e.getAttribute('aria-labelledby') || e.labels?.length)''')
    return {'visible': True, 'labelled': bool(labelled), 'enabled': loc.is_enabled()}


def inspect(page, address, pause_ms=800, screenshots=None, preloaded=False):
    result = {'page': safe_url(address), 'mode': 'logged-out / no-submit',
              'decision': 'NEEDS_HUMAN_REVIEW', 'submitted': False,
              'clicked_submit': False, 'entered_email': False}
    try:
        response = None if preloaded else page.goto(address, wait_until='domcontentloaded', timeout=20000)
        page.wait_for_timeout(pause_ms)
        result['http_status'] = response.status if response else None
        before_url = safe_url(page.url)
        result['before'] = email_field(page)
        if result['before']['visible']:
            result['decision'] = ('FORM_PRESENT_LABELLED' if result['before']['labelled']
                                  else 'FORM_PRESENT_NEEDS_LABEL_REVIEW')
            return result
        controls = page.locator(SELECTOR)
        clicked = False
        for idx in range(min(controls.count(), 20)):
            el = controls.nth(idx)
            if not el.is_visible():
                continue
            tag = el.evaluate('e => e.tagName.toLowerCase()')
            typ = el.get_attribute('type') or ''
            if tag == 'button' and typ.lower() != 'button':
                continue  # never click a form submit, even with no input rendered
            if tag not in ('a', 'button'):
                continue
            txt = (el.inner_text(timeout=2000) or '').lower()
            if not any(s in txt for s in ('subscribe', 'fieldbook', 'sign up', 'join')):
                continue
            result['control_kind'] = tag + (':' + typ if typ else '')
            # Click only link or explicitly non-submit button. No value is entered.
            el.click(timeout=5000, no_wait_after=True)
            clicked = True
            page.wait_for_timeout(pause_ms)
            break
        result['control_clicked'] = clicked
        result['after'] = email_field(page)
        result['destination'] = safe_url(page.url)
        if result['after']['visible']:
            result['decision'] = ('FORM_ACCESSIBLE_AFTER_SAFE_CLICK' if result['after']['labelled']
                                  else 'FORM_AFTER_CLICK_NEEDS_LABEL_REVIEW')
        elif clicked and (safe_url(page.url) == safe_url(address) or (preloaded and safe_url(page.url) == before_url)):
            result['decision'] = 'SUSPECT_SELF_LINK_LOOP_NO_FORM'
        elif clicked:
            result['decision'] = 'NAVIGATED_NO_FORM_NEEDS_HUMAN_REVIEW'
        else:
            result['decision'] = 'NO_SAFE_CONTROL_OR_FORM'
        if screenshots:
            path = Path(screenshots) / (urlparse(address).path.strip('/') or 'root')
            path.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(path.with_suffix('.png')), full_page=False)
            result['screenshot_file'] = path.name + '.png'
    except Exception as exc:
        # Keep exceptions sanitized: no raw URLs or PII in output.
        result['decision'] = 'BROWSER_PROBE_ERROR'
        result['exception_class'] = type(exc).__name__
    return result


def run(urls, screenshot_dir=None, browser='chromium', pause_ms=800):
    with sync_playwright() as pw:
        browser_type = getattr(pw, browser)
        executable = os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('chromium-browser')
        options = {'executable_path': executable} if executable else {}
        br = browser_type.launch(headless=True, **options)
        try:
            out = []
            for url in urls:
                context = br.new_context(service_workers='block', accept_downloads=False,
                                         viewport={'width': 390, 'height': 844})
                try:
                    out.append(inspect(context.new_page(), url, pause_ms, screenshot_dir))
                finally:
                    context.close()
            return out
        finally:
            br.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--url', action='append', help='Private local fixture HTTP URL only, when --allow-fixture')
    p.add_argument('--allow-fixture', action='store_true')
    p.add_argument('--screenshot-dir', help='Optional public-page viewport capture directory')
    p.add_argument('--json', dest='json_path', help='Output PII-free report file')
    args = p.parse_args()
    urls = tuple(args.url or PUBLIC)
    if args.url and not args.allow_fixture:
        p.error('Custom URL is disabled unless explicitly running fixture mode')
    if args.url and any(urlparse(u).hostname not in ('localhost', '127.0.0.1') for u in urls):
        p.error('Fixture URLs must be loopback-only')
    report = {'signup_completion_claimed_verified': False, 'is_email_delivery_test': False,
              'is_subscriber_confirmation': False, 'results': run(urls, args.screenshot_dir)}
    s = json.dumps(report, indent=2, sort_keys=True)
    if args.json_path:
        Path(args.json_path).write_text(s + '\n', encoding='utf-8')
    print(s)
    return 0 if all(row['decision'] in ('FORM_PRESENT_LABELLED', 'FORM_ACCESSIBLE_AFTER_SAFE_CLICK')
                    for row in report['results']) else 2

if __name__ == '__main__':
    raise SystemExit(main())
