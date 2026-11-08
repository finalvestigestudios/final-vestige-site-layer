"""Offline evidence contract for Dispatch. Never publishes, sends, or reads subscriber PII.

Only anonymized synthetic records belong in source control. Real provider identifiers
must remain in the authorized private provider system and must not be committed.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qs, urlsplit
import re

ALLOWED_KINDS = {"provider_confirmed_transition", "attempt", "gift_visible", "reader_follow", "welcome_configured", "welcome_receipt"}
ATTRIBUTION_PARTS = {"utm_source", "utm_medium", "utm_campaign", "utm_content"}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{1,79}$")


def _stamp(raw):
    if not isinstance(raw, str) or not raw:
        raise ValueError("timestamp missing")
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid timestamp") from exc
    if value.tzinfo is None:
        raise ValueError("timestamp must have timezone")
    return value.astimezone(timezone.utc)


def classify_subscription_counts(snapshot: dict) -> dict:
    """Display distinct, NONADDITIVE provider counters, not a recipient list."""
    keys = ("total", "confirmed", "unconfirmed", "suppressed", "wpcom_followers", "email_followers")
    for key in keys:
        v = snapshot.get(key)
        if v is not None and (type(v) is not int or v < 0):
            raise ValueError(f"invalid {key}")
    return {
        "reported": {k: snapshot.get(k) for k in keys},
        "recipient_eligible_count": None,
        "recipient_eligible_status": "UNKNOWN_REQUIRES_PROVIDER_ELIGIBILITY_EVIDENCE",
        "do_not_sum": True,
    }


def summarize_confirmed_signup(records: list[dict]) -> dict:
    """Counts only authenticatable transition-shaped inputs, never browser success.

    This is an OFFLINE STRUCTURAL CHECK; callers must separately validate that
    evidence references genuinely originate from a provider-authorized read.
    """
    seen = set()
    count = 0
    rejected = Counter()
    for record in records:
        kind = record.get("kind")
        if kind not in ALLOWED_KINDS:
            rejected["unrecognized"] += 1
            continue
        if kind != "provider_confirmed_transition":
            rejected[kind] += 1
            continue
        if record.get("provider") != "jetpack" or record.get("origin") != "authenticated_provider_read":
            rejected["missing_provider_proof"] += 1
            continue
        if record.get("previous_status") not in ("pending", "absent") or record.get("current_status") != "confirmed":
            rejected["not_new_confirmation"] += 1
            continue
        key = record.get("private_ephemeral_key")
        proof = record.get("provider_proof_ref")
        if not (isinstance(key, str) and key and isinstance(proof, str) and proof.startswith("provider-proof:")):
            rejected["non_deduplicable_proof"] += 1
            continue
        try:
            _stamp(record.get("confirmed_at"))
        except ValueError:
            rejected["bad_confirmation_time"] += 1
            continue
        if key in seen:
            rejected["duplicate"] += 1
            continue
        seen.add(key)
        count += 1
    return {
        "structurally_supported_new_confirmations": count,
        "actual_provider_confirmations_verified_by_this_code": False,
        "rejection_reasons": dict(sorted(rejected.items())),
        "identifiers_emitted": False,
    }


def validate_owned_utm(raw_url: str) -> dict:
    """For future OWNED LANDING page links. Reject embedded PII and attribution spoofing."""
    parsed = urlsplit(raw_url)
    if parsed.scheme != "https" or parsed.hostname not in ("finalvestige.com", "www.finalvestige.com"):
        raise ValueError("only HTTPS owned Final Vestige destinations")
    if parsed.username or parsed.password or parsed.fragment:
        raise ValueError("credentials/fragments are not allowed")
    params = parse_qs(parsed.query, keep_blank_values=True)
    if set(params) != ATTRIBUTION_PARTS or any(len(v) != 1 for v in params.values()):
        raise ValueError("require exactly four unique UTM parameters")
    for key, vals in params.items():
        if not ID_PATTERN.fullmatch(vals[0]):
            raise ValueError(f"noncompliant or potentially identifying {key}")
    if params["utm_medium"] != ["email"] or params["utm_source"] != ["dispatch"]:
        raise ValueError("incorrect Dispatch source/medium")
    return {"path": parsed.path, "attribution": {k: params[k][0] for k in sorted(ATTRIBUTION_PARTS)}}


def _money(raw):
    if isinstance(raw, float) or isinstance(raw, bool) or raw is None:
        raise ValueError("use exact signed decimal strings")
    try:
        result = Decimal(str(raw))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid exact currency") from exc
    if not result.is_finite():
        raise ValueError("nonfinite currency")
    return result


def revenue_per_1000(qualified_sessions, settlement_rows, attribution_verified: bool):
    """Sales must come from reconciled paid-order/merchant statements, not clicks."""
    if not attribution_verified or type(qualified_sessions) is not int or qualified_sessions <= 0:
        return {"status": "NOT_COMPUTABLE", "reason": "qualified sessions or attribution unverified"}
    if not settlement_rows:
        return {"status": "NOT_COMPUTABLE", "reason": "no independently reconciled settlement evidence"}
    seen = set()
    net = Decimal("0")
    for row in settlement_rows:
        if row.get("source") not in ("merchant_authenticated_statement", "fv_paid_order_reconciliation") or row.get("status") != "settled":
            return {"status": "NOT_COMPUTABLE", "reason": "unverified or unsettled order"}
        uid = row.get("transaction_ref")
        if not isinstance(uid, str) or not uid or uid in seen:
            return {"status": "NOT_COMPUTABLE", "reason": "missing or duplicate transaction reference"}
        seen.add(uid)
        try:
            gross = _money(row["gross_commission_or_sale"])
            refund = _money(row["refunded_amount"])
            fees = _money(row["fees"])
        except (KeyError, ValueError):
            return {"status": "NOT_COMPUTABLE", "reason": "incomplete exact settlement numbers"}
        net += gross - refund - fees
    return {"status": "COMPUTABLE_FOR_VERIFIED_INPUTS_ONLY", "net_revenue": str(net),
            "net_per_1000_qualified_sessions": str((net * 1000) / Decimal(qualified_sessions)),
            "settled_transaction_count": len(seen)}


def release_decision(evidence: dict) -> dict:
    """Never authorizes sending. This supports review, not founder approval."""
    req = ("named_affiliate_acceptance", "email_channel_permission", "account_issued_earning_url",
           "approved_live_warmup_guide", "current_checkout_terms_checked",
           "native_jetpack_preview_checked", "rendered_unsubscribe_verified",
           "publisher_physical_address_verified", "actual_eligible_audience_verified",
           "authorized_welcome_receipt_verified")
    missing = [k for k in req if evidence.get(k) is not True]
    return {"all_six": "HOLD_UNSENT", "issues_03_05": "HOLD_MERCHANT",
            "missing_evidence": missing, "founder_final_campaign_approval_required": True,
            "send_authorized": False}
