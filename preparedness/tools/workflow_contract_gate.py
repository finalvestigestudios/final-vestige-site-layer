#!/usr/bin/env python3
"""R19: exact, read-only PR workflow contract and R18 HOLD receipt verification.

An Actions green check proves machine custody ONLY. Never infer source accuracy,
qualified emergency/medical review, independent QD approval or permission to publish.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

WORKFLOW_PATH = '.github/workflows/preparedness-private-preflight.yml'
WORKFLOW_SHA256 = 'fd95747ebb685c87e8c254c40b822afeeffa647115bbf628bed7b2fd5eb8c0d0'
GATE_NAMES = (
    'native_validation', 'private_draft_build', 'native_unit_suite',
    'canonical_claim_corpus', 'draft_export_custody', 'rendered_citation_parity',
    'uncited_action_triage', 'outbound_link_custody', 'source_crosswalk_truth',
    'current_safety_copy_custody', 'seven_cluster_git_parity',
    'frozen_81_file_archive_custody',
)
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
RECEIPT_LIMIT = 150_000


class ContractHold(ValueError):
    """Unsafe or incomplete machine evidence; publication remains HOLD."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ContractHold(message)


def hex_sha(s: object, length: int = 64) -> bool:
    return isinstance(s, str) and (HEX64 if length == 64 else HEX40).fullmatch(s) is not None


def canonical_bytes(o: object) -> bytes:
    return json.dumps(o, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':')).encode('utf-8')


def check_workflow(repo_root: Path) -> dict:
    require(repo_root.is_dir() and not repo_root.is_symlink(), 'checkout root must be a directory')
    root = repo_root.resolve(strict=True)
    wf = root / WORKFLOW_PATH
    require(wf.is_file() and not wf.is_symlink() and wf.resolve().is_relative_to(root),
            'workflow missing, linked or escaped checkout')
    require(0 < wf.stat().st_size <= 16_384, 'unbounded workflow size')
    data = wf.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    require(digest == WORKFLOW_SHA256,
            'PR workflow contract drift: verify permissions, event, actions and command safety')
    return {'schema_version': 1, 'issue': 136, 'gate': 'R19_CI_WORKFLOW_CONTRACT',
            'workflow_sha256': digest, 'release_state': 'HOLD', 'may_publish': False,
            'authority': 'PR_MACHINE_WORKFLOW_ONLY', 'independent_QD_approval': False}


def verify_receipt(receipt: object, expected_head: str) -> dict:
    require(hex_sha(expected_head, 40), 'exact current Git commit SHA required')
    require(type(receipt) is dict, 'R18 receipt is not a JSON object')
    require(receipt.get('schema_version') == 1 and receipt.get('issue') == 136,
            'wrong receipt schema or issue')
    require(receipt.get('exact_checkout_sha') == expected_head, 'stale/different checkout')
    require(receipt.get('authority') == 'MACHINE_LOCAL_DRAFT_CUSTODY_ONLY',
            'unsupported approval authority')
    require(receipt.get('release_state') == 'HOLD' and receipt.get('may_publish') is False,
            'release status was not a definite HOLD')
    for key in ('wordpress_publishing_performed', 'independent_QD_approval',
                'source_claim_accuracy_verified', 'qualified_medical_or_emergency_safety_review'):
        require(receipt.get(key) is False, 'unsafe claimed approval or publication: ' + key)
    require(receipt.get('all_required_machine_gates_executed') is True,
            'R18 did not execute all machine gates')
    steps = receipt.get('steps')
    require(type(steps) is list and len(steps) == len(GATE_NAMES),
            'incomplete or extra gate results')
    for name, step in zip(GATE_NAMES, steps):
        require(type(step) is dict and step.get('gate') == name,
                'out-of-order, missing, duplicated or substituted gate')
        require(type(step.get('exit_code')) is int and step['exit_code'] == 0,
                name + ': nonzero exit code')
        for key in ('stdout_sha256', 'stderr_sha256'):
            require(hex_sha(step.get(key)), name + ': missing or forged output digest')
        if name == 'native_unit_suite':
            count = step.get('native_test_count')
            require(type(count) is int and 36 <= count <= 100_000,
                    'fewer than 36 actual passing native tests or invalid count')
            require('receipt_sha256' not in step and 'state' not in step,
                    'native unittest result incorrectly represented as independent review')
        elif name not in ('native_validation', 'private_draft_build'):
            require(step.get('state') == 'HOLD' and hex_sha(step.get('receipt_sha256')),
                    name + ': missing authoritative HOLD receipt digest')
        else:
            require('native_test_count' not in step and 'receipt_sha256' not in step,
                    name + ': native script claims unrelated evidence')
    fingerprint = receipt.get('fingerprint_sha256')
    require(hex_sha(fingerprint), 'missing exact R18 fingerprint')
    without_fingerprint = {k: v for k, v in receipt.items() if k != 'fingerprint_sha256'}
    require(hashlib.sha256(canonical_bytes(without_fingerprint)).hexdigest() == fingerprint,
            'R18 receipt fingerprint mismatch')
    require(set(receipt) == {'schema_version', 'issue', 'exact_checkout_sha', 'authority',
                            'release_state', 'may_publish', 'wordpress_publishing_performed',
                            'independent_QD_approval', 'source_claim_accuracy_verified',
                            'qualified_medical_or_emergency_safety_review',
                            'all_required_machine_gates_executed', 'steps', 'fingerprint_sha256'},
            'unexpected receipt keys or unexamined claims')
    return {'schema_version': 1, 'issue': 136, 'gate': 'R19_RECEIPT_CONTRACT',
            'exact_checkout_sha': expected_head,
            'verified_machine_step_count': len(GATE_NAMES),
            'native_test_count': steps[2]['native_test_count'],
            'r18_fingerprint_sha256': fingerprint,
            'release_state': 'HOLD', 'may_publish': False,
            'independent_QD_approval': False, 'qualified_safety_clearance': False}


def read_receipt(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink(), 'receipt must be an ordinary file')
    require(0 < path.stat().st_size <= RECEIPT_LIMIT, 'receipt empty or oversized')
    data = path.read_bytes()
    try:
        obj = json.loads(data.decode('utf-8', errors='strict'),
                         parse_constant=lambda t: (_ for _ in ()).throw(ValueError(t)),
                         object_pairs_hook=unique_json_object)
    except (UnicodeError, ValueError, TypeError) as exc:
        raise ContractHold('invalid or duplicated JSON receipt data') from exc
    return obj


def unique_json_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for k, v in pairs:
        require(k not in result, 'duplicate JSON field: ' + k)
        result[k] = v
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--expected-head')
    args = parser.parse_args(argv)
    try:
        result = check_workflow(args.repo_root)
        require(bool(args.receipt) == bool(args.expected_head),
                'receipt and exact current SHA must be supplied together')
        if args.receipt:
            result['r18_receipt'] = verify_receipt(read_receipt(args.receipt), args.expected_head)
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0  # Passing machine integrity does not authorize public release.
    except (ContractHold, OSError, ValueError, UnicodeError, TypeError) as exc:
        print(json.dumps({'schema_version': 1, 'issue': 136,
                          'gate': 'R19_PRIVATE_CI', 'integrity': 'FAILED',
                          'release_state': 'HOLD', 'may_publish': False,
                          'error': str(exc)}, sort_keys=True))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
