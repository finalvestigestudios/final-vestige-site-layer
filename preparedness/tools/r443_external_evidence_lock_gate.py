#!/usr/bin/env python3
"""R443: externally pinned original-source and article evidence custody (READ ONLY).

This lock protects byte identity, NOT reviewer identity, factual quality, qualified QD,
checkout status, safety, source accuracy, or permission to publish. An unreviewed
lock produced by the same integration code is not an independent trust anchor.
Always returns DRAFT_HARD_HOLD/exit 2; there is deliberately no release PASS.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

DRAFT = 'DRAFT_HARD_HOLD'
HEX40 = re.compile(r'[a-f0-9]{40}\Z')
HEX64 = re.compile(r'[a-f0-9]{64}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
REPO = 'finalvestigestudios/final-vestige-site-layer'
MAX_JSON = 8_000_000


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(b: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def canonical_json(obj: object) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def safe_parse(raw: bytes | None, label: str, errors: list[str]) -> dict:
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_JSON:
        errors.append(label+'_BYTES_MISSING_OR_OVERSIZED')
        return {}
    def reject_duplicate_keys(items):
        obj = {}
        for k,v in items:
            if k in obj: raise ValueError('duplicate JSON key')
            obj[k] = v
        return obj
    try:
        o = json.loads(raw.decode('utf-8', 'strict'), object_pairs_hook=reject_duplicate_keys,
                       parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
    except (UnicodeError, ValueError, TypeError):
        errors.append(label+'_MALFORMED_JSON')
        return {}
    if not isinstance(o, dict):
        errors.append(label+'_NOT_OBJECT')
        return {}
    return o


def inspect_lock(docket: dict, annotations: dict, lock: dict,
                 expected_lock_sha256: str | None, lock_bytes: bytes | None,
                 observed_heads: dict | None, bodies: dict | None) -> dict:
    """Require a *separately supplied* lock digest and exact original article bytes.

    The lock's own hash is not authority; pin must come from independent review.
    No inference from a matching digest to QD PASS or actual product sales.
    """
    errors = []
    blockers = ['INDEPENDENT_REVIEW_OF_LOCK_ORIGIN_REQUIRED',
                'QUALIFIED_FOOD_MEDICAL_EMERGENCY_PRIVACY_QD_REVIEW_REQUIRED',
                'FULL_NATIVE_BUILD_AND_AUTHENTIC_WORDPRESS_EXPORTS_REQUIRED',
                'FIVE_DISPUTED_SOURCE_RECORDS_UNRESOLVED',
                'NINE_UNSELECTED_FORKS_UNRESOLVED',
                'FOUNDER_RELEASE_AND_COMMERCE_APPROVAL_REQUIRED']
    if not isinstance(docket, dict):
        errors.append('DOCKET_NOT_OBJECT'); docket = {}
    if not isinstance(annotations, dict):
        errors.append('ANNOTATIONS_NOT_OBJECT'); annotations = {}
    if not isinstance(lock, dict):
        errors.append('LOCK_NOT_OBJECT'); lock = {}
    if not isinstance(lock_bytes, bytes) or not lock_bytes:
        errors.append('RAW_EXTERNAL_LOCK_BYTES_REQUIRED')
    if not isinstance(expected_lock_sha256, str) or not HEX64.fullmatch(expected_lock_sha256):
        errors.append('INDEPENDENT_LOCK_DIGEST_PIN_MISSING')
    elif not isinstance(lock_bytes, bytes) or sha256(lock_bytes) != expected_lock_sha256:
        errors.append('EXTERNAL_LOCK_DIGEST_MISMATCH')
    if isinstance(lock_bytes,bytes) and lock_bytes and lock_bytes != canonical_json(lock):
        errors.append('RAW_LOCK_NOT_CANONICAL_OR_OBJECT_MISMATCH')
    if lock.get('schema') != 1 or lock.get('repo') != REPO or lock.get('issue') != 136 or lock.get('conversion_issue') != 820:
        errors.append('LOCK_OWNER_SCHEMA_OR_ISSUE_DRIFT')
    if lock.get('release_state') != DRAFT or lock.get('review_state') != 'INDEPENDENT_REVIEW_REQUIRED':
        errors.append('LOCK_PREMATURE_REVIEW_OR_RELEASE_STATE')
    if lock.get('qd_pass') is not False or lock.get('publishing_allowed') is not False or lock.get('paid_offer_verified') is not False:
        errors.append('LOCK_CLAIMS_UNAPPROVED_PERMISSION')
    for name, value in [('docket_sha256', docket), ('citation_baseline_sha256', annotations)]:
        record = lock.get(name)
        if not isinstance(record, str) or not HEX64.fullmatch(record):
            errors.append('LOCK_DIGEST_MISSING:'+name)
        elif record != sha256(canonical_json(value)):
            errors.append('LOCK_DIGEST_DRIFT:'+name)
    if docket.get('schema') != 1 or annotations.get('schema') != 1:
        errors.append('ORIGINAL_DOCKET_OR_ANNOTATIONS_SCHEMA_MISSING')
    if observed_heads is None:
        errors.append('INDEPENDENT_NINE_CONTRIBUTOR_HEAD_OBSERVATIONS_MISSING'); observed_heads = {}
    if not isinstance(observed_heads, dict):
        errors.append('INVALID_HEAD_OBSERVATIONS'); observed_heads = {}
    pins = docket.get('branch_pins', [])
    if not isinstance(pins, list) or len(pins) != 9:
        errors.append('ORIGINAL_NINE_BRANCH_PINS_MISSING'); pins = []
    expected_heads = {p.get('branch'): p.get('sha') for p in pins if isinstance(p, dict)}
    if len(expected_heads) != 9 or any(not isinstance(k,str) or not isinstance(v,str) or not HEX40.fullmatch(v) for k,v in expected_heads.items()):
        errors.append('INVALID_ORIGINAL_BRANCH_PIN_MAP')
    if observed_heads != expected_heads:
        errors.append('CURRENT_CONTRIBUTOR_HEADS_NOT_AT_ORIGINAL_PINS')
    if lock.get('contributor_heads') != expected_heads:
        errors.append('EXTERNAL_LOCK_BRANCH_MAP_DRIFT')
    if bodies is None:
        errors.append('AUTHENTIC_ORIGINAL_ARTICLE_BYTES_MISSING'); bodies = {}
    if not isinstance(bodies, dict):
        errors.append('BODY_MAPPING_NOT_OBJECT'); bodies = {}
    original = docket.get('original_articles', [])
    if not isinstance(original, list) or len(original) != 35:
        errors.append('THIRTY_FIVE_ARTICLE_IDENTITIES_REQUIRED'); original = []
    article_locks = lock.get('articles')
    if not isinstance(article_locks, dict):
        errors.append('THIRTY_FIVE_EXTERNAL_ARTICLE_LOCKS_REQUIRED'); article_locks = {}
    originals = {a.get('slug'): a for a in original if isinstance(a,dict)}
    if len(originals) != 35 or any(not isinstance(s,str) or not SLUG.fullmatch(s) for s in originals):
        errors.append('ARTICLE_ORIGINAL_IDENTITY_COLLISION')
    if set(article_locks) != set(originals):
        errors.append('ARTICLE_LOCK_SET_NOT_EXACTLY_ORIGINAL_35')
    if set(bodies) != set(originals):
        errors.append('AUTHENTIC_ARTICLE_SET_NOT_EXACTLY_ORIGINAL_35')
    if set(annotations.get('articles', {}) if isinstance(annotations.get('articles'),dict) else {}) != set(originals):
        errors.append('ANNOTATION_ARTICLE_SET_NOT_EXACTLY_ORIGINAL_35')
    inspected = 0
    for slug in sorted(originals):
        row = article_locks.get(slug)
        raw = bodies.get(slug)
        if not isinstance(row, dict):
            errors.append('ARTICLE_LOCK_ROW_MISSING:'+slug); continue
        if not isinstance(raw, bytes) or not 0 < len(raw) <= 2_000_000:
            errors.append('ORIGINAL_BODY_BYTES_MISSING_OR_OVERSIZED:'+slug); continue
        if not isinstance(originals[slug].get('body_candidate_git_blobs'),list) or blob(raw) not in originals[slug]['body_candidate_git_blobs']:
            errors.append('BODY_NOT_ORIGINAL_GIT_CANDIDATE:'+slug)
        if row.get('body_git_blob') != blob(raw) or row.get('body_sha256') != sha256(raw) or row.get('byte_length') != len(raw):
            errors.append('ORIGINAL_BODY_EXTERNAL_LOCK_MISMATCH:'+slug)
        a = annotations.get('articles', {}).get(slug) if isinstance(annotations.get('articles'), dict) else None
        if not isinstance(a, dict) or row.get('citation_annotation_sha256') != sha256(canonical_json(a)):
            errors.append('ANNOTATION_EXTERNAL_LOCK_MISMATCH:'+slug)
        if a is None or not isinstance(a,dict) or a.get('body_git_blob') != blob(raw):
            errors.append('ANNOTATION_BODY_GIT_IDENTITY_MISMATCH:'+slug)
        inspected += 1
    # R440 and R442 have different scopes; either finding is a hard hold.
    try:
        from r440_original_slate_evidence_replay import inspect_docket
        errors.extend('R440:'+x for x in inspect_docket(docket, observed_heads))
    except (ImportError, ValueError, KeyError, TypeError):
        errors.append('R440_ORIGINAL_DOCKET_DEPENDENCY_UNAVAILABLE')
    try:
        from r442_claim_source_binding_gate import review_bundle
        lower = review_bundle(docket, bodies, annotations)
        errors.extend('R442:'+x for x in lower.get('errors', []))
        blockers.extend(lower.get('blockers', []))
    except (ImportError, ValueError, KeyError, TypeError):
        errors.append('R442_CLAIM_SOURCE_DEPENDENCY_UNAVAILABLE')
    return {'schema':1, 'repo':REPO, 'issue':136, 'conversion_issue':820,
            'release_state':DRAFT, 'eligible':False, 'qd_pass':False,
            'publishing_allowed':False, 'paid_offer_verified':False,
            'articles_examined':inspected, 'errors':sorted(set(errors)),
            'blockers':sorted(set(blockers)),
            'note':'Byte-pinned review artifacts cannot independently prove source accuracy, QD safety, commerce or reviewer authority.'}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='R443 external evidence lock, never a release PASS')
    p.add_argument('--docket', type=Path, required=True)
    p.add_argument('--frozen-citation-baseline', type=Path, required=True)
    p.add_argument('--external-lock', type=Path, required=True)
    p.add_argument('--expected-lock-sha256', required=True)
    p.add_argument('--observed-contributor-heads', type=Path, required=True)
    p.add_argument('--repo-root', type=Path, required=True)
    a = p.parse_args(argv)
    errors=[]
    def read(pth):
        if pth.is_symlink() or not pth.is_file() or not 0 < pth.stat().st_size <= MAX_JSON:
            raise OSError('missing, symlink or oversized')
        return pth.read_bytes()
    try:
        db=read(a.docket); ab=read(a.frozen_citation_baseline); lb=read(a.external_lock)
        docket=safe_parse(db,'DOCKET',errors)
        annotations=safe_parse(ab,'ANNOTATIONS',errors)
        lock=safe_parse(lb,'LOCK',errors)
        heads=safe_parse(read(a.observed_contributor_heads),'HEADS',errors)
        from r440_original_slate_evidence_replay import bounded_read
        bodies={a['slug']:bounded_read(a.repo_root,'preparedness/content/articles/'+a['slug']+'.body.html')
                for a in docket.get('original_articles',[]) if isinstance(a,dict)}
        report=inspect_lock(docket,annotations,lock,a.expected_lock_sha256,lb,heads,bodies)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError):
        report=inspect_lock({}, {}, {}, a.expected_lock_sha256, None, None, None)
        errors.append('INPUT_IO_OR_AUTHENTIC_CHECKOUT_FAILED')
    report['errors']=sorted(set(report['errors']+errors))
    print(json.dumps(report,indent=2,sort_keys=True))
    return 2

if __name__ == '__main__':
    sys.exit(main())
