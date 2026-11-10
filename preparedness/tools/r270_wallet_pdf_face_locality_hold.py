#!/usr/bin/env python3
"""R270: source-bound PDF-face *negative* safety custody, never publication approval.

The manually generated Chromium/PyMuPDF receipt documents PDF placement, not
physical cut/fold legibility or privacy. This offline pure-Python validator
refuses invented QA PASS and preserves the observed sub-9pt typography risk.
"""
from __future__ import annotations
import hashlib
import json

HOLD = 'DRAFT_HARD_HOLD'
HTML_PATH = 'audits/r269_cutout_status_card_REVIEW_ONLY.html'
HTML_BLOB = '4fbe028e0460dc81478825f501d76b03596faeaf'
RECEIPT_PATH = 'audits/r270_print_locality_receipt_REVIEW_ONLY.json'
RECEIPT_BLOB = 'df6a8732265a24fbc54442c87e24015f76ef5282'
SCRIPT_PATH = 'tools/r270_reproduce_wallet_print_locality_REVIEW_ONLY.py'
SCRIPT_BLOB = '02efdcb44f7dab1ccd4bbd5dae506952dc7ee9c4'
FRONT_FIELDS = ['Out-of-area contact:', 'Telephone:']
BACK_FIELDS = ['Backup contact:', 'Backup telephone:', 'Plan reviewed:']
FALSE_FLAGS = ('physical_print_approved', 'legibility_approved', 'child_privacy_approved',
               'independent_qd_pass', 'publication_authorized', 'commerce_approved',
               'full_native_pipeline_executed')


def git_blob(b: bytes) -> str:
    if type(b) is not bytes:
        raise ValueError('R270 requires bytes')
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\\0' + b).hexdigest()


def require(value, message):
    if not value:
        raise ValueError('R270 HARD HOLD: ' + message)


def no_duplicate_keys(pairs):
    d={}
    for k,v in pairs:
        require(k not in d, 'duplicate receipt JSON key: ' + k)
        d[k]=v
    return d


def load_receipt(raw):
    require(type(raw) is bytes and len(raw) <= 100_000, 'invalid receipt bytes')
    try:
        obj=json.loads(raw.decode('utf-8'),object_pairs_hook=no_duplicate_keys,
                       parse_constant=lambda x: (_ for _ in ()).throw(ValueError('NaN forbidden')))
    except (UnicodeError, TypeError, json.JSONDecodeError) as error:
        raise ValueError('R270 invalid JSON') from error
    require(type(obj) is dict, 'receipt not object')
    return obj


def validate(ob):
    require(type(ob) is dict, 'receipt object required')
    require(ob.get('schema') == 'fv.r270.wallet.pdf-face-locality.v1', 'schema drift')
    require(ob.get('state') == HOLD, 'release state drift')
    require(ob.get('source_git_blob') == HTML_BLOB, 'R269 exact HTML custody drift')
    require(ob.get('pdf_page_size_pt') == [612,792], 'US Letter PDF expected')
    require(ob.get('proof_scope') == 'bounded offline Chromium+PDF spans, not physical usability',
            'bounded proof qualification missing')
    cv=ob.get('chromium_version')
    require(type(cv) is str and cv.startswith('144.'), 'browser-version receipt mismatch')
    for key in FALSE_FLAGS:
        require(ob.get(key) is False, 'unsafe approval flag: '+key)
    require(ob.get('printed_warning_below_internal_9pt_review_floor') is True,
            'sub-9pt warning exposure not preserved')
    require(ob.get('physical_paper_cut_fold_not_tested') is True,
            'physical cut/fold completion falsely asserted')
    modes=ob.get('javascript_modes')
    require(type(modes) is dict and set(modes)=={'false','true'}, 'JS-off/on comparison absent')
    require(modes['false']==modes['true'], 'source-to-printed-face parity drift')
    for mode in ('false','true'):
        row=modes[mode]
        require(type(row) is dict and row.get('page_count') == 1 and
                row.get('pdf_text_label_count') == 2, 'PDF page or badge-count change')
        require(set(row)=={'page_count','pdf_text_label_count','front','back'},
                'unexpected print evidence fields')
        for face, labels in (('front',FRONT_FIELDS),('back',BACK_FIELDS)):
            f=row.get(face)
            require(type(f) is dict, 'face is not object')
            require(set(f)=={'status_count','privacy_count','min_warning_font_pt',
                             'max_warning_font_pt','verified_field_labels',
                             'text_inside_expected_cutout_bounds'}, 'face evidence schema drift')
            require(f['status_count'] == 1 and f['privacy_count'] == 1,
                    'status/privacy not once per cutout')
            require(f['text_inside_expected_cutout_bounds'] is True,
                    'printed text locality not demonstrated')
            require(f['verified_field_labels'] == labels, 'field/custody drift')
            lo=f['min_warning_font_pt'];hi=f['max_warning_font_pt']
            require(type(lo) in (float,int) and type(hi) in (float,int) and
                    7.7 <= lo <= hi <= 8.3, '8pt warning typography witness changed')
    return {'state':HOLD, 'source_git_blob':HTML_BLOB,
            'receipt_git_blob':RECEIPT_BLOB,'reproducer_git_blob':SCRIPT_BLOB,
            'printed_notice_8pt_risk_requires_human_review':True,
            'cutout_pdf_face_locality_bounded_observation':True,
            'source_changes_or_real_print_not_certified':True,
            'full_native_pipeline_executed':False,
            **{key: False for key in FALSE_FLAGS}}


def inspect(html:bytes,receipt:bytes,script:bytes):
    require(git_blob(html) == HTML_BLOB, 'authentic candidate source changed')
    require(git_blob(script) == SCRIPT_BLOB, 'manual offline PDF reproducer changed')
    ob=load_receipt(receipt)
    result=validate(ob)
    require(git_blob(receipt) == RECEIPT_BLOB, 'original browser evidence receipt changed')
    return result


def audit(root,safe_read):
    return inspect(safe_read(root,HTML_PATH),safe_read(root,RECEIPT_PATH),
                   safe_read(root,SCRIPT_PATH))
