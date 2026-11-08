#!/usr/bin/env python3
"""R217: supplemental, fail-closed browser-semantics review of R216 draft HTML.

This source-level gate checks duplicate attributes, global fragment collisions and
visible review language. It cannot substitute for browser/CSS, evidence, QD,
medical/safety review, or native validation/build. HOLD is its only valid state.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
SCHEMA = 'fv-preparedness-r217-transport-semantics-v1'
PARENT_SCHEMA = 'fv-preparedness-r216-draft-exposure-v1'
SCOPES = frozenset(('pa-chips', 'pa-review', 'pa-body', 'pa-sources'))
ASSURANCES = ('qd pass', 'medical safety verified', 'approved for publication',
              'ready to publish', 'publication authorized')
VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())
FRAGMENT = re.compile(r'^#[A-Za-z][\w:.-]*$')
SOURCE = re.compile(r'^src-[1-9][0-9]*

def invalid(errors):
    return {'schema': SCHEMA, 'state': INVALID, 'errors': list(errors), 'transports': [],
            'independent_qd_pass': False, 'publication_authorized': False,
            'medical_safety_verified': False, 'source_claim_review': 'REQUIRED',
            'issue': 136, 'conversion_issue': 820}


class SemanticsReader(HTMLParser):
    """Inspect actual HTML attribute ordering and global fragment targets."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors = []
        self.stack = []
        self.ids = {}
        self.refs = []
        self.visible = {'pa-chips': [], 'pa-review': []}
        self._scope_count = {name: 0 for name in SCOPES}
        self.tags = 0

    def _inside(self, name):
        return any(name in item['scopes'] for item in self.stack)

    def handle_starttag(self, tag, attrs):
        self.tags += 1
        keys = [k.lower() for k, _ in attrs]
        repeats = {k for k in keys if keys.count(k) > 1}
        if repeats:
            self.errors.append('duplicate HTML attribute: ' + ', '.join(sorted(repeats)))
        d = dict(attrs)  # Only after duplicates have been rejected.
        own = SCOPES.intersection((d.get('class') or '').split())
        for name in own:
            self._scope_count[name] += 1
        ident = d.get('id')
        if ident is not None:
            if not ident or ident in self.ids:
                self.errors.append('duplicate or empty document-wide id: ' + repr(ident))
            else:
                self.ids[ident] = {'tag': tag, 'bibliography_li': tag == 'li' and self._inside('pa-sources')}
        if tag == 'a' and isinstance(d.get('href'), str) and d['href'].startswith('#'):
            ref = d['href']
            if not FRAGMENT.fullmatch(ref):
                self.errors.append('invalid fragment identifier: ' + repr(ref))
            else:
                self.refs.append(ref[1:])
        if tag in BLOCK_BREAKS:
            for scope in self.visible:
                if self._inside(scope):
                    self.visible[scope].append(' ')
        if tag not in VOID:
            self.stack.append({'tag': tag, 'scopes': own})

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag in BLOCK_BREAKS:
            for scope in self.visible:
                if self._inside(scope):
                    self.visible[scope].append(' ')
        if not self.stack or self.stack[-1]['tag'] != tag:
            self.errors.append('malformed tag closure: ' + tag)
        else:
            self.stack.pop()

    def handle_data(self, data):
        for scope in self.visible:
            if self._inside(scope):
                self.visible[scope].append(data)

    def audit(self, raw):
        if type(raw) is not bytes or not raw or len(raw) > 5_000_000:
            return ['transport must be nonempty HTML bytes <= 5MB']
        try:
            self.feed(raw.decode('utf-8', 'strict'))
            self.close()
        except (ValueError, UnicodeError) as exc:
            return [f'HTML decode/parse error: {exc}']
        if self.stack:
            self.errors.append('unclosed HTML document')
        for name, count in sorted(self._scope_count.items()):
            if count != 1:
                self.errors.append(f'{name}: expected exactly one scope, found {count}')
        for ref in self.refs:
            target = self.ids.get(ref)
            if target is None:
                self.errors.append('unresolved document fragment #' + ref)
            elif SOURCE.fullmatch(ref) and not target['bibliography_li']:
                self.errors.append('citation fragment hijack: #' + ref)
        for scope, chunks in self.visible.items():
            # Inline tags do not add whitespace: App<span>roved</span> renders Approved.
            # Inserting a space per text node misses such false release assurances.
            visible = unicodedata.normalize('NFKC', ''.join(chunks)).translate(IGNORABLES)
            normalized = ' '.join(visible.casefold().split())
            if any(token in normalized for token in ASSURANCES):
                self.errors.append('false publication/safety assurance in ' + scope)
        return self.errors


def evaluate(prior, rendered):
    """Only valid four-transport R216 HOLD receipts may advance to R217 HOLD."""
    try:
        if type(prior) is not dict or prior.get('schema') != PARENT_SCHEMA or prior.get('state') != HOLD:
            raise ValueError('authenticated R216 DRAFT_HARD_HOLD report required')
        if prior.get('errors') != [] or any(prior.get(k) is not False for k in
             ('independent_qd_pass', 'publication_authorized', 'medical_safety_verified')):
            raise ValueError('R216 report must contain empty errors and explicit false release flags')
        if prior.get('source_claim_review') != 'REQUIRED':
            raise ValueError('R216 unresolved source claims must remain REQUIRED')
        rows = prior.get('transports')
        pairs = [(7, 'wp'), (7, 'preview'), (20, 'wp'), (20, 'preview')]
        if type(rows) is not list or len(rows) != 4 or type(rendered) is not dict or set(rendered) != {7, 20}:
            raise ValueError('exact four held R216 article/channel receipts required')
        if [(r.get('article'), r.get('channel')) for r in rows if type(r) is dict] != pairs:
            raise ValueError('R216 receipt ordering or article identity mismatch')
        if any(type(rendered.get(n)) is not dict or set(rendered[n]) != {'wp', 'preview'} for n in (7, 20)):
            raise ValueError('WP and preview transports required for both held articles')
        audited = []
        for row, (n, channel) in zip(rows, pairs):
            raw = rendered[n][channel]
            digest = hashlib.sha256(raw).hexdigest() if type(raw) is bytes else ''
            if digest != row.get('sha256') or row.get('exposure_gate') != HOLD:
                raise ValueError(f'R216 receipt drift or exposure status: {n}/{channel}')
            parser = SemanticsReader()
            findings = parser.audit(raw)
            if findings:
                raise ValueError(f'{n}/{channel}: ' + '; '.join(findings))
            audited.append({'article': n, 'channel': channel, 'sha256': digest,
                            'attributes_and_fragments_checked': True, 'gate': HOLD})
        return {'schema': SCHEMA, 'state': HOLD, 'errors': [], 'transports': audited,
                'independent_qd_pass': False, 'publication_authorized': False,
                'medical_safety_verified': False, 'source_claim_review': 'REQUIRED',
                'issue': 136, 'conversion_issue': 820}
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        return invalid([str(exc)])


def main(argv=None):
    parser = argparse.ArgumentParser(description='R217 read-only source transport semantics guard')
    for arg in ('r216-report', 'wp7', 'preview7', 'wp20', 'preview20'):
        parser.add_argument('--' + arg, required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        previous = json.loads(args.r216_report.read_text(encoding='utf-8'))
        docs = {n: {c: getattr(args, c + str(n)).read_bytes() for c in ('wp', 'preview')}
                for n in (7, 20)}
        result = evaluate(previous, docs)
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        result = invalid(['read-only input error: ' + str(exc)])
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2 if result['state'] == HOLD else 3


if __name__ == '__main__':
    raise SystemExit(main())
)
# Block tags create visible word boundaries; inline tags and comments do not.
BLOCK_BREAKS = frozenset(('address article aside blockquote br dd div dl dt fieldset '
                          'figcaption figure footer form h1 h2 h3 h4 h5 h6 header hr li '
                          'main nav ol p pre section table tbody td th thead tr ul').split())
# Default-ignorable characters can visually conceal otherwise forbidden words.
IGNORABLES = str.maketrans('', '', '\u00ad\u200b\u200c\u200d\u2060\ufeff')


def invalid(errors):
    return {'schema': SCHEMA, 'state': INVALID, 'errors': list(errors), 'transports': [],
            'independent_qd_pass': False, 'publication_authorized': False,
            'medical_safety_verified': False, 'source_claim_review': 'REQUIRED',
            'issue': 136, 'conversion_issue': 820}


class SemanticsReader(HTMLParser):
    """Inspect actual HTML attribute ordering and global fragment targets."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors = []
        self.stack = []
        self.ids = {}
        self.refs = []
        self.visible = {'pa-chips': [], 'pa-review': []}
        self._scope_count = {name: 0 for name in SCOPES}
        self.tags = 0

    def _inside(self, name):
        return any(name in item['scopes'] for item in self.stack)

    def handle_starttag(self, tag, attrs):
        self.tags += 1
        keys = [k.lower() for k, _ in attrs]
        repeats = {k for k in keys if keys.count(k) > 1}
        if repeats:
            self.errors.append('duplicate HTML attribute: ' + ', '.join(sorted(repeats)))
        d = dict(attrs)  # Only after duplicates have been rejected.
        own = SCOPES.intersection((d.get('class') or '').split())
        for name in own:
            self._scope_count[name] += 1
        ident = d.get('id')
        if ident is not None:
            if not ident or ident in self.ids:
                self.errors.append('duplicate or empty document-wide id: ' + repr(ident))
            else:
                self.ids[ident] = {'tag': tag, 'bibliography_li': tag == 'li' and self._inside('pa-sources')}
        if tag == 'a' and isinstance(d.get('href'), str) and d['href'].startswith('#'):
            ref = d['href']
            if not FRAGMENT.fullmatch(ref):
                self.errors.append('invalid fragment identifier: ' + repr(ref))
            else:
                self.refs.append(ref[1:])
        if tag == 'br':
            for scope in self.visible:
                if self._inside(scope):
                    self.visible[scope].append(' ')
        if tag not in VOID:
            self.stack.append({'tag': tag, 'scopes': own})

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1]['tag'] != tag:
            self.errors.append('malformed tag closure: ' + tag)
        else:
            self.stack.pop()

    def handle_data(self, data):
        for scope in self.visible:
            if self._inside(scope):
                self.visible[scope].append(data)

    def audit(self, raw):
        if type(raw) is not bytes or not raw or len(raw) > 5_000_000:
            return ['transport must be nonempty HTML bytes <= 5MB']
        try:
            self.feed(raw.decode('utf-8', 'strict'))
            self.close()
        except (ValueError, UnicodeError) as exc:
            return [f'HTML decode/parse error: {exc}']
        if self.stack:
            self.errors.append('unclosed HTML document')
        for name, count in sorted(self._scope_count.items()):
            if count != 1:
                self.errors.append(f'{name}: expected exactly one scope, found {count}')
        for ref in self.refs:
            target = self.ids.get(ref)
            if target is None:
                self.errors.append('unresolved document fragment #' + ref)
            elif SOURCE.fullmatch(ref) and not target['bibliography_li']:
                self.errors.append('citation fragment hijack: #' + ref)
        for scope, chunks in self.visible.items():
            normalized = ' '.join(' '.join(chunks).lower().split())
            if any(token in normalized for token in ASSURANCES):
                self.errors.append('false publication/safety assurance in ' + scope)
        return self.errors


def evaluate(prior, rendered):
    """Only valid four-transport R216 HOLD receipts may advance to R217 HOLD."""
    try:
        if type(prior) is not dict or prior.get('schema') != PARENT_SCHEMA or prior.get('state') != HOLD:
            raise ValueError('authenticated R216 DRAFT_HARD_HOLD report required')
        if prior.get('errors') != [] or any(prior.get(k) is not False for k in
             ('independent_qd_pass', 'publication_authorized', 'medical_safety_verified')):
            raise ValueError('R216 report must contain empty errors and explicit false release flags')
        if prior.get('source_claim_review') != 'REQUIRED':
            raise ValueError('R216 unresolved source claims must remain REQUIRED')
        rows = prior.get('transports')
        pairs = [(7, 'wp'), (7, 'preview'), (20, 'wp'), (20, 'preview')]
        if type(rows) is not list or len(rows) != 4 or type(rendered) is not dict or set(rendered) != {7, 20}:
            raise ValueError('exact four held R216 article/channel receipts required')
        if [(r.get('article'), r.get('channel')) for r in rows if type(r) is dict] != pairs:
            raise ValueError('R216 receipt ordering or article identity mismatch')
        if any(type(rendered.get(n)) is not dict or set(rendered[n]) != {'wp', 'preview'} for n in (7, 20)):
            raise ValueError('WP and preview transports required for both held articles')
        audited = []
        for row, (n, channel) in zip(rows, pairs):
            raw = rendered[n][channel]
            digest = hashlib.sha256(raw).hexdigest() if type(raw) is bytes else ''
            if digest != row.get('sha256') or row.get('exposure_gate') != HOLD:
                raise ValueError(f'R216 receipt drift or exposure status: {n}/{channel}')
            parser = SemanticsReader()
            findings = parser.audit(raw)
            if findings:
                raise ValueError(f'{n}/{channel}: ' + '; '.join(findings))
            audited.append({'article': n, 'channel': channel, 'sha256': digest,
                            'attributes_and_fragments_checked': True, 'gate': HOLD})
        return {'schema': SCHEMA, 'state': HOLD, 'errors': [], 'transports': audited,
                'independent_qd_pass': False, 'publication_authorized': False,
                'medical_safety_verified': False, 'source_claim_review': 'REQUIRED',
                'issue': 136, 'conversion_issue': 820}
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        return invalid([str(exc)])


def main(argv=None):
    parser = argparse.ArgumentParser(description='R217 read-only source transport semantics guard')
    for arg in ('r216-report', 'wp7', 'preview7', 'wp20', 'preview20'):
        parser.add_argument('--' + arg, required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        previous = json.loads(args.r216_report.read_text(encoding='utf-8'))
        docs = {n: {c: getattr(args, c + str(n)).read_bytes() for c in ('wp', 'preview')}
                for n in (7, 20)}
        result = evaluate(previous, docs)
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        result = invalid(['read-only input error: ' + str(exc)])
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2 if result['state'] == HOLD else 3


if __name__ == '__main__':
    raise SystemExit(main())
