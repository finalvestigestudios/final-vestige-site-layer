"""Read-only, privacy-safe proof reducer. Never sends, attributes guessed sales or authorizes a campaign."""
from __future__ import annotations
from datetime import date
from decimal import Decimal
import re

ALLOWED_SOURCES = {"analytics_audited_aggregate", "merchant_paid_settlement", "first_party_paid_order"}
KEYS = {"window_days", "as_of", "source_sessions", "paid_transactions", "refunds_complete", "fees_complete"}
PRIVATE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?:email|password|subscriber_id|token|cookie|secret|api_key)", re.I)


def _check_string(value, label):
    if not isinstance(value, str) or not value.strip() or PRIVATE.search(value):
        raise ValueError(f"Invalid, empty or private {label}")
    return value


def _evidence(entry, kind):
    if not isinstance(entry, dict):
        raise ValueError("Evidence must be an object")
    if entry.get("kind") != kind:
        raise ValueError("Evidence source kind does not match required independent authority")
    _check_string(entry.get("proof_ref"), "proof_ref")


def _cents(x, label):
    if isinstance(x, bool) or not isinstance(x, int) or x < 0:
        raise ValueError(f"{label} must be a nonnegative integer in cents")
    return x


def _dated(d, now, days):
    try:
        when = date.fromisoformat(d)
    except (ValueError, TypeError):
        raise ValueError("Invalid ISO event date") from None
    if not (0 <= (now - when).days < days):
        raise ValueError("Event outside declared window")


def reduce_proofs(payload):
    """Return an evidence-bound rollup. HOLD always; no payable sales inferred from upstream events."""
    if not isinstance(payload, dict) or set(payload) != KEYS:
        raise ValueError("Unexpected/missing top-level data")
    days = payload["window_days"]
    if days not in (7, 30) or isinstance(days, bool):
        raise ValueError("Only fixed 7/30-day windows are supported")
    try:
        now = date.fromisoformat(payload["as_of"])
    except (ValueError, TypeError):
        raise ValueError("Invalid as_of") from None
    sessions = payload["source_sessions"]
    orders = payload["paid_transactions"]
    if not isinstance(sessions, list) or not isinstance(orders, list):
        raise ValueError("Sessions and transactions must be arrays")
    warnings = []
    total_sessions, paid_cents = 0, 0
    assets, orders_seen = set(), set()
    for row in sessions:
        if not isinstance(row, dict) or set(row) != {"date", "asset_id", "utm_campaign", "qualified_human_sessions", "source"}:
            raise ValueError("Invalid audited session row schema")
        _dated(row["date"], now, days)
        asset = _check_string(row["asset_id"], "asset_id")
        campaign = _check_string(row["utm_campaign"], "utm_campaign")
        pair = (asset, campaign, row["date"])
        if pair in assets:
            raise ValueError("Duplicate session asset/day cohort")
        assets.add(pair)
        _evidence(row["source"], "analytics_audited_aggregate")
        total_sessions += _cents(row["qualified_human_sessions"], "qualified_human_sessions")
    for order in orders:
        if not isinstance(order, dict) or set(order) != {"date", "order_ref", "asset_id", "utm_campaign", "currency", "paid_commission_cents", "refund_cents", "fee_cents", "source"}:
            raise ValueError("Invalid paid order schema")
        _dated(order["date"], now, days)
        order_ref = _check_string(order["order_ref"], "order_ref")
        if order_ref in orders_seen:
            raise ValueError("Duplicate paid transaction")
        orders_seen.add(order_ref)
        _check_string(order["asset_id"], "asset_id")
        _check_string(order["utm_campaign"], "utm_campaign")
        if order["currency"] != "USD":
            raise ValueError("Currency must be explicit USD; no assumed FX conversions")
        kind = order["source"].get("kind") if isinstance(order["source"], dict) else None
        if kind not in ("merchant_paid_settlement", "first_party_paid_order"):
            raise ValueError("Click/checkout/pending-order evidence does not establish paid revenue")
        _evidence(order["source"], kind)
        gross = _cents(order["paid_commission_cents"], "paid_commission_cents")
        refund = _cents(order["refund_cents"], "refund_cents")
        fee = _cents(order["fee_cents"], "fee_cents")
        if refund > gross:
            raise ValueError("Refund cannot exceed recorded paid commission")
        paid_cents += gross - refund - fee
    if not payload["refunds_complete"] or not payload["fees_complete"]:
        warnings.append("Refund and fee evidence incomplete")
    if not sessions:
        warnings.append("No independently audited qualified-human session denominator")
    if not orders:
        warnings.append("No independently reported paid settlement evidence")
    if sessions and orders:
        known = {(r["asset_id"], r["utm_campaign"]) for r in sessions}
        if any((o["asset_id"], o["utm_campaign"]) not in known for o in orders):
            warnings.append("Paid order cannot be joined to a verified source campaign")
    eligible = not warnings and total_sessions > 0
    # Never treat an empty or unaudited partner export as proof of zero paid sales.
    net = str(Decimal(paid_cents) / 100) if eligible else None
    per_thousand = str((Decimal(paid_cents) * 10 / Decimal(total_sessions)).quantize(Decimal("0.01"))) if eligible else None
    return {"release": "HOLD_UNSENT", "window_days": days, "as_of": now.isoformat(),
            "qualified_sessions": total_sessions if sessions else None,
            "paid_orders": len(orders) if orders else None,
            "net_usd": net, "net_usd_per_1000_qualified_sessions": per_thousand,
            "commercial_kpi_status": "EVIDENCE_BOUND" if eligible else "NOT_COMPUTABLE",
            "warnings": warnings}
