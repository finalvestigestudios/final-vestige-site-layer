#!/usr/bin/env python3
"""R454: exact-pinned, read-only citation-to-claim-neighborhood drift audit.

Purpose: counts alone cannot identify a citation moved from one claim to another.
This tool compares contextual citation anchors, without pretending textual proximity
is proof of source support, QD approval, advice safety, or release readiness.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from r452_qa157_semantic_custody import PATHS, QA157, R451, HOLD, CustodyError, read_root
from r453_citation_read_depth_deltas import CITE, review_packet, source_index

BLOCKS = frozenset({'p', 'li', 'td', 'th', 'figcaption', 'blockquote', 'dt', 'dd'} |
                   {f'h{i}' for i in range(1, 7)})
SKIP = frozenset({'script', 'style', 'template'})
CITE_FLEX = re.compile(r'\{\{\s*cite\s*:', re.IGNORECASE)
MAX_EXCERPT = 150


def _plain(value: str) -> str:
    return ' '.join(unescape(value).split())


def _fingerprint(value: str) -> str:
    return sha256(value.encode('utf-8')).hexdigest()


class ClaimParser(HTMLParser):
    """No network or output writes. Preserve individual citation-bearing units."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.frames: list[dict] = []
        self.units: list[dict] = []
        self.heading = '(before first heading)'
        self.skipping: list[str] = []
        self.raw_tokens = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in SKIP:
            self.skipping.append(tag)
        if tag in BLOCKS:
            self.frames.append({'tag': tag, 'chunks': [], 'heading_at_start': self.heading})
        if tag == 'br' and self.frames:
            self.frames[-1]['chunks'].append(' ')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() in BLOCKS | SKIP:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self.skipping:
            return
        if self.frames:
            self.frames[-1]['chunks'].append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in SKIP:
            if not self.skipping or self.skipping[-1] != tag:
                raise CustodyError('unbalanced hidden-content tag: ' + tag)
            self.skipping.pop()
        if tag in BLOCKS:
            if not self.frames or self.frames[-1]['tag'] != tag:
                raise CustodyError('unbalanced review-unit tag: ' + tag)
            frame = self.frames.pop()
            raw_text = ''.join(frame['chunks'])
            cite_ids = CITE.findall(raw_text)
            plain = _plain(CITE.sub(' ', raw_text))
            if tag.startswith('h') and len(tag) == 2 and tag[1].isdigit():
                self.heading = plain or '(empty heading)'
            if cite_ids:
                context = frame['heading_at_start'] + '\n' + tag + '\n' + plain
                digest = _fingerprint(context)
                self.units.append({
                    'kind': tag, 'heading': frame['heading_at_start'],
                    'text_excerpt': plain[:MAX_EXCERPT],
                    'text_characters': len(plain), 'anchor_sha256': digest,
                    'source_ids': cite_ids,
                })

    def finalize(self, html: str) -> list[dict]:
        if self.frames or self.skipping:
            raise CustodyError('unclosed HTML review-unit or hidden-content tag')
        total = sum(len(u['source_ids']) for u in self.units)
        raw = CITE.findall(html)
        if total != len(raw) or Counter(s for u in self.units for s in u['source_ids']) != Counter(raw):
            raise CustodyError('citation outside supported visible claim unit, or unparsed citation')
        # Refuse quasi-citation or placeholder variants, rather than ignoring them.
        if len(CITE_FLEX.findall(html)) != len(raw):
            raise CustodyError('malformed citation token or noncanonical case/spacing')
        return self.units


def claim_units(html: str) -> list[dict]:
    if not isinstance(html, str):
        raise CustodyError('article must be UTF-8 text')
    parser = ClaimParser()
    try:
        parser.feed(html)
        parser.close()
        return parser.finalize(html)
    except (ValueError, UnicodeError) as exc:
        raise CustodyError('invalid citation-bearing HTML: ' + str(exc)) from exc


def _anchors(units: list[dict]) -> dict[str, Counter]:
    grouped = defaultdict(Counter)
    for unit in units:
        for source_id in unit['source_ids']:
            grouped[source_id][unit['anchor_sha256']] += 1
    return dict(grouped)


def _examples(units: list[dict]) -> dict[tuple[str, str], dict]:
    result = {}
    for unit in units:
        for sid in unit['source_ids']:
            result[(sid, unit['anchor_sha256'])] = {
                'unit': unit['kind'], 'heading': unit['heading'][:MAX_EXCERPT],
                'excerpt': unit['text_excerpt'], 'sha256': unit['anchor_sha256'],
            }
    return result


def _scope(sid: str, before: dict, after: dict) -> dict:
    if sid not in before or sid not in after:
        return {'status': 'NOT_IN_START_FRAGMENT_REQUIRES_FULL_REGISTER_LOOKUP'}
    src_old, src_new = before[sid], after[sid]
    return {
        'status': 'PRESENT_IN_PINNED_START_FRAGMENT',
        'url': src_old.get('url'),
        'reading_scope_changed': src_old.get('supports') != src_new.get('supports'),
        'reading_scope_before_sha256': _fingerprint(str(src_old.get('supports', ''))),
        'reading_scope_after_sha256': _fingerprint(str(src_new.get('supports', ''))),
        'qualified_source_review': 'REQUIRED',
    }


def anchored_review_packet(qa: dict[str, bytes], candidate: dict[str, bytes],
                           qa_pins=QA157, candidate_pins=R451) -> dict:
    """Human-review queue only, with exact R452/R453 Git blob custody first."""
    prior = review_packet(qa, candidate, qa_pins, candidate_pins)
    sources_qa = source_index(qa[PATHS[2]])
    sources_candidate = source_index(candidate[PATHS[2]])
    report = []
    for path in PATHS[:2]:
        before = claim_units(qa[path].decode('utf-8'))
        after = claim_units(candidate[path].decode('utf-8'))
        a = _anchors(before)
        b = _anchors(after)
        before_example, after_example = _examples(before), _examples(after)
        changed = []
        for source_id in sorted(set(a) | set(b)):
            lost = a.get(source_id, Counter()) - b.get(source_id, Counter())
            gained = b.get(source_id, Counter()) - a.get(source_id, Counter())
            if lost or gained:
                changed.append({
                    'source_id': source_id,
                    'citation_count_before': sum(a.get(source_id, {}).values()),
                    'citation_count_after': sum(b.get(source_id, {}).values()),
                    'removed_contexts': [{**before_example[(source_id, key)], 'count': n}
                                         for key, n in sorted(lost.items())],
                    'added_contexts': [{**after_example[(source_id, key)], 'count': n}
                                       for key, n in sorted(gained.items())],
                    'documented_source_scope': _scope(source_id, sources_qa, sources_candidate),
                    'human_claim_support_review': 'REQUIRED',
                })
        count_before = sum(len(u['source_ids']) for u in before)
        count_after = sum(len(u['source_ids']) for u in after)
        report.append({
            'path': path, 'citation_occurrences_before': count_before,
            'citation_occurrences_after': count_after,
            'citation_bearing_units_before': len(before),
            'citation_bearing_units_after': len(after),
            'source_ids_with_context_drift': len(changed),
            'citation_anchor_changes_requiring_review': changed,
            'same_counts_can_still_hide_retargeting': True,
            'article_claim_support_approved': False,
        })
    return {
        'release_state': HOLD,
        'source_review': 'NOT_APPROVED', 'medical_safety': 'NOT_APPROVED',
        'emergency_safety': 'NOT_APPROVED', 'qd_pass': False,
        'word_press_build': 'NOT_EXECUTED',
        'full_35_article_reconciliation': 'NOT_EXECUTED',
        'intent': 'Review contextual citation changes; SHA anchors are not evidence of authority correctness.',
        'original_git_blob_pins': prior['basis'],
        'original_sources_disputed': prior['unresolved_source_disputes'],
        'original_forks_unselected': prior['unselected_forks'],
        'shared_url_groups_not_merged': prior['shared_url_groups_not_merged'],
        'original_r453_change_queue_preserved': True,
        'articles': report,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qa-root', type=Path, required=True)
    parser.add_argument('--candidate-root', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = anchored_review_packet(read_root(args.qa_root), read_root(args.candidate_root))
        print(json.dumps(result, indent=2, sort_keys=True))
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({'release_state': HOLD, 'error': str(exc), 'qd_pass': False}))
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
