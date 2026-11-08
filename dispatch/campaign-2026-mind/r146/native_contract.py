"""Read-only WordPress/Jetpack native capabilities and campaign eligibility audit.

No network, credentials, subscribers, sending, CMS writes or tracking code.
Input is a redacted, independently observed settings/evidence snapshot.
A synthetic flag must never be treated as send permission.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ALLOWED_KINDS = {"editorial", "commercial"}
REQUIRED_NUMBERS = {f"{i:02d}" for i in range(1, 7)}
ALLOWED_DESTINATIONS = ("https://finalvestige.com/",)
RELEASE_SENTINEL = "HOLD_UNSENT"


class ContractError(ValueError):
    pass


def _is_true(record: dict, field: str) -> bool:
    # Reject strings like "true", numbers like 1, and truthy evidence references.
    return record.get(field) is True


def audit(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != "dispatch.native_jetpack.v1":
        raise ContractError("Unsupported native Jetpack contract")
    issues = snapshot.get("issues")
    if not isinstance(issues, list) or len(issues) != 6:
        raise ContractError("Six canonical newsletter issues are required")
    numbers = [x.get("number") for x in issues if isinstance(x, dict)]
    if set(numbers) != REQUIRED_NUMBERS or len(numbers) != len(set(numbers)):
        raise ContractError("Issue IDs must be 01–06 exactly once")
    if sum(x.get("kind") == "editorial" for x in issues) != 4 or sum(x.get("kind") == "commercial" for x in issues) != 2:
        raise ContractError("Founder allocation must stay at four editorial / two commercial")
    if any(x.get("kind") not in ALLOWED_KINDS or not isinstance(x.get("subject"), str)
           or not x.get("subject").strip() for x in issues):
        raise ContractError("Invalid edition kind or absent WordPress post-title candidate")
    if {x["number"] for x in issues if x["kind"] == "commercial"} != {"03", "05"}:
        raise ContractError("Commercial slots are reserved to Issues 03 and 05")

    jp = snapshot.get("jetpack", {})
    subs = snapshot.get("subscribers", {})
    welcome = snapshot.get("welcome", {})
    proof = snapshot.get("actual_delivery", {})
    measurement = snapshot.get("measurement", {})
    if not all(isinstance(v, dict) for v in (jp, subs, welcome, proof, measurement)):
        raise ContractError("Structured evidence groups are required")
    for key in ("reported_total", "reported_confirmed", "reported_unconfirmed",
                "jetpack_email_followers", "jetpack_wpcom_followers"):
        if type(subs.get(key)) is not int or subs[key] < 0:
            raise ContractError("Aggregate counts must be nonnegative integers, never PII")

    # Unverified overlapping provider counts CANNOT be added into a list size.
    eligible = None
    if _is_true(subs, "email_eligible_verified") and _is_true(subs, "consent_provenance_verified") and _is_true(subs, "counter_sets_reconciled"):
        # Exact email eligibility requires a provider-derived, reconciled number;
        # dashboard confirmed/total counts cannot provide it.
        candidate = subs.get("provider_eligible_count")
        if type(candidate) is int and candidate >= 0:
            eligible = candidate

    for x in issues:
        dest = x.get("destination")
        if dest is not None and (not isinstance(dest, str) or not dest.startswith(ALLOWED_DESTINATIONS)
                                 or "@" in dest or "?" in dest or "#" in dest):
            raise ContractError("Only untracked FV first-party canonical destinations permitted in draft")
        if x["kind"] == "commercial" and (dest is not None or x.get("destination_state") != "NOT_LIVE_OR_APPROVED"):
            raise ContractError("Unapproved commercial guide must have no active CTA")

    # These are NOT automated drip segments. The current WordPress newsletter
    # creates post notifications, not a verified event-triggered nurture series.
    capability = {
        "native_delivery_model": "WORDPRESS_POST_NOTIFICATION_NOT_VERIFIED_DRIP",
        "subject_source": "WORDPRESS_POST_TITLE",
        "native_preheader_control": "UNVERIFIED",
        "current_content_format": jp.get("email_content_format"),
        "sender_reply_to": jp.get("reply_to"),
        "default_send_disabled": jp.get("email_new_posts_by_default") is False,
        "topic_or_behavioral_recipient_segmentation": "NOT_VERIFIED",
        "email_eligible_recipient_count": eligible,
        "independent_paid_orders": None,
        "net_revenue_per_1000_qualified_human_sessions": None,
    }

    global_blockers = []
    if not _is_true(jp, "subscriptions"):
        global_blockers.append("NEWSLETTER_DISABLED")
    if jp.get("email_new_posts_by_default") is not False:
        global_blockers.append("DEFAULT_SEND_MUST_REMAIN_OFF")
    if jp.get("email_content_format") not in ("full", "excerpt"):
        global_blockers.append("DELIVERY_FORMAT_UNKNOWN")
    if not _is_true(subs, "consent_provenance_verified") or eligible is None:
        global_blockers.append("NATIVE_ELIGIBLE_RECIPIENTS_UNKNOWN")
    if not _is_true(welcome, "real_received_welcome_verified") or not _is_true(welcome, "live_pdf_http_and_pagecount_verified"):
        global_blockers.append("FIELD_BOOK_ACTUAL_RECEIPT_OR_PDF_UNKNOWN")
    if not _is_true(proof, "native_visual_preview_verified") or not _is_true(proof, "actual_received_mail_verified"):
        global_blockers.append("REAL_JETPACK_MIME_AND_LAYOUT_UNVERIFIED")
    if not _is_true(proof, "rendered_fv_postal_address_verified") or not _is_true(proof, "functional_unsubscribe_verified"):
        global_blockers.append("PUBLISHER_POSTAL_AND_OPTOUT_UNVERIFIED")
    if not _is_true(proof, "founder_final_send_approval"):
        global_blockers.append("FOUNDER_SEND_APPROVAL_MISSING")
    # Even artificially checked boxes don't imply release. Application is never a sender.
    per_issue = []
    for item in issues:
        reason = list(global_blockers)
        if item["kind"] == "commercial":
            reason.append("MERCHANT_ACCOUNT_EMAIL_RIGHTS_AND_LINK_HOLD")
            reason.append("UNPUBLISHED_UNAPPROVED_FIRST_PARTY_GUIDE")
        elif item["destination_state"] != "wp_published":
            reason.append("EDITORIAL_LANDING_PUBLICATION_UNVERIFIED")
        per_issue.append({
            "number": item["number"],
            "kind": item["kind"],
            "wordpress_post_title_candidate": item["subject"],
            "release_decision": RELEASE_SENTINEL,
            "merchant_decision": "HOLD_MERCHANT" if item["kind"] == "commercial" else "NOT_APPLICABLE",
            "first_party_destination": item["destination"],
            "blockers": sorted(set(reason)),
            "copy_review_note": item.get("known_copy_risk", ""),
        })
    return {"capability": capability,
            "global_blockers": sorted(set(global_blockers)),
            "issues": per_issue,
            "verified_confirmed_signup_events": None,
            "native_delivery_proof": "NOT_VERIFIED",
            "status": RELEASE_SENTINEL,
            "wrote_wordpress": False,
            "sent_email": False}


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("snapshot", type=Path)
    p.add_argument("--out", type=Path)
    a = p.parse_args()
    result = audit(json.loads(a.snapshot.read_text(encoding="utf-8")))
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if a.out:
        a.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
