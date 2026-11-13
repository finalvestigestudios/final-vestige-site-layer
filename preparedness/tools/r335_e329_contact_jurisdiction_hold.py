#!/usr/bin/env python3
"""R335: source-pinned out-of-area contact / emergency-jurisdiction review gate.

No original, WordPress, marketing, or source registry writes. Editorial E329 is
review-only. Textual predicates are *not* qualified evidence or safety approval.
Identity is source path+Git blob+semantic section, never an E327 ordinal alone.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from preparedness.tools import r331_editorial_handoff_custody_gate as source
from preparedness.tools import r334_e328_semantic_supersession_hold as parent

SCHEMA='fv-preparedness-r335-e329-jurisdiction-semantic-source-gate-v1'
CLAIMS=(
    ('out_of_area_contact_is_family_status_relay','https://www.911.gov/calling-911/'),
    ('remote_emergency_calls_not_generally_transferable','https://www.911.gov/calling-911/frequently-asked-questions/'),
    ('obtain_remote_jurisdiction_ten_digit_number_from_official_agency','https://www.911.gov/calling-911/frequently-asked-questions/'),
    ('local_scene_person_uses_local_emergency_services','https://www.911.gov/calling-911/'),
    ('individualized_support_and_communications','https://www.cdc.gov/disability-emergency-preparedness/people-with-disabilities/make-a-plan.html'),
)
SEMANTIC={
 'e329_new':'article15.contact.out_of_area_jurisdiction_limits',
 'phone':'article15.phones.uncertainty_paragraph',
 'missing_child':'article15.school.missing_child_reporting',
 'limits':'article15.limits.provenance_disclosure',
}
REQUIRED_FIELDS=('work_order','new_semantic_key','original_body_git_blob','insert_after_section',
                 'insert_before_section','phone_semantic_key','missing_child_semantic_key',
                 'limits_semantic_key','external_editorial_ordinal_conflict',
                 'engineering_ordinal_conflict','claim_targets','human_adjudication',
                 'changes_original','source_registry_approved','emergency_safety_approved',
                 'privacy_approved','independent_qd_pass','eligible_for_commercial_cta',
                 'may_merge','may_publish')


def review_order():
    """Machine-verifiable immutable review identity, not a source acceptance."""
    return {
        'work_order':'E329-CONTACT-JURISDICTION',
        'new_semantic_key':SEMANTIC['e329_new'],
        'original_body_git_blob':source.SOURCES['a_body'][1],
        'insert_after_section':'h2#contact',
        'insert_before_section':'h2#card',
        'phone_semantic_key':SEMANTIC['phone'],
        'missing_child_semantic_key':SEMANTIC['missing_child'],
        'limits_semantic_key':SEMANTIC['limits'],
        'external_editorial_ordinal_conflict':'E327-05_PHONE_IN_HANDOFF_VS_MISSING_CHILD_IN_R333',
        'engineering_ordinal_conflict':'R333_PHONE_E327-09_VS_E328_PHONE_LABEL_E327-05',
        'claim_targets':[{'claim':c,'url':u,'status':'UNADJUDICATED'} for c,u in CLAIMS],
        'human_adjudication':'REQUIRED_BEFORE_ANY_APPLICATION',
        'changes_original':False,'source_registry_approved':False,
        'emergency_safety_approved':False,'privacy_approved':False,
        'independent_qd_pass':False,'eligible_for_commercial_cta':False,
        'may_merge':False,'may_publish':False,
    }


def section_bounds(html):
    """Require unique genuine contiguous h2 boundaries; reject spoofing."""
    errors=[]
    tags=list(re.finditer(r'<h2\b([^>]*)>(.*?)</h2>',html,re.I|re.S))
    wanted=('contact','card','phones','school','limits')
    keys=[]
    for match in tags:
        idm=re.search(r'\bid\s*=\s*(["\'])([^"\']+)\1',match.group(1),re.I)
        keys.append((idm.group(2) if idm else None,match.start(),match.end()))
    for key in wanted:
        if sum(x[0]==key for x in keys)!=1:errors.append('REQUIRED_H2_NOT_UNIQUE_'+key.upper())
    if re.search(r'(?is)<!--[^>]*<h2\b|<!--(?:(?!-->).)*<h2\b',html):
        errors.append('POSSIBLE_COMMENTED_H2_SPOOF')
    if re.search(r'(?is)<script\b[^>]*>.*?<h2\b',html):
        errors.append('POSSIBLE_SCRIPT_EMBEDDED_H2_SPOOF')
    found={i:(start,end) for i,start,end in keys if i in wanted}
    if any(k not in found for k in wanted):return None,errors
    order=['contact','card','phones','school','limits']
    if not all(found[a][0]<found[b][0] for a,b in zip(order,order[1:])):
        errors.append('SECTION_ORDER_CHANGED')
    if len(keys)<=0 or not any(k[0]=='contact' for k in keys):
        errors.append('MISSING_CONTACT_SECTION')
    contact=html[found['contact'][1]:found['card'][0]]
    for witness in ("The FCC's guide recommends",'out of the area','{{cite:shelter-fcc-comms}}',
                    '{{cite:shelter-cdc-reunification}}'):
        if witness not in contact: errors.append('ORIGINAL_CONTACT_WITNESS_LOST_'+witness[:25])
    if html.count('<h2 id="contact">')!=1 or html.count('<h2 id="card">')!=1:
        errors.append('ORIGINAL_CONTACT_TAG_BYTES_CHANGED')
    return {'contact':contact,'insert_at':found['card'][0],
            'contact_sha256':hashlib.sha256(contact.encode('utf-8')).hexdigest(),
            'limits_sha256':hashlib.sha256(html[found['limits'][1]:].encode('utf-8')).hexdigest(),
            'boundary_before':html[max(0,found['card'][0]-30):found['card'][0]],
            'h2_count':len(tags)},errors


def lexical_preview_check(candidate):
    """Purely conservative draft preflight; false negative possible, not advice approval."""
    if candidate is None:return [],{'candidate_submitted':False}
    if type(candidate) is not str:return ['CANDIDATE_MUST_BE_PLAIN_TEXT'],{'candidate_submitted':True}
    errors=[]
    if not (180<=len(candidate)<=2200):errors.append('CANDIDATE_LENGTH_OUTSIDE_REVIEW_BOUNDS')
    if re.search(r'<[^>]*>|\{\{|\}\}|[\x00-\x08\x0b\x0c\x0e-\x1f]',candidate):
        errors.append('CANDIDATE_FORBIDDEN_MARKUP_CITATION_OR_CONTROL')
    if re.search(r'(?i)\b(?:pay now|checkout|purchase|exclusive offer|buy today|affiliate|collect.*phone number)\b',candidate):
        errors.append('CANDIDATE_COMMERCIAL_OR_PII_SCOPE_BREACH')
    if re.search(r'(?i)\b(?:guaranteed|guarantees|always|never|universal|medically safe|qd pass)\b|100\s*%',candidate):
        errors.append('CANDIDATE_UNREVIEWED_ABSOLUTE')
    if re.search(r'(?i)(?:dial|call|text)\s*911\s*(?:(?:for|to)\s+)?(?:an?\s+)?(?:test|practice)|transfer\s+911\s+to\s+any',candidate):
        errors.append('CANDIDATE_UNSCHEDULED_TEST_OR_UNIVERSAL_TRANSFER')
    checks={
        'family_status_not_dispatch':r'(?i)(?:out.of.area|outside.*area).*(?:family|status)|(?:family|status).*(?:out.of.area|outside.*area)',
        'emergency_scene_locality':r'(?i)(?:scene|emergency location).*(?:local|serving)|(?:local|serving).*(?:scene|emergency location)',
        'remote_jurisdiction_nontransfer':r'(?i)(?:911|emergency).*transferr?|transferr?.*(?:911|emergency)',
        'official_agency_contact_number':r'(?i)(?:10.digit|ten.digit).*(?:agency|website)|(?:agency|website).*(?:10.digit|ten.digit)',
        'role_distinction':r'(?i)(?:not emergency dispatch|not a dispatcher|not a substitute for.*emergency)',
        'local_rules_vary':r'(?i)(?:local.*var|jurisdiction.*var)',
    }
    observed={k:bool(re.search(p,candidate)) for k,p in checks.items()}
    for k,ok in observed.items():
        if not ok:errors.append('CANDIDATE_SOURCE_SCOPE_REQUIRES_HUMAN_REVIEW_'+k.upper())
    return errors,{'candidate_submitted':True,'candidate_sha256':hashlib.sha256(candidate.encode()).hexdigest(),
                   'lexical_witnesses_only_not_source_support':observed}


def audit_documents(documents,*,pins=None,work_order=None,candidate=None):
    base=parent.audit_documents(documents,pins=pins)
    errors=list(base['errors'])
    expected=review_order()
    row=review_order() if work_order is None else work_order
    if type(row) is not dict or set(row)!=set(REQUIRED_FIELDS):
        errors.append('REVIEW_ORDER_EXACT_SCHEMA_REQUIRED');row={}
    for key in REQUIRED_FIELDS:
        if row.get(key)!=expected[key]:errors.append('UNAUTHORIZED_SEMANTIC_MAPPING_SOURCE_OR_APPROVAL_'+key.upper())
    if parent.SEMANTIC['PHONE_SERVICE_AND_911_LOCATION']!='E327-09':
        errors.append('PARENT_PHONE_SEMANTIC_ID_CHANGED')
    if parent.SEMANTIC['MISSING_CHILD_LAW_ENFORCEMENT_FIRST']!='E327-05':
        errors.append('PARENT_MISSING_CHILD_SEMANTIC_ID_CHANGED')
    try:html=documents['a_body'].decode('utf-8','strict')
    except (KeyError,TypeError,AttributeError,UnicodeError):html=''
    bounds,scope_errors=section_bounds(html)
    errors+=scope_errors
    candidate_errors,candidate_report=lexical_preview_check(candidate)
    errors+=candidate_errors
    preview=None
    if bounds and candidate is not None and type(candidate) is str and not candidate_errors:
        before=html
        insert='<h3 data-fv-review-only="e329">Out-of-area contact and local emergency response — REVIEW ONLY</h3>\n<p>'+candidate+'</p>\n'
        hypothetical=before[:bounds['insert_at']]+insert+before[bounds['insert_at']:]
        for key in ('{{cite:', '<h2 id="phones">','<h2 id="school">','<h2 id="limits">'):
            if before.count(key)!=hypothetical.count(key):errors.append('PREVIEW_CHANGED_ORIGINAL_SOURCE_TOKEN_'+key)
        if not hypothetical.replace(insert,'',1)==before:errors.append('PREVIEW_NOT_INSERTION_ONLY')
        preview={'provisional_sha256':hashlib.sha256(hypothetical.encode()).hexdigest(),
                 'original_sha256':hashlib.sha256(before.encode()).hexdigest(),
                 'unapproved_preview_only':True,'no_original_written':True}
    if base.get('article15_original_claims_unresolved')!=9 or base.get('tool104_original_claims_unresolved')!=8:
        errors.append('PARENT_ORIGINAL_CLAIM_HOLDS_DROPPED')
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)),'source_provenance':base.get('provenance'),
            'source_body_git_blob':source.SOURCES['a_body'][1],
            'review_semantic_map':SEMANTIC,'e327_ordinal_collision_unresolved':True,
            'original_contact_sha256':bounds['contact_sha256'] if bounds else None,
            'original_limits_sha256':bounds['limits_sha256'] if bounds else None,
            'draft_source_urls_unadjudicated':True,'claim_targets':list(CLAIMS),
            'candidate_review':candidate_report,'in_memory_preview':preview,
            'article15_original_claims_unresolved':9,'tool104_original_claims_unresolved':8,
            'legacy_contributor_conflicts_unresolved':15,
            'all_35_articles_and_6_tools_source_depth_verified':False,
            'authentic_50_wordpress_50_preview_exports_verified':False,
            'qualified_source_support_approved':False,'independent_qd_pass':False,
            'emergency_and_child_privacy_safety_approved':False,
            'verified_purchasable_fv_preparedness_product':False,
            'changes_original':False,'may_merge':False,'may_publish':False}


def native_audit(root:Path):
    docs={key:source.safe_read(root,rel) for key,(rel,_) in source.SOURCES.items()}
    return audit_documents(docs)


def main():
    ap=argparse.ArgumentParser(description='Read-only E329 claim and jurisdiction hold')
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    args=ap.parse_args()
    try:report=native_audit(args.root.resolve())
    except (OSError,TypeError,ValueError,UnicodeError):
        report={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
                'errors':['AUTHENTIC_FOUR_ORIGINAL_GIT_OBJECTS_REQUIRED'],
                'independent_qd_pass':False,'may_publish':False}
    print(json.dumps(report,indent=2,sort_keys=True))
    return 2 if report['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
