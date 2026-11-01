#!/usr/bin/env python3
"""R45: fail-closed semantic/content-navigation audit of PRIVATE R44 HTML ZIP.

R44 authenticates exact bytes against independently supplied R42/R43 pins.
R45 additionally checks the actual HTML that an offline reviewer would open:
no executable/active markup, external navigation or CSS, missing safety banner,
or lost/misrouted article links. Never authorize review, CMS or publication.

This module performs no filesystem, network, WordPress or public-site writes.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from io import BytesIO
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

R44 = Path(__file__).with_name('reviewer_private_zip_gate.py')
if not R44.is_file() or R44.is_symlink():
    raise ValueError('R44 exact nonsymlinked ZIP verifier required')
_spec = importlib.util.spec_from_file_location('preparedness_r45_frozen_r44', R44)
if _spec is None or _spec.loader is None:
    raise ValueError('cannot load frozen R44 verifier')
r44 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r44)

FLAGS = r44.FLAGS
EXPECTED = r44.EXPECTED
AUTHORITY = 'PRIVATE_REVIEW_HTML_SEMANTIC_LINK_AUDIT_NOT_APPROVAL'
CSP = ("default-src 'none'; style-src 'unsafe-inline'; connect-src 'none'; "
       "img-src 'none'; font-src 'none'; form-action 'none'; base-uri 'none'")
CSS = (
    'body{font:16px/1.6 system-ui,sans-serif;max-width:1000px;'
    'margin:2rem auto;padding:1rem;background:#f5f5f1;color:#202833}'
    'section,article{background:white;border:1px solid #ddd;padding:1rem;'
    'margin:1rem 0}pre{white-space:pre-wrap;overflow-wrap:anywhere}'
    'dt{font-weight:700;margin-top:.6rem}.hold{border-left:6px solid #753900;'
    'background:#ffe2ae;padding:1rem;font-weight:700}'
    'a:focus-visible{outline:3px solid orange}'
)
TAGS = frozenset(('html', 'head', 'meta', 'title', 'style', 'body', 'h1',
                  'p', 'a', 'main', 'section', 'h2', 'dl', 'dt', 'dd',
                  'pre', 'article', 'ol', 'li'))
VOID = frozenset(('meta',))

class SemanticHold(ValueError):
    """An offline review ZIP is not safe to display or approve."""

def need(ok, message):
    if not ok:
        raise SemanticHold(message)

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

class _Page(HTMLParser):
    """Exact R43 conservative markup contract. Raw evidence stays escaped."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.links = []
        self.tags = Counter()
        self.doctypes = 0
        self.meta = []
        self.style_chunks = []
        self.hold_chunks = []
        self.hold_depth = None
        self.hold_count = 0

    def handle_decl(self, decl):
        need(decl.lower() == 'doctype html' and self.doctypes == 0
             and not self.tags, 'unsafe or repeated HTML doctype')
        self.doctypes += 1

    def unknown_decl(self, data):
        raise SemanticHold('unknown executable markup declaration')

    def handle_comment(self, data):
        raise SemanticHold('HTML comments are outside frozen R43 renderer')

    def handle_pi(self, data):
        raise SemanticHold('processing instruction is not inert review markup')

    def handle_startendtag(self, tag, attrs):
        raise SemanticHold('self-closing element outside frozen R43 renderer')

    def handle_starttag(self, tag, attrs):
        need(self.doctypes == 1 and tag in TAGS,
             'unexpected potentially active HTML tag')
        keys = [k for k, _ in attrs]
        need(len(keys) == len(set(keys)) and None not in keys,
             'duplicated or malformed HTML attribute')
        params = dict(attrs)
        if tag == 'html':
            need(params == {'lang': 'en'} and not self.stack,
                 'unsafe page root')
        elif tag == 'meta':
            need(self.stack == ['html', 'head'] and
                 (params == {'charset': 'utf-8'} or
                  params == {'http-equiv': 'Content-Security-Policy',
                             'content': CSP}),
                 'unexpected or weakened page metadata')
            self.meta.append(params)
        elif tag == 'a':
            need(set(params) == {'href'} and type(params['href']) is str,
                 'external, executable or ambiguous anchor attribute')
            self.links.append(params['href'])
        elif tag == 'p':
            need(params in ({}, {'class': 'hold'}),
                 'unsafe paragraph attributes')
            if params.get('class') == 'hold':
                need(self.hold_depth is None and self.hold_count == 0,
                     'missing or duplicate private safety banner')
                self.hold_depth = len(self.stack) + 1
                self.hold_count += 1
        else:
            need(not params, 'active, inline-style or unexpected HTML attribute')
        self.tags[tag] += 1
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        need(self.stack and self.stack[-1] == tag and tag not in VOID,
             'unbalanced or unexpectedly nested HTML')
        if tag == 'p' and self.hold_depth == len(self.stack):
            self.hold_depth = None
        self.stack.pop()

    def handle_data(self, data):
        if self.stack and self.stack[-1] == 'style':
            self.style_chunks.append(data)
        if self.hold_depth is not None:
            self.hold_chunks.append(data)

    def assert_safe(self):
        need(self.doctypes == 1 and not self.stack and
             self.tags['html'] == self.tags['head'] ==
             self.tags['body'] == self.tags['main'] ==
             self.tags['title'] == self.tags['style'] == 1 and
             self.tags['meta'] == 2 and
             self.hold_depth is None and self.hold_count == 1,
             'incomplete HTML or absent private reviewer HOLD banner')
        need(len(self.meta) == 2 and
             {'charset': 'utf-8'} in self.meta and
             {'http-equiv': 'Content-Security-Policy', 'content': CSP} in self.meta,
             'missing exact offline content-security policy')
        need(''.join(self.style_chunks) == CSS,
             'offline CSS differs from inert frozen R43 stylesheet')
        need('PRIVATE / UNVERIFIED / HOLD.' in ''.join(self.hold_chunks),
             'source reviewer may not see required unverified HOLD warning')


def inspect_page(name, html):
    """Expose pure per-page audit for independently synthetic adversarial QA."""
    need(type(name) is str and r44.allowed(name) and name != 'review-manifest.json',
         'unsafe private review page name')
    need(type(html) is str and html.startswith('<!doctype html>') and
         html.endswith('</html>\n') and '\x00' not in html,
         'changed outer page envelope')
    page = _Page()
    try:
        page.feed(html)
        page.close()
    except (AssertionError, UnicodeError, TypeError) as exc:
        raise SemanticHold('unparseable private HTML') from exc
    page.assert_safe()
    return tuple(page.links)


def audit_private_zip_html(archive, *, trusted_r42_sha256, trusted_r43_sha256,
                           expected=EXPECTED):
    """Validate complete R44 ZIP and safe, exact offline link topology.

    The two trust pins must originate OUTSIDE the package. A machine CI run
    may only confirm internal consistency; it cannot prove reviewer identity,
    actual source reading, clinical safety, editorial clearance or QD PASS.
    """
    try:
        manifest = r44.verify_private_zip(
            archive, trusted_r42_sha256=trusted_r42_sha256,
            trusted_r43_sha256=trusted_r43_sha256, expected=expected)
    except (r44.PrivateZipHold, ValueError, TypeError, KeyError) as exc:
        raise SemanticHold('R44 underlying source evidence is not trusted') from exc
    source = manifest['source_R43_manifest']
    names = set(source['files'])
    articles = {n for n in names if n.startswith('articles/')}
    need(len(articles) == expected[0] + expected[1] and
         names == articles | {'index.html', 'global-source-variants.html'},
         'article/tool and global-source page coverage lost')
    with ZipFile(BytesIO(archive), 'r') as z:
        links = {name: inspect_page(name, z.read(name).decode('utf-8'))
                 for name in sorted(names)}
    required_index = articles | {'global-source-variants.html'}
    actual_index = links['index.html']
    need(len(actual_index) == len(required_index) and
         set(actual_index) == required_index and
         len(actual_index) == len(set(actual_index)),
         'index omits, duplicates, externally links or misroutes a dossier')
    for name in articles:
        need(links[name] == ('../index.html',),
             'article/tool has an unsafe or missing private back-link')
    need(links['global-source-variants.html'] == ('index.html',),
         'shared-source page has an unsafe or missing index back-link')
    report = {
        'schema_version': 1,
        'issue': 136,
        'release_state': 'HOLD',
        'machine_authority': AUTHORITY,
        'parent_R44_fingerprint_sha256': manifest['fingerprint_sha256'],
        'parent_R42_fingerprint_sha256': trusted_r42_sha256,
        'parent_R43_fingerprint_sha256': trusted_r43_sha256,
        'counts': manifest['counts'],
        'pages_checked': len(names),
        'article_and_tool_pages_checked': len(articles),
        'global_shared_source_page_checked': True,
        'private_local_links_checked': sum(map(len, links.values())),
        'external_or_active_links_allowed': False,
        'human_review_started': False,
        **{flag: False for flag in FLAGS},
    }
    report['fingerprint_sha256'] = sha(canonical(report))
    return report
