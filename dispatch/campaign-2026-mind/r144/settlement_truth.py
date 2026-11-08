"""Offline, read-only, fail-closed *audit* of Dispatch acquisition -> realized revenue.

No WordPress/API integration, tracking snippet, subscriber import, email I/O, or merchant call.
Does not authenticate evidence; source references require independent human verification.
No recipient identities, emails, IP addresses or raw UTM URLs permitted as inputs.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
import json
import re
import sys

EVENTS = {"landing", "cta", "signup_attempt", "confirmed_signup", "welcome_received", "guide", "affiliate_click", "paid_order", "settlement"}
PROVIDERS = {
    "confirmed_signup": "native_provider_confirmed_subscription",
    "welcome_received": "authorized_received_welcome",
    "paid_order": "independent_order_report",
    "settlement": "independent_payment_or_affiliate_settlement",
}
REVENUE_EVENTS = {"paid_order", "settlement"}
MANDATORY = {"id", "kind", "ts", "journey", "evidence_ref"}
PROHIBITED = {"email", "phone", "name", "ip", "ip_address", "subscriber_id", "recipient", "cookie", "user_agent", "raw_url", "url"}
OPAQUE = re.compile(r"^[a-zA-Z0-9_-]{4,96}$")
EVIDENCE = re.compile(r"^[a-zA-Z0-9_/#.:-]{10,256}$")
IDENTITY = re.compile(r"(?:[\w.+'-]+@[\w.-]+\.[a-zA-Z]{2,}|(?:\d{1,3}\.){3}\d{1,3})")

class UnsafeLedger(ValueError):
    pass


def _date(s: str) -> datetime:
    if not isinstance(s, str):
        raise UnsafeLedger("time must be ISO8601 string")
    try:
        v = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as err:
        raise UnsafeLedger("invalid ISO8601 time") from err
    if v.tzinfo is None:
        raise UnsafeLedger("timezone required")
    return v.astimezone(timezone.utc)


def _money(v: Any) -> Decimal:
    if not isinstance(v, str) or not re.fullmatch(r"\d{1,10}(?:\.\d{1,2})?", v):
        raise UnsafeLedger("non-negative USD decimal string required")
    try:
        return Decimal(v)
    except InvalidOperation as err:
        raise UnsafeLedger("invalid amount") from err


def _safe(obj: Any) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in PROHIBITED:
                raise UnsafeLedger("personally identifying or raw-tracking field prohibited")
            _safe(v)
    elif isinstance(obj, list):
        for v in obj: _safe(v)
    elif isinstance(obj, str):
        if IDENTITY.search(obj):
            raise UnsafeLedger("suspected email or IP prohibited")


def evaluate(ledger: dict[str, Any], asof: str) -> dict[str, Any]:
    _safe(ledger)
    now = _date(asof)
    items = ledger.get("events", [])
    if not isinstance(items, list):
        raise UnsafeLedger("events must be list")
    unique, by_journey, errors = {}, defaultdict(list), []
    for e in items:
        if not isinstance(e, dict) or not MANDATORY <= set(e):
            errors.append("invalid_event_schema")
            continue
        if e["kind"] not in EVENTS:
            errors.append("unknown_event_kind")
            continue
        if any(not OPAQUE.fullmatch(str(e[k])) for k in ("id", "journey")):
            errors.append("nonopaque_identifier")
            continue
        if e["id"] in unique:
            if unique[e["id"]] != e: errors.append("conflicting_duplicate_event_id")
            continue
        if not EVIDENCE.fullmatch(str(e["evidence_ref"])):
            errors.append("missing_verifiable_source_reference")
            continue
        try: t = _date(e["ts"])
        except UnsafeLedger:
            errors.append("invalid_time")
            continue
        if t > now:
            errors.append("future_event")
            continue
        if e["kind"] in PROVIDERS:
            if e.get("evidence_type") != PROVIDERS[e["kind"]]:
                errors.append("unsupported_" + e["kind"] + "_evidence")
                continue
        if e["kind"] == "landing":
            if e.get("human_evidence_type") != "reviewed_bot_filtered_session_export":
                errors.append("human_session_not_independently_reviewed")
                continue
            if not OPAQUE.fullmatch(str(e.get("asset_id", ""))):
                errors.append("missing_grok_asset_id")
                continue
            if e.get("utm_source") not in ("youtube", "tiktok", "instagram", "facebook", "pinterest", "x", "bluesky") or e.get("utm_medium") != "organic_social":
                errors.append("invalid_social_source")
                continue
            if e.get("utm_content") != e["asset_id"] or not re.fullmatch(r"[a-z_]+_pilot_2026_11", str(e.get("utm_campaign", ""))):
                errors.append("invalid_asset_attribution")
                continue
        if e["kind"] in REVENUE_EVENTS:
            if not OPAQUE.fullmatch(str(e.get("order_key", ""))):
                errors.append("missing_opaque_order_key")
                continue
        if e["kind"] == "settlement":
            try:
                for amount in ("gross_usd", "fees_usd", "refunds_usd"): _money(e.get(amount))
                if _money(e["fees_usd"]) + _money(e["refunds_usd"]) > _money(e["gross_usd"]):
                    raise UnsafeLedger("net negative amount")
            except UnsafeLedger:
                errors.append("unverifiable_settlement_amount")
                continue
        unique[e["id"]] = e
        by_journey[e["journey"]].append((t, e))
    for lst in by_journey.values(): lst.sort(key=lambda x: x[0])
    coverage = ledger.get("coverage", {})
    if not isinstance(coverage, dict): coverage = {}
    complete = all(coverage.get(k, {}).get("status") == "independently_reconciled" and EVIDENCE.fullmatch(str(coverage.get(k, {}).get("evidence_ref", ""))) for k in ("qualified_session_feed", "orders_feed", "settlements_feed"))
    snapshots = {}
    for days in (7, 30):
        sessions, paid_orders, confirmed, cta, settled, paid = set(), set(), set(), set(), set(), Decimal("0.00")
        counted_order_keys = set()
        cutoff = now - timedelta(days=days)
        for journey, seq in by_journey.items():
            starts = [(t, e) for t, e in seq if e["kind"] == "landing" and cutoff <= t <= now]
            if not starts: continue
            t0 = starts[0][0]
            sessions.add(journey)
            allowed = [(t, e) for t, e in seq if t >= t0]
            if any(e["kind"] == "cta" for t, e in allowed): cta.add(journey)
            if any(e["kind"] == "confirmed_signup" for t, e in allowed): confirmed.add(journey)
            orders = {e["order_key"] for t, e in allowed if e["kind"] == "paid_order"}
            for key in orders:
                # Across multiple sessions, a settled order must only be credited once.
                settlements = [e for t, e in allowed if e["kind"] == "settlement" and e["order_key"] == key]
                if len(settlements) != 1 or key in counted_order_keys:
                    if len(settlements) > 1: errors.append("duplicate_settlement_order")
                    continue
                e = settlements[0]
                counted_order_keys.add(key)
                paid += _money(e["gross_usd"]) - _money(e["fees_usd"]) - _money(e["refunds_usd"])
                paid_orders.add(key)
                settled.add(journey)
        snapshots[str(days)] = {
            "qualified_human_sessions": len(sessions) if complete else None,
            "cta_journeys": len(cta) if complete else None,
            "confirmed_signup_journeys": len(confirmed) if complete and coverage.get("native_consent_feed", {}).get("status") == "independently_reconciled" else None,
            "independently_settled_orders": len(paid_orders) if complete else None,
            "net_realized_usd": str(paid.quantize(Decimal("0.01"))) if complete else None,
            "net_usd_per_1000_qualified_human_sessions": str((paid * Decimal(1000) / len(sessions)).quantize(Decimal("0.01"))) if complete and sessions else None,
            "tiny_sample_warning": len(sessions) < 100 if complete else None,
        }
    # Any malformed or conflicting evidence poisons an entire report. Never compute
    # a reassuring but false zero after rejecting a purchase or landing record.
    if errors:
        complete = False
        for c in snapshots.values():
            for field in c: c[field] = None
    return {"scope": "OFFLINE_AUDIT_NOT_A_LIVE_MEASUREMENT", "asof_utc": now.isoformat(), "input_events": len(items), "accepted_events": len(unique), "rejected_codes": sorted(set(errors)), "feed_coverage_independently_attested": complete, "cohorts": snapshots, "interpretation": "All values require independent validation of cited reports; null is unknown, not zero. No public-event client instrumentation."}


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python settlement_truth.py AUDIT_INPUT.json ASOF_ISO8601", file=sys.stderr)
        return 2
    raw = Path(sys.argv[1]).read_text(encoding="utf-8")
    try:
        print(json.dumps(evaluate(json.loads(raw), sys.argv[2]), indent=2))
    except (UnsafeLedger, json.JSONDecodeError) as e:
        print("FAIL_CLOSED: " + str(e), file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__": raise SystemExit(main())
