"""Read-only, PII-free interpretation of WordPress newsletter aggregates.

Never equate dashboard totals with eligible recipients; never authorizes email.
Source: https://wordpress.com/support/subscribers/ (reviewed 2026-10-26).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

COUNT_KEYS = ("total", "confirmed", "unconfirmed", "suppressed", "paid", "imported_last_24h")


def _counts(raw: object) -> dict[str, int]:
    if not isinstance(raw, dict):
        raise ValueError("subscribers must be a mapping")
    result = {}
    for key in COUNT_KEYS:
        if key not in raw:
            raise ValueError(f"missing aggregate: {key}")
        value = raw[key]
        if type(value) is not int or value < 0:
            raise ValueError(f"invalid aggregate: {key}")
        result[key] = value
    return result


def interpret(snapshot: object) -> dict[str, object]:
    """Return an allowlisted report only; no raw identifiers or addresses."""
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be a mapping")
    counts = _counts(snapshot.get("subscribers"))
    settings = snapshot.get("settings")
    if not isinstance(settings, dict):
        raise ValueError("settings must be a mapping")

    for key in ("subscriptions", "email_new_posts_by_default"):
        if type(settings.get(key)) is not bool:
            raise ValueError(f"missing or invalid setting: {key}")
    if settings.get("email_content_format") not in ("full", "excerpt"):
        raise ValueError("missing or invalid setting: email_content_format")
    sends = snapshot.get("recent_sends")
    if not isinstance(sends, list):
        raise ValueError("recent_sends must be an array")

    # WordPress: unconfirmed records are NOT included in total subscribers.
    # Therefore 2 total / 2 confirmed / 2 unconfirmed is not, by itself,
    # contradictory. It still cannot prove actual email eligibility.
    status = "CONSISTENT_WITH_DOCUMENTED_WP_BUCKETS"
    if counts["confirmed"] > counts["total"]:
        status = "REQUIRES_PRIVATE_RECONCILIATION"

    return {
        "source": "wordpress.com/support/subscribers/ (reviewed 2026-10-26)",
        "total_reported": counts["total"],
        "confirmed_reported": counts["confirmed"],
        "unconfirmed_not_in_total": counts["unconfirmed"],
        "counter_interpretation": status,
        "maximum_possible_confirmed_email_recipients": counts["confirmed"],
        "actual_email_eligible_recipients": None,
        "private_opt_in_bounce_pause_audit_required": True,
        "new_post_auto_email_enabled": settings["email_new_posts_by_default"],
        "newsletter_enabled": settings["subscriptions"],
        "configured_email_format": settings["email_content_format"],
        "no_recent_sends_reported": len(sends) == 0,
        "full_received_email_verified": False,
        "real_unsubscribe_and_sender_postal_verified": False,
        "founder_send_approval_verified": False,
        "release_decision": "HOLD_UNSENT",
        "reason": "Aggregate counts do not prove opt-in, email reachability, legal footer, or permission to send.",
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        print("usage: python audience_guard.py AGGREGATE_SNAPSHOT.json", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
        result = interpret(data)
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError):
        print("AUDIT_BLOCKED: invalid or inaccessible aggregate snapshot", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
