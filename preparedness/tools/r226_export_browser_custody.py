#!/usr/bin/env python3
"""R226: read-only browser-semantics citation/disclosure check for 41 draft exports.

This does not execute JavaScript or render CSS; it does not authorize publishing,
validate medical advice, or establish that an external source actually supports a
claim. It rejects DOM-level tricks that exact HTML-string checks cannot see.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import re

HOLD = 'DRAFT_HARD_HOLD'
SOURCE_ID = re.compile(r'src-([1-9][0-9]*)\Z')
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'}
HIDE_RE = re.compile(r'(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse)|opacity\s*:\s*0(?:\.0*)?\b|content-visibility\s*:\s*hidden|font-size\s*:\s*0(?:px|em|rem|%)?\b)', re.I)
WARNING = 'Independent safety/source and QD verification pending'


class _ExportDOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[dict] = []
        self.ids: Counter = Counter()
        self.errors: list[str] = []
        self.citations: Counter = Counter()
        self.sources: dict[int, list[str]] = {}
        self.body_count = 0
        self.warning_seen = False
        self.warning_parts: list[str] = []
        self.review_found = False
        self.source_section_found = False
        self.review_count = 0
        self.source_section_count = 0
        self.hidden_source_count = 0
        self.active_source: list[int] = []

    def handle_startendtag(self, tag, attrs):
        # WHATWG: in HTML, <template/> and <script/> are OPEN elements, not
        # empty elements. HTMLParser emits a synthetic start/end pair instead.
        # Treat ambiguous non-void slash syntax as a hard error, and retain
        # the opening frame so later source/review material cannot look visible.
        # Void HTML tags and foreign SVG/MathML self-closing tags are valid.
        tag = tag.lower()
        foreign = tag in ('svg', 'math') or any(
            frame['tag'] in ('svg', 'math') for frame in self.stack)
        self.handle_starttag(tag, attrs)
        if tag in VOID:
            return
        if foreign:
            self.handle_endtag(tag)
        else:
            self.errors.append('non-void HTML trailing solidus: ' + tag)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        keys = [k.lower() for k, _ in attrs if k]
        if len(keys) != len(set(keys)):
            self.errors.append('duplicate HTML attribute')
        a = {k.lower(): (v if v is not None else '') for k, v in attrs if k}
        if tag == 'base':
            self.errors.append('base href changes fragment/link navigation')
        if tag == 'meta' and a.get('http-equiv', '').strip().lower() == 'refresh':
            self.errors.append('meta refresh replaces source navigation')
        ancestor_hidden = bool(self.stack and self.stack[-1]['hidden'])
        hidden = (ancestor_hidden or 'hidden' in a or 'inert' in a
                  or a.get('aria-hidden', '').strip().lower() == 'true'
                  or HIDE_RE.search(a.get('style', '')) is not None)
        ident = a.get('id', '')
        if ident:
            self.ids[ident] += 1
            if self.ids[ident] > 1:
                self.errors.append('duplicate HTML id: ' + ident)
        classes = set(a.get('class', '').split())
        in_source_section = ('pa-sources' in classes or any(
            f['in_sources'] for f in self.stack))
        in_review = 'pa-review' in classes or any(f['in_review'] for f in self.stack)
        in_citation = 'pa-cite' in classes or any(f['in_citation'] for f in self.stack)
        if 'pa-sources' in classes:
            self.source_section_count += 1
            if in_review:
                self.errors.append('nested source list inside review')
            if hidden:
                self.errors.append('hidden source section')
            self.source_section_found = True
        if 'pa-review' in classes:
            self.review_count += 1
            if in_source_section:
                self.errors.append('nested review record inside source section')
            self.review_found = True
            if hidden:
                self.errors.append('hidden review/safety record')
        if 'pa-body' in classes and ident == 'pa-main':
            self.body_count += 1
            if hidden:
                self.errors.append('hidden article body')
        source_match = SOURCE_ID.fullmatch(ident) if ident else None
        source_num = int(source_match.group(1)) if source_match else None
        if source_num is not None:
            if tag != 'li' or not in_source_section:
                self.errors.append('citation anchor outside source bibliography')
            if hidden:
                self.hidden_source_count += 1
                self.errors.append('hidden bibliography entry')
            self.sources.setdefault(source_num, [])
        active_source = source_num if source_num is not None else (
            self.stack[-1]['active_source'] if self.stack else None)
        if tag == 'a':
            href = a.get('href', '')
            if re.match(r'^\s*(?:javascript|data|vbscript)\s*:', href, re.I):
                self.errors.append('unsafe link scheme')
            if in_citation:
                if hidden:
                    self.errors.append('hidden citation marker')
                if re.fullmatch(r'#src-[1-9][0-9]*', href):
                    self.citations[int(href[5:])] += 1
                else:
                    self.errors.append('citation target not a source anchor')
            if active_source is not None:
                if hidden:
                    self.errors.append('hidden source hyperlink')
                self.sources.setdefault(active_source, []).append(href)
        # A style tag inside source/review markup can override visual disclosure.
        if tag == 'style' and (in_source_section or in_review):
            self.errors.append('CSS override inside source/review section')
        # Disallow concealed text in visible warning/review path.
        self.stack.append({'tag': tag, 'hidden': hidden, 'in_sources': in_source_section,
                           'in_review': in_review, 'in_citation': in_citation,
                           'active_source': active_source})
        if tag in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        tag = tag.lower()
        for j in range(len(self.stack) - 1, -1, -1):
            if self.stack[j]['tag'] == tag:
                del self.stack[j:]
                return
        # HTML fragment wrappers can include orphan end tags: fail closed.
        if tag not in VOID:
            self.errors.append('unexpected closing tag: ' + tag)

    def handle_data(self, data):
        if (self.stack and not self.stack[-1]['hidden']
                and not any(f['tag'] in ('script', 'style', 'template', 'head') for f in self.stack)):
            self.warning_parts.append(data)


def verify_export(page: str, order: list[str], meta: dict, library, expected_body: str) -> dict:
    """Verify rendered DOM citation identities, target visibility, and disclosure.

    `library.source_for(meta, sid)` remains the independently bound producer's
    article-scoped reading selection; this module does not approve that reading.
    """
    if not isinstance(page, str) or not isinstance(expected_body, str):
        raise ValueError('non-text HTML export')
    if not isinstance(order, list) or not all(isinstance(s, str) for s in order):
        raise ValueError('invalid source sequence')
    dom = _ExportDOM()
    dom.feed(page)
    dom.close()
    if dom.stack:
        # HTMLParser is permissive; a missing source/review closing tag is not.
        if any(f['in_sources'] or f['in_review'] for f in dom.stack):
            dom.errors.append('unclosed source/review markup')
    if dom.body_count != 1 or dom.source_section_count != 1 or dom.review_count != 1:
        dom.errors.append('missing/duplicated body, source block or review record')
    if WARNING not in ' '.join(' '.join(dom.warning_parts).split()):
        dom.errors.append('no visible pending independent review warning')
    expected_numbers = set(range(1, len(order) + 1))
    if set(dom.sources) != expected_numbers:
        dom.errors.append('missing/extra bibliography targets')
    for n, sid in enumerate(order, 1):
        try:
            expected_url = library.source_for(meta, sid)['url']
        except (KeyError, TypeError) as exc:
            raise ValueError('source selection unavailable: ' + sid) from exc
        if dom.sources.get(n) != [expected_url]:
            dom.errors.append('source URL/ordinal mismatch at #' + str(n))
        expected_mentions = len(re.findall(r'href=["\']#src-' + str(n) + r'["\']', expected_body))
        if dom.citations[n] != expected_mentions or not expected_mentions:
            dom.errors.append('citation occurrence mismatch at #' + str(n))
    if set(dom.citations) != expected_numbers:
        dom.errors.append('missing/extra source citations')
    if dom.errors:
        raise ValueError('R226 DOM integrity: ' + '; '.join(sorted(set(dom.errors))))
    return {'state': HOLD, 'source_targets': len(order), 'citation_mentions': sum(dom.citations.values()),
            'visible_review_warning': True, 'no_duplicate_ids': True}
