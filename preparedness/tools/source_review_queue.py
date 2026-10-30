#!/usr/bin/env python3
"""Read-only, deterministic per-citation source-scope review queue.

Source rows are never collapsed just because a URL or source ID repeats.
This is editorial reconciliation evidence, NOT URL verification, QD or medical safety clearance.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = ("register.json", "fragments/start.json", "fragments/shelter.json", "fragments/food.json", "fragments/health.json", "fragments/hist-food.json", "fragments/hist-home.json", "fragments/hist-field.json")
CITE_RE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")


def normalize_url(url: str) -> str:
    """Use the literal stored URL, not redirects or speculative canonicalization."""
    return url


def source_rows(root: Path) -> list[dict]:
    """Load all source records individually with stable, reviewable row identities."""
    rows = []
    for fragment in SOURCE_FILES:
        file_path = root / "sources" / fragment
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        origin = "base" if fragment == "register.json" else Path(fragment).stem
        for index, source in enumerate(payload["sources"]):
            rows.append({
                "row_key": f"{origin}:{index}:{source['id']}",
                "origin": origin,
                "file": f"preparedness/sources/{fragment}",
                "index": index,
                "source_id": source["id"],
                "url": normalize_url(source["url"]),
                "publisher": source.get("publisher"),
                "kind": source.get("kind"),
                "verified_on": source.get("verified_on"),
                "human_link_check": source.get("human_link_check") is True,
                "supports": source.get("supports"),
                "reading_limits": source.get("notes"),
            })
    return rows


def resolve_own_scope(index: dict, origin: str, source_id: str) -> dict | None:
    """Mirror build.Library.source_for: own cluster, then base, never another cluster."""
    by_id = index.get(source_id, ())
    own = [row for row in by_id if row["origin"] == origin]
    if own:
        return own[0]
    base = [row for row in by_id if row["origin"] == "base"]
    return base[0] if base else None


def build_review_queue(lib, *, rows: list[dict] | None = None) -> dict:
    """Return a stable offline source-to-article crosswalk, never a publication pass."""
    raw = rows if rows is not None else source_rows(lib.root)
    index: dict[str, list[dict]] = defaultdict(list)
    urls: dict[str, list[dict]] = defaultdict(list)
    row_keys: set[str] = set()
    errors = []
    for row in raw:
        if row["row_key"] in row_keys:
            errors.append(f"duplicate physical source row key {row['row_key']}")
        row_keys.add(row["row_key"])
        index[row["source_id"]].append(row)
        urls[row["url"]].append(row)
    for source_id, versions in sorted(index.items()):
        origins = [row["origin"] for row in versions]
        if len(origins) != len(set(origins)):
            errors.append(f"same source id repeated inside contributor origin: {source_id}")
        if len({r["url"] for r in versions}) > 1:
            errors.append(f"source id has conflicting URLs: {source_id}")

    readings = []
    routes = {}
    citations_by_url: dict[str, list[str]] = defaultdict(list)
    citation_counts = Counter()
    for slug, meta in sorted(lib.articles.items(), key=lambda kv: (kv[1].get("n", 999), kv[0])):
        origin = lib.article_origins.get(slug)
        if not origin:
            errors.append(f"{slug}: missing article origin in crosswalk")
            origin = "MISSING_ORIGIN"
        path = lib.url_path(slug)
        if path in routes:
            errors.append(f"duplicate article URL {path} for {slug} and {routes[path]}")
        routes[path] = slug
        used = sorted(set(CITE_RE.findall(meta["_body"])))
        use_notes = meta.get("source_use", {})
        for sid in used:
            row = resolve_own_scope(index, origin, sid)
            if row is None:
                errors.append(f"{slug}: citation {sid} has no source row in owning cluster or base")
                continue
            note = use_notes.get(sid)
            if not isinstance(note, str) or not note.strip():
                errors.append(f"{slug}: citation {sid} lacks substantive nonblank article-specific source_use")
            if not row["verified_on"]:
                errors.append(f"{slug}: citation {sid} is not machine-verified in its own reading scope")
            if row["human_link_check"] and not row["verified_on"]:
                errors.append(f"{slug}: human-check flag set on machine-unverified row {row['row_key']}")
            group = lib.crosswalk_groups.get(row["url"])
            shared = group is not None
            if shared and group.get("review_status") not in ("resolved", "pending-human-source-and-reading-scope-review"):
                errors.append(f"{slug}: unknown review status for shared source {row['url']}")
            citation_counts[row["row_key"]] += 1
            citations_by_url[row["url"]].append(slug)
            readings.append({
                "article": slug,
                "article_origin": origin,
                "article_path": path,
                "status": meta["status"]["publish"],
                "editorial": meta["status"]["editorial"],
                "safety_review": meta["safety_review"]["state"],
                "source_id": sid,
                "source_row_key": row["row_key"],
                "source_file": row["file"],
                "source_row_index": row["index"],
                "source_origin": row["origin"],
                "url": row["url"],
                "machine_checked_on": row["verified_on"],
                "human_link_checked": row["human_link_check"],
                "author_claim_scope": note,
                "contributor_claim_scope": row["supports"],
                "reading_limits": row["reading_limits"],
                "shared_url_group": shared,
                "shared_scope_review": group.get("review_status") if group else "not-shared",
            })
        extra = sorted(set(use_notes) - set(used))
        if extra:
            errors.append(f"{slug}: uncited source_use metadata {extra}")

    groups = []
    for url, entries in sorted(urls.items()):
        if len(entries) < 2:
            if url in lib.crosswalk_groups:
                errors.append(f"obsolete crosswalk group for unique URL: {url}")
            continue
        group = lib.crosswalk_groups.get(url)
        if group is None:
            errors.append(f"repeated URL has no declared crosswalk group: {url}")
        status = group.get("review_status") if group else "UNTRACKED"
        group_rows = sorted(entries, key=lambda row: row["row_key"])
        groups.append({
            "url": url,
            "review_status": status,
            "source_row_count": len(group_rows),
            "source_row_keys": [row["row_key"] for row in group_rows],
            "article_citations": sorted(set(citations_by_url[url])),
            "cited_source_rows": sorted(row["row_key"] for row in group_rows if citation_counts[row["row_key"]] > 0),
            "uncited_source_rows": sorted(row["row_key"] for row in group_rows if citation_counts[row["row_key"]] == 0),
            "all_human_links_checked": all(row["human_link_check"] for row in group_rows),
            "needs_human_scope_reconciliation": status != "resolved",
            "crosswalk_declared_scopes": [
                {"origin": var["origin"], "row_index": var["row_index"], "source_id": var["source"]["id"]}
                for var in (group.get("variants", []) if group else [])
            ],
        })
        if group:
            observed = sorted((r["origin"], r["index"], r["source_id"]) for r in entries)
            declared = sorted((v["origin"], v["row_index"], v["source"]["id"]) for v in group["variants"])
            if observed != declared:
                errors.append(f"crosswalk identities do not match all physical source rows: {url}")
    for url in lib.crosswalk_groups:
        if url not in urls:
            errors.append(f"crosswalk group missing raw source URL: {url}")
    if len(raw) != lib.crosswalk.get("raw_source_rows"):
        errors.append("raw source row count differs from crosswalk provenance baseline")
    if len(urls) != lib.crosswalk.get("unique_source_urls"):
        errors.append("literal unique URL count differs from crosswalk provenance baseline")
    if len(groups) != lib.crosswalk.get("duplicate_url_groups"):
        errors.append("shared source count differs from crosswalk provenance baseline")

    pending = sum(g["needs_human_scope_reconciliation"] for g in groups)
    draft_count = sum(meta["status"]["publish"] == "draft" for meta in lib.articles.values())
    safety_pending = sum(meta["safety_review"]["state"] == "pending" for meta in lib.articles.values())
    not_human_checked = sum(not row["human_link_check"] for row in raw)
    payload = {
        "schema_version": 1,
        "purpose": "ORIGINAL_SCOPE_RECONCILIATION_REVIEW_ONLY_NOT_SAFETY_APPROVAL",
        "release_state": "HOLD",
        "may_publish": False,
        "independent_human_safety_review_performed_by_this_tool": False,
        "summary": {
            "article_drafts_and_tool_drafts": draft_count,
            "safety_reviews_pending": safety_pending,
            "source_rows": len(raw),
            "machine_verified_source_rows": sum(bool(r["verified_on"]) for r in raw),
            "human_link_checks_pending": not_human_checked,
            "unique_literal_urls": len(urls),
            "shared_url_groups": len(groups),
            "shared_scope_reviews_pending": pending,
            "distinct_article_urls": len(routes),
            "unique_source_row_citations": len(citation_counts),
            "article_source_citation_pairs": len(readings),
            "structural_errors": len(errors),
        },
        "errors": sorted(set(errors)),
        "collisions": groups,
        "citations": readings,
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    payload["sha256_review_queue_payload"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write an offline JSON file, never WordPress")
    parser.add_argument("--require-release-ready", action="store_true", help="fail while review holds exist")
    args = parser.parse_args(argv)
    sys.path.insert(0, str(ROOT / "tools"))
    import build
    report = build_review_queue(build.Library())
    encoded = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)
    if report["errors"]:
        return 2
    if args.require_release_ready:
        return 1  # This CLI is strictly review evidence and never attests to release permission.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
