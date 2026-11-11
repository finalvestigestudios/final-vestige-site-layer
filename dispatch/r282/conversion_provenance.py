"""Offline, synthetic-input contract for Dispatch conversion provenance.

NOT connected to Jetpack, WordPress, analytics, Grok or a merchant. Nothing here
sends mail, changes consent, or proves a sale. Fail closed on uncertain joins.
"""
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit, parse_qsl

KNOWN_EVENTS = {"landing_visit", "cta_click", "confirmed_signup", "paid_order", "affiliate_settlement"}
PROVEN_SOURCES = {"jetpack_provider", "first_party_server", "merchant_statement", "fv_checkout"}
FORBIDDEN_KEYS = {"email", "recipient", "ip", "ip_address", "phone", "address", "cookie", "user_agent", "name"}


def _money(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("invalid money")
    if not amount.is_finite() or amount < 0:
        raise ValueError("money must be finite and nonnegative")
    return amount


def _no_pii(value):
    if isinstance(value, dict):
        for k, v in value.items():
            if k.lower() in FORBIDDEN_KEYS:
                raise ValueError("personal data field prohibited")
            _no_pii(v)
    elif isinstance(value, list):
        for v in value:
            _no_pii(v)
    elif isinstance(value, str):
        if "@" in value or "mailto:" in value.lower():
            raise ValueError("identifying email-looking value prohibited")


def check_campaign_url(url):
    """Validate a source-tagged owned landing URL; never add parameters here."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "finalvestige.com" or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("unsafe or noncanonical landing URL")
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("ambiguous duplicate query keys")
    allowed = {"utm_source", "utm_medium", "utm_campaign", "utm_content", "asset_id"}
    if set(keys) - allowed:
        raise ValueError("unapproved attribution parameter")
    for key, value in pairs:
        if not value or len(value) > 96 or not all(c.isalnum() or c in "_-" for c in value):
            raise ValueError("unsafe attribution value")
    if "asset_id" in keys and ("utm_campaign" not in keys or "utm_source" not in keys):
        raise ValueError("asset provenance incomplete")
    return {k: v for k, v in pairs}


def inspect(events, provider_snapshot):
    """Return only non-identifying counts and evidence states; no email send action.

    Events here are untrusted *fixtures*. A source field is not an attestation.
    The caller must establish source authenticity outside this function.
    """
    _no_pii(events)
    _no_pii(provider_snapshot)
    if not isinstance(events, list) or not isinstance(provider_snapshot, dict):
        raise ValueError("invalid input shape")
    if set(provider_snapshot) != {"total", "confirmed", "unconfirmed", "email_followers", "wpcom_followers"}:
        raise ValueError("incomplete provider diagnostic")
    for n in provider_snapshot.values():
        if not isinstance(n, int) or isinstance(n, bool) or n < 0:
            raise ValueError("invalid count")
    seen = set()
    confirmed = set()
    paid = set()
    settled = {}
    stats = {"landing_visit": 0, "cta_click": 0, "confirmed_signup": 0, "paid_order": 0, "affiliate_settlement": 0}
    for event in events:
        if not isinstance(event, dict) or set(event) - {"kind", "ref", "source", "verified", "consent_recorded", "provider_eligible", "order_ref", "gross", "fees", "refunds", "commission", "landing_url", "cohort"}:
            raise ValueError("unapproved event fields")
        kind = event.get("kind")
        if kind not in KNOWN_EVENTS or event.get("source") not in PROVEN_SOURCES:
            raise ValueError("unknown event kind or source")
        ref = event.get("ref")
        if not isinstance(ref, str) or not (6 <= len(ref) <= 80) or not all(c.isalnum() or c in "_-" for c in ref):
            raise ValueError("use non-reversible internal reference, not identity")
        key = (kind, ref)
        if key in seen:
            continue  # idempotent event ingestion
        seen.add(key)
        if event.get("verified") is not True:
            continue
        if kind == "landing_visit":
            if event.get("source") != "first_party_server" or "landing_url" not in event:
                continue
            check_campaign_url(event["landing_url"])
        if kind == "cta_click" and event.get("source") != "first_party_server":
            continue
        if kind == "confirmed_signup":
            if event.get("source") != "jetpack_provider" or event.get("provider_eligible") is not True or event.get("consent_recorded") is not True:
                continue
            confirmed.add(ref)  # no click requirement: preverified WordPress.com accounts possible
        if kind == "paid_order":
            if event.get("source") != "fv_checkout":
                continue
            paid.add(ref)
        if kind == "affiliate_settlement":
            if event.get("source") != "merchant_statement" or not isinstance(event.get("order_ref"), str):
                continue
            gross = _money(event.get("commission"))
            fees = _money(event.get("fees"))
            refunds = _money(event.get("refunds"))
            if fees + refunds > gross:
                raise ValueError("net commission would be negative")
            if event["order_ref"] in settled:
                continue
            settled[event["order_ref"]] = gross - fees - refunds
        stats[kind] += 1
    # Provider diagnostics cannot establish a unique eligible audience by themselves.
    return {"provider_eligible_audience": None,
            "provider_diagnostic": provider_snapshot.copy(),
            "verified_confirmed_leads_in_supplied_events": len(confirmed),
            "verified_first_party_orders_in_supplied_events": len(paid),
            "independently_reported_affiliate_settlements_in_supplied_events": len(settled),
            "affiliate_net_commission_in_supplied_events": str(sum(settled.values(), Decimal("0"))),
            "qualified_human_sessions": None,
            "net_revenue_per_1000_qualified_sessions": None,
            "verified_events_by_kind": stats,
            "is_live_measurement": False,
            "is_campaign_release_approved": False}
