#!/usr/bin/env python3
"""R102: deterministic, read-only same-URL citation and claim-scope reviewer workorder.

Literal shared URLs do not imply shared claim support or human approval.
Never deduplicate records, resolve a review status, publish or write to WordPress.
"""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build
import validate

SCHEMA = "r102-author-scoped-citation-collision-workorder-v1"
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
TAGS = re.compile(r"<[^>]*>")
WHITE = re.compile(r"\s+")
EXPECTED_ARTICLES = 35
EXPECTED_BUILDABLE_TOOLS = {"water-planner"}
EXPECTED_PENDING_COLLISIONS = 30


class Hold(ValueError):
    """A private source/citation safety boundary changed; deny release."""


def need(ok: bool, why: str) -> None:
    if not ok:
        raise Hold(why)


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def digest(value: object) -> str:
    data = value if isinstance(value, str) else canonical(value)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def source_snapshot(row: dict) -> dict:
    return {"origin": row["_origin"],
            "source": {k: v for k, v in row.items() if k != "_origin"}}


def surrounding_context(body: str, match: re.Match[str]) -> dict:
    """Bounded authored-text proximity for HUMAN review, not claim proof.

    No guessed paragraph boundary is asserted: a citation can be adjacent to
    multiple sentences or a list. Preserve a full-body digest for custody.
    """
    left = max(0, match.start() - 210)
    right = min(len(body), match.end() + 210)
    before = html.unescape(TAGS.sub(" ", body[left:match.start()]))
    after = html.unescape(TAGS.sub(" ", body[match.end():right]))
    excerpt = WHITE.sub(" ", (before + " [CITATION] " + after)).strip()
    return {"proximity_excerpt_not_claim_verification": excerpt,
            "proximity_sha256": digest(excerpt),
            "token_offset": match.start()}


def workorder(lib: build.Library) -> dict:
    """Fail closed against metadata drift while retaining each author's evidence."""
    slugs = {item["slug"] for item in lib.taxonomy["slate"]}
    need(len(slugs) == EXPECTED_ARTICLES and
         {s for s, m in lib.articles.items() if m.get("kind") != "tool"} == slugs,
         "35-article slate changed; manual provenance reconciliation required")
    tools = {s for s, m in lib.articles.items() if m.get("kind") == "tool"}
    need(tools == EXPECTED_BUILDABLE_TOOLS,
         "actual complete tool inventory changed; five planned tools are not assumed built")
    need(set(lib.article_origins) == set(lib.articles),
         "author-origin crosswalk incomplete or has unexpected slugs")
    need(len(lib.crosswalk_groups) == EXPECTED_PENDING_COLLISIONS,
         "collision inventory drift; review every newly changed group")
    need(all(g.get("review_status") ==
             "pending-human-source-and-reading-scope-review"
             for g in lib.crosswalk_groups.values()),
         "crosswalk review state changed; do not silently inherit approvals")

    actual: dict[str, list[dict]] = {}
    for sid, rows in lib.source_variants.items():
        for row in rows:
            need(row.get("id") == sid and isinstance(row.get("url"), str),
                 "fragment ID or URL corrupt")
            actual.setdefault(row["url"], []).append(source_snapshot(row))
    collisions = {url: rows for url, rows in actual.items() if len(rows) > 1}
    need(set(collisions) == set(lib.crosswalk_groups),
         "new, missing or renamed literal-URL collision")
    for url, rows in collisions.items():
        declared = lib.crosswalk_groups[url]["variants"]
        normalized = lambda entries: sorted(
            ({"origin": r["origin"], "source": r["source"]} for r in entries),
            key=canonical)
        need(normalized(rows) == normalized(declared),
             "crosswalk source/reading-scope drift: " + url)
        declared_identities = sorted((r["origin"], r["source"]["id"])
                                     for r in declared)
        need(declared_identities ==
             sorted((r["origin"], r["id"]) for r in
                    lib.crosswalk_groups[url]["identities"]),
             "crosswalk identity roster drift: " + url)

    uses_by_url: dict[str, list[dict]] = {u: [] for u in collisions}
    all_cites = 0
    for slug, meta in sorted(lib.articles.items()):
        need(meta.get("status", {}).get("publish") == "draft" and
             meta.get("safety_review", {}).get("state") == "pending",
             "private draft / pending human safety state changed: " + slug)
        origin = lib.article_origins[slug]
        body = meta["_body"]
        citations = list(CITE.finditer(body))
        all_cites += len(citations)
        seen = set()
        for occurrence, match in enumerate(citations, start=1):
            sid = match.group(1)
            need(sid in lib.source_variants, "unrecognized source ID: " + sid)
            scope = meta.get("source_use", {}).get(sid)
            need(isinstance(scope, str) and scope.strip(),
                 "missing original author reading scope: " + slug + "/" + sid)
            source = lib.source_for(meta, sid)
            url = source["url"]
            if url in collisions:
                context = surrounding_context(body, match)
                uses_by_url[url].append({
                    "article_slug": slug,
                    "article_origin": origin,
                    "article_track": meta["track"],
                    "original_body_sha256": digest(body),
                    "citation_ordinal_in_article": occurrence,
                    "source_id_as_authored": sid,
                    "selected_source_origin": source["_origin"],
                    "author_scoped_source_use": scope,
                    "author_scoped_source_use_sha256": digest(scope),
                    **context,
                })
            seen.add(sid)
        need(set(meta.get("source_use", {})) == seen,
             "authored source-use reading depth not one-to-one with citations: " + slug)

    groups = []
    for url in sorted(collisions):
        group = lib.crosswalk_groups[url]
        variants = []
        for v in sorted(collisions[url], key=canonical):
            s = v["source"]
            variants.append({
                "origin": v["origin"], "source_id": s["id"],
                "title": s.get("title"), "publisher": s.get("publisher"),
                "published": s.get("published"), "updated": s.get("updated"),
                "reviewed": s.get("reviewed"),
                "machine_checked_on_not_human_approval": s.get("verified_on"),
                "human_link_check_recorded": s.get("human_link_check"),
                "supports_as_recorded_not_independently_verified": s.get("supports"),
                "reading_limitations_as_recorded": s.get("notes"),
                "variant_sha256": digest(v),
            })
        citations = sorted(uses_by_url[url],
                           key=lambda item: (item["article_slug"],
                                             item["citation_ordinal_in_article"]))
        groups.append({
            "literal_url": url,
            "review_state": group["review_status"],
            "human_review": "NOT_REVIEWED",
            "same_url_is_not_shared_claim_authority": True,
            "variant_count": len(variants),
            "variants": variants,
            "citation_occurrences": len(citations),
            "citing_articles": sorted({x["article_slug"] for x in citations}),
            "author_bound_citation_contexts": citations,
        })

    report = {
        "schema": SCHEMA,
        "issue": 136,
        "release_state": "HOLD",
        "may_publish": False,
        "may_merge": False,
        "source_claim_support_review": "NOT_REVIEWED",
        "qualified_safety_review": "NOT_REVIEWED",
        "independent_QD": "NOT_REVIEWED",
        "browser_and_wordpress_qa": "NOT_REVIEWED",
        "source_crosswalk_sha256": digest(lib.crosswalk),
        "frozen_historical_source_commit_pins_not_current_heads":
            lib.crosswalk.get("source_head_commits", {}),
        "original_article_drafts": EXPECTED_ARTICLES,
        "actual_buildable_tools": len(tools),
        "additional_planned_tools_not_buildable": 5,
        "literal_url_collision_groups_pending_human_review": len(groups),
        "citation_tokens_across_all_private_drafts": all_cites,
        "collision_citation_occurrences": sum(x["citation_occurrences"] for x in groups),
        "groups": groups,
    }
    report["sha256_seal"] = digest(report)
    return report


def main() -> int:
    lib = build.Library()
    errors, warnings = validate.validate(lib)
    need(not errors, "native Preparedness validation errors: " + "; ".join(errors[:5]))
    report = workorder(lib)
    report["native_validation_warnings_not_approvals"] = warnings
    report["sha256_seal"] = digest({k: v for k, v in report.items()
                                   if k != "sha256_seal"})
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Hold, ValueError, KeyError, TypeError) as exc:
        print(canonical({"schema": SCHEMA, "release_state": "HOLD",
                         "may_publish": False, "error": str(exc)}),
              file=sys.stderr)
        raise SystemExit(2)
