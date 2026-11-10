#!/usr/bin/env python3
"""R261: source-bound, offline-only draft correction of Tool #104 print privacy.

Never writes original content or grants QD, privacy, medical or release approval.
Use a qualified editor and real browser/print testing before any publication.
"""
from __future__ import annotations

import hashlib
import re

SCHEMA = 'fv-preparedness-r261-family-card-print-remediation-draft-v1'
HOLD = 'DRAFT_HARD_HOLD'
PATH = 'content/tools/family-reunification-card.body.html'
ORIGINAL_BLOB = 'be8698ac5d020476ff649d85813810e2000c6f98'
NOTICE = ('Privacy: A printed card can be lost or photographed. Anyone who finds it can read it. '
          'Do not include full child names, home addresses, government ID numbers, '
          'medical diagnoses, passwords, or access codes. Review details before carrying.')
JS_NOTE = "Cut out each card and fold it on the dotted line to wallet size. Keep the card with you. Review it each year."
NOJS_OLD = 'The form below still works and prints. Only the automatic reminders and the text download need JavaScript.'
NOJS_NEW = ('Use the blank printable card below and fill it in by hand. The interactive '
            'preview, automatic reminders and text download require JavaScript.')
FALLBACK = '<noscript><div class="pa-printsheet"><div class="pa-foldcard">'
FALLBACK_NEW = ('<noscript><div class="pa-printsheet">'
                '<p class="pa-printpage-note" role="note">' + NOTICE + '</p>'
                '<div class="pa-foldcard">')


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def propose(raw: bytes, *, expected_blob: str = ORIGINAL_BLOB):
    if type(raw) is not bytes or not raw or len(raw) > 3_000_000 or b'\0' in raw:
        raise ValueError('R261 invalid original source bytes')
    if type(expected_blob) is not str or not re.fullmatch(r'[0-9a-f]{40}', expected_blob):
        raise ValueError('R261 invalid source pin')
    if git_blob(raw) != expected_blob:
        raise ValueError('R261 source identity changed: independent review needed')
    text = raw.decode('utf-8', 'strict')
    expected = (
        ("'" + JS_NOTE + "'", "'" + JS_NOTE + ' ' + NOTICE + "'"),
        (FALLBACK, FALLBACK_NEW),
        (NOJS_OLD, NOJS_NEW),
    )
    for old, new in expected:
        if text.count(old) != 1 or new in text:
            raise ValueError('R261 draft anchor missing, duplicated or already changed')
        text = text.replace(old, new, 1)
    if any(s in NOTICE for s in ("'", '\\', '<', '>', '\n', '\r')):
        raise ValueError('R261 JS/HTML notice needs safe literal review')
    if any(s in NOJS_NEW for s in ('<', '>', '\n', '\r')):
        raise ValueError('R261 no-JS copy needs safe text review')
    if (text.count(NOTICE) != 2 or NOJS_OLD in text or
            text.count(FALLBACK_NEW) != 1 or
            not re.search(r'@media\s+print\s*\{', text)):
        raise ValueError('R261 print paths not independently preserved')
    # Reconstruct originals and assert exact byte equality: limits changes to three
    # reviewable anchors, preserving every citation/link, field, route and source.
    reconstructed = text.replace(NOJS_NEW, NOJS_OLD, 1).replace(FALLBACK_NEW, FALLBACK, 1)
    reconstructed = reconstructed.replace("'" + JS_NOTE + ' ' + NOTICE + "'", "'" + JS_NOTE + "'", 1)
    if reconstructed.encode('utf-8') != raw:
        raise ValueError('R261 reconstruction failed: content may have drifted')
    if (re.findall(r'\{\{(?:cite|link):[^}]+\}\}', text) !=
            re.findall(r'\{\{(?:cite|link):[^}]+\}\}', raw.decode('utf-8'))):
        raise ValueError('R261 source/citation evidence changed')
    result = {
        'schema': SCHEMA, 'state': HOLD, 'source_path': PATH,
        'original_git_blob': expected_blob,
        'draft_git_blob': git_blob(text.encode('utf-8')),
        'changed_anchor_count': 3, 'draft_notice_occurrences': 2,
        'javascript_print_note_contains_notice': True,
        'nojs_print_sheet_contains_notice': True,
        'nojs_functionality_claim_corrected_in_draft': True,
        'original_source_unchanged': True,
        'independent_editorial_review_required': True,
        'real_browser_and_print_tests_required': True,
        'privacy_certified': False, 'medical_safety_verified': False,
        'independent_qd_pass': False, 'source_review_approved': False,
        'merchant_approved': False, 'release_authorized': False,
        'public_published': False,
    }
    return text, result


def audit(root, safe_read):
    """Pre-render gate: build in memory, return only a held evidence receipt."""
    _draft, receipt = propose(safe_read(root, PATH))
    return receipt
