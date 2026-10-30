#!/usr/bin/env python3
"""Deterministic, read-only integration evidence report for Preparedness.

No network, CMS publishing, link check or modification of repository inputs.
The word 'HOLD' is governance state, not a claim that articles are unsafe;
the full human review and rendered-QA process remains outside this script.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import validate  # noqa: E402


def make_report(lib: build.Library | None = None) -> dict:
    lib = lib or build.Library()
    errors, warnings = validate.validate(lib)
    articles = []
    claimed_urls: set[str] = set()
    for slug, meta in sorted(lib.articles.items(), key=lambda item: (item[1]["n"], item[0])):
        refs = list(dict.fromkeys(re.findall(r"\{\{cite:([a-z0-9\-]+)\}\}", meta["_body"])))
        sources = []
        for sid in refs:
            try:
                source = lib.source_for(meta, sid)
            except KeyError as exc:
                errors.append(f"article:{slug}: {exc}")
                continue
            claimed_urls.add(source["url"])
            cross = lib.crosswalk_groups.get(source["url"])
            sources.append({
                "id": sid, "origin": source["_origin"],
                "url": source["url"],
                "machine_checked": bool(source.get("verified_on")),
                "human_link_checked": source.get("human_link_check") is True,
                "shared_source_scope": "pending" if cross and cross.get("review_status") != "resolved" else "not-pending",
            })
        articles.append({
            "n": meta["n"],
            "slug": slug,
            "kind": meta.get("kind", "article"),
            "origin": lib.article_origins.get(slug, "base"),
            "track": meta["track"],
            "section": meta["section"],
            "word_count": build.word_count(meta["_body"]),
            "publication": meta["status"]["publish"],
            "editorial": meta["status"]["editorial"],
            "safety": meta["safety_review"]["state"],
            "source_count": len(sources),
            "human_verified_source_count": sum(s["human_link_checked"] for s in sources),
            "pending_shared_source_count": sum(s["shared_source_scope"] == "pending" for s in sources),
            "sources": sources,
        })
    source_rows = [v for rows in lib.source_variants.values() for v in rows]
    unresolved = sorted(url for url, group in lib.crosswalk_groups.items()
                        if group.get("review_status") != "resolved")
    drafts = [a for a in articles if a["publication"] == "draft"]
    release_ready = (
        not errors and not unresolved and not drafts and all(
            item["human_verified_source_count"] == item["source_count"]
            for item in articles
        ) and all(item["editorial"] == "reviewed" for item in articles)
    )
    return {
        "schema_version": 1,
        "publication": "HOLD" if not release_ready else "REQUIRES_FINAL_INDEPENDENT_APPROVAL",
        "release_ready_by_static_checks": release_ready,
        "external_human_qa_proven": False,
        "wordpress_published_by_this_tool": False,
        "slate": {
            "expected_articles": len(lib.slate),
            "actual_articles": sum(a["kind"] != "tool" for a in articles),
            "tools": sum(a["kind"] == "tool" for a in articles),
            "drafts_including_tools": len(drafts),
            "safety_states": dict(sorted(Counter(a["safety"] for a in articles).items())),
        },
        "sources": {
            "raw_rows": len(source_rows),
            "verified_by_machine": sum(bool(s.get("verified_on")) for s in source_rows),
            "human_link_checked_rows": sum(s.get("human_link_check") is True for s in source_rows),
            "unique_cited_urls": len(claimed_urls),
            "shared_url_groups": len(lib.crosswalk_groups),
            "pending_groups": len(unresolved),
            "pending_urls": unresolved,
        },
        "validation_errors": sorted(set(errors)),
        "validation_warnings": sorted(set(warnings)),
        "articles": articles,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact", action="store_true", help="print JSON without indentation")
    parser.add_argument("--require-release-ready", action="store_true",
                        help="fail nonzero if safety/editorial/source-release checks still hold")
    parser.add_argument("--output", type=Path, default=None,
                        help="optional local JSON report path; never uploads or publishes")
    args = parser.parse_args(argv)
    report = make_report()
    output = json.dumps(report, indent=None if args.compact else 2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    if report["validation_errors"]:
        return 2
    return 1 if args.require_release_ready and not report["release_ready_by_static_checks"] else 0


if __name__ == "__main__":
    sys.exit(main())
