"""Offline/zero-network Dispatch preflight. NEVER sends, publishes or accesses subscriber PII.

All booleans are attestations for human inspection; no combination authorizes sending.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Mapping

EDITORIAL = frozenset((1, 2, 4, 6))
MERCHANT = frozenset((3, 5))
ISSUES = EDITORIAL | MERCHANT
SHARED = (
    "founder_approved_final_copy", "founder_approved_recipient_audience",
    "founder_approved_specific_delivery", "provider_email_eligibility_reconciled",
    "provider_double_opt_in_witness", "welcome_received_witness",
    "real_jetpack_preview_witness", "sender_identity_witness",
    "publisher_postal_address_witness", "working_unsubscribe_witness",
    "post_level_send_control_witness", "source_and_subject_review",
)
MERCHANT_FIELDS = (
    "publisher_affiliate_acceptance", "email_channel_permission",
    "specific_merchant_offer_approved", "approved_issued_earning_link",
    "independent_live_first_party_guide", "accurate_current_checkout_terms",
    "merchant_claim_boundaries_reviewed", "adjacent_commission_disclosure",
)


def edition_gate(number: int, proofs: Mapping[str, bool] | None = None) -> dict:
    """A missing attestation remains missing. This function cannot approve a send."""
    if number not in ISSUES:
        raise ValueError("Unknown campaign edition")
    proofs = proofs or {}
    required = SHARED + (MERCHANT_FIELDS if number in MERCHANT else ())
    missing = [field for field in required if proofs.get(field) is not True]
    return {
        "issue": number,
        "type": "commercial" if number in MERCHANT else "editorial",
        "status": "HOLD_UNSENT",
        "merchant_status": "HOLD_MERCHANT" if number in MERCHANT and any(
            proofs.get(field) is not True for field in MERCHANT_FIELDS) else "NOT_APPLICABLE_OR_REVIEW_ONLY",
        "missing": missing,
        "human_review_only": len(missing) == 0,
        "send_authorized": False,
    }


def confirmed_signup(proof: Mapping) -> bool:
    """Require a real provider-confirmed *transition*, never browser/URL signals.

    This is a synthetic contract. No provider integration/event emission.
    """
    return (
        proof.get("source") == "authenticated_provider"
        and proof.get("confirmation_attested") is True
        and proof.get("prior_email_status") in ("pending", "unconfirmed")
        and isinstance(proof.get("confirmation_proof_id"), str)
        and len(proof["confirmation_proof_id"].strip()) >= 8
        and "@" not in proof["confirmation_proof_id"]
        and proof.get("new_email_status") == "subscribed"
        and isinstance(proof.get("opaque_provider_key"), str)
        and len(proof["opaque_provider_key"].strip()) >= 12
        and "@" not in proof["opaque_provider_key"]
        and proof.get("deduplicated") is True
        and proof.get("opted_out") is False
    )


def qualified_revenue_rate(qualified_sessions, orders) -> dict:
    """Only independently reported PAID & settled order rows; no guessed zero.

    Each row needs settled, source_verified, gross, refunds, fees in ONE currency;
    no attributed sessions/orders -> null, not zero. Cohort filters upstream.
    """
    if not isinstance(qualified_sessions, int) or isinstance(qualified_sessions, bool) or qualified_sessions <= 0:
        return {"status": "NOT_COMPUTABLE", "reason": "qualified_sessions_missing", "rate": None}
    if not isinstance(orders, list) or not orders:
        return {"status": "NOT_COMPUTABLE", "reason": "paid_order_evidence_missing", "rate": None}
    currencies = set()
    cohorts = set()
    seen = set()
    net = Decimal("0")
    for item in orders:
        if not isinstance(item, dict) or item.get("settled") is not True or item.get("source_verified") is not True or item.get("attribution_verified") is not True:
            return {"status": "NOT_COMPUTABLE", "reason": "unverified_order", "rate": None}
        order_id = item.get("opaque_order_id")
        if not isinstance(order_id, str) or len(order_id) < 8 or order_id in seen or "@" in order_id:
            return {"status": "NOT_COMPUTABLE", "reason": "order_identity_unreconciled", "rate": None}
        seen.add(order_id)
        currencies.add(item.get("currency"))
        cohorts.add(item.get("cohort"))
        try:
            vals = [Decimal(str(item[k])) for k in ("gross", "refunds", "fees")]
        except (KeyError, InvalidOperation, TypeError, ValueError):
            return {"status": "NOT_COMPUTABLE", "reason": "missing_financial_component", "rate": None}
        if not all(v.is_finite() and v >= 0 for v in vals) or vals[1] > vals[0]:
            return {"status": "NOT_COMPUTABLE", "reason": "invalid_amount", "rate": None}
        net += vals[0] - vals[1] - vals[2]
    if len(cohorts) != 1 or next(iter(cohorts)) not in ("7d", "30d"):
        return {"status": "NOT_COMPUTABLE", "reason": "cohort_not_reconciled", "rate": None}
    if len(currencies) != 1 or next(iter(currencies)) not in ("USD",):
        return {"status": "NOT_COMPUTABLE", "reason": "currency_not_reconciled", "rate": None}
    return {"status": "COMPUTED_FROM_SUPPLIED_EVIDENCE", "rate": str((net * 1000 / qualified_sessions).quantize(Decimal("0.01"))),
            "currency": "USD", "cohort": next(iter(cohorts)), "verified_order_rows": len(seen), "net": str(net)}


def static_subject_audit(manifest: Mapping) -> dict:
    """Review flags: duplicate CTA; questionable Apollo duration; redundant signup.

    Flags are editorial redlines, not assertions that an email was transmitted.
    """
    issues = manifest["issues"]
    destinations = {}
    flags = {}
    for issue in issues:
        num = int(issue["number"])
        target = issue.get("editorial_cta")
        if target and str(target).startswith("https://"):
            destinations.setdefault(target, []).append(num)
        entry = []
        if num == 4 and "Fourteen seconds" in issue.get("subject", ""):
            entry.append("NASA_TIMING_CLAIM_REVIEW")
        if num == 6 and target == "https://finalvestige.com/focus/":
            entry.append("RETURNING_SUBSCRIBER_REOPTIN_RISK")
        if "[[" in str(target):
            entry.append("PENDING_CTA_INERT")
        flags[str(num)] = entry
    for nums in destinations.values():
        if len(nums) > 1:
            for num in nums:
                flags[str(num)].append("DUPLICATE_EDITORIAL_DESTINATION")
    return flags
