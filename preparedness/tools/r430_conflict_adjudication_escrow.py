#!/usr/bin/env python3
"""R430: read-only source-dispute/manuscript-fork review escrow, Issue #136.

Emits evidence-preserving, deterministic human-review queues. Never chooses a
source variant, resolves a manuscript fork, authenticates external source truth,
or approves emergency advice, WordPress publication, sales or conversion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ORIGINAL_GIT_BLOB = '86d22a1d504c93db7689b914e2202a7845b648e2'
SHA40 = re.compile(r'[0-9a-f]{40}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
FORK_PATH = re.compile(r'preparedness/(?:content/articles/[a-z0-9-]+\.(?:body\.html|meta\.json)|sources/fragments/[a-z0-9-]+\.json)\Z')
EXPECTED_COUNTS = {'original_article_count': 35, 'original_source_fragments': 7,
                   'source_record_occurrences': 280, 'original_distinct_source_ids': 203,
                   'source_evidence_disputes': 5, 'unselected_original_forks': 9}
REVIEW_STEPS = ('independently_open_source_and_record_access_date',
                'read_exact_scope_not_just_hub_or_catalogue',
                'compare_source_claim_to_each_candidate_and_record_limits',
                'qualified_human_check_for_emergency_food_medical_or_child_privacy',
                'separate_draft_selection_from_release_authorization')


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def held(errors=(), *, cases=(), receipt=None, complete=False):
    """Structural completeness never grants editorial, QD or commerce approval."""
    errors = sorted(set(errors))
    return {'schema': 1, 'issue': 136, 'conversion_issue': 820,
            'release_state': 'DRAFT_HARD_HOLD', 'eligible': False,
            'publication_approved': False, 'qualified_safety_approved': False,
            'merchant_offer_verified': False, 'paid_activation_approved': False,
            'verified_paid_orders': None, 'net_revenue_per_1000_qualified_humans': None,
            'escrow_structure_ok': complete and not errors,
            'errors': errors, 'unresolved_cases': list(cases),
            'source_disputes_unresolved': sum(c.get('kind') == 'SOURCE_APPLICABILITY' for c in cases),
            'manuscript_forks_unresolved': sum(c.get('kind') == 'MANUSCRIPT_FORK' for c in cases),
            'human_review_required': True, 'review_receipt_sha256': receipt,
            'evidence_truth': 'NOT_INDEPENDENTLY_VERIFIED',
            'original_reading_depth_and_70_exports': 'NOT_TESTED_BY_R430',
            'conversion_evidence': 'NOT_AUTHENTICATED'}


def audit(docket, *, raw=None, test_only=False):
    """Read a pinned original R397 docket, preserve every source and fork candidate."""
    errors, cases = [], []
    if not isinstance(docket, dict):
        return held(['R430_DOCKET_NOT_OBJECT'])
    if not test_only and (not isinstance(raw, bytes) or git_blob(raw) != ORIGINAL_GIT_BLOB):
        errors.append('R430_ORIGINAL_GIT_BLOB_UNVERIFIED')
    if raw is not None:
        if not isinstance(raw, bytes):
            errors.append('R430_RAW_NOT_BYTES')
        else:
            try:
                on_disk = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_pairs,
                                     parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
                if on_disk != docket:
                    errors.append('R430_RAW_OBJECT_MISMATCH')
            except (ValueError, UnicodeError, TypeError):
                errors.append('R430_RAW_JSON_UNTRUSTED')
    if docket.get('schema') != 1 or docket.get('issue') != 136 or \
       docket.get('provenance') != 'ORIGINAL_UNSELECTED_GIT_SOURCE_INVENTORY' or \
       docket.get('release_state') != 'DRAFT_HARD_HOLD':
        errors.append('R430_DOCKET_PROVENANCE_OR_STATE_CHANGED')
    for name in ('publication_approved', 'qualified_safety_approved',
                 'merchant_offer_verified', 'automatic_variant_selection'):
        if docket.get(name) is not False:
            errors.append('R430_FORBIDDEN_APPROVAL_' + name)
    for group in ('expected', 'observed'):
        counts = docket.get(group)
        if not isinstance(counts, dict) or any(type(counts.get(k)) is not int or counts[k] != v for k, v in EXPECTED_COUNTS.items()):
            errors.append('R430_ORIGINAL_COUNTS_' + group.upper())
    pins = docket.get('branch_pins')
    sources = docket.get('all_original_source_id_crosswalk')
    disputes = docket.get('source_evidence_disputes')
    forks = docket.get('original_fork_disputes')
    articles = docket.get('original_articles')
    if not all(isinstance(v, list) for v in (pins, sources, disputes, forks, articles)):
        return held(errors + ['R430_MISSING_OR_INVALID_ARRAYS'])
    if (len(pins), len(sources), len(disputes), len(forks), len(articles)) != (9, 203, 5, 9, 35):
        errors.append('R430_9_203_5_9_35_COVERAGE_CHANGED')
    try:
        branch_map = {p['branch']: p['sha'] for p in pins if isinstance(p, dict)}
        slug_set = {a['slug'] for a in articles if isinstance(a, dict)}
        source_map = {s['source_id']: s['variants'] for s in sources if isinstance(s, dict)}
    except (TypeError, KeyError):
        return held(errors + ['R430_INVALID_IDENTITY_ROWS'])
    if len(branch_map) != len(pins) or len(branch_map) != 9 or not all(
        isinstance(k, str) and k.startswith('claude/prep-') and isinstance(v, str) and SHA40.fullmatch(v)
        for k, v in branch_map.items()
    ):
        errors.append('R430_BRANCH_PIN_MISMATCH')
    if len(slug_set) != 35 or not all(isinstance(x, str) and SLUG.fullmatch(x) for x in slug_set):
        errors.append('R430_ARTICLE_IDENTITY_CHANGED')
    if len(source_map) != 203 or not all(isinstance(x, str) and SLUG.fullmatch(x) for x in source_map):
        errors.append('R430_SOURCE_IDENTITY_CHANGED')
    seen_sources, seen_paths = set(), set()
    for row in disputes:
        if not isinstance(row, dict):
            errors.append('R430_SOURCE_DISPUTE_NOT_OBJECT'); continue
        sid, variants = row.get('source_id'), row.get('variants')
        if not isinstance(sid, str) or not SLUG.fullmatch(sid) or sid in seen_sources:
            errors.append('R430_SOURCE_DISPUTE_ID_COLLISION'); continue
        seen_sources.add(sid)
        if row.get('decision') != 'HUMAN_REVIEW_REQUIRED' or row.get('selected_record') is not None:
            errors.append('R430_SOURCE_DECISION_PREMATURE_' + sid)
        if not isinstance(variants, list) or len(variants) < 2:
            errors.append('R430_SOURCE_VARIANTS_MISSING_' + sid); continue
        src_variants = source_map.get(sid)
        if not isinstance(src_variants, list) or len(src_variants) != len(variants):
            errors.append('R430_SOURCE_CROSSWALK_MISMATCH_' + sid)
        contenders, keys = [], set()
        for v in variants:
            if not isinstance(v, dict):
                errors.append('R430_SOURCE_VARIANT_NOT_OBJECT_' + sid); continue
            branch, blob, url = v.get('branch'), v.get('source_blob'), v.get('url')
            if not isinstance(branch, str) or branch not in branch_map or not isinstance(blob, str) or not SHA40.fullmatch(blob):
                errors.append('R430_SOURCE_BRANCH_OR_BLOB_INVALID_' + sid); continue
            if not isinstance(url, str) or not url.startswith('https://') or len(url) > 2048 or any(ord(c) < 33 for c in url):
                errors.append('R430_SOURCE_URL_INVALID_' + sid); continue
            signature = (branch, blob, url)
            if signature in keys:
                errors.append('R430_DUPLICATED_SOURCE_VARIANT_' + sid)
            keys.add(signature)
            if not isinstance(src_variants, list) or signature not in {
                (s.get('branch'), s.get('source_blob'), s.get('url'))
                for s in src_variants if isinstance(s, dict)
            }:
                errors.append('R430_SOURCE_NOT_IN_ORIGINAL_CROSSWALK_' + sid)
            if v.get('human_link_check') is not False:
                errors.append('R430_UNVERIFIED_LINK_CLAIM_' + sid)
            if not all(isinstance(v.get(k), str) and v.get(k).strip() for k in
                       ('publisher', 'supports_exact', 'reading_scope_notes_exact', 'fragment', 'verified_on')):
                errors.append('R430_SOURCE_SCOPE_METADATA_MISSING_' + sid)
            contenders.append({'branch': branch, 'source_blob': blob, 'url': url,
                               'publisher_as_drafted': v.get('publisher'),
                               'claimed_support_as_drafted': v.get('supports_exact'),
                               'reading_scope_as_drafted': v.get('reading_scope_notes_exact'),
                               'verified_on_as_drafted': v.get('verified_on'),
                               'human_link_check': False,
                               'evidence_status': 'CLAIM_ONLY_REQUIRES_INDEPENDENT_REVIEW'})
        cases.append({'kind': 'SOURCE_APPLICABILITY', 'id': sid, 'selected': None,
                      'state': 'HUMAN_REVIEW_REQUIRED', 'contenders': contenders,
                      'review_steps': list(REVIEW_STEPS)})
    for row in forks:
        if not isinstance(row, dict):
            errors.append('R430_MANUSCRIPT_FORK_NOT_OBJECT'); continue
        path, variants = row.get('path'), row.get('variants')
        if not isinstance(path, str) or not FORK_PATH.fullmatch(path) or path in seen_paths:
            errors.append('R430_FORK_PATH_COLLISION_OR_UNSAFE'); continue
        seen_paths.add(path)
        if path.startswith('preparedness/content/articles/'):
            slug = path.rsplit('/', 1)[-1].split('.')[0]
            if slug not in slug_set:
                errors.append('R430_FORK_FOREIGN_ARTICLE_' + path)
        if row.get('decision') != 'HUMAN_REVIEW_REQUIRED' or row.get('selected_sha') is not None or \
           row.get('requires_reading_depth_review') is not True or row.get('requires_source_citation_review') is not True:
            errors.append('R430_FORK_PREMATURE_SELECTION_OR_REVIEW_BYPASS_' + path)
        if not isinstance(variants, list) or len(variants) < 2:
            errors.append('R430_FORK_VARIANTS_MISSING_' + path); continue
        contenders, by_sha, branches = [], {}, set()
        for v in variants:
            if not isinstance(v, dict):
                errors.append('R430_FORK_VARIANT_NOT_OBJECT_' + path); continue
            branch, blob, length = v.get('branch'), v.get('git_blob_sha'), v.get('byte_length')
            if not isinstance(branch, str) or branch not in branch_map or branch in branches or \
               not isinstance(blob, str) or not SHA40.fullmatch(blob) or type(length) is not int or not 0 < length <= 2_000_000:
                errors.append('R430_FORK_VARIANT_IDENTITY_INVALID_' + path); continue
            branches.add(branch)
            if blob in by_sha and by_sha[blob] != length:
                errors.append('R430_IDENTICAL_BLOB_DIFFERENT_LENGTH_' + path)
            by_sha[blob] = length
            contenders.append({'branch': branch, 'branch_head_pin': branch_map[branch],
                               'git_blob_sha': blob, 'byte_length': length,
                               'evidence_status': 'ORIGINAL_CANDIDATE_UNSELECTED'})
        cases.append({'kind': 'MANUSCRIPT_FORK', 'id': path, 'selected': None,
                      'state': 'HUMAN_REVIEW_REQUIRED', 'contenders': contenders,
                      'unique_git_blob_count': len(by_sha),
                      'same_blob_does_not_imply_qualified_approval': True,
                      'review_steps': list(REVIEW_STEPS)})
    # Order-independent review layout; the digest binds ALL candidate records.
    cases.sort(key=lambda c: (c['kind'], c['id']))
    if len(cases) != 14 or len(seen_sources) != 5 or len(seen_paths) != 9:
        errors.append('R430_UNRESOLVED_14_CASE_COVERAGE_CHANGED')
    receipt = None
    if not errors:
        payload = {'original_git_blob': ORIGINAL_GIT_BLOB if not test_only else 'TEST_ONLY_UNPINNED',
                   'cases': cases, 'branches': sorted(branch_map.items())}
        receipt = hashlib.sha256(b'FV-R430-UNRESOLVED-REVIEW-ESCROW\0' +
                                 json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()
    return held(errors, cases=cases, receipt=receipt, complete=not errors)


def unique_pairs(pairs):
    out = {}
    for k, value in pairs:
        if k in out:
            raise ValueError('duplicate JSON key')
        out[k] = value
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description='R430 exact original conflict review queue; ALWAYS HARD HOLD')
    parser.add_argument('original_docket', type=Path)
    args = parser.parse_args(argv)
    try:
        path = args.original_docket
        if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1 or not 0 < path.stat().st_size <= 2000000:
            raise ValueError('unsafe original evidence file')
        raw = path.read_bytes()
        d = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_pairs,
                       parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
        result = audit(d, raw=raw)
    except (OSError, TypeError, ValueError, UnicodeError) as exc:
        result = held(['R430_UNAVAILABLE_OR_INVALID_ORIGINAL_' + type(exc).__name__])
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2


if __name__ == '__main__':
    sys.exit(main())
