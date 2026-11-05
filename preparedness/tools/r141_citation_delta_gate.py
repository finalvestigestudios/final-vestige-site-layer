#!/usr/bin/env python3
"""R141: fail-closed, read-only occurrence-level audit of contributor citation drift.

Exact baseline source identity is pinned to R140. Passing this structural audit never
establishes source correctness, medical safety, QD review, commerce or release approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

R140_MANIFEST_BLOB = 'a839c53bc3b6f7c72c7eaf1c901edae02664007e'
EXPECTED_CLUSTERS = frozenset(('start', 'shelter', 'food', 'health', 'histfood', 'histhome', 'histfield'))
SHA40 = re.compile(r'[a-f0-9]{40}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
SOURCE = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
CITE = re.compile(r'\{\{cite:([^}]+)\}\}')
RELEASE = 'DRAFT_HOLD_HUMAN_SOURCE_SAFETY_AND_QD_REVIEW_REQUIRED'
FIELDS = {'schema', 'r140_rc_sha', 'r140_manifest_blob', 'article_deltas', 'review_state'}
ARTICLE_FIELDS = {'slug', 'cluster', 'rc_blob', 'contributor_blob', 'counts'}
COUNT_FIELDS = {'id', 'rc', 'contributor'}


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def citation_counts(raw: bytes) -> Counter[str]:
    html = raw.decode('utf-8', errors='strict')
    return Counter(CITE.findall(html))


def _check_unsafe_path(p: Path, anchor: Path) -> None:
    if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(anchor.resolve()):
        raise ValueError(f'missing, symlink or escaping article: {p}')


def validate_docket(manifest: dict, manifest_bytes: bytes, docket: dict) -> list[dict]:
    if git_blob(manifest_bytes) != R140_MANIFEST_BLOB:
        raise ValueError('R140 frozen manifest Git blob differs: stop, no rebaseline here')
    if not isinstance(manifest, dict) or set(manifest) != {'schema', 'rc_sha', 'branch_heads', 'drifts', 'source_note'}:
        raise ValueError('invalid R140 manifest structure')
    if manifest['schema'] != 'R140-INTAKE-1' or not isinstance(manifest['rc_sha'], str) or not SHA40.fullmatch(manifest['rc_sha']):
        raise ValueError('invalid R140 release identity')
    heads = manifest['branch_heads']
    if not isinstance(heads, dict) or set(heads) != EXPECTED_CLUSTERS or any(not isinstance(s, str) or not SHA40.fullmatch(s) for s in heads.values()):
        raise ValueError('missing or malformed contributor heads')
    if not isinstance(docket, dict) or set(docket) != FIELDS:
        raise ValueError('unexpected docket fields, including attempted approvals')
    if docket['schema'] != 'R141-CITATION-OCCURRENCE-1' or docket['r140_rc_sha'] != manifest['rc_sha'] or docket['r140_manifest_blob'] != R140_MANIFEST_BLOB:
        raise ValueError('docket not anchored to the exact R140 freeze')
    if docket['review_state'] != 'UNREVIEWED_HUMAN_REQUIRED':
        raise ValueError('human safety/source/approval states cannot be changed')
    rows = docket['article_deltas']
    if not isinstance(rows, list) or len(rows) != 14 or len(manifest['drifts']) != 14:
        raise ValueError('must enumerate every R140 drift exactly once')
    m = {}
    for original in manifest['drifts']:
        if not isinstance(original, dict) or not isinstance(original.get('slug'), str) or original['slug'] in m:
            raise ValueError('duplicate/malformed original article')
        m[original['slug']] = original
    seen = set()
    report = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != ARTICLE_FIELDS:
            raise ValueError('invalid article fields or unauthorized review approval')
        slug, cluster = row['slug'], row['cluster']
        if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug in seen or slug not in m:
            raise ValueError('duplicate, unknown or unsafe article slug')
        seen.add(slug)
        original = m[slug]
        if cluster != original['cluster'] or cluster not in EXPECTED_CLUSTERS:
            raise ValueError('wrong article author / contributor cluster')
        if row['rc_blob'] != original['baseline_blob'] or row['contributor_blob'] != original['contributor_blob']:
            raise ValueError('article Git blob substitutions detected')
        if any(not isinstance(row[f], str) or not SHA40.fullmatch(row[f]) for f in ('rc_blob', 'contributor_blob')):
            raise ValueError('malformed Git blob')
        counts = row['counts']
        if not isinstance(counts, list):
            raise ValueError('counts must be a list')
        used = set()
        delta = 0
        removed = set()
        added = set()
        for c in counts:
            if not isinstance(c, dict) or set(c) != COUNT_FIELDS:
                raise ValueError('unexpected count entry fields')
            sid = c['id']
            if not isinstance(sid, str) or not SOURCE.fullmatch(sid) or sid in used:
                raise ValueError('duplicate or malformed source ID')
            used.add(sid)
            old, new = c['rc'], c['contributor']
            if type(old) is not int or type(new) is not int or old < 0 or new < 0 or old == new:
                raise ValueError('invalid or unchanged source occurrence delta')
            delta += new - old
            if old and not new: removed.add(sid)
            if new and not old: added.add(sid)
        if delta != original['contributor_citations'] - original['baseline_citations']:
            raise ValueError('citation net loss masked by incomplete count changes')
        if removed != set(original['removed_source_ids']) or added != set(original['added_source_ids']):
            raise ValueError('lost or added citation source identity mismatch')
        if original['baseline_citations'] < 1 or original['contributor_citations'] < 1:
            raise ValueError('empty cited article')
        if (original['baseline_words'] > original['contributor_words'] and not counts) and cluster not in ('start', 'shelter'):
            raise ValueError('unclassified depth loss')
        kind = ('SOURCE_IDENTITY_RETARGET_HOLD' if added or removed else
                'CITATION_OCCURRENCE_CHANGE_HOLD' if counts else
                'PROSE_OR_PROVENANCE_DRIFT_HOLD')
        report.append({'slug': slug, 'cluster': cluster, 'kind': kind,
                       'total_rc_citations': original['baseline_citations'],
                       'total_contributor_citations': original['contributor_citations'],
                       'changed_source_counts': len(counts), 'human_review': 'REQUIRED'})
    if seen != set(m):
        raise ValueError('missing original author evidence')
    return sorted(report, key=lambda r: r['slug'])


def verify_files(root: Path, rows: list[dict], *, version: str, anchor: Path | None = None) -> list[str]:
    if version not in ('rc', 'contributor'):
        raise ValueError('unknown file version')
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f'checkout missing: {root}')
    matched = []
    for r in rows:
        p = root / 'preparedness' / 'content' / 'articles' / (r['slug'] + '.body.html')
        _check_unsafe_path(p, root)
        raw = p.read_bytes()
        field = 'rc_blob' if version == 'rc' else 'contributor_blob'
        if git_blob(raw) != r[field]:
            raise ValueError(f'{r["slug"]}: {version} bytes differ from independently observed Git blob')
        matched.append(r['slug'])
    return matched


def verify_occurrences(root: Path, docket: dict, manifest: dict, *, version: str) -> int:
    root = root.resolve()
    originals = {r['slug']: r for r in manifest['drifts']}
    for row in docket['article_deltas']:
        slug = row['slug']
        raw = (root / 'preparedness' / 'content' / 'articles' / (slug + '.body.html')).read_bytes()
        cnt = citation_counts(raw)
        orig = originals[slug]
        expected_total = orig['baseline_citations'] if version == 'rc' else orig['contributor_citations']
        if sum(cnt.values()) != expected_total:
            raise ValueError(f'{slug}: unexpected total citation occurrences')
        for entry in row['counts']:
            expected = entry[version]
            if cnt[entry['id']] != expected:
                raise ValueError(f'{slug}: {entry["id"]} count not equal to independently observed record')
    return len(docket['article_deltas'])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', required=True, type=Path)
    ap.add_argument('--docket', required=True, type=Path)
    ap.add_argument('--root', required=True, type=Path)
    ap.add_argument('--contributor-root', type=Path, help='optional separately staged exact 14 contributor article bodies')
    ap.add_argument('--report', type=Path, help='optional JSON report, never an approval artifact')
    args = ap.parse_args(argv)
    result = {'status': RELEASE, 'source_review': 'UNREVIEWED_HUMAN_REQUIRED',
              'QD': 'NOT_APPROVED', 'article_diff_verification': 'BLOCKED'}
    try:
        raw = args.manifest.read_bytes()
        manifest = json.loads(raw)
        docket = json.loads(args.docket.read_text(encoding='utf-8'))
        result['deltas'] = validate_docket(manifest, raw, docket)
        matched = verify_files(args.root, docket['article_deltas'], version='rc')
        verify_occurrences(args.root, docket, manifest, version='rc')
        result['exact_rc_articles_verified'] = len(matched)
        if args.contributor_root is None:
            result['article_diff_verification'] = 'HOLD_CONTRIBUTOR_BYTES_NOT_STAGED'
        else:
            staged = verify_files(args.contributor_root, docket['article_deltas'], version='contributor')
            verify_occurrences(args.contributor_root, docket, manifest, version='contributor')
            result['exact_contributor_articles_verified'] = len(staged)
            result['article_diff_verification'] = 'MATCHED_BLOB_AND_CITATION_COUNTS_NOT_CONTENT_APPROVAL'
    except (ValueError, OSError, UnicodeError, KeyError, TypeError, json.JSONDecodeError) as exc:
        result['article_diff_verification'] = 'HOLD_INVALID_OR_MISSING_EVIDENCE'
        result['error'] = str(exc)
        code = 2
    else:
        code = 0
    payload = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.report:
        args.report.write_text(payload, encoding='utf-8')
    else:
        print(payload)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
