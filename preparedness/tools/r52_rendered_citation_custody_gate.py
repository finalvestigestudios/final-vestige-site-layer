#!/usr/bin/env python3
"""R52: frozen R48 preview citation/source parity against R51 original corpus.

This validates the integrity and internal consistency of PRIVATE machine QA
evidence only. It is NOT evidence of human source review, a live WordPress
render, qualified hazard safety, accessibility certification, or QD approval.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R48_DIR = Path("preparedness/docs/r48")
UPSTREAM_R48_COMMIT = "4fe053c41c0a78e32124991fcfbdb52c36753e49"
UPSTREAM_R51_COMMIT = "5d407793f4009c26b1862d4c135a9d62294ca13f"
PINS = {
    "ARTICLE-READINESS-MATRIX-2026-11-01.csv": "c357ed2a5135f641c45b5e2c620a8015dfd43c34",
    "ARTICLE-READINESS-MATRIX-2026-11-01.md": "0ee396fc78b7455a69730030c884e7d5d922b39d",
    "RENDERED-QA-ACTION-BOX-POSITION-2026-11-01.json": "d62f96f25d30e1c0a4b0151bd589e1cd0ebcbd8f",
    "RENDERED-QA-DEEP-2026-11-01.json": "4310fa7bdc21c66c9ac60ce7801cb248cf4fd9d6",
    "RENDERED-QA-LAYOUT-2026-11-01.json": "888364cbb13426df6d8be16071f9ce3ca8663605",
    "RENDERED-QA-REPORT-2026-11-01.md": "36ebb08e30ba3bb9f09f868df95bb2c9e2bb6a44",
    "qa-shots/hub-lost-ways-390.png": "51055786fe47999a6c3dce4671e1d619c1e4482e",
    "qa-shots/hub-water-1440.png": "2f61da3bff749b7b6d990a33bd514cbca00fcf20",
    "qa-shots/landing-1440.png": "465233520a6f5a164a714cbf97b66ee3c072845b",
    "qa-shots/landing-390.png": "0d52b2c6ffa37f509e793f61b63bdc1fb8453d2d",
    "qa-shots/making-water-safer-1440.png": "e0863d692c3ec1d5dccf90f012a0e2943172b4e9",
    "qa-shots/making-water-safer-390.png": "34a9b58a4a23dc10efe3e4f640bc413ec8b957b4",
    "qa-shots/medication-and-devices-390.png": "fe12c721526bb6ba015ae8ea52d27a3ff96bfb22",
    "qa-shots/outage-heat-cold-generators-390.png": "447d223a0cb8aa2d5c9cc4e98983198b86955d10",
    "qa-shots/pressure-canning-low-acid-1440.png": "f6bb43053ace4e916befeb6d667cebdd51d5f6c7",
    "qa-shots/salt-beef-salt-pork-age-of-sail-1440.png": "61fe6ea5f2b6dd54c935c4fe038039c3bf51104e",
    "qa-shots/water-planner-1440.png": "9376e4d23558ec45b1df33847caf19c431963743",
    "qa-shots/water-planner-390.png": "6ecf1ed785e44443b7c2b781847a414f955f3653",
    "scripts/qa_deep.py": "97ae25a6ae228a483f7d7d0e7e90a42b7b18ec26",
    "scripts/qa_full.py": "40b17bc0a9ba1d2f4528c944ea1fa50715c72b28",
}
WIDTHS = ("360", "390", "768", "1440", "1920")
EXTRA_PAGES = {"landing"} | {"hub-" + s for s in (
    "start-here", "water", "food", "shelter-power",
    "health-sanitation", "family-communication", "lost-ways", "field-tools",
)}
OPEN_FINDINGS = tuple("QA-F" + str(i) for i in range(1, 7))


class EvidenceHold(ValueError):
    """A frozen preview or cited-source relationship disagreed: remain HOLD."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise EvidenceHold(message)


def git_blob_sha(content: bytes) -> str:
    """Git's blob ID, not a misleading plain SHA-1 of file contents."""
    header = ("blob " + str(len(content)) + "\0").encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def verify_blob(content: bytes, pin: str, label: str) -> None:
    require(git_blob_sha(content) == pin, "R48 original Git blob changed: " + label)


def verify_pins(root: Path = ROOT) -> None:
    for relative, sha in PINS.items():
        path = root / R48_DIR / relative
        require(path.is_file(), "R48 evidence missing: " + relative)
        verify_blob(path.read_bytes(), sha, relative)


def load_packet(root: Path = ROOT):
    p = root / R48_DIR
    matrix = (p / "ARTICLE-READINESS-MATRIX-2026-11-01.csv").read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(matrix))
    required_cols = {"n", "slug", "distinct_sources_cited", "human_link_checked",
                     "publish_state", "independent_QD", "publication_eligible",
                     "safety_review", "rendered_qa_this_pass", "blockers"}
    require(reader.fieldnames is not None and len(set(reader.fieldnames)) == len(reader.fieldnames)
            and required_cols <= set(reader.fieldnames),
            "readiness matrix columns missing or duplicated")
    rows = list(reader)
    def read_json(filename: str):
        return json.loads((p / filename).read_text(encoding="utf-8"))
    return (
        rows,
        read_json("RENDERED-QA-LAYOUT-2026-11-01.json"),
        read_json("RENDERED-QA-DEEP-2026-11-01.json"),
        read_json("RENDERED-QA-ACTION-BOX-POSITION-2026-11-01.json"),
        (p / "RENDERED-QA-REPORT-2026-11-01.md").read_text(encoding="utf-8"),
    )


def verify_packet(rows, layout, deep, positions, report) -> dict:
    """Independent deterministic checks; inputs must be pinned separately."""
    require(type(rows) is list and len(rows) == 36, "lost original 35 articles or water tool")
    require([r.get("n") for r in rows] ==
            [str(i) for i in range(1, 36)] + ["tool"], "original slate order changed")
    slugs = [r.get("slug") for r in rows]
    require(all(isinstance(s, str) and s for s in slugs)
            and len(set(slugs)) == 36 and slugs[-1] == "water-planner",
            "invalid or duplicate article/tool slug")
    per_article = {}
    for row in rows:
        slug = row["slug"]
        require(row.get("human_link_checked") == "0"
                and row.get("publish_state") == "draft"
                and row.get("publication_eligible") == "NO"
                and row.get("independent_QD") == "no",
                "fabricated human or publication approval in matrix: " + slug)
        require(row.get("safety_review") in {"pending", "approved", "not-required"},
                "unrecognized historical safety-review metadata: " + slug)
        require("automated only" in row.get("rendered_qa_this_pass", "").lower()
                and "not live theme" in row.get("rendered_qa_this_pass", "").lower(),
                "rendered QA falsely represented as live review: " + slug)
        require("independent qd pass not recorded" in row.get("blockers", "").lower(),
                "missing explicit independent-QD HOLD: " + slug)
        try:
            source_count = int(row["distinct_sources_cited"])
        except (TypeError, ValueError, KeyError) as exc:
            raise EvidenceHold("bad source census in matrix: " + slug) from exc
        require(source_count > 0, "source records lost: " + slug)
        per_article[slug] = source_count

    pages = layout.get("pages") if type(layout) is dict else None
    require(type(pages) is dict and set(pages) == set(slugs) | EXTRA_PAGES
            and len(pages) == 45, "private 45-page rendered inventory drift")
    require(type(deep) is dict and type(positions) is dict,
            "rendered QA details lost")
    for family in ("keyboard", "no_js", "print"):
        require(type(deep.get(family)) is dict
                and set(deep[family]) == set(pages),
                "private review coverage drift: " + family)
    axe = deep.get("axe")
    expected_axe = {slug + "@" + width for slug in pages for width in ("390", "1440")}
    require(type(axe) is dict and set(axe) == expected_axe
            and len(axe) == 90, "90 original machine axe records lost")
    for key, result in axe.items():
        require(type(result) is dict and result.get("violations") == [],
                "machine axe record changed or has violations: " + key)

    citation_total = 0
    source_total = 0
    for slug, page in pages.items():
        widths = page.get("widths") if type(page) is dict else None
        require(type(widths) is dict and set(widths) == set(WIDTHS),
                "missing private preview width: " + slug)
        baseline = widths["390"]
        require(type(baseline) is dict, "invalid baseline QA metrics: " + slug)
        original_citations = baseline.get("citeLinks")
        original_sources = baseline.get("sourceItems")
        require(type(original_citations) is int and type(original_sources) is int
                and original_citations >= 0 and original_sources >= 0,
                "invalid rendered citation/source counts: " + slug)
        if slug in per_article:
            require(original_sources == per_article[slug] and original_citations > 0,
                    "rendered article citations mismatch original source slate: " + slug)
            citation_total += original_citations
            source_total += original_sources
        else:
            require(original_citations == 0 and original_sources == 0,
                    "nonarticle hub masquerading as a sourced article: " + slug)
        for width in WIDTHS:
            m = widths[width]
            require(type(m) is dict and m.get("citeLinks") == original_citations
                    and m.get("sourceItems") == original_sources,
                    "citation count changed with viewport: " + slug + "@" + width)
            require(m.get("brokenCiteAnchors") == 0
                    and m.get("unreferencedSources") == 0
                    and m.get("hashBroken") == 0
                    and m.get("dupIds") == []
                    and m.get("consoleErrors") == []
                    and m.get("hOverflow") is False
                    and m.get("h1") == 1
                    and m.get("mains") == 1,
                    "rendered evidence/navigation safety failure: " + slug + "@" + width)
            require(m.get("draftBadge") is (slug in per_article),
                    "misleading draft status in rendered page: " + slug + "@" + width)
    require(citation_total == 1959 and source_total == 367,
            "global 1959 citation occurrences / 367 source relationships lost")

    require(set(positions) == {"360", "390"},
            "original phone action-box measurements changed")
    for width in ("360", "390"):
        group = positions[width]
        require(type(group) is dict and type(group.get("rows")) is dict
                and set(group["rows"]) == set(slugs), "missing action-box safety measurements")
        vh = group.get("vh")
        require(type(vh) is int and vh > 0, "invalid phone viewport measurement")
        for slug, value in group["rows"].items():
            require(type(value) is dict and type(value.get("actTop")) is int
                    and value["actTop"] >= vh,
                    "recorded QA-F1 below-fold defect silently changed: " + slug)
    nojs = deep["no_js"].get("water-planner")
    require(type(nojs) is dict and nojs.get("noscript") is False
            and nojs.get("results_text_nojs") == 0,
            "recorded QA-F2 no-JS planner defect silently changed")
    require(type(report) is str and all(f in report for f in OPEN_FINDINGS)
            and "open; none fixed" in report.lower(),
            "original unresolved human-facing QA findings removed")

    return {
        "issue": 136,
        "release_state": "HOLD",
        "may_publish": False,
        "human_source_links_verified": False,
        "qualified_safety_clearance": False,
        "independent_QD_approval": False,
        "r48_original_commit": UPSTREAM_R48_COMMIT,
        "r51_integration_parent": UPSTREAM_R51_COMMIT,
        "frozen_qa_git_blobs": len(PINS),
        "articles": 35,
        "water_planner": 1,
        "preview_pages": len(pages),
        "viewport_measurements": len(pages) * len(WIDTHS),
        "reported_automated_axe_runs": len(axe),
        "visible_citation_links": citation_total,
        "visible_article_source_entries": source_total,
        "open_preview_issues": list(OPEN_FINDINGS),
        "browser_qa_scope": "R48 LOCAL PREVIEWS ONLY / NOT LIVE WORDPRESS / NOT HUMAN-QD",
    }


def verify(root: Path = ROOT) -> dict:
    verify_pins(root)
    return verify_packet(*load_packet(root))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    opts = parser.parse_args()
    try:
        report = verify(opts.root)
    except (EvidenceHold, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"release_state": "HOLD", "evidence_integrity": "INVALID",
                          "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
