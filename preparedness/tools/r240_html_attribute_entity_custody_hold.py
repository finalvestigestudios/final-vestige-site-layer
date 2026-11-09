#!/usr/bin/env python3
"""R245 revision of R240-R242: preserve valid valueless-attribute separators.

Fail closed on encoded aria-hidden/style/class/id values and ambiguous syntax.
Unlike the original raw regex, text inside unrelated quoted attributes is not
misidentified as another attribute. R242 rejects missing separators, control
characters and parser-value drift. R245 preserves whitespace before a
valueless attribute's next neighbor. Syntactic custody, never human approval.
"""
from __future__ import annotations

import hashlib
import re
from html import unescape
from html.parser import HTMLParser

HOLD = 'DRAFT_HARD_HOLD'
CITE = re.compile(r'\{\{cite:[a-z0-9]+(?:-[a-z0-9]+)*\}\}')
SENSITIVE = frozenset(('aria-hidden', 'style', 'class', 'id'))
CHAR_REF = re.compile(r'&(?:\#[xX][0-9a-fA-F]+;?|\#[0-9]+;?|[A-Za-z][A-Za-z0-9]+;?)')
TAG = re.compile(r'^\s*<\s*([A-Za-z][\w:-]*)\b', re.I)
ATTR_NAME = re.compile(r'[^\s"\'<>/=]+')
SAFE_SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
HTML_SPACE = ' \t\r\n\f'
DISALLOWED_C0 = frozenset(chr(i) for i in (*range(0,9), 11, *range(14,32), 127))


def raw_attributes(raw: str, expected_tag: str) -> list[tuple[str, str | None]]:
    """Read attribute boundaries, not name=value lookalikes inside strings.

    HTMLParser performs structural tokenization; this lexical second view
    retains raw entities in values. Any divergence is a hard hold rather than
    trusting normalization of malformed or browser-ambiguous markup.
    """
    if any(ch in DISALLOWED_C0 for ch in raw):
        raise ValueError('R242 control character in HTML opening tag')
    match = TAG.match(raw)
    if match is None or match.group(1).lower() != expected_tag.lower():
        raise ValueError('R240/R241 malformed opening tag')
    pos = match.end()
    found: list[tuple[str, str | None]] = []
    while pos < len(raw):
        while pos < len(raw) and raw[pos] in HTML_SPACE:
            pos += 1
        if raw[pos:] == '>' or raw[pos:] == '/>':
            return found
        name_match = ATTR_NAME.match(raw, pos)
        if name_match is None:
            raise ValueError('R240/R241 invalid raw attribute boundary')
        name = name_match.group(0).lower()
        name_end = name_match.end()
        pos = name_end
        while pos < len(raw) and raw[pos] in HTML_SPACE:
            pos += 1
        value: str | None = None
        if pos < len(raw) and raw[pos] == '=':
            pos += 1
            while pos < len(raw) and raw[pos] in HTML_SPACE:
                pos += 1
            if pos == len(raw):
                raise ValueError('R240/R241 missing attribute value')
            if raw[pos] in ('"', "'"):
                quote = raw[pos]
                pos += 1
                end = raw.find(quote, pos)
                if end < 0:
                    raise ValueError('R240/R241 unclosed quoted attribute')
                value = raw[pos:end]
                if '<' in value:
                    raise ValueError('R242 malformed less-than in quoted HTML attribute')
                pos = end + 1
            else:
                start = pos
                while pos < len(raw) and not raw[pos] in HTML_SPACE and raw[pos] != '>':
                    if raw[pos] in ('"', "'", '<', '=', chr(96)):
                        raise ValueError('R240/R241 invalid unquoted attribute value')
                    pos += 1
                if start == pos:
                    raise ValueError('R240/R241 blank unquoted attribute')
                value = raw[start:pos]
        else:
            # The whitespace after a valueless attribute belongs to the
            # separator before its neighbor, not to a missing equals sign.
            # Rewind for the strict adjacency check below. R242 otherwise
            # falsely rejects valid `<p data-note class="visible">`.
            pos = name_end
        # HTML requires a space before another attribute. HTMLParser
        # tolerates 'title="x"aria-hidden="false"' and reports both names,
        # so matching names alone is NOT a sufficient browser-safety test.
        if pos < len(raw) and raw[pos] not in HTML_SPACE and raw[pos:] not in ('>', '/>'):
            raise ValueError('R242 missing HTML attribute separator')
        found.append((name, value))
    raise ValueError('R240/R241 unterminated opening tag')


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
        if raw is None:
            raise ValueError('R240/R241 opening tag unavailable')
        tokens = raw_attributes(raw, tag)
        parsed_names = [name.lower() for name, _ in attrs]
        if [name for name, _ in tokens] != parsed_names:
            raise ValueError('R242 HTML parser/raw attribute name mismatch')
        if [(unescape(value) if value is not None else None) for _, value in tokens] != [value for _, value in attrs]:
            raise ValueError('R242 HTML parser/raw attribute decoded value mismatch')
        for name in SENSITIVE:
            if parsed_names.count(name) > 1:
                raise ValueError('R240/R241 ambiguous duplicate visibility attribute: ' + name)
        for name, raw_value in tokens:
            if name not in SENSITIVE:
                continue
            self.sensitive += 1
            if raw_value is not None and CHAR_REF.search(raw_value):
                self.guarded += 1
                raise ValueError('R240/R241 encoded visibility-sensitive attribute: ' + name)


def check_html_attribute_entities(body: str) -> dict:
    if type(body) is not str:
        raise ValueError('R240/R241 body must be UTF-8 text')
    p = AttributeEntityInspector()
    # Independent R238/R239 gates handle opaque script/style bodies and
    # HTML nonvoid solidus behavior respectively.
    p.feed(body)
    p.close()
    return {'state': HOLD, 'tags_scanned': p.tags,
            'visibility_attribute_occurrences': p.sensitive,
            'release_authorized': False, 'independent_qd_pass': False,
            'source_review_approved': False, 'medical_safety_verified': False}


def audit_attribute_entity_custody(root, roster, safe_read) -> dict:
    if type(roster) is not list or len(roster) != 35:
        raise ValueError('R240/R241 exact original 35-article roster required')
    slugs, fingerprints, count = set(), [], 0
    for number, entry in enumerate(roster, 1):
        if type(entry) is not dict or type(entry.get('n')) is not int or entry['n'] != number:
            raise ValueError('R240/R241 roster order invalid')
        slug = entry.get('slug')
        if type(slug) is not str or not SAFE_SLUG.fullmatch(slug) or slug in slugs:
            raise ValueError('R240/R241 malformed/duplicate source slug')
        slugs.add(slug)
        raw = safe_read(root, 'content/articles/' + slug + '.body.html')
        if type(raw) is not bytes:
            raise ValueError('R240/R241 source reader must return bytes')
        body = raw.decode('utf-8', 'strict')
        check_html_attribute_entities(body)
        count += len(CITE.findall(body))
        fingerprints.append(f'{number}:{slug}:{hashlib.sha256(raw).hexdigest()}')
    return {'state': HOLD, 'article_count': 35, 'citation_count': count,
            'human_review_required': True, 'release_authorized': False,
            'independent_qd_pass': False, 'source_review_approved': False,
            'medical_safety_verified': False,
            'receipt_sha256': hashlib.sha256('\n'.join(fingerprints).encode()).hexdigest()}
