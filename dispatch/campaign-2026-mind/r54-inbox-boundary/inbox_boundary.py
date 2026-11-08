"""Read-only WordPress excerpt boundary rehearsal, NEVER an email sender.

Models WordPress.com's documented 55-word *fallback* in excerpt mode when a
post has no custom excerpt. A custom excerpt uses its own text. Neither
simulation proves the actual Jetpack HTML, recipient view, legal footer,
preheader, eligibility or delivery. All six editions stay UNSENT.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

CAMPAIGN = Path(__file__).resolve().parents[1]
ISSUE_FILENAMES = (
    "01-the-mind-is-not-a-camera.md",
    "02-before-hypnosis-had-a-name.md",
    "03-the-twelve-minute-question.md",
    "04-the-hatch-and-the-spark.md",
    "05-before-you-press-play.md",
    "06-the-evidence-log.md",
)
COMMERCIAL = (3, 5)
FALLBACK_WORDS = 55
NO_SEND = "HOLD_UNSENT"
NO_MERCHANT = "HOLD_MERCHANT"
OFFICIAL_PROVIDER_REFERENCE = "https://wordpress.com/support/newsletter-settings/"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def editable_body(markdown: str) -> str:
    """Extract narrative between markdown delimiters, never drafting/legal header."""
    sections = re.split(r"(?m)^\s*---\s*$", markdown)
    if len(sections) != 3:
        raise ValueError("Unexpected issue structure: cannot isolate safe narrative")
    narrative = sections[1].strip()
    if not narrative or "Pre-send compliance block" in narrative:
        raise ValueError("Draft/legal-only text crossed the message boundary")
    return narrative


def visible_text(markdown: str) -> str:
    """Offline approximation of readable Markdown; not the Jetpack renderer."""
    text = re.sub(r"\[([^\]]+)\]\(([^)]*)\)", r"\1", markdown)
    text = re.sub(r"(?m)^\s*[-*]\s+", "", text)
    text = re.sub(r"(?m)^\s*#{1,6}\s+", "", text)
    text = re.sub(r"[*_]", "", text)
    text = text.replace(chr(96), "")
    return " ".join(text.split())


def fallback_preview(narrative: str, limit: int = FALLBACK_WORDS) -> str:
    """An explicit, *approximate* word-boundary model, not actual inbox evidence."""
    if limit < 1:
        raise ValueError("Word budget must be positive")
    return " ".join(visible_text(narrative).split()[:limit])


def financial_disclosure_visible(text: str) -> bool:
    """A royal commission is NOT a financial disclosure."""
    return bool(re.search(
        r"(?i)(?:commercial disclosure|affiliate evaluation|"
        r"may (?:earn|receive) (?:a )?commission|"
        r"we (?:may|could) earn (?:a )?commission)",
        text,
    ))


def disclosure_word_position(narrative: str) -> int | None:
    """Zero-based word offset of the explicit commercial-disclosure label."""
    clean = visible_text(narrative)
    m = re.search(r"(?i)\bCommercial disclosure\s*:", clean)
    if m is None:
        return None
    return len(clean[: m.start()].split())


def merchant_link_count(markdown: str) -> int:
    """Count directly clickable named-offer seller citations in original copy."""
    links = re.findall(r"\]\((https?://[^)\s]+)\)", markdown)
    return sum(
        1 for url in links
        if re.match(r"(?i)^https?://(?:www\.)?"
        r"(?:zen12\.com|hypnosislive\.com)(?:/|$)", url)
    )


def safe_editor_rehearsal(envelope: dict[str, Any]) -> bool:
    """Review-only guard. True NEVER means publish/send permission."""
    return (
        envelope.get("status") == "draft"
        and envelope.get("send_to_subscribers") is False
        and envelope.get("scheduled_at") is None
        and envelope.get("test_email_sent") is False
        and envelope.get("audience") == "NONE"
        and envelope.get("native_received_email") is False
        and envelope.get("founder_send_approval") is False
    )


def build_audit() -> dict[str, Any]:
    manifest = load_json(CAMPAIGN / "manifest.json")
    proposed = load_json(CAMPAIGN / "delivery" / "wordpress_excerpt_copy.json")
    observed = load_json(Path(__file__).with_name("snapshot.json"))
    if manifest.get("status") != "DRAFT_UNSENT_NO_SCHEDULING":
        raise ValueError("Campaign no longer in its approved draft-only state")
    if len(manifest["issues"]) != 6 or len(proposed["entries"]) != 6:
        raise ValueError("Original six-issue allocation changed")
    if proposed["status"] != "DRAFT_FOR_WORDPRESS_EDITOR_REVIEW_ONLY":
        raise ValueError("Custom excerpt proposal is no longer review-only")
    if observed["jetpack"]["email_content_format"] != "excerpt":
        raise ValueError("Observed email mode changed; reverify before extrapolating")

    editions: list[dict[str, Any]] = []
    for number, (metadata, name, optional) in enumerate(
        zip(manifest["issues"], ISSUE_FILENAMES, proposed["entries"]), 1
    ):
        if metadata["number"] != number or optional["number"] != number:
            raise ValueError("Manifest, canonical source, and optional excerpt disagree")
        if optional["subject"] != metadata["subject"]:
            raise ValueError("Proposed subject no longer agrees with manifest")
        body = (CAMPAIGN / "issues" / name).read_text(encoding="utf-8")
        if "**Subject:** " + metadata["subject"] not in body:
            raise ValueError("Canonical manuscript subject mismatch")
        if "**Preheader:** " + metadata["preheader"] not in body:
            raise ValueError("Canonical manuscript preheader mismatch")
        if metadata["publish_state"] != "hold" or metadata["merchant_affiliate_url"] is not None:
            raise ValueError("Unexpected publication or merchant activation in manifest")
        narrative = editable_body(body)
        fallback = fallback_preview(narrative)
        commercial = number in COMMERCIAL
        fallback_financial = financial_disclosure_visible(fallback)
        proposed_financial = financial_disclosure_visible(optional["excerpt"])
        if commercial and not proposed_financial:
            raise ValueError("Proposed commercial introduction lacks disclosure")
        if not commercial and proposed_financial:
            raise ValueError("Editorial introduction unexpectedly implies earning link")
        preview = {
            "number": number,
            "subject": metadata["subject"],
            "kind": metadata["kind"],
            "source_markdown": "issues/" + name,
            "first_55_words_fallback_model": fallback,
            "fallback_word_count": len(fallback.split()),
            "fallback_contains_explicit_financial_disclosure": fallback_financial,
            "proposed_custom_excerpt_not_installed": optional["excerpt"],
            "proposed_custom_excerpt_word_count": len(optional["excerpt"].split()),
            "proposed_contains_explicit_financial_disclosure": proposed_financial,
            "first_explicit_disclosure_zero_based_word": disclosure_word_position(narrative),
            "clickable_seller_citations_in_original": merchant_link_count(body),
            "original_primary_cta": metadata["editorial_cta"],
            "first_55_words_contains_primary_cta": metadata["editorial_cta"] in fallback,
            "native_preheader_verified": False,
            "native_received_email_verified": False,
            "release_state": NO_SEND,
            "merchant_state": NO_MERCHANT if commercial else "NOT_APPLICABLE",
        }
        editions.append(preview)

    return {
        "identity": "OFFLINE_APPROXIMATION_ONLY_NOT_AN_EMAIL",
        "readiness": NO_SEND,
        "underlying_official_rule": OFFICIAL_PROVIDER_REFERENCE,
        "current_settings_as_of": observed["jetpack"]["as_of"],
        "observed_mode": observed["jetpack"]["email_content_format"],
        "custom_excerpts_installed": False,
        "native_preview_performed": False,
        "received_jetpack_email_inspected": False,
        "real_unique_eligible_audience": None,
        "word_budget_used_for_fallback_model": FALLBACK_WORDS,
        "editions": editions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    result = build_audit()
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
