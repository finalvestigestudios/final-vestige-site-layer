"""Read-only, fail-closed WordPress/Dispatch acquisition audit. Never sends or writes.

Input: redacted JSON snapshots (content excerpts, not subscribers). Output: aggregated
findings without addresses, tokens, or any claim of verified inbox delivery.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

HOLD = "HOLD_UNSENT"
MERCHANT_HOLD = "HOLD_MERCHANT"
PROVIDER_UNKNOWN = "NOT_VERIFIED"
EXPECTED_PDF = "Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf"


def inspect(snapshot: dict) -> dict:
    settings = snapshot.get("newsletter_settings") or {}
    status = snapshot.get("newsletter_status") or {}
    pages = snapshot.get("pages") or {}
    wp = status.get("subscribers") or {}
    focus_raw = (pages.get("focus") or {}).get("raw", "")
    dispatch_raw = (pages.get("dispatch") or {}).get("raw", "")
    dispatch_rendered = (pages.get("dispatch") or {}).get("rendered", "")
    evidence = snapshot.get("proof") or {}
    findings = []

    def add(code, value, reasoning):
        findings.append({"code": code, "status": value, "reason": reasoning})

    add("NEWSLETTER_CONFIG", "PASS_CONFIG_ONLY" if settings.get("subscriptions") is True else "FAIL",
        "Provider-enabled setting is not proof of recipient eligibility.")
    add("POST_AUTO_SEND", "PASS" if settings.get("email_new_posts_by_default") is False else "FAIL",
        "Even when off globally, publication can opt in at the individual post level.")
    add("WELCOME_PDF_CONFIG", "PASS_CONFIG_ONLY" if EXPECTED_PDF in settings.get("welcome_message", "") else "FAIL",
        "A configured 52-page download is not proof that the welcome was delivered.")
    add("DISPATCH_NATIVE_BLOCK", "PASS_SOURCE" if "<!-- wp:jetpack/subscriptions" in dispatch_raw else "FAIL",
        "A stored Jetpack block is not proof the form renders in guest sessions.")
    fallback = "post_type=page" in dispatch_rendered and "p=523" in dispatch_rendered
    editable_form = bool(re.search(r'<input[^>]+type=["\']email["\']', dispatch_rendered, re.I))
    add("DISPATCH_RENDERED_GUEST_FORM", "BROWSER_CHECK_REQUIRED" if fallback and not editable_form else
        ("BROWSER_CHECK_REQUIRED" if not dispatch_rendered else "RENDERED_MARKUP_OBSERVED"),
        "An API-rendered self-link is not evidence of a broken guest form; independently inspect a signed-out browser.")
    unsafe_q = "get('subscribe')" in focus_raw and "if(q)" in focus_raw and "show();" in focus_raw
    unsafe_css = "is-subscriber" in focus_raw and "MutationObserver" in focus_raw
    add("FOCUS_FALSE_SUCCESS", "REPRODUCIBLE_SOURCE_RISK" if unsafe_q or unsafe_css else "NOT_SEEN_IN_EXCERPT",
        "URL and DOM-class observations are not authoritative confirmation or confirmed_signup events.")
    add("SUBSCRIBER_COUNTERS", "NONADDITIVE" if isinstance(wp.get("total"), int) else "NOT_VERIFIED",
        "Do not add counted and unconfirmed categories or infer eligible email recipients.")
    recent = status.get("recent_sends") or []
    add("RECENT_SEND_EVIDENCE", "NEVER_SENT_REPORTED" if recent and all(x.get("status") == "never_sent_opted_out" for x in recent) else "NOT_VERIFIED",
        "Only the reported posts, not every historical mailing, are covered by this observation.")
    for name, label in [("native_email_eligibility", "NATIVE_EMAIL_ELIGIBILITY"),
                        ("received_welcome", "RECEIVED_FIELDBOOK_WELCOME"),
                        ("jetpack_native_preview", "JETPACK_NATIVE_EMAIL_PREVIEW"),
                        ("publisher_postal", "PUBLISHER_POSTAL_ADDRESS"),
                        ("functional_unsubscribe", "FUNCTIONAL_UNSUBSCRIBE"),
                        ("named_email_permission", "NAMED_MERCHANT_EMAIL_PERMISSION"),
                        ("approved_affiliate_link", "APPROVED_AFFILIATE_LINK"),
                        ("approved_live_guide", "LIVE_APPROVED_GUIDE"),
                        ("paid_settlement", "INDEPENDENT_PAID_SETTLEMENT")]:
        # A pointer alone is not independently checked evidence. Explicit external
        # approvals must be manually audited by the correct owner before release.
        add(label, PROVIDER_UNKNOWN, "External provider/owner verification required; automation does not self-attest.")
    result = {
        "revision": "R171-2026-11-06", "campaign_issues": 6,
        "allocation": {"editorial": 4, "commercial": 2},
        "release": HOLD, "commercial_issue_03": MERCHANT_HOLD,
        "commercial_issue_05": MERCHANT_HOLD,
        "confirmed_signup": "NOT_COMPUTABLE_FROM_PAGE_OR_COUNTERS",
        "qualified_human_sessions": PROVIDER_UNKNOWN,
        "net_revenue_per_1000_qualified_sessions": "NOT_COMPUTABLE",
        "counted_subscribers": wp.get("total") if isinstance(wp.get("total"), int) else None,
        "unconfirmed_pending": wp.get("unconfirmed") if isinstance(wp.get("unconfirmed"), int) else None,
        "email_eligible_recipients": None,
        "findings": findings,
        "documentation": "No messages sent; all inputs are read-only redacted snippets."
    }
    # Never include proof payloads (may include sensitive personal data) in outputs.
    return result


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: dispatch_truth_gate.py INPUT_SNAPSHOT.json OUTPUT_REPORT.json", file=sys.stderr)
        return 2
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    report = inspect(data)
    Path(sys.argv[2]).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("HOLD_UNSENT; 6 drafts; external delivery and merchant proofs remain missing")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
