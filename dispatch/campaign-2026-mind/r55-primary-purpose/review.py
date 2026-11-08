"""Read-only FTC primary-purpose triage and exact-merchant claim-routing audit.

NEVER a legal determination, sending permission, subscriber export, or metric collector.
Reads ONLY already source-controlled material. Python standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL = {3, 5}
EDITORIAL = {1, 2, 4, 6}
POSTAL = "[[VALID_POSTAL_ADDRESS_REQUIRED]]"
UNSUB = "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"
DIRECT_SELLER = re.compile(
    r"https?://(?:www\.)?(?:zen12\.com|hypnosislive\.com|inspire3\.com)(?:/|$)",
    re.IGNORECASE,
)
MONEY_AMOUNT = re.compile(r"(?<!\w)\$\s?\d+(?:[.,]\d+)?")
FINANCIAL_RELATIONSHIP = re.compile(
    r"\b(?:may|might|could)\s+(?:earn|receive|make)\s+(?:a\s+)?commission\b"
    r"|\b(?:affiliate\s+link|paid\s+recommendation|commercial\s+disclosure)\b",
    re.IGNORECASE,
)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def narrative_from_markdown(markdown: str) -> str:
    """Return the authored narrative, excluding draft headers and legal hard stops."""
    parts = re.split(r"(?m)^\s*---\s*$", markdown, maxsplit=2)
    if len(parts) < 2:
        raise ValueError("missing narrative separator")
    return parts[1].split("**Pre-send compliance block", 1)[0].strip()


def email_text_approximation(narrative: str) -> str:
    """A source-text model, NOT a native Jetpack excerpt implementation."""
    without_links = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", narrative)
    without_markup = re.sub(r"[*_#]+", "", without_links)
    return re.sub(r"\s+", " ", without_markup).strip()


def first_words(narrative: str, n: int = 55) -> str:
    """Approximate first n words only; WP actual WordPress rendering NOT verified."""
    if n <= 0:
        raise ValueError("word boundary must be positive")
    return " ".join(email_text_approximation(narrative).split()[:n])


def has_disclosure(text: str) -> bool:
    """Narrow semantic flag, not a legal finding or claim of reader comprehension."""
    return bool(FINANCIAL_RELATIONSHIP.search(text))


def merchant_domains(text: str) -> list[str]:
    matches = DIRECT_SELLER.findall(text)
    # We deliberately preserve occurrence counts: multiple seller citations matter.
    return [m.lower() for m in matches]


def classify_for_human_review(number: int) -> str:
    """Risk queue only. FTC primary purpose requires assessment of the final email."""
    if number in COMMERCIAL:
        return "COMMERCIAL_PRIMARY_PURPOSE_HUMAN_REVIEW"
    if number in EDITORIAL:
        return "EDITORIAL_OR_MIXED_PRIMARY_PURPOSE_HUMAN_REVIEW"
    raise ValueError("unknown edition")


def scan_issue(entry: dict, markdown: str) -> dict:
    number = entry["number"]
    narrative = narrative_from_markdown(markdown)
    snippet = first_words(narrative)
    exact_target = entry["editorial_cta"]
    is_commercial = number in COMMERCIAL
    seller_occurrences = merchant_domains(narrative)
    explicit_disclosure = has_disclosure(narrative)
    excerpt_disclosure = has_disclosure(snippet)
    hard_stops = [
        "FOUNDER_FINAL_SEND_APPROVAL_ABSENT",
        "ACTUAL_RECEIVED_JETPACK_MIME_ABSENT",
        "VALID_FINAL_VESTIGE_POSTAL_ADDRESS_UNVERIFIED",
        "FUNCTIONAL_RECEIVED_UNSUBSCRIBE_UNVERIFIED",
        "DISTINCT_CONSENT_ELIGIBLE_AUDIENCE_UNKNOWN",
    ]
    if is_commercial:
        hard_stops += [
            "NAMED_PRODUCT_PUBLISHER_EMAIL_PERMISSION_UNVERIFIED",
            "APPROVED_LIVE_FIRST_PARTY_BUYER_GUIDE_ABSENT",
            "AUTHORIZED_TRACKED_EARNING_URL_ABSENT",
            "CURRENT_CHECKOUT_AND_REFUND_UNVERIFIED",
        ]
        if not excerpt_disclosure:
            hard_stops.append("MODELED_EXCERPT_HAS_NO_FINANCIAL_DISCLOSURE")
        if seller_occurrences:
            hard_stops.append("DIRECT_SELLER_CITATIONS_BYPASS_UNAPPROVED_BUYER_GUIDE")
    source_errors = []
    expected_kind = "commercial-review-pending" if is_commercial else "editorial"
    if entry["kind"] != expected_kind:
        source_errors.append("EDITION_KIND_NOT_CANONICAL")
    if POSTAL not in markdown or UNSUB not in markdown:
        source_errors.append("LEGAL_PLACEHOLDER_BROKEN")
    if f"**Subject:** {entry['subject']}" not in markdown:
        source_errors.append("SUBJECT_NOT_CANONICAL")
    if f"**Preheader:** {entry['preheader']}" not in markdown:
        source_errors.append("PREHEADER_NOT_CANONICAL")
    if exact_target not in narrative:
        source_errors.append("PRIMARY_CTA_NOT_IN_NARRATIVE")
    if entry["publish_state"] != "hold" or entry["merchant_affiliate_url"] is not None:
        source_errors.append("RELEASE_STATE_NOT_HELD")
    if is_commercial:
        if not explicit_disclosure:
            source_errors.append("FINANCIAL_DISCLOSURE_MISSING")
        if not exact_target.startswith("[[APPROVED_"):
            source_errors.append("MERCHANT_GUIDE_PLACEHOLDER_MISSING")
    else:
        parsed = urlparse(exact_target)
        if parsed.scheme != "https" or parsed.netloc != "finalvestige.com":
            source_errors.append("EDITORIAL_CTA_NOT_FIRST_PARTY_HTTPS")
    return {
        "issue": number,
        "subject": entry["subject"],
        "preheader": entry["preheader"],
        "type": entry["kind"],
        "primary_purpose_triage_not_a_legal_determination": classify_for_human_review(number),
        "modeled_first_55_words": snippet,
        "modeled_excerpt_discloses_financial_connection": excerpt_disclosure,
        "full_manuscript_discloses_financial_connection": explicit_disclosure,
        "direct_merchant_link_occurrences_in_narrative": len(seller_occurrences),
        "unverified_price_quoted_in_narrative": bool(MONEY_AMOUNT.search(narrative)),
        "canonical_cta": exact_target,
        "source_errors": source_errors,
        "hard_holds": sorted(set(hard_stops)),
        "send_allowed": False,
        "email_preview_is_received_mime": False,
        "legal_compliance_verified": False,
    }


def audit(root: Path = ROOT) -> dict:
    manifest = _read_json(root / "manifest.json")
    register = _read_json(root / "r55-primary-purpose/merchant_evidence.json")
    if manifest.get("status") != "DRAFT_UNSENT_NO_SCHEDULING":
        raise ValueError("campaign status changed")
    entries = manifest["issues"]
    if [i["number"] for i in entries] != list(range(1, 7)):
        raise ValueError("canonical order changed")
    if manifest.get("mix") != {"editorial": 4, "commercial_review_pending": 2}:
        raise ValueError("original 4:2 mix changed")
    if not set(register["products"]) == {"Zen12", "Total Focus"}:
        raise ValueError("unexpected product evidence registry")
    for p in register["products"].values():
        if any(p[key] for key in (
            "final_vestige_accepted", "specific_email_channel_permission",
            "approved_earning_url", "final_checkout_verified",
            "refund_applies_to_current_cart_verified",
            "approved_creative_rights", "approved_live_first_party_guide",
        )):
            raise ValueError("merchant evidence may not be self-approved")
    reports = []
    for entry in entries:
        file = root / "issues" / f"{entry['number']:02d}-{entry['slug']}.md"
        reports.append(scan_issue(entry, file.read_text(encoding="utf-8")))
    return {
        "schema": 1,
        "status": "ALL_SIX_HOLD_UNSENT",
        "commercial_slots": [3, 5],
        "original_four_editorial_two_commercial": True,
        "final_vestige_eligible_unique_audience": None,
        "observed_wordpress_counts": {"total": 2, "confirmed": 2, "unconfirmed": 2},
        "counts_are_additive": False,
        "recent_sends_empty_not_lifetime_zero": True,
        "merchant_status": "BOTH_HOLD_MERCHANT",
        "native_received_email_verified": False,
        "source_errors": [e for issue in reports for e in issue["source_errors"]],
        "issues": reports,
        "send_allowed": False,
        "report_is_not_legal_or_deliverability_signoff": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true",
                        help="Fail if canonical manuscript/source drift is detected.")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return int(args.strict and bool(report["source_errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
