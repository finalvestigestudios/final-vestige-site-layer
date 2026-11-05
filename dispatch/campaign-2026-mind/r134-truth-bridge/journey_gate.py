"""R134. Read-only, PII-free, fail-closed Dispatch conversion evidence gate.

Only synthetic or manually reviewed aggregate evidence is accepted. This script
NEVER sends mail, updates WordPress, or calls an external checkout.
"""
import json
import sys
from pathlib import Path

COUNTER_KEYS = ("total", "confirmed", "unconfirmed", "suppressed")
ALLOWED_STATUS = {"unverified", "source_observed", "native_verified"}


def assess(snapshot):
    if not isinstance(snapshot, dict) or "wordpress" not in snapshot:
        raise ValueError("snapshot must contain wordpress evidence")
    raw = json.dumps(snapshot, sort_keys=True).lower()
    for forbidden in ("subscriber_email", "email_address", "recipient_email", "customer_name", "password", "api_key"):
        if forbidden in raw:
            raise ValueError("PII/secrets prohibited in evidence payload: " + forbidden)

    wp = snapshot["wordpress"]
    counts = wp.get("counts", {})
    for key in COUNTER_KEYS:
        value = counts.get(key)
        if type(value) is not int or value < 0:
            raise ValueError("missing or invalid count: " + key)
    # Counts come from different WordPress diagnostics, NOT a mutually exclusive partition.
    if counts["confirmed"] > counts["total"]:
        raise ValueError("confirmed exceeds reported total: inspect source")
    eligible = wp.get("native_email_eligible")
    if eligible is not None and (type(eligible) is not int or not 0 <= eligible <= counts["total"]):
        raise ValueError("native_email_eligible must be source-verified and within total")
    if wp.get("cta_observation_status") not in ALLOWED_STATUS:
        raise ValueError("CTA observation status must be explicit")
    if wp.get("email_new_posts_by_default") is not False:
        raise ValueError("automatic new-post email default must remain disabled")
    if wp.get("email_content_format") not in ("excerpt", "full"):
        raise ValueError("email format unknown")

    gates = {
        "confirmed_signup_measured": bool(snapshot.get("native_confirmed_signup_evidence", False)),
        "recipient_eligibility_known": eligible is not None and bool(snapshot.get("native_recipient_filter_evidence", False)),
        "welcome_received": bool(snapshot.get("received_welcome_evidence", False)),
        "fieldbook_received": bool(snapshot.get("fieldbook_received_evidence", False)),
        "genuine_jetpack_preview": bool(snapshot.get("native_email_preview_evidence", False)),
        "physical_address_rendered": bool(snapshot.get("publisher_postal_address_rendered", False)),
        "unsubscribe_working": bool(snapshot.get("unsubscribe_mechanism_verified", False)),
        "explicit_founder_send_approval": bool(snapshot.get("explicit_founder_send_approval", False)),
    }
    # A click, a frontend state switch, and changing aggregate counters cannot be
    # promoted to native confirmation proof. Require independent evidence provenance.
    if gates["confirmed_signup_measured"] and not snapshot.get("native_signup_provenance"):
        raise ValueError("signup evidence lacks native confirmation provenance")
    if gates["recipient_eligibility_known"] and not snapshot.get("recipient_filter_provenance"):
        raise ValueError("recipient filter lacks provenance")
    if wp["cta_observation_status"] == "native_verified" and not snapshot.get("real_visitor_browser_evidence"):
        raise ValueError("do not treat serialized page HTML as visitor-browser evidence")

    offer = snapshot.get("offer", {})
    commercial = {
        "named_partner_approval": bool(offer.get("named_partner_approval", False)),
        "email_promotion_permission": bool(offer.get("email_promotion_permission", False)),
        "verified_link_format": bool(offer.get("verified_link_format", False)),
        "exact_sku_guide_live": bool(offer.get("exact_sku_guide_live", False)),
        "seller_claims_reviewed": bool(offer.get("seller_claims_reviewed", False)),
        "current_checkout_terms_reviewed": bool(offer.get("current_checkout_terms_reviewed", False)),
        "merchant_consent_separate": bool(offer.get("merchant_consent_separate", False)),
    }
    if any(commercial.values()) and not offer.get("evidence_records"):
        raise ValueError("commercial readiness assertion requires source records")

    paid = snapshot.get("paid_outcomes", {})
    confirmed_orders = paid.get("confirmed_orders")
    net = paid.get("realized_net_revenue_usd")
    qualified = paid.get("qualified_human_sessions")
    if confirmed_orders is not None:
        if type(confirmed_orders) is not int or confirmed_orders < 0:
            raise ValueError("invalid paid order count")
        if confirmed_orders > 0 and not paid.get("settled_order_reconciliation_evidence"):
            raise ValueError("orders require authoritative source reconciliation")
    if net is not None:
        if not isinstance(net, (int, float)) or isinstance(net, bool):
            raise ValueError("invalid realized net revenue")
        if not paid.get("settled_order_reconciliation_evidence"):
            raise ValueError("net revenue requires settled payment evidence")
    if qualified is not None and (type(qualified) is not int or qualified < 0):
        raise ValueError("invalid qualified human session denominator")
    revenue_per_k = round(net * 1000 / qualified, 2) if (net is not None and qualified is not None and qualified > 0 and paid.get("settled_order_reconciliation_evidence")) else None

    editorial_ready = all(gates.values())
    commercial_ready = editorial_ready and all(commercial.values())
    return {
        "release": "HOLD_UNSENT",  # release is NEVER automated, even if evidence someday passes
        "editorial_gate": "REVIEW_ELIGIBLE_NOT_AUTHORIZED" if editorial_ready else "HOLD_EVIDENCE",
        "commercial_gate": "REVIEW_ELIGIBLE_NOT_AUTHORIZED" if commercial_ready else "HOLD_MERCHANT_AND_EVIDENCE",
        "readiness": {"core": gates, "commercial": commercial},
        "verified_email_reachable": eligible if gates["recipient_eligibility_known"] else None,
        "confirmed_and_unconfirmed_are_not_additive": True,
        "cta_source_risk": "VISITOR_BROWSER_TEST_REQUIRED" if wp["cta_observation_status"] != "native_verified" else "VISITOR_BROWSER_EVIDENCE_RECORDED",
        "realized_net_revenue_per_1000_qualified_human_sessions": revenue_per_k,
        "sample_warning": "Small audiences do not support reliable A/B claims",
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python journey_gate.py sanitized_snapshot.json")
    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(assess(payload), indent=2, sort_keys=True))
