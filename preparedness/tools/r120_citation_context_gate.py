#!/usr/bin/env python3
"""R120 read-only, fail-closed 35-article citation-context custody gate.

Validates independently retrieved exact Git blobs in two frozen review manifests
against the R117 nine-head catalog. Does NOT validate medical advice, reviewer
judgment, URLs, merchant status, HTML semantics, or WordPress readiness.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

SOURCE_SCHEMA = "fv-preparedness-r117-nine-snapshot-article-source-git-custody-HOLD-v1"
PART_SCHEMA = "r120-partial-citation-context-HOLD-v1"
OID = re.compile(r"[0-9a-f]{40}\Z")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SOURCE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")

class Hold(ValueError):
    """Reject stale, contradictory or tampered evidence; never approve release."""

def require(value, code):
    if not value:
        raise Hold(code)

def strict_json(path):
    def no_dupes(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=no_dupes)

def check_oid(value):
    require(type(value) is str and bool(OID.fullmatch(value)), "INVALID_GIT_BLOB")

def check_natural(value, code):
    require(type(value) is int and value >= 0, code)

def check(snapshots, parts):
    require(type(snapshots) is dict and snapshots.get("schema") == SOURCE_SCHEMA, "INVALID_R117_SNAPSHOT_SCHEMA")
    require(snapshots.get("issue") == 136 and snapshots.get("business_issue") == 820, "WRONG_ISSUE")
    heads = snapshots.get("snapshots")
    require(type(heads) is list and len(heads) == 9, "NINE_HEADS_REQUIRED")
    baseline, candidate, *contributors = heads
    require([x.get("role") for x in heads] == ["baseline", "candidate"] + ["contributor"] * 7, "INVALID_HEAD_ROLES")
    require(len({x.get("cluster") for x in contributors}) == 7, "SEVEN_CLUSTERS_REQUIRED")
    require(snapshots.get("governance", {}).get("release_state") == "HOLD", "RELEASE_HOLD_REQUIRED")
    for flag in ("may_merge", "may_publish", "independent_QD_PASS", "medical_safety_verified", "merchant_offer_verified"):
        require(snapshots["governance"].get(flag) is False, "GOVERNANCE_UPGRADE")
    for h in heads:
        check_oid(h.get("sha"))
    files_before, files_after = baseline.get("article_files"), candidate.get("article_files")
    require(type(files_before) is dict and type(files_after) is dict and files_before.keys() == files_after.keys(), "ARTICLE_ROSTER_CHANGED")
    bodies = sorted(x for x in files_before if x.endswith(".body.html"))
    metas = {x for x in files_before if x.endswith(".meta.json")}
    require(len(bodies) == 35 and {x[:-10] + ".meta.json" for x in bodies} == metas, "NOT_35_PAIRED_ARTICLES")
    for filename in files_before:
        require(type(filename) is str, "INVALID_ARTICLE_PATH")
        slug = filename[:-10]
        require(bool(SLUG.fullmatch(slug)), "INVALID_ARTICLE_PATH")
        check_oid(files_before[filename]); check_oid(files_after[filename])
    expected_changed = {x[:-10] for x in bodies if files_before[x] != files_after[x]}
    require(type(parts) is list and len(parts) == 2, "TWO_PARTS_REQUIRED")
    found = {}
    for part in parts:
        require(type(part) is dict and part.get("schema") == PART_SCHEMA, "INVALID_PART_SCHEMA")
        require(part.get("issue") == 136 and part.get("base_sha") == baseline["sha"] and part.get("candidate_sha") == candidate["sha"], "STALE_PART_HEAD")
        rows = part.get("rows")
        require(type(rows) is list and len(rows) > 0, "EMPTY_PART")
        for row in rows:
            require(type(row) is dict, "INVALID_ROW")
            slug = row.get("slug")
            require(type(slug) is str and bool(SLUG.fullmatch(slug)), "INVALID_SLUG")
            require(slug in expected_changed, "UNTRACKED_OR_UNCHANGED_BODY")
            require(slug not in found, "DUPLICATE_ARTICLE_EVIDENCE")
            found[slug] = row
            filename = slug + ".body.html"
            check_oid(row.get("before_git_blob")); check_oid(row.get("after_git_blob"))
            require(row["before_git_blob"] == files_before[filename] and row["after_git_blob"] == files_after[filename], "BODY_BLOB_IDENTITY_MISMATCH")
            require(row.get("approval") == "UNREVIEWED", "ILLEGAL_APPROVAL")
            for field in ("before_word_count", "after_word_count", "before_citation_count", "after_citation_count", "same_source_id_changed_context_count"):
                check_natural(row.get(field), "INVALID_COUNT_" + field.upper())
            require(row["before_word_count"] > 0 and row["after_word_count"] > 0, "EMPTY_ARTICLE")
            require(type(row.get("citation_sequence_changed")) is bool, "INVALID_SEQUENCE_FLAG")
            changes = row.get("occurrence_changes")
            require(type(changes) is list, "INVALID_OCCURRENCE_CHANGES")
            ids = []
            for change in changes:
                require(type(change) is dict, "INVALID_SOURCE_DELTA")
                sid = change.get("source_id")
                require(type(sid) is str and bool(SOURCE.fullmatch(sid)), "INVALID_SOURCE_ID")
                ids.append(sid)
                check_natural(change.get("before"), "INVALID_BEFORE_OCCURRENCES")
                check_natural(change.get("after"), "INVALID_AFTER_OCCURRENCES")
                require(change["before"] != change["after"], "NOOP_SOURCE_DELTA")
            require(ids == sorted(set(ids)), "DUPLICATE_OR_UNSORTED_SOURCE_DELTA")
            require(sum(x["after"] - x["before"] for x in changes) == row["after_citation_count"] - row["before_citation_count"], "CITATION_CONSERVATION_MISMATCH")
            require((not changes) or row["citation_sequence_changed"], "CITATION_SEQUENCE_CONTRADICTION")
            examples = row.get("context_examples")
            require(type(examples) is list and len(examples) <= 5 and len(examples) <= row["same_source_id_changed_context_count"], "UNSOUND_CONTEXT_EXAMPLES")
            keys = []
            for item in examples:
                require(type(item) is dict and set(item) == {"citation", "before", "after"}, "MALFORMED_CONTEXT_EXAMPLE")
                keys.append(item["citation"])
                require(type(item["citation"]) is str and bool(re.fullmatch(r"[a-z0-9-]+#[1-9][0-9]*", item["citation"])), "BAD_CITATION_OCCURRENCE_KEY")
                require(type(item["before"]) is str and type(item["after"]) is str and item["before"] != item["after"] and len(item["before"]) <= 140 and len(item["after"]) <= 140, "INVALID_CONTEXT_DIFFERENCE")
            require(len(keys) == len(set(keys)), "DUPLICATE_CONTEXT_KEY")
    require(set(found) == expected_changed, "MISSING_OR_EXTRA_CHANGED_BODIES")
    return {"state": "HOLD", "may_publish": False, "may_merge": False,
            "article_count": len(bodies), "changed_body_count": len(found),
            "unmodified_body_count": len(bodies) - len(found),
            "total_added_citation_tokens": sum(r["after_citation_count"] - r["before_citation_count"] for r in found.values()),
            "source_occurrence_delta_articles": sum(bool(r["occurrence_changes"]) for r in found.values()),
            "source_context_drift_articles": sum(bool(r["same_source_id_changed_context_count"]) for r in found.values()),
            "human_adjudication_required": sorted(found),
            "QD_status": "NOT_APPROVED", "medical_safety_status": "NOT_VERIFIED"}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshots",type=Path,required=True)
    parser.add_argument("--part-a",type=Path,required=True)
    parser.add_argument("--part-b",type=Path,required=True)
    a=parser.parse_args(argv)
    try:
        print(json.dumps(check(strict_json(a.snapshots),[strict_json(a.part_a),strict_json(a.part_b)]),indent=2,sort_keys=True))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print("HOLD: "+str(exc),file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
