#!/usr/bin/env python3
"""R108: read-only, exact-Git source/citation change impact crosswalk. PRIVATE HOLD.

R107 proves ancestry and lists changed contributor paths, not that claims are
correct. R108 reads BOTH exact Git blobs, checks their OIDs, and routes changes
to human reviewers without importing revised content or granting approvals.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r107_exact_branch_progression_adjudication as r107

SCHEMA = "r108-source-citation-change-impact-HOLD-v1"
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
CITE_ANY = re.compile(r"\{\{cite:([^{}]*)\}\}")
WORD = re.compile(r"\b[\w'-]+\b", flags=re.UNICODE)
HEADING = re.compile(r"<h[1-6]\b", re.IGNORECASE)
TAG = re.compile(r"<[^>]*>")
MAX_BYTES = 2_000_000
MAX_PATHS = 200


class Hold(ValueError):
    """An incomplete or untrusted change docket cannot proceed to review."""


def need(ok, reason):
    if not ok:
        raise Hold(reason)


def canonical_hash(data):
    return r107.digest(data)


def text_bytes(raw):
    need(type(raw) is bytes and len(raw) <= MAX_BYTES, "missing/oversize Git blob")
    return raw.decode("utf-8", "strict")


def _tokens(body):
    refs = CITE.findall(body)
    need(len(refs) == len(CITE_ANY.findall(body)) ==
         body.count("{{cite:"), "malformed or ambiguous citation token")
    return Counter(refs)


def summarize_body(raw):
    value = text_bytes(raw)
    refs = _tokens(value)
    visible = TAG.sub(" ", value)
    return {
        "citation_occurrences": dict(sorted(refs.items())),
        "citation_total": sum(refs.values()),
        "word_count_estimate": len(WORD.findall(visible)),
        "heading_count": len(HEADING.findall(value)),
        "safety_notice_marker_count": value.count('class="pa-act') +
            value.count('class="pa-tag--unc'),
        "length_bytes": len(raw),
    }


def _object(raw, name):
    out = json.loads(text_bytes(raw))
    need(type(out) is dict, name + " must be JSON object")
    return out


def summarize_meta(raw):
    x = _object(raw, "article metadata")
    need(type(x.get("slug")) is str and
         type(x.get("status")) is dict and
         type(x.get("safety_review")) is dict and
         type(x.get("source_use")) is dict,
         "article metadata lacks slug, status, safety or source-use fields")
    use = x["source_use"]
    need(all(type(k) is str and type(v) is str for k, v in use.items()),
         "invalid source-use claims")
    return {
        "slug": x["slug"],
        "publish_status": x["status"].get("publish"),
        "editorial_status": x["status"].get("editorial"),
        "safety_state": x["safety_review"].get("state"),
        "safety_review_changed_fields": {
            k: canonical_hash(v) for k, v in sorted(x["safety_review"].items())
        },
        "source_use_claim_sha256": {k: canonical_hash(v)
                                    for k, v in sorted(use.items())},
        "last_checked": x.get("last_checked"),
        "word_count_estimate": len(WORD.findall(" ".join(use.values()))),
    }


def summarize_fragment(raw):
    x = _object(raw, "source fragment")
    data = x.get("sources")
    need(type(data) is list and len(data) <= 2000,
         "source fragment must hold a bounded sources list")
    rows = {}
    for v in data:
        need(type(v) is dict and type(v.get("id")) is str and
             re.fullmatch(r"[a-z0-9-]+", v["id"]) and
             v["id"] not in rows and type(v.get("url")) is str,
             "invalid/duplicated source identity or missing literal URL")
        rows[v["id"]] = {
            "url": v["url"], "publisher": v.get("publisher"),
            "supports_digest": canonical_hash(v.get("supports")),
            "notes_digest": canonical_hash(v.get("notes")),
            "reading_scope_digest": canonical_hash(v.get("reading_scope")),
            "human_link_check": v.get("human_link_check"),
            "verified_on": v.get("verified_on"),
            "whole_record_digest": canonical_hash(v),
        }
    return rows


def delta(before, after, kind):
    if kind == "body":
        a, b = summarize_body(before), summarize_body(after)
        ca, cb = Counter(a["citation_occurrences"]), Counter(b["citation_occurrences"])
        return {
            "citations_added": dict(sorted((cb-ca).items())),
            "citations_removed": dict(sorted((ca-cb).items())),
            "citation_total_before": a["citation_total"],
            "citation_total_after": b["citation_total"],
            "words_before_estimate": a["word_count_estimate"],
            "words_after_estimate": b["word_count_estimate"],
            "heading_count_before": a["heading_count"],
            "heading_count_after": b["heading_count"],
            "safety_marker_count_before": a["safety_notice_marker_count"],
            "safety_marker_count_after": b["safety_notice_marker_count"],
            "depth_reduction_needs_review":
                b["word_count_estimate"] < a["word_count_estimate"],
            "safety_marker_reduction_needs_review":
                b["safety_notice_marker_count"] < a["safety_notice_marker_count"],
        }
    if kind == "meta":
        a, b = summarize_meta(before), summarize_meta(after)
        au, bu = a["source_use_claim_sha256"], b["source_use_claim_sha256"]
        return {
            "slug_changed": a["slug"] != b["slug"],
            "slug_before": a["slug"], "slug_after": b["slug"],
            "publication_changed": a["publish_status"] != b["publish_status"],
            "publication_before": a["publish_status"],
            "publication_after": b["publish_status"],
            "editorial_changed": a["editorial_status"] != b["editorial_status"],
            "safety_state_changed": a["safety_state"] != b["safety_state"],
            "safety_state_before": a["safety_state"],
            "safety_state_after": b["safety_state"],
            "safety_review_fields_changed": sorted(k for k in
                a["safety_review_changed_fields"].keys() |
                b["safety_review_changed_fields"].keys()
                if a["safety_review_changed_fields"].get(k) !=
                b["safety_review_changed_fields"].get(k)),
            "source_use_added": sorted(bu.keys() - au.keys()),
            "source_use_removed": sorted(au.keys() - bu.keys()),
            "source_use_reinterpreted": sorted(k for k in au.keys() & bu.keys()
                                                if au[k] != bu[k]),
            "source_use_words_before_estimate": a["word_count_estimate"],
            "source_use_words_after_estimate": b["word_count_estimate"],
            "last_checked_changed": a["last_checked"] != b["last_checked"],
            "proposed_release_status_is_not_draft": b["publish_status"] != "draft",
            "changed_safety_record_requires_human_review":
                a["safety_review_changed_fields"] != b["safety_review_changed_fields"],
        }
    if kind == "fragment":
        a, b = summarize_fragment(before), summarize_fragment(after)
        return {
            "source_ids_added": sorted(b.keys() - a.keys()),
            "source_ids_removed": sorted(a.keys() - b.keys()),
            "source_ids_changed": sorted(k for k in a.keys() & b.keys()
                                         if a[k] != b[k]),
            "literal_urls_changed": sorted(k for k in a.keys() & b.keys()
                                           if a[k]["url"] != b[k]["url"]),
            "reading_support_changed": sorted(k for k in a.keys() & b.keys()
                if (a[k]["supports_digest"], a[k]["notes_digest"],
                    a[k]["reading_scope_digest"]) !=
                   (b[k]["supports_digest"], b[k]["notes_digest"],
                    b[k]["reading_scope_digest"])),
            "human_link_check_value_changed": sorted(k for k in a.keys() & b.keys()
                if a[k]["human_link_check"] != b[k]["human_link_check"]),
            "verified_date_changed": sorted(k for k in a.keys() & b.keys()
                if a[k]["verified_on"] != b[k]["verified_on"]),
            "unchanged_literal_url_does_not_imply_same_source_scope": True,
        }
    return {"non_article_evidence_changed": True,
            "human_diff_review_required": True}


def crosswalk(queue, fetch_blob):
    """Pure, bounded, exact-OID reviewer queue. fetch_blob(sha, path)->bytes.

    Caller supplies Git object reads; never path data from a stranger without
    R107's exact SHA/manifest/ancestry custody gate.
    """
    need(type(queue) is dict and queue.get("schema") == r107.SCHEMA and
         queue.get("release_state") == "HOLD" and queue.get("may_publish") is False and
         queue.get("source_or_claim_accuracy_verified") is False and
         queue.get("qualified_emergency_or_medical_safety_review") is False and
         queue.get("independent_QD_PASS") is False and
         queue.get("frozen_R14_historical_exception_open") is True and
         queue.get("mandatory_R15_seven_cluster_parity") ==
         "FAIL_CLOSED_ON_MOVED_REFS" and
         queue.get("sha256_NOT_A_SIGNATURE") ==
         canonical_hash({k: v for k, v in queue.items()
                         if k != "sha256_NOT_A_SIGNATURE"}),
         "missing or altered R107 original evidence custody/HOLD seal")
    origins = queue.get("seven_contributor_commit_ancestry")
    rows = queue.get("contributor_reviewer_queue_NOT_APPROVED")
    need(type(origins) is list and len(origins) == 7 and
         type(rows) is list and len(rows) <= MAX_PATHS and
         queue.get("changed_path_count") == len(rows),
         "invalid seven-branch or changed-path R107 census")
    tip = {}
    for x in origins:
        need(type(x) is dict and x.get("origin") in r107.EXPECTED_HEADS and
             x.get("origin") not in tip and
             x.get("observed_commit_sha") == r107.EXPECTED_HEADS[x["origin"]] and
             x.get("is_direct_descendant") is True and
             x.get("human_lineage_approval") == "NOT_REVIEWED",
             "untrusted contributor SHA/lineage approval")
        tip[x["origin"]] = x
    need(set(tip) == set(r107.EXPECTED_HEADS),
         "seven contributor origins incomplete")
    output, seen = [], set()
    for row in rows:
        need(type(row) is dict and
             row.get("origin") in tip and
             row.get("path") is not None and
             r107.r60.valid_path(row["path"]) and
             row.get("classification") == r107.kind(row["path"]) and
             row.get("human_provenance_review") == "NOT_REVIEWED" and
             row.get("human_source_and_claim_review") == "NOT_REVIEWED" and
             row.get("may_publish") is False and
             (row["origin"], row["path"]) not in seen,
             "altered source path/classification or forged approval")
        seen.add((row["origin"], row["path"]))
        old_sha, new_sha = row.get("frozen_blob_sha"), row.get("current_blob_sha")
        need((old_sha is None or (type(old_sha) is str and r107.SHA.fullmatch(old_sha))) and
             (new_sha is None or (type(new_sha) is str and r107.SHA.fullmatch(new_sha))) and
             (old_sha is not None or new_sha is not None) and old_sha != new_sha,
             "missing/invalid Git object SHA pair")
        old = fetch_blob(tip[row["origin"]]["frozen_commit_sha"], row["path"]) if old_sha else None
        new = fetch_blob(tip[row["origin"]]["observed_commit_sha"], row["path"]) if new_sha else None
        for raw, oid in ((old, old_sha), (new, new_sha)):
            if oid:
                need(type(raw) is bytes and len(raw) <= MAX_BYTES and
                     r107.r60.blob_sha(raw) == oid,
                     "Git object changed/missing or supplied blob not matching R107")
        kind = row["classification"]
        if old is not None and new is not None:
            change = delta(old, new, kind)
        else:
            change = {"path_created_or_removed": True,
                      "human_new_or_removed_file_review_required": True}
        output.append({
            "origin": row["origin"], "path": row["path"],
            "category": kind, "frozen_oid": old_sha, "observed_oid": new_sha,
            "original_72_path_scope": row.get("original_72_path_scope"),
            "change_indicators_NOT_FACT_VERDICTS": change,
            "human_source_or_claim_review": "NOT_REVIEWED",
            "human_safety_review": "NOT_REVIEWED",
            "may_publish": False,
        })
    result = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "may_publish": False, "factual_claim_support_approved": False,
        "qualified_emergency_safety_approved": False, "independent_QD_PASS": False,
        "source_records_transferred_to_CMS": False,
        "R107_queue_sha256_NOT_A_SIGNATURE": queue["sha256_NOT_A_SIGNATURE"],
        "original_35_article_slate_unchanged": True,
        "scope": "EXACT_CHANGED_CONTRIBUTOR_PATHS_ONLY_NOT_FULL_35_FACT_AUDIT",
        "original_historical_metadata_exception_open": True,
        "unreviewed_shared_source_url_groups": 30,
        "row_count": len(output),
        "rows_NOT_APPROVED": sorted(output, key=lambda x: (x["origin"], x["path"])),
        "review_instructions": (
            "Compare each revised passage with its original source and reading "
            "scope, human-check each cited URL and safety warning, and approve "
            "separately through the authorized human/QD lane. This report never "
            "changes the historical R15 parity failure or publication HOLD."
        ),
    }
    result["sha256_NOT_A_SIGNATURE"] = canonical_hash(result)
    return result


def git_object(root, commit, path):
    need(type(commit) is str and r107.SHA.fullmatch(commit) and
         r107.r60.valid_path(path), "unsafe Git reader argument")
    result = subprocess.run(
        ["git", "-C", str(root), "show", commit + ":" + path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=20)
    need(result.returncode == 0 and len(result.stdout) <= MAX_BYTES,
         "Git object read failed or exceeded 2MB bound")
    return result.stdout


def scan(root):
    report = r107.scan(root)
    return crosswalk(report, lambda commit, path: git_object(root, commit, path))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=r107.ROOT)
    parser.add_argument("--json", action="store_true", help="Private reviewer rows")
    args = parser.parse_args(argv)
    report = scan(args.repo_root.resolve())
    if args.json:
        print(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({
            "schema": SCHEMA, "release_state": "HOLD", "may_publish": False,
            "row_count": report["row_count"],
            "sha256_NOT_A_SIGNATURE": report["sha256_NOT_A_SIGNATURE"],
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Hold, r107.Hold, r107.r60.DriftHold, ValueError, OSError,
            UnicodeError, subprocess.TimeoutExpired, KeyError) as exc:
        print("R108 SOURCE/CITATION CROSSWALK HOLD: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
