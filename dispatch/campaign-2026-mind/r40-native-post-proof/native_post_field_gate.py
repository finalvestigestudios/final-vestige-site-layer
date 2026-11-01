#!/usr/bin/env python3
"""R40: read-only WordPress post-field / Jetpack inbox evidence bridge.

This module NEVER authenticates with WordPress, writes, previews, sends or
approves a campaign. It validates *sanitized manual review snapshots* against
the original six-issue manifest and proposed custom excerpts. A good result
means field alignment ONLY, not inbox delivery, CAN-SPAM compliance, consent
or founder approval. See R40_README.md.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = Path(__file__).with_name("READ_ONLY_OBSERVATION.json")
ISSUES = {
    1: "01-the-mind-is-not-a-camera.md",
    2: "02-before-hypnosis-had-a-name.md",
    3: "03-the-twelve-minute-question.md",
    4: "04-the-hatch-and-the-spark.md",
    5: "05-before-you-press-play.md",
    6: "06-the-evidence-log.md",
}
KINDS = {
    1: "editorial", 2: "editorial", 3: "commercial-review-pending",
    4: "editorial", 5: "commercial-review-pending", 6: "editorial",
}
BLOCKERS = (
    "[[VALID_POSTAL_ADDRESS_REQUIRED]]",
    "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",
)
HOSTS = {"zen12.com", "hypnosislive.com"}
TRACKER_FRAGMENTS = ("hop.clickbank.net", "affiliates.inspire3.com", "clickbank.net")
UNAUTHORIZED_CMS_FLAGS = ("published", "sent", "approved", "scheduled")


def _text(value: object) -> str:
    """Normalize WordPress rendered/raw fields without trusting HTML as proof."""
    if isinstance(value, dict):
        value = value.get("raw", value.get("rendered", ""))
    if not isinstance(value, str):
        raise ValueError("WordPress field is not text")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def _urls(source: str) -> list[str]:
    urls = re.findall(r"https?://[^\s<>'\"\])]+", source, flags=re.I)
    return [u.rstrip(".,;") for u in urls]


def _is_seller_url(url: str) -> bool:
    try:
        domain = (urlsplit(url).hostname or "").lower()
    except ValueError:
        return True
    return any(domain == h or domain.endswith("." + h) for h in HOSTS)


def _load(campaign: Path = ROOT, evidence_path: Path = EVIDENCE) -> tuple[dict, dict, dict]:
    manifest = json.loads((campaign / "manifest.json").read_text(encoding="utf-8"))
    excerpts = json.loads((campaign / "delivery" / "wordpress_excerpt_copy.json").read_text(encoding="utf-8"))
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "DRAFT_UNSENT_NO_SCHEDULING":
        raise ValueError("Canonical campaign not firmly draft/unsent")
    issues = manifest.get("issues", [])
    entries = excerpts.get("entries", [])
    if len(issues) != 6 or len(entries) != 6:
        raise ValueError("Six-issue/excerpt correspondence broken")
    if [x["number"] for x in issues] != list(range(1, 7)):
        raise ValueError("Six canonical numbers altered")
    if (sum(x["kind"] == "editorial" for x in issues) != 4
            or sum(x["kind"] == "commercial-review-pending" for x in issues) != 2):
        raise ValueError("4:2 allocation altered")
    s = evidence["wordpress"]
    if not (s["subscriptions"] is True and s["email_new_posts_by_default"] is False
            and s["email_content_format"] == "excerpt" and s["recent_sends"] == 0):
        raise ValueError("WordPress delivery configuration drift; re-read source")
    if (s["subscriber_counts"] != {"total": 2, "confirmed": 2, "unconfirmed": 2}
            or s["unique_eligible"] != "UNKNOWN"):
        raise ValueError("Subscriber diagnostics must be reviewed privately")
    if any(v is not False for v in evidence["external_release_proofs"].values()):
        raise ValueError("Unverified external proof was asserted")
    for row, proposal in zip(issues, entries):
        n = row["number"]
        if row["kind"] != KINDS[n] or row["publish_state"] != "hold":
            raise ValueError("Release state/kind changed")
        if proposal["number"] != n or proposal["subject"] != row["subject"]:
            raise ValueError("Proposed excerpt has incorrect subject")
        excerpt = proposal["excerpt"]
        if not 35 <= len(excerpt.split()) <= 95:
            raise ValueError("Excerpt should be substantive and mobile-conscious")
        if n in (3, 5) and not ("commission" in excerpt.lower() and "affiliate" in excerpt.lower()):
            raise ValueError("Commercial excerpt missing explicit relationship disclosure")
        if "[[" in excerpt or any(_is_seller_url(u) for u in _urls(excerpt)):
            raise ValueError("Unapproved URL or template marker in excerpt")
        original = (campaign / "issues" / ISSUES[n]).read_text(encoding="utf-8")
        if ("DO NOT PUBLISH OR EMAIL" not in original or
                f"**Subject:** {row['subject']}" not in original or
                f"**Preheader:** {row['preheader']}" not in original or
                not all(b in original for b in BLOCKERS)):
            raise ValueError("Original subject, preheader, or legal hard-stop drift")
        if row["merchant_affiliate_url"] is not None:
            raise ValueError("Unexpected merchant earning link")
    return manifest, excerpts, evidence


def packets(campaign: Path = ROOT, evidence_path: Path = EVIDENCE) -> list[dict]:
    """One per-post *review instruction*, never an executable publishing job."""
    manifest, excerpts, _ = _load(campaign, evidence_path)
    items = []
    for issue, x in zip(manifest["issues"], excerpts["entries"]):
        commercial = issue["kind"] != "editorial"
        items.append({
            "number": issue["number"],
            "post_type_required": "post",
            "post_status_required": "draft",
            "post_title_required_as_native_subject": issue["subject"],
            "custom_excerpt_required": x["excerpt"],
            "custom_excerpt_not_installed": True,
            "planned_preheader_separate_jetpack_control_verified": False,
            "per_post_send_toggle_required": False,
            "per_post_send_toggle_verified": False,
            "source_manuscript": "issues/" + ISSUES[issue["number"]],
            "manifest_cta": issue["editorial_cta"],
            "first_party_guide_live": False if commercial else "SEE_PUBLISHED_EDITORIAL_DESTINATION_LEDGER",
            "edition_release": "HOLD_MERCHANT_AND_UNSENT" if commercial else "HOLD_UNSENT",
            "native_preview_verified": False,
            "received_email_verified": False,
            "legal_footer_verified": False,
            "commercial_partner_email_permission_verified": False,
            "founder_final_send_approval": False,
        })
    return items


def audit_manual_post_snapshot(packet: dict, candidate: dict) -> dict:
    """Inspect a redacted admin field snapshot; do not infer mail compliance.

    This is intentionally strict: a *field-aligned* draft can still NEVER be
    released without separate private recipient, legal, delivery, and founder
    evidence. No email addresses, tokens or subscriber exports are accepted.
    """
    problems = []
    def check(condition: bool, name: str) -> None:
        if not condition:
            problems.append(name)

    check(candidate.get("site") == "finalvestige.com", "wrong_site")
    check(candidate.get("post_type") == "post", "wrong_post_type")
    check(candidate.get("status") == "draft", "not_a_draft")
    try:
        check(_text(candidate.get("title")) == packet["post_title_required_as_native_subject"],
              "subject_drift")
        check(_text(candidate.get("excerpt")) == packet["custom_excerpt_required"],
              "custom_excerpt_missing_or_drifted")
        body = candidate.get("content")
        if isinstance(body, dict):
            body = body.get("raw", body.get("rendered", ""))
        check(isinstance(body, str) and len(_text(body)) >= 80, "empty_post_body")
        if isinstance(body, str):
            check(not any(s in body for s in ("DO NOT PUBLISH OR EMAIL", "[[",
                                              "Pre-send compliance block", "**Subject:**",
                                              "**Preheader:**")), "internal_editor_markers_exposed")
            check(not any(_is_seller_url(u) for u in _urls(body)), "direct_seller_route_bypass")
            check(not any(s in body.lower() for s in TRACKER_FRAGMENTS), "earning_link_not_authorized")
            check(not re.search(r"mailto:[^\s<'\"\)]+", body, flags=re.I),
                  "personally_addressed_link_or_token")
    except ValueError:
        problems.append("unparseable_native_field")
    check(candidate.get("send_this_post_to_subscribers") is False,
          "newsletter_toggle_must_remain_off")
    check(candidate.get("publication_scheduled") is False,
          "scheduled_post_not_allowed")
    for name in UNAUTHORIZED_CMS_FLAGS:
        check(candidate.get(name) is not True, "unauthorized_" + name)
    # Existence of a WordPress draft or preview is never a send or CAN-SPAM proof.
    return {
        "edition": packet["number"],
        "field_alignment": "PASS_REVIEW_FIELDS_ONLY" if not problems else "FAIL",
        "checks_failed": sorted(set(problems)),
        "legal_footer_and_functional_unsubscribe": "UNVERIFIED",
        "native_inbox_and_welcome": "UNVERIFIED",
        "recipient_consent": "UNKNOWN",
        "authorization": "HOLD_UNSENT",
    }


def assessment(campaign: Path = ROOT, evidence_path: Path = EVIDENCE) -> dict:
    observed = json.loads(evidence_path.read_text(encoding="utf-8"))
    return {
        "mode": "OFFLINE_REVIEW_ONLY_NO_WORDPRESS_WRITE_NO_EMAIL",
        "observed_utc": observed["observed_utc"],
        "preheader_native_ui": "UNVERIFIED",
        "featured_image_top_of_email_enabled": observed["wordpress"]["featured_image_in_email"],
        "post_date_byline_enabled": observed["wordpress"]["post_date_in_email"],
        "return_address_control": "WORDPRESS_PLATFORM_CONTROLLED_NOT_FV_DOMAIN",
        "subscriber_counts": "NON_ADDITIVE_2_2_2_UNIQUE_ELIGIBLE_UNKNOWN",
        "posts": packets(campaign, evidence_path),
        "approved_for_any_send": False,
        "new_platform": False,
        "publisher_action": "NONE",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    data = assessment()
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("R40: 6 review packets; 4 editorial, 2 commercial HOLD.")
        print("No real WordPress post fields or received email verified. All HOLD_UNSENT.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
