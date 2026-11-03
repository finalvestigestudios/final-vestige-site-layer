#!/usr/bin/env python3
"""Offline, fail-closed NYPL image-rights remediation for WP homepage page ID 6.

This script reads a LOCAL COPY of raw Gutenberg markup only. It has NO WordPress
API, networking, publishing, installation, or deployment abilities. The user
must independently approve any eventual production change.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

NYPL_FILE = "edit-017-v02-nypl-5003296-original.jpg"
NYPL_RECORD = "https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0"
UNVERIFIED_CLAIM = (
    "<strong>Credit:</strong> From The New York Public Library. "
    "NYPL believes this item is in the public domain under United States law."
)
REVIEWED_CREDIT = (
    "<strong>Source:</strong> From The New York Public Library; 1903 Brooklyn "
    "Rapid Transit system map, catalog item 5003296. "
    "<strong>Reuse:</strong> The digital image's specific rights status "
    "is not verified. The reproduction is withheld pending review."
)
ORIGINAL_CAPTION = (
    "<strong>Image:</strong> Brooklyn Rapid Transit system map, 1903; "
    "NYPL Digital Collections item 5003296, as published in Final Vestige's Malbone investigation."
)
REPLACEMENT_CAPTION = (
    "<strong>Catalog record:</strong> Brooklyn Rapid Transit system map, 1903; "
    "NYPL Digital Collections item 5003296. The source is linked, not reproduced here."
)
ARTICLE = re.compile(
    r'<article class="fv-hf__case" data-fv-case="malbone"[^>]*>.*?</article>',
    re.DOTALL,
)
IMG = re.compile(r'<img\b[^>]*\bdata-fv-archive-img\b[^>]*>', re.DOTALL)
MARGINS = re.compile(r'<span class="fv-margin-strip__item" style="--i:(\d+)">')
MARKER = '<span class="fv-hf__case-image-fallback">'
SAFE_FALLBACK_MARKER = ('<span class="fv-hf__case-image-fallback" '
    'style="left:clamp(16px,6%,72px);right:clamp(16px,6%,72px);'
    'width:auto;font-size:clamp(17px,2.4vw,30px);overflow-wrap:break-word">')
BINARY_LABEL = "ARCHIVE IMAGE 03 / NYPL 5003296"
RECORD_LABEL = "NYPL RECORD 03 / 5003296"


class UnsafeCandidate(ValueError):
    """The source differs from the narrowly reviewed published markup."""


def invariants(raw: str) -> dict:
    """Preserve Gutenberg, 72 source fragments, Jetpack and Focus resources."""
    records = [int(i) for i in MARGINS.findall(raw)]
    if records != list(range(72)):
        raise UnsafeCandidate("Missing, duplicated or reordered Margins records")
    markers = {
        "gutenberg": "<!-- wp:html -->",
        "flagship": 'data-fv-home-flagship',
        "jetpack": "<!-- wp:jetpack/subscriptions",
        "focus": "Focus Fieldbook",
        "chapter_navigation": 'fv-hf__chapter-',
        "malbone_source": NYPL_RECORD,
        "apollo": 'data-fv-case="apollo"',
        "franklin": 'data-fv-case="franklin"',
    }
    missing = [name for name, phrase in markers.items() if phrase not in raw]
    if missing:
        raise UnsafeCandidate("Required source components absent: " + ", ".join(missing))
    if raw.count(NYPL_RECORD) < 2:
        raise UnsafeCandidate("The accessible NYPL source links are missing")
    return {
        "margins": len(records),
        "jetpack": raw.count("jetpack/subscriptions"),
        "focus": raw.count("Focus Fieldbook"),
        "catalog_links": raw.count(NYPL_RECORD),
        "image_controls": len(IMG.findall(raw)),  # actual <img> tags, not JS selector strings
    }


def patch_homepage(raw: str) -> tuple[str, dict]:
    """Create a rights-safe *local candidate*, never apply it to WordPress."""
    before = invariants(raw)
    matches = list(ARTICLE.finditer(raw))
    if len(matches) != 1:
        raise UnsafeCandidate(f"Expected exactly one Malbone article, found {len(matches)}")
    match = matches[0]
    segment = match.group(0)

    if segment.count(MARKER) != 1 or segment.count(BINARY_LABEL) != 1:
        raise UnsafeCandidate("The original accessible image fallback has changed")
    imgs = [m for m in IMG.finditer(segment) if NYPL_FILE in m.group(0)]
    if len(imgs) != 1:
        raise UnsafeCandidate(f"Expected one exact NYPL image, found {len(imgs)}")
    image = imgs[0].group(0)
    if "src=" not in image or "srcset=" not in image:
        raise UnsafeCandidate("The expected NYPL src/srcset boundary has changed")
    if raw.count(NYPL_FILE) != image.count(NYPL_FILE):
        raise UnsafeCandidate("NYPL binary referenced outside the reviewed image")
    if segment.count(UNVERIFIED_CLAIM) != 1:
        raise UnsafeCandidate("Unverified public-domain wording has changed")
    if segment.count(ORIGINAL_CAPTION) != 1:
        raise UnsafeCandidate("Source caption has changed")
    if NYPL_RECORD not in segment:
        raise UnsafeCandidate("Linked primary source missing from article")

    # With the image removed, the original 1903/NYPL text fallback becomes
    # visible; keep its exact typography, source link, no-JS semantics and
    # all surrounding evidence chronology intact.
    edited = segment.replace(image, "", 1)
    edited = edited.replace(UNVERIFIED_CLAIM, REVIEWED_CREDIT, 1)
    edited = edited.replace(ORIGINAL_CAPTION, REPLACEMENT_CAPTION, 1)
    edited = edited.replace(BINARY_LABEL, RECORD_LABEL, 1)
    edited = edited.replace(MARKER, SAFE_FALLBACK_MARKER, 1)
    candidate = raw[: match.start()] + edited + raw[match.end() :]

    after = invariants(candidate)
    for key in ("margins", "jetpack", "focus", "catalog_links"):
        if after[key] != before[key]:
            raise UnsafeCandidate(f"Protected homepage inventory changed: {key}")
    if before["image_controls"] - after["image_controls"] != 1:
        raise UnsafeCandidate("Expected precisely one image-control removal")
    if NYPL_FILE in candidate or UNVERIFIED_CLAIM in candidate:
        raise UnsafeCandidate("Unreviewed image binary or rights claim remains")

    return candidate, {
        "status": "OFFLINE_REVIEW_ONLY_NOT_PUBLISHED",
        "scope": "Published homepage page 6, Malbone image only",
        "source_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "candidate_sha256": hashlib.sha256(candidate.encode("utf-8")).hexdigest(),
        "source_length": len(raw.encode("utf-8")),
        "candidate_length": len(candidate.encode("utf-8")),
        "changes": ["NYPL reproduction img + srcset removed",
                    "unverified public-domain claim replaced",
                    "source caption rewritten without binary",
                    "decorative frame relabeled source record"],
        "protected_before": before,
        "protected_after": after,
        "catalog_link": NYPL_RECORD,
        "production_writes": 0,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True,
                    help="Local raw Gutenberg homepage markup; never a WordPress URL")
    ap.add_argument("--output", type=Path, required=True,
                    help="Separate local review candidate; NEVER a live WordPress path")
    ap.add_argument("--expected-sha256", required=True,
                    help="Independent SHA-256 of authorized page-6 raw export")
    ap.add_argument("--report", type=Path, required=True,
                    help="Local JSON report containing no page contents")
    args = ap.parse_args()
    if args.source.resolve() in {args.output.resolve(), args.report.resolve()}:
        ap.error("Refusing to overwrite source or use source as report")
    if len(args.expected_sha256) != 64 or not all(c in "0123456789abcdef" for c in args.expected_sha256):
        ap.error("Expected lowercase 64-character source SHA-256")
    raw_bytes = args.source.read_bytes()
    actual = hashlib.sha256(raw_bytes).hexdigest()
    if actual != args.expected_sha256:
        ap.error("Exact source SHA-256 mismatch; abort without writing candidate")
    raw = raw_bytes.decode("utf-8")  # Do not normalize Windows CRLF.
    candidate, report = patch_homepage(raw)
    if args.output.exists() or args.report.exists():
        ap.error("Output/report already exists; refuse overwrite")
    args.output.write_bytes(candidate.encode("utf-8"))
    args.report.write_bytes((json.dumps(report, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
