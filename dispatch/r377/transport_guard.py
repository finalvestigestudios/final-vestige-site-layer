"""Offline-only Dispatch/Jetpack release evidence evaluator. Never sends or publishes.

All evidence starts false, null or absent. This module cannot establish consent, vendor
acceptance, native email appearance or paid sales from synthetic fixtures.
"""
from __future__ import annotations
import json
from pathlib import Path

BASE_GATES = (
    "founder_final_campaign_approval",
    "provider_unique_email_eligible_count_verified_privately",
    "welcome_and_fieldbook_received_verified",
    "native_jetpack_preview_captured",
    "actual_rendered_subject_checked",
    "actual_rendered_preheader_checked",
    "final_vestige_postal_address_verified_in_render",
    "functional_unsubscribe_verified_without_sending_campaign",
    "editorial_source_and_claim_review_approved",
    "landing_cta_live_and_accessible",
)
COMMERCIAL_GATES = (
    "named_publisher_partner_acceptance_verified",
    "specific_sku_email_channel_permission_verified",
    "issued_attributable_earning_link_verified",
    "live_mind_owned_warmup_guide_verified",
    "referred_checkout_price_and_refund_terms_verified",
    "adjacent_disclosure_in_native_email_verified",
)
FORBIDDEN_UNPROVEN = (
    "[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]",
    "[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]",
    "[[VALID_POSTAL_ADDRESS_REQUIRED]]",
    "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",
)

def reconcile_subscribers(total, confirmed, unconfirmed, wpcom, email):
    """Only category arithmetic; not recipient/consent authority."""
    if any(type(n) is not int or n < 0 for n in (total,confirmed,unconfirmed,wpcom,email)):
        raise ValueError("counts must be nonnegative integers")
    if confirmed > total:
        relationship = "unexplained_confirmed_exceeds_total"
    else:
        relationship = "not_inherently_contradictory_unconfirmed_excluded"
    return {"relationship": relationship, "reported_total": total,
            "reported_confirmed": confirmed, "reported_unconfirmed": unconfirmed,
            "reader_wpcom_followers": wpcom, "stats_direct_email_followers": email,
            "unique_email_eligible_inboxes": None, "confirmed_signup_events": None}

def evaluate_issue(issue, proof=None):
    """Decision means REVIEW HOLD, never permission to publish/send."""
    proof = proof or {}
    kind = issue.get("kind")
    if kind not in ("editorial", "commercial-review-pending"):
        raise ValueError("unknown issue kind")
    required = BASE_GATES + (COMMERCIAL_GATES if kind == "commercial-review-pending" else ())
    missing = [key for key in required if proof.get(key) is not True]
    cta = issue.get("editorial_cta", "")
    if not isinstance(cta, str) or not cta.startswith("https://finalvestige.com/"):
        missing.append("verified_first_party_cta")
    if issue.get("merchant_affiliate_url") is not None:
        missing.append("merchant_url_not_allowed_in_draft")
    if not issue.get("subject") or not issue.get("preheader"):
        missing.append("subject_and_preheader_present")
    if issue.get("publish_state") != "hold":
        missing.append("source_must_remain_held")
    if any(token in str(issue) for token in FORBIDDEN_UNPROVEN):
        missing.append("unresolved_placeholder_must_not_be_scheduled")
    # Even all-false release evidence is handled as a reviewer artifact; no send method exists.
    return {"issue":issue["number"], "type":kind, "decision":"HOLD_UNSENT",
            "send_authorized":False, "release_proofs_missing":sorted(set(missing)),
            "subject_is_proposed_post_title_not_verified_rendered_email":True,
            "preheader_is_draft_metadata_not_verified_jetpack_control":True}

def validate_manifest(data):
    issues = data["issues"]
    if len(issues)!=6 or [a.get("number") for a in issues]!=list(range(1,7)):
        raise ValueError("six ordered issues required")
    if sum(i.get("kind")=="editorial" for i in issues)!=4:
        raise ValueError("editorial balance must be four")
    if [i["number"] for i in issues if i.get("kind")=="commercial-review-pending"] != [3,5]:
        raise ValueError("exactly Issues 03 and 05 may reserve merchant placement")
    return True

def revenue_per_1000(*, sessions, session_evidence, partner_orders, costs_verified=False):
    """Strict financial reporting contract. Null means unavailable, not zero sales."""
    if type(sessions) is not int or sessions <= 0 or session_evidence != "qualified_human_audited":
        return None
    if not costs_verified or not isinstance(partner_orders, list):
        return None
    if not partner_orders:
        return None
    if any(not isinstance(o,dict) or o.get("evidence")!="partner_settled" or
           any(type(o.get(k)) not in (int,float) or o[k]<0 for k in ("gross", "refunds", "fees"))
           for o in partner_orders):
        return None
    net = sum(o["gross"]-o["refunds"]-o["fees"] for o in partner_orders)
    return {"net_revenue_per_1000":round(1000*net/sessions,2),
            "net_revenue":round(net,2), "independently_settled_order_records":len(partner_orders),
            "small_sample_warning":sessions<1000 or len(partner_orders)<30}

def dossier(manifest):
    validate_manifest(manifest)
    return {"mode":"REVIEW_ONLY_NEVER_SEND", "original_campaign_preserved":True,
            "native_email_render_verified":False,
            "note":"WordPress post title is native subject. Draft preheaders are not a verified Jetpack control.",
            "issue_decisions":[evaluate_issue(i) for i in manifest["issues"]],
            "conversion_result":revenue_per_1000(sessions=None,session_evidence=None,partner_orders=None),
            "source_refs":{
              "wp_native":"https://wordpress.com/support/newsletter/send-newsletter-emails/",
              "ftc_can_spam":"https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",
              "merchant_zen12":"https://zen12.com/",
              "merchant_total_focus":"https://hypnosislive.com/mental-skills/total-focus",
              "merchant_refund_faq":"https://hypnosislive.com/faq"
            }}

if __name__=="__main__":
    import sys
    src=Path(sys.argv[1])
    print(json.dumps(dossier(json.loads(src.read_text())),indent=2))
