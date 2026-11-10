#!/usr/bin/env python3
"""R263: source-bound witness for privacy notice OUTSIDE the cut-out wallet card.

A visible print-page notice is not necessarily part of a card once cut out.
This is a read-only, fail-closed negative finding on the R262 candidate, not
an alternate design, rendering test, privacy certification, or QD clearance.
"""
from __future__ import annotations

import hashlib
import re

SCHEMA = 'fv-preparedness-r263-wallet-cutout-privacy-witness-v1'
HOLD = 'DRAFT_HARD_HOLD'
ORIGINAL_BLOB = 'be8698ac5d020476ff649d85813810e2000c6f98'
NOTICE_PREFIX = 'Privacy: A printed card can be lost or photographed.'
JS_NOTE_PREFIX = "pr.appendChild(el('p', 'pa-printpage-note', 'Cut out each card"
JS_CARD = "var c = el('div', 'pa-foldcard'); c.appendChild(face('Emergency contacts', m.front)); c.appendChild(face(minimal ? 'Reviewed' : 'School and care', m.back)); pr.appendChild(c);"
JS_FACE_START = 'function face(title, rows) {'
JS_FACE_END = 'function clear(node) {'
FALLBACK_START = '<noscript><div class="pa-printsheet">'
FOLD_OPEN = '<div class="pa-foldcard">'
FALLBACK_CLOSE = '</div></div></div></noscript>'
PRINT_CARD_CSS = '.pa-foldcard { display: grid !important; grid-template-columns: 1fr 1fr; width: 7in; height: 2.125in;'
PRINT_FACE_CSS = '.pa-foldcard .pa-face { border: 0; border-right: 1px dashed #000; padding: .07in .1in; font-size: 7.5pt; line-height: 1.14; overflow: hidden; height: 2.125in; }'
REQUIRED_FALSE = ('privacy_certified', 'medical_safety_verified', 'independent_qd_pass',
                  'source_review_approved', 'merchant_approved', 'release_authorized',
                  'public_published')
CITATION = re.compile(r'\{\{(?:cite|link):[^}]+\}\}')


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def _unique_window(content: str, start: str, end: str, label: str) -> tuple[str, int, int]:
    if content.count(start) != 1:
        raise ValueError('R263 nonunique ' + label + ' start')
    a = content.index(start)
    b = content.find(end, a + len(start))
    if b == -1:
        raise ValueError('R263 missing ' + label + ' end')
    return content[a:b+len(end)], a, b+len(end)


def inspect(raw: bytes, r261, r262, *, expected_original_blob: str = ORIGINAL_BLOB) -> dict:
    if type(raw) is not bytes or not raw or len(raw) > 3_000_000 or b'\0' in raw:
        raise ValueError('R263 invalid original source bytes')
    if type(expected_original_blob) is not str or re.fullmatch(r'[0-9a-f]{40}', expected_original_blob) is None:
        raise ValueError('R263 invalid source pin')
    if git_blob(raw) != expected_original_blob:
        raise ValueError('R263 original source identity mismatch')
    if not callable(getattr(r262, 'propose', None)) or not callable(getattr(r261, 'propose', None)):
        raise ValueError('R263 prior authenticated gates missing')
    original = raw.decode('utf-8', 'strict')
    draft, prior = r262.propose(raw, r261, expected_original_blob=expected_original_blob)
    if type(draft) is not str or type(prior) is not dict:
        raise ValueError('R263 prior draft types changed')
    if (prior.get('state') != HOLD or prior.get('original_git_blob') != expected_original_blob
            or prior.get('r262_candidate_blob') != git_blob(draft.encode('utf-8'))
            or prior.get('two_print_privacy_notices_retained') is not True
            or prior.get('citations_and_links_unchanged') is not True
            or prior.get('original_source_unchanged') is not True
            or any(prior.get(k) is not False for k in REQUIRED_FALSE)):
        raise ValueError('R263 R262 custody or release drift')
    if (not hasattr(r262, 'CORRECTED') or draft.count(r262.CORRECTED) != 1
            or any(x in draft.lower() for x in ('automatic reminders', 'text download'))):
        raise ValueError('R263 R262 corrected functionality copy changed')
    if CITATION.findall(draft) != CITATION.findall(original):
        raise ValueError('R263 original citation/link sequence changed')
    if draft.count(NOTICE_PREFIX) != 2:
        raise ValueError('R263 two inherited print-page privacy notices changed')
    if draft.count(PRINT_CARD_CSS) != 1 or draft.count(PRINT_FACE_CSS) != 1:
        raise ValueError('R263 print dimensions or clipping CSS changed')
    if draft.count(JS_CARD) != 1 or draft.count(JS_NOTE_PREFIX) != 1:
        raise ValueError('R263 JS print-page/card structure changed')
    face, _, _ = _unique_window(draft, JS_FACE_START, JS_FACE_END, 'dynamic card face')
    jsprint, _, _ = _unique_window(draft, JS_NOTE_PREFIX, JS_CARD, 'JS print-page segment')
    if jsprint.count(NOTICE_PREFIX) != 1 or NOTICE_PREFIX in face:
        raise ValueError('R263 JS on-card/preamble witness drift')
    nojs, _, _ = _unique_window(draft, FALLBACK_START, FALLBACK_CLOSE, 'no-JS card')
    original_nojs, _, _ = _unique_window(original, FALLBACK_START, FALLBACK_CLOSE, 'original no-JS card')
    if re.findall(r'<b>([^<]+)</b>', nojs) != re.findall(r'<b>([^<]+)</b>', original_nojs):
        raise ValueError('R263 no-JS original field labels changed in candidate')
    if nojs.count(FOLD_OPEN) != 1:
        raise ValueError('R263 no-JS card count drift')
    preamble, cutout = nojs.split(FOLD_OPEN, 1)
    if (preamble.count(NOTICE_PREFIX) != 1 or NOTICE_PREFIX in cutout
            or cutout.count('class="pa-face"') != 2
            or cutout.count('<b>') != 13):
        raise ValueError('R263 no-JS on-card/preamble or field witness drift')
    # This is intentionally a NON-PASS: warnings are on the printed sheet, but
    # not bound to the wallet-size card that a reader is instructed to cut out.
    return {
        'schema': SCHEMA, 'state': HOLD, 'original_git_blob': expected_original_blob,
        'r262_candidate_blob': prior['r262_candidate_blob'],
        'nojs_source_field_count': 13, 'nojs_cutout_faces': 2,
        'print_css_card_height_in': '2.125', 'print_css_face_overflow_hidden': True,
        'javascript_warning_on_print_page_only': True,
        'nojs_warning_on_print_page_only': True,
        'wallet_cutout_has_privacy_warning': False,
        'printed_card_privacy_resolved': False,
        'actual_browser_and_physical_cutout_qa_completed': False,
        'qualified_child_privacy_review_completed': False,
        'requires_editorial_resolution_before_publication': True,
        'original_source_unchanged': True,
        'release_authorized': False, 'public_published': False,
        'independent_qd_pass': False, 'privacy_certified': False,
        'medical_safety_verified': False, 'source_review_approved': False,
        'merchant_approved': False,
    }


def audit(root, safe_read, r261, r262) -> dict:
    """Produce held source-level evidence; neither export nor alter a card."""
    return inspect(safe_read(root, r261.PATH), r261, r262)
