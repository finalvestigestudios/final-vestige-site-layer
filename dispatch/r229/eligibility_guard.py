"""Offline-only Dispatch provider-evidence and release guard. No HTTP, PII or sends."""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Any

ACTIVE = "Subscribed"
INELIGIBLE = frozenset({"Not subscribed", "Not confirmed", "Bounced", "Emails paused", "Not sending"})
BLOCK = "HOLD_UNSENT"
MERCHANT_BLOCK = "HOLD_MERCHANT"


def diagnose_counts(newsletter: dict[str, Any], followers: dict[str, Any]) -> dict[str, Any]:
    """Counts describe overlapping systems, never recipients or lead attribution."""
    subs = newsletter.get("subscribers", {})
    checks = {key: subs.get(key) for key in ("total", "confirmed", "unconfirmed", "suppressed")}
    if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in checks.values()):
        return {"status": "UNVERIFIABLE_PROVIDER_COUNTERS", "eligible_email_recipients": None}
    if followers.get("partial") or any(not isinstance(followers.get(k), int) for k in ("wpcom", "email")):
        return {"status": "PARTIAL_FOLLOWER_COUNTERS", "eligible_email_recipients": None}
    if checks["confirmed"] > checks["total"]:
        return {"status": "INCONSISTENT_PROVIDER_COUNTERS", "eligible_email_recipients": None}
    return {"status": "NEEDS_EMAIL_SUBSCRIPTION_STATUS_BREAKDOWN",
            "newsletter_total": checks["total"], "confirmed_counter": checks["confirmed"],
            "unconfirmed_requests_separate": checks["unconfirmed"],
            "wpcom_followers_overlapping": followers["wpcom"],
            "email_only_followers": followers["email"],
            "eligible_email_recipients": None, "attributed_confirmed_signups": None}


def confirmed_signup(event: dict[str, Any]) -> bool:
    """An event needs authenticated provider state transition AND proven source linkage."""
    if not isinstance(event, dict):
        return False
    if event.get("provider") != "Jetpack" or event.get("authenticated_provider") is not True:
        return False
    if event.get("current_email_status") != ACTIVE:
        return False
    if event.get("previous_email_status") not in INELIGIBLE:
        return False
    if event.get("is_first_verified_transition") is not True or event.get("deduplicated") is not True:
        return False
    if event.get("consent_for_dispatch") is not True:
        return False
    if event.get("attribution_evidence") != "first_party_verified_source":
        return False
    # Never accept direct personal identifiers or URLs with email tokens as event IDs.
    forbidden_terms = ("email", "address", "phone", "ip_", "_ip", "cookie", "raw_name", "recipient_name")
    safe_status_keys = {"current_email_status", "previous_email_status"}
    if any(k not in safe_status_keys and any(term in k.lower() for term in forbidden_terms) for k in event):
        return False
    token = event.get("opaque_transition_id")
    if not isinstance(token, str) or not (12 <= len(token) <= 96):
        return False
    if any(c not in "abcdef0123456789-_" for c in token.lower()):
        return False
    return True


def release_state(issue: int, proofs: dict[str, Any]) -> dict[str, Any]:
    """Human signoff is necessary but NEVER sufficient for auto-sending."""
    if issue not in range(1, 7):
        raise ValueError("only six approved draft editions")
    commercial = issue in (3, 5)
    required_common = ("native_jetpack_received_mime", "publisher_postal_address_verified",
                       "working_received_unsubscribe", "eligible_recipient_status_aggregate",
                       "final_creative_reviewed", "founder_final_send_approval")
    required_merchant = ("named_affiliate_acceptance", "explicit_email_promotion_permission",
                         "account_issued_earning_url", "published_approved_guide",
                         "current_checkout_and_refunds_checked", "merchant_claims_checked")
    checked = required_common + (required_merchant if commercial else ())
    valid = {k: proofs.get(k) is True and bool(proofs.get(k+"_evidence_ref")) for k in checked}
    unresolved = [key for key, ok in valid.items() if not ok]
    return {"issue": issue, "commercial": commercial, "status": BLOCK,
            "merchant_status": MERCHANT_BLOCK if commercial else "NOT_APPLICABLE",
            "missing_proof": unresolved, "ready_for_human_review_only": len(unresolved) == 0,
            "send_authorized_by_code": False}


def realized_revenue_per_1000(qualified_sessions: int | None, settled_transactions: list[dict[str, Any]] | None) -> Decimal | None:
    """Refuse conversion estimates without independent settlement evidence."""
    if not isinstance(qualified_sessions, int) or isinstance(qualified_sessions, bool) or qualified_sessions <= 0:
        return None
    if not isinstance(settled_transactions, list) or not settled_transactions:
        return None
    net = Decimal("0")
    observed_order_refs = set()
    for item in settled_transactions:
        if (not isinstance(item, dict) or item.get("independently_verified_paid") is not True
            or item.get("settled") is not True or item.get("attributed_qualified_session") is not True
            or item.get("currency") != "USD" or item.get("report_authoritative") is not True):
            return None
        order_ref = item.get("opaque_order_ref")
        proof_ref = item.get("partner_settlement_report_ref")
        if (not isinstance(order_ref, str) or not (8 <= len(order_ref) <= 96)
            or not isinstance(proof_ref, str) or not (8 <= len(proof_ref) <= 128)
            or order_ref in observed_order_refs or "@" in order_ref or "@" in proof_ref):
            return None
        observed_order_refs.add(order_ref)
        try:
            gross, refunds, fees = (Decimal(str(item[x])) for x in ("gross", "refunds", "fees"))
        except (InvalidOperation, KeyError, TypeError, ValueError):
            return None
        if not all(x.is_finite() for x in (gross, refunds, fees)) or gross < 0 or refunds < 0 or fees < 0:
            return None
        net += gross - refunds - fees
    return (net * Decimal("1000") / Decimal(qualified_sessions)).quantize(Decimal("0.01"))
