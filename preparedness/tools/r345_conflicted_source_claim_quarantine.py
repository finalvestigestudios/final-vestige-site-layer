#!/usr/bin/env python3
"""R345: fail-closed human-review packets for competing Preparedness source IDs.

Read-only. Expected *known* conflicts are never approvals. No source URL or
claim is selected, and no private document or tool is made public.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha1, sha256
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r345-source-claim-conflict-quarantine-v1'
CONFLICT_FILES = {
    'fsis-power-failure': ('fragments/food.json', 'fragments/shelter.json'),
    'nchfp-home': ('fragments/food.json', 'fragments/hist-home.json'),
    'loc-prairie-traveler': ('fragments/hist-field.json', 'fragments/hist-food.json'),
    'loc-pioneer-diaries': ('fragments/hist-field.json', 'fragments/hist-food.json'),
}
ID_RE = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
TICKET_RE = re.compile(r'[0-9a-f]{24}\Z')
FIELDS = ('title', 'publisher', 'kind', 'url', 'supports', 'verified_on')
HOLD = {
    'may_publish': False, 'may_merge': False,
    'qualified_qd_pass': False, 'human_source_link_review_pass': False,
    'claim_source_support_verified': False,
    'emergency_or_medical_advice_approved': False,
    'paid_preparedness_sku_verified': False, 'confirmed_paid_orders_verified': False,
    'realized_net_revenue_verified': False,
    'native_100_export_build_verified': False,
}


def canonical_json(obj: object) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':')).encode('utf-8')


def git_blob(data: bytes) -> str:
    return sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def _key(record: dict) -> str:
    return sha256(canonical_json({k: record.get(k) for k in FIELDS})).hexdigest()


def make_packets(records: dict, tickets: list[dict]) -> dict:
    """Pure quarantine analysis; synthetic rows never authorize any changes."""
    errors: list[str] = []
    groups = defaultdict(list)
    if not isinstance(records, dict):
        return {'errors': ['SOURCE_RECORD_MAP_REQUIRED'], 'packets': [], 'impacted_tickets': 0}
    for filename, rows in sorted(records.items()):
        if not isinstance(filename, str) or not filename or not isinstance(rows, list):
            errors.append('INVALID_SOURCE_FILE_ROWS')
            continue
        within = set()
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not ID_RE.fullmatch(row['id']):
                errors.append('INVALID_SOURCE_ROW:' + filename)
                continue
            if row['id'] in within:
                errors.append('DUPLICATED_SOURCE_WITHIN_ONE_FILE:' + filename + ':' + row['id'])
            within.add(row['id'])
            groups[row['id']].append((filename, row))
    actual_multi = {
        sid for sid, group in groups.items()
        if sum(row.get('verified_on') is not None for _, row in group) > 1
    }
    if actual_multi != set(CONFLICT_FILES):
        errors.append('VERIFIED_CONFLICT_ID_SET_DRIFT')
    packets = []
    for sid, expected in sorted(CONFLICT_FILES.items()):
        group = groups.get(sid, [])
        verified = [(file, row) for file, row in group if row.get('verified_on') is not None]
        if tuple(sorted(file for file, _ in verified)) != tuple(sorted(expected)):
            errors.append('VERIFIED_CONFLICT_PROVENANCE_DRIFT:' + sid)
        urls = {row.get('url') for _, row in verified if isinstance(row.get('url'), str)}
        if len(urls) != 1 or len(verified) != 2:
            errors.append('CONFLICT_URL_OR_VARIANT_DRIFT:' + sid)
        changed = [k for k in FIELDS if len({canonical_json(row.get(k)) for _, row in verified}) > 1]
        if not changed:
            errors.append('REVIEW_CONFLICT_VARIANTS_IDENTICAL:' + sid)
        variants = []
        for filename, row in sorted(verified, key=lambda x: x[0]):
            variants.append({
                'source_file': filename,
                'source_record_sha256': _key(row),
                'research_verified_on': row.get('verified_on'),
                'human_link_check_established': False,
            })
        packets.append({
            'source_id': sid,
            'verified_variants': variants,
            'divergent_fields': changed,
            'candidate_selected': None,
            'human_claim_source_adjudication': 'UNREVIEWED_REQUIRED',
            'review_disposition': 'QUARANTINED_SOURCE_ID',
            'citations': [],
        })
    if not isinstance(tickets, list):
        errors.append('CITATION_TICKETS_REQUIRED')
        tickets = []
    packet_by_id = {p['source_id']: p for p in packets}
    seen = set()
    for t in tickets:
        if not isinstance(t, dict):
            errors.append('INVALID_CITATION_TICKET')
            continue
        tid, sid = t.get('ticket_id'), t.get('source_id')
        if not isinstance(tid, str) or not TICKET_RE.fullmatch(tid) or tid in seen:
            errors.append('INVALID_OR_DUPLICATE_CITATION_TICKET_ID')
            continue
        seen.add(tid)
        if t.get('human_claim_source_adjudication') != 'UNREVIEWED_REQUIRED':
            errors.append('FORGED_CLAIM_REVIEW_STATE:' + tid)
        if not isinstance(sid, str) or sid not in groups:
            errors.append('UNKNOWN_CITED_SOURCE:' + str(sid))
        if sid not in packet_by_id:
            continue
        if t.get('kind') not in ('articles', 'tools') or not isinstance(t.get('slug'), str) or not ID_RE.fullmatch(t['slug']):
            errors.append('INVALID_IMPACT_DOCUMENT_ID:' + tid)
            continue
        if not isinstance(t.get('claim_text_sha256'), str) or not re.fullmatch(r'[a-f0-9]{64}', t['claim_text_sha256']):
            errors.append('INVALID_IMPACT_CLAIM_DIGEST:' + tid)
            continue
        packet_by_id[sid]['citations'].append({
            'ticket_id': tid,
            'document': t['kind'] + '/' + t['slug'],
            'heading': str(t.get('heading', ''))[:120],
            'claim_text_sha256': t['claim_text_sha256'],
            'unreviewed_only': True,
        })
    for p in packets:
        p['citations'].sort(key=lambda x: (x['document'], x['ticket_id']))
        p['impacted_document_ids'] = sorted({x['document'] for x in p['citations']})
        p['claim_tickets_impacted'] = len(p['citations'])
    impacted = sum(p['claim_tickets_impacted'] for p in packets)
    return {'errors': sorted(set(errors)), 'packets': packets,
            'impacted_tickets': impacted,
            'impacted_distinct_documents': len({d for p in packets for d in p['impacted_document_ids']})}


def _native_source_records(prep: Path, pins: dict) -> tuple[dict, list[str]]:
    records, errors = {}, []
    base = prep / 'sources'
    actual = {p.relative_to(base).as_posix() for p in base.glob('*.json')}
    actual |= {p.relative_to(base).as_posix() for p in (base / 'fragments').glob('*.json')}
    if actual != set(pins):
        errors.append('SOURCE_FILE_SET_DRIFT')
    for rel, digest in sorted(pins.items()):
        p = base / rel
        if p.is_symlink() or not p.is_file():
            errors.append('MISSING_OR_SYMLINK_SOURCE:' + rel)
            continue
        try:
            b = p.read_bytes()
            if git_blob(b) != digest:
                errors.append('SOURCE_BLOB_DRIFT:' + rel)
                continue
            data = json.loads(b.decode('utf-8'))
            if not isinstance(data, dict) or not isinstance(data.get('sources'), list):
                raise ValueError('not a sources list')
            records[rel] = data['sources']
        except (OSError, ValueError, TypeError, UnicodeError):
            errors.append('UNREADABLE_SOURCE:' + rel)
    return records, errors


def native_audit(root: Path) -> dict:
    """Requires full original R337 witness; known source conflicts stay HARD HOLD."""
    prep = root / 'preparedness' if (root / 'preparedness').is_dir() else root
    errors = []
    try:
        from preparedness.tools import r343_claim_citation_review_crosswalk_hold as claims
        from preparedness.tools import r344_source_url_identity_citation_hold as sources
        records, source_errors = _native_source_records(prep, sources.SOURCE_PINS)
        errors.extend(source_errors)
        prior = claims.audit_native(root)
        known_claim_errors = {'UNSAFE_DUPLICATE_OR_DOWNGRADE_SOURCE:' + sid for sid in CONFLICT_FILES}
        unexpected_claim_errors = set(prior.get('errors', [])) - known_claim_errors
        if prior.get('entries_inspected') != 41 or unexpected_claim_errors:
            errors.append('R343_NATIVE_41_ENTRY_SOURCE_AND_CLAIM_GUARD_FAILED')
            errors.extend(sorted(unexpected_claim_errors))
        # Source bytes are pinned above. The R344 global catalog intentionally
        # rejects unverified placeholder supports and the four conflicts.
        # This quarantine never approves either category.
        review = make_packets(records, prior.get('review_tickets', []))
        errors.extend(review['errors'])
        if review['impacted_tickets'] == 0:
            errors.append('NO_CITATION_IMPACT_WITNESS')
        if len({(t.get('kind'), t.get('slug')) for t in prior.get('review_tickets', [])}) != 41:
            errors.append('ALL_41_CITATION_ENTRY_WITNESSES_REQUIRED')
        if len(prior.get('review_tickets', [])) != prior.get('citation_claim_review_tickets'):
            errors.append('CITATION_TICKET_TOTAL_MISMATCH')
    except (ImportError, OSError, ValueError, UnicodeError, TypeError, KeyError) as exc:
        errors.append('NATIVE_FROZEN_PREDECESSOR_REQUIRED:' + type(exc).__name__)
        review = {'packets': [], 'impacted_tickets': 0, 'impacted_distinct_documents': 0}
    return {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD' if errors else 'KNOWN_CONFLICT_HARD_HOLD',
            'errors': sorted(set(errors)), 'known_verified_fragment_conflicts_unresolved': len(CONFLICT_FILES),
            'packets': review['packets'],
            'citation_tickets_affected': review['impacted_tickets'],
            'documents_affected': review['impacted_distinct_documents'],
            'original_editorial_conflicts_unresolved': 15,
            'original_article15_tool104_claim_reviews_unresolved': 17,
            'limitations': ['Metadata citations and research fetches do not prove claim support',
                            'Competing source fragments are quarantined; no winner selected',
                            'Qualified human review, full native 100 exports and commerce remain separate'],
            **HOLD}


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description='R345 read-only source conflict impact HARD HOLD')
    p.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    args = p.parse_args()
    output = native_audit(args.repo_root)
    print(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True))
    return 2 if output['state'] == 'KNOWN_CONFLICT_HARD_HOLD' else 1


if __name__ == '__main__':
    raise SystemExit(main())
