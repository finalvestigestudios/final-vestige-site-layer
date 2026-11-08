"""Evidence-shape validator only. It NEVER authorizes publishing, sending, or promotion.

Private evidence artifacts are reviewed separately. A well-shaped attestation is
only a MANUAL_REVIEW_REQUIRED candidate, never merchant approval.
No addresses, recipient identifiers, earning URLs, or tokens are stored.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

PRODUCTS = {"zen12": 3, "total_focus": 5}
PROOF_TYPES = {"direct_partner_written_confirmation", "signed_partner_agreement", "verified_partner_dashboard"}
OPAQUE_REF = re.compile(r"^FV-PRIVATE-[A-Z0-9]{8,24}$")
STATES = {"NOT_VERIFIED", "VERIFIED_BY_HUMAN_REVIEWER"}
PROOF_FIELDS = {
    "product_key", "publisher", "source_type", "evidence_ref", "scope_channels",
    "scope_products", "partner_status", "affiliate_link_verified_privately",
    "creative_rights_checked", "offer_terms_checked", "valid_through",
    "human_reviewer_ref", "human_reviewed_date"
}

def evaluate_proof(product_key: str, proof: object, as_of: str = "2026-11-01") -> dict:
    """Fail closed. Does not adjudicate truthfulness of an external attestation."""
    issues = []
    if product_key not in PRODUCTS:
        return {"merchant_status": "HOLD_MERCHANT", "issues": ["UNKNOWN_PRODUCT"], "send_status": "HOLD_UNSENT"}
    if not isinstance(proof, dict):
        return {"merchant_status": "HOLD_MERCHANT", "issues": ["NO_PARTNER_PROOF"], "send_status": "HOLD_UNSENT"}
    missing = PROOF_FIELDS - set(proof)
    if missing:
        issues.append("MISSING_FIELDS:" + ",".join(sorted(missing)))
    if set(proof) - PROOF_FIELDS:
        issues.append("UNEXPECTED_FIELDS")
    if proof.get("product_key") != product_key or PRODUCTS[product_key] not in (3, 5):
        issues.append("WRONG_PRODUCT")
    if proof.get("publisher") != "Final Vestige Studios":
        issues.append("WRONG_PUBLISHER")
    if proof.get("source_type") not in PROOF_TYPES:
        issues.append("NOT_A_PARTNER_AUTHORITY_SOURCE")
    if not isinstance(proof.get("evidence_ref"), str) or not OPAQUE_REF.fullmatch(proof["evidence_ref"]):
        issues.append("MISSING_PRIVATE_EVIDENCE_REFERENCE")
    channels = proof.get("scope_channels")
    if not isinstance(channels, list) or "email" not in channels or any(c not in {"email", "website", "social"} for c in channels):
        issues.append("EMAIL_CHANNEL_NOT_SPECIFICALLY_PERMITTED")
    scopes = proof.get("scope_products")
    if not isinstance(scopes, list) or product_key not in scopes:
        issues.append("PRODUCT_NOT_SPECIFICALLY_PERMITTED")
    if proof.get("partner_status") != "approved":
        issues.append("PARTNER_APPROVAL_NOT_ESTABLISHED")
    for key in ("affiliate_link_verified_privately", "creative_rights_checked", "offer_terms_checked"):
        if proof.get(key) is not True:
            issues.append("NOT_CHECKED:" + key)
    if not isinstance(proof.get("human_reviewer_ref"), str) or not OPAQUE_REF.fullmatch(proof["human_reviewer_ref"]):
        issues.append("HUMAN_REVIEW_REFERENCE_REQUIRED")
    try:
        today = date.fromisoformat(as_of)
        expiry = date.fromisoformat(proof["valid_through"])
        reviewed = date.fromisoformat(proof["human_reviewed_date"])
        if expiry < today:
            issues.append("PERMISSION_EXPIRED")
        if reviewed > today:
            issues.append("REVIEW_IN_FUTURE")
    except (TypeError, ValueError, KeyError):
        issues.append("DATE_PROOF_INVALID")
    if issues:
        return {"merchant_status": "HOLD_MERCHANT", "issues": sorted(set(issues)), "send_status": "HOLD_UNSENT"}
    return {"merchant_status": "MANUAL_AUTHORITY_REVIEW_REQUIRED", "issues": ["WELL_SHAPED_NOT_INDEPENDENTLY_AUTHENTICATED"], "send_status": "HOLD_UNSENT"}

def audit_manifest(document: dict) -> dict:
    if document.get("schema") != "fv-dispatch-r53-authority-v1":
        raise ValueError("Unknown evidence schema")
    if document.get("canonical", {}).get("editorial_issues") != [1, 2, 4, 6]:
        raise ValueError("Four editorial issues are immutable")
    if document.get("canonical", {}).get("commercial_issues") != [3, 5]:
        raise ValueError("Two commercial positions are immutable")
    if document.get("disposition") != "ALL_ISSUES_HOLD_UNSENT":
        raise ValueError("This source cannot confer send permission")
    live = document.get("site", {})
    if live.get("new_post_email_default") is not False or live.get("email_format") != "excerpt":
        raise ValueError("Snapshot changed: independently re-read WordPress")
    counters = live.get("subscriber_counters", {})
    if any(type(counters.get(k)) is not int for k in ("total","confirmed","unconfirmed")):
        raise ValueError("Invalid aggregate counters")
    if live.get("unique_consent_eligible") != "NOT_VERIFIED":
        raise ValueError("An aggregate report cannot prove unique recipients")
    outputs = {}
    for key, position in PRODUCTS.items():
        offer = document.get("offers", {}).get(key, {})
        if offer.get("issue") != position:
            raise ValueError("Offer mapped to wrong edition")
        for field in ("partner_acceptance","product_email_channel_permission","permission_to_use_specific_creative","earnings_link_format","pricing_refund_at_final_checkout","published_approved_first_party_guide"):
            if offer.get(field) not in STATES:
                raise ValueError("Unknown evidence status: "+field)
        outputs[key] = evaluate_proof(key, offer.get("proof"), document.get("collected_at_utc","")[:10])
    return {"send_status": "HOLD_UNSENT", "newsletter_count": 6,
            "confirmed_eligible_recipients": None,
            "source_is_a_read_only_snapshot": True,
            "merchant": outputs}

def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    src = Path(args[0]) if args else Path(__file__).with_name("merchant_authority.json")
    try:
        result = audit_manifest(json.loads(src.read_text(encoding="utf-8")))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"send_status":"HOLD_UNSENT","error":str(exc)}, sort_keys=True))
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
