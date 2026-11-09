#!/usr/bin/env python3
"""Fail-closed, read-only inspection of an UNAPPROVED family-card preview.

This is NOT a WordPress/browser/medical-safety approval. The original card is not
changed. R248 separately authenticates source originals; this checks only the
proposed reader-copy preview and prohibits accidental commercialization.
"""
from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

HOLD = 'DRAFT_HARD_HOLD'
PREVIEW = 'audits/r249_family_card_reader_disclosure_draft.html'
REQUIRED = (
    'household name', 'household phone number', 'out-of-area contact',
    'out-of-area phone number', 'first meeting place', 'review date',
    'six filled-in fields', 'thirteen filled-in fields', 'excludes seven fields',
    'printed card is lost or shared', 'javascript turned off',
    'interactive form is hidden when javascript is off',
    'written plan at home', 'real browser and print checks',
    'free household-planning resources', 'no paid kit', 'no paid checkout',
)
PROHIBITED_COPY = (
    'only the out-of-area contact', 'nothing is stored',
    'private by design', 'guaranteed safe', 'medically safe',
    'approved for publication', 'form below still works',
    'click here to buy', 'enter payment',
)
PROHIBITED_TAGS = frozenset(
    'script style form input select option textarea iframe object embed '
    'link meta base svg img picture video audio canvas template details '
    'dialog button noscript'.split()
)


class ReaderParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.ids = set()
        self.links = []
        self.text = []
        self.section = 0
        self.headings = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag in PROHIBITED_TAGS:
            self.errors.append('unsafe element: ' + tag)
        keys = [k for k, _ in attrs]
        if len(keys) != len(set(keys)):
            self.errors.append('duplicate attribute')
        for key, value in attrs:
            val = (value or '').strip()
            if key is None or key.lower().startswith('on'):
                self.errors.append('event or malformed attribute')
            if key in ('src', 'srcset', 'style', 'target', 'action', 'formaction', 'hidden', 'contenteditable'):
                self.errors.append('resource/visibility attribute')
            if key in ('class', 'id', 'aria-labelledby', 'aria-label', 'aria-hidden') and '&#' in val:
                self.errors.append('encoded visibility attribute')
            if key == 'aria-hidden' or (key == 'class' and re.search(r'\bhidden\b', val, re.I)):
                self.errors.append('hidden content')
            if key == 'id':
                if val in self.ids:
                    self.errors.append('duplicate id')
                self.ids.add(val)
            if key == 'href':
                self.links.append(val)
                uri = urlsplit(val)
                if uri.scheme or uri.netloc or val != '/preparedness/':
                    self.errors.append('unapproved destination')
        if tag == 'section':
            self.section += 1
        if tag in ('h1', 'h2', 'h3'):
            self.headings.append(tag)
        if tag not in ('br', 'hr', 'wbr'):
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append('unbalanced tags')
        else:
            self.stack.pop()

    def handle_data(self, data):
        self.text.append(data)

    def handle_comment(self, data):
        if any(s in data.lower() for s in ('<script', 'javascript:', '<iframe', 'https://')):
            self.errors.append('active comment payload')


def inspect(markup: str) -> dict:
    if type(markup) is not str or not 400 < len(markup) < 20000 or '\0' in markup:
        raise ValueError('invalid preview size or encoding')
    p = ReaderParser()
    try:
        p.feed(markup)
        p.close()
    except (ValueError, AssertionError) as e:
        raise ValueError('invalid markup parse') from e
    if p.stack:
        p.errors.append('unclosed elements')
    plain = re.sub(r'\s+', ' ', ' '.join(p.text)).strip().lower()
    if p.section != 1 or p.headings != ['h2', 'h3'] or p.ids != {'r249-title'}:
        p.errors.append('reader structure changed')
    if p.links != ['/preparedness/'] or 'aria-labelledby="r249-title"' not in markup:
        p.errors.append('free destination or accessible label changed')
    for phrase in REQUIRED:
        if phrase not in plain:
            p.errors.append('missing disclosure: ' + phrase)
    for phrase in PROHIBITED_COPY:
        if phrase in plain:
            p.errors.append('unsafe assertion: ' + phrase)
    if len(re.findall(r'\b(?:href|src|onclick|onload)\s*=', markup, flags=re.I)) != 1:
        p.errors.append('unexpected link or executable attribute')
    if p.errors:
        raise ValueError('R249 reader disclosure HARD HOLD validation: ' + '; '.join(sorted(set(p.errors))))
    return {
        'state': HOLD, 'issue': 136, 'conversion_issue': 820,
        'tested_scope': 'offline proposed reader-copy markup only',
        'preview_sha256': hashlib.sha256(markup.encode('utf-8')).hexdigest(),
        'visible_free_destinations': ['/preparedness/'],
        'printed_full_fields': 13, 'printed_shorter_fields': 6,
        'excluded_shorter_fields': 7,
        'source_and_medical_safety_approved': False,
        'browser_print_verified': False, 'privacy_certified': False,
        'independent_qd_pass': False, 'commerce_approved': False,
        'release_authorized': False, 'human_review_required': True,
    }


def audit(root: Path, safe_read) -> dict:
    return inspect(safe_read(root, PREVIEW).decode('utf-8', 'strict'))


if __name__ == '__main__':
    import json
    import sys
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    try:
        print(json.dumps(audit(root, lambda r, p: (r/p).read_bytes()), indent=2))
    except (ValueError, OSError, UnicodeError) as exc:
        print(json.dumps({'state': 'INVALID_HARD_HOLD', 'errors': [str(exc)]}))
        sys.exit(3)
