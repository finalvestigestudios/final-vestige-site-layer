#!/usr/bin/env python3
"""R346: immutable citation-ticket bindings for human source-conflict proposals.

READ ONLY. Candidate reviewer proposals are unauthenticated inputs, not source
support, human link verification, QD clearance, product approval or release.
Every execution keeps HARD HOLD. No data is written or sent anywhere.
"""
from __future__ import annotations
from hashlib import sha1, sha256
from pathlib import Path
import json
import re

SCHEMA = 'fv-preparedness-r346-citation-review-binding-v1'
EXPECTED_VARIANT_FILES = {
    'fsis-power-failure': ('fragments/food.json', 'fragments/shelter.json'),
    'loc-pioneer-diaries': ('fragments/hist-field.json', 'fragments/hist-food.json'),
    'loc-prairie-traveler': ('fragments/hist-field.json', 'fragments/hist-food.json'),
    'nchfp-home': ('fragments/food.json', 'fragments/hist-home.json'),
}
EXPECTED_IDS = tuple(sorted(EXPECTED_VARIANT_FILES))
SHA = re.compile(r'[a-f0-9]{64}\Z')
TICKET = re.compile(r'[a-f0-9]{24}\Z')
DOC = re.compile(r'(?:articles|tools)/[a-z0-9]+(?:-[a-z0-9]+)*\Z')
PROPOSAL_KEYS = frozenset(('source_id', 'packet_sha256', 'proposed_variant_sha256',
                           'ticket_bindings', 'proposal_note', 'disposition'))
DISPOSITION = 'PROPOSED_FOR_INDEPENDENT_REVIEW_ONLY'
HOLD = {'may_publish': False, 'may_merge': False, 'qualified_qd_pass': False,
        'human_source_link_review_pass': False, 'claim_source_support_verified': False,
        'emergency_or_medical_advice_approved': False,
        'paid_preparedness_sku_verified': False, 'confirmed_paid_orders_verified': False,
        'realized_net_revenue_verified': False, 'native_100_export_build_verified': False}


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(obj):
    return sha256(canonical(obj)).hexdigest()


def git_blob(data):
    return sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def source_packet_binding(packet):
    """Bind exact redacted variants, claim fingerprints and affected documents."""
    if not isinstance(packet, dict):
        raise ValueError('INVALID_REVIEW_PACKET')
    sid = packet.get('source_id')
    if sid not in EXPECTED_IDS:
        raise ValueError('UNKNOWN_REVIEW_SOURCE')
    variants = packet.get('verified_variants')
    claims = packet.get('citations')
    if not isinstance(variants, list) or len(variants) != 2:
        raise ValueError('EXACTLY_TWO_SOURCE_VARIANTS_REQUIRED')
    if not isinstance(claims, list) or not claims:
        raise ValueError('UNREVIEWED_CLAIMS_REQUIRED')
    if packet.get('candidate_selected') is not None or packet.get('human_claim_source_adjudication') != 'UNREVIEWED_REQUIRED' or packet.get('review_disposition') != 'QUARANTINED_SOURCE_ID':
        raise ValueError('FORGED_PACKET_APPROVAL')
    variant_keys = []
    paths = set()
    for v in variants:
        if not isinstance(v, dict) or not isinstance(v.get('source_file'), str):
            raise ValueError('INVALID_VARIANT')
        key = v.get('source_record_sha256')
        if not isinstance(key, str) or not SHA.fullmatch(key):
            raise ValueError('INVALID_VARIANT_DIGEST')
        if v.get('human_link_check_established') is not False:
            raise ValueError('FORGED_LINK_REVIEW')
        if v['source_file'] in paths:
            raise ValueError('DUPLICATE_VARIANT_PATH')
        paths.add(v['source_file'])
        variant_keys.append((v['source_file'], key))
    if len(set(variant_keys)) != 2 or len(set(k for _, k in variant_keys)) != 2:
        raise ValueError('DUPLICATE_VARIANTS')
    if tuple(sorted(paths)) != tuple(sorted(EXPECTED_VARIANT_FILES[sid])):
        raise ValueError('SOURCE_VARIANT_FILE_PROVENANCE_DRIFT')
    rows = []
    tickets = set()
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError('INVALID_CLAIM')
        tid, doc, claim_hash = claim.get('ticket_id'), claim.get('document'), claim.get('claim_text_sha256')
        if not isinstance(tid, str) or not TICKET.fullmatch(tid) or tid in tickets:
            raise ValueError('INVALID_OR_DUPLICATE_TICKET')
        if not isinstance(doc, str) or not DOC.fullmatch(doc):
            raise ValueError('INVALID_DOCUMENT_ID')
        if not isinstance(claim_hash, str) or not SHA.fullmatch(claim_hash):
            raise ValueError('INVALID_CLAIM_FINGERPRINT')
        if claim.get('unreviewed_only') is not True:
            raise ValueError('FORGED_CLAIM_CLEARANCE')
        tickets.add(tid)
        rows.append({'ticket_id': tid, 'document': doc, 'claim_text_sha256': claim_hash})
    if sorted({r['document'] for r in rows}) != sorted(packet.get('impacted_document_ids', [])) or len(rows) != packet.get('claim_tickets_impacted'):
        raise ValueError('IMPACT_COUNT_OR_DOCUMENT_DRIFT')
    if len(set(variant_keys)) != 2:
        raise ValueError('DUPLICATE_VARIANT_ID')
    binding = {'source_id': sid,
               'variants': [{'path': path, 'record_sha256': key} for path, key in sorted(variant_keys)],
               'claims': sorted(rows, key=lambda x: x['ticket_id'])}
    return {'source_id': sid, 'packet_sha256': digest(binding),
            'variant_sha256s': sorted(k for _, k in variant_keys),
            'ticket_bindings': {r['ticket_id']: r['claim_text_sha256'] for r in rows},
            'impacted_documents': sorted({r['document'] for r in rows}),
            'claim_count': len(rows)}


def review_preflight(packets, proposals=None):
    """Produce deterministic review checks; NEVER output a release PASS."""
    errors, bindings = [], {}
    if not isinstance(packets, list):
        packets = []
        errors.append('PACKETS_LIST_REQUIRED')
    claimed_ticket_ids = set()
    for packet in packets:
        try:
            row = source_packet_binding(packet)
            if row['source_id'] in bindings:
                errors.append('DUPLICATE_SOURCE_PACKET:' + row['source_id'])
            overlapping = claimed_ticket_ids.intersection(row['ticket_bindings'])
            if overlapping:
                errors.append('CROSS_SOURCE_DUPLICATE_CITATION_TICKET')
            claimed_ticket_ids.update(row['ticket_bindings'])
            bindings[row['source_id']] = row
        except (ValueError, TypeError, OverflowError) as exc:
            errors.append(str(exc))
    if set(bindings) != set(EXPECTED_IDS):
        errors.append('EXACT_FOUR_QUARANTINED_SOURCES_REQUIRED')
    if proposals is None:
        proposals = []
    if not isinstance(proposals, list):
        errors.append('PROPOSALS_LIST_REQUIRED')
        proposals = []
    processed = set()
    for prop in proposals:
        if not isinstance(prop, dict):
            errors.append('INVALID_PROPOSAL')
            continue
        sid = prop.get('source_id')
        if not isinstance(sid, str) or sid not in bindings:
            errors.append('UNKNOWN_PROPOSAL_SOURCE')
            continue
        if sid in processed:
            errors.append('DUPLICATE_PROPOSAL:' + sid)
        processed.add(sid)
        if set(prop) != PROPOSAL_KEYS:
            errors.append('UNAUTHORIZED_OR_MISSING_PROPOSAL_FIELDS:' + sid)
        row = bindings[sid]
        if prop.get('disposition') != DISPOSITION:
            errors.append('FORGED_APPROVAL_DISPOSITION:' + sid)
        if prop.get('packet_sha256') != row['packet_sha256']:
            errors.append('STALE_OR_FORGED_PACKET_BINDING:' + sid)
        if prop.get('proposed_variant_sha256') not in row['variant_sha256s']:
            errors.append('UNKNOWN_VARIANT_SELECTION:' + sid)
        if prop.get('ticket_bindings') != row['ticket_bindings']:
            errors.append('MISSING_OR_STALE_CLAIM_BINDINGS:' + sid)
        note = prop.get('proposal_note')
        if not isinstance(note, str) or not (40 <= len(note.strip()) <= 800) or any(ord(c) < 32 and c not in '\n\t' for c in note):
            errors.append('MISSING_OR_UNSAFE_REVIEW_RATIONALE:' + sid)
    # Source candidate selection is never authorization: evidence is independent.
    state = ('INVALID_HARD_HOLD' if errors else
             'PROPOSALS_STILL_UNREVIEWED_HARD_HOLD' if len(processed) == len(EXPECTED_IDS) else
             'PENDING_PROPOSALS_HARD_HOLD')
    return {'schema': SCHEMA, 'state': state, 'errors': sorted(set(errors)),
            'docket': [bindings[k] for k in sorted(bindings)],
            'proposals_received': len(processed), 'proposals_missing': sorted(set(EXPECTED_IDS)-processed),
            'reviewer_identity_authenticated': False, 'human_decisions_authenticated': False,
            'source_support_proved': False,
            'outstanding_editorial_conflicts': 15, 'outstanding_article15_tool104_reviews': 17,
            'unresolved_competing_source_ids': 4, **HOLD}


def native_audit(root: Path):
    """Read R345's pinned-source docket from an authentic checkout; fail closed."""
    errors = []
    prep = root / 'preparedness' if (root / 'preparedness').is_dir() else root
    try:
        from preparedness.tools import r345_conflicted_source_claim_quarantine as prior
        filename = prep / 'tools' / 'r345_conflicted_source_claim_quarantine.py'
        if filename.is_symlink() or not filename.is_file() or git_blob(filename.read_bytes()) != '9712a220212508f832fb05083c7a3a03e84412e4':
            errors.append('R345_PREDECESSOR_GIT_BLOB_UNVERIFIED')
        previous = prior.native_audit(root)
        if previous.get('state') != 'KNOWN_CONFLICT_HARD_HOLD' or previous.get('known_verified_fragment_conflicts_unresolved') != 4:
            errors.append('R345_NATIVE_CUSTODY_NOT_ESTABLISHED')
        report = review_preflight(previous.get('packets', []))
        errors += report['errors']
    except (ImportError, OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        errors.append('NATIVE_R345_SOURCE_REQUIRED:' + type(exc).__name__)
        report = review_preflight([])
    report['errors'] = sorted(set(errors + report['errors']))
    if report['errors']:
        report['state'] = 'INVALID_HARD_HOLD'
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description='R346 read-only proposed source-review binding / HARD HOLD')
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(native_audit(args.repo_root), sort_keys=True, ensure_ascii=False, indent=2))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
