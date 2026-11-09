#!/usr/bin/env python3
"""R243: source-only active-markup and deceptive URL hard hold.

The authenticated renderer is a separate boundary. Article source HTML must not
carry executable markup, event listeners, form submissions, URL scheme tricks,
or covert third-party loads. This screen does NOT approve any source, safety
claim, external link, WordPress export, product, transaction or publication.
R238/R239/R242 remain separate required citation and tokenizer gates.
"""
from __future__ import annotations

import hashlib
import html
import re
from html.parser import HTMLParser

HOLD = 'DRAFT_HARD_HOLD'
SAFE_SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
CITE = re.compile(r'\{\{cite:[a-z0-9]+(?:-[a-z0-9]+)*\}\}')
# Trusted article content uses frozen {{link:...}} token resolution. These raw
# HTML surfaces would bypass that path or create invisible browser behavior.
ACTIVE_TAGS = frozenset(('script', 'iframe', 'object', 'embed', 'applet', 'form',
    'input', 'button', 'select', 'textarea', 'base', 'meta', 'link', 'portal',
    'frameset', 'frame', 'svg:script', 'foreignobject', 'animate',
    'style', 'template', 'noscript', 'video', 'audio',
    'animatetransform', 'animatemotion', 'set'))
ACTIVE_ATTRIBUTES = frozenset(('srcdoc', 'formaction', 'ping', 'autofocus',
    'form', 'formmethod', 'formenctype', 'formtarget', 'formnovalidate',
    'srcset', 'imagesrcset', 'sandbox', 'nonce', 'integrity', 'is'))
URL_ATTRIBUTES = frozenset(('href', 'src', 'xlink:href', 'action', 'poster',
    'background', 'longdesc', 'cite', 'data', 'itemid', 'usemap'))
ALLOWED_SCHEMES = frozenset(('https', 'http', 'mailto', 'tel'))
REMOTE_RESOURCE_ATTRIBUTES = frozenset(('src', 'poster', 'background', 'data',
    'xlink:href'))
SCHEME = re.compile(r'^([a-z][a-z0-9+.-]*):', re.I)
PERCENT_SCHEME = re.compile(r'^[a-z][a-z0-9+.-]*(?:%0[0-9adf]|%1[0-9a-f]|%2[0-9]|%3a)', re.I)
DANGEROUS_STYLE = re.compile(r'(?:url\s*\(|@import\b|expression\s*\(|-moz-binding\b|\\)', re.I)


def safe_url(value: str, name: str) -> None:
    """Protect authored URLs from browser scheme normalization and redirects.

    Neither successful parsing nor an allowed http(s) scheme establishes link
    provenance. That remains in the independent 244-row source review docket.
    """
    if type(value) is not str or not value.strip():
        raise ValueError('R243 empty URL: ' + name)
    # HTMLParser decodes character references in attributes; canonicalize once
    # more for conservative defense against subsequent DOM/template decoding.
    raw = html.unescape(value)
    if any(ord(ch) <= 32 or ord(ch) == 127 for ch in raw.strip(' \t\r\n\f')):
        raise ValueError('R243 whitespace/control inside URL: ' + name)
    url = raw.strip()
    if url.startswith('//') or url.startswith('\\\\'):
        raise ValueError('R243 protocol-relative or backslash URL: ' + name)
    if '\\' in url:
        raise ValueError('R243 ambiguous backslash URL: ' + name)
    if PERCENT_SCHEME.match(url):
        raise ValueError('R243 encoded URL scheme: ' + name)
    matched = SCHEME.match(url)
    if matched and matched.group(1).lower() not in ALLOWED_SCHEMES:
        raise ValueError('R243 executable or unreviewed URL scheme: ' + name)
    if matched and name in REMOTE_RESOURCE_ATTRIBUTES:
        raise ValueError('R243 unreviewed remote resource loading: ' + name)
    if '%' in url[:15] and ':' in html.unescape(url):
        raise ValueError('R243 ambiguous URL encoding: ' + name)


class ActiveMarkupInspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = 0
        self.url_attrs = 0
        self.raw_links = 0
        self.external_links = 0

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_starttag(self, tag, attrs):
        self.tags += 1
        tag = tag.lower()
        if tag in ACTIVE_TAGS:
            raise ValueError('R243 active authored HTML element: ' + tag)
        # The separate R242 gate rejects syntactically ambiguous raw attributes
        # and decoded-value mismatches. This gate rejects their dangerous meaning.
        found = set()
        values = {}
        for name, value in attrs:
            key = name.lower()
            if key in found and (key in URL_ATTRIBUTES or key in ACTIVE_ATTRIBUTES or
                                 key in ('target', 'rel', 'style')):
                raise ValueError('R243 duplicate browser-behavior attribute: ' + key)
            found.add(key)
            values[key] = value
            if key.startswith('on') and len(key) > 2 or key.startswith(('v-on:', 'x-on:', '@')):
                raise ValueError('R243 executable event attribute: ' + key)
            if key in ACTIVE_ATTRIBUTES:
                raise ValueError('R243 interactive/bypass attribute: ' + key)
            if key in URL_ATTRIBUTES:
                safe_url(value, key)
                self.url_attrs += 1
                # SVG 2 places fetchable resource references in ordinary href,
                # not just xlink:href. A generic non-anchor element can also
                # acquire such behavior in embedded markup. Without a reviewed
                # asset manifest, fail closed on every non-navigation href that
                # is not a same-document fragment. This does not rewrite or
                # approve original contributor citations or source records.
                if key in ('href', 'xlink:href') and tag not in ('a', 'area'):
                    reference = html.unescape(value).strip()
                    if not re.fullmatch(r'#[A-Za-z_][\\w:.-]*', reference):
                        raise ValueError('R244 nonnavigation href loads unreviewed resource: ' + tag)
                if key == 'href' and tag in ('a', 'area'):
                    self.raw_links += 1
                    if SCHEME.match(value.strip()):
                        self.external_links += 1
            if key == 'style' and value is not None and DANGEROUS_STYLE.search(value):
                raise ValueError('R243 external or executable CSS: style')
        if values.get('target', '').lower() == '_blank':
            rel = (values.get('rel') or '').lower().split()
            if not {'noopener', 'noreferrer'}.issubset(set(rel)):
                raise ValueError('R243 unsafe new-tab link target')


def check_active_markup(body: str) -> dict:
    if type(body) is not str:
        raise ValueError('R243 source must be text')
    scan = ActiveMarkupInspector()
    scan.feed(body)
    scan.close()
    return {'state': HOLD, 'tags': scan.tags, 'raw_url_attributes': scan.url_attrs,
            'raw_links': scan.raw_links, 'external_raw_links_not_source_approved': scan.external_links,
            'release_authorized': False, 'source_review_approved': False,
            'independent_qd_pass': False, 'medical_safety_verified': False,
            'merchant_approved': False, 'human_review_required': True}


def audit_active_markup_custody(root, roster, safe_read) -> dict:
    if type(roster) is not list or len(roster) != 35:
        raise ValueError('R243 original 35-article roster required')
    seen, receipts, total, links = set(), [], 0, 0
    for index, article in enumerate(roster, 1):
        if type(article) is not dict or type(article.get('n')) is not int or article['n'] != index:
            raise ValueError('R243 article identity/order drift')
        slug = article.get('slug')
        if type(slug) is not str or not SAFE_SLUG.fullmatch(slug) or slug in seen:
            raise ValueError('R243 duplicate or unsafe article slug')
        seen.add(slug)
        raw = safe_read(root, 'content/articles/' + slug + '.body.html')
        if type(raw) is not bytes:
            raise ValueError('R243 source reader must return bytes')
        result = check_active_markup(raw.decode('utf-8', 'strict'))
        total += len(CITE.findall(raw.decode('utf-8', 'strict')))
        links += result['raw_links']
        receipts.append(f'{index}:{slug}:{hashlib.sha256(raw).hexdigest()}')
    return {'state': HOLD, 'article_count': len(seen), 'citation_count': total,
            'raw_link_count': links,
            'receipt_sha256': hashlib.sha256('\n'.join(receipts).encode('utf-8')).hexdigest(),
            'release_authorized': False, 'source_review_approved': False,
            'independent_qd_pass': False, 'medical_safety_verified': False,
            'merchant_approved': False, 'human_review_required': True}
