"""Offline, privacy-preserving Dispatch campaign gate. Never sends or contacts anyone.

No customer identifier or raw email is returned, logged, saved, or transmitted.
The synthetic transition tester is not connected to Jetpack; lack of a true
first-party confirmed-transition feed always leaves production attribution UNKNOWN.
"""
from __future__ import annotations

import json
import pathlib
from decimal import Decimal, InvalidOperation

BASE = pathlib.Path(__file__).resolve().parent
ALLOWED_SOURCES = {"youtube", "tiktok", "instagram", "facebook", "pinterest", "x", "bluesky"}


def load_contract(path: pathlib.Path | None = None) -> dict:
    return json.loads((path or BASE / "contract.json").read_text(encoding="utf-8"))


def validate_contract(c: dict) -> list[str]:
    errors: list[str] = []
    if c.get("status") != "DRAFT_ONLY_HOLD_UNSENT":
        errors.append("campaign must remain draft")
    src = c.get("source_campaign", {})
    if (src.get("editorial"), src.get("commercial_reserved")) != (4, 2):
        errors.append("the 4:2 source allocation must not change")
    if src.get("head_sha") != "d57ccdba3aee8f065e143e101c2945f4f3d01647":
        errors.append("source campaign version has drifted")
    issues = c.get("issue_routing", [])
    if [x.get("issue") for x in issues] != [1, 2, 3, 4, 5, 6]:
        errors.append("six original issue slots required")
    if [x.get("issue") for x in issues if x.get("kind") == "commercial_reserved"] != [3, 5]:
        errors.append("only issues 03 and 05 may reserve an offer")
    if any(x.get("state") not in ("HOLD", "HOLD_MERCHANT") for x in issues):
        errors.append("an issue was activated")
    lead = c.get("source_to_lead", {})
    if lead.get("first_party_list") != "Jetpack_existing_only" or lead.get("raw_email_in_analytics") is not False:
        errors.append("cannot create a new list or export subscriber identity")
    if lead.get("required_utm") != ["utm_source", "utm_medium", "utm_campaign", "utm_content"]:
        errors.append("campaign UTM mapping changed")
    event = c.get("authoritative_confirmed_signup", {})
    for field, expect in (("event", "confirmed_signup"), ("allowed_source", "jetpack_authoritative_transition"),
                          ("required_transition", "not_confirmed_to_confirmed"),
                          ("deduplication_site", "first_party_only_no_identifier_export")):
        if event.get(field) != expect:
            errors.append("unreliable confirmed-signup contract: " + field)
    if any(event.get(k) is not False for k in ("count_from_form_submit", "count_from_page_view",
                                                  "count_from_confirmation_email_open", "count_from_dashboard_total")):
        errors.append("inferred signups cannot be accepted")
    obs = c.get("observed_state", {})
    if (obs.get("newsletter_total"), obs.get("newsletter_confirmed"), obs.get("newsletter_unconfirmed")) != (2, 2, 2):
        errors.append("dashboard discrepancy requires a newly sourced reconciliation")
    if obs.get("reachable_recipient_count") is not None:
        errors.append("reachable recipients not proven")
    if obs.get("current_confirmed_signup_events") is not None:
        errors.append("no authoritative confirmed transition observed")
    if obs.get("welcome_received_proven") is not False or obs.get("real_received_newsletter") is not False:
        errors.append("do not claim a received email")
    offer = c.get("revenue_offer", {})
    if offer.get("offer_status") != "NO_RIGHTS_AND_PAYMENT_VERIFIED_OFFER_SELECTED":
        errors.append("no approved paid product has been selected")
    for k in ("one_offer_id", "merchant_outbound_url", "paid_orders_reported", "realized_net_revenue"):
        if offer.get(k) is not None:
            errors.append("unverified merchant or revenue field: " + k)
    report = c.get("reporting", {})
    for k in ("qualified_human_sessions", "confirmed_paid_orders", "paid_conversion_rate",
              "lead_to_paid_conversion", "net_revenue_per_1000"):
        if report.get(k) is not None:
            errors.append("unknown cohort KPI cannot be reported: " + k)
    if report.get("cohorts_days") != [7, 30] or report.get("no_clicks_as_sales") is not True:
        errors.append("commercial measurement safeguards missing")
    release = c.get("release", {})
    if release.get("result") != "HOLD_UNSENT" or any(release.get(k) is not False for k in (
        "founder_approved_exact_creative", "founder_approved_audience", "founder_approved_send",
        "merchant_permission", "verified_native_email", "address_and_unsubscribe")):
        errors.append("founder or compliance approval cannot be implied")
    return errors


def valid_asset_utm(utm: dict) -> bool:
    """Validate syntax only. Do not assert asset existence or observed traffic."""
    keys = {"utm_source", "utm_medium", "utm_campaign", "utm_content"}
    if set(utm) != keys:
        return False
    if utm["utm_source"] not in ALLOWED_SOURCES or utm["utm_medium"] != "organic_social":
        return False
    if utm["utm_campaign"] not in {f"{cluster}_pilot_2026_11" for cluster in
                                    ("mind", "mysteries", "history", "preparedness")}:
        return False
    asset = utm["utm_content"]
    return isinstance(asset, str) and 4 <= len(asset) <= 64 and all(ch.isascii() and
        (ch.isalnum() or ch in "_-.") for ch in asset)


def unique_confirmations(events: list[dict]) -> int:
    """Synthetic model: one qualifying transition per site/subscription identifier.

    The opaque identifier must never appear outside a trusted first-party adapter.
    This simulator returns only an aggregate integer and never authenticates a lead.
    """
    seen: set[tuple[str, str]] = set()
    for e in events:
        if e.get("event") != "confirmed_signup" or e.get("source") != "jetpack_authoritative_transition":
            continue
        if e.get("prior_state") == "confirmed" or e.get("new_state") != "confirmed":
            continue
        if e.get("prior_state") not in ("unconfirmed", "absent") or not e.get("consent_recorded"):
            continue
        if e.get("suppressed") or e.get("unsubscribed"):
            continue
        site, token = e.get("site_id"), e.get("internal_subscription_id")
        if not isinstance(site, str) or not isinstance(token, str) or not site or not token:
            continue
        seen.add((site, token))
    return len(seen)


def net_revenue_per_thousand(sessions: int | None, merchant_orders: list[dict] | None) -> Decimal | None:
    """Returns N/A as None where denominator or merchant facts cannot be verified.

    Synthetic only: order receipts must be independently sourced by an approved
    merchant-side adapter; a click, checkout start or unconfirmed order is insufficient.
    """
    if not isinstance(sessions, int) or isinstance(sessions, bool) or sessions <= 0:
        return None
    if merchant_orders is None:
        return None
    ids: set[str] = set()
    net = Decimal("0")
    for order in merchant_orders:
        if order.get("source") not in ("payhip_confirmed_paid_order", "affiliate_confirmed_paid_conversion"):
            return None
        if order.get("payment_status") != "paid" or order.get("refund_status") not in ("none", "partial", "full"):
            return None
        order_id = order.get("order_id")
        if not isinstance(order_id, str) or not order_id or order_id in ids:
            return None
        ids.add(order_id)
        try:
            amount, fees, refunds = (Decimal(str(order[k])) for k in ("earned", "fees", "refunds"))
        except (InvalidOperation, KeyError, TypeError):
            return None
        if any(not n.is_finite() or n < 0 for n in (amount, fees, refunds)):
            return None
        net += amount - fees - refunds
    return (net * Decimal("1000") / Decimal(sessions)).quantize(Decimal("0.01"))


if __name__ == "__main__":
    failures = validate_contract(load_contract())
    print(json.dumps({"result": "HOLD_UNSENT", "contract_valid": not failures,
                      "violations": failures, "confirmed_signups": "UNKNOWN",
                      "net_revenue_per_1000_qualified_sessions": "N/A"}, indent=2))
    raise SystemExit(bool(failures))
