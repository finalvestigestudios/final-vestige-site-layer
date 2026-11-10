#!/usr/bin/env python3
"""R271: bounded full-text PDF/cutout witness; always DRAFT_HARD_HOLD.

Do not confuse PDF text geometry with physical usability, accessibility, child
privacy, independent QD review, product clearance or publication approval.
Python stdlib for pre-export custody; PyMuPDF only for optional PDF reproduction.
"""
from __future__ import annotations
import hashlib
import json
import re

STATE = 'DRAFT_HARD_HOLD'
PARENT_PATH = 'audits/r269_cutout_status_card_REVIEW_ONLY.html'
PARENT_BLOB = '4fbe028e0460dc81478825f501d76b03596faeaf'
PREVIEW_PATH = 'audits/r271_wallet_full_warning_9pt_REVIEW_ONLY.html'
PREVIEW_BLOB = 'a898d45f5cf050e941ce9f771f0d684084735570'
RECEIPT_PATH = 'audits/r271_full_warning_print_receipt_REVIEW_ONLY.json'
RECEIPT_BLOB = '5d5145a433576a42deb05e1c9518b9044154b8ca'
SCRIPT_PATH = 'tools/r271_reproduce_full_warning_REVIEW_ONLY.py'
SCRIPT_BLOB = '7d2541cdafc2de9cb71c7b49d102c75a086674a5'
SCHEMA = 'fv.r271.wallet.full-privacy-text.v1'
FALSE_FLAGS = ('physical_print_approved', 'legibility_approved',
               'child_information_privacy_approved', 'accessibility_approved',
               'independent_qd_pass', 'publication_authorized',
               'commerce_approved', 'full_native_pipeline_executed')
FACES = {
    'front': {
        'status': 'UNAPPROVED - DO NOT USE',
        'heading': 'Emergency contact',
        'privacy': ('Privacy: This card may be lost or photographed. Do not write '
                    'child names, school details, home addresses, passwords, '
                    'medical information or access codes.'),
        'fields': ['Out-of-area contact:', 'Telephone:'],
        'bounds': [42., 70., 294.2, 220.],
    },
    'back': {
        'status': 'UNAPPROVED - DO NOT USE',
        'heading': 'Backup contact',
        'privacy': ('Privacy: A finder can read this card. Carry only non-sensitive '
                    'contact details and review before sharing.'),
        'fields': ['Backup contact:', 'Backup telephone:', 'Plan reviewed:'],
        'bounds': [294.2, 70., 546.2, 220.],
    },
}


def git_blob(b):
    if type(b) is not bytes:
        raise ValueError('R271 expected exact bytes')
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def require(x, msg):
    if not x:
        raise ValueError('R271 DRAFT HARD HOLD: '+msg)


def normalized(value):
    require(type(value) is str, 'text must be string')
    return re.sub(r'\s+', ' ', re.sub(r'-\s+', '-', value)).strip()


def parse_json(raw):
    require(type(raw) is bytes and 0 < len(raw) < 100000, 'receipt bytes invalid')
    def pairs(items):
        obj = {}
        for k, v in items:
            require(k not in obj, 'duplicate JSON key '+k)
            obj[k] = v
        return obj
    try:
        doc = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                         parse_constant=lambda x: (_ for _ in ()).throw(ValueError('non-finite JSON '+x)))
    except (UnicodeError, TypeError, json.JSONDecodeError) as e:
        raise ValueError('R271 invalid receipt JSON') from e
    require(type(doc) is dict, 'receipt must be object')
    return doc


def source_only_delta(parent: bytes, preview: bytes):
    require(git_blob(parent) == PARENT_BLOB, 'frozen R269 original changed')
    require(git_blob(preview) == PREVIEW_BLOB, 'candidate identity changed')
    require(parent.count(b'font-size:8pt') == 2, 'expected two held 8pt declarations')
    require(parent.replace(b'font-size:8pt', b'font-size:9pt') == preview,
            'candidate must be CSS font-size-only 8pt->9pt, no copy/citation changes')
    return True


def _in_bounds(box, limit):
    return (type(box) is list and len(box) == 4 and
            all(type(x) in (int, float) and 0 <= x < 800 for x in box) and
            box[0] >= limit[0] - .2 and box[1] >= limit[1] - .2 and
            box[2] <= limit[2] + .2 and box[3] <= limit[3] + .2 and
            box[0] < box[2] and box[1] < box[3])


def validate(ob):
    require(type(ob) is dict and set(ob) == {'schema', 'state', 'parent_git_blob',
            'candidate_git_blob', 'proof_scope', 'chromium_version', 'page_size_pt',
            'js_modes', 'release_flags', 'physical_cut_fold_not_tested',
            'reader_legibility_not_assessed'}, 'top-level receipt contract')
    require(ob['schema'] == SCHEMA and ob['state'] == STATE, 'schema or state drift')
    require(ob['parent_git_blob'] == PARENT_BLOB and ob['candidate_git_blob'] == PREVIEW_BLOB,
            'source custody missing')
    require(ob['proof_scope'] == 'offline Chromium PDF spans; not physical or independent safety QA',
            'scope exaggerated')
    require(type(ob['chromium_version']) is str and ob['chromium_version'].startswith('144.'),
            'browser version unpinned')
    require(ob['page_size_pt'] == [612,792], 'not US Letter print')
    require(ob['physical_cut_fold_not_tested'] is True and
            ob['reader_legibility_not_assessed'] is True, 'unearned human signoff')
    require(type(ob['release_flags']) is dict and set(ob['release_flags']) == set(FALSE_FLAGS) and
            all(ob['release_flags'][k] is False for k in FALSE_FLAGS), 'approval flag drift')
    require(type(ob['js_modes']) is dict and set(ob['js_modes']) == {'false', 'true'},
            'JavaScript mode absent')
    require(ob['js_modes']['false'] == ob['js_modes']['true'], 'JavaScript print difference')
    for mode in ('false','true'):
        item = ob['js_modes'][mode]
        require(type(item) is dict and set(item) == {'page_count','faces'} and
                type(item['page_count']) is int and item['page_count'] == 1, 'PDF count/schema mismatch')
        require(type(item['faces']) is dict and set(item['faces']) == set(FACES),
                'card faces missing')
        for name, spec in FACES.items():
            row = item['faces'][name]
            require(type(row) is dict and set(row) == {'status','heading','full_privacy_text',
                    'privacy_lines','privacy_boxes_pt','privacy_fonts_pt','status_box_pt',
                    'status_font_pt','field_labels','field_boxes_pt','cutout_bounding_box_pt'},
                    'face schema mismatch: '+name)
            require(row['status'] == spec['status'] and row['heading'] == spec['heading'],
                    'status/heading altered')
            require(row['full_privacy_text'] == spec['privacy'] and
                    normalized(row['full_privacy_text']) == normalized(spec['privacy']),
                    'full wrapped warning not captured: '+name)
            require(row['field_labels'] == spec['fields'], 'contact field custody changed')
            require(row['cutout_bounding_box_pt'] == spec['bounds'], 'cutout geometry changed')
            n=row['privacy_lines']; boxes=row['privacy_boxes_pt']; fonts=row['privacy_fonts_pt']
            require(type(n) is int and 2 <= n <= 8 and type(boxes) is list and
                    type(fonts) is list and len(boxes) == len(fonts) == n,
                    'complete multi-line text evidence absent')
            require(all(_in_bounds(box, spec['bounds']) for box in boxes),
                    'privacy continuation outside face')
            require(all(type(v) in (float,int) and 8.8 <= v <= 9.2 for v in fonts),
                    'privacy text 9pt witness changed')
            require(_in_bounds(row['status_box_pt'], spec['bounds']) and
                    type(row['status_font_pt']) in (int,float) and
                    8.8 <= row['status_font_pt'] <= 9.2, 'status print evidence invalid')
            require(type(row['field_boxes_pt']) is list and
                    len(row['field_boxes_pt']) == len(spec['fields']) and
                    all(_in_bounds(box, spec['bounds']) for box in row['field_boxes_pt']),
                    'five field boxes not demonstrated')
            require(max(b[3] for b in boxes) < min(b[1] for b in row['field_boxes_pt']),
                    'privacy text overlaps or follows fields')
    return {'state':STATE, 'candidate_git_blob':PREVIEW_BLOB,
            'full_wrapped_privacy_pdf_text_bounded_observation':True,
            'print_9pt_source_witness':True, 'reader_legibility_approved':False,
            'physical_cut_fold_tested':False, 'independent_qd_pass':False,
            'publication_authorized':False, 'full_native_pipeline_executed':False}


def inspect(parent, preview, receipt, script):
    source_only_delta(parent, preview)
    require(git_blob(script) == SCRIPT_BLOB, 'reproducer changed')
    result=validate(parse_json(receipt))
    require(git_blob(receipt) == RECEIPT_BLOB, 'PDF evidence receipt changed')
    return result


def audit(root, safe_read):
    return inspect(safe_read(root,PARENT_PATH),safe_read(root,PREVIEW_PATH),
                   safe_read(root,RECEIPT_PATH),safe_read(root,SCRIPT_PATH))


def face_from_pdf_spans(spans, name):
    """Use every PDF text line in each face; never infer full copy from prefix."""
    spec=FACES[name]; limit=spec['bounds']
    parts=[s for s in spans if _in_bounds(s['box'],limit)]
    parts.sort(key=lambda s:(s['box'][1],s['box'][0]))
    statuses=[s for s in parts if s['text'] == spec['status']]
    require(len(statuses) == 1, name+' status absent/duplicated in PDF')
    heads=[s for s in parts if s['text'] == spec['heading']]
    require(len(heads) == 1, name+' heading absent/duplicated')
    priv=[s for s in parts if s['text'].startswith('Privacy:')]
    require(len(priv) == 1, name+' privacy prefix absent/duplicated')
    fields=[]
    for label in spec['fields']:
        matches=[s for s in parts if s['text'].startswith(label)]
        require(len(matches) == 1, name+' field missing or duplicate: '+label)
        fields.append(matches[0])
    after_priv=[s for s in parts if s['box'][1] >= priv[0]['box'][1]-.5 and
                s['box'][1] < fields[0]['box'][1]-.5]
    require(2 <= len(after_priv) <= 8 and after_priv[0] is priv[0],
            name+' privacy continuation not fully captured')
    full=normalized(' '.join(s['text'] for s in after_priv))
    require(full == spec['privacy'], name+' PDF warning truncated, missing, rearranged or clipped')
    require(all(8.8 <= s['font'] <= 9.2 for s in after_priv+[statuses[0]]),
            name+' PDF typography below internal 9pt target')
    require(max(s['box'][3] for s in after_priv)<min(s['box'][1] for s in fields),
            name+' footer overlapped fields')
    return {'status':spec['status'],'heading':spec['heading'],
            'full_privacy_text':full,'privacy_lines':len(after_priv),
            'privacy_boxes_pt':[s['box'] for s in after_priv],
            'privacy_fonts_pt':[s['font'] for s in after_priv],
            'status_box_pt':statuses[0]['box'],'status_font_pt':statuses[0]['font'],
            'field_labels':spec['fields'],
            'field_boxes_pt':[s['box'] for s in fields],
            'cutout_bounding_box_pt':spec['bounds']}


def examine_pdf(pdf_bytes):
    """Manual-only PyMuPDF; never invoked by unattended WordPress build."""
    import fitz
    pdf=fitz.open(stream=pdf_bytes,filetype='pdf')
    require(len(pdf)==1, 'expected one-page PDF')
    page=pdf[0]
    require(abs(page.rect.width-612)<.25 and abs(page.rect.height-792)<.25,
            'US Letter page mismatch')
    spans=[]
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for s in line['spans']:
                if s['text'].strip():
                    spans.append({'text':s['text'].strip(), 'font':round(s['size'],2),
                                  'box':[round(float(v),2) for v in s['bbox']]})
    faces={name:face_from_pdf_spans(spans,name) for name in FACES}
    require(sum(s['text']=='UNAPPROVED - DO NOT USE' for s in spans)==2,
            'review-status must appear exactly twice in PDF')
    return {'page_count':1,'faces':faces}


def create_receipt(parent, preview, off_pdf, on_pdf, version):
    source_only_delta(parent,preview)
    ob={'schema':SCHEMA,'state':STATE,'parent_git_blob':PARENT_BLOB,
        'candidate_git_blob':PREVIEW_BLOB,
        'proof_scope':'offline Chromium PDF spans; not physical or independent safety QA',
        'chromium_version':version,'page_size_pt':[612,792],
        'js_modes':{'false':examine_pdf(off_pdf),'true':examine_pdf(on_pdf)},
        'release_flags':{k:False for k in FALSE_FLAGS},
        'physical_cut_fold_not_tested':True,'reader_legibility_not_assessed':True}
    validate(ob)
    return ob
