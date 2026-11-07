#!/usr/bin/env python3
"""R188: freeze independently observed Preparedness *producer code* identities.

This is a read-only admission precondition for the R186/R187 disposable native
pipeline. It detects accidental validator/build/test-gate code replacement before
executing them. It cannot validate the trustworthiness of itself or of the parent
runner, cannot prevent malicious runtime code, and is never a safety/QD review.
All evidence is DRAFT_HARD_HOLD, never release authorization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat

SCHEMA = 'fv-preparedness-r188-producer-code-custody-v1'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
# Git blob SHAs fetched from the connected GitHub repository at exact R187
# commit c881583358c485dcc02ca69e6cc275cd395a287a on 2026-11-07.
# A legitimate producer edit MUST be reviewed and repinned, not auto-admitted.
PINS = {
    'tools/validate.py': 'a0b6a1c8a63b7502125e5750b0bc1e3cf347620b',
    'tools/build.py': '349173d1e1d735eade218d95c7a0a2649c8cccd9',
    'tools/r161_body_custody_gate.py': 'e2c3ed8eb1e8f2a97a5146b8b4162be87cf02451',
    'tools/r174_rendered_citation_gate.py': 'b9eb91f01d88d00e8e38b8eacdcc086761bb97fc',
    'tools/r175_link_custody_gate.py': '794524902ebdc9bcc4c61d0070ed94634633577c',
    'tools/r176_native_review_preflight.py': '12e45241dd2a16bd5957b6031505234245caeb92',
    'tools/r177_safety_wording_gate.py': 'febf37090e00c82700da4cf228ba900983bf15ec',
    'tools/r178_safety_state_admission_gate.py': 'f4010a1a2a18aa24e201a4ba510511aafb86d465',
    'tools/r179_source_use_crosswalk_gate.py': 'b3007488e3ee3a095ccf394ebedb009a06a9641b',
    'tools/r180_docket_reconciliation_gate.py': '92a92c8122df81fb53ce0a859464638722bde595',
    'tools/r181_contributor_intake_gate.py': 'ee0982ef0a50e401d218acee9c7c4814c8aa56d8',
    'tools/r182_semantic_patch_reconciliation_gate.py': 'a2730ac6d221f387ca790e7f81f9981da0d25e23',
    'tools/r184_report_admission_gate.py': 'f55fc67280d7ceb81cbc50323171e50c64ed667d',
    'tools/r185_tool_custody_gate.py': 'fd9665aeaa18f57476e119da06ae60f56fd764c5',
    'tools/r186_whole_archive_preflight.py': 'e18a7f4018c3f366a3dd551285faa3f61a7aea7c',
    'tools/r187_receipt_contract_gate.py': '8d423aa65b8dd60941579babee707bc8b226b369',
}
PINNED_PARENT_SHA = 'c881583358c485dcc02ca69e6cc275cd395a287a'


def git_blob(payload: bytes) -> str:
    """Git's original blob SHA-1, NOT plain SHA-1 of the source text."""
    return hashlib.sha1(b'blob ' + str(len(payload)).encode('ascii') + b'\0' + payload).hexdigest()


def verify(preparedness: Path, pins: dict[str, str] | None = None) -> dict:
    """Raise ValueError on missing/replaced source before any producer runs.

    `pins` injection exists for isolated synthetic tests; production calls use
    the frozen authenticated PINS above. No file contents leave this function.
    """
    expected = PINS if pins is None else pins
    if not isinstance(expected, dict) or not expected:
        raise ValueError('missing immutable producer roster')
    if not preparedness.is_dir() or preparedness.is_symlink():
        raise ValueError('missing or symlinked Preparedness root')
    if not (preparedness / 'tools').is_dir() or (preparedness / 'tools').is_symlink():
        raise ValueError('missing or symlinked producer tools directory')
    for relative, sha in expected.items():
        if (not isinstance(relative, str) or
            re.fullmatch(r'tools/[A-Za-z0-9_]+\.py', relative) is None or
            not isinstance(sha, str) or re.fullmatch(r'[0-9a-f]{40}', sha) is None):
            raise ValueError('malformed producer pin')
    receipt = []
    for relative, sha in sorted(expected.items()):
        path = preparedness / relative
        try:
            # stat without following symlinks and refuse links/other file types.
            mode = path.lstat().st_mode
            if not stat.S_ISREG(mode):
                raise ValueError(relative + ': producer is not a regular file')
            if path.stat().st_size > 8_000_000:
                raise ValueError(relative + ': producer exceeds size bound')
            payload = path.read_bytes()
        except (FileNotFoundError, PermissionError) as exc:
            raise ValueError(relative + ': missing/unreadable producer') from exc
        if len(payload) > 8_000_000 or git_blob(payload) != sha:
            raise ValueError(relative + ': producer Git blob differs from R187 baseline')
        receipt.append({'path': relative, 'git_blob': sha})
    manifest = hashlib.sha256(json.dumps(receipt, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'schema': SCHEMA, 'state': HOLD, 'source_parent_sha': PINNED_PARENT_SHA,
            'producer_count': len(receipt), 'producer_manifest_sha256': manifest,
            'publication_authorized': False, 'independent_qd_pass': False,
            'qualified_source_review': False, 'qualified_safety_review_complete': False,
            'merchant_offer_verified': False, 'native_build_executed': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    try:
        packet = verify(args.repo / 'preparedness')
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        packet = {'schema': SCHEMA, 'state': INVALID, 'blocker': str(exc)[:300],
                  'publication_authorized': False, 'independent_qd_pass': False}
    print(json.dumps(packet, sort_keys=True))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
