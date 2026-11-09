#!/usr/bin/env python3
"""R240: fail-closed HTML-character-reference guard for citation visibility attributes.

This is an independent syntactic guard, not an HTML5 browser proof, a source
adjudication, a medical-safety clearance, or a publishing authorization.
R238's regex-based hidden-element check can miss browser-decoded attribute
values such as aria-hidden="tr&#117;e" and style="display:&#110;one".
"""
from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser

HOLD = 'DRAFT_HARD_HOLD'
CITE = re.compile(r'\{\{cite:[a-z0-9]+(?:-[a-z0-9]+)*\}\}')
SENSITIVE = frozenset(('aria-hidden', 'style', 'class', 'id'))
ATTR = re.compile(r'''(?<![\w:-])(aria-hidden|style|class|id)\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)''', re.I)
CHAR_REF = re.compile(r'&(?:\#[xX][0-9a-fA-F]+;?|\#[0-9]+;?|[A-Za-z][A-Za-z0-9]+;?)')
TAG = re.compile(r'^\s*<\s*([A-Za-z][\w:-]*)\b', re.I)
SAFE_SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


class AttributeEntityInspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = 0
        self.sensitive = 0
        self.guarded = 0

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_starttag(self, tag, attrs):
        self.tags += 1
        raw = self.get_starttag_text()
        if raw is None or not TAG.match(raw):
            raise ValueError('R240 malformed opening tag')
        # HTMLParser has browser-like entity decoding of attribute *values*;
        # its raw spelling is used to reject obfuscated visibility selectors.
        # Refuse duplicate sensitive names: browsers and parsers can disagree.
        names = [name.lower() for name, _ in attrs]
        for key in SENSITIVE:
            if names.count(key) > 1:
                raise ValueError('R240 ambiguous duplicate visibility attribute: ' + key)
        for match in ATTR.finditer(raw):
            self.sensitive += 1
            name, token = match.groups()
            if CHAR_REF.search(token):
                self.guarded += 1
                raise ValueError('R240 encoded visibility-sensitive attribute: ' + name.lower())
        # HTMLParser can normalize values before caller sees them; ensure a raw
        # visibility attribute with a reference cannot slip through ATTR because
        # of unexpected quoting/spacing or a malformed parser edge case.
        if CHAR_REF.search(raw) and any(name in SENSITIVE for name in names):
            seen = {m.group(1).lower() for m in ATTR.finditer(raw)}
            if any(name in SENSITIVE and name not in seen for name in names):
                raise ValueError('R240 ambiguous encoded visibility attribute syntax')


def check_html_attribute_entities(body: str) -> dict:
    if type(body) is not str:
        raise ValueError('R240 body must be UTF-8 text')
    p = AttributeEntityInspector()
    # HTMLParser treats script/style contents as opaque; R238 is responsible
    # for rejecting citations hidden there, and R239 handles self-closing HTML.
    p.feed(body)
    p.close()
    return {'state': HOLD, 'tags_scanned': p.tags,
            'visibility_attribute_occurrences': p.sensitive,
            'release_authorized': False, 'independent_qd_pass': False,
            'source_review_approved': False, 'medical_safety_verified': False}


def audit_attribute_entity_custody(root, roster, safe_read) -> dict:
    if type(roster) is not list or len(roster) != 35:
        raise ValueError('R240 exact original 35-article roster required')
    slugs, fingerprints, count = set(), [], 0
    for number, entry in enumerate(roster, 1):
        if type(entry) is not dict or type(entry.get('n')) is not int or entry['n'] != number:
            raise ValueError('R240 roster order invalid')
        slug = entry.get('slug')
        if type(slug) is not str or not SAFE_SLUG.fullmatch(slug) or slug in slugs:
            raise ValueError('R240 malformed/duplicate source slug')
        slugs.add(slug)
        raw = safe_read(root, 'content/articles/' + slug + '.body.html')
        if type(raw) is not bytes:
            raise ValueError('R240 source reader must return bytes')
        body = raw.decode('utf-8', 'strict')
        check_html_attribute_entities(body)
        count += len(CITE.findall(body))
        fingerprints.append(f'{number}:{slug}:{hashlib.sha256(raw).hexdigest()}')
    return {'state': HOLD, 'article_count': 35, 'citation_count': count,
            'human_review_required': True, 'release_authorized': False,
            'independent_qd_pass': False, 'source_review_approved': False,
            'medical_safety_verified': False,
            'receipt_sha256': hashlib.sha256('\n'.join(fingerprints).encode()).hexdigest()}
