#!/usr/bin/env python3
"""R262: source-bound no-JavaScript truthfulness correction, offline only.

R261's proposed functionality copy still promises a text download and reminders
that are not present in the authenticated original Tool #104. This gate checks
specific original DOM/JS affordances and emits only a further UNPUBLISHED draft.
Static source observations are not browser, print, privacy or medical approvals.
"""
from __future__ import annotations

import hashlib
import re

SCHEMA = 'fv-preparedness-r262-nojs-functionality-truth-draft-v1'
HOLD = 'DRAFT_HARD_HOLD'
ORIGINAL_BLOB = 'be8698ac5d020476ff649d85813810e2000c6f98'
R261_INACCURATE = ('Use the blank printable card below and fill it in by hand. The interactive '
                   'preview, automatic reminders and text download require JavaScript.')
CORRECTED = ("Use your browser's Print command to print the blank card below, then fill "
             'it in by hand. The on-page form, preview, Print button and Clear '
             'everything button require JavaScript.')
# These exact original-source affordances—not marketing claims—anchor our copy.
CONTROL_ANCHORS = (
    '<form class="pa-sheet pa-card-mainhide" id="rc"',
    'id="rc-preview"',
    'id="rc-print" hidden>',
    'id="rc-reset" hidden>',
    "$('rc-live').hidden = false;",
    "$('rc-print').hidden = false; $('rc-print').addEventListener('click', function () { window.print(); });",
    "$('rc-reset').hidden = false; $('rc-reset').addEventListener('click', function () { form.reset(); render(); });",
    '<noscript><style>#rc, #rc-warn { display: none; }</style></noscript>',
    '<noscript><div class="pa-printsheet"><div class="pa-foldcard">',
)
CITATION_TOKEN = re.compile(r'\{\{(?:cite|link):[^}]+\}\}')


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def propose(raw: bytes, r261, *, expected_original_blob: str = ORIGINAL_BLOB):
    if type(raw) is not bytes or not raw or len(raw) > 3_000_000 or b'\0' in raw:
        raise ValueError('R262 original body bytes invalid')
    if type(expected_original_blob) is not str or re.fullmatch('[0-9a-f]{40}', expected_original_blob) is None:
        raise ValueError('R262 malformed original pin')
    if git_blob(raw) != expected_original_blob:
        raise ValueError('R262 original Tool 104 source pin mismatch')
    source = raw.decode('utf-8', 'strict')
    for anchor in CONTROL_ANCHORS:
        if source.count(anchor) != 1:
            raise ValueError('R262 missing/duplicated original UI affordance: ' + anchor[:48])
    if source.count('The form below still works and prints.') != 1:
        raise ValueError('R262 original no-JS claim not located once')
    if not callable(getattr(r261, 'propose', None)):
        raise ValueError('R262 missing authenticated R261 source proposal')
    prior, prior_receipt = r261.propose(raw, expected_blob=expected_original_blob)
    if (type(prior) is not str or type(prior_receipt) is not dict
            or prior_receipt.get('state') != HOLD
            or prior_receipt.get('original_git_blob') != expected_original_blob
            or prior_receipt.get('draft_git_blob') != git_blob(prior.encode('utf-8'))
            or prior_receipt.get('changed_anchor_count') != 3
            or prior_receipt.get('draft_notice_occurrences') != 2
            or prior_receipt.get('release_authorized') is not False
            or prior_receipt.get('privacy_certified') is not False
            or prior_receipt.get('independent_qd_pass') is not False):
        raise ValueError('R262 prior draft custody/release state mismatch')
    if prior.count(R261_INACCURATE) != 1 or CORRECTED in prior:
        raise ValueError('R262 R261 unsupported functionality claim drift')
    draft = prior.replace(R261_INACCURATE, CORRECTED, 1)
    if (draft.replace(CORRECTED, R261_INACCURATE, 1) != prior
            or any(x in draft.lower() for x in ('automatic reminders', 'text download'))):
        raise ValueError('R262 unsupported feature promise remains in draft')
    # No unrelated text, source tokens, privacy warnings or form fields may move.
    if CITATION_TOKEN.findall(draft) != CITATION_TOKEN.findall(source):
        raise ValueError('R262 citation/link tokens changed')
    for anchor in CONTROL_ANCHORS:
        if draft.count(anchor) != 1:
            raise ValueError('R262 actual affordances lost')
    if draft.count('Privacy: A printed card can be lost or photographed.') != 2:
        raise ValueError('R262 inherited JS/no-JS print privacy notices lost')
    return draft, {
        'schema': SCHEMA, 'state': HOLD, 'original_git_blob': expected_original_blob,
        'r261_candidate_blob': git_blob(prior.encode('utf-8')),
        'r262_candidate_blob': git_blob(draft.encode('utf-8')),
        'unsupported_feature_promises_removed': 2,
        'review_only_claim_replacements': 1,
        'required_static_affordances': len(CONTROL_ANCHORS),
        'static_affordance_checks_pass': True,
        'two_print_privacy_notices_retained': True,
        'citations_and_links_unchanged': True,
        'original_source_unchanged': True,
        'independent_editorial_review_required': True,
        'real_browser_and_print_tests_required': True,
        'privacy_certified': False, 'medical_safety_verified': False,
        'independent_qd_pass': False, 'source_review_approved': False,
        'merchant_approved': False, 'release_authorized': False,
        'public_published': False,
    }


def audit(root, safe_read, r261):
    """R220 pre-render gate; no file, browser, merchant or WordPress writes."""
    _unpublished, receipt = propose(safe_read(root, r261.PATH), r261)
    return receipt
