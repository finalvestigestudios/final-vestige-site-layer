#!/usr/bin/env python3
"""R453 read-only claim/citation and source reading-depth change queue.

Compares SHA-pinned QA #157 and R451 source snapshots using R452 custody
checks. It never declares any emergency advice, source or release safe.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from html import unescape
from r452_qa157_semantic_custody import (
    PATHS, QA157, R451, HOLD, CustodyError, assess, parse_json, read_root,
)

CITE = re.compile(r'\{\{cite:([A-Za-z0-9][A-Za-z0-9_.-]*)\}\}')
HEADING = re.compile(r'<h([1-6])\b[^>]*>(.*?)</h\1\s*>', re.I | re.S)
HTML_TAG = re.compile(r'<[^>]+>')
EXCERPT_CAP = 220


def digest(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def excerpt(value: str) -> str:
    text = unescape(HTML_TAG.sub(' ', CITE.sub(' ', value)))
    text = ' '.join(text.split())
    return text[:EXCERPT_CAP]


def citations(html: str) -> Counter:
    return Counter(CITE.findall(html))


def headings(html: str) -> list[tuple[str, str]]:
    return [(level, excerpt(text)) for level, text in HEADING.findall(html)]


def source_index(raw: bytes) -> dict:
    obj = parse_json(raw, 'R453 source fragment')
    if not isinstance(obj, dict) or not isinstance(obj.get('sources'), list):
        raise CustodyError('invalid source fragment')
    sources = {}
    for entry in obj['sources']:
        if not isinstance(entry, dict) or not isinstance(entry.get('id'), str) or not entry['id']:
            raise CustodyError('source entry missing id')
        if entry['id'] in sources:
            raise CustodyError('duplicate source ID: ' + entry['id'])
        sources[entry['id']] = entry
    return sources


def review_packet(qa: dict[str, bytes], candidate: dict[str, bytes],
                  qa_pins=QA157, candidate_pins=R451) -> dict:
    """Deterministic, non-approving comparison; rejects unpinned inputs."""
    custody = assess(qa, candidate, qa_pins, candidate_pins)
    before = source_index(qa[PATHS[2]])
    after = source_index(candidate[PATHS[2]])
    changed_sources = []
    for sid in sorted(before):
        old, new = before[sid], after[sid]
        fields = []
        for field in ('supports', 'notes', 'published', 'updated', 'reviewed',
                      'verified_on', 'human_link_check', 'kind', 'title'):
            if old.get(field) != new.get(field):
                fields.append({
                    'field': field, 'before_sha256': digest(json.dumps(old.get(field), sort_keys=True)),
                    'after_sha256': digest(json.dumps(new.get(field), sort_keys=True)),
                    'before_excerpt': excerpt(str(old.get(field, ''))),
                    'after_excerpt': excerpt(str(new.get(field, ''))),
                })
        if fields:
            changed_sources.append({'source_id': sid, 'url': old.get('url'),
                                    'reading_scope_changed': any(f['field'] == 'supports' for f in fields),
                                    'fields': fields, 'requires_qualified_review': True})

    article_review = []
    for path in PATHS[:2]:
        old = qa[path].decode('utf-8')
        new = candidate[path].decode('utf-8')
        a, b = citations(old), citations(new)
        removed = {k: a[k] - b[k] for k in sorted(a) if a[k] > b[k]}
        added = {k: b[k] - a[k] for k in sorted(b) if b[k] > a[k]}
        old_head, new_head = headings(old), headings(new)
        article_review.append({
            'path': path, 'body_sha256_before': digest(old), 'body_sha256_after': digest(new),
            'source_citations_before': dict(sorted(a.items())),
            'source_citations_after': dict(sorted(b.items())),
            'citation_occurrences_removed': removed,
            'citation_occurrences_added': added,
            'headings_before': old_head, 'headings_after': new_head,
            'heading_sequence_changed': old_head != new_head,
            'text_characters_before': len(excerpt_all(old)),
            'text_characters_after': len(excerpt_all(new)),
            'requires_qualified_review': old != new,
        })

    return {
        'release_state': HOLD, 'qualified_review': 'NOT_APPROVED',
        'original_safety_review': 'REQUIRED', 'article_citation_placements': 'NOT_INDEPENDENTLY_VERIFIED',
        'source_id_to_url_custody': 'R452_STRUCTURAL_CHECK_ONLY',
        'basis': {'qa157_sha_pins': dict(zip(PATHS, qa_pins)),
                  'r451_sha_pins': dict(zip(PATHS, candidate_pins))},
        'structural_custody': custody,
        'source_changes_requiring_review': changed_sources,
        'article_citation_changes_requiring_review': article_review,
        'unresolved_source_disputes': 5, 'unselected_forks': 9,
        'shared_url_groups_not_merged': 17,
        'commerce_verification': 'NOT_VERIFIED',
        'word_press_export_verification': 'NOT_EXECUTED',
        'interpretation': 'Change detection only. Even unchanged citations do not prove correct support or safe advice.',
    }


def excerpt_all(html: str) -> str:
    return ' '.join(unescape(HTML_TAG.sub(' ', CITE.sub(' ', html))).split())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qa-root', type=Path, required=True)
    parser.add_argument('--candidate-root', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = review_packet(read_root(args.qa_root), read_root(args.candidate_root))
        print(json.dumps(report, sort_keys=True, indent=2))
    except (ValueError, OSError, UnicodeError) as exc:
        print(json.dumps({'release_state': HOLD, 'error': str(exc), 'qualified_review': 'NOT_APPROVED'}))
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
