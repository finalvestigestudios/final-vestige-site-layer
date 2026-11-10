"""Fail-closed, NON-SENDING Dispatch release evidence checker. No network, no PII."""
import json
import pathlib
import sys

EXPECTED = {1: "editorial", 2: "editorial", 3: "commercial", 4: "editorial", 5: "commercial", 6: "editorial"}
COMMON_GATES = (
    "primary_purpose_legal_review", "truthful_subject_review",
    "genuine_jetpack_preview", "actual_received_render_review",
    "final_vestige_postal_address_in_received_message",
    "unsubscribe_visible_in_received_message", "unsubscribe_function_verified",
    "eligible_recipients_provider_verified", "welcome_delivery_verified",
    "relevant_first_party_cta_live", "founder_final_campaign_approval",
)
MERCHANT_GATES = (
    "named_affiliate_acceptance", "permission_to_promote_by_email",
    "merchant_issued_earning_url", "approved_first_party_buyer_guide_live",
    "specific_seller_sales_page_and_creative_reviewed",
    "current_cart_price_and_refund_verified", "product_claims_independently_cleared",
    "near_offer_affiliate_disclosure_checked",
)
VALID_STATUSES = {"verified", "not_verified", "blocked", "not_applicable"}


def audit(document):
    errors, blockers = [], {}
    if document.get("release_policy") != "NO_SEND_NO_PUBLICATION":
        errors.append("Missing immutable no-send policy")
    entries = document.get("issues")
    if not isinstance(entries, list):
        return {"status": "HOLD", "errors": [*errors, "issues must be a list"], "blockers": {}}
    if len(entries) != 6:
        errors.append("Exactly six issues required")
    seen = set()
    for item in entries:
        number = item.get("number") if isinstance(item, dict) else None
        if number not in EXPECTED or number in seen:
            errors.append("Unexpected/duplicated issue number")
            continue
        seen.add(number)
        if item.get("kind") != EXPECTED[number]:
            errors.append(f"Issue {number} violates canonical 4 editorial / 2 offer plan")
        required = COMMON_GATES + (MERCHANT_GATES if number in (3, 5) else ())
        evidence = item.get("evidence") or {}
        missing = []
        for gate in required:
            entry = evidence.get(gate)
            if not isinstance(entry, dict) or entry.get("status") != "verified":
                missing.append(gate)
                continue
            if not all(isinstance(entry.get(k), str) and entry[k].strip() for k in ("source", "verified_at", "reviewer")):
                missing.append(gate + " (no provenance)")
        blockers[str(number)] = missing
        if item.get("send_authorized") is not False:
            errors.append(f"Issue {number} must explicitly remain unsent")
        if item.get("actual_received_evidence") not in (None, "WITHHELD_PRIVATE"):
            errors.append(f"Issue {number} may not include raw recipient evidence")
    if seen != set(EXPECTED):
        errors.append("Canonical six issue IDs missing")
    return {
        "status": "HOLD" if errors or any(blockers.values()) else "FOUNDER_REVIEW_CANDIDATE_ONLY_NOT_SEND_AUTHORIZATION",
        "errors": errors,
        "blockers": blockers,
        "send_authorized": False,
        "sends_performed": 0,
        "note": "Offline validation cannot authenticate any provenance or authorize delivery.",
    }


if __name__ == "__main__":
    payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(audit(payload), indent=2))
