#!/usr/bin/env python3
"""R334: resolve E328 phone-work-order *identity*, never certify emergency advice.

R333's E327-05 means missing-child report order. Editorial E328 calls its
VoIP-phone replacement 'E327-05', whereas R333's phone slot is E327-09.
Do not treat equal ordinal labels as the same source paragraph. All outputs are
read-only reviewer evidence; INVALID or DRAFT_HARD_HOLD are the only states.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from preparedness.tools import r331_editorial_handoff_custody_gate as original
from preparedness.tools import r333_e327_nine_slot_supersession_hold as parent

SCHEMA = 'fv-preparedness-r334-e328-semantic-parent-and-voip-citation-hold-v1'
EVIDENCE = (
    ('voip_registered_location','https://www.911.gov/calling-911/frequently-asked-questions/'),
    ('voip_move_update','https://www.911.gov/calling-911/frequently-asked-questions/'),
    ('power_service_not_guaranteed','https://www.cpuc.ca.gov/consumer-support/psps/potential-impacts-on-telephone-service-during-de-energization'),
    ('disconnected_wireless_cannot_locate_or_callback','https://www.911.gov/calling-911/frequently-asked-questions/'),
    ('text_to_911_local_and_call_preferred','https://www.911.gov/calling-911/frequently-asked-questions/'),
    ('scheduled_911_test_via_non_emergency_number','https://www.911.gov/calling-911/frequently-asked-questions/'),
)
# These are review targets that were read externally, NOT approved source_use IDs.
SEMANTIC = {
    'PHONE_SERVICE_AND_911_LOCATION': 'E327-09',
    'MISSING_CHILD_LAW_ENFORCEMENT_FIRST': 'E327-05',
}
SAFE = ('work_order','editorial_declared_supersedes','semantic_parent','semantic_target',
        'target_body','target_section','mode','source_targets','status',
        'changes_original','source_registered','citation_accepted','claim_supported',
        'privacy_approved','qualified_safety_approved','independent_qd_pass','may_publish')


def work_order() -> dict:
    return dict(work_order='E328-05',editorial_declared_supersedes='E327-05',
        semantic_parent='E327-09',semantic_target='PHONE_SERVICE_AND_911_LOCATION',
        target_body='ARTICLE_15_ORIGINAL',target_section='h2#phones',
        mode='REPLACE_SINGLE_EXISTING_PHONE_UNCERTAINTY_PARAGRAPH',
        source_targets=[{'claim':k,'url':v,'review_status':'UNADJUDICATED'} for k,v in EVIDENCE],
        status='ORDINAL_COLLISION_REQUIRES_HUMAN_CROSSWALK_CORRECTION',
        changes_original=False,source_registered=False,citation_accepted=False,
        claim_supported=False,privacy_approved=False,qualified_safety_approved=False,
        independent_qd_pass=False,may_publish=False)


def _source_paragraph(original_html: str) -> tuple[str|None,list[str]]:
    """Find phone source paragraph; reject any forged IDs or ambiguous markup."""
    paragraph,errors=parent._phone_paragraph(original_html)
    for section_id in ('phones','school','limits'):
        tags=re.findall(r'<h2\s+id=["\']'+section_id+r'["\'][^>]*>',original_html,re.I)
        if len(tags)!=1: errors.append('NONUNIQUE_SECTION_ID_'+section_id)
    if re.search(r'(?is)<!--.*?<h2\s+id=["\'](?:phones|school|limits)["\']',original_html):
        errors.append('POSSIBLE_COMMENTED_SECTION_SPOOF')
    if paragraph is None: return None,errors
    if original_html.count(paragraph)!=1: errors.append('PHONE_PARAGRAPH_NOT_UNIQUE_IN_BODY')
    if '<script' in paragraph.lower() or '{{link:' in paragraph:
        errors.append('PHONE_PARAGRAPH_UNEXPECTED_ACTIVE_MARKUP')
    return paragraph,errors


def _scan_candidate(fragment: str|None) -> tuple[list[str],dict]:
    """Syntactic preflight ONLY; a matching phrase is not evidence of safety."""
    if fragment is None: return [],{'candidate_submitted':False}
    if type(fragment) is not str: return ['CANDIDATE_NOT_PLAIN_TEXT'],{'candidate_submitted':True}
    errs=[]
    if not 200<=len(fragment)<=3000: errs.append('CANDIDATE_LENGTH_OR_EMPTY')
    if re.search(r'<[^>]*>|\{\{|\}\}|[\x00-\x08\x0b\x0c\x0e-\x1f]',fragment):
        errs.append('CANDIDATE_MARKUP_TOKEN_OR_CONTROL_CODE')
    if re.search(r'(?i)(?:\b(?:guaranteed|guarantees|always works|never fails|medically safe|qd pass)\b|100\s*%)',fragment):
        errs.append('CANDIDATE_UNREVIEWED_ABSOLUTE_ASSURANCE')
    if re.search(r'(?i)call\s+911\s+(?:now\s+)?(?:to\s+)?test|test\s+call\s+911\s+without',fragment):
        errs.append('UNSCHEDULED_911_TEST_CLAIM')
    checks={
        'voip':r'(?i)\bvoip\b',
        'registered_physical_address':r'(?i)registered physical address|physical address.*911',
        'change_location':r'(?i)update.*(?:address|location).*(?:move|relocat)|move.*update.*(?:address|location)',
        'service_power_dependency':r'(?i)power outage|power dependenc',
        'no_plan_location_limit':r'(?i)without (?:an )?active (?:plan|service)|without a wireless calling plan',
        'cannot_callback':r'(?i)cannot call.*back|cannot call it back',
        'text_911_locality':r'(?i)text(?:ing)?(?:\s+to|-to-)?911.*(?:local|depend|availab)',
        'scheduled_non_emergency_test':r'(?i)(?:test|schedul).*non.emergency|non.emergency.*(?:test|schedul)',
        'california_only':r'(?i)california.*(?:example|not a nationwide|not a national|specific)',
    }
    observed={key:bool(re.search(pattern,fragment)) for key,pattern in checks.items()}
    for key,value in observed.items():
        if not value: errs.append('CANDIDATE_SOURCE_SCOPE_NEEDS_REVIEW_'+key.upper())
    return errs,{'candidate_submitted':True,'lexical_only_not_source_support':observed,
                 'candidate_sha256':hashlib.sha256(fragment.encode('utf-8')).hexdigest()}


def audit_documents(documents:dict, *, pins:dict|None=None, proposed:dict|None=None,
                    candidate:str|None=None) -> dict:
    first=parent.audit_documents(documents,pins=pins)
    errors=list(first['errors'])
    row=work_order() if proposed is None else proposed
    want=work_order()
    if type(row) is not dict or set(row)!=set(SAFE):
        errors.append('E328_EXACT_REVIEW_SCHEMA_REQUIRED');row={}
    for field in SAFE:
        if row.get(field)!=want[field]: errors.append('E328_UNAUTHORIZED_CROSSWALK_OR_APPROVAL_'+field.upper())
    if parent.WORK[4][0]!='E327-05' or parent.WORK[4][3]!='r333-ncmec-report-order':
        errors.append('PARENT_MISSING_CHILD_SEMANTIC_ID_CHANGED')
    if parent.WORK[8][0]!='E327-09' or parent.WORK[8][3]!='r333-disconnected-phone-911-limitations':
        errors.append('PARENT_PHONE_SEMANTIC_ID_CHANGED')
    # A dangerous mismatch is an open review *finding*, not permission to
    # silently repair the editorial team's identifier or rewrite Tool #104.
    collision = want['editorial_declared_supersedes']!=SEMANTIC['PHONE_SERVICE_AND_911_LOCATION']
    if not collision: errors.append('EDITORIAL_COLLISION_WITNESS_DISAPPEARED')
    try: html=documents['a_body'].decode('utf-8','strict')
    except (TypeError,KeyError,AttributeError,UnicodeError): html=''
    old,source_errors=_source_paragraph(html)
    errors+=source_errors
    if html.count('The FCC page is undated')!=2:
        errors.append('TWO_DISTINCT_FCC_CUSTODY_ANCHORS_REQUIRED')
    if old is not None and 'The FCC page is undated' not in old:
        errors.append('PHONE_CLAIM_SOURCE_ANCHOR_LOST')
    cand_errors,cand_report=_scan_candidate(candidate)
    errors+=cand_errors
    # No original byte is written; a prospective rewrite may be measured only
    # in memory. The #limits original disclosure is never selected by this gate.
    provisional=None
    if old is not None and candidate is not None and type(candidate) is str and not cand_errors:
        new_html=html.replace(old,'<p>'+candidate+'</p>',1)
        if new_html.count('The FCC page is undated')!=1:
            errors.append('REVIEW_PREVIEW_CHANGED_PROVENANCE_ANCHOR_COUNT')
        if new_html.count('{{cite:')!=html.count('{{cite:'):
            errors.append('REVIEW_PREVIEW_TOUCHED_ORIGINAL_CITATIONS')
        provisional={'preview_sha256':hashlib.sha256(new_html.encode()).hexdigest(),
                     'original_sha256':hashlib.sha256(html.encode()).hexdigest(),
                     'no_original_source_written':True,'not_wordpress_ready_for_release':True}
    if first.get('original_claims_unresolved')!=17 or first.get('tool104_original_claims_unresolved')!=8:
        errors.append('PARENT_RELEASE_HOLDS_DROPPED')
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)),'provenance':first.get('provenance'),
            'editorial_work_order':'E328-05',
            'editorial_declared_parent':'E327-05',
            'semantic_phone_parent':'E327-09',
            'semantic_missing_child_parent':'E327-05',
            'ordinal_collision_found':collision,
            'collision_resolution':'HUMAN_CORRECTED_MAPPING_REQUIRED_BEFORE_ANY_APPLICATION',
            'source_paragraph_sha256':hashlib.sha256(old.encode()).hexdigest() if old else None,
            'source_register_urls_are_unadjudicated':True,
            'article15_original_claims_unresolved':9,'tool104_original_claims_unresolved':8,
            'cross_cluster_conflicts_unresolved':15,
            'active_e327_review_slots':9,'e328_proposed_phone_supersession_slots':1,
            'candidate_checks':cand_report,'in_memory_preview':provisional,
            'citation_claim_support_approved':False,'editorial_change_applied':False,
            'native_50_pair_exports_verified':False,'independent_qd_pass':False,
            'qualified_safety_and_child_privacy_approved':False,
            'merchant_preparedness_offer_verified':False,'may_merge':False,'may_publish':False}


def native_audit(root:Path) -> dict:
    return audit_documents({k:original.safe_read(root,rel) for k,(rel,_) in original.SOURCES.items()})


def main() -> int:
    arg=argparse.ArgumentParser()
    arg.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    a=arg.parse_args()
    try:result=native_audit(a.root.resolve())
    except (OSError,ValueError,TypeError,UnicodeError):
        result={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
                'errors':['AUTHENTIC_FOUR_PINNED_ORIGINAL_DOCUMENTS_REQUIRED'],'may_publish':False}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2 if result['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
