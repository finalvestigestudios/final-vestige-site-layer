#!/usr/bin/env python3
"""R267 source-bound screen-only mobile card preview; publication always HARD HOLD.

R266's original candidate overflow remains an immutable negative finding. A
separate CSS-only alternative is NOT a fix to the published Tool #104 or an
accessibility, privacy, medical, independent-QD or commercial certification.
"""
from __future__ import annotations
import hashlib
import json

SCHEMA = 'fv-preparedness-r267-responsive-preview-observation-v1'
HOLD = 'DRAFT_HARD_HOLD'
ORIGINAL_PATH = 'audits/r264_minimal_wallet_card_REVIEW_ONLY.html'
PREVIEW_PATH = 'audits/r267_responsive_wallet_card_REVIEW_ONLY.html'
RECEIPT_PATH = 'audits/r267_responsive_browser_observation_REVIEW_ONLY.json'
ORIGINAL_BLOB = '40782ef142edfd348fec53eb6d8a0dc673244dea'
PREVIEW_BLOB = '5ae643302faf6bce47e8c507fbcfff9c099eaf00'
RECEIPT_BLOB = '74dc8e0f9cbb07e6cfd14a2d2dd3b4552239e40f'
SCREEN_RULE = '''/* R267: SCREEN-ONLY reviewer preview; does not change held 7-inch print geometry. */
@media screen and (max-width: 739px) {
.pa-foldcard { width:100%; max-width:100%; grid-template-columns:minmax(0, 1fr); }
.pa-face { min-height:0; border-right:0; border-bottom:1px dashed #111; padding:12px; font-size:14px; }
.pa-privacy { font-size:14px; line-height:1.4; overflow-wrap:anywhere; }
.pa-write { overflow-wrap:anywhere; }
}
'''.encode('utf-8')
NO_APPROVAL = (
 'physical_print_cut_fold_verified', 'accessibility_approved',
 'child_privacy_approved', 'source_citations_approved',
 'independent_qd_pass', 'merchant_approved', 'release_authorized',
 'public_published', 'ready_for_wordpress', 'full_native_pipeline_executed',
 'original_tool_104_browser_tested',
)
EXPECTED = {
 'schema': SCHEMA, 'state': HOLD, 'date_utc': '2026-11-10',
 'test_engine': 'Chromium', 'test_method': 'local Playwright set_content; synthetic blank fields; no network',
 'source_original_git_blob': ORIGINAL_BLOB, 'source_preview_git_blob': PREVIEW_BLOB,
 'screen_viewports_css_px': [320, 360, 390, 768, 1440],
 'original_document_scroll_width_css_px': [680, 680, 680, 768, 1440],
 'preview_document_scroll_width_css_px': [320, 360, 390, 768, 1440],
 'screen_preview_overflow_not_observed_at_tested_widths': True,
 'original_r266_mobile_overflow_remains_documented': True,
 'responsive_change_only_in_screen_css': True,
 'print_unfolded_card_width_css_px': 672,
 'print_unfolded_card_height_css_px': 206,
 'print_face_width_css_px': [335,335],
 'print_notice_font_css_px': [10.6667,10.6667],
 'print_pdf_js_on_sha256': '232495acec8411828d2c8a67ee6118b6441aafe52de050dd95a9a9f33d13193f',
 'print_pdf_js_off_sha256': '232495acec8411828d2c8a67ee6118b6441aafe52de050dd95a9a9f33d13193f',
 'same_run_old_and_new_print_pdf_bytes': True,
 'same_run_js_on_and_off_pdf_bytes': True,
 'printed_warnings_in_pdf_text_verified': True,
 'real_paper_legibility_unverified': True,
 **{key: False for key in NO_APPROVAL}
}

def git_blob(b:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def _unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj: raise ValueError('R267 duplicate JSON key '+key)
        obj[key] = value
    return obj

def inspect(original:bytes, preview:bytes, raw_receipt:bytes, r266:dict)->dict:
    if any(type(s) is not bytes or not s or len(s)>100_000 for s in (original, preview, raw_receipt)):
        raise ValueError('R267 invalid source/receipt bytes')
    if git_blob(original)!=ORIGINAL_BLOB:
        raise ValueError('R267 frozen original R264 differs from R266 observation')
    if original.count(b'@media print {')!=1 or original.count(b'<style>')!=1:
        raise ValueError('R267 CSS anchor differs')
    # Exact reversible CSS-only transform; no unreviewed edits to words,
    # warning ownership, fields, citations, routes or 7in print rules.
    expected_preview = original.replace(b'@media print {', SCREEN_RULE+b'@media print {', 1)
    if preview != expected_preview or git_blob(preview)!=PREVIEW_BLOB:
        raise ValueError('R267 candidate content or exact screen-only CSS drift')
    if (type(r266) is not dict or r266.get('state')!=HOLD or
        r266.get('candidate_git_blob')!=ORIGINAL_BLOB or
        r266.get('mobile_horizontal_overflow_observed') is not True or
        r266.get('full_native_pipeline_executed') is not False or
        r266.get('ready_for_wordpress') is not False):
        raise ValueError('R267 prior R266 negative mobile observation erased')
    try:
        rec=json.loads(raw_receipt.decode('utf-8'), object_pairs_hook=_unique_pairs,
                       parse_constant=lambda s: (_ for _ in ()).throw(ValueError('nonfinite')))
    except (UnicodeDecodeError, ValueError, TypeError) as exc:
        raise ValueError('R267 invalid strict JSON receipt') from exc
    if (type(rec) is not dict or set(rec)!=set(EXPECTED) or
        any(type(rec[k]) is not type(EXPECTED[k]) or rec[k]!=EXPECTED[k] for k in EXPECTED)):
        raise ValueError('R267 receipt schema, evidence or safety state drift')
    if git_blob(raw_receipt)!=RECEIPT_BLOB:
        raise ValueError('R267 receipt bytes changed')
    if any(v < w for v,w in zip(rec['preview_document_scroll_width_css_px'], rec['screen_viewports_css_px'])):
        raise ValueError('R267 impossible under-width document witness')
    return {
        'schema':SCHEMA, 'state':HOLD,
        'source_preview_git_blob':PREVIEW_BLOB,
        'browser_receipt_git_blob':RECEIPT_BLOB,
        'screen_overflow_not_observed_at_five_tested_widths':True,
        'original_r266_overflow_negative_finding_preserved':True,
        'screen_css_exactly_reversible':True,
        'printed_card_css_unchanged':True,
        'print_warning_font_is_only_8pt':True,
        'independent_human_release_review_still_required':True,
        **{k:False for k in NO_APPROVAL},
    }

def audit(root, safe_read, r266):
    return inspect(safe_read(root,ORIGINAL_PATH),safe_read(root,PREVIEW_PATH),
                   safe_read(root,RECEIPT_PATH),r266)
