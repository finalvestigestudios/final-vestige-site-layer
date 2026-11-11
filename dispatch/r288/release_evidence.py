"""Read-only, fail-closed Dispatch editorial/commercial release decision helper.

Never sends, imports, logs identities, touches WordPress or contacts merchants.
Dated observations are reviewer assertions, not live telemetry.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from typing import Mapping
import json
import re

EXPECTED_ORIGINAL_BLOBS = {
    "manifest.json": "86df98ad8a84e583ff5df64ddbf8c0eaa1335b00",
    "tests/test_campaign.py": "fd7f05e30092a7ec82090993dc5d7d0e23755c8e",
    "issues/01-the-mind-is-not-a-camera.md": "039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8",
    "issues/02-before-hypnosis-had-a-name.md": "faa207ab7deafd86460d36f8c17fe62d392d0e14",
    "issues/03-the-twelve-minute-question.md": "aeeef34efea0cc281f69901488e4501fea851245",
    "issues/04-the-hatch-and-the-spark.md": "89635bfb9c8d1ff17297a59b6b5b5b2a176934ca",
    "issues/05-before-you-press-play.md": "a9dfaa450ba025a7b5113ade8a294d6dbad778dc",
    "issues/06-the-evidence-log.md": "004d558df6376d2ad6f4f79a4581e8d2c444e355",
}
MERCHANT_NUMBERS = {3, 5}
REQUIRED_GLOBAL = (
    "audience_provider_confirmed", "audience_email_eligible_verified",
    "consent_and_suppression_checked", "native_jetpack_preview_reviewed",
    "real_received_footer_verified", "publisher_postal_address_verified",
    "unsubscribe_end_to_end_verified", "subject_and_content_approved",
    "founder_final_campaign_approval", "post_level_send_flag_authorized",
)
REQUIRED_MERCHANT = (
    "merchant_partner_accepted", "merchant_email_channel_permitted",
    "offer_specific_earning_link_verified", "current_terms_verified",
    "offer_specific_claim_review_complete", "vetted_guide_live_and_approved",
    "adjacent_email_and_guide_disclosures_verified",
)


def git_blob_sha(content: bytes) -> str:
    return sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


def validate_original_files(root: Path) -> dict:
    mismatches = {}
    for path, expected in EXPECTED_ORIGINAL_BLOBS.items():
        loc = root / path
        actual = git_blob_sha(loc.read_bytes()) if loc.exists() else "MISSING"
        if actual != expected:
            mismatches[path] = {"expected": expected, "actual": actual}
    return {"files_checked": len(EXPECTED_ORIGINAL_BLOBS), "byte_identical": not mismatches, "mismatches": mismatches}


def release_decisions(manifest: Mapping, evidence: Mapping) -> dict:
    """Does not produce a send instruction; only HUMAN_REVIEW_CANDIDATE or HOLD.

    Evidence is required to be a named mapping per issue, not inferred from total counts.
    This denies inferred permissions and never mutates any external system.
    """
    entries = manifest["issues"]
    if len(entries) != 6 or sorted(i["number"] for i in entries) != list(range(1, 7)):
        raise ValueError("Expected exact original six-issue manifest")
    if sum(i["kind"] == "editorial" for i in entries) != 4 or sum(i["kind"] == "commercial-review-pending" for i in entries) != 2:
        raise ValueError("Original four-editorial/two-commercial split changed")
    if {i["number"] for i in entries if i["kind"] == "commercial-review-pending"} != MERCHANT_NUMBERS:
        raise ValueError("Commercial reservations must remain editions 03 and 05")
    if any(i.get("merchant_affiliate_url") for i in entries):
        raise ValueError("Unapproved earning link in original manifest")
    decisions = []
    for issue in entries:
        n = issue["number"]
        e = evidence.get("issues", {}).get(f"{n:02}", {})
        g = evidence.get("global", {})
        blockers = [k for k in REQUIRED_GLOBAL if g.get(k) is not True]
        if issue.get("publish_state") != "hold":
            blockers.append("source_manifest_must_remain_hold")
        if n in MERCHANT_NUMBERS:
            blockers.extend(k for k in REQUIRED_MERCHANT if e.get(k) is not True)
            if "[[APPROVED_" in str(issue.get("editorial_cta", "")):
                blockers.append("inactive_buyer_guide_placeholder")
        if n == 4 and "fourteen seconds" in issue["subject"].lower() and e.get("apollo_interval_copy_approved") is not True:
            blockers.append("apollo_14_second_interval_unexplained")
        if n in (1, 2) and e.get("duplicate_puysegur_cta_reviewed") is not True:
            blockers.append("duplicate_puysegur_destination_review_pending")
        if n == 6 and e.get("fieldbook_repeat_cta_reviewed") is not True:
            blockers.append("fieldbook_already_in_welcome")
        decisions.append({"issue": n, "classification": issue["kind"],
                          "status": "HOLD_UNSENT" if blockers else "HUMAN_REVIEW_CANDIDATE_ONLY",
                          "blockers": blockers})
    return {"send_authorized": False, "scheduled": False, "issues": decisions}


def confirmed_signup_from_event(event: Mapping) -> bool:
    """A page click or logged-in WordPress follower is never enough proof."""
    return (event.get("source") == "authenticated_subscription_provider" and
            event.get("provider_state") == "confirmed_email_eligible" and
            event.get("user_marketing_consent") is True and
            event.get("is_suppressed") is False and
            bool(event.get("dedupe_confirmation_event_id")))


def realized_net_per_1000(cohort: Mapping):
    """Never divide by visitors until independently verified paid settlement exists."""
    if cohort.get("orders_independently_settled") is not True or cohort.get("qualified_sessions_verified") is not True:
        return None
    count = cohort.get("qualified_human_sessions")
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        return None
    fields = ("gross_settled_usd", "refunded_usd", "fees_usd")
    if any(type(cohort.get(k)) not in (int, float) for k in fields):
        return None
    gross, refunds, fees = (float(cohort[k]) for k in fields)
    if gross < 0 or refunds < 0 or fees < 0 or refunds + fees > gross:
        return None
    return round(1000 * (gross - refunds - fees) / count, 2)


def main():
    here = Path(__file__).resolve().parent
    source = here.parent / "campaign-2026-mind"
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    evidence = json.loads((here / "evidence_snapshot.json").read_text(encoding="utf-8"))
    ids = validate_original_files(source)
    decision = release_decisions(manifest, evidence)
    report = {"original_sha_verified": ids, "campaign": decision,
              "subscriber_counters_not_additive": True,
              "actual_eligible_recipient_count": None,
              "independently_verified_net_revenue": None,
              "net_revenue_per_1000_qualified_sessions": None}
    print(json.dumps(report, indent=2))
    return 0 if ids["byte_identical"] and all(i["status"] == "HOLD_UNSENT" for i in decision["issues"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
