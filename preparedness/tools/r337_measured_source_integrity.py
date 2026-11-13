#!/usr/bin/env python3
"""R337 read-only source-depth and citation-token custody, NOT safety signoff.

This independent measurement binds 41 frozen Git objects to text depth,
heading IDs, citation occurrences and internal links. It neither asserts
claim/source support nor relaxes R336's canonical route/safety hard holds.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from preparedness.tools import r336_frozen_archive_integrity as r336

SCHEMA = 'fv-preparedness-r337-measurement-part-v1'
SOURCE_COMMIT = '05fa47e24f5d7bb17ce40a3737242983706e57c7'
PRIOR_WITNESS_BLOB = 'ff714125b0e785248819acc1358f912b470f4a69'
PARTS = ((1, 0, 9), (2, 9, 18), (3, 18, 27), (4, 27, 36), (5, 36, 41))
TAG = re.compile(r'<[^>]+>')
TOKEN = re.compile(r'\{\{(?:cite|link):[^}]*\}\}')
ENTITY = re.compile(r'&(?:[A-Za-z]+|#[0-9]+|#x[0-9A-Fa-f]+);')
WORD = re.compile(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*")
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
LINK = re.compile(r'\{\{link:([a-z0-9-]+)(?:\|[^}]*)?\}\}')
HEAD = re.compile(r'<h[1-6]\b[^>]*\bid=["\']([^"\']+)["\'][^>]*>', re.I)
FALSE_FLAGS = ('qualified_qd_pass', 'may_merge', 'may_publish', 'commercial_sku_verified')


def measured(body: str) -> dict:
    clean = ENTITY.sub(' ', TOKEN.sub(' ', TAG.sub(' ', body)))
    return {'word_units': len(WORD.findall(clean)),
            'citations': dict(sorted(Counter(CITE.findall(body)).items())),
            'links': dict(sorted(Counter(LINK.findall(body)).items())),
            'headings': HEAD.findall(body)}


def report(errors: list[str], rows: int = 0, words: int = 0, citations: int = 0) -> dict:
    return {'state': 'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors': errors, 'entries_checked': rows,
            'measured_ascii_word_units': words, 'citation_tokens': citations,
            'claim_support_verified': False, 'qualified_qd_pass': False,
            'may_merge': False, 'may_publish': False,
            'commerce_and_realized_revenue_verified': False}


def audit(root: Path, *, prior_witness: dict | None = None) -> dict:
    """Read only; all five separately pinned parts required. Always non-publishing."""
    errors: list[str] = []
    if prior_witness is None:
        try:
            raw_witness = (root / 'audits' / 'r336_frozen_41_entry_witness.json').read_bytes()
            if r336.git_blob(raw_witness) != PRIOR_WITNESS_BLOB:
                return report(['R336_WITNESS_GIT_BLOB_DRIFT'])
            prior_witness = json.loads(raw_witness.decode('utf-8'))
        except (OSError, ValueError, UnicodeError):
            return report(['MISSING_OR_INVALID_R336_AUTHENTIC_WITNESS'])
    if prior_witness.get('schema') != r336.SCHEMA or len(prior_witness.get('entries', [])) != 41:
        return report(['R336_WITNESS_IDENTITY_INVALID'])
    if prior_witness.get('release_state') != 'DRAFT_HARD_HOLD' or any(prior_witness.get(k) is not False for k in (
        'qualified_qd_pass', 'published_or_live', 'commercial_sku_verified')):
        return report(['FORGED_PRIOR_RELEASE_STATE'])
    expected = prior_witness['entries']
    if len({(e.get('kind'),e.get('slug')) for e in expected}) != 41:
        return report(['DUPLICATE_PRIOR_ENTRY'])
    prior_git = None
    all_rows = []
    for number, start, end in PARTS:
        part_file = root / 'audits' / f'r337_source_metrics_part_{number:02d}.json'
        try:
            part = json.loads(part_file.read_text('utf-8'))
        except (OSError, ValueError, UnicodeError):
            errors.append(f'MISSING_OR_INVALID_MEASURED_PART:{number:02d}')
            continue
        if part.get('schema') != SCHEMA or part.get('part') != number or part.get('range') != [start,end]:
            errors.append(f'MEASUREMENT_PART_IDENTITY_DRIFT:{number:02d}')
        if part.get('source_commit') != SOURCE_COMMIT:
            errors.append(f'MEASUREMENT_SOURCE_COMMIT_DRIFT:{number:02d}')
        if prior_git is None:
            prior_git = part.get('r336_witness_blob')
        if part.get('r336_witness_blob') != prior_git or prior_git != PRIOR_WITNESS_BLOB:
            errors.append(f'MEASUREMENT_PREVIOUS_WITNESS_PIN_DRIFT:{number:02d}')
        rows = part.get('rows')
        if not isinstance(rows, list) or len(rows) != end-start:
            errors.append(f'MEASUREMENT_PART_COUNT_DRIFT:{number:02d}')
            continue
        all_rows.extend(rows)
    if len(all_rows) != 41:
        return report(errors + ['INCOMPLETE_41_ENTRY_MEASUREMENT'], len(all_rows))
    total_words = total_citations = 0
    for idx,(row,old) in enumerate(zip(all_rows,expected)):
        key = f"{old.get('kind')}:{old.get('slug')}"
        if any(row.get(k) != old.get(k) for k in ('kind','slug','route','body_blob','meta_blob')):
            errors.append('MEASUREMENT_IDENTITY_DRIFT:' + key)
            continue
        if row.get('min_utf8_bytes') != old.get('body_min_bytes'):
            errors.append('SOURCE_BYTE_FLOOR_DRIFT:' + key)
        if row.get('word_units') is None or type(row.get('word_units')) is not int or row['word_units'] < 1:
            errors.append('INVALID_WORD_WITNESS:' + key)
        if not isinstance(row.get('citations'), dict) or not isinstance(row.get('links'), dict) or not isinstance(row.get('headings'), list):
            errors.append('INVALID_SOURCE_TOKEN_WITNESS:' + key)
            continue
        if not isinstance(row.get('slug'), str) or not r336.SLUG.fullmatch(row['slug']) or row.get('kind') not in ('articles','tools'):
            errors.append('UNSAFE_CONTENT_PATH:' + key)
            continue
        base = root / 'content' / row['kind'] / row['slug']
        try:
            body_bytes = base.with_suffix('.body.html').read_bytes()
            meta_bytes = base.with_suffix('.meta.json').read_bytes()
            body = body_bytes.decode('utf-8')
            meta = json.loads(meta_bytes.decode('utf-8'))
        except (OSError, UnicodeError, ValueError):
            errors.append('MISSING_AUTHENTIC_SOURCE:' + key)
            continue
        if r336.git_blob(body_bytes) != row['body_blob'] or r336.git_blob(meta_bytes) != row['meta_blob']:
            errors.append('SOURCE_CHANGED_REQUIRES_HUMAN_REPIN:' + key)
        if len(body_bytes) < row['min_utf8_bytes']:
            errors.append('SOURCE_BYTE_DEPTH_LOSS:' + key)
        m = measured(body)
        if m['word_units'] != row['word_units']:
            errors.append('MEASURED_READING_DEPTH_DRIFT:' + key)
        for field,code in (('citations','CITATION_COUNTS_DRIFT'),('links','INTERNAL_LINK_COUNTS_DRIFT'),('headings','HEADING_IDS_DRIFT')):
            if m[field] != row[field]:
                errors.append(code + ':' + key)
        if len(set(m['headings'])) != len(m['headings']):
            errors.append('DUPLICATE_HEADING_ID:' + key)
        ids = meta.get('source_use',{})
        if not isinstance(ids,dict) or not set(m['citations']).issubset(ids):
            errors.append('CITATION_NOT_IN_SOURCE_USE:' + key)
        if meta.get('status',{}).get('publish') != 'draft':
            errors.append('PUBLICATION_STATE_CHANGED:' + key)
        total_words += m['word_units']
        total_citations += sum(m['citations'].values())
    return report(errors, len(all_rows), total_words, total_citations)


def main() -> int:
    ap = argparse.ArgumentParser(description='Read-only R337 Preparedness lexical source custody. Never releases content.')
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    ns = ap.parse_args()
    print(json.dumps(audit(ns.root.resolve()), indent=2,sort_keys=True))
    return 2  # always DRAFT / HARD HOLD, even when deterministic integrity passes


if __name__ == '__main__':
    raise SystemExit(main())
