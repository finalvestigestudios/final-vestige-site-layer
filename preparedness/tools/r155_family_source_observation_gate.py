#!/usr/bin/env python3
"""R155: reconcile read-only browser observations with authentic Family Reunification source custody.

Never confuses retrieved page text, blocked crawler access, a citation and qualified review.
Successful reconciliation is HARD HOLD (exit 2), not permission to release or sell.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

SCHEMA = 'fv-preparedness-r155-family-source-observation-v1'
R149_DOCKET_PATH = 'preparedness/docs/r149/tool-source-use-review-docket.json'
R149_DOCKET_BLOB = 'e63aaaa35bcb5c4378f05ae45a07cc8cfc5c070c'
R149_GATE_PATH = 'preparedness/tools/r149_tool_claim_custody.py'
R149_GATE_BLOB = 'a2b896e579e66399d6c4253242d577ee9083bda7'
OBSERVATIONS = 'preparedness/docs/r155/family-source-observations.json'
FAMILY = 'family-reunification-card'
# Observations are independent, dated *retrieval* results, never safety approvals.
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

def need(ok: bool, message: str):
    if not ok:
        raise ValueError(message)

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()

def frozen_bytes(root: Path, rel: str, expected: str) -> bytes:
    file = root / rel
    need(file.is_file() and not file.is_symlink(), 'missing/linked custody: ' + rel)
    raw = file.read_bytes()
    need(git_blob(raw) == expected, 'Git blob mismatch: ' + rel)
    return raw

def original_family_rows(docket: dict) -> dict:
    need(type(docket) is dict and docket.get('schema') == 'FV-PREP-R149-TOOL-CLAIM-CUSTODY-1',
         'unexpected R149 schema')
    need(docket.get('publication_allowed') is False and docket.get('independent_qd') == 'NOT_APPROVED'
         and docket.get('source_scope_human_review') == 'PENDING'
         and docket.get('human_link_checked_rows') == 0 and docket.get('payment_offer_verified') is False,
         'historical release gate has changed')
    need(docket.get('source_use_row_count') == 67 and
         docket.get('currently_unresolved_source_ids') == 58,
         'historical source inventory drift')
    rows = docket.get('source_use_rows')
    need(type(rows) is list and len(rows) == 67, 'missing R149 relationships')
    need(sum(r.get('citation_occurrences', 0) for r in rows) == 173,
         'original citation occurrences changed')
    family = {}
    for row in rows:
        if row.get('tool') != FAMILY:
            continue
        sid = row.get('source_id')
        need(sid in EXPECTED and sid not in family and row.get('review_decision') == 'PENDING'
             and row.get('reviewer') is None and row.get('human_link_check_recorded') is False
             and row.get('human_source_scope_adjudicated') is False
             and row.get('medical_safety_approved') is False,
             'family source identity or review state altered')
        need(type(row.get('citation_occurrences')) is int and row['citation_occurrences'] > 0,
             'missing family citation occurrences')
        need(type(row.get('author_specific_use')) is str and row['author_specific_use'].strip()
             and type(row.get('source_supports')) is str and row['source_supports'].strip(),
             'source description or author-specific use lost')
        family[sid] = row
    need(set(family) == set(EXPECTED) and sum(x['citation_occurrences'] for x in family.values()) == 16,
         'family 11-source / 16-citation baseline changed')
    return family

def inspect(docket: dict, observations: dict) -> dict:
    family = original_family_rows(docket)
    need(type(observations) is dict and set(observations) ==
         {'schema', 'observed_date', 'tool', 'observations', 'independent_review',
          'source_approval', 'publication_authorized', 'commercial_offer_verified'},
         'unknown fields or incomplete observation manifest')
    need(observations['schema'] == SCHEMA and observations['observed_date'] == '2026-11-05'
         and observations['tool'] == FAMILY and observations['independent_review'] is False
         and observations['source_approval'] is False
         and observations['publication_authorized'] is False
         and observations['commercial_offer_verified'] is False,
         'browser evidence falsely asserts review, publication or paid offer')
    rows = observations['observations']
    need(type(rows) is list and len(rows) == 11, 'expected exactly 11 source observations')
    seen, flagged, blocked, supported, items = set(), 0, 0, 0, []
    for o in rows:
        need(type(o) is dict and set(o) == {'source_id','source_url', 'access', 'scope',
                 'observation', 'review_state', 'human_link_checked', 'qualified_safety_review'},
             'unknown observation fields or reviewer approval injection')
        sid = o.get('source_id')
        need(sid in family and sid not in seen, 'unknown or duplicated family source')
        seen.add(sid)
        need(o['source_url'] == family[sid]['literal_url'], 'source URL substitution: ' + sid)
        need((o['access'], o['scope']) == EXPECTED[sid], 'observation state drift: ' + sid)
        need(o['review_state'] == 'PENDING' and o['human_link_checked'] is False
             and o['qualified_safety_review'] is False,
             'browser observation must not imply human source/safety approval')
        note = o.get('observation')
        need(type(note) is str and 24 <= len(note) <= 650 and
             not any(c in note for c in '<>\x00\r'), 'missing, unsafe or implausible observation')
        if o['access'] == 'RETRIEVAL_BLOCKED':
            blocked += 1
            need(o['scope'] == 'NOT_OBSERVABLE', '403/retrieval failure is not link death')
        elif o['scope'] == 'CLAIM_MATCH_OBSERVED':
            supported += 1
        else:
            flagged += 1
        items.append({'source_id': sid, 'citation_occurrences': family[sid]['citation_occurrences'],
                      'url': o['source_url'], 'observed_access': o['access'],
                      'observed_scope': o['scope'], 'independent_review': False,
                      'human_link_verified': False, 'publication_allowed': False})
    need(seen == set(EXPECTED) and (supported, flagged, blocked) == (3, 2, 6),
         '11-source observation count drift')
    return {'schema': SCHEMA, 'status': 'DRAFT_HARD_HOLD',
            'observation_date': observations['observed_date'],
            'source_relationships': len(items), 'citation_occurrences': 16,
            'text_accessible_limited_claim_match': supported, 'source_scope_flags': flagged,
            'retrieval_blocked_not_link_dead': blocked, 'unreviewed_source_relationships': 11,
            'qualified_source_review': False, 'medical_safety_approval': False,
            'independent_qd_pass': False, 'publish_allowed': False,
            'paid_offer_verified': False, 'items': sorted(items, key=lambda x:x['source_id'])}

def authentic_inspect(root: Path, observation_path: Path) -> dict:
    root = root.resolve(strict=True)
    r149_bytes = frozen_bytes(root, R149_DOCKET_PATH, R149_DOCKET_BLOB)
    gate_path = root / R149_GATE_PATH
    frozen_bytes(root, R149_GATE_PATH, R149_GATE_BLOB)
    spec = importlib.util.spec_from_file_location('r149_frozen', gate_path)
    need(spec is not None and spec.loader is not None, 'R149 source validator unavailable')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    docket = json.loads(r149_bytes.decode('utf-8'))
    # Active sources and original tool bodies must still match frozen R149 dossier.
    mod.verify(root / 'preparedness', docket)
    need(observation_path.is_file() and not observation_path.is_symlink(),
         'missing or linked observation docket')
    return inspect(docket, json.loads(observation_path.read_text('utf-8')))

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=Path('.'))
    ap.add_argument('--observations', type=Path, default=Path(OBSERVATIONS))
    ap.add_argument('--report', type=Path)
    args = ap.parse_args(argv)
    try:
        out = authentic_inspect(args.repo, args.observations)
        if args.report:
            path = args.report.resolve()
            root = args.repo.resolve()
            need(not path.exists() and not path.is_relative_to(root),
                 'report may only be created outside repository')
            path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print(json.dumps({k: v for k, v in out.items() if k != 'items'}, sort_keys=True))
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({'status':'INVALID_HARD_HOLD', 'error':str(exc),
                          'publish_allowed':False, 'independent_qd_pass':False}))
    return 2

if __name__ == '__main__':
    raise SystemExit(main())
