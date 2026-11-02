#!/usr/bin/env python3
"""R63 PRIVATE HOLD: lossless two-version source-record/citation impact crosswalk.

All seven contributor inventories (including uncited sources) are retained.
A shared URL/ID is never evidence of source equivalence or claim support.
This program requires R61's fresh Git-object provenance check via subprocess.
"""
from __future__ import annotations

import argparse
import importlib.util
from collections import defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

_parent_path = Path(__file__).with_name('r62_contributor_claim_context_docket.py')
if not _parent_path.is_file() or _parent_path.is_symlink():
    raise ImportError('R62 original claim-context custody gate missing')
_spec = importlib.util.spec_from_file_location('r63_r62_dependency', _parent_path)
if _spec is None or _spec.loader is None:
    raise ImportError('R62 original gate could not be loaded')
r62 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r62)

SCHEMA = 'r63-private-contributor-source-impact-crosswalk-v1'
NOTE_SCHEMA = 'r63-unsigned-source-review-notes-v1'
FIELDS = ('work_order_sha256', 'cluster', 'source_id', 'change_kind',
          'frozen_record_sha256', 'observed_record_sha256',
          'frozen_citations', 'observed_citations',
          'frozen_source_uses', 'observed_source_uses',
          'shared_url_identity_risk', 'changed_field_count',
          'reviewer_note_UNTRUSTED')
KINDS = frozenset(('ADDED_NOT_APPROVED', 'REMOVED_NOT_ALIASED',
                   'CHANGED_NOT_APPROVED', 'UNCHANGED_NOT_REVERIFIED'))
HOLD = ('may_publish', 'independent_QD_approval', 'qualified_safety_clearance',
        'human_source_links_verified')
MAX_CSV_BYTES = 8_000_000
MAX_JSON_BYTES = 24_000_000


class SourceHold(ValueError):
    """Review evidence incomplete, manipulated, or deceptively approved."""


def need(condition, reason):
    if not condition:
        raise SourceHold(reason)


def read_ledger(lineage, docket):
    """Recompute R62 from the complete R61 packet; never trust a saved summary."""
    need(type(lineage) is dict and type(docket) is dict,
         'R61/R62 source custody packets required')
    try:
        r62.verify_report(docket, lineage)
    except (r62.ReviewHold, ValueError, TypeError, KeyError) as exc:
        raise SourceHold('R62 original claim-context custody did not verify') from exc
    need(lineage.get('existing_R14_exception_remains_open') is True and
         all(lineage.get(k) is False and docket.get(k) is False for k in HOLD),
         'release-state assertion or frozen provenance exception changed')
    usage = {v: defaultdict(lambda: {'citations': [], 'source_uses': []})
             for v in ('frozen', 'observed')}
    outside = {'frozen': [], 'observed': []}
    expected = {'frozen': 0, 'observed': 0}
    mapping_expected = {'frozen': 0, 'observed': 0}
    for article in lineage['per_article_citation_and_context_lineage_NOT_REVIEWED']:
        group, slug = article['cluster'], article['slug']
        for v in ('frozen', 'observed'):
            part = article['versions'][v]
            for ordinal, occurrence in enumerate(
                    part['citation_occurrences_in_original_order'], 1):
                candidates = occurrence['candidate_contributor_readings_NOT_CLAIM_SUPPORT']
                ref = {'article_cluster': group, 'article_slug': slug,
                       'citation_ordinal': ordinal, 'source_id': occurrence['source_id'],
                       'article_body_sha256': part['body_sha256'],
                       'offset_codepoints': occurrence['offset_codepoints'],
                       'unabridged_context_NOT_SUPPORT_PROOF':
                           occurrence['unabridged_local_context']}
                if not candidates:
                    outside[v].append({'kind': 'CITATION_OUTSIDE_SEVEN_CLUSTERS',
                                       'ref': ref})
                for candidate in candidates:
                    usage[v][(candidate['cluster'], occurrence['source_id'])][
                        'citations'].append({
                            **ref,
                            'candidate_record_sha256_NOT_CLAIM_PROOF':
                                candidate['source_record_sha256']})
                    expected[v] += 1
            for sid, note in sorted(part['full_source_use_mapping_UNABRIDGED'].items()):
                matches = [x for group_row in lineage[
                    'source_inventories_BOTH_VERSIONS_UNREVIEWED']
                    for x in group_row[
                        'all_original_reading_records_UNABRIDGED' if v == 'frozen'
                        else 'all_observed_reading_records_UNABRIDGED_UNVERIFIED']
                    if x['id'] == sid]
                clusters = [g['cluster'] for g in lineage[
                    'source_inventories_BOTH_VERSIONS_UNREVIEWED']
                    if any(x['id'] == sid for x in g[
                        'all_original_reading_records_UNABRIDGED' if v == 'frozen'
                        else 'all_observed_reading_records_UNABRIDGED_UNVERIFIED'])]
                ref = {'article_cluster': group, 'article_slug': slug,
                       'source_id': sid, 'article_body_sha256': part['body_sha256'],
                       'source_use_note_UNABRIDGED_NOT_CLAIM_PROOF': note}
                if not matches:
                    outside[v].append({'kind': 'SOURCE_USE_OUTSIDE_SEVEN_CLUSTERS',
                                       'ref': ref})
                else:
                    need(len(matches) == len(clusters),
                         'duplicate source ID inside a contributor inventory')
                for cluster in clusters:
                    usage[v][(cluster, sid)]['source_uses'].append(ref)
                    mapping_expected[v] += 1
    return usage, outside, expected, mapping_expected


def make_report(lineage, docket):
    usage, outside, expected, mapping_expected = read_ledger(lineage, docket)
    records, counts = [], {'frozen': 0, 'observed': 0}
    kinds = defaultdict(int)
    source_groups = lineage['source_inventories_BOTH_VERSIONS_UNREVIEWED']
    source_sha = r62.digest
    collided = {'frozen': set(), 'observed': set()}
    for v in ('frozen', 'observed'):
        for item in docket['exact_url_shared_identity_groups_NO_DEDUP'][v]:
            for row in item['distinct_readings']:
                collided[v].add((row['cluster'], row['source_id']))
    for group in sorted(source_groups, key=lambda row: row['cluster']):
        cluster = group['cluster']
        pairs = {}
        for v, key in (('frozen', 'all_original_reading_records_UNABRIDGED'),
                       ('observed', 'all_observed_reading_records_UNABRIDGED_UNVERIFIED')):
            pairs[v] = {row['id']: row for row in group[key]}
        for sid in sorted(pairs['frozen'].keys() | pairs['observed'].keys()):
            old, new = pairs['frozen'].get(sid), pairs['observed'].get(sid)
            if old is None:
                kind = 'ADDED_NOT_APPROVED'
            elif new is None:
                kind = 'REMOVED_NOT_ALIASED'
            elif old != new:
                kind = 'CHANGED_NOT_APPROVED'
            else:
                kind = 'UNCHANGED_NOT_REVERIFIED'
            changed = sorted(
                key for key in (set(old or {}) | set(new or {}))
                if (old or {}).get(key, object()) != (new or {}).get(key, object())
            ) if old is not None and new is not None else sorted(
                (old or new).keys())
            # Missing vs explicit null values are distinct, including on changed keys.
            if old is not None and new is not None:
                changed = sorted(key for key in old.keys() | new.keys()
                                 if (key in old) != (key in new)
                                 or (key in old and key in new and old[key] != new[key]))
            versions = {}
            for v, row in (('frozen', old), ('observed', new)):
                if row is None:
                    versions[v] = None
                    continue
                counts[v] += 1
                refs = usage[v].pop((cluster, sid),
                                    {'citations': [], 'source_uses': []})
                versions[v] = {
                    'record_sha256': source_sha(row),
                    'unabridged_contributor_reading_NOT_HUMAN_CHECKED': row,
                    'candidate_citation_occurrences_NOT_SUPPORT_PROOF':
                        refs['citations'],
                    'article_source_use_notes_UNABRIDGED_NOT_SUPPORT_PROOF':
                        refs['source_uses'],
                    'same_exact_url_distinct_identity_NOT_ALIAS':
                        (cluster, sid) in collided[v]}
            identity = {'cluster': cluster, 'source_id': sid,
                        'frozen_sha256': source_sha(old) if old is not None else None,
                        'observed_sha256': source_sha(new) if new is not None else None,
                        'change_kind': kind}
            records.append({
                'work_order_sha256': source_sha(identity),
                'cluster': cluster, 'source_id': sid,
                'change_kind': kind, 'changed_source_fields_NOT_APPROVED': changed,
                'versions': versions, 'human_source_review': 'NOT_REVIEWED',
                'qualified_claim_safety_review': 'NOT_REVIEWED'})
            kinds[kind] += 1
    need(not any(usage[v] for v in usage),
         'candidate citation/source-use links were lost from source inventory')
    for v in ('frozen', 'observed'):
        need(counts[v] == sum(
            row['original_source_record_count' if v == 'frozen'
                else 'observed_source_record_count'] for row in source_groups),
            'an original or observed contributor source record disappeared')
        need(sum(len(row['versions'][v][
            'candidate_citation_occurrences_NOT_SUPPORT_PROOF'])
            for row in records if row['versions'][v]) == expected[v],
            'citation candidate occurrence coverage drift')
        need(sum(len(row['versions'][v][
            'article_source_use_notes_UNABRIDGED_NOT_SUPPORT_PROOF'])
            for row in records if row['versions'][v]) == mapping_expected[v],
            'source-use note coverage drift')
    need(len({row['work_order_sha256'] for row in records}) == len(records),
         'non-unique source review work orders')
    report = {
        'schema': SCHEMA, 'issue': 136, 'release_state': 'HOLD',
        'machine_only': True, 'parent_R61_sha256': lineage['fingerprint_sha256'],
        'parent_R62_sha256': docket['fingerprint_sha256'],
        'source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS': records,
        'citation_or_source_use_outside_seven_clusters_NOT_ALIASED': outside,
        'source_id_collisions_NO_ALIAS':
            docket['source_id_collisions_NO_ALIAS'],
        'exact_url_shared_identity_groups_NO_DEDUP':
            docket['exact_url_shared_identity_groups_NO_DEDUP'],
        'counts': {'work_orders': len(records),
                   'original_source_records': counts['frozen'],
                   'observed_source_records_UNVERIFIED': counts['observed'],
                   'kinds': dict(sorted(kinds.items())),
                   'candidate_citation_links_BOTH_VERSIONS': expected,
                   'source_use_links_BOTH_VERSIONS': mapping_expected,
                   'outside_seven_cluster_references': {
                       v: len(outside[v]) for v in outside}},
        'full_35_article_R58_custody_NOT_REVALIDATED': True,
        'original_R14_contributor_provenance_HOLD': True,
        'not_verified': ('No source URL or reading note is independently checked; '
                         'citation/source-use linkage is not proof of claim support. '
                         'Observed contributor records remain proposals, even if '
                         'unchanged IDs or URLs appear. No qualified medical or '
                         'emergency safety review, independent QD or publication.'),
        **{k: False for k in HOLD},
    }
    report['fingerprint_sha256'] = r62.digest(report)
    return report


def verify_report(report, lineage, docket):
    need(type(report) is dict and report == make_report(lineage, docket),
         'source impact crosswalk differs from regenerated Git-based parent evidence')
    return True


def csv_workbook(report, lineage, docket):
    verify_report(report, lineage, docket)
    out = io.StringIO(newline='')
    w = csv.writer(out, quoting=csv.QUOTE_ALL, lineterminator='\n')
    w.writerow(FIELDS)
    for row in report['source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS']:
        a, b = row['versions']['frozen'], row['versions']['observed']
        w.writerow((row['work_order_sha256'], row['cluster'], row['source_id'],
                    row['change_kind'],
                    a['record_sha256'] if a else '',
                    b['record_sha256'] if b else '',
                    len(a['candidate_citation_occurrences_NOT_SUPPORT_PROOF']) if a else 0,
                    len(b['candidate_citation_occurrences_NOT_SUPPORT_PROOF']) if b else 0,
                    len(a['article_source_use_notes_UNABRIDGED_NOT_SUPPORT_PROOF'])
                    if a else 0,
                    len(b['article_source_use_notes_UNABRIDGED_NOT_SUPPORT_PROOF'])
                    if b else 0,
                    str(any(v['same_exact_url_distinct_identity_NOT_ALIAS']
                            for v in (a, b) if v)).lower(),
                    len(row['changed_source_fields_NOT_APPROVED']), ''))
    return out.getvalue().encode('utf-8')


def quarantine_notes(report, lineage, docket, returned):
    """Unsigned notes only. Never accept decision/status or approval columns."""
    baseline = csv_workbook(report, lineage, docket)
    need(type(returned) is bytes and len(returned) <= MAX_CSV_BYTES,
         'missing or oversized returned source review worksheet')
    try:
        submitted = list(csv.reader(io.StringIO(returned.decode('utf-8', 'strict'),
                                                newline=''), strict=True))
        original = list(csv.reader(io.StringIO(baseline.decode('utf-8'),
                                               newline=''), strict=True))
    except (UnicodeError, csv.Error) as exc:
        raise SourceHold('invalid UTF-8 or CSV reader data') from exc
    need(len(submitted) == len(original) and submitted[0] == list(FIELDS),
         'review worksheet column/record count modified')
    notes = []
    for index, (row, frozen) in enumerate(zip(submitted[1:], original[1:]), 1):
        need(len(row) == len(FIELDS) and row[:-1] == frozen[:-1],
             'protected source/citation field or row order changed: ' + str(index))
        note = row[-1]
        normalized = unicodedata.normalize('NFKC', note)
        need(len(note) <= 3000 and
             not any(unicodedata.category(c) in ('Cc', 'Cf', 'Cs', 'Zl', 'Zp')
                     for c in note) and
             not normalized.lstrip().startswith(('=', '+', '-', '@')),
             'reviewer note contains control/spoofing/formula text')
        if note:
            notes.append({'work_order_sha256': frozen[0],
                          'row_ordinal': index,
                          'untrusted_note_NOT_VERIFIED': note,
                          'review_state': 'UNTRUSTED_NOT_REVIEWED'})
    quarantine = {
        'schema': NOTE_SCHEMA, 'issue': 136, 'release_state': 'HOLD',
        'machine_only': True,
        'parent_R63_sha256': report['fingerprint_sha256'],
        'returned_csv_sha256': hashlib.sha256(returned).hexdigest(),
        'unsigned_untrusted_source_notes': notes,
        **{k: False for k in HOLD},
    }
    quarantine['fingerprint_sha256'] = r62.digest(quarantine)
    return quarantine


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument('--remote', default='origin')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--summary', action='store_true')
    group.add_argument('--csv', action='store_true')
    args = parser.parse_args(argv)
    need(re.fullmatch(r'[A-Za-z0-9_-]+', args.remote),
         'remote must be a plain trusted Git remote name')
    parent = Path(__file__).with_name('r61_contributor_version_source_lineage.py')
    need(parent.is_file() and not parent.is_symlink(),
         'original Git-custody reviewer prerequisite not found')
    try:
        proc = subprocess.run(
            [sys.executable, '-I', str(parent),
             '--repo-root', str(args.repo_root), '--remote', args.remote],
            capture_output=True, check=False, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SourceHold('original R61 real-Git provenance was unavailable') from exc
    need(proc.returncode == 0 and 0 < len(proc.stdout) <= MAX_JSON_BYTES,
         'R61 Git-object provenance failed closed; no cached substitute permitted')
    try:
        lineage = r62.strict_load(proc.stdout.decode('utf-8', 'strict'))
        docket = r62.make_report(lineage)
        report = make_report(lineage, docket)
    except (UnicodeError, ValueError, TypeError, KeyError) as exc:
        raise SourceHold('trusted R61/R62 regeneration failed closed') from exc
    if args.csv:
        sys.stdout.buffer.write(csv_workbook(report, lineage, docket))
    else:
        obj = {'schema': SCHEMA, 'release_state': 'HOLD',
               'counts': report['counts'],
               'fingerprint_sha256': report['fingerprint_sha256']} if args.summary else report
        sys.stdout.write(json.dumps(obj, sort_keys=True, indent=2,
                                    ensure_ascii=False, allow_nan=False) + '\n')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (SourceHold, OSError) as exc:
        print('R63 PRIVATE SOURCE CUSTODY HOLD: ' + str(exc), file=sys.stderr)
        raise SystemExit(2)
