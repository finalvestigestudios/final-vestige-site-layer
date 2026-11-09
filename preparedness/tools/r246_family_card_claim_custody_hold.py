#!/usr/bin/env python3
"""R246 read-only source/claim discrepancy docket for Article 15 and Tool 104.

Checks exact original source identities and documents known REVIEW REQUIRED claims.
It cannot certify privacy, field minimization, medical safety, or publication.
No inputs are rendered or submitted and no personal details are read from users.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HOLD = 'DRAFT_HARD_HOLD'
SOURCES = {
    'content/articles/family-communication-plan.body.html': '8ac8bd7dba3be15d477c15737e54d83364d72527',
    'content/tools/family-reunification-card.body.html': 'be8698ac5d020476ff649d85813810e2000c6f98',
    'content/tools/family-reunification-card.meta.json': '47da1e7e20e39f0ea85e26d54a8d58301f6e0a15',
    'tools/reunion_card.js': 'b1a09b1eda1ae26f081de65b400a37bc19538035',
    'tools/shelter_common.js': 'efe1c7910d99437e3687621dabab8ce55dc24fd4',
}
A, T, M, J, C = SOURCES


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def unique_object(raw: bytes) -> dict:
    def pairs(xs):
        result = {}
        for key, value in xs:
            if key in result:
                raise ValueError('R246 duplicate metadata key: ' + key)
            result[key] = value
        return result
    def nonfinite(x):
        raise ValueError('R246 nonfinite metadata number: ' + x)
    out = json.loads(raw.decode('utf-8', 'strict'), object_pairs_hook=pairs,
                     parse_constant=nonfinite)
    if type(out) is not dict:
        raise ValueError('R246 metadata must be an object')
    return out


def assess_source_custody(inputs: dict[str, bytes], pins: dict[str, str] | None = None) -> dict:
    """Synthetic fixtures may supply pins; no pin choice can return approval."""
    pins = SOURCES if pins is None else pins
    if type(inputs) is not dict or type(pins) is not dict or set(inputs) != set(SOURCES) or set(pins) != set(SOURCES):
        raise ValueError('R246 requires exact five-source provenance')
    texts = {}
    fingerprints = []
    for path in SOURCES:
        raw = inputs[path]
        if type(raw) is not bytes or not 0 < len(raw) < 3_000_000 or b'\0' in raw:
            raise ValueError('R246 invalid source bytes: ' + path)
        oid = git_blob(raw)
        if pins[path] != oid:
            raise ValueError('R246 source identity changed; request independent review: ' + path)
        texts[path] = raw.decode('utf-8', 'strict')
        fingerprints.append(path + ':' + oid)
    meta = unique_object(inputs[M])
    if (meta.get('n') != 104 or meta.get('slug') != 'family-reunification-card'
            or meta.get('kind') != 'tool' or meta.get('status', {}).get('publish') != 'draft'
            or meta.get('safety_review', {}).get('state') != 'pending'):
        raise ValueError('R246 Tool 104 state changed; review required')
    if '{{link:family-reunification-card|fold-over wallet card}}' not in texts[A]:
        raise ValueError('R246 article-to-tool link provenance changed')
    if '{{cite:shelter-fcc-comms}}' not in texts[T]:
        raise ValueError('R246 original source citation missing from Tool 104')
    # Do not mechanically certify the truth or falsity of these statements.
    # They are known, high-consequence *review targets*. Changed text requires
    # an explicit source/version docket update rather than an automatic PASS.
    assertions = {
        'A15_LOCAL_DATA_ASSERTION': 'keeps what you type on your own device' in texts[A],
        'T104_NO_STORAGE_ASSERTION': 'It is not sent or saved. Closing the tab clears it.' in texts[T],
        'T104_MINIMAL_PROSE_ASSERTION': 'It prints only the out-of-area contact, a phone and the first meeting place.' in texts[T],
        'T104_MINIMAL_LABEL_ASSERTION': 'Minimal version: only the out-of-area contact, a phone number, the first meeting place and the review date' in texts[T],
        'T104_META_STORAGE_ASSERTION': 'Nothing is stored.' in str(meta.get('description', '')),
        'T104_MINIMAL_RUNTIME_REVIEW': all(x in texts[J] for x in (
            'function rcModel(fields, minimal)', 'row("Household", c.hhName)',
            'row("Phone", c.hhPhone)', 'row("Out-of-area contact", c.outName)',
            'var back = minimal')),
        'T104_HOME_PLAN_ASSUMPTION': 'Kept in our written plan at home.' in texts[J],
    }
    if not all(assertions.values()):
        raise ValueError('R246 original held-claim witness changed; refresh human adjudication docket')
    if 'function paDownloadText(filename, text)' not in texts[C]:
        raise ValueError('R246 shared tool helper provenance changed')
    receipt = hashlib.sha256(('\n'.join(fingerprints) + '\n' +
                             '\n'.join(sorted(assertions))).encode('utf-8')).hexdigest()
    return {
        'state': HOLD, 'issue': 136, 'conversion_issue': 820,
        'source_count': 5, 'held_claim_count': len(assertions),
        'held_claim_ids': sorted(assertions), 'receipt_sha256': receipt,
        'human_review_required': True, 'claim_truth_evaluated': False,
        'runtime_privacy_certified': False, 'release_authorized': False,
        'independent_qd_pass': False, 'source_review_approved': False,
        'medical_safety_verified': False, 'merchant_approved': False,
    }


def audit_family_card_claims(root: Path, safe_read) -> dict:
    return assess_source_custody({p: safe_read(root, p) for p in SOURCES})
