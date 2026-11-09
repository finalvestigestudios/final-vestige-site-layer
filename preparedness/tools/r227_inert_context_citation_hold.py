#!/usr/bin/env python3
"""R227: reject safety/citation markup rendered only in inert or conditional HTML.

Read-only companion to R226. It cannot determine computed CSS, execute JavaScript,
verify external sources, or authorize publication; all successful reads stay on HOLD.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import re

HOLD = 'DRAFT_HARD_HOLD'
WARNING = 'Independent safety/source and QD verification pending'
SOURCE_ID = re.compile(r'src-([1-9][0-9]*)\Z')
VOID = frozenset(('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                  'link', 'meta', 'param', 'source', 'track', 'wbr'))
# These containers never provide reliably visible, interactive source/disclosure
# material to an ordinary reading surface. <noscript> is conditional on JS.
INERT = frozenset(('template', 'noscript', 'head', 'script', 'style',
                   'iframe', 'object', 'canvas', 'svg', 'math', 'select',
                   'textarea', 'audio', 'video'))
CRITICAL = frozenset(('pa-body', 'pa-sources', 'pa-review', 'pa-cite'))
# R228: source/citation/review evidence cannot be hidden INSIDE an otherwise
# visible semantic block. Unrelated decorative body templates remain allowed.
CRITICAL_DESCENDANTS = frozenset(('pa-sources', 'pa-review', 'pa-cite'))


# Conservative, known SVG/MathML foreign-content tags: unknown self-closing
# names remain a HARD HOLD instead of guessing HTML namespace integration.
FOREIGN_SELF_CLOSING = frozenset((
    'svg', 'math', 'path', 'circle', 'rect', 'ellipse', 'line', 'polyline',
    'polygon', 'use', 'g', 'defs', 'stop', 'lineargradient', 'radialgradient',
    'clippath', 'mask', 'filter', 'fegaussianblur',
    'mi', 'mn', 'mo', 'mrow', 'mspace'))
# These SVG/MathML integration points can switch descendants back to HTML;
# e.g. <svg><foreignObject><template/></foreignObject></svg> must be rejected.
HTML_INTEGRATION_POINT = frozenset(('foreignobject', 'desc', 'title', 'annotation-xml'))


class _Visibility(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.sources = Counter()
        self.visible_fragments = []
        self.citation_markers = 0
        self.critical_seen = Counter()

    def _conditional(self, tag, attrs):
        if tag in INERT:
            return tag
        if tag == 'dialog' and 'open' not in attrs:
            return 'dialog without open'
        if tag == 'details' and 'open' not in attrs:
            return 'details without open'
        return None

    def handle_startendtag(self, tag, attrs):
        # WHATWG: in HTML, <template/> and <script/> are OPEN elements, not
        # empty elements. HTMLParser emits a synthetic start/end pair instead.
        # Treat ambiguous non-void slash syntax as a hard error, and retain
        # the opening frame so later source/review material cannot look visible.
        # Void HTML tags and foreign SVG/MathML self-closing tags are valid.
        tag = tag.lower()
        foreign = tag in FOREIGN_SELF_CLOSING and (
            tag in ('svg', 'math') or (
                any(f['tag'] in ('svg', 'math') for f in self.stack)
                and not any(f['tag'] in HTML_INTEGRATION_POINT for f in self.stack)))
        self.handle_starttag(tag, attrs)
        if tag in VOID:
            return
        if foreign:
            self.handle_endtag(tag)
        else:
            self.errors.append('non-void HTML trailing solidus: ' + tag)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        a = {str(k).lower(): (v if v is not None else '') for k, v in attrs if k}
        classes = set(a.get('class', '').split())
        ident = a.get('id', '')
        source = SOURCE_ID.fullmatch(ident)
        roles = CRITICAL & classes
        is_critical = bool(roles) or source is not None
        conditional = self._conditional(tag, a)
        ancestors = [f['conditional'] for f in self.stack if f['conditional']]
        # R227 checked only a critical element beginning INSIDE inert markup.
        # R228 closes the inverse case: a visible <li id="src-1"> whose only
        # source anchor sits inside a <template>, closed <details>, etc.
        if conditional and any(f['roles'] & CRITICAL_DESCENDANTS for f in self.stack):
            self.errors.append('inert/conditional descendant of bibliography, citation or review')
        # Catch even unclassified citation-target links hidden in body markup.
        if tag == 'a' and ancestors and re.fullmatch(r'#src-[1-9][0-9]*', a.get('href', '')):
            self.errors.append('source-fragment hyperlink in inert/conditional context')
        if is_critical:
            if conditional or ancestors:
                self.errors.append('source, citation, body or review in inert/conditional context')
            for cls in (CRITICAL & classes):
                self.critical_seen[cls] += 1
            if source:
                self.sources[int(source.group(1))] += 1
            if 'pa-cite' in classes:
                self.citation_markers += 1
        self.stack.append({'tag': tag, 'conditional': conditional,
                           'critical': is_critical, 'roles': roles})
        if tag in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in VOID:
            return
        target = next((i for i in range(len(self.stack) - 1, -1, -1)
                       if self.stack[i]['tag'] == tag), None)
        if target is None:
            if any(f['critical'] for f in self.stack):
                self.errors.append('orphan closing tag inside critical material')
            return
        # Unlike HTMLParser's permissive stack repair, closing a parent must
        # not silently swallow an unclosed citation, source, or review element.
        if any(f['critical'] for f in self.stack[target + 1:]):
            self.errors.append('critical element closed by ancestor recovery')
        del self.stack[target:]

    def handle_data(self, data):
        if not any(f['conditional'] for f in self.stack):
            self.visible_fragments.append(data)


def verify_inert_contexts(page: str, expected_order: list[str]) -> dict:
    """Fail closed on invisible citations and reviews; cannot issue QD PASS."""
    if not isinstance(page, str) or type(expected_order) is not list or not all(
        isinstance(x, str) for x in expected_order
    ) or len(expected_order) != len(set(expected_order)):
        raise ValueError('R227 invalid page or source-order contract')
    view = _Visibility()
    view.feed(page)
    view.close()
    if any(f['critical'] for f in view.stack):
        view.errors.append('unclosed critical element')
    required = set(range(1, len(expected_order) + 1))
    if set(view.sources) != required or any(v != 1 for v in view.sources.values()):
        view.errors.append('source targets absent, duplicated, or unbound')
    if view.critical_seen['pa-body'] != 1 or view.critical_seen['pa-sources'] != 1 or view.critical_seen['pa-review'] != 1:
        view.errors.append('body/source/review semantic containers missing or duplicated')
    # This is a separate browser-context test; R226 verifies the exact marker
    # ordinals/URLs, but we also reject missing markers on cited articles.
    if required and not view.citation_markers:
        view.errors.append('missing citation elements')
    visible_text = ' '.join(' '.join(view.visible_fragments).split())
    if WARNING not in visible_text:
        view.errors.append('pending warning exists only in conditional/inert markup or is missing')
    if view.errors:
        raise ValueError('R227 conditional DOM: ' + '; '.join(sorted(set(view.errors))))
    return {'state': HOLD, 'source_targets': len(required),
            'conditional_contexts_rejected': True, 'release_authorized': False}
