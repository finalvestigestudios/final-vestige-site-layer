#!/usr/bin/env python3
"""Read-only Apollo Experience 2.0 WordPress staging admission probe.

NEVER installs, activates, logs into or changes WordPress. Explicit non-production
host and an existing editor cookie are required. Checks served source provenance,
server-side privilege/nonce controls, CSP, and the four exact export bytes.
May test localhost PHP *stub* with --offline-php-stub, which is NOT WordPress.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import stat
import sys
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse
from urllib.request import Request, build_opener, HTTPRedirectHandler, ProxyHandler
from urllib.error import HTTPError
from source_concordance import build_concordance, build_context_index
from atlas_custody import build_atlas

HERE = Path(__file__).resolve().parent
GENERATED = HERE.parent.parent / 'generated'
EXPORTS = ('evidence-export.csv','evidence-export.json','response-export.csv','response-export.json','source-context.json','atlas-custody.json')
EXPECTED_SOURCE_HEAD = '74375657f2cdaac0710f94c6de6c24534ee06858'


class AdmissionError(RuntimeError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise AdmissionError('Redirect forbidden: staging session, origin, or URL not verified')


class PreviewParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.iframes = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'iframe':
            self.iframes.append(dict(attrs))


def require_safe_origin(base: str, allow_stub: bool = False) -> str:
    u = urlparse(base)
    host = (u.hostname or '').lower().rstrip('.')
    if (u.username or u.password or u.query or u.fragment or
        u.path not in ('', '/') or not host):
        raise AdmissionError('Expected bare staging origin; no credentials, query, or path')
    if host == 'finalvestige.com' or host.endswith('.finalvestige.com'):
        raise AdmissionError('Production/brand domain is prohibited for admission probe')
    if allow_stub:
        if not (u.scheme == 'http' and host in ('127.0.0.1', 'localhost')):
            raise AdmissionError('Stub mode only permits loopback HTTP')
    elif u.scheme != 'https' or host in ('127.0.0.1','localhost','0.0.0.0'):
        raise AdmissionError('Live review requires HTTPS on an explicitly separate staging host')
    if u.port is not None and (u.port < 1 or u.port > 65535):
        raise AdmissionError('Invalid staging port')
    return f'{u.scheme}://{u.netloc}'


def no_redirect_fetch(url: str, cookie: str = '') -> tuple[int, dict, bytes]:
    headers = {'User-Agent': 'FV-Apollo-ReadOnly-Staging-Admission/1.0',
               'Accept': 'text/html, application/json, text/csv'}
    if cookie:
        headers['Cookie'] = cookie
    # Never forward an editor cookie through proxy environment variables.
    opener = build_opener(NoRedirect, ProxyHandler({}))
    try:
        with opener.open(Request(url, headers=headers, method='GET'), timeout=12) as r:
            return r.status, {k.lower():v for k,v in r.headers.items()}, r.read(1_000_001)
    except HTTPError as e:
        return e.code, {k.lower():v for k,v in e.headers.items()}, e.read(4096)


def same_origin_ajax(origin: str, url: str, action: str) -> str:
    u = urlparse(url)
    base = urlparse(origin)
    if ((u.scheme, u.netloc) != (base.scheme, base.netloc)
        or not u.path.endswith('/wp-admin/admin-ajax.php') or u.fragment):
        raise AdmissionError('Preview URL must be a same-origin WordPress admin-ajax endpoint')
    q = parse_qs(u.query, keep_blank_values=True)
    if set(q) != {'action','_wpnonce'} or q['action'] != [action] or len(q['_wpnonce']) != 1 or not q['_wpnonce'][0]:
        raise AdmissionError('Preview AJAX action/nonce must be unique and expected')
    return url


def read_cookie_file(path: Path) -> str:
    s = path.stat()
    if not stat.S_ISREG(s.st_mode) or s.st_mode & 0o077:
        raise AdmissionError('Session cookie file must be a private regular file (chmod 600)')
    if s.st_size > 4096:
        raise AdmissionError('Session cookie file too large')
    value = path.read_text(encoding='utf-8').strip()
    if not value or '\n' in value or '\r' in value or not re.fullmatch(r'[\x20-\x7e]+',value):
        raise AdmissionError('Invalid cookie header contents')
    return value


def admit(origin: str, review_path: str, cookie: str, *, allow_stub=False,
          fetch=no_redirect_fetch, expected_dir=GENERATED) -> dict:
    origin = require_safe_origin(origin, allow_stub=allow_stub)
    if not review_path.startswith('/') or review_path.startswith('//') or '#' in review_path or '?' in review_path:
        raise AdmissionError('Review path must be a literal same-origin absolute path without query')
    if not cookie:
        raise AdmissionError('No editor cookie: private staged experience cannot be assessed')
    status, headers, body = fetch(origin + review_path, cookie)
    if status != 200:
        raise AdmissionError(f'Authorized review page failed: HTTP {status}')
    parser = PreviewParser();parser.feed(body.decode('utf-8', 'replace'))
    if len(parser.iframes) != 1:
        raise AdmissionError('Expected exactly one private Apollo iframe')
    frame = parser.iframes[0]
    flags = set((frame.get('sandbox') or '').split())
    if ('allow-scripts' not in flags or 'allow-downloads' not in flags
        or 'allow-same-origin' in flags or 'allow-top-navigation' in flags):
        raise AdmissionError('Iframe sandbox flags violated')
    src = same_origin_ajax(origin, frame.get('src',''), 'fv_ex2_apollo_sealed_page')
    anonymous, _, anonymous_body = fetch(src, '')
    if anonymous != 403 or anonymous_body:
        raise AdmissionError('Anonymous private-page request did not return empty HTTP 403')
    u = urlparse(src)
    bad_nonce = urlencode({'action':'fv_ex2_apollo_sealed_page',
                           '_wpnonce':parse_qs(u.query)['_wpnonce'][0]+'-corrupt'})
    bad_url = urlunparse((u.scheme,u.netloc,u.path,'',bad_nonce,''))
    rejected, _, rejected_body = fetch(bad_url,cookie)
    if rejected != 403 or rejected_body:
        raise AdmissionError('Tampered preview nonce did not return empty HTTP 403')
    status, headers, html = fetch(src, cookie)
    if status != 200 or len(html) < 100000:
        raise AdmissionError(f'Private source rendering failed or truncated: HTTP {status}')
    if headers.get('x-fv-ex2-apollo-source-head') != EXPECTED_SOURCE_HEAD:
        raise AdmissionError('Actually served Apollo source-head header mismatch')
    expected_fragment = hashlib.sha256((expected_dir/'fragment.html').read_bytes()).hexdigest()
    if headers.get('x-fv-ex2-apollo-fragment-sha256') != expected_fragment:
        raise AdmissionError('Actually served fragment provenance hash mismatch')
    for kind, file in (('css','apollo.css'),('js','apollo.js')):
        digest = hashlib.sha256((expected_dir/file).read_bytes()).hexdigest()
        if headers.get('x-fv-ex2-apollo-'+kind+'-sha256') != digest:
            raise AdmissionError('Actually served '+kind.upper()+' provenance hash mismatch')
    # The generated source-concordance must also match the local pinned data.
    # A valid original fragment hash alone is insufficient for staged HTML
    # assembled from a second authenticated asset.
    expected_concordance_sha = build_concordance(generated=expected_dir)[2]['concordance_html_sha256']
    if headers.get('x-fv-ex2-apollo-concordance-sha256') != expected_concordance_sha:
        raise AdmissionError('Actually served concordance provenance hash mismatch')
    expected_context = build_context_index(generated=expected_dir).encode('utf-8')
    expected_context_sha = hashlib.sha256(expected_context).hexdigest()
    if headers.get('x-fv-ex2-apollo-context-sha256') != expected_context_sha:
        raise AdmissionError('Actually served source context index hash mismatch')
    atlas_panel, _, atlas_data, atlas_receipt = build_atlas(expected_dir)
    if headers.get('x-fv-ex2-apollo-atlas-sha256') != atlas_receipt['atlas_index_sha256']:
        raise AdmissionError('Actually served Atlas provenance index hash mismatch')
    if headers.get('x-fv-ex2-apollo-atlas-panel-sha256') != atlas_receipt['atlas_html_sha256']:
        raise AdmissionError('Actually served Atlas panel hash mismatch')
    if (html.count(b'data-atlas-custody-id=') != 6 or html.count(b'id="fv-ex2-atlas-custody"') != 1
        or b'{{FV_EX2_ATLAS_EXPORT}}' in html or b'No mapped location: archival precision unreviewed.' not in html):
        raise AdmissionError('Served Atlas six-record geography hold missing')
    if b'id="source-concordance"' not in html or html.count(b'data-concordance-record=') != 6:
        raise AdmissionError('Served six-source concordance incomplete')
    if html.count(b'type="radio"') != 4 or html.count(b' data-concordance-era=') != 6:
        raise AdmissionError('Source year lens incomplete')
    if (html.count(b'data-crosswalk-id=') != 6 or
        html.count(b'data-crosswalk-review="hold">') != 1 or
        html.count(b'id="fv-ex2-research-desk-crosswalk"') != 1):
        raise AdmissionError('Independent Research Desk crosswalk or identifier review hold missing')
    if b'{{FV_EX2_CONTEXT_EXPORT}}' in html or html.count(b'source-context.json') < 1:
        raise AdmissionError('Served six-source concordance incomplete')
    csp = headers.get('content-security-policy','')
    for term in ("default-src 'none'", "frame-ancestors 'self'", "img-src 'none'",
                 "script-src 'nonce-", "style-src 'nonce-", "connect-src 'none'"):
        if term not in csp:
            raise AdmissionError('Missing private preview CSP term: '+term)
    if "'unsafe-inline'" in csp or headers.get('x-content-type-options') != 'nosniff' or 'noindex' not in headers.get('x-robots-tag',''):
        raise AdmissionError('Private preview response headers unsafe')
    if html.count(b'<main ') != 1 or html.count(b'<h1 ') != 1 or b'id="atlas"' not in html or b'id="documentary-trails"' not in html:
        raise AdmissionError('Actual HTML evidence component contract incomplete')
    for n in (b'data-ex2-stage',b'data-ex2-atlas-item',b'data-ex2-trail-card',b'data-ex2-response-item'):
        if html.count(n) < 6:
            raise AdmissionError('Missing six evidence records: '+n.decode())
    if b'{{FV_EX2_ASSET_BASE}}' in html:
        raise AdmissionError('Unresolved evidence export placeholders')
    download_hashes = {}
    u = urlparse(src)
    for name in EXPORTS:
        query = urlencode({'action':'fv_ex2_apollo_sealed_download',
                           'file':name, '_wpnonce':parse_qs(u.query)['_wpnonce'][0]})
        url = urlunparse((u.scheme,u.netloc,u.path,'',query,''))
        anonymous_status, _, anonymous_data = fetch(url,'')
        if anonymous_status != 403 or anonymous_data:
            raise AdmissionError('Anonymous private export did not return empty HTTP 403: '+name)
        status,h,data = fetch(url,cookie)
        expected = (expected_context if name == 'source-context.json' else
                    atlas_data.encode('utf-8') if name == 'atlas-custody.json' else
                    (expected_dir/name).read_bytes())
        digest = hashlib.sha256(expected).hexdigest()
        if (status != 200 or data != expected or h.get('x-fv-ex2-apollo-asset-sha256') != digest
            or 'attachment;' not in h.get('content-disposition','') or 'noindex' not in h.get('x-robots-tag','')):
            raise AdmissionError('Export integrity/status/headers failed: '+name)
        download_hashes[name] = digest
    return {'status':'PASS_HTTP_INTEGRITY_ONLY', 'source_head':EXPECTED_SOURCE_HEAD,
            'fragment_sha256':expected_fragment,'concordance_sha256':expected_concordance_sha,'context_index_sha256':expected_context_sha,
            'exports_sha256':download_hashes,
            'atlas_index_sha256':atlas_receipt['atlas_index_sha256'],
            'atlas_panel_sha256':atlas_receipt['atlas_html_sha256'],
            'atlas_publication_references':6,'atlas_geo_pins':0,'atlas_edges':0,
            'anonymous_private_page':403,'anonymous_private_exports':len(EXPORTS),
            'tampered_nonce_page':403,'review_http':200,'source_http':200,
            'read_only':True,'no_wordpress_writes':True,
            'browser_csp_enforcement':'NOT_TESTED', 'axe':'NOT_TESTED',
            'wordpress_integrated':False, 'target':'PHP_STUB' if allow_stub else 'EXTERNAL_HTTP_UNVERIFIED_WP',
            'limitations':('HTTP response and source bytes only; this does NOT establish '
                           'Playwright browser CSP, screen-reader, Safari, axe or field CWV.')}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin',required=True,help='HTTPS origin of a separate, approved WP staging host')
    parser.add_argument('--review-path',required=True,help='Read-only page containing private shortcode')
    parser.add_argument('--cookie-file',required=True, type=Path,help='Mode-600 Cookie header; never written into report')
    parser.add_argument('--expected-dir',type=Path,default=GENERATED)
    parser.add_argument('--report',type=Path,help='Write redacted JSON results, never session tokens')
    parser.add_argument('--offline-php-stub',action='store_true',help='Only for localhost PHP unit tests; not a WP admission')
    args=parser.parse_args()
    try:
        report=admit(args.origin,args.review_path,read_cookie_file(args.cookie_file),
                     allow_stub=args.offline_php_stub,expected_dir=args.expected_dir)
        if args.report:args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        print(json.dumps(report,indent=2,sort_keys=True))
    except (AdmissionError,OSError) as err:
        print('RELEASE HOLD: '+str(err),file=sys.stderr)
        raise SystemExit(2)


if __name__=='__main__':main()
