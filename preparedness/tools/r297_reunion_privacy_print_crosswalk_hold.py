#!/usr/bin/env python3
"""Review-only cross-file privacy, minimum-disclosure and no-JS print crosswalk.

Inputs are pinned Git blobs from R296. No browser, network, CMS or files are written.
A match identifies a documented review problem, NOT a safety approval. Unknown
or changed evidence is INVALID_HARD_HOLD. Known evidence is DRAFT_HARD_HOLD.
The program intentionally has no release-authorizing exit-0 path.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

BODY='preparedness/content/tools/family-reunification-card.body.html'
META='preparedness/content/tools/family-reunification-card.meta.json'
JS='preparedness/tools/reunion_card.js'
R200='preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
EXPECTED={BODY:'be8698ac5d020476ff649d85813810e2000c6f98',
          META:'47da1e7e20e39f0ea85e26d54a8d58301f6e0a15',
          JS:'b1a09b1eda1ae26f081de65b400a37bc19538035',
          R200:'5822f9dfde21d1f3bdfc26658769d852c639438c'}
REVIEW_CODES=('NOJS_FORM_PRINT_CONTRADICTION','MINIMAL_EXTRA_IDENTITY_FIELDS',
              'UNVERIFIED_LOCAL_ONLY_PRIVACY','UNVERIFIED_EMERGENCY_DISPATCH_SCOPE')


def blob_oid(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def line_of(s:str, fragment:str)->int|None:
    pos=s.find(fragment)
    return None if pos<0 else s.count('\n',0,pos)+1


def _occurs(pattern:str,s:str)->bool:
    return bool(re.search(pattern,s,re.I|re.S))


def inspect_source(body:str,meta:dict,js:str)->dict:
    """Mechanical cross-file claims only, not evidence of browser/runtime behavior."""
    checks={
      'noscript_promises_form_print':_occurs(r'<noscript[^>]*>[^<]*(?:<[^>]+>[^<]*)*?the form below still works and prints',body),
      'noscript_hides_form':_occurs(r'<noscript>\s*<style>[^<]*#rc[^\{]*\{\s*display\s*:\s*none\s*;',body),
      'form_has_print_hide_class':_occurs(r'<form[^>]+class=["\'][^"\']*\bpa-card-mainhide\b',body),
      'print_rule_hides_class':_occurs(r'@media\s+print\s*\{.*?\.pa-card-mainhide\s*\{\s*display\s*:\s*none\s*!important\s*;',body),
      'minimal_promises_limited_fields':_occurs(r'Minimal version:\s*only the out-of-area contact, a phone number, the first meeting place and the review date',body),
      'minimal_js_keeps_household_name':_occurs(r'row\("Household",\s*c\.hhName\)',js),
      'minimal_js_keeps_household_phone':_occurs(r'row\("Phone",\s*c\.hhPhone\)',js),
      'minimal_js_keeps_out_contact':_occurs(r'row\("Out-of-area contact",\s*c\.outName\)',js),
      'minimal_js_keeps_out_phone':_occurs(r'row\("Out-of-area phone",\s*c\.outPhone\)',js),
      'minimal_js_keeps_meeting':_occurs(r'row\("Meet first at",\s*c\.meet1\)',js),
      'minimal_js_back_restricted':_occurs(r'var back\s*=\s*minimal\s*\?\s*keep\(',js),
      'privacy_body_absolute':_occurs(r'It is not sent or saved\. Closing the tab clears it\.',body),
      'privacy_metadata_absolute':_occurs(r'Nothing is stored',str(meta.get('description',''))),
      'emergency_note_has_citation':_occurs(r'call 911 for anything life-threatening.*?\{\{cite:shelter-ready-tech\}\}',body),
    }
    issues={
      'NOJS_FORM_PRINT_CONTRADICTION':all(checks[k] for k in ('noscript_promises_form_print','noscript_hides_form','form_has_print_hide_class','print_rule_hides_class')),
      'MINIMAL_EXTRA_IDENTITY_FIELDS':all(checks[k] for k in ('minimal_promises_limited_fields','minimal_js_keeps_household_name','minimal_js_keeps_household_phone','minimal_js_keeps_out_contact','minimal_js_keeps_out_phone','minimal_js_keeps_meeting','minimal_js_back_restricted')),
      'UNVERIFIED_LOCAL_ONLY_PRIVACY':checks['privacy_body_absolute'] and checks['privacy_metadata_absolute'],
      'UNVERIFIED_EMERGENCY_DISPATCH_SCOPE':checks['emergency_note_has_citation'],
    }
    claims=[
      {'id':'T104-NOJS-001','problem':'No-JS form promised to print, yet source hides #rc in noscript and hides form class in print',
       'body_lines':{'promise':line_of(body,'The form below still works and prints.'),'noscript_style':line_of(body,'<noscript><style>#rc, #rc-warn { display: none; }</style></noscript>'),'form':line_of(body,'<form class="pa-sheet pa-card-mainhide"'),'print_css':line_of(body,'.pa-card-mainhide { display: none !important; }')},
       'review':'no-JS/print browser QA + accessibility reviewer'},
      {'id':'T104-MIN-002','problem':'Minimal card wording limits fields; rcModel source retains household name plus two telephone fields',
       'body_lines':{'minimal_label':line_of(body,'Minimal version: only the out-of-area contact')},
       'js_lines':{'household_name':line_of(js,'row("Household", c.hhName)'),'household_phone':line_of(js,'row("Phone", c.hhPhone)')},
       'review':'child-data privacy and product editorial QA'},
      {'id':'T104-PRIV-003','problem':'Absolute storage/network/tab-close claim needs actual WordPress runtime and browser privacy verification',
       'body_lines':{'privacy_claim':line_of(body,'It is not sent or saved. Closing the tab clears it.')},
       'review':'privacy + security runtime QA'},
      {'id':'T104-911-004','problem':'Text messages to household contacts vs immediate emergency dispatch must be disambiguated and source reviewed',
       'body_lines':{'emergency_note':line_of(body,'call 911 for anything life-threatening')},
       'review':'independent emergency communications QA'},
    ]
    return {'checks':checks,'issue_witnesses':issues,'claims':claims}


def examine(files:dict[str,bytes])->dict:
    errors=[]; trusted={}
    for path,oid in EXPECTED.items():
        data=files.get(path)
        if not isinstance(data,bytes): errors.append('MISSING_WITNESS:'+path)
        elif blob_oid(data)!=oid: errors.append('CHANGED_WITNESS:'+path)
        else: trusted[path]=oid
    cross=None
    if len(trusted)==len(EXPECTED):
        try:
            meta=json.loads(files[META].decode('utf8'))
            custody=json.loads(files[R200].decode('utf8'))
            body=files[BODY].decode('utf8'); js=files[JS].decode('utf8')
            cross=inspect_source(body,meta,js)
            if (meta.get('kind'),meta.get('n'),meta.get('slug'))!=('tool',104,'family-reunification-card'):errors.append('TOOL_IDENTITY_DRIFT')
            if meta.get('status',{}).get('publish')!='draft' or meta.get('safety_review',{}).get('state')!='pending':errors.append('RELEASE_STATE_DRIFT')
            if (custody.get('state'),custody.get('artifact_count'),custody.get('export_target_count_with_six_tools'))!=('DRAFT_HARD_HOLD',35,41):errors.append('INVENTORY_DRIFT')
            if not all(cross['issue_witnesses'].values()): errors.append('KNOWN_CROSS_FILE_WITNESS_DRIFT')
        except (ValueError,UnicodeError,TypeError,AttributeError) as exc:errors.append('PARSE_FAILURE:'+type(exc).__name__)
    invalid=bool(errors)
    return {'schema':'fv-preparedness-r297-tool104-crossfile-hold-v1',
            'state':'INVALID_HARD_HOLD' if invalid else 'DRAFT_HARD_HOLD',
            'authenticated_git_blobs':trusted,'checks':cross['checks'] if cross else {},
            'issue_witnesses':cross['issue_witnesses'] if cross else {},
            'source_claim_crosswalk':cross['claims'] if cross else [],
            'errors':sorted(set(errors)), 'independent_qa_required':True,
            'source_level_only_not_browser_tested':True,
            'publication_authorized':False,'independent_qd_pass':False,
            'medical_safety_verified':False,'privacy_approved':False,
            'paid_offer_approved':False,'revenue_verified':False}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    ns=ap.parse_args(argv)
    data={}
    for path in EXPECTED:
        try:data[path]=(ns.repo_root/path).read_bytes()
        except OSError:pass
    result=examine(data)
    print(json.dumps(result,indent=2,sort_keys=True))
    return 1 if result['state']=='INVALID_HARD_HOLD' else 2

if __name__=='__main__':raise SystemExit(main())
