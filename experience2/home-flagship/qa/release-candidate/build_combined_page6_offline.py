#!/usr/bin/env python3
"""Build an OFFLINE, review-only Gutenberg page-6 candidate from an exact local export.

Combines the existing NYPL rights-safe image-withholding transformer with the
existing contrast-safe Margins CSS. No WordPress API, HTTP, credentials,
publication, plugin activation, or site mutations are implemented here.
DO NOT commit a production page export or a generated candidate to Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = HERE.parents[1]
sys.path.insert(0, str(HOME / "rights"))
from withhold_unverified_nypl_capture import (  # noqa: E402
    NYPL_FILE, NYPL_RECORD, UNVERIFIED_CLAIM, UnsafeCandidate, patch_homepage,
)

CSS_PATH = HOME / "accessibility/margins/margin_strip_contrast_safe.css"
MARKER = "/* FV-EX2 PAGE6 REVIEW-ONLY: integrated accessible Margins CSS; NOT PUBLISHED */"
CLOSE_BLOCK = "<!-- /wp:html -->"
CLOSE_STYLE = "</style>"
MIN_CSS_TOKENS = (
    ".fv-margin-strip--rotator .fv-margin-strip__item",
    "@keyframes fvMarginContrastSafe",
    "animation-timing-function: steps(1, end)",
    "visibility: hidden",
    "visibility: visible",
    "opacity: 1",
    "filter: none",
    "prefers-reduced-motion: reduce",
    "animation: none",
)
REJECT_CSS = ("@import", "url(", "expression(", "javascript:", "</style", "<script", "<!--")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_css(css: str) -> None:
    if not css.strip() or any(token not in css for token in MIN_CSS_TOKENS):
        raise UnsafeCandidate("Contrast candidate is incomplete or has drifted")
    if any(token in css.lower() for token in REJECT_CSS):
        raise UnsafeCandidate("Refusing executable, external or HTML-like CSS")


def structural_inventory(raw: str) -> dict:
    return {
        "margin_indices": [
            int(x) for x in re.findall(
                r'<span class="fv-margin-strip__item" style="--i:(\d+)">', raw
            )
        ],
        "html_blocks": raw.count("<!-- wp:html -->"),
        "html_block_ends": raw.count(CLOSE_BLOCK),
        "inline_scripts": raw.count("<script>"),
        "inline_styles": raw.count("<style>"),
        "jetpack_subscription_blocks": raw.count("jetpack/subscriptions"),
        "focus_fieldbook_occurrences": raw.count("Focus Fieldbook"),
        "nypl_catalog_links": raw.count(NYPL_RECORD),
        "archive_image_controls": raw.count("data-fv-archive-img"),
        "chapter_nav_marker": raw.count('class="fv-hf__chapter-nav"'),
    }


def build_candidate(raw: str, css: str) -> tuple[str, dict]:
    """Return an exact-preservation review candidate; never modify source."""
    validate_css(css)
    if MARKER in raw or "fvMarginContrastSafe" in raw:
        raise UnsafeCandidate("Already patched or source unexpectedly changed")
    before = structural_inventory(raw)
    if before["margin_indices"] != list(range(72)):
        raise UnsafeCandidate("72 Margins records missing/reordered")
    if before["jetpack_subscription_blocks"] != 1:
        raise UnsafeCandidate("Native Jetpack subscription source drift")
    if before["html_blocks"] < 2 or before["html_blocks"] != before["html_block_ends"]:
        raise UnsafeCandidate("Gutenberg HTML block boundary drift")
    if before["focus_fieldbook_occurrences"] < 1:
        raise UnsafeCandidate("Focus Fieldbook missing")
    if before["chapter_nav_marker"] != 1:
        raise UnsafeCandidate("Seven-chapter navigation source drift")
    if raw.count(NYPL_FILE) < 2 or raw.count(UNVERIFIED_CLAIM) != 1:
        raise UnsafeCandidate("Rights source drift")

    rights, rights_report = patch_homepage(raw)
    boundary = rights.find(CLOSE_BLOCK)
    if boundary < 0 or not rights.startswith("<!-- wp:html -->"):
        raise UnsafeCandidate("Margins is no longer the first Gutenberg HTML block")
    first = rights[:boundary]
    if (first.count("<style>") != 1 or first.count(CLOSE_STYLE) != 1
            or ".fv-margin-strip" not in first
            or "@keyframes fvMarginReveal" not in first):
        raise UnsafeCandidate("Unreviewed first Margins stylesheet structure")

    insert = "\n" + MARKER + "\n" + css.rstrip() + "\n"
    repaired_first = first.replace(CLOSE_STYLE, insert + CLOSE_STYLE, 1)
    combined = repaired_first + rights[boundary:]

    # The combined candidate MUST be exactly the rights-only candidate plus
    # one insertion into the original first Margins style block.
    if combined.replace(insert, "", 1) != rights or combined.count(MARKER) != 1:
        raise UnsafeCandidate("Combined candidate changed unrelated markup")
    after = structural_inventory(combined)
    for key in (
        "margin_indices", "html_blocks", "html_block_ends", "inline_scripts",
        "inline_styles", "jetpack_subscription_blocks",
        "focus_fieldbook_occurrences", "nypl_catalog_links",
        "chapter_nav_marker",
    ):
        if before[key] != after[key]:
            raise UnsafeCandidate(f"Protected source changed: {key}")
    if before["archive_image_controls"] - after["archive_image_controls"] != 1:
        raise UnsafeCandidate("Unexpected archival image difference")
    if NYPL_FILE in combined or UNVERIFIED_CLAIM in combined:
        raise UnsafeCandidate("Unverified NYPL reproduction or rights claim persists")
    if combined.count("@keyframes fvMarginContrastSafe") != 1:
        raise UnsafeCandidate("Marginal contrast override duplicated")

    return combined, {
        "decision": "OFFLINE_REVIEW_CANDIDATE_ONLY_RELEASE_HOLD",
        "site": "finalvestige.com",
        "wordpress_page_id": 6,
        "wordpress_writes": 0,
        "source_sha256": sha(raw.encode("utf-8")),
        "candidate_sha256": sha(combined.encode("utf-8")),
        "contrast_css_sha256": sha(css.encode("utf-8")),
        "source_utf8_bytes": len(raw.encode("utf-8")),
        "candidate_utf8_bytes": len(combined.encode("utf-8")),
        "protected_before": {k: v for k, v in before.items() if k != "margin_indices"},
        "protected_after": {k: v for k, v in after.items() if k != "margin_indices"},
        "margin_indices_preserved": before["margin_indices"] == after["margin_indices"],
        "nypl_source_links_retained": after["nypl_catalog_links"],
        "rights_transform_report_sha256": sha(json.dumps(
            rights_report, sort_keys=True).encode("utf-8")),
        "manual_wcag_22_aa": "NOT_QUALIFIED",
        "gutenberg_save_readback": "NOT_PERFORMED",
        "safari_200pct_zoom_physical_devices": "NOT_TESTED",
        "image_rights_approval": "HOLD",
        "lighthouse_field_cwv": "NOT_MEASURED",
        "independent_qd": "HOLD",
        "founder_release_approval": "NOT_GRANTED",
        "production_release": "HOLD",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--css", type=Path, default=CSS_PATH)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{64}", args.expected_sha256):
        parser.error("Provide independently verified lowercase SHA-256")
    paths = [p.resolve() for p in (args.source, args.output, args.report)]
    if len(set(paths)) != 3:
        parser.error("Inputs and outputs must be distinct paths")
    if args.output.exists() or args.report.exists():
        parser.error("Refusing to overwrite an existing candidate or report")
    raw_bytes = args.source.read_bytes()
    if sha(raw_bytes) != args.expected_sha256:
        parser.error("Production raw export SHA-256 mismatch; no outputs written")
    raw = raw_bytes.decode("utf-8")
    css = args.css.read_text(encoding="utf-8")
    combined, receipt = build_candidate(raw, css)
    # Never include a full public page or any personal information in the report.
    # Keep candidate locally; do NOT upload it to public GitHub Actions artifacts.
    with args.output.open("xb") as target:
        target.write(combined.encode("utf-8"))
    with args.report.open("xb") as output:
        output.write((json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
