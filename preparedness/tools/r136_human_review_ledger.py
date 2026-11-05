#!/usr/bin/env python3
"""Custody-bound reviewer notes for R135 tasks: never a source, safety or release approval.

A local/exported review sheet is *unsigned reviewer evidence*, not an authorization.
The CLI regenerates the R135 queue through R134/R133 before considering notes.
No article, source register, CMS, publication, merchant or metrics writes occur.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))  # Python -I excludes the script directory.
from r135_review_queue import fingerprint, review_queue, ReviewHold

HOLD = 'HOLD_REVIEW_RECORDS_NOT_RELEASE_APPROVAL'
OPEN = 'OPEN'
OUTCOMES = frozenset((OPEN, 'EVIDENCE_LOGGED_NOT_APPROVED',
                      'NEEDS_CORRECTION', 'INSUFFICIENT_EVIDENCE'))
TASK_ID = re.compile(r'^(SOURCE|PASSAGE)-[a-f0-9]{20}$')
SHA256 = re.compile(r'^[a-f0-9]{64}$')
URL = re.compile(r'^https://[^\s/#?]+(?:[^\s]*)$')
UTC = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
FIELDS = ('task_id', 'kind', 'outcome', 'reviewer_reference', 'reviewed_at_utc',
          'evidence_url', 'evidence_passage', 'source_scope_analysis',
          'specialist_review_reference', 'proposed_correction')


def require(ok: bool, code: str) -> None:
    if not ok:
        raise ReviewHold(code)


def source_task_key(t: dict) -> str:
    return t['task_id']


def validate_queue(queue: dict) -> dict[str, str]:
    """R135 is generated from real custody by the CLI; this is a second shape gate."""
    require(isinstance(queue, dict) and queue.get('status') ==
            'HOLD_HUMAN_SOURCE_AND_SAFETY_ADJUDICATION', 'UPSTREAM_HOLD_REQUIRED')
    for k in ('may_publish', 'qd_pass', 'medical_safety_verified',
              'merchant_offer_verified'):
        require(queue.get(k) is False, 'UNAUTHORIZED_GATE:' + k)
    p, s = queue.get('provenance'), queue.get('summary')
    require(isinstance(p, dict) and isinstance(s, dict) and
            isinstance(p.get('candidate_parent'), str) and p['candidate_parent'] and
            type(p.get('article_count')) is int and p['article_count'] == 35 and
            type(p.get('citation_occurrences')) is int and
            p['citation_occurrences'] == 2000 and
            type(s.get('crosswalk_groups_requiring_human_review')) is int and
            s['crosswalk_groups_requiring_human_review'] == 32,
            'ROSTER_OR_CITATION_DRIFT')
    groups, passages = queue.get('source_group_tasks'), queue.get('safety_passage_tasks')
    require(isinstance(groups, list) and len(groups) == 32 and
            isinstance(passages, list) and len(passages) ==
            s.get('risk_passages_requiring_human_review'), 'TASK_COUNT_DRIFT')
    require({x.get('crosswalk_group_index') for x in groups if isinstance(x, dict)}
            == set(range(1, 33)), 'GROUP_ID_DRIFT')
    tasks: dict[str, str] = {}
    for kind, collection in [('source', groups), ('passage', passages)]:
        for t in collection:
            require(isinstance(t, dict), 'INVALID_TASK')
            tid = t.get('task_id')
            require(isinstance(tid, str) and TASK_ID.fullmatch(tid) is not None and
                    tid.startswith(kind.upper() + '-') and tid not in tasks and
                    t.get('decision') == 'UNREVIEWED_HUMAN_REQUIRED',
                    'FORGED_OR_DUPLICATE_TASK_ID')
            if kind == 'source':
                variants = t.get('cited_variant_identities_only')
                require(isinstance(variants, list) and len(variants) > 0 and
                        all(isinstance(v, list) and len(v) == 3 and
                            all(isinstance(z, str) and z for z in v) for v in variants),
                        'MISSING_ORIGIN_SOURCE_VARIANTS')
            else:
                digest = t.get('witness_sha256')
                require(isinstance(digest, str) and SHA256.fullmatch(digest) is not None
                        and tid == 'PASSAGE-' + digest[:20] and
                        isinstance(t.get('risk_families_for_triage_only'), list),
                        'PASSAGE_WITNESS_DRIFT')
            tasks[tid] = kind
    return tasks


def template(queue: dict) -> dict:
    tasks = validate_queue(queue)
    return {
        'purpose': 'UNSIGNED_HUMAN_REVIEW_NOT_SAFETY_OR_QD_APPROVAL',
        'queue_sha256': fingerprint(queue),
        'candidate_parent': queue['provenance']['candidate_parent'],
        'records': [dict(zip(FIELDS, (tid, kind, OPEN, '', '', '', '', '', '', '')))
                    for tid, kind in sorted(tasks.items())],
    }


def _validate_time(value: str) -> bool:
    if not isinstance(value, str) or UTC.fullmatch(value) is None:
        return False
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).isoformat() != ''
    except ValueError:
        return False


def reconcile(queue: dict, sheet: dict) -> dict:
    """Check review-note provenance/coverage without conferring ANY approval."""
    expected = template(queue)
    require(isinstance(sheet, dict) and set(sheet) == set(expected) and
            sheet['purpose'] == expected['purpose'] and
            sheet['queue_sha256'] == expected['queue_sha256'] and
            sheet['candidate_parent'] == expected['candidate_parent'],
            'REVIEW_SHEET_NOT_BOUND_TO_CURRENT_QUEUE')
    raw = sheet.get('records')
    require(isinstance(raw, list) and len(raw) == len(expected['records']),
            'REVIEW_TASK_COVERAGE_INCOMPLETE')
    valid = {r['task_id']: r['kind'] for r in expected['records']}
    seen: set[str] = set()
    counts = {key: 0 for key in OUTCOMES}
    for r in raw:
        require(isinstance(r, dict) and set(r) == set(FIELDS), 'REVIEW_RECORD_SHAPE_DRIFT')
        tid, kind, outcome = r['task_id'], r['kind'], r['outcome']
        require(isinstance(tid, str) and tid in valid and tid not in seen and
                kind == valid[tid] and outcome in OUTCOMES,
                'UNKNOWN_DUPLICATE_OR_FORGED_DECISION')
        seen.add(tid)
        for key in FIELDS[3:]:
            require(isinstance(r[key], str) and len(r[key]) <= 4000,
                    'INVALID_REVIEW_FIELD:' + key)
        if outcome == OPEN:
            require(all(r[key] == '' for key in FIELDS[3:]),
                    'OPEN_TASK_CANNOT_CLAIM_REVIEW')
        else:
            require(bool(r['reviewer_reference'].strip()) and
                    bool(r['source_scope_analysis'].strip()) and
                    _validate_time(r['reviewed_at_utc']) and
                    URL.fullmatch(r['evidence_url']) is not None and
                    bool(r['evidence_passage'].strip()),
                    'DOCUMENTED_REVIEW_EVIDENCE_REQUIRED')
            if kind == 'passage':
                passages = {x['task_id']: x for x in queue['safety_passage_tasks']}
                families = passages[tid]['risk_families_for_triage_only']
                if ('medicine-medical-dependency' in families or
                    'power-fire-carbon-monoxide' in families):
                    require(bool(r['specialist_review_reference'].strip()),
                            'HIGH_CONSEQUENCE_SPECIALIST_REFERENCE_REQUIRED')
            if outcome == 'NEEDS_CORRECTION':
                require(bool(r['proposed_correction'].strip()),
                        'CORRECTION_DESCRIPTION_REQUIRED')
        counts[outcome] += 1
    require(seen == set(valid), 'UNMATCHED_REVIEW_TASKS')
    return {'status': HOLD, 'may_publish': False, 'qd_pass': False,
            'medical_safety_verified': False, 'merchant_offer_verified': False,
            'human_approval_auto_granted': False,
            'queue_sha256': expected['queue_sha256'],
            'total_review_tasks': len(valid),
            'source_groups_total': 32,
            'recorded_outcomes': {k: counts[k] for k in sorted(counts)},
            'warning': 'Reviewer inputs are unsigned notes and require independent qualification, source adjudication, native QA, separate QD and founder release. NEVER publish from this output.'}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path('.'))
    ap.add_argument('--review-records', type=Path,
                    help='Optional private local review JSON; never committed as an approval ledger')
    args = ap.parse_args(argv)
    try:
        from r133_snapshot_gate import load_json
        from r134_reviewer_packet import packet
        manifest = load_json((args.root / 'preparedness/docs/r133/locked_files.json').read_bytes())
        upstream = review_queue(packet(args.root, manifest))
        sheet = (json.loads(args.review_records.read_text(encoding='utf-8'))
                 if args.review_records else template(upstream))
        print(json.dumps({'template': sheet, 'audit': reconcile(upstream, sheet)},
                         sort_keys=True, ensure_ascii=False, indent=2))
        return 0
    except (ReviewHold, OSError, ValueError, TypeError, KeyError, UnicodeError, ImportError) as exc:
        print('HOLD: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
