#!/usr/bin/env python3
"""R436: fail-closed review of visible full-document text and controls.

R435 locks a multiset of anchor destinations, not which label or accessible name
points to which destination. Nor does it compare safety copy outside <main>.
This read-only additive gate compares both, without assuming template equivalence
is publication approval. Native CMS and qualified reviewers remain required.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import sys

MAX_BYTES = 1_000_000
CONTROL = {'a', 'button', 'input', 'select', 'textarea'}
BLOCK = {'p', 'div', 'section', 'aside', 'header', 'footer', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'}
ACCESS = ('aria-label', 'aria-labelledby', 'aria-describedby', 'title', 'role', 'rel', 'target', 'download', 'referrerpolicy', 'hreflang', 'type', 'value', 'name', 'id')
SKIP = {'script', 'style', 'head', 'template', 'noscript'}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}


def tidy(value):
    return re.sub(r'\s+', ' ', str(value or '')).strip()


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class Semantics(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors = []
        self.stack = []
        self.controls = []
        self.open_controls = []
        self.all_text = []
        self.outside_text = []
        self.in_main = 0
        self.main_count = 0
        self.ids = {}
        self.refs = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)
        d = {k.lower(): v for k, v in attrs if isinstance(k, str)}
        if tag == 'main':
            self.in_main += 1
            self.main_count += 1
        if d.get('id'):
            ident = d['id']
            self.ids[ident] = self.ids.get(ident, 0) + 1
        for key in ('aria-labelledby', 'aria-describedby'):
            if d.get(key):
                self.refs.extend(d[key].split())
        if tag in CONTROL:
            record = {'tag': tag, 'href': tidy(d.get('href')), 'text': '',
                      'attributes': {k: tidy(d.get(k)) for k in ACCESS if k in d},
                      'outside_main': self.in_main == 0}
            self.controls.append(record)
            if tag in ('a', 'button', 'select', 'textarea'):
                self.open_controls.append((tag, record))
        if tag == 'input' and d.get('type', '').lower() in ('submit', 'button', 'reset'):
            if not d.get('value') and not d.get('aria-label'):
                self.errors.append('UNNAMED_INPUT_CONTROL')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == 'main':
            self.in_main = max(0, self.in_main - 1)
        if self.open_controls and self.open_controls[-1][0] == tag:
            self.open_controls.pop()
        if tag in self.stack:
            # Recover without mistaking malformed nesting for trusted semantics.
            if self.stack[-1] != tag:
                self.errors.append('MALFORMED_CONTROL_OR_DOCUMENT_NESTING')
            while self.stack:
                if self.stack.pop() == tag:
                    break
        else:
            self.errors.append('UNEXPECTED_END_TAG')

    def handle_data(self, data):
        if set(self.stack).intersection(SKIP):
            return
        value = tidy(data)
        if not value:
            return
        self.all_text.append(value)
        if not self.in_main:
            self.outside_text.append(value)
        for _, record in self.open_controls:
            record['text'] += (' ' if record['text'] else '') + value

    def result(self):
        if self.main_count != 1:
            self.errors.append('MISSING_OR_DUPLICATE_MAIN')
        if self.stack or self.open_controls:
            self.errors.append('UNCLOSED_DOCUMENT_OR_CONTROL')
        for ref in self.refs:
            if self.ids.get(ref, 0) != 1:
                self.errors.append('ARIA_REFERENCE_MISSING_OR_DUPLICATED')
        for rec in self.controls:
            rec['text'] = tidy(rec['text'])
            if rec['tag'] in ('a', 'button') and not (rec['text'] or rec['attributes'].get('aria-label') or rec['attributes'].get('aria-labelledby')):
                self.errors.append('UNNAMED_INTERACTIVE_CONTROL')
        return {'errors': sorted(set(self.errors)),
                'control_binding_sha256': digest(self.controls),
                'outside_main_text_sha256': digest(self.outside_text),
                'all_document_text_sha256': digest(self.all_text),
                'control_count': len(self.controls),
                'outside_main_fragment_count': len(self.outside_text)}


def inspect(raw):
    if not isinstance(raw, bytes) or not 12 <= len(raw) <= MAX_BYTES or b'\0' in raw:
        raise ValueError('INVALID_OR_MISSING_DOCUMENT')
    parser = Semantics()
    parser.feed(raw.decode('utf-8', 'strict'))
    parser.close()
    return parser.result()


def pair_review(wordpress, preview):
    a, b = inspect(wordpress), inspect(preview)
    errors = ['wordpress:' + e for e in a['errors']] + ['preview:' + e for e in b['errors']]
    for name, code in (('control_binding_sha256', 'CONTROL_ACCESSIBLE_NAME_OR_DESTINATION_DRIFT'),
                       ('outside_main_text_sha256', 'OUTSIDE_MAIN_SAFETY_OR_CTA_COPY_DRIFT'),
                       ('all_document_text_sha256', 'FULL_DOCUMENT_READING_COPY_DRIFT')):
        if a[name] != b[name]:
            errors.append(code)
    return {'errors': sorted(set(errors)), 'wordpress': a, 'preview': b,
            'human_review_required': True}


def load_parent():
    p = Path(__file__).with_name('r435_redirect_visibility_custody_gate.py')
    if not p.is_file():
        raise ValueError('R435_PARENT_REQUIRED')
    spec = importlib.util.spec_from_file_location('r435_redirect_visibility_custody_gate', p)
    if spec is None or spec.loader is None:
        raise ValueError('R435_PARENT_UNLOADABLE')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hold(errors, base=None, rows=()):
    base = base if isinstance(base, dict) else {}
    errs = sorted(set(list(base.get('errors', [])) + list(errors)))
    return {'schema': 1, 'issue': 136, 'business_issue': 820,
            'release_state': 'DRAFT_HARD_HOLD', 'eligible': False,
            'publication_approved': False, 'qualified_safety_approved': False,
            'paid_product_verified': False, 'merchant_orders_verified': None,
            'net_revenue_per_1000_qualified_human_sessions': None,
            'r435_full_anchor_parity': bool(base.get('r435_complete_link_and_visibility_parity', False)),
            'r436_semantic_review_clear': not errs and len(rows) == 35,
            'errors': errs, 'review_rows': list(rows),
            'authentic_source_accuracy': 'NOT_VERIFIED',
            'human_accessibility_review': 'NOT_PERFORMED',
            'review_only_digest': digest(rows) if rows else None}


def audit(manifest, exports, lock, *, test_only=False):
    try:
        base = load_parent().audit(manifest, exports, lock, test_only=test_only)
    except (ValueError, OSError, TypeError, AttributeError, ImportError):
        return hold(['PARENT_R435_AUDIT_UNAVAILABLE'])
    if not isinstance(manifest, dict) or not isinstance(manifest.get('articles'), list) or not isinstance(exports, dict):
        return hold(['AUTHENTIC_MANIFEST_OR_EXPORTS_MISSING'], base)
    errors, rows, seen = [], [], set()
    for item in manifest['articles']:
        if not isinstance(item, dict) or not isinstance(item.get('slug'), str):
            errors.append('INVALID_ARTICLE_IDENTITY'); continue
        slug = item['slug']
        if slug in seen or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
            errors.append('DUPLICATE_OR_INVALID_ARTICLE_IDENTITY'); continue
        seen.add(slug)
        pair = exports.get(slug)
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            errors.append('MISSING_PAIR:' + slug); continue
        try:
            review = pair_review(pair[0], pair[1])
            errors.extend(slug + ':' + e for e in review['errors'])
            rows.append({'slug': slug, 'wordpress': review['wordpress'],
                         'preview': review['preview'], 'human_review_required': True})
        except (ValueError, TypeError, UnicodeError, OverflowError):
            errors.append('INVALID_PAIR:' + slug)
    if seen != set(exports):
        errors.append('EXTRA_OR_MISSING_ARTICLE_EXPORT')
    if not test_only and len(rows) != 35:
        errors.append('INCOMPLETE_35_ARTICLE_SLATE')
    return hold(errors, base, sorted(rows, key=lambda x: x['slug']))


def main(argv=None):
    p = argparse.ArgumentParser(description='R436 semantic export review; always HOLD')
    p.add_argument('manifest', type=Path); p.add_argument('lock', type=Path); p.add_argument('exports', type=Path)
    a = p.parse_args(argv)
    try:
        # Read-only original asset loading through R425, never create a source fixture.
        base = Path(__file__).with_name('r425_integrated_custody_gate.py')
        spec = importlib.util.spec_from_file_location('r425_integrated_custody_gate', base)
        if spec is None or spec.loader is None: raise ValueError('R425_READER_MISSING')
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        manifest, _ = m.read_json(a.manifest, a.manifest.parent)
        lock, _ = m.read_json(a.lock, a.lock.parent)
        exports = {}
        for item in manifest['articles']:
            slug = item['slug']
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in exports:
                raise ValueError('UNSAFE_EXPORT_ID')
            exports[slug] = tuple(m.r409.read_original(m.safe_path(a.exports / ch / (slug + '.html'), a.exports), MAX_BYTES)
                                   for ch in ('wordpress', 'preview'))
        report = audit(manifest, exports, lock)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, UnicodeError, OverflowError):
        report = hold(['AUTHENTIC_COMPLETE_EVIDENCE_UNAVAILABLE'])
    print(json.dumps(report, sort_keys=True, indent=2)); return 2


if __name__ == '__main__':
    sys.exit(main())
