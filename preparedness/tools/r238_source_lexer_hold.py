#!/usr/bin/env python3
"""Fail-closed source citation placement lexer. A structural screen, NEVER source approval.

Unlike regex rfind('<') / rfind('>'), quote-aware tokenization cannot be fooled by
'>' inside an attribute or an unterminated HTML comment. Kept separate from R237
so authenticated prior reviewer receipts stay unchanged. Original author HTML is
read-only. Source semantic review and native/browser validation are still required.
"""
from __future__ import annotations
import hashlib
import re

HOLD = 'DRAFT_HARD_HOLD'
CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
TAG_NAME = re.compile(r'\s*(/?)\s*([A-Za-z][A-Za-z0-9:-]*)\b([\s\S]*)\Z')
OPAQUE = frozenset(('script', 'style', 'template', 'noscript', 'textarea',
                    'title', 'iframe', 'noembed', 'noframes', 'xmp', 'plaintext'))
VOID = frozenset(('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                  'link', 'meta', 'param', 'source', 'track', 'wbr'))
HIDDEN_ATTR = re.compile(r'(?i)(?:^|\s)(?:hidden|inert)(?=\s|=|$)')
ARIA_HIDDEN = re.compile(r'(?i)(?:^|\s)aria-hidden\s*=\s*(?:"true"|\'true\'|true)(?=\s|$)')
HIDDEN_STYLE = re.compile(r'(?i)(?:display\s*:\s*none|visibility\s*:\s*hidden)')
END_RAW = {}


def tag_end(markup: str, start: int) -> int:
    """Return ending >, ignoring all > inside quoted attributes."""
    quote = None
    for j in range(start + 1, len(markup)):
        char = markup[j]
        if quote:
            if char == quote:
                quote = None
        elif char in ('"', "'"):
            quote = char
        elif char == '>':
            return j
    raise ValueError('R238 unterminated or quoted HTML tag')


def visible_citations(body: str):
    """Enumerate (offset, source ID), rejecting nonreader source placements.

    This is a deliberately conservative *source syntax* gate, not an HTML5
    conformance parser. Dangerous ambiguities fail rather than being approved.
    Full export/browser and source-adjudication gates remain independently held.
    """
    if type(body) is not str:
        raise ValueError('R238 body must be UTF-8 text')
    stack = []  # (name, is_hidden); only relevant to citation visibility
    citations = []
    i, length = 0, len(body)
    while i < length:
        if body.startswith('<!--', i):
            end = body.find('-->', i + 4)
            if end < 0:
                raise ValueError('R238 unterminated comment')
            if '{{cite:' in body[i:end+3]:
                raise ValueError('R238 citation in HTML comment')
            i = end + 3
            continue
        if body[i] == '<':
            if body.startswith('<!', i) or body.startswith('<?', i):
                raise ValueError('R238 unsupported declaration or processing instruction')
            end = tag_end(body, i)
            raw = body[i + 1:end]
            if '{{cite:' in raw:
                raise ValueError('R238 citation in HTML tag or attribute')
            match = TAG_NAME.fullmatch(raw)
            if not match:
                raise ValueError('R238 malformed HTML tag')
            closing, name, attributes = match.groups()
            name = name.lower()
            if closing:
                if attributes.strip():
                    raise ValueError('R238 ambiguous closing tag')
                for idx in range(len(stack) - 1, -1, -1):
                    if stack[idx][0] == name:
                        del stack[idx:]
                        break
            else:
                if name == 'plaintext':
                    raise ValueError('R238 plaintext HTML tokenizer mode prohibited')
                hidden = bool(HIDDEN_ATTR.search(attributes) or
                              ARIA_HIDDEN.search(attributes) or
                              HIDDEN_STYLE.search(attributes))
                if name in OPAQUE:
                    closing_pattern = END_RAW.setdefault(name, re.compile(
                        r'</\s*' + re.escape(name) + r'\s*>', re.I))
                    stop = closing_pattern.search(body, end + 1)
                    if not stop:
                        raise ValueError('R238 unterminated nonreader HTML element: ' + name)
                    payload = body[end + 1:stop.start()]
                    if name == 'template' and re.search(r'<\s*template\b', payload, re.I):
                        raise ValueError('R238 nested template requires independent browser review')
                    if '{{cite:' in payload:
                        raise ValueError('R238 citation inside nonreader HTML element: ' + name)
                    i = stop.end()
                    continue
                if name not in VOID and not raw.rstrip().endswith('/'):
                    stack.append((name, hidden))
            i = end + 1
            continue
        if body.startswith('{{cite:', i):
            m = CITE.match(body, i)
            if not m:
                raise ValueError('R238 malformed citation in reader text')
            if any(is_hidden for _, is_hidden in stack):
                raise ValueError('R238 citation in hidden/aria-hidden/inert subtree')
            citations.append((i, m.group(1)))
            i = m.end()
            continue
        i += 1
    if body.count('{{cite:') != len(citations):
        raise ValueError('R238 citation occurrence mismatch')
    return citations


def audit_source_visibility(root, roster, safe_read):
    if type(roster) is not list or len(roster) != 35:
        raise ValueError('R238 exact 35 article roster required')
    total, receipts, slugs = 0, [], set()
    for n, entry in enumerate(roster, 1):
        if type(entry) is not dict or type(entry.get('n')) is not int or entry['n'] != n:
            raise ValueError('R238 article order invalid')
        slug = entry.get('slug')
        if type(slug) is not str or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in slugs:
            raise ValueError('R238 duplicate or malformed article slug')
        slugs.add(slug)
        raw = safe_read(root, 'content/articles/' + slug + '.body.html')
        body = raw.decode('utf-8', 'strict')
        citations = visible_citations(body)
        total += len(citations)
        receipt = hashlib.sha256(repr(citations).encode('utf-8')).hexdigest()
        receipts.append(f'{n}:{slug}:{receipt}')
    return {'state': HOLD, 'article_count': 35, 'citation_count': total,
            'source_approved': False, 'medical_safety_verified': False,
            'independent_qd_pass': False, 'release_authorized': False,
            'human_review_required': True,
            'receipt_sha256': hashlib.sha256('\n'.join(receipts).encode('utf-8')).hexdigest()}
