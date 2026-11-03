"""Dispatch R96: read-only evidence reconciliation; never authorizes an email.

No network, email, subscriber export, WordPress write, or affiliate link capability.
The bundled JSON snapshot is dated evidence, NOT a live connection.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAMPAIGN = ROOT.parent
REQUIRED_PROOFS = (
    "merchant_email_permission",
    "approved_published_guides",
    "qualified_recipients_reconciled",
    "received_jetpack_message",
    "functional_unsubscribe_in_received_message",
    "publisher_postal_in_received_message",
    "welcome_delivery_receipt",
    "founder_final_approval",
)
EXPECTED_KEYS = {
    "evidence_date", "source", "newsletter_settings", "newsletter_counts",
    "follower_stats", "last_five_delivery_records",
    "unverified_real_world_proofs", "audit_notes",
}
SENSITIVE_KEYS = {
    "subscriber", "subscribers", "subscriber_email", "buyer_name",
    "buyer_email", "mailing_address", "postal_address", "phone",
    "phone_number", "token", "api_key", "recipient_email", "ip_address",
    "order_id", "cookie", "individual_purchases", "email_addresses",
}
EMAIL_PATTERN = re.compile(r"(?i)[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}")


class EvidenceError(ValueError):
    """A snapshot may not be safely interpreted as verified launch evidence."""


def _fail_if_sensitive(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                raise EvidenceError("Private data field prohibited: " + str(key))
            _fail_if_sensitive(item)
    elif isinstance(value, list):
        for item in value:
            _fail_if_sensitive(item)
    elif isinstance(value, str) and EMAIL_PATTERN.search(value):
        raise EvidenceError("Personal email address prohibited in evidence")


def _require(obj, key, expected):
    if type(obj.get(key)) is not type(expected) or obj.get(key) != expected:
        raise EvidenceError(f"Unexpected {key}; captured snapshot must remain evidence, not a release flag")


def inspect(snapshot: dict, manifest: dict) -> dict:
    """Evaluate exactly the captured evidence; fail closed if it drifts."""
    if not isinstance(snapshot, dict) or set(snapshot) != EXPECTED_KEYS:
        raise EvidenceError("Snapshot field contract mismatch")
    _fail_if_sensitive(snapshot)
    if snapshot["source"] != "wordpress_authenticated_read_only":
        raise EvidenceError("Snapshot source does not identify authenticated read-only observation")
    if snapshot["evidence_date"] != "2026-11-03T18:36:42Z":
        raise EvidenceError("Dated evidence may not be silently refreshed")
    settings = snapshot["newsletter_settings"]
    if set(settings) != {
        "subscriptions", "site_can_send", "email_new_posts_by_default", "email_content_format",
        "reply_to", "from_name", "welcome_fieldbook_configured", "welcome_delivered_verified",
    }:
        raise EvidenceError("Newsletter settings field contract changed")
    for key, expected in (
        ("subscriptions", True), ("site_can_send", True),
        ("email_new_posts_by_default", False), ("email_content_format", "excerpt"),
        ("reply_to", "no-reply"), ("from_name", "Final Vestige"),
        ("welcome_fieldbook_configured", True), ("welcome_delivered_verified", False),
    ):
        _require(settings, key, expected)
    counts = snapshot["newsletter_counts"]
    if set(counts) != {"total", "confirmed", "unconfirmed", "suppressed", "paid", "imported_last_24h"}:
        raise EvidenceError("Subscriber counters field contract changed")
    for key, expected in (("total", 2), ("confirmed", 2), ("unconfirmed", 2),
                          ("suppressed", 0), ("paid", 0), ("imported_last_24h", 0)):
        _require(counts, key, expected)
    followers = snapshot["follower_stats"]
    if set(followers) != {"total", "email", "wpcom", "comment", "partial"}:
        raise EvidenceError("Follower stats field contract changed")
    for key, expected in (("total", 2), ("email", 0), ("wpcom", 2),
                          ("comment", 0), ("partial", False)):
        _require(followers, key, expected)
    records = snapshot["last_five_delivery_records"]
    if not isinstance(records, list) or len(records) != 5:
        raise EvidenceError("Expected five sampled native WordPress delivery records")
    ids = [1926, 1924, 1922, 1920, 1917]
    for row, expected_id in zip(records, ids):
        if not isinstance(row, dict) or set(row) != {
            "post_id", "status", "dispatched_at", "recipients"
        }:
            raise EvidenceError("Delivery record field contract changed")
        _require(row, "post_id", expected_id)
        _require(row, "status", "never_sent_opted_out")
        _require(row, "dispatched_at", None)
        _require(row, "recipients", None)
    proofs = snapshot["unverified_real_world_proofs"]
    if set(proofs) != set(REQUIRED_PROOFS):
        raise EvidenceError("Missing or unexpected real-world proof")
    for key in REQUIRED_PROOFS:
        _require(proofs, key, False)
    notes = snapshot["audit_notes"]
    if not isinstance(notes, list) or len(notes) != 4 or any(
        not isinstance(x, str) or not x.strip() for x in notes
    ):
        raise EvidenceError("Four safety caveats required")
    if not isinstance(manifest, dict) or manifest.get("status") != "DRAFT_UNSENT_NO_SCHEDULING":
        raise EvidenceError("Master campaign must remain unsent")
    issues = manifest.get("issues")
    if not isinstance(issues, list) or [x.get("number") for x in issues] != [1, 2, 3, 4, 5, 6]:
        raise EvidenceError("Six ordered master editions required")
    if [x.get("kind") for x in issues] != [
        "editorial", "editorial", "commercial-review-pending", "editorial",
        "commercial-review-pending", "editorial",
    ]:
        raise EvidenceError("Original four-editorial/two-commercial allocation changed")
    if any(x.get("publish_state") != "hold" or x.get("merchant_affiliate_url") is not None
           for x in issues):
        raise EvidenceError("Unexpected campaign link activation or publish state")

    # Important: the API's five recent delivery objects are *non-sends*. This is
    # different from saying that the API returned zero historical records.
    return {
        "captured_at": snapshot["evidence_date"],
        "campaign": "HOLD_UNSENT",
        "commercial_editions": {"03": "HOLD_MERCHANT", "05": "HOLD_MERCHANT"},
        "campaign_issues": 6,
        "observed_recent_record_count": len(records),
        "observed_recent_successful_sends": 0,
        "observed_recent_opted_out_non_sends": len(records),
        "native_email_excerpt_mode": True,
        "welcome_configured_not_delivered": True,
        "subscriber_counts_inconsistent": counts["confirmed"] + counts["unconfirmed"] > counts["total"],
        "follower_stats_email": followers["email"],
        "follower_stats_wordpress_com": followers["wpcom"],
        "verified_email_eligible_recipients": None,
        "received_email_html_verified": False,
        "received_email_plaintext_verified": False,
        "final_vestige_postal_footer_verified": False,
        "functional_unsubscribe_in_received_email_verified": False,
        "founder_send_approval": False,
        "merchant_email_permissions": False,
        "publish_or_send_authorized": False,
    }


def render_text(result: dict) -> str:
    return "\n".join([
        "FINAL VESTIGE DISPATCH / NATIVE SEND-LEDGER EVIDENCE",
        "Captured: " + str(result["captured_at"]) + " (historical snapshot; not a live query)",
        "CAMPAIGN: HOLD_UNSENT — issues 03/05 also HOLD_MERCHANT",
        f"WordPress delivery records observed: {result['observed_recent_record_count']}",
        f"Opted-out / never-sent records: {result['observed_recent_opted_out_non_sends']}",
        f"Successful sends within sampled five records: {result['observed_recent_successful_sends']}",
        "Caution: this does NOT establish historical zero sends beyond the sampled records.",
        "Newsletter counts: total 2, confirmed 2, unconfirmed 2 (non-additive/contradictory).",
        "Follower stats: email 0, WordPress.com 2; actual eligible addresses UNKNOWN.",
        "Jetpack: newsletter enabled; post auto-send OFF; email format EXCERPT.",
        "Welcome Fieldbook configured; receipt UNVERIFIED.",
        "Email preview, publisher postal footer and working unsubscribe UNVERIFIED.",
        "Product-specific affiliate EMAIL permission and buyer guides UNVERIFIED.",
        "No subscriber PII or email addresses stored. No campaign send permitted.",
    ]) + "\n"


def render_html(result: dict) -> str:
    lines = render_text(result).strip().splitlines()
    head = html.escape(lines[0])
    body = "\n".join("<li>" + html.escape(line) + "</li>" for line in lines[1:])
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Dispatch native delivery evidence — HOLD</title>'
        '<style>body{font:1rem/1.6 system-ui,sans-serif;background:#101111;color:#F4EFE6;'
        'max-width:70ch;margin:auto;padding:2rem 1rem}a{color:#E2BB7D}'
        'li{margin:.5rem 0}h1{line-height:1.2}*:focus-visible{outline:3px solid #E2BB7D}'
        '</style></head><body><main><h1>' + head + '</h1>'
        '<p><strong>Review-only. Nothing here authorizes sending.</strong></p><ul>'
        + body + '</ul><p><a href="https://github.com/finalvestigestudios/'
        'final-vestige-site-layer/issues/174">Campaign evidence issue #174</a></p>'
        '</main></body></html>'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only Dispatch evidence review")
    parser.add_argument("--html", action="store_true", help="Print static accessible HTML to stdout")
    args = parser.parse_args()
    snap = json.loads((ROOT / "wordpress_2026-11-03.json").read_text(encoding="utf-8"))
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text(encoding="utf-8"))
    report = inspect(snap, manifest)
    print(render_html(report) if args.html else render_text(report), end="" if not args.html else "\n")


if __name__ == "__main__":
    main()
