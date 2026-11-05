"""Fail-closed, PII-free aggregation of read-only WordPress newsletter snapshots.

Does not call the network, contact subscribers, calculate sales, or authorize sends.
Input shapes are those of the `newsletter.get_settings` and `newsletter.status`
read-only WordPress connector operations. The output deliberately excludes PII.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any

REQUIRED_GATES = (
    "native_email_eligibility", "received_welcome", "fieldbook_pdf_retrieval",
    "signed_out_signup", "received_jetpack_email_preview",
    "publisher_postal_address", "operational_unsubscribe",
    "founder_campaign_release_approval",
)
COMMERCIAL_GATES = (
    "named_merchant_acceptance", "written_email_promotion_permission",
    "approved_tracking_url", "live_exact_sku_buyer_guide",
    "checkout_and_refund_terms", "independent_claim_review",
)


def _nonnegative_int(value: Any, key: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"invalid aggregate counter: {key}")
    return value


def _check_time(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("missing snapshot as_of")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid snapshot as_of") from exc
    if dt.tzinfo is None:
        raise ValueError("as_of must include timezone")
    return value


def analyze(settings_response: dict, status_response: dict) -> dict:
    """Return only safe aggregate facts; missing/invalid fields prevent a report."""
    if not isinstance(settings_response, dict) or not isinstance(status_response, dict):
        raise ValueError("expected native read-only response dictionaries")
    if settings_response.get("success") is not True or status_response.get("success") is not True:
        raise ValueError("unverified WordPress response")
    if settings_response.get("action") != "get_settings" or status_response.get("action") != "status":
        raise ValueError("incorrect read-only WordPress operations")
    if settings_response.get("blog_id") != status_response.get("blog_id"):
        raise ValueError("different WordPress sites")
    if settings_response.get("site_url") != "https://finalvestige.com" or status_response.get("site_url") != "https://finalvestige.com":
        raise ValueError("unexpected site")
    settings = settings_response.get("settings")
    subs = status_response.get("subscribers")
    if not isinstance(settings, dict) or not isinstance(subs, dict):
        raise ValueError("missing settings or subscriber aggregate")
    for key in ("subscriptions", "email_new_posts_by_default"):
        if type(settings.get(key)) is not bool:
            raise ValueError(f"missing/invalid {key}")
    format_ = settings.get("email_content_format")
    if format_ not in ("excerpt", "full"):
        raise ValueError("invalid email_content_format")
    counts = {name: _nonnegative_int(subs.get(name), name) for name in
              ("total", "confirmed", "unconfirmed", "suppressed", "paid", "imported_last_24h")}
    if type(status_response.get("site_can_send")) is not bool:
        raise ValueError("missing site_can_send")
    raw_sends = status_response.get("recent_sends")
    if not isinstance(raw_sends, list):
        raise ValueError("missing recent_sends")
    sends = []
    for send in raw_sends[:10]:
        if not isinstance(send, dict) or type(send.get("post_id")) is not int:
            raise ValueError("invalid send entry")
        state = send.get("status")
        if not isinstance(state, str) or not state:
            raise ValueError("missing send status")
        sends.append({"post_id": send["post_id"], "status": state})
    as_of_settings = _check_time(settings_response.get("as_of"))
    as_of_status = _check_time(status_response.get("as_of"))
    warnings = []
    if counts["confirmed"] + counts["unconfirmed"] > counts["total"]:
        warnings.append("NON_ADDITIVE_COUNTERS: do not sum confirmed and unconfirmed with total")
    if counts["imported_last_24h"] > 0:
        warnings.append("IMPORT_ACTIVITY_REQUIRES_PRIVATE_RECONCILIATION: native aggregate is nonzero; it does not identify actor, origin, or consent")
    if format_ == "excerpt":
        warnings.append("EXCERPT_CTA_RISK: native received-email preview still required")
    if not settings["email_new_posts_by_default"]:
        warnings.append("POST_NOTIFICATIONS_DEFAULT_OFF: must remain unchanged without approval")
    if not any(s["status"] not in ("never_sent_opted_out",) for s in sends):
        warnings.append("NO_DELIVERY_PROOF: recent posts were not delivered as emails")
    else:
        warnings.append("SEND_STATUS_NOT_INBOX_RECEIPT: reconcile any dispatched records privately")
    return {
        "site": "finalvestige.com", "source": "WordPress read-only newsletter operations",
        "settings_as_of": as_of_settings, "status_as_of": as_of_status,
        "newsletter_enabled": settings["subscriptions"],
        "auto_send_default_enabled": settings["email_new_posts_by_default"],
        "delivery_format": format_, "wp_site_can_send": status_response["site_can_send"],
        "aggregate_counters": counts,
        "recent_send_states": sends,
        "warnings": warnings,
        "verified_email_recipients": None, "confirmed_signup_events": None,
        "welcome_received": None, "fieldbook_received": None,
        "verified_paid_orders": None, "net_revenue_per_1000_qualified_sessions": None,
        "shared_release_gates": {key: "NOT_VERIFIED" for key in REQUIRED_GATES},
        "commercial_release_gates": {key: "NOT_VERIFIED" for key in COMMERCIAL_GATES},
        "issue_decisions": {str(n).zfill(2):
            "HOLD_MERCHANT_AND_HOLD_UNSENT" if n in (3, 5) else "HOLD_UNSENT"
            for n in range(1, 7)},
        "release_decision": "HOLD_UNSENT", "evidence_kind": "AGGREGATE_DIAGNOSTIC_NOT_DELIVERY",
    }
