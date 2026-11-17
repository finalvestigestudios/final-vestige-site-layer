#!/usr/bin/env python3
"""R444 read-only Preparedness regression closure and original-evidence custody.

All tests and integrity checks are structural, never source correctness, advice
safety, QD approval, publishing authority, authenticated purchase or revenue.
No network, subprocess, CMS changes, tracking, merchant calls, or file writes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path

DRAFT = 'DRAFT_HARD_HOLD'
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
ALLOWED = re.compile(r'preparedness/(?:tools|tests|reviews)/[a-zA-Z0-9_.-]+\Z')
REQUIRED_REVISIONS = tuple(range(434, 444))
MAX_BYTES = 2_000_000


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_file(root: Path, name: str) -> bytes:
    """Bounded no-follow read rooted within Preparedness; never trust path spelling."""
    if not isinstance(name, str) or not ALLOWED.fullmatch(name) or '..' in name or '\\' in name:
        raise ValueError('UNSAFE_EVIDENCE_PATH')
    base = root.resolve(strict=True)
    path = base.joinpath(*name.split('/'))
    if not path.parent.resolve(strict=True).is_relative_to(base):
        raise ValueError('EVIDENCE_PATH_ESCAPE')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size <= 0 or before.st_size > MAX_BYTES:
            raise ValueError('INVALID_EVIDENCE_FILE')
        data = b''
        while len(data) <= MAX_BYTES:
            chunk = os.read(fd, min(32768, MAX_BYTES + 1 - len(data)))
            if not chunk:
                break
            data += chunk
        after = os.fstat(fd)
        if (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_size) != (after.st_dev, after.st_ino, after.st_mtime_ns, after.st_size):
            raise ValueError('EVIDENCE_FILE_CHANGED_DURING_READ')
        if len(data) != before.st_size or len(data) > MAX_BYTES:
            raise ValueError('TRUNCATED_OR_OVERSIZED_EVIDENCE')
        return data
    finally:
        os.close(fd)


def audit(manifest: object, root: Path | None = None) -> dict:
    """Check revision closure and test receipt honesty; never grant release."""
    errors = []
    if not isinstance(manifest, dict):
        manifest = {}
        errors.append('MANIFEST_NOT_OBJECT')
    if manifest.get('schema') != 1 or manifest.get('repo') != 'finalvestigestudios/final-vestige-site-layer' or manifest.get('issue') != 136 or manifest.get('conversion_issue') != 820:
        errors.append('INTEGRATION_OWNER_OR_SCHEMA_DRIFT')
    if manifest.get('release_state') != DRAFT or manifest.get('publication_approved') is not False or manifest.get('qd_pass') is not False:
        errors.append('RELEASE_OR_QD_STATE_NOT_HARD_HOLD')
    if manifest.get('paid_offer_verified') is not False or manifest.get('net_revenue_verified') is not False:
        errors.append('FALSE_COMMERCIAL_VERIFICATION')
    if manifest.get('original_articles') != 35 or manifest.get('source_ids') != 203 or manifest.get('source_occurrences') != 280 or manifest.get('shared_url_groups') != 17:
        errors.append('ORIGINAL_SLATE_COUNTS_DRIFT')
    if manifest.get('source_disputes_unresolved') != 5 or manifest.get('forks_unselected') != 9:
        errors.append('UNADJUDICATED_SOURCE_OR_FORK_WAS_SELECTED')
    if manifest.get('native_build_verified') is not False or manifest.get('authentic_exports_verified') is not False:
        errors.append('UNPROVEN_NATIVE_BUILD_OR_EXPORT_CLAIM')
    records = manifest.get('records')
    if not isinstance(records, list):
        errors.append('SOURCE_RECORDS_MISSING')
        records = []
    seen_paths = set()
    revisions = set()
    counted = 0
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            errors.append('BAD_EVIDENCE_ROW:' + str(i))
            continue
        path = rec.get('path')
        revision = rec.get('revision')
        if not isinstance(path, str) or not ALLOWED.fullmatch(path) or '..' in path:
            errors.append('INVALID_EVIDENCE_PATH:' + str(i))
            continue
        if path in seen_paths:
            errors.append('DUPLICATE_EVIDENCE_PATH:' + path)
        seen_paths.add(path)
        if type(revision) is not int or revision not in REQUIRED_REVISIONS:
            errors.append('REVISION_OUTSIDE_PINNED_CHAIN:' + path)
        else:
            revisions.add(revision)
        if rec.get('role') not in ('source', 'test', 'review'):
            errors.append('UNDECLARED_EVIDENCE_ROLE:' + path)
        if not isinstance(rec.get('sha256'), str) or not HEX64.fullmatch(rec['sha256']):
            errors.append('MISSING_SHA256_PIN:' + path)
        if not isinstance(rec.get('git_blob'), str) or not HEX40.fullmatch(rec['git_blob']):
            errors.append('MISSING_GIT_BLOB_PIN:' + path)
        if type(rec.get('bytes')) is not int or not (0 < rec['bytes'] <= MAX_BYTES):
            errors.append('INVALID_BYTE_LENGTH:' + path)
        if root is not None:
            try:
                data = exact_file(Path(root), path)
                counted += 1
                if len(data) != rec.get('bytes') or sha256(data) != rec.get('sha256') or blob_sha(data) != rec.get('git_blob'):
                    errors.append('BYTES_OR_HASH_DRIFT:' + path)
            except (OSError, ValueError, TypeError):
                errors.append('MISSING_OR_UNSAFE_EVIDENCE_FILE:' + path)
    if set(REQUIRED_REVISIONS) != revisions:
        errors.append('INCOMPLETE_R434_TO_R443_REVISION_CLOSURE')
    for rev in REQUIRED_REVISIONS:
        if not any(isinstance(x, dict) and x.get('revision') == rev and x.get('role') in ('source', 'test') for x in records):
            errors.append('MISSING_EXECUTABLE_REVISION:' + str(rev))
    receipts = manifest.get('test_receipts')
    if not isinstance(receipts, list) or not receipts:
        errors.append('NO_TEST_RECEIPTS')
        receipts = []
    for i, receipt in enumerate(receipts):
        if not isinstance(receipt, dict):
            errors.append('INVALID_TEST_RECEIPT:' + str(i))
            continue
        if receipt.get('scope') not in ('new', 'focused', 'combined', 'historical-conflict'):
            errors.append('TEST_SCOPE_UNDECLARED:' + str(i))
        if type(receipt.get('run_count')) is not int or receipt['run_count'] <= 0:
            errors.append('TEST_COUNT_INVALID:' + str(i))
        if type(receipt.get('failure_count')) is not int or type(receipt.get('error_count')) is not int or receipt['failure_count'] < 0 or receipt['error_count'] < 0:
            errors.append('FAILURE_COUNT_INVALID:' + str(i))
        if receipt.get('claimed_pass') is True and (receipt.get('failure_count') != 0 or receipt.get('error_count') != 0):
            errors.append('FALSE_PASS_CLAIM:' + str(i))
        if receipt.get('scope') == 'combined' and receipt.get('claimed_pass') is True and receipt.get('all_inherited_files_authenticated') is not True:
            errors.append('UNAUTHENTICATED_CUMULATIVE_PASS:' + str(i))
    if root is None:
        errors.append('LOCAL_EXECUTED_FILES_NOT_SUPPLIED')
    return {
        'schema': 1, 'release_state': DRAFT, 'publication_approved': False,
        'qd_pass': False, 'commerce_approved': False, 'realized_revenue_verified': False,
        'r444_structural_check_only': not errors, 'evidence_files_read': counted,
        'errors': sorted(set(errors)),
        'blockers': [
            'ORIGINAL_35_MANUSCRIPT_NATIVE_BUILD_AND_70_EXPORTS_NOT_VERIFIED',
            'QUALIFIED_EMERGENCY_FOOD_MEDICAL_PRIVACY_AND_QD_REVIEW_REQUIRED',
            'FIVE_SOURCE_DISPUTES_AND_NINE_UNSELECTED_FORKS',
            'GROK_ASSET_ID_AND_FV_OWNED_PAYABLE_PRODUCT_NOT_AUTHENTICATED',
            'MERCHANT_CONFIRMED_ORDERS_FEES_REFUNDS_AND_7_30_DAY_COHORTS_MISSING'
        ]
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='R444 read-only Preparedness evidence/test closure')
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--root', type=Path)
    opts = parser.parse_args(argv)
    try:
        manifest = json.loads(opts.manifest.read_text('utf-8'))
    except (OSError, UnicodeError, ValueError):
        manifest = {}
    print(json.dumps(audit(manifest, opts.root), sort_keys=True, indent=2))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
