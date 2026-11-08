#!/usr/bin/env python3
"""Read-only Jetpack send-provenance audit. No network, CMS actions, or send capability.

Important: WordPress recent_sends is a bounded feed, not a historical campaign ledger.
This software may verify that returned rows show no dispatch, NEVER infer no mail
was sent anywhere or that a confirmed subscriber count is deliverable.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOP_KEYS = {
    "schema_version", "mode", "campaign_status", "snapshot_as_of_utc",
    "owner_issue", "companion_issue", "original_master_pr", "stack_parent_pr",
    "site", "newsletter", "newsletter_counters", "follower_counters",
    "deliverable_audience", "recent_send_records", "commercial_gates",
    "shared_gates",
}
NEWSLETTER_KEYS = {
    "enabled", "site_can_send", "email_new_posts_by_default", "email_content_format",
    "reply_to", "welcome_52_page_fieldbook_configured", "actual_welcome_receipt_verified",
}
COUNTER_KEYS = {"total", "confirmed", "unconfirmed", "suppressed"}
FOLLOWER_KEYS = {"total", "email", "wpcom", "partial"}
ROW_KEYS = {"post_id", "title", "scheduled_for", "dispatched_at", "status", "reason", "counts"}
ROW_COUNT_KEYS = {"recipients", "sent", "bounced", "blocked_by_recipient"}
COMMERCIAL_KEYS = {
    "zen12_email_permission", "total_focus_email_permission",
    "approved_published_guides", "approved_affiliate_links",
    "current_price_refund_verified",
}
SHARED_KEYS = {
    "final_founder_send_approval", "founder_postal_address_verified",
    "delivered_unsubscribe_verified", "real_received_jetpack_email_verified",
    "email_eligible_audience_verified",
}
EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}")
TOKEN = re.compile(r"(?i)(?:https?://[^\s]+[?&](?:token|key|email|auth|aff_id)=)")
NEVER_SENT = "never_sent_opted_out"


def exact_keys(obj, expected, where):
    if not isinstance(obj, dict) or set(obj) != expected:
        raise ValueError("Unsupported or extra fields in " + where)


def iso_time(value):
    if not isinstance(value, str):
        raise ValueError("Invalid timestamp")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid timestamp") from exc
    if dt.tzinfo is None:
        raise ValueError("Offset is required")
    return dt


def count(value):
    if type(value) is not int or value < 0:
        raise ValueError("Counts must be nonnegative integers")


def validate(snapshot):
    exact_keys(snapshot, TOP_KEYS, "snapshot")
    if snapshot["schema_version"] != "r82-2026-11-02-v1":
        raise ValueError("Unsupported snapshot schema")
    if snapshot["mode"] != "READ_ONLY_AGGREGATE" or snapshot["campaign_status"] != "HOLD_UNSENT":
        raise ValueError("A snapshot cannot authorize a campaign")
    if snapshot["site"] != "https://finalvestige.com":
        raise ValueError("Unexpected site")
    if [snapshot[k] for k in ("owner_issue", "companion_issue", "original_master_pr", "stack_parent_pr")] != [174, 171, 175, 721]:
        raise ValueError("Source identity mismatch")
    observed = iso_time(snapshot["snapshot_as_of_utc"])
    exact_keys(snapshot["newsletter"], NEWSLETTER_KEYS, "newsletter")
    n = snapshot["newsletter"]
    for k in ("enabled", "site_can_send", "email_new_posts_by_default",
              "welcome_52_page_fieldbook_configured", "actual_welcome_receipt_verified"):
        if type(n[k]) is not bool:
            raise ValueError("Newsletter flag type")
    if not n["enabled"] or n["email_new_posts_by_default"] or n["email_content_format"] != "excerpt" or n["reply_to"] != "no-reply":
        raise ValueError("Do not silently normalize newsletter setting changes")
    if n["actual_welcome_receipt_verified"]:
        raise ValueError("No valid received-welcome evidence in this snapshot")
    exact_keys(snapshot["newsletter_counters"], COUNTER_KEYS, "newsletter_counters")
    exact_keys(snapshot["follower_counters"], FOLLOWER_KEYS, "follower_counters")
    for k in COUNTER_KEYS:
        count(snapshot["newsletter_counters"][k])
    for k in ("total", "email", "wpcom"):
        count(snapshot["follower_counters"][k])
    if type(snapshot["follower_counters"]["partial"]) is not bool:
        raise ValueError("Invalid partial flag")
    if snapshot["deliverable_audience"] != "UNKNOWN":
        raise ValueError("No verified eligible-audience count")
    # Contradictory classifications are evidence to investigate, not sum.
    if snapshot["newsletter_counters"] != {"total": 2, "confirmed": 2, "unconfirmed": 2, "suppressed": 0}:
        raise ValueError("R82 counts changed: take a new separately dated snapshot")
    if snapshot["follower_counters"] != {"total": 2, "email": 0, "wpcom": 2, "partial": False}:
        raise ValueError("R82 follower classifications changed: re-verify")
    exact_keys(snapshot["commercial_gates"], COMMERCIAL_KEYS, "commercial_gates")
    exact_keys(snapshot["shared_gates"], SHARED_KEYS, "shared_gates")
    for gates in (snapshot["commercial_gates"], snapshot["shared_gates"]):
        if not all(value is False for value in gates.values()):
            raise ValueError("External evidence cannot be approved by editing this snapshot")
    rows = snapshot["recent_send_records"]
    if not isinstance(rows, list) or len(rows) != 5:
        raise ValueError("This proof is scoped to exactly five returned recent records")
    seen = set()
    prev = None
    for row in rows:
        exact_keys(row, ROW_KEYS, "record")
        count(row["post_id"])
        if row["post_id"] in seen:
            raise ValueError("Duplicate record")
        seen.add(row["post_id"])
        if not isinstance(row["title"], str) or not 12 <= len(row["title"]) <= 180:
            raise ValueError("Invalid post title")
        if EMAIL.search(row["title"]) or TOKEN.search(row["title"]):
            raise ValueError("Recipient, token or tracking data in title")
        ts = iso_time(row["scheduled_for"])
        if ts > observed:
            raise ValueError("Record timestamp after observation")
        if prev is not None and ts > prev:
            raise ValueError("Feed must remain in the actual returned newest-first order")
        prev = ts
        if row["status"] != NEVER_SENT or row["dispatched_at"] is not None:
            raise ValueError("Changed dispatch status requires new human reconciliation")
        if row["reason"] != "send_subscription flag is false":
            raise ValueError("Unverified opt-out cause")
        exact_keys(row["counts"], ROW_COUNT_KEYS, "record counts")
        if any(v is not None for v in row["counts"].values()):
            raise ValueError("Do not coerce unknown deliveries or recipients to zero")
    # No PII/tokens even in unexpected nested structures; exact keys above prevent
    # a caller from smuggling in subscriber records or raw email MIME.
    raw = json.dumps(snapshot, ensure_ascii=False)
    if EMAIL.search(raw) or TOKEN.search(raw):
        raise ValueError("No recipient addresses or private tracking tokens permitted")
    return True


def summarize(snapshot):
    validate(snapshot)
    return {
        "status": "HOLD_UNSENT",
        "source": "authenticated WordPress Jetpack newsletter status — bounded recent_sends feed",
        "as_of_utc": snapshot["snapshot_as_of_utc"],
        "returned_recent_records": len(snapshot["recent_send_records"]),
        "records_unequivocally_never_sent_opted_out": len(snapshot["recent_send_records"]),
        "dispatched_in_these_returned_records": 0,
        "all_time_sends": "UNKNOWN — bounded feed, not lifetime evidence",
        "actual_email_eligible_recipients": "UNKNOWN — provider classification conflict",
        "site_can_send_means_delivery": False,
        "configured_welcome_means_received": False,
        "merchant_email_permissions": "UNVERIFIED",
        "publisher_address_unsubscribe": "UNVERIFIED",
        "full_mime_delivery_and_rendering": "UNVERIFIED",
        "release": "NO_SEND_NO_TEST_SEND_NO_PUBLISH_NO_WORDPRESS_CHANGES",
    }


def main():
    parser = argparse.ArgumentParser(description="Offline read-only Jetpack evidence inspector")
    parser.add_argument("--snapshot", default=str(ROOT / "SNAPSHOT.json"))
    args = parser.parse_args()
    source = Path(args.snapshot)
    if source.stat().st_size > 128_000:
        raise ValueError("Unexpectedly large evidence file")
    data = json.loads(source.read_text(encoding="utf-8"))
    print(json.dumps(summarize(data), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
