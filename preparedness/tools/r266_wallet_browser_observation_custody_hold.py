#!/usr/bin/env python3
"""R266 bound ONE offline Chromium print observation; never a safety/pass gate.

Retains negative mobile-overflow evidence and all human-release holds. This
receipt is not real-paper testing, an accessibility audit, or a browser matrix.
"""
from __future__ import annotations
import hashlib
import json
import re

SCHEMA = 'fv-preparedness-r266-bounded-browser-observation-v1'
HOLD = 'DRAFT_HARD_HOLD'
CANDIDATE_PATH = 'audits/r264_minimal_wallet_card_REVIEW_ONLY.html'
OBSERVATION_PATH = 'audits/r266_chromium_wallet_print_observation_REVIEW_ONLY.json'
CANDIDATE_BLOB = '40782ef142edfd348fec53eb6d8a0dc673244dea'
NO_APPROVAL = ('original_tool_104_rendered', 'physical_cut_fold_completed',
    'legibility_and_accessibility_approved', 'qualified_child_privacy_approved',
    'source_citation_approved', 'independent_qd_pass', 'merchant_approved',
    'release_authorized', 'public_published')
EXPECTED = {
    'schema': SCHEMA, 'state': HOLD,
    'observation_date_utc': '2026-11-10', 'browser_engine': 'Chromium',
    'browser_major': 144,
    'method': 'local Playwright set_content; print media; Letter PDF; no network or household data',
    'original_candidate_git_blob': CANDIDATE_BLOB,
    'javascript_on_pdf_sha256': '1dae8e974cd87e629f670e3393a5361bccc328ff9307e7984a32c9f899f6d251',
    'javascript_off_pdf_sha256': '1dae8e974cd87e629f670e3393a5361bccc328ff9307e7984a32c9f899f6d251',
    'pdf_pages_observed': 1, 'print_card_width_css_px': 672,
    'print_card_height_css_px': 206, 'print_face_width_css_px': 335,
    'print_warning_font_css_px': 10.6667,
    'warnings_present_in_pdf_text': True, 'javascript_off_pdf_matches_on': True,
    'screen_widths_checked_css_px': [360, 390, 768, 1440],
    'screen_document_widths_css_px': [680, 680, 768, 1440],
    'mobile_horizontal_overflow_observed': True,
    **{k: False for k in NO_APPROVAL},
}

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def _reject_duplicates(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError('R266 duplicate evidence key: ' + k)
        d[k] = v
    return d

def inspect(candidate: bytes, raw_receipt: bytes, previous: dict) -> dict:
    if type(candidate) is not bytes or git_blob(candidate) != CANDIDATE_BLOB:
        raise ValueError('R266 candidate source differs from observed Git blob')
    if type(raw_receipt) is not bytes or not 500 < len(raw_receipt) < 20000:
        raise ValueError('R266 invalid receipt bytes')
    if type(previous) is not dict or previous.get('state') != HOLD or \
       previous.get('candidate_git_blob') != CANDIDATE_BLOB or \
       previous.get('ready_for_wordpress') is not False or \
       previous.get('safe_to_carry_certified') is not False or \
       previous.get('real_browser_and_cutout_qa_completed') is not False:
        raise ValueError('R266 inherited hard hold was changed')
    try:
        r = json.loads(raw_receipt.decode('utf-8'), object_pairs_hook=_reject_duplicates,
                       parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
    except (UnicodeError, json.JSONDecodeError) as e:
        raise ValueError('R266 unreadable observation') from e
    if type(r) is not dict or r.keys() != EXPECTED.keys() or any(
        type(r[k]) is not type(v) or r[k] != v for k, v in EXPECTED.items()
    ):
        raise ValueError('R266 observed evidence/status drift')
    if not re.fullmatch('[0-9a-f]{64}', r['javascript_on_pdf_sha256']):
        raise ValueError('R266 invalid PDF digest')
    return {'schema': SCHEMA, 'state': HOLD,
        'candidate_git_blob': CANDIDATE_BLOB,
        'receipt_git_blob': git_blob(raw_receipt),
        'bounded_chromium_print_observation_recorded': True,
        'mobile_horizontal_overflow_observed': True,
        'single_browser_is_not_independent_accessibility_or_privacy_approval': True,
        'full_native_pipeline_executed': False,
        'ready_for_wordpress': False,
        **{k: False for k in NO_APPROVAL}}

def audit(root, safe_read, previous):
    return inspect(safe_read(root, CANDIDATE_PATH),
                   safe_read(root, OBSERVATION_PATH), previous)
