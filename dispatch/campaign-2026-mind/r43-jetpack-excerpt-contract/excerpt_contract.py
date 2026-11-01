#!/usr/bin/env python3
"""R43 read-only adjudication of generic WordPress versus Jetpack email excerpts.

NOT an inbox renderer, WordPress write client, publication gate or email sender.
See README.md for Oct 2026 provider-specific sources and unavoidable uncertainty.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPTS = {
    1: "01-the-mind-is-not-a-camera.md",
    2: "02-before-hypnosis-had-a-name.md",
    3: "03-the-twelve-minute-question.md",
    4: "04-the-hatch-and-the-spark.md",
    5: "05-before-you-press-play.md",
    6: "06-the-evidence-log.md",
}
COMMERCIAL = {3, 5}
EXPECTED_KINDS = ["editorial", "editorial", "commercial-review-pending",
                  "editorial", "commercial-review-pending", "editorial"]
SELLERS = {"zen12.com", "www.zen12.com", "hypnosislive.com",
           "www.hypnosislive.com"}
LEGAL_MARKERS = ("[[VALID_POSTAL_ADDRESS_REQUIRED]]",
                 "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]")
DOCS = {
    "jetpack_specific": "https://jetpack.com/support/newsletter/customize-the-newsletter-experience/",
    "wordpress_generic": "https://wordpress.com/support/excerpts/",
    "jetpack_preview": "https://jetpack.com/support/newsletter/",
    "ftc_can_spam": "https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",
}


def story_section(markdown: str) -> str:
    """Return story without the author-only STOP header and legal release footer."""
    parts = re.split(r"(?m)^---[ \t]*$", markdown)
    if len(parts) < 3 or "**Subject:**" not in parts[0] or "DO NOT PUBLISH" not in parts[0]:
        raise ValueError("Missing draft boundary/STOP header; do not preview or transmit")
    return parts[1].strip()


def plain_preview(markdown: str) -> str:
    """Lightweight counterfactual; NOT Jetpack's actual block/HTML normalization."""
    s = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", markdown)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"(?m)^\s*#{1,6}\s*", "", s)
    s = re.sub(r"(?m)^\s*[-*]\s+", "", s)
    s = re.sub(r"[*_`>]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def diagnostic_models(clean_text: str, raw_text: str, custom_excerpt: str) -> dict:
    """55-words is generic WordPress; 350-chars is provider Jetpack reference.

    Both are approximations because uploaded WordPress block markup and email
    transformations are unobserved. An entered custom excerpt is a *third*
    path, never proof of the fields in an unpublished post.
    """
    body = plain_preview(clean_text)
    raw = plain_preview(raw_text)
    if not body:
        raise ValueError("Empty story")
    if not custom_excerpt.strip():
        raise ValueError("Empty custom excerpt candidate")
    return {
        "generic_wordpress_55_word_model": " ".join(body.split()[:55]),
        "jetpack_documented_350_character_model": body[:350],
        "raw_markdown_mistake_350_character_model": raw[:350],
        "proposed_custom_excerpt_model": custom_excerpt.strip(),
        "proposed_custom_excerpt_first_350_display_characters": custom_excerpt.strip()[:350],
        "clean_story_has_no_draft_banner": "DO NOT PUBLISH" not in body[:350],
        "raw_copy_exposes_draft_banner": "DO NOT PUBLISH" in raw[:350],
        "character_model_has_disclosure": bool(re.search(r"affiliate|commission", body[:350], re.I)),
        "word_model_has_disclosure": bool(re.search(r"affiliate|commission", " ".join(body.split()[:55]), re.I)),
        "custom_excerpt_has_disclosure": bool(re.search(r"affiliate|commission", custom_excerpt, re.I)),
        "custom_excerpt_first_350_has_disclosure": bool(re.search(r"affiliate|commission", custom_excerpt[:350], re.I)),
    }


def merchant_links(markdown: str) -> list[str]:
    urls = re.findall(r"https?://[^\s)\]>'\"]+", markdown)
    return sorted({url.rstrip(".,;") for url in urls
                   if (urlparse(url).hostname or "").lower() in SELLERS})


def audit(root: Path = ROOT) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    excerpts = json.loads((root / "delivery" / "wordpress_excerpt_copy.json").read_text(encoding="utf-8"))
    issues = manifest["issues"]
    if manifest["status"] != "DRAFT_UNSENT_NO_SCHEDULING" or len(issues) != 6:
        raise ValueError("Canonical campaign is no longer six held drafts")
    if [x["number"] for x in issues] != [1, 2, 3, 4, 5, 6]:
        raise ValueError("Issue ordering/identity changed")
    if [x["kind"] for x in issues] != EXPECTED_KINDS:
        raise ValueError("Approved 4:2 allocation changed")
    if any(x["publish_state"] != "hold" or x["merchant_affiliate_url"] is not None for x in issues):
        raise ValueError("A manifest release or earning link has been activated")
    entries = excerpts["entries"]
    if len(entries) != 6 or [e["number"] for e in entries] != [1, 2, 3, 4, 5, 6]:
        raise ValueError("Optional excerpts no longer align 1:1 with six editions")

    out = []
    for issue, entry in zip(issues, entries):
        n = issue["number"]
        if entry["subject"] != issue["subject"]:
            raise ValueError("Canonical subject / custom excerpt drift")
        content = (root / "issues" / MANUSCRIPTS[n]).read_text(encoding="utf-8")
        if "**Subject:** " + issue["subject"] not in content:
            raise ValueError("Manuscript subject mismatch")
        if "**Preheader:** " + issue["preheader"] not in content:
            raise ValueError("Preheader content drift")
        if not all(marker in content for marker in LEGAL_MARKERS):
            raise ValueError("Legal release placeholders absent")
        if "DO NOT PUBLISH OR EMAIL" not in content or "hop.clickbank.net" in content.lower():
            raise ValueError("STOP banner missing or unauthorized earning URL")
        models = diagnostic_models(story_section(content), content, entry["excerpt"])
        links = merchant_links(story_section(content))
        if n not in COMMERCIAL and links:
            raise ValueError("Noncommercial edition unexpectedly links to seller")
        if n in COMMERCIAL and not models["custom_excerpt_first_350_has_disclosure"]:
            raise ValueError("Commercial optional excerpt lacks early disclosure")
        out.append({
            "number": n, "subject": issue["subject"], "kind": issue["kind"],
            "models": models,
            "canonical_merchant_citation_urls": links,
            "planned_preheader_native_verified": False,
            "optional_custom_excerpt_installed": False,
            "actual_received_jetpack_email_verified": False,
            "legal_footer_and_optout_verified": False,
            "founder_approved_to_send": False,
            "release": "HOLD_MERCHANT_AND_UNSENT" if n in COMMERCIAL else "HOLD_UNSENT"
        })
    return {
        "status": "R43_OFFLINE_DIAGNOSTIC_ONLY_ALL_SIX_HOLD",
        "interpretation": "55 WORDS describes generic post excerpts; Jetpack email documentation specifies 350 CHARACTERS when a post has no entered excerpt. Neither model is a received email.",
        "sources": DOCS,
        "read_only": True,
        "wordPress_posts_created": False,
        "emails_sent_or_test_sent": False,
        "raw_subscriber_data_accessed": False,
        "live_sender_address_or_unsubscribe_proof": False,
        "email_content_format_observed": "excerpt",
        "actual_eligible_recipient_count": None,
        "editions": out,
    }


if __name__ == "__main__":
    report = audit()
    print(json.dumps(report, indent=2, ensure_ascii=False))
