#!/usr/bin/env python3
"""R156 read-only, source-bound Family Reunification reviewer workorders.

Requires the frozen R154 + R155 gates and their underlying original source custody
in an authentic checkout. Structural success is DRAFT_HARD_HOLD (exit 2), never QD.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

R154_GATE = 'preparedness/tools/r154_review_triage_gate.py'
R154_BLOB = '96bf1114f75b53413f4d6cbef6fc69a2d81b4294'
R155_GATE = 'preparedness/tools/r155_family_source_observation_gate.py'
R155_BLOB = '2da35a444834579096f491bb3c91d92eb6f8af3b'
OBSERVATIONS = 'preparedness/docs/r155/family-source-observations.json'
OBS_BLOB = '9e689fde7e2913340c89886a7fb02994245b60eb'
SCHEMA = 'fv-preparedness-r156-family-review-workorders-v1'
FAMILY = 'family-reunification-card'
SHA256 = re.compile(r'^[a-f0-9]{64}$')
EXPECTED = {
    'shelter-ca-cde-safety-plans': ('RETRIEVED_TEXT', 'CLAIM_MATCH_OBSERVED'),
    'shelter-cdc-chemical-evac': ('RETRIEVED_TEXT', 'CLAIM_MATCH_OBSERVED'),
    'shelter-cdc-reunification': ('RETRIEVED_TEXT', 'CLAIM_MATCH_OBSERVED'),
    'shelter-co-oss-reunification': ('RETRIEVED_TEXT', 'SCOPE_REVIEW_REQUIRED'),
    'shelter-ncmec-hotline': ('RETRIEVED_TEXT', 'CONTEXT_REVIEW_REQUIRED'),
    'shelter-fema-reunification': ('RETRIEVAL_BLOCKED', 'NOT_OBSERVABLE'),
    'shelter-fcc-comms': ('RETRIEVAL_BLOCKED', 'NOT_OBSERVABLE'),
    'shelter-ready-evacuation': ('RETRIEVAL_BLOCKED', 'NOT_OBSERVABLE'),
    'shelter-ready-plan': ('RETRIEVAL_BLOCKED', 'NOT_OBSERVABLE'),
    'shelter-ready-plan-form': ('RETRIEVAL_BLOCKED', 'NOT_OBSERVABLE'),
    'shelter-ready-tech': ('RETRIEVAL_BLOCKED', 'NOT_OBSERVABLE'),
}
SPECIAL = {
    'shelter-co-oss-reunification': 'Find an exact page, linked document, or timestamp proving the attributed photo ID, pen, and limit-calls instructions; otherwise propose a precise citation/claim correction.',
    'shelter-ncmec-hotline': 'Distinguish the documented hotline from the CyberTipline web form; establish whether a separate authoritative disaster-reunification source is needed.',
    'shelter-ready-plan-form': 'Verify the exact current form privacy/storage/sharing language and its applicability; never infer privacy guarantees from a blocked page.',
    'shelter-ready-tech': 'Verify current agency messaging instructions and any text-command syntax against a dated primary source; do not repeat stale SMS commands.',
    'shelter-cdc-chemical-evac': 'Document the chemical-hazard scope; do not extend an evacuation warning to all family reunification situations.',
}


def need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def pinned(root: Path, path: str, sha: str) -> Path:
    file = root / path
    need(file.is_file() and not file.is_symlink(), 'missing/symlink pinned evidence: ' + path)
    need(git_blob(file.read_bytes()) == sha, 'changed Git source identity: ' + path)
    return file


def load_gate(root: Path, path: str, sha: str, name: str):
    file = pinned(root, path, sha)
    spec = importlib.util.spec_from_file_location(name, file)
    need(spec is not None and spec.loader is not None, 'unable to load pinned gate: ' + path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def reconcile(family: dict, triage: dict, observations: dict) -> dict:
    """Reconcile *validator outputs*, never substitute for validating original corpus."""
    need(type(family) is dict and family.get('status') == 'DRAFT_HARD_HOLD'
         and family.get('schema') == 'fv-preparedness-r155-family-source-observation-v1'
         and family.get('source_relationships') == 11 and family.get('citation_occurrences') == 16
         and (family.get('text_accessible_limited_claim_match'), family.get('source_scope_flags'),
              family.get('retrieval_blocked_not_link_dead')) == (3, 2, 6)
         and family.get('unreviewed_source_relationships') == 11
         and all(family.get(k) is False for k in ('qualified_source_review', 'medical_safety_approval',
             'independent_qd_pass', 'publish_allowed', 'paid_offer_verified')),
         'R155 validator output incompatible with source hard hold')
    need(type(triage) is dict and triage.get('schema') == 'fv-preparedness-r154-triage-v1'
         and triage.get('decision') == 'DRAFT_HARD_HOLD'
         and triage.get('review_tasks_total') == 75
         and (triage.get('priority_hist_food'), triage.get('priority_reunification'),
              triage.get('priority_interpretation'), triage.get('remaining_tool_source')) == (8, 11, 4, 52)
         and all(triage.get(k) is False for k in ('qualified_source_review', 'safety_approved',
             'independent_qd_pass', 'publication_authorized', 'merchant_offer_verified'))
         and type(triage.get('original_packet_fingerprint')) is str
         and SHA256.fullmatch(triage['original_packet_fingerprint']) is not None,
         'R154 triage inventory or approval state drift')
    need(type(observations) is dict and observations.get('schema') ==
         'fv-preparedness-r155-family-source-observation-v1'
         and observations.get('tool') == FAMILY and observations.get('observed_date') == '2026-11-05'
         and all(observations.get(k) is False for k in ('source_approval', 'independent_review',
               'publication_authorized', 'commercial_offer_verified')),
         'original observation state was changed')
    fs, ts, os = family.get('items'), triage.get('tasks'), observations.get('observations')
    need(type(fs) is list and len(fs) == 11 and type(ts) is list and len(ts) == 75
         and type(os) is list and len(os) == 11,
         'missing or duplicated original evidence inventory')
    by_f, by_t, by_o = {}, {}, {}
    all_task_keys = set()
    for t in ts:
        need(type(t) is dict and type(t.get('task_fingerprint')) is str
             and SHA256.fullmatch(t['task_fingerprint']) is not None
             and t['task_fingerprint'] not in all_task_keys
             and t.get('qualified_source_review') is False
             and t.get('medical_or_food_safety_approved') is False
             and t.get('publication_allowed') is False,
             'missing/duplicate task or fabricated review approval')
        all_task_keys.add(t['task_fingerprint'])
        if t.get('review_lane') != 'FAMILY_REUNIFICATION_SOURCE_AND_PRIVACY':
            continue
        key = t.get('original_identity')
        need(type(key) is str and key.startswith(FAMILY + '/') and key not in by_t
             and t.get('priority') == 1 and t.get('note_status') == 'NO_NOTE'
             and t.get('reviewer_note') is None and t.get('evidence_urls_unverified') == [],
             'family task changed or contains unreviewed intake')
        by_t[key] = t
    for f in fs:
        need(type(f) is dict and f.get('source_id') in EXPECTED
             and f['source_id'] not in by_f and type(f.get('citation_occurrences')) is int
             and f['citation_occurrences'] > 0 and f.get('independent_review') is False
             and f.get('human_link_verified') is False and f.get('publication_allowed') is False,
             'missing/duplicated citation relationship or forged source review')
        by_f[f['source_id']] = f
    for o in os:
        need(type(o) is dict and o.get('source_id') in EXPECTED
             and o['source_id'] not in by_o and o.get('review_state') == 'PENDING'
             and o.get('human_link_checked') is False and o.get('qualified_safety_review') is False
             and type(o.get('observation')) is str and o['observation'].strip(),
             'untrusted source observation or review-state change')
        by_o[o['source_id']] = o
    need(set(by_f) == set(by_o) == set(EXPECTED)
         and set(by_t) == {FAMILY + '/' + k for k in EXPECTED}
         and sum(v['citation_occurrences'] for v in by_f.values()) == 16,
         'source-to-workorder cardinality or citation conservation failed')
    result = []
    for sid in sorted(EXPECTED):
        f, o, t = by_f[sid], by_o[sid], by_t[FAMILY + '/' + sid]
        access, scope = EXPECTED[sid]
        need((o.get('access'), o.get('scope')) == (access, scope)
             and (f.get('observed_access'), f.get('observed_scope')) == (access, scope)
             and type(o.get('source_url')) is str and o['source_url'].startswith('https://')
             and f.get('url') == o['source_url'] == t.get('source_url'),
             'original source URL/observation mismatch: ' + sid)
        category, priority = (('DISPUTED_SCOPE', 0) if scope in ('SCOPE_REVIEW_REQUIRED', 'CONTEXT_REVIEW_REQUIRED')
                              else ('UNOBSERVABLE_403', 1) if access == 'RETRIEVAL_BLOCKED'
                              else ('LIMITED_TEXT_MATCH', 2))
        result.append({
            'source_id': sid, 'source_url': o['source_url'], 'citation_occurrences': f['citation_occurrences'],
            'original_task_fingerprint': t['task_fingerprint'],
            'original_observation': o['observation'], 'observed_date': observations['observed_date'],
            'automated_retrieval': access, 'source_scope': scope, 'queue_priority': priority,
            'review_lane': category,
            'reviewer_question': SPECIAL.get(sid,
                'Read original publisher text manually, check page title/date/version and exact cited claim in context; document any change proposal.'),
            'reviewer_evidence_required': 'Primary exact URL, title, date/edition, passage or timestamp, claim-to-passage analysis, contextual/household limitation, reviewer identity, date and qualified independent decision outside this draft gate.',
            'source_link_human_checked': False, 'claim_scope_approved': False,
            'safety_approved': False, 'independent_qd_pass': False, 'publish_allowed': False,
        })
    result.sort(key=lambda x: (x['queue_priority'], x['source_id']))
    need(sum(r['queue_priority'] == 0 for r in result) == 2
         and sum(r['queue_priority'] == 1 for r in result) == 6
         and sum(r['queue_priority'] == 2 for r in result) == 3,
         'workorder safety priority drift')
    return {'schema': SCHEMA, 'status': 'DRAFT_HARD_HOLD',
            'original_r154_packet_fingerprint': triage['original_packet_fingerprint'],
            'family_source_relationships': 11, 'family_citation_occurrences': 16,
            'other_review_tasks_still_pending': 64,
            'critical_source_scope': 2, 'blocked_retrieval_not_link_death': 6,
            'narrow_text_matches_not_approved': 3,
            'source_safety_qd_approved': False, 'public_release_allowed': False,
            'merchant_sku_verified': False, 'social_asset_id_verified': False,
            'paid_conversions_verified': False, 'net_revenue_per_1000_sessions': None,
            'workorders': result}


def authentic_reconcile(repo: Path) -> dict:
    repo = repo.resolve(strict=True)
    r154 = load_gate(repo, R154_GATE, R154_BLOB, 'r154_frozen_r156')
    r155 = load_gate(repo, R155_GATE, R155_BLOB, 'r155_frozen_r156')
    obs_file = pinned(repo, OBSERVATIONS, OBS_BLOB)
    obs = json.loads(obs_file.read_text(encoding='utf-8'))
    # Both pinned validators independently verify their upstream frozen sources and original bodies.
    return reconcile(r155.authentic_inspect(repo, obs_file),
                     r154.triage(r154.authentic_packet(repo)), obs)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--report', type=Path, help='New JSON file OUTSIDE checkout (no overwrites)')
    a = parser.parse_args(argv)
    try:
        root = a.repo.resolve(strict=True)
        report = authentic_reconcile(root)
        if a.report:
            dest = a.report.resolve()
            need(not dest.exists() and not dest.is_relative_to(root) and not dest.is_symlink(),
                 'must write only a new report outside checkout')
            dest.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({k: v for k, v in report.items() if k != 'workorders'}, sort_keys=True))
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({'status': 'INVALID_HARD_HOLD', 'error': str(exc),
                          'public_release_allowed': False, 'source_safety_qd_approved': False}))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
