#!/usr/bin/env python3
"""Review-only Article 15 / Tool 104 field-disclosure crosswalk.

Source hashes are evidence custody, NEVER proof of medical/privacy/sales safety.
No WordPress, network, personal inputs, or production side effects.
"""
from __future__ import annotations
import hashlib
import json
import re
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
# The 13 user-entered fields eligible for the front/back fold-over card.
# Minimal mode is NOT an anonymity or only-four-fields guarantee.
FIELDS = (
    ('hhName', 'Household', True), ('hhPhone', 'Phone', True),
    ('outName', 'Out-of-area contact', True), ('outPhone', 'Out-of-area phone', True),
    ('meet1', 'Meet first at', True), ('meet2', 'If not, meet at', False),
    ('school', 'School or childcare', False), ('schoolPlan', 'Reunification plan', False),
    ('pickup', 'Pick-up reminder', False), ('careName', 'Caregiver', False),
    ('carePhone', 'Caregiver phone', False), ('access', 'Communication needs', False),
    ('reviewed', 'Reviewed', True),
)
EXTRA_MINIMAL = 'Kept in our written plan at home.'
HTML_MINIMAL = ('It prints only the out-of-area contact, a phone and the first meeting place.',
                'Minimal version: only the out-of-area contact, a phone number, the first meeting place and the review date')
HTML_NOJS = 'The form below still works and prints.'


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def unique_json(raw: bytes) -> dict:
    def unique(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError('R248 duplicate metadata key')
            d[k] = v
        return d
    obj = json.loads(raw.decode('utf-8', 'strict'), object_pairs_hook=unique,
                     parse_constant=lambda x: (_ for _ in ()).throw(ValueError('R248 invalid constant')))
    if type(obj) is not dict:
        raise ValueError('R248 metadata must be an object')
    return obj


def inspect(originals: dict[str, bytes], pins: dict[str, str] | None = None) -> dict:
    if pins is None:
        pins = SOURCES
    if type(originals) is not dict or type(pins) is not dict or set(originals) != set(SOURCES) or set(pins) != set(SOURCES):
        raise ValueError('R248 five-source roster changed')
    decoded = {}
    for path in SOURCES:
        raw = originals[path]
        if type(raw) is not bytes or not 0 < len(raw) < 3_000_000 or b'\0' in raw:
            raise ValueError('R248 invalid source bytes')
        if git_blob(raw) != pins[path]:
            raise ValueError('R248 original source identity changed')
        decoded[path] = raw.decode('utf-8', 'strict')
    meta = unique_json(originals[M])
    if (type(meta.get('n')) is not int or meta['n'] != 104
            or meta.get('status', {}).get('publish') != 'draft'
            or meta.get('safety_review', {}).get('state') != 'pending'):
        raise ValueError('R248 original safety/publish state drift')
    js = decoded[J]
    scope = re.search(r'function\s+rcModel\s*\(\s*fields\s*,\s*minimal\s*\)\s*\{(.*?)\n\}', js, re.S)
    if scope is None:
        raise ValueError('R248 rcModel absent or structurally changed')
    model = scope.group(1)
    rows = re.findall(r'row\(\s*"([^"]+)"\s*,\s*c\.(\w+)\s*\)', model)
    expected = ([(label, key) for key, label, _ in FIELDS[:6]]
                + [('Reviewed', 'reviewed')]
                + [(label, key) for key, label, _ in FIELDS[6:]])
    if rows != expected or len(set(rows)) != 13 or len(rows) != 14:
        raise ValueError('R248 field/label-to-model crosswalk drift')
    if ('minimal ? null : row("If not, meet at", c.meet2)' not in model or
            'var back = minimal' not in model or
            'row("Reviewed", c.reviewed), { k: "Details", v: "' + EXTRA_MINIMAL + '" }' not in model):
        raise ValueError('R248 minimal branch or blanket home-plan claim drift')
    if ('function rcClean(' not in js or 'function paCleanText(' not in decoded[C]):
        raise ValueError('R248 original sanitizer chain drift')
    tool = decoded[T]
    if any(tool.count(phrase) != 1 for phrase in HTML_MINIMAL) or tool.count(HTML_NOJS) != 1:
        raise ValueError('R248 public-facing minimal/noJS claims drift')
    if ('what you type stays on this page. It is not sent or saved.' not in tool
            or 'keeps what you type on your own device' not in decoded[A]
            or 'Nothing is stored.' not in str(meta.get('description', ''))):
        raise ValueError('R248 unresolved privacy assurance drift')
    # No source data, names, phone numbers or household inputs are written to receipts.
    matrix = [{'field': key, 'print_label': label, 'in_minimal': in_minimal,
               'in_full': True, 'reader_authorization': 'UNREVIEWED'}
              for key, label, in_minimal in FIELDS]
    receipt_input = '\n'.join(f'{p}:{git_blob(originals[p])}' for p in SOURCES)
    receipt = hashlib.sha256((receipt_input + '\nR248:13:6:7:HARD_HOLD').encode()).hexdigest()
    return {'state': HOLD, 'issue': 136, 'conversion_issue': 820,
            'source_count': 5, 'full_field_count': 13, 'minimal_field_count': 6,
            'minimal_excluded_field_count': 7, 'unconditional_minimal_household_name': True,
            'unconditional_minimal_household_phone': True,
            'unconditional_home_plan_statement': True,
            'claimed_only_list_is_incomplete': True,
            'nojs_form_claim_is_contradicted': True,
            'privacy_claim_scope_requires_browser_review': True,
            'field_matrix': matrix, 'receipt_sha256': receipt,
            'reader_disclosure_approved': False, 'privacy_certified': False,
            'claims_adjudicated': False, 'medical_safety_verified': False,
            'source_review_approved': False, 'independent_qd_pass': False,
            'merchant_approved': False, 'release_authorized': False,
            'human_review_required': True}


def audit(root: Path, safe_read) -> dict:
    return inspect({p: safe_read(root, p) for p in SOURCES})
