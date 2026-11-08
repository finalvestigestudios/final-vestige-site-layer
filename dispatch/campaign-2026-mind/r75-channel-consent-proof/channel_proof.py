#!/usr/bin/env python3
"""Privacy-minimizing, READ-ONLY evidence register for the FV Dispatch pilot.

This program cannot verify a WordPress account, prove delivery, contact a subscriber,
certify legal compliance, send a test, or release any edition. It accepts only
predefined count-only and yes/no fields; unexpected PII-bearing fields are rejected.
"""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path

HOLD = "HOLD_UNSENT"
SCHEMA = "fv-dispatch-human-evidence-v1"
ISSUES = ("01", "02", "03", "04", "05", "06")
COMMERCIAL = ("03", "05")
ATTESTATIONS = (
    "recipient_email_status_filtered_in_native_wordpress",
    "publisher_postal_address_ownership_verified",
    "native_editor_email_preview_reviewed",
    "explicitly_authorized_received_test_email_inspected",
    "html_and_plain_mime_claims_and_footers_reviewed",
    "unsubscribe_functionally_verified",
    "focus_fieldbook_welcome_actually_received",
    "final_founder_campaign_approval",
)
MERCHANT = (
    "partner_account_acceptance",
    "email_channel_permission_specific_to_product",
    "approved_tracking_link_and_format",
    "guide_published_and_founder_approved",
    "seller_terms_and_claims_rechecked",
)
SNAPSHOT_KEYS = (
    "captured_utc", "total", "confirmed", "unconfirmed", "suppressed",
    "eligible_email_count", "newsletter_enabled", "new_post_auto_email",
    "content_format", "welcome_configured", "recent_send_count",
)

class InvalidEvidence(ValueError):
    pass

def _keys(item, expected, label):
    if type(item) is not dict or set(item) != set(expected):
        raise InvalidEvidence("INVALID_" + label + "_SHAPE")

def validate(raw: dict) -> dict:
    _keys(raw, ("schema", "snapshot", "attestations", "merchants"), "ROOT")
    if raw["schema"] != SCHEMA:
        raise InvalidEvidence("INVALID_SCHEMA")
    s = raw["snapshot"]
    _keys(s, SNAPSHOT_KEYS, "SNAPSHOT")
    if type(s["captured_utc"]) is not str or not (
        len(s["captured_utc"]) == 20 and s["captured_utc"].endswith("Z")
    ):
        raise InvalidEvidence("INVALID_CAPTURE_TIMESTAMP")
    for key in ("total", "confirmed", "unconfirmed", "suppressed", "recent_send_count"):
        if type(s[key]) is not int or s[key] < 0 or s[key] > 10000000:
            raise InvalidEvidence("INVALID_COUNT")
    if s["eligible_email_count"] is not None and (
        type(s["eligible_email_count"]) is not int
        or not (0 <= s["eligible_email_count"] <= s["total"])
    ):
        raise InvalidEvidence("INVALID_ELIGIBLE_COUNT")
    for key in ("newsletter_enabled", "new_post_auto_email", "welcome_configured"):
        if type(s[key]) is not bool:
            raise InvalidEvidence("INVALID_SETTING")
    if s["content_format"] not in ("excerpt", "full"):
        raise InvalidEvidence("INVALID_EMAIL_FORMAT")
    _keys(raw["attestations"], ATTESTATIONS, "ATTESTATIONS")
    if any(type(v) is not bool for v in raw["attestations"].values()):
        raise InvalidEvidence("INVALID_ATTESTATION_VALUE")
    _keys(raw["merchants"], COMMERCIAL, "MERCHANT_SLOTS")
    for edition, obj in raw["merchants"].items():
        _keys(obj, MERCHANT, "MERCHANT_" + edition)
        if any(type(v) is not bool for v in obj.values()):
            raise InvalidEvidence("INVALID_MERCHANT_ATTESTATION")
    return raw

def assess(record: dict) -> dict:
    """Recompute observed blockers. No combination can authorize sending."""
    r = validate(record)
    s, a, m = r["snapshot"], r["attestations"], r["merchants"]
    blockers = []
    if s["eligible_email_count"] is None or not a["recipient_email_status_filtered_in_native_wordpress"]:
        blockers.append("ELIGIBLE_EMAIL_AUDIENCE_NOT_INDEPENDENTLY_ESTABLISHED")
    if not s["newsletter_enabled"] or s["new_post_auto_email"] or s["recent_send_count"]:
        blockers.append("WORDPRESS_CONFIG_REQUIRES_FOUNDER_REVIEW")
    if s["content_format"] == "excerpt":
        blockers.append("CUSTOM_EXCERPT_NATIVE_DELIVERY_NEEDS_EVIDENCE")
    for k, label in (
        ("publisher_postal_address_ownership_verified", "PUBLISHER_POSTAL_NOT_VERIFIED"),
        ("native_editor_email_preview_reviewed", "NATIVE_EDITOR_PREVIEW_NOT_VERIFIED"),
        ("explicitly_authorized_received_test_email_inspected", "RECEIVED_JETPACK_EMAIL_NOT_VERIFIED"),
        ("html_and_plain_mime_claims_and_footers_reviewed", "MIME_PARITY_NOT_VERIFIED"),
        ("unsubscribe_functionally_verified", "UNSUBSCRIBE_FUNCTION_NOT_VERIFIED"),
        ("focus_fieldbook_welcome_actually_received", "FOCUS_WELCOME_RECEIPT_NOT_VERIFIED"),
        ("final_founder_campaign_approval", "FINAL_FOUNDER_APPROVAL_NOT_EVIDENCED"),
    ):
        if not a[k]:
            blockers.append(label)
    commercial = {}
    for edition in COMMERCIAL:
        pending = [k.upper() for k in MERCHANT if not m[edition][k]]
        commercial[edition] = {
            "state": "HOLD_MERCHANT",
            "unverified": pending,
            "partner_rights_proven_by_program": False,
        }
    return {
        "schema": "fv-dispatch-channel-proof-summary-v1",
        "captured_utc": s["captured_utc"],
        "newsletter": {
            "enabled": s["newsletter_enabled"],
            "auto_new_post_email": s["new_post_auto_email"],
            "format": s["content_format"],
            "recent_send_count": s["recent_send_count"],
            "welcome_configured_not_received": s["welcome_configured"],
        },
        "subscribers": {
            "total_reported": s["total"],
            "confirmed_reported": s["confirmed"],
            "unconfirmed_reported": s["unconfirmed"],
            "suppressed_reported": s["suppressed"],
            "email_eligible": s["eligible_email_count"],
            "counter_interpretation": "NONADDITIVE_DO_NOT_INFER_FOUR_SUBSCRIBERS",
        },
        "common_blockers": blockers,
        "commercial_issues": commercial,
        "edition_states": {issue: ("HOLD_MERCHANT" if issue in COMMERCIAL else HOLD) for issue in ISSUES},
        "release_state": HOLD,
        "send_allowed": False,
        "subscriber_details_in_output": False,
        "real_delivery_proven_by_program": False,
        "human_attestations_cryptographically_verified": False,
        "postal_and_optout_reachability_proven_by_program": False,
    }

def plaintext(result: dict) -> str:
    lines = [
        "FINAL VESTIGE STUDIOS / THE DISPATCH — READ-ONLY CHANNEL PROOF",
        "ALL SIX: HOLD_UNSENT. Commercial 03 and 05: HOLD_MERCHANT.",
        "No person, address, source email, unsubscribe URL or tracking parameter is stored.",
        "This is a human-input ledger, NOT a third-party verification or permission to send.",
        "",
        "WORDPRESS",
        "Newsletter: " + ("enabled" if result["newsletter"]["enabled"] else "disabled"),
        "Automatic post emails: " + str(result["newsletter"]["auto_new_post_email"]),
        "Email body: " + result["newsletter"]["format"],
        "Recent sends: " + str(result["newsletter"]["recent_send_count"]),
        "Subscriber counters: NONADDITIVE; eligibility remains unverified unless separately proven.",
        "",
        "ALL-ISSUE HOLD REASONS:",
    ]
    lines.extend("- " + b for b in result["common_blockers"])
    lines += ["", "PRODUCT-SPECIFIC HOLDS:"]
    for issue in COMMERCIAL:
        lines.append("- Issue " + issue + ": " + ", ".join(result["commercial_issues"][issue]["unverified"]) )
    lines += [
        "", "No send, post, schedule, subscriber import, tracking or merchant URL is authorized.",
        "Homepage flagship and frozen PR #49 remain untouched.",
    ]
    return "\n".join(lines) + "\n"

def html_board(result: dict) -> str:
    blocks = []
    for issue in ISSUES:
        typ = "Commercial / merchant approval required" if issue in COMMERCIAL else "Editorial / no product"
        blocks.append(
            "<li class='card'><span class='no'>" + issue + "</span><p>" + escape(typ) +
            "</p><strong>" + escape(result["edition_states"][issue]) + "</strong></li>"
        )
    bs = "".join("<li>" + escape(x.replace("_", " ").title()) + "</li>" for x in result["common_blockers"])
    cs = "".join("<li>Issue " + issue + ": " +
        escape(", ".join(result["commercial_issues"][issue]["unverified"]).replace("_", " ").title()) +
        "</li>" for issue in COMMERCIAL)
    return ("""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive"><title>Dispatch Channel Proof | HOLD</title>
<style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#0b0c0c;color:#f2ebe2;font:16px/1.65 system-ui,sans-serif}
main{width:min(1080px,calc(100% - 32px));margin:auto;padding:40px 0 80px}
h1,h2{font-family:Georgia,serif;font-weight:400;line-height:1.14}h1{font-size:clamp(2.2rem,6vw,4rem)}h2{font-size:1.8rem}
p{max-width:75ch;color:#d0c8bd}.eyebrow{letter-spacing:.14em;text-transform:uppercase;color:#d6ae78;font-weight:700;font-size:.8rem}
.notice{border:2px solid #ebbd77;background:#302218;padding:16px 20px;font-weight:700;color:#fff1d9}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;padding:0;list-style:none}
.card{border:1px solid #555047;padding:20px;min-width:0}.card .no{font:2rem Georgia,serif;color:#d6ae78}.card p{margin:.5rem 0}.card strong{font-size:.83rem;color:#f5d9a6}
section{margin-top:48px}li{overflow-wrap:anywhere}a{color:#f3d7a5}:focus-visible{outline:3px solid #ffe0a0;outline-offset:4px}
footer{margin-top:50px;border-top:1px solid #555047;padding-top:25px;font-size:.9rem}
@media(max-width:750px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:480px){.grid{grid-template-columns:1fr}}
</style></head><body><main>
<p class="eyebrow">Final Vestige Studios / internal reviewer evidence</p>
<h1>What must be true before one Dispatch email is sent?</h1>
<div class="notice" role="status">HOLD_UNSENT — no campaign, preview send or publication authorized</div>
<p>Read-only, privacy-minimized evidence register. This report does not prove that an actual Jetpack email reached an inbox, an unsubscribe link works, a merchant approved email promotion, or a business address qualifies. All claims of verification require separate human evidence.</p>
<section aria-labelledby="ed"><h2 id="ed">The founder’s six-week pilot</h2><ol class="grid">""" +
    "".join(blocks) + """</ol></section>
<section aria-labelledby="co"><h2 id="co">Unresolved general delivery evidence</h2><ol>""" + bs + """</ol></section>
<section aria-labelledby="me"><h2 id="me">Two additional merchant holds</h2><ol>""" + cs + """</ol></section>
<section aria-labelledby="rule"><h2 id="rule">What the small list cannot tell us</h2>
<p>Reported total=2, confirmed=2, unconfirmed=2 are overlapping counters, not four subscribers. Without a native email-status filter there is no justified eligible audience count. Do not present open-rate, A/B winners, sales, attributed revenue, or causal conversion claims.</p></section>
<footer><p>No live links, publisher address, recipient personal data or unsubscribe token appears here. Homepage PR #49 is untouched. Use one existing Jetpack subscriber list only.</p></footer>
</main></body></html>""")

def main(argv=None):
    p = argparse.ArgumentParser(description="Read-only, private COUNT-ONLY human evidence review")
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        if args.input.is_symlink() or not args.input.is_file() or args.input.stat().st_size > 16384:
            raise InvalidEvidence("INVALID_INPUT")
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        result = assess(raw)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "channel-summary.json").write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
        (args.output_dir / "channel-summary.txt").write_text(plaintext(result), encoding="utf-8")
        (args.output_dir / "channel-review.html").write_text(html_board(result), encoding="utf-8")
    except (OSError, ValueError, TypeError):
        # Never echo input content, file paths or accidental subscriber PII.
        print("EVIDENCE_REJECTED_HOLD_UNSENT")
        return 2
    print("REDACTED_CHANNEL_PROOF_GENERATED_HOLD_UNSENT")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
