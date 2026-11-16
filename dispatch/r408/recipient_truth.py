"""Offline, privacy-preserving reconciliation of WordPress/Jetpack audience snapshots.

Inputs are read-only aggregates. It NEVER sends mail, writes to WordPress,
authenticates recipients or proves email delivery. Only authoritative per-recipient
provider proof (not accepted by this tool) could establish distinct recipients.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SAFE_TOP_KEYS = {"snapshot_id", "as_of_utc", "newsletter", "followers", "proof"}
SAFE_NEWS_KEYS = {"total", "confirmed", "unconfirmed", "suppressed", "paid", "imported_last_24h", "site_can_send", "send_blockers", "email_new_posts_by_default", "subscriptions", "recent_send_statuses"}
SAFE_FOLLOW_KEYS = {"wpcom", "email", "comment", "total", "partial"}
SAFE_PROOF_KEYS = {"unique_email_eligible", "deduped_confirmed_signup_events", "welcome_received", "fieldbook_received", "publisher_postal_verified", "unsubscribe_rendered_and_operational", "native_non_sending_preview_seen", "inspire3_named_email_authorization", "referred_checkout_verified", "verified_paid_order_evidence", "qualified_human_sessions_evidence"}


def _nonnegative(x: Any) -> bool:
    return type(x) is int and x >= 0


def _fail_unknown(d: dict, allowed: set[str], label: str) -> None:
    unknown = set(d) - allowed
    if unknown:
        raise ValueError(f"{label}: unauthorized fields: {','.join(sorted(unknown))}")


def audit(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return aggregate-only acceptance verdict. Always explicitly non-sending."""
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be an object")
    _fail_unknown(snapshot, SAFE_TOP_KEYS, "snapshot")
    if set(snapshot) != SAFE_TOP_KEYS:
        raise ValueError("missing top-level snapshot keys")
    n, f, p = snapshot["newsletter"], snapshot["followers"], snapshot["proof"]
    if not all(isinstance(x, dict) for x in (n, f, p)):
        raise ValueError("newsletter, followers, proof must be objects")
    for data, keys, name in ((n, SAFE_NEWS_KEYS, "newsletter"), (f, SAFE_FOLLOW_KEYS, "followers"), (p, SAFE_PROOF_KEYS, "proof")):
        _fail_unknown(data, keys, name)
        if set(data) != keys:
            raise ValueError(f"{name}: missing fields")
    if not isinstance(snapshot["snapshot_id"], str) or not re.fullmatch(r"wp-readonly-[a-z0-9-]{1,70}", snapshot["snapshot_id"]):
        raise ValueError("invalid or potentially identifying snapshot ID")
    if not isinstance(snapshot["as_of_utc"], str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", snapshot["as_of_utc"]):
        raise ValueError("UTC timestamp required without personal data")
    try:
        datetime.fromisoformat(snapshot["as_of_utc"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid UTC timestamp") from exc
    for k in ("total", "confirmed", "unconfirmed", "suppressed", "paid", "imported_last_24h"):
        if not _nonnegative(n[k]):
            raise ValueError(f"newsletter.{k} must be nonnegative integer")
    for k in ("total", "wpcom", "email", "comment"):
        if not _nonnegative(f[k]):
            raise ValueError(f"followers.{k} must be nonnegative integer")
    for k in ("site_can_send", "email_new_posts_by_default", "subscriptions"):
        if type(n[k]) is not bool:
            raise ValueError(f"newsletter.{k} must be boolean")
    if type(f["partial"]) is not bool or not isinstance(n["send_blockers"], list) or not isinstance(n["recent_send_statuses"], list):
        raise ValueError("malformed status arrays or partial flag")
    if not all(isinstance(x, str) for x in n["send_blockers"]+n["recent_send_statuses"]):
        raise ValueError("redacted status arrays must contain strings")
    for k, val in p.items():
        if k in ("unique_email_eligible", "deduped_confirmed_signup_events"):
            if val is not None and not _nonnegative(val):
                raise ValueError(f"proof.{k}: null or verified integer required")
        elif val is not None and type(val) is not bool:
            raise ValueError(f"proof.{k}: null or bool required")

    blockers = []
    notes = []
    if n["email_new_posts_by_default"]:
        blockers.append("AUTOMATIC_POST_EMAILS_ENABLED_UNEXPECTEDLY")
    if not n["subscriptions"]:
        blockers.append("NEWSLETTER_DISABLED")
    if f["partial"]:
        blockers.append("FOLLOWER_SNAPSHOT_PARTIAL")
    if n["confirmed"] > n["total"]:
        blockers.append("CONFIRMED_EXCEEDS_TOTAL")
    # 'unconfirmed' may share a different reporting universe; never sum it with confirmed.
    if n["confirmed"] + n["unconfirmed"] > n["total"]:
        notes.append("COUNT_UNIVERSES_OVERLAP_OR_DIFFER: do not add totals")
    if f["email"] == 0 and n["confirmed"] > 0:
        notes.append("CONFIRMED_VS_DIRECT_EMAIL_FOLLOWERS_CONFLICT: recipient count unknown")
    if n["site_can_send"]:
        notes.append("PLATFORM_SEND_CAPABILITY_NOT_CAMPAIGN_PERMISSION")
    if p["unique_email_eligible"] is None:
        blockers.append("EMAIL_ELIGIBLE_UNIQUE_UNKNOWN")
    if p["deduped_confirmed_signup_events"] is None:
        blockers.append("CONFIRMED_SIGNUP_EVENTS_NOT_ATTESTED")
    for key, code in (("welcome_received", "WELCOME_RECEIPT_UNPROVEN"),
                      ("fieldbook_received", "FIELDBOOK_RECEIPT_UNPROVEN"),
                      ("publisher_postal_verified", "PUBLISHER_ADDRESS_UNVERIFIED"),
                      ("unsubscribe_rendered_and_operational", "UNSUBSCRIBE_UNVERIFIED"),
                      ("native_non_sending_preview_seen", "NATIVE_JETPACK_PREVIEW_MISSING")):
        if p[key] is not True:
            blockers.append(code)
    commercial = ["inspire3_named_email_authorization", "referred_checkout_verified"]
    for key in commercial:
        if p[key] is not True:
            blockers.append("COMMERCIAL_"+key.upper()+"_MISSING")
    if not p["verified_paid_order_evidence"] or not p["qualified_human_sessions_evidence"]:
        notes.append("NET_REVENUE_PER_1000_QUALIFIED_SESSIONS_NOT_COMPUTABLE")
    return {
        "snapshot_id": snapshot["snapshot_id"],
        "as_of_utc": snapshot["as_of_utc"],
        "status": "HOLD_UNSENT",
        "mail_allowed": False,
        "confirmed_signup_v1": None,  # deliberately NOT an estimate from aggregate counters
        "unique_receivers": p["unique_email_eligible"],
        "net_revenue_per_1000_qualified_sessions": None,
        "counts": {"total": n["total"], "confirmed": n["confirmed"], "unconfirmed": n["unconfirmed"], "follower_wpcom": f["wpcom"], "follower_email": f["email"]},
        "blockers": blockers,
        "notes": notes,
    }


def run(path: str) -> dict[str, Any]:
    return audit(json.loads(Path(path).read_text(encoding="utf-8")))


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Read-only aggregate Jetpack witness. This script NEVER sends mail")
    p.add_argument("snapshot")
    args = p.parse_args()
    print(json.dumps(run(args.snapshot), indent=2))
