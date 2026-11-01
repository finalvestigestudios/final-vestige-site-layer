#!/usr/bin/env python3
"""Read-only local HTTP -> Chromium DOM replay for environments blocking browser localhost.

This does not replace native browser navigation, host CSP/cookies, Jetpack, axe,
Lighthouse or field CWV. It makes the ACTUAL WordPress server-rendered HTML
visually inspectable if a WordPress instance is separately running on loopback.
Rejects redirects, off-origin assets, unknown images, and incomplete archives.
"""
from __future__ import annotations
import argparse
import asyncio
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit, unquote
from urllib.request import build_opener, HTTPRedirectHandler, Request

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
MAX_DOCUMENT = 5_000_000
MAX_ASSET = 12_000_000
MAX_TOTAL = 32_000_000
SHA = re.compile(r'^[a-f0-9]{64}$')
# HTTP DOM replay can only attest resources whose bytes it has captured. A
# blocked subresource is a QA failure, not proof of successful offline display.
NETWORK_TAGS = ('iframe', 'frame', 'object', 'embed', 'video', 'audio',
                'source', 'track', 'picture', 'portal')


def audit_css_dependencies(css, label):
    """Refuse resources whose bytes won't be available in captured HTML."""
    require(not re.search(r'@import\b', css, re.I), label + ': CSS @import not captured')
    for match in re.finditer(r'url\s*\(\s*([^)]*)\)', css, re.I | re.S):
        target = match.group(1).strip().strip('\"\'').strip()
        require(target.startswith(('#', 'data:')),
                label + ': CSS url() resource not captured: ' + target[:120])


class Hold(RuntimeError):
    pass


def require(ok, msg):
    if not ok:
        raise Hold('REPLAY HOLD: ' + msg)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Hold('HTTP redirect refused: ' + str(newurl)[:150])


def origin(url):
    p = urlsplit(url)
    require(p.scheme == 'http' and p.hostname == '127.0.0.1' and
            p.port is not None and not p.username and not p.password and not p.fragment,
            'only explicit 127.0.0.1 loopback HTTP with port permitted')
    require('..' not in unquote(p.path).split('/'), 'parent path traversal refused')
    return f'http://127.0.0.1:{p.port}'


class Capture:
    def __init__(self, url, manifest):
        self.root = origin(url)
        require(urlsplit(url).path in ('', '/'), 'only local homepage root permitted')
        self.opener = build_opener(NoRedirect)
        self.manifest = manifest
        self.total = 0
        self.resources = []

    def get(self, href, budget=MAX_ASSET):
        url = urljoin(self.root + '/', href)
        require(origin(url) == self.root, 'off-origin or unexpected URL refused: ' + url[:160])
        require(urlsplit(url).path not in ('', '/wp-admin', '/wp-login.php'),
                'administrative URL refused')
        with self.opener.open(Request(url, headers={'User-Agent': 'FV-Local-Replay-QA/1.0'}),
                              timeout=8) as resp:
            require(resp.status == 200, 'asset HTTP status is not 200')
            require(resp.geturl() == url, 'asset redirected or changed URL')
            data = resp.read(budget + 1)
            mime = resp.headers.get_content_type()
        require(0 < len(data) <= budget, 'asset missing or exceeded size budget')
        self.total += len(data)
        require(self.total <= MAX_TOTAL, 'total capture exceeded 32 MB')
        self.resources.append({'path': urlsplit(url).path,
                               'sha256': hashlib.sha256(data).hexdigest(),
                               'bytes': len(data), 'mime': mime})
        return data, mime, url

    def assemble(self):
        html, mime, _ = self.get('/', MAX_DOCUMENT)
        require(mime in ('text/html', 'application/xhtml+xml'), 'root is not HTML')
        soup = BeautifulSoup(html, 'html.parser')
        require(not soup.find(NETWORK_TAGS),
                'embedded/picture/media content is not captured or certified')
        for tag in soup.find_all('link'):
            require(not set(tag.get('rel', [])) &
                    {'preload', 'modulepreload', 'prefetch', 'prerender'},
                    'preloaded or speculative resource is not captured')
        for tag in soup.find_all('style'):
            audit_css_dependencies(tag.get_text(), 'inline stylesheet')
        for tag in soup.find_all(style=True):
            audit_css_dependencies(str(tag['style']), 'inline style attribute')
        require(bool(soup.select_one('[data-fv-home-flagship]')),
                'actual homepage contains no flagship')
        require(len(soup.select('.fv-margin-strip__item')) == 72,
                '72 preserved Margins items not rendered')
        require(len(soup.select('[data-fv-case]')) == 3,
                'three investigation evidence cases not rendered')
        require(len(soup.select('.fv-hf__chapter-nav a')) == 7,
                'seven chapter navigation links not rendered')
        require(bool(soup.select_one('[data-fv-subscriptions-local-only]')),
                'isolated Jetpack nonfunctional boundary absent')
        require(len(soup.select('a[href*="/focus/"]')) >= 2,
                'protected Fieldbook links not rendered')
        stylesheet_count = 0
        script_count = 0
        for link in list(soup.find_all('link')):
            if 'stylesheet' not in link.get('rel', []):
                continue
            require(link.get('href'), 'stylesheet href missing')
            payload, kind, _ = self.get(link['href'], MAX_ASSET)
            require(kind in ('text/css', 'text/plain', 'application/octet-stream'),
                    'stylesheet MIME mismatch')
            css = payload.decode('utf-8')
            audit_css_dependencies(css, 'linked stylesheet')
            require('</style' not in css.lower(), 'CSS cannot be safely inlined')
            tag = soup.new_tag('style')
            if link.get('media'):
                tag['media'] = link['media']
            tag['data-fv-source-sha256'] = hashlib.sha256(payload).hexdigest()
            tag.string = css
            link.replace_with(tag)
            stylesheet_count += 1
        for script in list(soup.find_all('script')):
            if not script.get('src'):
                continue
            payload, kind, _ = self.get(script['src'], MAX_ASSET)
            require(kind in ('application/javascript', 'text/javascript', 'text/plain',
                             'application/octet-stream'), 'script MIME mismatch')
            code = payload.decode('utf-8')
            require('</script' not in code.lower(), 'JS cannot be safely inlined')
            del script['src']
            for attr in ('defer', 'async', 'integrity', 'crossorigin'):
                script.attrs.pop(attr, None)
            script['data-fv-source-sha256'] = hashlib.sha256(payload).hexdigest()
            script.string = code
            script_count += 1
        images = self.manifest['images']
        require(isinstance(images, dict) and len(images) == 3,
                'exact independent three-image manifest required')
        matched = set()
        for img in soup.select('img[src]'):
            require(not img.has_attr('srcset'), 'srcset cannot be byte-custodied in replay')
            url = urljoin(self.root + '/', img['src'])
            require(url in images, 'unapproved image in staged DOM: ' + url[:140])
            entry = images[url]
            require(isinstance(entry, dict) and SHA.fullmatch(entry.get('sha256', '')) and
                    type(entry.get('bytes')) is int, 'image digest/size missing')
            data, kind, _ = self.get(img['src'])
            require(len(data) == entry['bytes'] and
                    hashlib.sha256(data).hexdigest() == entry['sha256'],
                    'browser media differs from separately approved image fingerprint')
            require(kind.startswith('image/'), 'image MIME mismatch')
            img['src'] = f'data:{kind};base64,' + base64.b64encode(data).decode('ascii')
            matched.add(url)
        require(matched == set(images), 'all three archival-image exhibits must be present')
        require(stylesheet_count >= 1 and script_count >= 1,
                'CSS or interactive JS missing in rendered WordPress output')
        # Keep URLs of evidence links as links, but never navigate them during QA.
        return str(soup), {'html_sha256': hashlib.sha256(html).hexdigest(),
                           'stylesheets': stylesheet_count, 'scripts': script_count,
                           'archival_images_verified': len(matched),
                           'http_resources': self.resources}


async def browser_review(html, out, chromium):
    results = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=chromium, headless=True,
                                          args=['--no-sandbox', '--disable-dev-shm-usage'])
        version = browser.version
        for w in WIDTHS:
            page = await browser.new_page(viewport={'width': w, 'height': 900},
                                          reduced_motion='reduce' if w == 1024 else 'no-preference')
            errors = []
            blocked_requests = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            async def block_unverified(route):
                blocked_requests.append({'url': route.request.url,
                                         'type': route.request.resource_type})
                await route.abort()
            await page.route('**/*', block_unverified)
            await page.set_content(html, wait_until='domcontentloaded')
            # Bounded observation for startup/deferred subresources. Not a claim
            # that arbitrary later network activity can be certified offline.
            await page.wait_for_timeout(450)
            state = await page.evaluate('''() => ({
               width: document.documentElement.scrollWidth,
               chapters: [...document.querySelectorAll('.fv-hf__chapter-nav a')]
                 .every(a => document.querySelector(a.getAttribute('href'))),
               cases: document.querySelectorAll('[data-fv-case]').length,
               unloadedImages: [...document.images].filter(i=>!i.complete||i.naturalWidth===0).length,
               focus: document.querySelectorAll('a[href*="/focus/"]').length
            })''')
            results[str(w)] = {'no_overflow': state['width'] <= w + 1,
                               'anchors_work': bool(state['chapters']),
                               'images_decoded': state['unloadedImages'] == 0,
                               'focus_preserved': state['focus'] >= 2,
                               'no_js_errors': not errors,
                               'no_unverified_network': not blocked_requests,
                               'blocked_requests': blocked_requests,
                               'scroll_width': state['width'], 'js_errors': errors}
            if w in (320, 390, 768, 1440, 1920):
                await page.screenshot(path=str(out / f'wp-http-replay-{w}.png'), full_page=(w in (390, 1440)))
            await page.wait_for_timeout(50)
            # Full-page screenshots may trigger lazy resource requests. Do not
            # finalize the success flags until after the screenshot completes.
            results[str(w)]['no_unverified_network'] = not blocked_requests
            results[str(w)]['blocked_requests'] = list(blocked_requests)
            results[str(w)]['no_js_errors'] = not errors
            results[str(w)]['js_errors'] = list(errors)
            await page.close()
        page = await browser.new_page(viewport={'width': 390, 'height': 844},java_script_enabled=False)
        no_js_blocked = []
        async def block_no_js(route):
            no_js_blocked.append(route.request.url)
            await route.abort()
        await page.route('**/*', block_no_js)
        await page.set_content(html, wait_until='domcontentloaded')
        visible = await page.locator('[data-fv-case]:visible').count()
        results['no_js'] = {'all_three_cases_visible': visible == 3,
                            'no_unverified_network': not no_js_blocked,
                            'blocked_requests': no_js_blocked}
        await page.close()
        # Viewport-width approximation is not a claim of real browser 200% zoom.
        page = await browser.new_page(viewport={'width': 720, 'height': 900})
        zoom_blocked = []
        async def block_zoom(route):
            zoom_blocked.append(route.request.url)
            await route.abort()
        await page.route('**/*', block_zoom)
        await page.set_content(html, wait_until='domcontentloaded')
        await page.wait_for_timeout(450)
        sw = await page.evaluate('document.documentElement.scrollWidth')
        results['zoom_proxy_720'] = {'no_overflow': sw <= 721,
                                     'no_unverified_network': not zoom_blocked,
                                     'blocked_requests': zoom_blocked,
                                     'scroll_width': sw}
        await page.screenshot(path=str(out / 'wp-http-replay-zoom-proxy.png'))
        await page.wait_for_timeout(50)
        results['zoom_proxy_720']['no_unverified_network'] = not zoom_blocked
        results['zoom_proxy_720']['blocked_requests'] = list(zoom_blocked)
        await page.close()
        await browser.close()
    return version, results


def passing(checks):
    return all(passing(v) if isinstance(v, dict) else v is True for k, v in checks.items()
               if k not in ('scroll_width', 'js_errors', 'blocked_requests'))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--url', required=True, help='actual local HTTP server, 127.0.0.1 only')
    ap.add_argument('--media-manifest', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--chromium', default='/usr/bin/chromium')
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True, mode=0o700)
    receipt = {'mode': 'SERVER_RENDERED_HTTP_DOM_REPLAY_NOT_BROWSER_NAVIGATION',
               'status': 'FAILED_CLOSED', 'run_utc': datetime.now(timezone.utc).isoformat(),
               'wordPress_hosted_certification': False, 'jetpack_delivery_verified': False,
               'axe_wCAG_certified': False, 'lighthouse_measured': False, 'field_cwv_measured': False,
               'browser_CSP_or_cookies_verified': False, 'source_rights_cleared': False}
    try:
        manifest = json.loads(args.media_manifest.read_text('utf-8'))
        html, captured = Capture(args.url, manifest).assemble()
        version, checks = asyncio.run(browser_review(html, args.output, args.chromium))
        receipt.update(capture=captured, chromium_version=version, checks=checks,
                       status=('VISUAL_REPLAY_PASS_NOT_WORDPRESS_ACCEPTANCE'
                               if passing(checks) else 'VISUAL_REPLAY_FAIL'))
    except Exception as exc:
        receipt.update(error_type=type(exc).__name__, error=str(exc)[:400])
    (args.output / 'HTTP_REPLAY_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'status': receipt['status'], 'error': receipt.get('error'),
                      'checks': receipt.get('checks')}, indent=2))
    return 0 if receipt['status']=='VISUAL_REPLAY_PASS_NOT_WORDPRESS_ACCEPTANCE' else 1


if __name__=='__main__':
    raise SystemExit(main())
