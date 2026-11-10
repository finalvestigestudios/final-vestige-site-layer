#!/usr/bin/env python3
"""Fail-closed DOM-presence admission for additive WordPress Page 6 candidates.

The byte-level preservation gate verifies raw custody; this parser rejects a
preserved footprint that has been placed in HTML comments, templates, or hidden
from keyboard and assistive-technology access. This static parser cannot prove
computed CSS visibility, actual WordPress rendering, or Jetpack confirmation.
"""
from collections import Counter
from html.parser import HTMLParser
import re

_BLOCKED = {'template', 'script', 'style'}
_HIDE = re.compile(r'(?:^|;)\s*(?:display\s*:\s*none\b|visibility\s*:\s*(?:hidden|collapse)\b|content-visibility\s*:\s*hidden\b)', re.I)
_VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}


class CustodyHTMLParser(HTMLParser):
    """Count elements only when present in meaningful, exposed HTML DOM."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.margin_indices = []
        self.jetpack_count = 0
        self.focus_links = 0
        self.chapter_ids = Counter()
        self.root_count = 0

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs)
        if tag not in _VOID:
            self.handle_endtag(tag)

    def _start(self, tag, attrs):
        attrs = dict(attrs)
        bits = (attrs.get('class') or '').split()
        style = attrs.get('style') or ''
        is_hidden = (tag in _BLOCKED or 'hidden' in attrs or 'inert' in attrs
                     or (attrs.get('aria-hidden') or '').lower() == 'true'
                     or bool(_HIDE.search(style)))
        blocked = is_hidden or (self.stack[-1][1] if self.stack else False)
        if not blocked:
            if tag == 'span' and 'fv-margin-strip__item' in bits:
                match = re.search(r'--i\s*:\s*(\d+)', style)
                self.margin_indices.append(int(match.group(1)) if match else None)
            if tag == 'div' and 'wp-block-jetpack-subscriptions' in bits:
                self.jetpack_count += 1
            if tag == 'a' and attrs.get('href') == 'https://finalvestige.com/focus/':
                self.focus_links += 1
            if attrs.get('id'):
                self.chapter_ids[attrs['id']] += 1
            if 'data-fv-home-flagship' in attrs:
                self.root_count += 1
        if tag not in _VOID:
            self.stack.append((tag, blocked))

    def handle_endtag(self, tag):
        # HTMLParser does not repair malformed nesting. End all matching
        # ancestors together; full browser DOM inspection remains required.
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def evaluate_dom(html: str, manifest: dict) -> dict:
    parser = CustodyHTMLParser()
    parser.feed(html)
    parser.close()
    expected = list(range(manifest['record_count']))
    errors = []
    if parser.margin_indices != expected:
        errors.append(f'Exposed Margins order/count invalid: got {len(parser.margin_indices)}, expected {len(expected)}')
    if parser.jetpack_count != 1:
        errors.append(f'Exposed native Jetpack block count invalid: {parser.jetpack_count}; expected 1')
    if parser.focus_links < manifest['focus_href_min_count']:
        errors.append(f'Exposed exact Focus links insufficient: {parser.focus_links}')
    for key in manifest['required_chapter_ids']:
        if parser.chapter_ids[key] != 1:
            errors.append(f'Exposed chapter id {key}: {parser.chapter_ids[key]}; expected exactly 1')
    if parser.root_count != 1:
        errors.append(f'Exposed flagship root count invalid: {parser.root_count}; expected 1')
    return {
        'dom_gate': 'PASS' if not errors else 'HOLD',
        'errors': errors,
        'exposed_margin_count': len(parser.margin_indices),
        'exposed_jetpack_blocks': parser.jetpack_count,
        'exposed_focus_links': parser.focus_links,
        'release_approved': False,
        'limitations': 'Static DOM only; computed styles, JS, WordPress and Jetpack require independent hosted/browser acceptance.'
    }
