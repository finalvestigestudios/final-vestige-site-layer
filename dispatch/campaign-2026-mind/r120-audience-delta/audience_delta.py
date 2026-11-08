"""Read-only, PII-minimizing audience change and conversion evidence checks.

This module cannot read WordPress, subscribe, email, or publish. It accepts
separately sourced snapshots and rejects inferred customer/conversion events.
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re

COUNTER_KEYS = ("total", "confirmed", "unconfirmed", "suppressed", "paid", "imported_last_24h")
OPAQUE = re.compile(r"^[a-f0-9]{64}$")
EVENT_KEYS = {"opaque_subscriber_id", "native_event_id", "source", "confirmed_status",
              "consent_evidence", "occurred_at", "source_verified", "email_eligible",
              "opted_out", "utm_source", "utm_campaign", "utm_content"}


def _instant(value):
    if not isinstance(value, str):
        raise ValueError("timestamp required")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid timestamp") from exc
    if result.tzinfo is None:
        raise ValueError("timezone required")
    return result


def validate_snapshot(snapshot):
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("subscribers"), dict):
        raise ValueError("native subscriber snapshot required")
    _instant(snapshot.get("as_of"))
    counts = snapshot["subscribers"]
    for key in COUNTER_KEYS:
        if key in counts and (type(counts[key]) is not int or counts[key] < 0):
            raise ValueError("invalid counter " + key)
    for key in ("total", "confirmed", "unconfirmed"):
        if key not in counts:
            raise ValueError("missing counter " + key)
    # WordPress pending confirmations are excluded from the visible total;
    # do not sum these buckets or equate a confirmed count with inbox delivery.
    return {key: counts.get(key) for key in COUNTER_KEYS}


def compare_snapshots(previous, current):
    older = validate_snapshot(previous)
    newer = validate_snapshot(current)
    if _instant(current["as_of"]) <= _instant(previous["as_of"]):
        raise ValueError("non-increasing timestamps")
    delta = {k: newer[k] - older[k] for k in ("total", "confirmed", "unconfirmed")}
    grew = delta["confirmed"] > 0
    return {
        "previous_at": previous["as_of"], "current_at": current["as_of"],
        "delta": delta,
        "current_imported_last_24h": newer["imported_last_24h"],
        "interpretation": ("CONFIRMED_COUNTER_GREW_ORIGIN_NOT_ESTABLISHED" if grew else
                           "COUNTER_CHANGED_OR_STABLE_NO_EVENT_INFERENCE"),
        "import_is_signup_proof": False,
        "confirmed_signup_events_verified": None,
        "email_reachable_verified": None,
        "delivered_welcome_verified": None,
        "paid_conversions_verified": None,
        "release_gate": "HOLD_ALL_UNSENT",
    }


def admitted_confirmed_signups(events):
    """Require authoritative native evidence, not changes in aggregate counters.

    Caller must obtain consent and status evidence independently and must use
    a secret-keyed HMAC digest for opaque ID. This function never creates IDs.
    """
    accepted = {}
    rejected = []
    for pos, event in enumerate(events):
        if not isinstance(event, dict) or set(event) - EVENT_KEYS:
            rejected.append(pos); continue
        token = event.get("opaque_subscriber_id")
        event_id = event.get("native_event_id")
        if not isinstance(token, str) or not OPAQUE.fullmatch(token):
            rejected.append(pos); continue
        if not isinstance(event_id, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{8,100}", event_id):
            rejected.append(pos); continue
        if not (event.get("source") == "native_wordpress" and
                event.get("source_verified") is True and
                event.get("consent_evidence") is True and
                event.get("confirmed_status") == "confirmed" and
                event.get("opted_out") is False):
            rejected.append(pos); continue
        try:
            when = _instant(event.get("occurred_at"))
        except ValueError:
            rejected.append(pos); continue
        # An already-verified WordPress account may subscribe with no second click.
        # Consent still must be explicit and native status must be authenticated.
        if token not in accepted or when < accepted[token]:
            accepted[token] = when
    return {"verified_unique_signups": len(accepted), "rejected_positions": rejected,
            "verified_reachable": None,
            "warning": "Eligibility and actual delivery require independent evidence."}


def revenue_per_1000(qualified_sessions, orders):
    """No estimated denominator, click-as-sale, or inferred transaction totals."""
    if type(qualified_sessions) is not int or qualified_sessions <= 0:
        return {"status": "NOT_COMPUTABLE", "reason": "qualified session denominator unavailable"}
    if not isinstance(orders, list) or not orders:
        return {"status": "NOT_COMPUTABLE", "reason": "no authoritative paid order evidence"}
    seen = set()
    net = Decimal("0")
    try:
        for item in orders:
            if not isinstance(item, dict) or not item.get("merchant_verified") or item.get("status") != "settled":
                return {"status": "NOT_COMPUTABLE", "reason": "unverified or unsettled order"}
            ident = item.get("merchant_order_id")
            if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z0-9_-]{8,100}", ident):
                return {"status": "NOT_COMPUTABLE", "reason": "missing opaque order reference"}
            if ident in seen:
                continue
            seen.add(ident)
            gross, fees, refunds = [Decimal(str(item[key])) for key in ("gross", "fees", "refunds")]
            if not all(v.is_finite() and v >= 0 for v in (gross, fees, refunds)):
                raise ValueError("invalid financial amount")
            net += gross - fees - refunds
    except (InvalidOperation, KeyError, ValueError, TypeError):
        return {"status": "NOT_COMPUTABLE", "reason": "invalid financial record"}
    return {"status": "VERIFIED_INPUTS_ONLY", "settled_order_count": len(seen),
            "net_revenue": str(net), "net_revenue_per_1000_sessions": str((net * 1000 / qualified_sessions).quantize(Decimal("0.01")))}
