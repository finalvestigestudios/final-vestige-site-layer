#!/usr/bin/env python3
"""R107: exact Git ancestry and author-scoped adoption workorder. PRIVATE HOLD.

R15's historical parity gate remains STRICT and fails on moved contributor
heads. This independent, read-only workorder shows what needs human adjudication;
it never re-pins a branch, imports an article, approves a source, or releases.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

# -I removes the script directory from sys.path; pin imports to our own tools.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cluster_git_parity_gate as r15
import r60_contributor_provenance_drift_docket as r60

SCHEMA = "r107-seven-contributor-lineage-adoption-hold-v1"
EXPECTED_HEADS = {
    "start": "2122d856fce9f64887c16df3d52e64be9f59a55b",
    "shelter": "5daeaf2dd5ab71806a6b73c91edfb1d8df5da976",
    "food": "f911ff7a655de8d81535ea86ec3d65a49ee76648",
    "health": "d5ef5bafd68361434dd1cc9209915b8e8a4eaf17",
    "hist-food": "67e116e536c7410bed30f8f3b1bb8c166f3c223d",
    "hist-home": "7504a5f099594d635e3dd7332a33a2e1346c43a2",
    "hist-field": "4e5caf812727953aa45e3bda2d382f2c67b6a09c",
}
EXPECTED_RC = "ddb3528ba6494dada1fa1c3a142ce746e3a67706"
EXPECTED_ARTICLES = dict(r15.EXPECTED)
# Extra attention to evidence-bearing changes; this is a routing hint, never a safety verdict.
RISK = {
    "fragment": "SOURCE_IDENTITY_AND_SUPPORTS_HUMAN_REVIEW",
    "body": "ARTICLE_CLAIMS_AND_CITATIONS_HUMAN_REVIEW",
    "meta": "SOURCE_USE_STATUS_AND_SAFETY_HUMAN_REVIEW",
    "doc": "CONTRIBUTOR_RESEARCH_LOG_HUMAN_REVIEW",
    "test": "TEST_PROVENANCE_HUMAN_REVIEW",
    "other": "UNCLASSIFIED_CHANGE_HUMAN_REVIEW",
}
SHA = re.compile(r"[0-9a-f]{40}\Z")
MAX_ROWS = 200
ROOT = Path(__file__).resolve().parents[2]


class Hold(ValueError):
    """Evidence is incomplete or attempts to turn engineering into permission."""


def need(condition, message):
    if not condition:
        raise Hold(message)


def digest(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
                     allow_nan=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def kind(path):
    need(r60.valid_path(path), "unsafe contributor change path")
    if path.startswith("preparedness/sources/fragments/") and path.endswith(".json"):
        return "fragment"
    if path.startswith("preparedness/content/articles/") and path.endswith(".body.html"):
        return "body"
    if path.startswith("preparedness/content/articles/") and path.endswith(".meta.json"):
        return "meta"
    if path.startswith("preparedness/docs/CLUSTER-") and path.endswith(".md"):
        return "doc"
    if path.startswith("preparedness/tests/") and path.endswith(".py"):
        return "test"
    return "other"


def workorder(manifest, drift, *, is_ancestor, integrated_blob):
    """Pure reconciler. Its drift argument MUST come from fresh r60.report Git checks.

    No matching of source URLs is interpreted as matching source support.
    No 'adoption' status here is permission to accept revised contributor text.
    """
    need(type(manifest) is dict and manifest.get("authority") ==
         "GIT_BLOB_PARITY_ONLY_NOT_FACT_OR_SAFETY_APPROVAL" and
         manifest.get("release_state") == "HOLD" and manifest.get("may_publish") is False
         and manifest.get("reference_integrated_commit_sha") == r15.R13_SHA
         and manifest.get("human_source_review_complete") is False
         and manifest.get("qualified_emergency_safety_clearance") is False
         and manifest.get("independent_human_source_checks_verified") == 0,
         "frozen source manifest/HOLD contract not intact")
    need(type(manifest.get("branches")) is list and len(manifest["branches"]) == 7,
         "seven historical clusters required")
    branches = {b["name"]: b for b in manifest["branches"]
                if type(b) is dict and b.get("name") in EXPECTED_HEADS}
    need(set(branches) == set(EXPECTED_HEADS) and
         len({b["name"] for b in manifest["branches"]}) == 7
         and sum(b["article_count"] for b in branches.values()) == 29
         and sum(len(b["files"]) for b in branches.values()) == 72,
         "29 original contributor articles / 72 provenance paths required")
    need(all(branches[k]["article_count"] == EXPECTED_ARTICLES[k] for k in branches),
         "cluster article census changed")
    frozen_paths = {}
    for origin, b in branches.items():
        need(type(b.get("files")) is list and
             len(b["files"]) == 2 * EXPECTED_ARTICLES[origin] + 2,
             "incomplete contributor author scope")
        for f in b["files"]:
            path = f["path"]
            need(r60.valid_path(path) and path not in frozen_paths and
                 r15.SHA1.fullmatch(f["contributor_blob_sha"]) and
                 r15.SHA1.fullmatch(f["integrated_blob_sha"]) and
                 type(f["identical"]) is bool and
                 f["identical"] == (f["contributor_blob_sha"] ==
                                    f["integrated_blob_sha"]),
                 "duplicated or altered frozen evidence path")
            frozen_paths[path] = (origin, f)
    need(len(frozen_paths) == 72 and
         sum(not f["identical"] for _, f in frozen_paths.values()) == 1
         and manifest.get("exceptions") and
         len(manifest["exceptions"]) == 1 and
         manifest["exceptions"][0].get("state") == "NEEDS_HUMAN_DIFF_REVIEW",
         "historical source-use discrepancy was removed")
    need(type(drift) is dict and drift.get("schema") == r60.SCHEMA
         and drift.get("release_state") == "HOLD" and
         drift.get("may_publish") is False and
         drift.get("fingerprint_sha256") ==
         r60.sha256(r60.canonical({k: v for k, v in drift.items()
                                   if k != "fingerprint_sha256"}))
         and drift.get("frozen_manifest_blob_sha") == r60.R14_BLOB
         and drift.get("checked_clusters") == 7
         and drift.get("existing_R14_exception_remains_open") is True
         and drift.get("human_source_links_verified") is False
         and drift.get("qualified_safety_clearance") is False
         and drift.get("independent_QD_approval") is False,
         "Git-derived R60 custody must remain complete and unapproved")
    moved = drift.get("moved_contributor_heads")
    changes = drift.get("changed_files")
    need(type(moved) is list and type(changes) is list
         and len(changes) <= MAX_ROWS
         and drift.get("changed_file_count") == len(changes),
         "missing or oversized exact Git progression changes")
    observed = {key: branches[key]["contributor_commit_sha"] for key in branches}
    moved_seen = set()
    for m in moved:
        origin = m.get("cluster")
        need(origin in branches and origin not in moved_seen and m.get("frozen_commit_sha") ==
             branches[origin]["contributor_commit_sha"] and
             type(m.get("observed_commit_sha")) is str and
             SHA.fullmatch(m["observed_commit_sha"]) and
             m["observed_commit_sha"] != observed[origin],
             "untrusted moved branch evidence")
        moved_seen.add(origin)
        observed[origin] = m["observed_commit_sha"]
    need(observed == EXPECTED_HEADS and len(moved) == 5,
         "live contributor SHA moved since this human-review workorder was pinned")
    comparisons = []
    for origin in sorted(branches):
        frozen = branches[origin]["contributor_commit_sha"]
        current = observed[origin]
        need(is_ancestor(frozen, current) is True,
             origin + ": frozen commit is NOT an ancestor of proposed head")
        comparisons.append({
            "origin": origin, "frozen_commit_sha": frozen,
            "observed_commit_sha": current,
            "is_direct_descendant": True,
            "branch_moved": frozen != current,
            "human_lineage_approval": "NOT_REVIEWED",
        })
    seen = set()
    review = []
    for item in changes:
        origin, path = item.get("cluster"), item.get("path")
        need(origin in branches and r60.valid_path(path)
             and (origin, path) not in seen
             and type(item.get("frozen_blob_sha")) in (str, type(None))
             and type(item.get("observed_blob_sha")) in (str, type(None))
             and item.get("frozen_blob_sha") != item.get("observed_blob_sha")
             and item.get("human_provenance_review_state") == "NOT_REVIEWED",
             "changed-file evidence missing, duplicated or pre-approved")
        seen.add((origin, path))
        if path in frozen_paths:
            owner, frozen_row = frozen_paths[path]
            need(owner == origin and
                 frozen_row["contributor_blob_sha"] == item["frozen_blob_sha"],
                 "changed frozen file reassigned to a different contributor")
            integrated = integrated_blob(r15.R13_SHA, path)
            need(integrated == frozen_row["integrated_blob_sha"],
                 "historical integrated Git blob changed")
            current = item["observed_blob_sha"]
            state = ("CURRENT_EQUALS_INTEGRATED" if current == integrated
                     else "CURRENT_DIFFERS_FROM_INTEGRATED_REVIEW"
                     if item["frozen_blob_sha"] != integrated
                     else "POST_FREEZE_CHANGE_NOT_IN_INTEGRATED")
        else:
            integrated = None
            state = "OUTSIDE_ORIGINAL_72_PATH_SCOPE_REVIEW"
        category = kind(path)
        review.append({
            "origin": origin, "path": path,
            "original_72_path_scope": path in frozen_paths,
            "classification": category, "risk_queue": RISK[category],
            "frozen_blob_sha": item["frozen_blob_sha"],
            "current_blob_sha": item["observed_blob_sha"],
            "integrated_blob_sha": integrated,
            "integration_relationship_NOT_APPROVAL": state,
            "human_provenance_review": "NOT_REVIEWED",
            "human_source_and_claim_review": "NOT_REVIEWED",
            "may_publish": False,
        })
    # A move with unmodified scoped files still requires human Git-lineage review.
    counts = Counter(row["classification"] for row in review)
    result = {
        "schema": SCHEMA, "issue": 136, "authority": "READ_ONLY_GIT_PROVENANCE_NOT_SAFETY_REVIEW",
        "release_state": "HOLD", "may_publish": False,
        "source_or_claim_accuracy_verified": False,
        "qualified_emergency_or_medical_safety_review": False,
        "independent_QD_PASS": False,
        "site_or_wordpress_write": False,
        "frozen_R14_manifest_blob_sha": r60.R14_BLOB,
        "frozen_R14_historical_exception_open": True,
        "mandatory_R15_seven_cluster_parity": "FAIL_CLOSED_ON_MOVED_REFS",
        "seven_contributor_commit_ancestry": comparisons,
        "distinct_original_articles": 29,
        "original_evidence_paths": 72,
        "moved_branch_count": 5,
        "changed_path_count": len(review),
        "change_classification_counts": dict(sorted(counts.items())),
        "contributor_reviewer_queue_NOT_APPROVED": sorted(
            review, key=lambda x: (x["origin"], x["path"])),
        "unreviewed_shared_url_groups": 30,
        "human_safety_exceptions_unresolved": 15,
        "editorial_decisions_unresolved": 22,
        "review_protocol": (
            "Human reviewer must examine exact Git diff and source-use/citation "
            "context for each changed path and the original R14 metadata exception. "
            "A descendant commit is not approved merely because ancestry holds. "
            "Keep R15 parity gate closed; never rewrite frozen pins or source records."
        ),
    }
    result["sha256_NOT_A_SIGNATURE"] = digest(result)
    return result


def git_is_ancestor(root, frozen, current):
    need(SHA.fullmatch(frozen) and SHA.fullmatch(current),
         "untrusted Git ancestry SHA")
    process = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", frozen, current],
        capture_output=True, timeout=15, check=False)
    need(process.returncode in (0, 1),
         "Git ancestry could not be confirmed")
    return process.returncode == 0


def git_head(root, ref):
    need(ref in (*r15.BRANCHES.values(),
                 "integration/preparedness-release-candidate-20261101"),
         "untrusted remote branch")
    data = r60.git(root, "rev-parse", "--verify",
                   "refs/remotes/origin/" + ref + "^{commit}", limit=100)
    value = data.decode("ascii").strip()
    need(SHA.fullmatch(value), "invalid observed Git head")
    return value


def scan(root):
    source = root / "preparedness/docs/R14-SEVEN-CLUSTER-GIT-BLOB-PARITY.json"
    need(source.is_file() and not source.is_symlink() and
         source.stat().st_size <= 2_000_000,
         "frozen R14 manifest is missing or unsafe")
    raw = source.read_bytes()
    need(r60.blob_sha(raw) == r60.R14_BLOB,
         "historical R14 manifest blob not pinned")
    manifest = json.loads(raw.decode("utf-8"))
    heads = {origin: git_head(root, ref)
             for origin, ref in r15.BRANCHES.items()}
    need(git_head(root, "integration/preparedness-release-candidate-20261101") ==
         EXPECTED_RC, "independent release candidate ref moved")
    # This validates the historical 72 Git blob claims without pretending that
    # the moved current contributor refs match the old frozen R14 pins.
    by_name = {b["name"]: b["contributor_commit_sha"]
               for b in manifest["branches"]}
    r15.check_manifest(
        manifest, lambda sha, path: r15.git_blob(root, sha, path),
        lambda name: by_name.get(next(
            (origin for origin, ref in r15.BRANCHES.items() if ref == name), "")),
        integrated_head=r15.R14_SHA)
    drift = r60.report(
        manifest, heads,
        lambda old, new: r60.git_changed(root, old, new),
        lambda sha, path: r60.git_blob(root, sha, path),
        lambda sha, path: r60.git_read(root, sha, path),
        lambda doc: None, r15.BRANCHES)
    return workorder(
        manifest, drift,
        is_ancestor=lambda old, new: git_is_ancestor(root, old, new),
        integrated_blob=lambda sha, path: r15.git_blob(root, sha, path))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=ROOT)
    p.add_argument("--json", action="store_true",
                   help="Emit private review queue, never import into CMS")
    args = p.parse_args(argv)
    result = scan(args.repo_root.resolve())
    if args.json:
        print(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({
            "schema": SCHEMA, "release_state": "HOLD", "may_publish": False,
            "moved_branch_count": result["moved_branch_count"],
            "changed_path_count": result["changed_path_count"],
            "change_classification_counts": result["change_classification_counts"],
            "sha256_NOT_A_SIGNATURE": result["sha256_NOT_A_SIGNATURE"],
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Hold, r60.DriftHold, r15.ParityFailure, OSError, ValueError,
            KeyError, UnicodeError, subprocess.TimeoutExpired) as err:
        print("R107 PRIVATE PROVENANCE HOLD: " + str(err), file=sys.stderr)
        raise SystemExit(2)
