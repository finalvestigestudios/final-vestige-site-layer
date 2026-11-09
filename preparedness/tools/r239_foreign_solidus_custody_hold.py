#!/usr/bin/env python3
"""R239: reject HTML non-void '/>' while preserving actual SVG/MathML syntax.

A source-level, fail-closed companion to the pinned R238 citation lexer.
It does not approve citations, author advice, medical safety, or publication.
"""
from __future__ import annotations

import hashlib
import re

HOLD = 'DRAFT_HARD_HOLD'
TAG = re.compile(r'\s*(/?)\s*([A-Za-z][A-Za-z0-9:-]*)\b([\s\S]*)\Z')
VOID = frozenset(('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                  'link', 'meta', 'param', 'source', 'track', 'wbr'))
OPAQUE = frozenset(('script', 'style', 'template', 'noscript', 'textarea',
                    'title', 'iframe', 'noembed', 'noframes', 'xmp'))
SVG_SELF = frozenset(('svg', 'path', 'rect', 'circle', 'ellipse', 'line', 'polyline',
                      'polygon', 'stop', 'use', 'image', 'lineargradient',
                      'radialgradient', 'clippath', 'mask', 'filter', 'feoffset',
                      'fegaussianblur', 'fecolormatrix', 'feblend', 'femerge',
                      'femergenode', 'symbol', 'marker', 'pattern'))
MATH_SELF = frozenset(('math', 'mi', 'mn', 'mo', 'ms', 'mspace', 'mglyph',
                       'malignmark', 'mprescripts', 'none'))
SVG_HTML_INTEGRATION = frozenset(('foreignobject', 'desc', 'title'))
MATH_HTML_INTEGRATION = frozenset(('mtext', 'mi', 'mo', 'mn', 'ms', 'annotation-xml'))
CITE = re.compile(r'\{\{cite:[a-z0-9]+(?:-[a-z0-9]+)*\}\}')


def end_of_tag(body: str, pos: int) -> int:
    """HTML-tag boundary: a greater-than sign inside quotes is not a boundary."""
    quote = None
    for index in range(pos + 1, len(body)):
        char = body[index]
        if quote:
            if char == quote:
                quote = None
        elif char in ('"', "'"):
            quote = char
        elif char == '>':
            return index
    raise ValueError('R239 unterminated quoted tag')


def check_solidus_html(body: str) -> dict:
    """Reject '/>' on HTML non-void elements, including inside SVG integration points.

    This only screens ambiguous self-closing markup; R238 and the exported DOM
    validators independently screen citations, hidden evidence and browser state.
    Foreign SVG/MathML self-closing is accepted only for explicit known tags.
    """
    if type(body) is not str:
        raise ValueError('R239 body must be text')
    stack = []  # tuples (element_name, child_namespace)
    index = 0
    tags = 0
    foreign_void = 0
    while index < len(body):
        pos = body.find('<', index)
        if pos < 0:
            break
        if body.startswith('<!--', pos):
            stop = body.find('-->', pos + 4)
            if stop < 0:
                raise ValueError('R239 unclosed comment')
            index = stop + 3
            continue
        if body.startswith('<!', pos) or body.startswith('<?', pos):
            raise ValueError('R239 unsupported markup declaration')
        end = end_of_tag(body, pos)
        m = TAG.fullmatch(body[pos + 1:end])
        if m is None:
            raise ValueError('R239 malformed tag')
        closing, name, attrs = m.groups()
        name = name.lower()
        tags += 1
        if closing:
            if attrs.strip():
                raise ValueError('R239 malformed closing tag')
            for j in range(len(stack)-1, -1, -1):
                if stack[j][0] == name:
                    del stack[j:]
                    break
            index = end + 1
            continue
        namespace = stack[-1][1] if stack else 'html'
        if namespace == 'html' and name == 'svg':
            own_namespace = 'svg'
        elif namespace == 'html' and name == 'math':
            own_namespace = 'math'
        else:
            own_namespace = namespace
        # If a tag is in foreign content but is an HTML integration point,
        # descendants reenter HTML parsing (not generic SVG/MathML parsing).
        children = own_namespace
        if own_namespace == 'svg' and name in SVG_HTML_INTEGRATION:
            children = 'html'
        if own_namespace == 'math' and name in MATH_HTML_INTEGRATION:
            children = 'html'
        self_closing = attrs.rstrip().endswith('/')
        if self_closing:
            if own_namespace == 'html' and name not in VOID:
                raise ValueError('R239 non-void self-closing HTML tag: ' + name)
            if own_namespace == 'svg' and name not in SVG_SELF:
                raise ValueError('R239 unsafe foreign self-closing SVG tag: ' + name)
            if own_namespace == 'math' and name not in MATH_SELF:
                raise ValueError('R239 unsafe foreign self-closing MathML tag: ' + name)
            if own_namespace != 'html':
                foreign_void += 1
        elif name not in VOID:
            if name in OPAQUE:
                pattern = re.compile(r'</\s*' + re.escape(name) + r'\s*>', re.I)
                match = pattern.search(body, end + 1)
                if match is None:
                    raise ValueError('R239 unclosed raw-text element: ' + name)
                index = match.end()
                continue
            stack.append((name, children))
        index = end + 1
    return {'state': HOLD, 'tags_checked': tags, 'foreign_self_closing': foreign_void,
            'release_authorized': False, 'independent_qd_pass': False,
            'source_review_approved': False, 'medical_safety_verified': False}


def audit_solidus_custody(root, roster, safe_read):
    if type(roster) is not list or len(roster) != 35:
        raise ValueError('R239 exact original roster required')
    receipts, total, seen = [], 0, set()
    for number, article in enumerate(roster, 1):
        if type(article) is not dict or type(article.get('n')) is not int or article['n'] != number:
            raise ValueError('R239 roster order invalid')
        slug = article.get('slug')
        if type(slug) is not str or re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) is None or slug in seen:
            raise ValueError('R239 duplicate/malformed slug')
        seen.add(slug)
        raw = safe_read(root, 'content/articles/' + slug + '.body.html')
        doc = raw.decode('utf-8', 'strict')
        metrics = check_solidus_html(doc)
        total += len(CITE.findall(doc))
        receipts.append(f'{number}:{slug}:{hashlib.sha256(raw).hexdigest()}:{metrics["foreign_self_closing"]}')
    return {'state': HOLD, 'article_count': 35, 'citation_count': total,
            'release_authorized': False, 'independent_qd_pass': False,
            'source_review_approved': False, 'medical_safety_verified': False,
            'human_review_required': True,
            'receipt_sha256': hashlib.sha256('\n'.join(receipts).encode()).hexdigest()}
