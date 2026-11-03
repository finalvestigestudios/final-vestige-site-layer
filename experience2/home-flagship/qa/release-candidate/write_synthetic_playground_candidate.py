#!/usr/bin/env python3
"""Produce only a SYNTHETIC EX2 Gutenberg candidate for isolated WordPress QA.

Never reads WordPress credentials, network, production exports, or live content.
The manifest is intentionally small and contains no Gutenberg markup.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_combined_page6_offline import build_candidate, structural_inventory, CSS_PATH
from test_build_combined_page6_offline import source_fixture


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_fixture(output: Path, manifest: Path) -> dict:
    if output.resolve() == manifest.resolve():
        raise ValueError("Candidate and manifest must be different files")
    if output.exists() or manifest.exists():
        raise FileExistsError("Never overwrite a pre-existing fixture or manifest")
    raw = source_fixture()  # Explicitly synthetic fixture from the existing tests
    css = CSS_PATH.read_text(encoding="utf-8")
    candidate, receipt = build_candidate(raw, css)
    before = structural_inventory(raw)
    after = structural_inventory(candidate)
    if before["margin_indices"] != list(range(72)) or after["margin_indices"] != list(range(72)):
        raise ValueError("Synthetic 72-record preservation failed")
    if receipt["production_release"] != "HOLD" or receipt["wordpress_writes"] != 0:
        raise ValueError("Unexpected release decision or WordPress side effect")
    contents = candidate.encode("utf-8")
    evidence = {
        "data_classification": "SYNTHETIC_TEST_FIXTURE_ONLY",
        "release": "HOLD",
        "page6_live_content_included": False,
        "candidate_sha256": sha(contents),
        "candidate_bytes": len(contents),
        "margin_items": len(after["margin_indices"]),
        "gutenberg_custom_html_blocks": after["html_blocks"],
        "jetpack_block_comments": after["jetpack_subscription_blocks"],
        "focus_occurrences": after["focus_fieldbook_occurrences"],
        "nypl_record_links": after["nypl_catalog_links"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(contents)
    manifest.write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(write_fixture(args.output, args.manifest), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
