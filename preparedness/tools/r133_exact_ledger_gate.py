#!/usr/bin/env python3
"""Read-only R133 35-article provenance snapshot verification; never authorizes publication.

Run at repo root: python -I preparedness/tools/r133_exact_ledger_gate.py --root .
Requires an exact candidate checkout containing all 35 article bodies, metadata,
source registers and seven R133 JSON ledgers. This is structural, not safety review.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, urlunsplit

CANDIDATE = "5685b54796d520e8dd50e0cdf4d35e38c9cec7a4"
PARTS = (0, 5, 10, 15, 20, 25, 30)
PENDING = "pending-human-source-and-reading-scope-review"
CITE = re.compile(r"\{\{cite:([^}]+)\}\}")
LINK = re.compile(r"\{\{link:([^}]+)\}\}")


class IntegrityHold(ValueError):
    """Evidence drift or invalid safety/release state; never interpreted as PASS."""


def require(condition, reason):
    if not condition:
        raise IntegrityHold(reason)


def disallow_duplicate_keys(pairs):
    result = {}
    for k, value in pairs:
        require(k not in result, "DUPLICATE_JSON_KEY:" + k)
        result[k] = value
    return result


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=disallow_duplicate_keys)


def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def alias(url):
    u = urlsplit(url)
    require(u.scheme == "https" and bool(u.netloc), "INVALID_SOURCE_URL")
    return urlunsplit((u.scheme, u.netloc, (u.path or "/").rstrip("/") or "/",
                       u.query, u.fragment))


def citations(html):
    return CITE.findall(html)


def visible_lexical_citations(html):
    """Preliminary lexical count; NOT a DOM accessibility/visibility audit."""
    raw = re.sub(r"<!--[\s\S]*?-->", "", html)
    raw = re.sub(r"<(script|style)\b[^>]*>[\s\S]*?</\1\s*>", "", raw,
                 flags=re.IGNORECASE)
    return CITE.findall(re.sub(r"<[^>]*>", "", raw))


def link_targets(html):
    return [token.split("|", 1)[0] for token in LINK.findall(html)]


def audit(root):
    root = Path(root)
    p = root / "preparedness"
    d = p / "docs" / "r133"
    tax = load(p / "taxonomy.json")
    cross = load(p / "sources" / "crosswalk.json")
    lock = load(p / "sources" / "article-evidence-lock.json")
    index = load(d / "SOURCE_ID_ORIGIN_LOOKUP.json")
    require(index["candidate_ref"] == CANDIDATE and index["state"] == "HOLD_UNREVIEWED",
            "INVALID_CANDIDATE_OR_SOURCE_HOLD")
    article_slugs = [x["slug"] for x in tax["slate"]]
    tool_slugs = [x["slug"] for x in tax["tools"]]
    require(len(article_slugs) == 35 and len(set(article_slugs)) == 35,
            "ARTICLE_ROSTER_DRIFT")
    require(len(set(article_slugs + tool_slugs)) == len(article_slugs + tool_slugs),
            "DUPLICATE_ARTICLE_TOOL_ROUTE")
    known_routes = set(article_slugs + tool_slugs)
    by_id = defaultdict(list)
    by_alias = defaultdict(list)
    actual_source_files = []
    for f in index["source_files"]:
        path = root / f["path"]
        raw = path.read_bytes()
        require(blob_sha(raw) == f["sha"], "SOURCE_BLOB_DRIFT:" + f["path"])
        items = load(path)["sources"]
        require(len(items) == f["count"], "SOURCE_ROW_COUNT_DRIFT")
        actual_source_files.append(f)
        for i, item in enumerate(items):
            record = {"origin": f["origin"], "row_index": i, "url": item["url"]}
            by_id[item["id"]].append(record)
            by_alias[alias(item["url"])].append((f["origin"], i, item))
    require(len(actual_source_files) == 8, "SOURCE_REGISTER_COUNT_DRIFT")
    require(dict(by_id) == index["by_source_id"], "SOURCE_ORIGIN_LOOKUP_DRIFT")
    require(sum(len(v) for v in by_id.values()) == 244 and len(by_id) == 225,
            "SOURCE_INVENTORY_DRIFT")
    require(len({v["url"] for rows in by_id.values() for v in rows}) == 202,
            "SOURCE_LITERAL_URL_DRIFT")
    collisions = {key: rows for key, rows in by_alias.items() if len(rows) > 1}
    require(len(collisions) == 32 and len(cross["groups"]) == 32,
            "SHARED_SOURCE_GROUP_COUNT_DRIFT")
    seen = set()
    for group in cross["groups"]:
        key = alias(group["url"])
        require(key in collisions and key not in seen, "CROSSWALK_GROUP_DRIFT")
        seen.add(key)
        require(group["review_status"] == PENDING and
                group.get("reviewer") is None and group.get("reviewed_on") is None,
                "UNAUTHORIZED_SOURCE_APPROVAL")
        expected = {(origin, idx, json.dumps(item, sort_keys=True))
                    for origin, idx, item in collisions[key]}
        observed = {(v["origin"], v["row_index"],
                     json.dumps(v["source"], sort_keys=True))
                    for v in group["variants"]}
        require(expected == observed, "CROSSWALK_SOURCE_VARIANT_DRIFT:" + key)
    require(seen == set(collisions), "UNLISTED_SHARED_SOURCE_GROUP")
    entries = []
    for start in PARTS:
        entry = load(d / f"CITATION_LEDGER_{start:02d}.json")
        require(entry["candidate_ref"] == CANDIDATE and
                entry["release"] == "DRAFT_HOLD" and entry["offset"] == start,
                "LEDGER_RELEASE_OR_ORDER_DRIFT")
        require(entry["taxonomy_sha"] == blob_sha((p / "taxonomy.json").read_bytes()) and
                entry["crosswalk_sha"] == blob_sha((p / "sources" / "crosswalk.json").read_bytes()) and
                entry["prior_article_lock_sha"] == blob_sha((p / "sources" / "article-evidence-lock.json").read_bytes()),
                "LEDGER_INPUT_BLOB_DRIFT")
        require(len(entry["entries"]) == 5, "LEDGER_SEGMENT_SIZE_DRIFT")
        entries.extend(entry["entries"])
    require([e["slug"] for e in entries] == article_slugs, "ARTICLE_LEDGER_ROSTER_DRIFT")
    citation_total = 0
    review_counts = Counter()
    original_by_slug = {r["slug"]: r for r in lock["records"]}
    for e in entries:
        slug = e["slug"]
        path = p / "content" / "articles" / slug
        raw = (path.with_suffix(".body.html")).read_bytes()
        mb = (path.with_suffix(".meta.json")).read_bytes()
        require(blob_sha(raw) == e["body_sha"] and
                blob_sha(mb) == e["metadata_sha"], "ARTICLE_BLOB_DRIFT:" + slug)
        meta = json.loads(mb, object_pairs_hook=disallow_duplicate_keys)
        text = raw.decode("utf-8")
        ids = citations(text)
        unique = sorted(set(ids))
        explanations = sorted(meta.get("source_use", {}))
        require(meta["slug"] == slug and meta["status"]["publish"] == "draft" and
                e["status"] == "draft", "UNAUTHORIZED_ARTICLE_PUBLISH:" + slug)
        require(e["origin"] == cross["article_origins"][slug], "ARTICLE_ORIGIN_DRIFT")
        require(meta["safety_review"]["state"] == e["safety_review"],
                "ARTICLE_SAFETY_STATE_DRIFT")
        require(e["citation_occurrences"] == len(ids) and
                e["unique_citation_ids"] == unique and
                e["author_explanation_ids"] == explanations,
                "ARTICLE_CITATION_SCOPE_DRIFT:" + slug)
        require(len(visible_lexical_citations(text)) == e["lexically_visible_citations"],
                "LEXICAL_CITATION_EXPOSURE_DRIFT:" + slug)
        require(len(ids) == len(visible_lexical_citations(text)),
                "HIDDEN_CITATION_TOKEN:" + slug)
        require(not (set(unique) - set(explanations)), "MISSING_AUTHOR_SOURCE_EXPLANATION:" + slug)
        require(not (set(unique) - set(by_id)), "UNKNOWN_SOURCE_ID:" + slug)
        require(not (set(link_targets(text)) - known_routes), "MISSING_INTERNAL_DESTINATION:" + slug)
        require(all(isinstance(v, str) and v.strip() for v in meta["source_use"].values()),
                "BLANK_SOURCE_EXPLANATION:" + slug)
        require(e["missing_source_ids"] == [] and e["missing_explanations"] == [] and
                e["broken_article_links"] == [] and e["invisible_token_count"] == 0,
                "PREEXISTING_LEDGER_ISSUES:" + slug)
        old = original_by_slug[slug]
        require(e["prior_body_same"] == (e["body_sha"] == old["body"]["git_blob_sha"]) and
                e["prior_meta_same"] == (e["metadata_sha"] == old["metadata"]["git_blob_sha"]),
                "ORIGINAL_BASELINE_DIFF_NOT_RECORDED:" + slug)
        citation_total += len(ids)
        review_counts[e["safety_review"]] += 1
    require(citation_total == 2000, "TOTAL_CITATION_CENSUS_DRIFT")
    require(review_counts == {"pending": 29, "approved": 2, "not-required": 4},
            "HISTORICAL_SAFETY_STATE_CENSUS_DRIFT")
    return {"state": "HOLD", "qualified_safety_review": False,
            "independent_QD_PASS": False, "may_publish": False,
            "article_count": len(entries), "source_rows": 244,
            "shared_source_groups_unreviewed": len(collisions),
            "raw_citations": citation_total, "historical_safety_review_states": dict(review_counts)}


def main(argv=None):
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--root", type=Path, default=Path("."))
    args = arg.parse_args(argv)
    try:
        print(json.dumps(audit(args.root), indent=2, sort_keys=True))
        return 0
    except (IntegrityHold, OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        print("HOLD: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
