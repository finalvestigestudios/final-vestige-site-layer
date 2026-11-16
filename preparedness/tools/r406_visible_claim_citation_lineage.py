#!/usr/bin/env python3
"""R406 four-edition, read-only visible-text and citation-context audit.

This is deliberately *not* a scientific, medical, privacy or publication approval.
It must be used alongside the R405 fixed-hash/ZIP custody audit. It treats
unreviewed manuscript edits as an adjudication requirement, never as clearance.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlsplit

HOLD = 'DRAFT_HARD_HOLD'
E399_HTML_PIN = '75ed08831c138ad3057220df060897e1efe518f1156ea68bb2400c06db898661'
E399_PRINT_PIN = '240a20ea5cdb6a34a686eb605550766e8572bb9c37d3836e2abd85f2d84e7709'
E399_PACKAGE_PIN = 'b2b9f151959ae39169d0884bf8ee16f1500721256b7a5aa0cff923248061404e'
EDITION_KEYS = ('E395', 'E397', 'E398', 'E399')
MAX_HTML_BYTES = 4 * 1024 * 1024
MAX_BLOCKS = 6000
MAX_DEPTH = 256
BLOCKS = frozenset('p li h1 h2 h3 h4 h5 h6 blockquote pre figcaption td th dt dd'.split())
CLAIM_BLOCKS = BLOCKS - {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
EXCLUDE = frozenset('head style script noscript template nav footer'.split())
VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())
SPACE = re.compile(r'\s+')
WORDS = re.compile(r"(?u)\b[\w]+(?:[\u2019'-][\w]+)*\b")
HIDDEN_CSS = re.compile(r'(?i)(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)(?:\s*!important)?\s*(?:;|$)')


def normalized(s: str) -> str:
    return SPACE.sub(' ', unicodedata.normalize('NFC', s)).strip()


def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _link(url: str) -> str:
    u = urlsplit(url)
    return url.split('#', 1)[0] if u.scheme == 'https' and u.hostname else ''


class VisibleClaims(HTMLParser):
    """Extract in-flow visible text, source-link context and stable block hashes.

    This is a conservative static heuristic. CSS classes, stylesheets, browser
    layout and factual claim support still require independent review.
    """
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[dict] = []
        self.blocks: list[dict] = []
        self.visible_pieces: list[str] = []
        self.visible_source_urls: set[str] = set()
        self.claim_bound_urls: set[str] = set()
        self.raw_source_urls: set[str] = set()
        self.problems: set[str] = set()
        self.anchors: list[dict] = []
        self.current_anchor: dict | None = None
        self.block_count = 0

    def _excluded(self):
        return any(f['excluded'] for f in self.stack)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID:
            self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if len(self.stack) >= MAX_DEPTH:
            self.problems.add('html_nesting_limit')
            return
        attributes = dict(attrs)
        hidden = ('hidden' in attributes or 'inert' in attributes or
                  (attributes.get('aria-hidden') or '').casefold() == 'true' or
                  bool(HIDDEN_CSS.search(attributes.get('style') or '')))
        excluded = self._excluded() or hidden or tag in EXCLUDE
        if tag == 'a':
            href = attributes.get('href') or ''
            canonical = _link(href)
            if canonical:
                self.raw_source_urls.add(canonical)
            if self.current_anchor is not None:
                self.problems.add('nested_anchor')
            if not excluded:
                self.current_anchor = {'url': canonical, 'text': [],
                                       'bound': any(f['tag'] in CLAIM_BLOCKS and not f['excluded'] for f in self.stack),
                                       'heading': any(f['tag'] in BLOCKS - CLAIM_BLOCKS for f in self.stack)}
        frame = {'tag': tag, 'excluded': excluded, 'text': [], 'source_urls': set(),
                 'has_child': False}
        if tag in BLOCKS and not excluded:
            for ancestor in reversed(self.stack):
                if ancestor['tag'] in BLOCKS and not ancestor['excluded']:
                    ancestor['has_child'] = True
                    break
        if tag not in VOID:
            self.stack.append(frame)

    def handle_data(self, data):
        if not data or self._excluded():
            return
        self.visible_pieces.append(data)
        if self.current_anchor is not None:
            self.current_anchor['text'].append(data)
        for f in self.stack:
            if f['tag'] in BLOCKS:
                f['text'].append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in VOID:
            return
        if not self.stack:
            self.problems.add('stray_closing_tag')
            return
        # Malformed nesting is not normalized into an alleged accurate claim map.
        if self.stack[-1]['tag'] != tag:
            self.problems.add('misnested_html')
            return
        frame = self.stack.pop()
        if tag == 'a' and self.current_anchor is not None:
            anchor = self.current_anchor
            self.current_anchor = None
            label = normalized(''.join(anchor['text']))
            if anchor['url']:
                if not label:
                    self.problems.add('unlabeled_source_link')
                if anchor['heading'] or not anchor['bound']:
                    self.problems.add('source_link_outside_claim_context')
                if not frame['excluded']:
                    self.visible_source_urls.add(anchor['url'])
                    if anchor['bound'] and label:
                        self.claim_bound_urls.add(anchor['url'])
                        for ancestor in reversed(self.stack):
                            if ancestor['tag'] in CLAIM_BLOCKS and not ancestor['excluded']:
                                ancestor['source_urls'].add(anchor['url'])
                                break
            self.anchors.append({'url': anchor['url'], 'label_sha256': digest(label),
                                 'bound': bool(anchor['bound'] and label),
                                 'visible': not frame['excluded']})
        if tag in BLOCKS and not frame['excluded']:
            content = normalized(''.join(frame['text']))
            if content and not frame['has_child']:
                self.block_count += 1
                if self.block_count > MAX_BLOCKS:
                    self.problems.add('block_inventory_limit')
                else:
                    self.blocks.append({'tag': tag, 'text_sha256': digest(content),
                                        'words': len(WORDS.findall(content)),
                                        'source_urls': sorted(frame['source_urls'])})

    def finish(self):
        if self.stack:
            self.problems.add('unclosed_html_markup')
        if self.current_anchor:
            self.problems.add('unclosed_source_anchor')
        return self


def capture(raw: object, required_sources: set[str] | frozenset[str]) -> dict:
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_HTML_BYTES:
        return {'integrity': 'FAIL', 'failures': ['missing_or_oversized_html']}
    if not isinstance(required_sources, (set, frozenset)) or any(not isinstance(x, str) for x in required_sources):
        return {'integrity': 'FAIL', 'failures': ['invalid_source_inventory']}
    try:
        scanner = VisibleClaims()
        scanner.feed(raw.decode('utf-8', 'strict'))
        scanner.close()
        scanner.finish()
    except (UnicodeDecodeError, ValueError, AssertionError, OverflowError):
        return {'integrity': 'FAIL', 'failures': ['unparseable_html']}
    missing = set(required_sources) - scanner.claim_bound_urls
    failures = set(scanner.problems)
    if missing:
        failures.add('required_sources_not_visibly_claim_bound')
    text = normalized(' '.join(scanner.visible_pieces))
    if not text:
        failures.add('empty_visible_manuscript')
    if not scanner.blocks:
        failures.add('missing_reading_blocks')
    return {'integrity': 'FAIL' if failures else 'PASS', 'failures': sorted(failures),
            'source_scope_missing': sorted(missing), 'reading_sha256': digest(text),
            'reading_word_count': len(WORDS.findall(text)),
            'blocks': scanner.blocks, 'source_urls_seen': sorted(scanner.raw_source_urls),
            'visible_source_urls': sorted(scanner.visible_source_urls),
            'claim_bound_source_urls': sorted(scanner.claim_bound_urls),
            'unreviewed_contextual_source_links': sum(1 for a in scanner.anchors if a['url'] and not a['bound'])}


def _delta(older: dict, newer: dict) -> dict:
    a, b = older.get('blocks', []), newer.get('blocks', [])
    key = lambda z: (z['tag'], z['text_sha256'], tuple(z['source_urls']))
    old, new = Counter(map(key, a)), Counter(map(key, b))
    removed, added = old - new, new - old
    return {'removed_blocks': sum(removed.values()), 'added_blocks': sum(added.values()),
            'removed_block_ids': sorted([k[1] for k, count in removed.items() for _ in range(count)]),
            'added_block_ids': sorted([k[1] for k, count in added.items() for _ in range(count)]),
            'reordered_or_changed': [key(x) for x in a] != [key(x) for x in b],
            'word_delta': newer.get('reading_word_count', 0) - older.get('reading_word_count', 0),
            'removed_bound_sources': sorted(set(older.get('claim_bound_source_urls', [])) - set(newer.get('claim_bound_source_urls', [])))}


def inspect(variants: dict, required_sources: set[str] | frozenset[str], *,
            e399_receipt: str | None = None) -> dict:
    if not isinstance(variants, dict) or set(variants) != set(EDITION_KEYS):
        return {'schema': 'r406.claim_context.v1', 'integrity': 'FAIL', 'release': HOLD,
                'publication_approved': False, 'failures': ['variant_inventory_mismatch']}
    records = {name: capture(variants[name], required_sources) for name in EDITION_KEYS}
    deltas = {a + '_to_' + b: _delta(records[a], records[b]) for a, b in
              zip(EDITION_KEYS, EDITION_KEYS[1:])}
    failures = {f'{name}:{f}' for name, report in records.items() for f in report['failures']}
    expected = E399_HTML_PIN if e399_receipt is None else e399_receipt
    if not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
        failures.add('invalid_e399_receipt')
    elif not isinstance(variants['E399'], bytes) or hashlib.sha256(variants['E399']).hexdigest() != expected:
        failures.add('e399_original_receipt_mismatch')
    if any(d['reordered_or_changed'] for d in deltas.values()):
        failures.add('editorial_depth_or_citation_context_changes_need_human_review')
    if any(d['removed_bound_sources'] for d in deltas.values()):
        failures.add('claim_bound_source_removed')
    return {'schema': 'r406.claim_context.v1', 'article_slug': 'safe-jerky-dehydration',
            'integrity': 'FAIL' if failures else 'PASS', 'release': HOLD,
            'eligible': False, 'publication_approved': False, 'medical_or_food_safety_approved': False,
            'source_authenticity_proven': False, 'human_review': 'NOT_GRANTED',
            'selected_variant': None, 'records': records, 'deltas': deltas,
            'failures': sorted(failures)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('e395-zip', 'e395-html', 'e397-html', 'e398-html', 'e399-html', 'e399-print'):
        parser.add_argument('--' + arg, type=Path)
    options = parser.parse_args(argv)
    here = Path(__file__).parent
    try:
        spec = importlib.util.spec_from_file_location('r405_prior_gate', here / 'r405_editorial_lineage_citation_gate.py')
        upstream = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(upstream)
        files = {'E395': upstream.read_html(options.e395_html),
                 'E397': upstream.read_html(options.e397_html),
                 'E398': upstream.read_html(options.e398_html),
                 'E399': upstream.read_html(options.e399_html)}
        worksheet = upstream.read_html(options.e399_print)
        prior_spec = importlib.util.spec_from_file_location('r404_bounded_zip', here / 'r402_external_editorial_custody.py')
        custody = importlib.util.module_from_spec(prior_spec)
        prior_spec.loader.exec_module(custody)
        archive = custody.read_bounded_original(options.e395_zip) if options.e395_zip else None
        original_result = upstream.inspect_bundle(archive, {k: files[k] for k in EDITION_KEYS[:-1]})
        depth_result = inspect(files, upstream.SOURCE_URLS)
        worksheet_hash_ok = isinstance(worksheet, bytes) and hashlib.sha256(worksheet).hexdigest() == E399_PRINT_PIN
        # Worksheet may contain no references; require independent immutable receipt.
        failures = ['r405:' + x for x in original_result.get('failures', [])] + ['r406:' + x for x in depth_result['failures']]
        if not worksheet_hash_ok:
            failures.append('e399_original_printable_receipt_mismatch')
        output = {'schema': 'r406.composite.v1', 'integrity': 'FAIL' if failures else 'PASS',
                  'release': HOLD, 'publication_approved': False,
                  'upstream_custody': original_result, 'visible_lineage': depth_result,
                  'e399_print_sha256_matched': worksheet_hash_ok, 'e399_reported_package_receipt': E399_PACKAGE_PIN,
                  'failures': sorted(failures)}
    except (OSError, ValueError, RuntimeError):
        output = {'schema': 'r406.composite.v1', 'integrity': 'FAIL', 'release': HOLD,
                  'publication_approved': False, 'failures': ['unavailable_or_unreadable_original_artifacts']}
    print(json.dumps(output, sort_keys=True))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
