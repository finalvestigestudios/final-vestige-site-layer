#!/usr/bin/env python3
"""R333: inspect E327 Article #15 replacement-only review without promoting advice.

Pure, read-only, fail-closed; the nine suggested E327 editorial replacements
SUPERSEDE (do not stack with) E326's eight proposed directions. Original
17 P0 claims (9 article + 8 independent Tool #104) stay unresolved.
Neither citation-token presence nor source URL presence counts as source support.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from preparedness.tools import r331_editorial_handoff_custody_gate as originals
from preparedness.tools import r332_provenance_citation_custody_hold as e326

SCHEMA = 'fv-preparedness-r333-e327-nine-slot-section-scoped-supersession-v1'
# Reviewer work orders only; none is a canonical registered, checked source.
# The 9th original witness is scoped to #phones, because the sentence
# 'The FCC page is undated' ALSO occurs in #limits (false global uniqueness).
WORK = (
 ('E327-01', 'E326-01', 'call 911 for anything life-threatening', 'r333-911-immediate-response', 'https://www.911.gov/calling-911/'),
 ('E327-02', 'E326-02', 'keep at least one corded telephone that does not depend on electricity', 'r333-cpuc-telephone-power', 'https://www.cpuc.ca.gov/consumer-support/psps/potential-impacts-on-telephone-service-during-de-energization'),
 ('E327-03', 'E326-03', "Put an emergency contact card in each child's school bag", 'r333-cdc-school-safety', 'https://www.cdc.gov/children-and-school-preparedness/keeping-safe/'),
 ('E327-04', 'E326-04', 'keeps what you type on your own device', None, None),
 ('E327-05', 'E326-05', 'If a child is missing after a disaster', 'r333-ncmec-report-order', 'https://us.missingkids.org/gethelpnow/isyourchildmissing'),
 ('E327-06', 'E326-06', 'Red Cross takes welfare-check requests at 1-800-RED CROSS', 'r333-redcross-service-eligibility', 'https://www.redcross.org/get-help/disaster-relief-and-recovery-services/contact-and-locate-loved-ones.html'),
 ('E327-07', 'E326-07', 'Practice the plan with everyone in the household', 'r333-911-rehearsal', 'https://www.911.gov/calling-911/frequently-asked-questions/'),
 ('E327-08', 'E326-08', "We did not open the Ready.gov fillable PDF card, the Red Cross's Reconnecting Families program", None, None),
 ('E327-09', None, 'The FCC page is undated', 'r333-disconnected-phone-911-limitations', 'https://www.911.gov/calling-911/frequently-asked-questions/'),
)
IDS = tuple(row[0] for row in WORK)
SAFE_KEYS = ('source_id', 'source_url', 'supersedes', 'status', 'scope', 'replacement_mode',
             'source_supported', 'source_registered', 'reviewer_approved',
             'qualified_safety_approved', 'changes_original', 'citation_accepted', 'publish_allowed')


def proposals() -> dict:
    return {rid:dict(source_id=sid,source_url=url,supersedes=prev,
          status='PENDING_INDEPENDENT_EDITORIAL_SOURCE_AND_PRIVACY_REVIEW',
          scope='ARTICLE_15_ONLY',replacement_mode='REPLACE_IN_CONTEXT_NOT_APPEND',
          source_supported=False,source_registered=False,reviewer_approved=False,
          qualified_safety_approved=False,changes_original=False,citation_accepted=False,
          publish_allowed=False) for rid,prev,_,sid,url in WORK}


def _phone_paragraph(body: str) -> tuple[str|None,list[str]]:
    """Find exactly one #phones uncertainty paragraph and no duplicate section IDs."""
    errors=[]
    # The explicit section boundary prevents the second #limits mention from
    # mistakenly matching an editor's supposed unique global phrase.
    left=list(re.finditer(r'<h2\s+id=["\']phones["\'][^>]*>',body,re.I))
    right=list(re.finditer(r'<h2\s+id=["\']school["\'][^>]*>',body,re.I))
    if len(left)!=1 or len(right)!=1 or left[0].end()>=right[0].start():
        return None,['PHONE_SECTION_BOUNDARY_MISSING_OR_REPEATED']
    section=body[left[0].end():right[0].start()]
    notes=[m.group(0) for m in re.finditer(r'<p\b[^>]*>.*?</p>',section,re.I|re.S)
           if 'The FCC page is undated' in m.group(0) and 'pa-tag--unc' in m.group(0)]
    if len(notes)!=1: errors.append('PHONE_UNCERTAINTY_PARAGRAPH_NOT_UNIQUE_IN_SECTION')
    # Do not demand global uniqueness: #limits legitimately contains same words.
    return notes[0] if len(notes)==1 else None,errors


def audit_documents(documents:dict, *, pins:dict|None=None, proposed:dict|None=None) -> dict:
    parent=e326.audit_documents(documents,pins=pins)
    errors=list(parent['errors'])
    supplied=proposals() if proposed is None else proposed
    expected=proposals()
    if type(supplied) is dict and any(str(k).startswith('E326') for k in supplied):
        errors.append('DOUBLE_APPLY_E326_E327_FORBIDDEN')
    if type(supplied) is not dict or set(supplied)!=set(IDS):
        errors.append('EXACT_NINE_E327_REPLACEMENTS_REQUIRED')
        supplied={}
    if len(WORK)!=9 or IDS!=tuple('E327-%02d'%i for i in range(1,10)):
        errors.append('E327_REVIEW_DOCKET_IDENTITY_DRIFT')
    if tuple(x[1] for x in WORK[:8])!=e326.REQUIRED:
        errors.append('E326_TO_E327_SUPERSESSION_MAP_CHANGED')
    try: body=documents['a_body'].decode('utf-8','strict')
    except (KeyError,TypeError,UnicodeError,AttributeError): body=''
    phone,phone_errors=_phone_paragraph(body)
    errors+=phone_errors
    review=[]
    for rid,predecessor,anchor,sid,url in WORK:
        if rid=='E327-09':
            hits=phone.count(anchor) if phone is not None else 0
        else:
            hits=body.count(anchor)
        if hits!=1:errors.append('ORIGINAL_REPLACEMENT_ANCHOR_MISSING_OR_REPEATED_'+rid)
        p=supplied.get(rid)
        if type(p) is not dict:
            errors.append('MISSING_OR_INVALID_E327_REVIEW_'+rid)
        else:
            if set(p)!=set(SAFE_KEYS):errors.append('E327_PROPOSAL_FIELD_SCHEMA_CHANGED_'+rid)
            for k,v in expected[rid].items():
                if p.get(k)!=v: errors.append('E327_CUSTODY_OR_FALSE_CLEARANCE_'+rid+'_'+k.upper())
        review.append(dict(review_id=rid,supersedes=predecessor,
             source_anchor_sha256=hashlib.sha256(anchor.encode('utf-8')).hexdigest(),
             source_anchor_occurrences_within_scope=hits,
             scoped_to='SECTION_H2_PHONES_PARAGRAPH' if rid=='E327-09' else 'ARTICLE_15_ORIGINAL_BODY',
             replacement_only=True,source_id_candidate=sid,source_url_review_target=url,
             original_review_holds_cleared=0,source_claim_independently_verified=False,
             tool104_modified=False,publication_permitted=False))
    if phone is not None and ('#limits' in phone or '<h2' in phone):
        errors.append('PHONE_REVIEW_NOT_PARAGRAPH_SCOPED')
    if parent['original_claims_unresolved']!=17 or parent['tool104_claims_unresolved']!=8:
        errors.append('PARENT_SEVENTEEN_OR_TOOL104_HOLDS_CHANGED')
    if parent['article_e326_proposed_review_slots']!=8:
        errors.append('REQUIRED_E326_PROVENANCE_CUSTODY_LOST')
    return dict(schema=SCHEMA,state='INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
        errors=sorted(set(errors)),provenance=parent['provenance'],
        source_pins=parent['source_pins'],original_claims_unresolved=17,
        article15_original_claims_unresolved=9,tool104_original_claims_unresolved=8,
        prior_e326_review_slots=8,active_e327_review_slots=len(review),
        phone_phrase_global_occurrences=body.count('The FCC page is undated'),
        phone_section_paragraph_sha256=(hashlib.sha256(phone.encode()).hexdigest() if phone else None),
        editorial_revision_applied=False,source_register_edited=False,
        citation_support_approved=False,qualified_emergency_and_privacy_review=False,
        independent_qd_pass=False,word_press_draft_export_verified=False,
        paid_offer_authenticated=False,may_publish=False,review=review)


def native_audit(root:Path) -> dict:
    return audit_documents({k:originals.safe_read(root,rel) for k,(rel,_) in originals.SOURCES.items()})


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    args=parser.parse_args()
    try: result=native_audit(args.root.resolve())
    except (OSError,ValueError) as e:
        print(json.dumps({'schema':SCHEMA,'state':'INVALID_HARD_HOLD','error':str(e),'may_publish':False},sort_keys=True))
        return 1
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2 if result['state']=='DRAFT_HARD_HOLD' else 1


if __name__=='__main__': raise SystemExit(main())
