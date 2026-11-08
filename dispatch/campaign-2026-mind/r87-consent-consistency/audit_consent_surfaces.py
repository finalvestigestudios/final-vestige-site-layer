"""Read-only, privacy-safe consent/operations consistency checker.

Only public page-level copy and aggregate Jetpack statuses are accepted.
No WordPress writes, no subscriber reads, no network access and no send capability.
Every report is HOLD_UNSENT. Not a legal or deliverability certification.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import re
from typing import Any

SNAPSHOT = pathlib.Path(__file__).with_name("snapshot.json")
TOP_LEVEL = {"schema", "observed_utc", "readonly", "site", "first_party_evidence",
             "public_consent_copy", "jetpack", "audience", "recent_posts", "campaign", "sources"}
PAGE_KEYS = {"dispatch", "focus", "editorial_standards"}
EMAIL_PATTERN = re.compile(r"(?i)\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b")
PRIVATE_KEYS = {"email_address", "recipient_email", "subscriber_email", "subscribers",
                "contacts", "mailing_list", "personal_address", "customer_email",
                "customer_id", "subscriber_id", "access_token", "authorization",
                "private_affiliate_url", "affiliate_url", "unsubscribe_token",
                "phone_number", "recipient_list", "raw_referrer", "click_id"}


class UnsafeSnapshot(ValueError):
    """Unsafe input must not reach reports."""


def _reject_pii(obj: Any) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in PRIVATE_KEYS:
                raise UnsafeSnapshot("private_field_not_permitted")
            _reject_pii(value)
    elif isinstance(obj, list):
        for element in obj:
            _reject_pii(element)
    elif isinstance(obj, str):
        if EMAIL_PATTERN.search(obj):
            raise UnsafeSnapshot("email_address_not_permitted")
        if re.search(r"https?://[^\s]*[?&](?:token|email|subscriber|click_id|aff_id)=", obj, re.I):
            raise UnsafeSnapshot("private_tracking_not_permitted")


def _bool(value: Any, label: str) -> bool:
    if type(value) is not bool:
        raise UnsafeSnapshot("invalid_boolean:" + label)
    return value


def _count(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise UnsafeSnapshot("invalid_aggregate:" + label)
    return value


def audit(snapshot: dict[str, Any]) -> dict[str, Any]:
    if type(snapshot) is not dict or set(snapshot) != TOP_LEVEL:
        raise UnsafeSnapshot("unexpected_snapshot_fields")
    _reject_pii(snapshot)
    if snapshot["schema"] != "fv_dispatch_r87_public_operational_snapshot_v1":
        raise UnsafeSnapshot("invalid_schema")
    if snapshot["readonly"] is not True or snapshot["site"] != "finalvestige.com":
        raise UnsafeSnapshot("not_an_authorized_readonly_snapshot")
    if set(snapshot["first_party_evidence"]) != PAGE_KEYS:
        raise UnsafeSnapshot("unknown_public_pages")
    pages = snapshot["first_party_evidence"]
    for key, expected in (("dispatch", 523), ("focus", 1579), ("editorial_standards", 17)):
        page = pages[key]
        if type(page) is not dict or page.get("page_id") != expected or page.get("status") != "publish":
            raise UnsafeSnapshot("wrong_public_page:" + key)
    dispatch = pages["dispatch"]
    focus = pages["focus"]
    for key in ("shows_affiliate_expectations", "mentions_52_page_fieldbook",
                "mentions_unsubscribe", "uses_existing_jetpack_subscription"):
        _bool(dispatch.get(key), "dispatch."+key)
        _bool(focus.get(key), "focus."+key)
    for key in ("requires_source_vs_inference", "requires_commercial_separation"):
        _bool(pages["editorial_standards"].get(key), "standards."+key)
    copy = snapshot["public_consent_copy"]
    if set(copy) != {"dispatch", "focus"} or any(type(s) is not str or len(s) > 800 for s in copy.values()):
        raise UnsafeSnapshot("bad_public_consent_copy")
    wp = snapshot["jetpack"]
    for key in ("subscriptions", "site_can_send", "email_new_posts_by_default",
                "welcome_fieldbook_configured", "actual_welcome_receipt_verified",
                "verified_jetpack_received_eml", "verified_sender_postal_in_received_email",
                "verified_unsubscribe_functionality"):
        _bool(wp.get(key), "jetpack."+key)
    if wp.get("email_content_format") not in {"full", "excerpt"} or wp.get("reply_to") not in {"comment", "author", "no-reply"}:
        raise UnsafeSnapshot("invalid_jetpack_configuration")
    audience = snapshot["audience"]
    for key in ("newsletter_total", "newsletter_confirmed", "newsletter_unconfirmed",
                "other_endpoint_email_followers", "other_endpoint_wpcom_followers"):
        _count(audience.get(key), key)
    for key in ("recipient_count_verified", "classification_conflict"):
        _bool(audience.get(key), key)
    history = snapshot["recent_posts"]
    if type(history.get("post_ids")) is not list or type(history.get("statuses")) is not list:
        raise UnsafeSnapshot("invalid_send_history")
    if len(history["post_ids"]) != len(history["statuses"]) or len(set(history["post_ids"])) != len(history["post_ids"]):
        raise UnsafeSnapshot("invalid_send_history")
    for val in history["post_ids"]:
        _count(val, "post_id")
    for status in history["statuses"]:
        if status not in {"never_sent_opted_out", "sent", "pending", "failed"}:
            raise UnsafeSnapshot("unknown_send_status")
    _bool(history.get("proof_of_all_time_zero_sends"), "all_time")
    campaign = snapshot["campaign"]
    if campaign.get("issues") != 6 or campaign.get("editorial") != 4 or campaign.get("commercial_reservations") != [3, 5]:
        raise UnsafeSnapshot("unapproved_campaign_mix")
    for key in ("marketing_authorization_verified", "merchant_email_channel_authorization_verified",
                "approved_commercial_guides_live", "founder_final_send_approval"):
        _bool(campaign.get(key), "campaign."+key)
    if type(snapshot["sources"]) is not list or len(snapshot["sources"]) < 3:
        raise UnsafeSnapshot("missing_public_sources")
    if any(type(s) is not str or not s.startswith("https://") for s in snapshot["sources"]):
        raise UnsafeSnapshot("invalid_public_sources")

    # Important: a counts contradiction is not solved by summing 2+2, nor can
    # the follower endpoint's email=0 be taken as definitive deliverability.
    copy_mismatch = (dispatch["shows_affiliate_expectations"] != focus["shows_affiliate_expectations"]
                     or ("commission" in copy["dispatch"].lower()) != ("commission" in copy["focus"].lower()))
    conflicting_counts = (audience["classification_conflict"]
                          or audience["newsletter_confirmed"] + audience["newsletter_unconfirmed"] > audience["newsletter_total"])
    unexpected_send = any(status != "never_sent_opted_out" for status in history["statuses"])
    return {
        "snapshot_utc": snapshot["observed_utc"],
        "decision": "HOLD_UNSENT",
        "offer_03_05": "HOLD_MERCHANT",
        "consent_parity": "MISMATCH_REQUIRES_COPY_REVIEW" if copy_mismatch else "PARITY_OF_STATED_COPY_ONLY_NOT_PROOF_OF_CONSENT",
        "audience": "UNRECONCILED_DO_NOT_INFER_RECIPIENTS" if conflicting_counts or not audience["recipient_count_verified"] else "AGGREGATES_PRESENT_PRIVATE_VERIFICATION_STILL_REQUIRED",
        "delivery_history": "MIXED_STATUS_REVIEW_REQUIRED" if unexpected_send else "FIVE_SPECIFIC_OPTED_OUT_NOT_ALL_TIME_PROOF",
        "post_send_default": "OFF_NOT_A_GLOBAL_INTERLOCK" if not wp["email_new_posts_by_default"] else "ON_STOP_AND_REVIEW",
        "welcome": "CONFIGURED_NOT_RECEIPT_PROVEN" if wp["welcome_fieldbook_configured"] and not wp["actual_welcome_receipt_verified"] else "NOT_ESTABLISHED_BY_THIS_AUDIT",
        "email_render": "NOT_A_GENUINE_RECEIVED_EMAIL" if not wp["verified_jetpack_received_eml"] else "SEPARATE_HUMAN_MIME_AND_CLIENT_QA_REQUIRED",
        "commercial_permissions": "NOT_VERIFIED" if not campaign["merchant_email_channel_authorization_verified"] else "DOCUMENTARY_REVIEW_REQUIRED",
        "human_founder_approval": "ABSENT" if not campaign["founder_final_send_approval"] else "APPROVAL_CANNOT_BE_GRANTED_BY_THIS_AUDIT",
        "privacy": "NO_PII_ACCEPTED_NO_PERSON_LEVEL_METRICS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=pathlib.Path, default=SNAPSHOT)
    args = parser.parse_args()
    try:
        report = audit(json.loads(args.snapshot.read_text(encoding="utf-8")))
    except (UnsafeSnapshot, json.JSONDecodeError, OSError, TypeError, KeyError) as exc:
        # Deliberately do not print exception values or input text.
        print(json.dumps({"decision": "HOLD_UNSENT", "audit": "REJECTED_UNSAFE_OR_INVALID_INPUT"}))
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
