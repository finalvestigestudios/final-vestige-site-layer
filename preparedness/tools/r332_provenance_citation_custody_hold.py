#!/usr/bin/env python3
"""R332 E326: fail-closed source-citation proposal custody, never safety clearance.

Read-only review scaffold: preserve 17 original claim holds (R331), require a
separate eighth Article 15 provenance redline, reject recycled citations as
support for newly proposed claims. Does not edit source, source_use or HTML.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from preparedness.tools import r331_editorial_handoff_custody_gate as prior

SCHEMA = 'fv-preparedness-r332-e326-citation-custody-hard-hold-v1'
# Each prospective source is only a REVIEW TARGET, NOT VERIFIED registration.
# Source IDs deliberately differ from old source_use IDs: new claims must get
# independent source-register review, not an old citation beside new prose.
ROWS = (
 ('E326-01','call 911 for anything life-threatening','r332-911-immediate-response','https://www.911.gov/calling-911/','shelter-fcc-comms'),
 ('E326-02','keep at least one corded telephone that does not depend on electricity','r332-cpuc-telephone-power','https://www.cpuc.ca.gov/consumer-support/psps/potential-impacts-on-telephone-service-during-de-energization','shelter-fcc-comms'),
 ('E326-03',"Put an emergency contact card in each child's school bag",'r332-cdc-school-card','https://www.cdc.gov/children-and-school-preparedness/keeping-safe/','shelter-cdc-reunification'),
 ('E326-04','keeps what you type on your own device',None,None,None),
 ('E326-05','If a child is missing after a disaster','r332-ncmec-report-order','https://us.missingkids.org/gethelpnow/isyourchildmissing','shelter-ncmec-hotline'),
 ('E326-06','Red Cross takes welfare-check requests at 1-800-RED CROSS','r332-redcross-current-criteria','https://www.redcross.org/get-help/disaster-relief-and-recovery-services/contact-and-locate-loved-ones.html','shelter-fema-reunification'),
 ('E326-07','Practice the plan with everyone in the household','r332-911-test-procedure','https://www.911.gov/calling-911/frequently-asked-questions/','shelter-ready-plan'),
 ('E326-08',"We did not open the Ready.gov fillable PDF card, the Red Cross's Reconnecting Families program",'r332-provenance-disclosure',None,None),
)
REQUIRED = tuple(x[0] for x in ROWS)
FORBIDDEN_STATES = {'approved','published','verified','source_supported','qd_pass','ready','live','safe'}

def proposed_rows():
    return {rid:{'source_id':sid,'source_url':url,
                 'state':'PENDING_INDEPENDENT_CLAIM_AND_SOURCE_REVIEW',
                 'reviewed':False,'qualified_safety_approved':False,
                 'article_only':True,'modifies_original':False,
                 'citation_replaced_in_original':False,
                 'notes':'PROPOSED_CITATION_ONLY' if sid else 'NONCITATION_PRIVACY_OR_EDITORIAL_REVIEW'}
            for rid,_,sid,url,_ in ROWS}

def audit_documents(documents:dict, *, pins:dict|None=None, proposals:dict|None=None)->dict:
    """Pure audit: authentic Git blob pins required unless explicit synthetic test pins."""
    baseline=prior.audit_documents(documents,pins=pins)
    errors=list(baseline['errors'])
    proposed=proposed_rows() if proposals is None else proposals
    if type(proposed) is not dict or set(proposed)!=set(REQUIRED):
        errors.append('EIGHT_REVIEW_ROWS_REQUIRED'); proposed={}
    if len(ROWS)!=8 or len(set(REQUIRED))!=8 or any(x[0]!='E326-%02d'%i for i,x in enumerate(ROWS,1)):
        errors.append('EIGHT_ROW_DOCKET_IDENTITY_DRIFT')
    body=documents.get('a_body',b'') if type(documents) is dict else b''
    body_text=body.decode('utf-8','replace') if type(body) is bytes else ''
    meta=documents.get('a_meta',b'{}') if type(documents) is dict else b'{}'
    try: original_source_ids=set(prior.unique_json(meta).get('source_use',{}))
    except (UnicodeError,ValueError,TypeError,AttributeError): original_source_ids=set()
    review=[]
    for rid,needle,required_id,url,obsolete in ROWS:
        hits=body_text.count(needle)
        if hits!=1: errors.append('MISSING_OR_REPEATED_ORIGINAL_ANCHOR_'+rid)
        r=proposed.get(rid)
        if type(r) is not dict:
            errors.append('MISSING_OR_INVALID_PROPOSAL_'+rid); continue
        expected=proposed_rows()[rid]
        if set(r)!=set(expected): errors.append('PROPOSAL_FIELDS_CHANGED_'+rid)
        for k,v in expected.items():
            if r.get(k)!=v: errors.append('PROPOSAL_CUSTODY_DRIFT_'+rid+'_'+k.upper())
        sid=r.get('source_id')
        if isinstance(sid,str) and sid in original_source_ids:
            errors.append('OLD_CITATION_LAUNDERED_AS_NEW_CLAIM_'+rid)
        if isinstance(sid,str) and (sid==obsolete or not sid.startswith('r332-')):
            errors.append('UNREVIEWED_SOURCE_ID_REUSED_'+rid)
        if r.get('state') in FORBIDDEN_STATES or r.get('reviewed') is True or r.get('qualified_safety_approved') is True:
            errors.append('FALSE_HUMAN_APPROVAL_'+rid)
        review.append({'review_id':rid,'original_anchor_sha256':hashlib.sha256(needle.encode()).hexdigest(),
                       'original_anchor_count':hits,'candidate_source_id':required_id,
                       'source_url_review_target':url,'old_source_not_sufficient_for_new_claim':obsolete,
                       'disposition':'UNRESOLVED','source_verified':False,'may_publish':False})
    if not any(x['review_id']=='E326-08' for x in review):
        errors.append('MISSING_PROVENANCE_DISCLOSURE_REVIEW')
    if baseline.get('original_claim_witnesses')!=17 or baseline.get('unresolved_tool104_claims')!=8:
        errors.append('SEVENTEEN_OR_TOOL104_HOLDS_MISSING')
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'provenance':baseline.get('provenance'), 'errors':sorted(set(errors)),
            'original_claims_unresolved':17,'tool104_claims_unresolved':8,
            'article_e326_proposed_review_slots':len(review),
            'candidate_source_ids_are_registered':False,
            'claim_support_verified':False,'qualified_safety_approved':False,
            'independent_qd_pass':False,'may_publish':False,'merchant_conversion_verified':False,
            'review':review,'source_pins':{k:sha for k,(_,sha) in prior.SOURCES.items()}}

def native_audit(root:Path)->dict:
    docs={}
    try: docs={k:prior.safe_read(root,rel) for k,(rel,_) in prior.SOURCES.items()}
    except OSError: pass
    return audit_documents(docs)

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    a=p.parse_args()
    result=native_audit(a.root)
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2 if result['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__': raise SystemExit(main())
