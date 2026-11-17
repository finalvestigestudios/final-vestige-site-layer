"""Offline, read-only reconciliation of aggregate Jetpack newsletter evidence.

This never reads subscriber rows, sends mail, or generates production events.
No dashboard number is a confirmed_signup event or an eligible inbox count.
"""
import json
import pathlib
import re
import sys

ALLOWED_KEYS = {"snapshot_at_utc", "site", "source", "newsletter", "followers", "fieldbook", "acceptance_evidence", "release"}
SENSITIVE = re.compile(r"(^|_)(email_address|subscriber_email|recipient_email|first_name|last_name|subscriber_token|email_hash|ip_address|phone_number)(_|$)", re.I)
EMAILISH = re.compile(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", re.I)


def _reject_sensitive(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if SENSITIVE.search(key):
                raise ValueError("private subscriber attribute must not enter public QA")
            _reject_sensitive(value)
    elif isinstance(obj, list):
        for value in obj:
            _reject_sensitive(value)
    elif isinstance(obj, str) and EMAILISH.search(obj):
        raise ValueError("private email address must not enter public QA")


def assess(data):
    if not isinstance(data, dict) or set(data) != ALLOWED_KEYS:
        raise ValueError("invalid source schema")
    _reject_sensitive(data)
    if data["site"] != "https://finalvestige.com" or data["release"] != "HOLD_UNSENT":
        raise ValueError("wrong site or unsafe release state")
    n, f, book, a = (data[k] for k in ("newsletter", "followers", "fieldbook", "acceptance_evidence"))
    for field in ("total", "confirmed", "unconfirmed", "suppressed", "paid"):
        if type(n.get(field)) is not int or n[field] < 0:
            raise ValueError("newsletter count invalid")
    for field in ("email", "wpcom", "comment"):
        if type(f.get(field)) is not int or f[field] < 0:
            raise ValueError("follower count invalid")
    if type(f.get("partial")) is not bool or type(n.get("new_post_auto_email")) is not bool:
        raise ValueError("source state missing")
    if not isinstance(n.get("recent_five_post_sends"), list) or len(n["recent_five_post_sends"]) != 5:
        raise ValueError("recent post send window missing")
    if book.get("media_source_url") != book.get("configured_welcome_pdf"):
        raise ValueError("configured welcome points to other media")
    if book.get("media_mime") != "application/pdf" or type(book.get("media_size_bytes")) is not int or book["media_size_bytes"] <= 0:
        raise ValueError("Fieldbook media listing missing")
    if book.get("actual_received_welcome") is not None or book.get("actual_pdf_received_or_downloaded") is not None:
        raise ValueError("a live receipt claim requires a separate private witness")
    if not isinstance(a, dict) or not a or any(v is not None for v in a.values()):
        raise ValueError("unverified release attestations cannot be asserted")
    if n.get("enabled") is not True or n.get("can_send_platform") is not True:
        raise ValueError("platform status mismatch")
    return {
        "mode": "READ_ONLY_AGGREGATE_DIAGNOSTIC",
        "release": "HOLD_UNSENT",
        "snapshot_at_utc": data["snapshot_at_utc"],
        "newsletter_counts_not_a_partition": n["total"] != n["confirmed"] + n["unconfirmed"],
        "newsletter_total": n["total"],
        "newsletter_confirmed_aggregate": n["confirmed"],
        "newsletter_unconfirmed_aggregate": n["unconfirmed"],
        "stats_email_followers": f["email"],
        "stats_reader_followers": f["wpcom"],
        "stats_partial": f["partial"],
        "platform_capable_does_not_mean_permission": True,
        "media_library_pdf_exists_not_inbox_receipt": True,
        "eligible_distinct_inboxes": None,
        "confirmed_signup_events": None,
        "actual_welcome_deliveries": None,
        "publisher_address_and_optout_proven": False,
        "named_merchant_email_permission_proven": False,
        "paid_orders_verified": None,
        "qualified_human_sessions_verified": None,
        "realized_net_revenue_per_1000_human_sessions": None,
        "send_allowed": False
    }


def main():
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).with_name("consent_snapshot.json")
    print(json.dumps(assess(json.loads(path.read_text(encoding="utf-8"))), indent=2))

if __name__ == "__main__":
    main()
