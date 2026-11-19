#!/usr/bin/env python3
"""R475 read-only CDC child-card source-scope/provenance hold (Issue #136).

Never changes original drafts, source registers, card fields, consent, URLs or safety
states. E466's catalog-only historical record and E467's later one-page PDF
visual inspection are separate *dated* evidence, not interchangeable citations.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

STATUS = "DRAFT_HARD_HOLD"
SCHEMA = "fv-preparedness-r475-cdc-child-card-claim-custody-v1"
FROZEN = {
 "r474_integration_head":"7d0a7ad4e00465041b82667a9560bc8e6aa04b56",
 "r474_historical_catalog_scope_manifest_blob":"3b90c422aa85fdcbd26b7d4f09a123c3dbf26ffc",
 "editorial_e466_memo_blob":"c83330dbc53625be81e30c681aa6df35308ab52e",
 "editorial_e467_commit":"28e10b233eb110b03603b6c8f3e4a8868d41d5f0",
 "editorial_e467_memo_blob":"68de3215599eddf04b1f63a75558da203a5969c7",
 "original_article_html_blob":"8ac8bd7dba3be15d477c15737e54d83364d72527",
 "original_article_meta_blob":"dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3",
 "original_tool_html_blob":"be8698ac5d020476ff649d85813810e2000c6f98",
 "original_tool_meta_blob":"47da1e7e20e39f0ea85e26d54a8d58301f6e0a15",
}
IDS=("cdc-2020-backpack-pdf-e467-review-only", "cdc-2025-keeping-children-safe-e467-review-only", "cdc-2025-before-during-after-e467-review-only")
URLS=("https://stacks.cdc.gov/view/cdc/139829/cdc_139829_DS1.pdf", "https://www.cdc.gov/children-and-school-preparedness/keeping-safe/index.html", "https://www.cdc.gov/children-and-school-preparedness/before-during-after/index.html")
DATES=("2020-07-14","2025-12-16","2025-12-24")
SCOPES=("one_pdf_page_visually_inspected_2026-11-18","full_official_web_page","full_official_web_page")
ORIGINS=("E467_EDITORIAL_PDF_VISUAL_REVIEW", "E467_EDITORIAL_WEB_REVIEW", "E467_EDITORIAL_WEB_REVIEW")
RIGHTS=("US_GOV_PUBLIC_DOMAIN_PER_CATALOG", "OFFICIAL_WEB_GUIDANCE_NOT_TEMPLATE_LICENSE", "OFFICIAL_WEB_GUIDANCE")
CHILD=("child_name", "child_dob", "home_address", "school_contact", "medical_allergies", "emergency_contacts", "pickup_address")
GUARDIAN=CHILD+("healthcare_specialist",)
WEB=("child_name", "child_dob", "medical_allergies", "school_caregiver_contacts", "parent_guardian_contacts", "emergency_contacts")
CLAIMS={
 "cdc_guardian_wallet_is_child_specific":True,
 "cdc_guardian_wallet_is_fv_minimal_adult_card":False,
 "fv_minimal_adult_note_is_optional_editorial_only":True,
 "fv_minimal_tool_is_approved_cdc_template":False,
 "cdc_2020_pdf_and_2025_web_fields_are_interchangeable":False,
 "cdc_2025_page_prohibits_home_address":False,
 "cdc_2025_page_mandates_home_address":False,
 "emergency_card_grants_school_pickup_permission":False,
 "parent_written_card_proves_ferpa_compliance":False,
 "original_cdc_citation_updated_without_registration":False,
 "full_original_35_article_native_build_passed":False,
 "word_press_or_live_child_data_security_verified":False,
 "no_child_pii_collected_by_this_gate":True,
 "no_advice_approved_as_medically_safe":True,
}
DECISIONS=("form_purpose_and_custodian", "necessary_child_medical_identifiers", "school_childcare_local_pickup_policy", "new_source_registration_and_citation_scope", "production_js_data_privacy_and_print", "native_build_wordpress_preview_parity", "accessible_mobile_print_and_200_percent_zoom", "qualified_release_approval")
OWNERS=("Preparedness/QD",)*4+("Claude/Engineering",)*2+("Preparedness/QD", "Founder/Commerce")
ORIGINALS={
 "content/articles/family-communication-plan.body.html":"original_article_html_blob",
 "content/articles/family-communication-plan.meta.json":"original_article_meta_blob",
 "content/tools/family-reunification-card.body.html":"original_tool_html_blob",
 "content/tools/family-reunification-card.meta.json":"original_tool_meta_blob",
}

class Hold(ValueError):pass

def require(condition, reason):
    if not condition:raise Hold(reason)

def git_blob(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def strict_json(data:bytes)->dict:
    def no_dupes(pairs):
        d={}
        for k,v in pairs:
            require(k not in d,"duplicate JSON key: "+k)
            d[k]=v
        return d
    v=json.loads(data.decode("utf-8"),object_pairs_hook=no_dupes,parse_constant=lambda s:(_ for _ in ()).throw(Hold("invalid JSON constant: "+s)))
    require(type(v) is dict,"JSON object required")
    return v

def read_pinned(root:Path, relative:str, blob:str)->bytes:
    root=root.resolve(); path=root/relative
    require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root),"missing/untrusted native file: "+relative)
    raw=path.read_bytes();require(git_blob(raw)==blob,"Git blob drift: "+relative)
    return raw

def check_crosswalk(m:dict)->dict:
    require(type(m) is dict and m.get("schema")==SCHEMA,"schema drift")
    for k,v in (("status",STATUS),("may_publish",False),("qualified_qd_pass",False),("qualified_school_privacy_review",False),("native_35_article_build_pass",False),("wordpress_private_export_parity_pass",False),("article_15_status","draft_safety_pending"),("tool_104_status","draft_safety_pending"),("tool_102_distinct",True),("review_only_last_checked","2026-11-18"),("review_by","2026-12-18")):
        require(type(m.get(k)) is type(v) and m[k]==v, "unearned clearance / changed review status: "+k)
    require(m.get("evidence")==FROZEN,"historical or original evidence SHA drift")
    src=m.get("sources")
    require(type(src) is list and len(src)==3 and all(type(s) is dict for s in src),"source inventory wrong")
    for n,s in enumerate(src):
        for k,v in (("id",IDS[n]),("url",URLS[n]),("published",DATES[n]),("scope",SCOPES[n]),("origin",ORIGINS[n]),("rights",RIGHTS[n]),("citation_registered",False)):
            require(type(s.get(k)) is type(v) and s[k]==v,f"source {n} altered {k}")
    require(src[0].get("2020_child_backpack_fields")==list(CHILD),"2020 backpack source field loss/addition")
    require(src[0].get("2020_guardian_wallet_fields")==list(GUARDIAN),"CDC guardian card is child-specific and includes specialist field")
    require(src[0].get("old_e466_catalog_only_is_historical") is True,"E466 historical catalog scope suppressed")
    require(src[1].get("2025_page_explicit_fields")==list(WEB),"2025 web claim inflation/loss")
    for k in ("2025_page_explicitly_lists_home_address","2025_address_is_prohibited","2025_address_is_required"):
        require(src[1].get(k) is False,"2025 address inference invented")
    for k,v in (("card_grants_school_pickup_authority",False),("school_emergency_contacts_must_stay_current",True),("follow_authorized_pickup_instructions",True)):
        require(src[2].get(k) is v,"school pickup rule laundered")
    claims=m.get("claim_boundaries")
    require(type(claims) is dict and claims==CLAIMS,"unsupported child privacy/CDC authority claim")
    decisions=m.get("human_decisions")
    require(type(decisions) is list and len(decisions)==len(DECISIONS),"human docket changed")
    for i,d in enumerate(decisions):
        require(type(d) is dict and d.get("id")==DECISIONS[i] and d.get("owner")==OWNERS[i] and d.get("status")=="UNADJUDICATED" and d.get("reviewer") is None and d.get("signed_receipt") is None,"invented qualified reviewer clearance")
    com=m.get("commercial_funnel")
    require(type(com) is dict and set(com)=={"verified_purchasable_preparedness_sku","published_grok_asset_id_matched","paid_checkout_verified","settled_customer_order_verified","attributable_net_revenue_1000_qualified_sessions"},"commercial contract drift")
    for k,v in com.items():require(v is (None if k=="attributable_net_revenue_1000_qualified_sessions" else False),"invented sale/asset/attribution")
    require(set(m)=={"schema","status","may_publish","qualified_qd_pass","qualified_school_privacy_review","native_35_article_build_pass","wordpress_private_export_parity_pass","article_15_status","tool_104_status","tool_102_distinct","evidence","sources","claim_boundaries","human_decisions","commercial_funnel","review_only_last_checked","review_by"},"unknown crosswalk assertions")
    return {"state":"E467_CDC_SOURCE_SCOPE_AND_CHILD_PRIVACY_HARD_HOLD", "source_records_review_only":3,"original_blobs_expected":4,"unadjudicated_decisions":8,"child_identity_values_collected":0,"qualified_qd_pass":False,"may_publish":False,"paid_offer_verified":False,"net_revenue_per_1000_sessions":None}

def check_native(root:Path,m:dict,editorial_pdf_review:Path|None=None)->dict:
    # This is *not* a hosted 35-article build. Native check is read-only and
    # cannot grant qualified approval even when all exact original inputs exist.
    result=check_crosswalk(m)
    for p,k in ORIGINALS.items():
        raw=read_pinned(root,p,FROZEN[k])
        if p.endswith(".meta.json"):
            meta=strict_json(raw)
            require(meta.get("status",{}).get("publish")=="draft" and meta.get("safety_review",{}).get("state")=="pending","original safety state altered")
    # An E467 memo is an independent editorial-branch witness, not something
    # silently copied into the canonical archive or substituted for old links.
    require(editorial_pdf_review is not None,"editorial E467 memo not materialized: HARD HOLD")
    memo=editorial_pdf_review
    require(memo.is_file() and not memo.is_symlink() and git_blob(memo.read_bytes())==FROZEN["editorial_e467_memo_blob"],"E467 memo changed")
    result["native_original_source_custody"]="STRUCTURAL_ONLY"
    result["native_35_article_build_pass"]=False
    return result

def main(argv=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--editorial-e467-memo",type=Path)
    a=p.parse_args(argv)
    try:
        raw=(a.root/"reviews/r475_cdc_2020_2025_child_card_claim_crosswalk.json").read_bytes()
        m=strict_json(raw)
        result=check_native(a.root,m,a.editorial_e467_memo)
    except (Hold,ValueError,KeyError,TypeError,OSError,UnicodeError,json.JSONDecodeError) as e:
        result={"state":"R475_E467_NATIVE_INPUT_OR_REVIEW_MISSING_HARD_HOLD","reason":str(e),"may_publish":False,"qualified_qd_pass":False}
    print(json.dumps(result,sort_keys=True))
    return 2 # No output can be misread as release PASS.

if __name__=="__main__":sys.exit(main())
