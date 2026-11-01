#!/usr/bin/env python3
"""Read-only R39 evidence: compare campaign copy with real Jetpack excerpt-mode risks.

This does NOT generate, publish, schedule, test-send, approve, or authorize email.
The 55-word computation is an illustrative DEFAULT excerpt, not a received email.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

CAMPAIGN = Path(__file__).resolve().parents[1]
EVIDENCE = Path(__file__).resolve().parent / "LIVE_READ_ONLY_EVIDENCE.json"
EXPECTED = {
    1: "01-the-mind-is-not-a-camera.md",
    2: "02-before-hypnosis-had-a-name.md",
    3: "03-the-twelve-minute-question.md",
    4: "04-the-hatch-and-the-spark.md",
    5: "05-before-you-press-play.md",
    6: "06-the-evidence-log.md",
}
BLOCKS = ("[[VALID_POSTAL_ADDRESS_REQUIRED]]",
          "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]")
DISALLOWED = ("hop.clickbank.net", "clickbank.net", "affiliates.inspire3.com")
MERCHANT_HOSTS = {"zen12.com", "hypnosislive.com", "www.zen12.com",
                  "www.hypnosislive.com"}
EXPECTED_KIND = {1: "editorial", 2: "editorial", 3: "commercial-review-pending",
                 4: "editorial", 5: "commercial-review-pending", 6: "editorial"}


def text_after_editorial_header(source: str) -> str:
    """Use only the story body, dropping the STOP banner / metadata / legal tail."""
    header, separator, _rest = source.partition("\n---\n")
    if not separator or header.count("\n") > 15 or "**Subject:**" not in header:
        raise ValueError("The first draft metadata-to-story separator is missing or misplaced")
    sections = re.split(r"(?m)^---\s*$", source, maxsplit=2)
    if len(sections) < 2:
        raise ValueError("Draft is missing the editorial-body boundary")
    return sections[1].strip()


def visible_text(text: str) -> str:
    text = re.sub(r"!\[([^]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^\s*#+\s*", "", text)
    text = re.sub(r"[*_`>]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def illustrative_55_words(text: str) -> str:
    return " ".join(visible_text(text).split()[:55])


def merchant_links(source: str) -> list[str]:
    urls = re.findall(r"https?://[^\s)\]>\"']+", source)
    result = []
    for url in urls:
        host = (urlparse(url).hostname or "").lower()
        if host in MERCHANT_HOSTS:
            result.append(url.rstrip(".,;"))
    return sorted(set(result))


def build_docket(campaign: Path = CAMPAIGN, evidence_path: Path = EVIDENCE) -> dict:
    manifest = json.loads((campaign / "manifest.json").read_text(encoding="utf-8"))
    proposals = json.loads((campaign / "delivery" / "wordpress_excerpt_copy.json").read_text(encoding="utf-8"))
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    settings = evidence["authenticated_wordpress"]
    issues = manifest["issues"]
    if manifest["status"] != "DRAFT_UNSENT_NO_SCHEDULING":
        raise ValueError("Campaign status drift: not draft-unsent")
    if len(issues) != 6 or [x["number"] for x in issues] != list(range(1, 7)):
        raise ValueError("Manifest not six distinct ordered issues")
    if len(proposals["entries"]) != 6:
        raise ValueError("Custom excerpt proposal length drift")
    if any(x["kind"] != EXPECTED_KIND[x["number"]] or x["publish_state"] != "hold" for x in issues):
        raise ValueError("Issue mix or hold-state drift")
    if settings["subscriptions"] is not True or settings["email_new_posts_by_default"] is not False:
        raise ValueError("Jetpack site newsletter/automatic-send status changed")
    if settings["email_content_format"] != "excerpt":
        raise ValueError("Delivery mode changed: first-55-word simulation invalid")
    if settings["recent_send_count"] != 0:
        raise ValueError("Unreported email send; re-audit production immediately")
    if any(evidence["proofs"][k] for k in evidence["proofs"]):
        raise ValueError("Read-only snapshot must not assert unverified proofs")
    if settings["subscriber_counts"] != {"total": 2, "confirmed": 2, "unconfirmed": 2}:
        raise ValueError("Counts changed: fresh private subscriber review required")

    results = []
    for issue, proposal in zip(issues, proposals["entries"]):
        n = issue["number"]
        if n != proposal["number"] or issue["subject"] != proposal["subject"]:
            raise ValueError("Subject or edition number drift")
        source = (campaign / "issues" / EXPECTED[n]).read_text(encoding="utf-8")
        if "**Subject:** " + issue["subject"] not in source:
            raise ValueError("Manuscript subject changed")
        if "**Preheader:** " + issue["preheader"] not in source:
            raise ValueError("Manifest preheader differs from manuscript")
        if "DO NOT PUBLISH OR EMAIL" not in source or not all(k in source for k in BLOCKS):
            raise ValueError("Fail-closed draft/legal markers missing")
        for bad in DISALLOWED:
            if bad in source.lower():
                raise ValueError("Unauthorized earning-link host detected")
        body = text_after_editorial_header(source)
        model = illustrative_55_words(body)
        banner_example = illustrative_55_words(source)
        proposed = proposal["excerpt"]
        merchant_urls = merchant_links(body)
        disclosure_in_default = ("commission" in model.lower() or "affiliate" in model.lower())
        disclosure_in_custom = ("commission" in proposed.lower() or "affiliate" in proposed.lower())
        if n in (3, 5) and not disclosure_in_custom:
            raise ValueError("Commercial custom excerpt lacks commission disclosure")
        if n not in (3, 5) and merchant_urls:
            raise ValueError("Direct merchant URL unexpectedly in editorial edition")
        results.append({
            "number": n, "kind": issue["kind"], "subject": issue["subject"],
            "planned_preheader": issue["preheader"],
            "planned_preheader_native_setting_verified": False,
            "default_55_word_story_simulation": model,
            "raw_markdown_55_word_simulation": banner_example,
            "raw_draft_warning_would_be_visible_if_pasted": "DO NOT PUBLISH" in banner_example,
            "commercial_disclosure_in_story_55_word_simulation": disclosure_in_default,
            "commercial_disclosure_in_proposed_custom_excerpt": disclosure_in_custom,
            "proposed_custom_excerpt": proposed,
            "custom_excerpt_placed_into_wordpress_post_verified": False,
            "direct_merchant_source_urls_in_canonical_body": merchant_urls,
            "approved_for_publication_or_email": False,
            "actual_received_email_verified": False,
            "release_status": "HOLD_MERCHANT_AND_UNSENT" if n in (3, 5) else "HOLD_UNSENT"
        })
    return {
        "model": "R39_READ_ONLY_NOT_RECEIVED_EMAIL",
        "source_screenshot_status": "NO_NATIVE_INBOX_PROOF",
        "default_excerpt_caveat": "55-word text is a rough illustrative model, not actual WordPress rendering.",
        "wordpress_observed_utc": evidence["observed_utc"],
        "subscriber_count_interpretation": "Non-additive counters; unique opted-in email eligible group UNKNOWN.",
        "custom_excerpts_not_installed": True,
        "actual_post_subject_header_preheader_footers": "NOT_VERIFIED",
        "six_issues": results,
        "all_six_hold": True,
        "commercial_03_and_05_hold": True,
        "transmission_or_wordpress_write_performed": False
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed, offline Dispatch/Jetpack review model")
    parser.add_argument("--json", action="store_true", help="print non-PII review JSON")
    args = parser.parse_args()
    report = build_docket()
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("DISPATCH R39 — ALL SIX HOLD_UNSENT; 03/05 HOLD_MERCHANT")
        for x in report["six_issues"]:
            print(f'{x["number"]:02d}: default55-disclosure={x["commercial_disclosure_in_story_55_word_simulation"]}; '
                  f'custom-excerpt-in-WP=NOT VERIFIED; merchant-source-URLs={len(x["direct_merchant_source_urls_in_canonical_body"])}')
        print("No native Jetpack email, sender/legal footer, or audience consent verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
