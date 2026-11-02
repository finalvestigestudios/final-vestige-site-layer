#!/usr/bin/env python3
"""R81 PRIVATE HOLD: frozen/current/release-candidate seven-cluster Git custody.

Read-only review ledger. No content rewriting, source deduplication, approval
import, network fetch, publication, WordPress, navigation, or CMS calls.
Git blob equality establishes ancestry/custody ONLY, not claim support/safety.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

SCHEMA = "r81-seven-contributor-three-way-blob-and-source-custody-hold-v1"
MANIFEST = "preparedness/docs/R14-SEVEN-CLUSTER-GIT-BLOB-PARITY.json"
PINNED = {
    "start": ("claude/prep-start-bbfeb8", "2122d856fce9f64887c16df3d52e64be9f59a55b"),
    "shelter": ("claude/prep-shelter-5e1e0e", "5daeaf2dd5ab71806a6b73c91edfb1d8df5da976"),
    "food": ("claude/prep-food-ccdc55", "f911ff7a655de8d81535ea86ec3d65a49ee76648"),
    "health": ("claude/prep-health-837444", "d5ef5bafd68361434dd1cc9209915b8e8a4eaf17"),
    "hist-food": ("claude/prep-hist-food-b81f19", "67e116e536c7410bed30f8f3b1bb8c166f3c223d"),
    "hist-home": ("claude/prep-hist-home-0e0e38", "7504a5f099594d635e3dd7332a33a2e1346c43a2"),
    "hist-field": ("claude/prep-hist-field-9db767", "4e5caf812727953aa45e3bda2d382f2c67b6a09c"),
}
RC_BRANCH = "integration/preparedness-release-candidate-20261101"
RC_SHA = "ddb3528ba6494dada1fa1c3a142ce746e3a67706"
EXPECTED = (7, 29, 72)
HEX40 = re.compile(r"^[0-9a-f]{40}$")
CITES = re.compile(rb"\{\{cite:[^{}]+\}\}")
REVIEW = "NOT_REVIEWED"


class Hold(ValueError):
    """Evidence is unavailable, ambiguous, changed or incorrectly approved."""


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise Hold(reason)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(value: object) -> str:
    need(type(value) is str and value.startswith("preparedness/")
         and "\\" not in value and "\x00" not in value,
         "unsafe or out-of-scope path")
    p = PurePosixPath(value)
    need(str(p) == value and all(x not in ("", ".", "..") for x in value.split("/"))
         and ".git" not in p.parts and not value.endswith("/"),
         "noncanonical or traversal path")
    return value


def source_records(raw: bytes, origin: str) -> list[dict]:
    """Preserve full, separate candidate research readings; never normalize URLs."""
    need(type(origin) is str and bool(origin), "source origin missing")
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise Hold("source fragment is not complete UTF-8 JSON") from exc
    need(type(parsed) is dict and type(parsed.get("sources")) is list,
         "source fragment records missing")
    output, ids = [], set()
    for record in parsed["sources"]:
        need(type(record) is dict, "source reading is not a record")
        sid, url = record.get("id"), record.get("url")
        need(type(sid) is str and bool(sid)
             and type(url) is str and bool(url)
             and sid not in ids, "duplicate or malformed origin-scoped source")
        need(record.get("human_link_check") is False,
             "source has human-link clearance; release snapshot must be reviewed anew")
        ids.add(sid)
        output.append({
            "origin": origin, "source_id": sid, "exact_URL_UNVERIFIED": url,
            "complete_reading_NOT_HUMAN_VERIFIED": record,
            "complete_reading_sha256": sha256(json.dumps(
                record, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                allow_nan=False).encode("utf-8")),
            "claim_support_review": REVIEW,
            "qualified_safety_review": REVIEW,
        })
    return output


def classify(frozen: str, current: str, rc: str) -> str:
    for sha in (frozen, current, rc):
        need(type(sha) is str and bool(HEX40.fullmatch(sha)), "invalid Git blob SHA")
    if frozen == current == rc:
        return "FROZEN_CURRENT_AND_RC_IDENTICAL"
    if current != frozen and rc == current:
        return "RC_MATCHES_ADVANCED_CONTRIBUTOR"
    if current != frozen and rc == frozen:
        return "RC_RETAINS_FROZEN_NOT_ADVANCED"
    if current != frozen and rc != frozen and rc != current:
        return "THREE_DISTINCT_BLOBS_REVIEW"
    return "RC_DIFFERS_FROM_UNCHANGED_CONTRIBUTOR"


def guard_manifest(m: object) -> None:
    need(type(m) is dict and m.get("schema_version") == 1
         and m.get("issue") == 136 and m.get("release_state") == "HOLD"
         and m.get("may_publish") is False
         and m.get("human_source_review_complete") is False
         and m.get("qualified_emergency_safety_clearance") is False
         and m.get("independent_human_source_checks_verified") == 0
         and m.get("authority") == "GIT_BLOB_PARITY_ONLY_NOT_FACT_OR_SAFETY_APPROVAL",
         "frozen manifest assertions or HOLD status changed")
    need(type(m.get("reference_integrated_commit_sha")) is str
         and bool(HEX40.fullmatch(m["reference_integrated_commit_sha"])),
         "missing integrated frozen reference commit")
    branches = m.get("branches")
    need(type(branches) is list and len(branches) == EXPECTED[0],
         "seven original contributors not preserved")
    seen, paths, articles = set(), set(), 0
    for b in branches:
        need(type(b) is dict and b.get("name") in PINNED
             and b["name"] not in seen
             and type(b.get("files")) is list
             and type(b.get("contributor_commit_sha")) is str
             and bool(HEX40.fullmatch(b["contributor_commit_sha"])),
             "frozen branch identity or commit invalid")
        seen.add(b["name"])
        need(b.get("scoped_paths") == len(b["files"])
             and type(b.get("article_count")) is int
             and b["article_count"] > 0, "incomplete frozen contributor scope")
        articles += b["article_count"]
        for f in b["files"]:
            need(type(f) is dict, "missing manifest scoped file")
            p = safe_path(f.get("path"))
            need(p not in paths, "frozen path double-assigned across contributors")
            paths.add(p)
            need(type(f.get("identical")) is bool
                 and all(type(f.get(k)) is str
                         and bool(HEX40.fullmatch(f[k])) for k in
                         ("contributor_blob_sha", "integrated_blob_sha"))
                 and (f["contributor_blob_sha"] == f["integrated_blob_sha"])
                       == f["identical"], "frozen manifest blob parity inconsistent")
    need(seen == set(PINNED) and
         (len(branches), articles, len(paths)) == EXPECTED,
         "29 articles or 72 frozen scoped files missing")
    t = m.get("totals")
    need(type(t) is dict and
         (t.get("contributor_branches"), t.get("cluster_authored_articles"),
          t.get("scoped_blob_paths")) == EXPECTED
         and t.get("exact_matches") + t.get("nonidentical_paths") == 72,
         "historical original baseline totals changed")
    need(type(m.get("exceptions")) is list
         and len(m["exceptions"]) == t["nonidentical_paths"],
         "historical human-diff exceptions silently removed")
    for e in m["exceptions"]:
        need(type(e) is dict and e.get("state") == "NEEDS_HUMAN_DIFF_REVIEW"
             and (e.get("branch"), e.get("path")) in
             {(b["name"], f["path"]) for b in branches for f in b["files"]},
             "historical human-diff exception approved or relocated")


def git(root: Path, *args: str, allow_one: bool = False) -> bytes | bool:
    cmd = ["git", "-C", str(root), *args]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       check=False)
    if allow_one and p.returncode in (0, 1):
        return p.returncode == 0
    need(p.returncode == 0,
         "required Git evidence unavailable: " + " ".join(args[:3]))
    return p.stdout.strip() if args[:1] == ("rev-parse",) else p.stdout


def blob(root: Path, commit: str, path: str) -> tuple[str, bytes]:
    need(type(commit) is str and bool(HEX40.fullmatch(commit)),
         "Git commit must be pinned SHA")
    path = safe_path(path)
    blob_sha = git(root, "rev-parse", "--verify", commit + ":" + path).decode("ascii")
    need(bool(HEX40.fullmatch(blob_sha)), "file blob missing")
    raw = git(root, "cat-file", "blob", blob_sha)
    return blob_sha, raw


def pinned_ref(root: Path, branch: str, sha: str) -> None:
    need(type(branch) is str and branch and type(sha) is str
         and bool(HEX40.fullmatch(sha)), "invalid pinned ref")
    head = git(root, "rev-parse", "--verify",
               "refs/remotes/origin/" + branch + "^{commit}").decode("ascii")
    need(head == sha, "moving or unverified contributor/release-candidate ref: " + branch)


def three_way(root: Path, manifest: dict, heads: dict[str, str],
              rc_sha: str, verify_remote: bool = False) -> dict:
    """Exact Git tree comparison, no merge/rebaseline and no source approvals."""
    guard_manifest(manifest)
    need(type(heads) is dict and set(heads) == set(PINNED)
         and all(type(v) is str and bool(HEX40.fullmatch(v))
                 for v in heads.values())
         and type(rc_sha) is str and bool(HEX40.fullmatch(rc_sha)),
         "seven immutable current refs and RC required")
    if verify_remote:
        need(heads == {name: value[1] for name, value in PINNED.items()}
             and rc_sha == RC_SHA, "read-only production pins modified")
        for name, (branch, _) in PINNED.items():
            pinned_ref(root, branch, heads[name])
        pinned_ref(root, RC_BRANCH, rc_sha)
    frozen_integrated = manifest["reference_integrated_commit_sha"]
    rows, branch_summaries, rc_sources = [], [], []
    for b in manifest["branches"]:
        name, frozen, current = b["name"], b["contributor_commit_sha"], heads[b["name"]]
        ancestor = git(root, "merge-base", "--is-ancestor", frozen, current,
                       allow_one=True)
        branch_rows = []
        for f in b["files"]:
            path = f["path"]
            oldsha, old = blob(root, frozen, path)
            integrated_sha, integrated = blob(root, frozen_integrated, path)
            newsha, new = blob(root, current, path)
            rc_blob_sha, candidate = blob(root, rc_sha, path)
            need(oldsha == f["contributor_blob_sha"]
                 and integrated_sha == f["integrated_blob_sha"],
                 "historical R14 frozen or integrated Git evidence changed: " + path)
            row = {
                "origin": name, "path": path,
                "frozen_commit": frozen, "current_contributor_commit": current,
                "separate_rc_commit": rc_sha,
                "frozen_blob": oldsha, "R14_integrated_blob": integrated_sha,
                "current_blob": newsha, "rc_blob": rc_blob_sha,
                "comparison": classify(oldsha, newsha, rc_blob_sha),
                "historical_integration_exception": oldsha != integrated_sha,
                "byte_lengths": {
                    "frozen": len(old), "R14_integrated": len(integrated),
                    "current": len(new), "rc": len(candidate)},
                "sha256_entire_file_bytes": {
                    "frozen": sha256(old), "R14_integrated": sha256(integrated),
                    "current": sha256(new), "rc": sha256(candidate)},
                "citation_token_counts_NOT_CLAIM_PROOF": {
                    "frozen": len(CITES.findall(old)), "current": len(CITES.findall(new)),
                    "rc": len(CITES.findall(candidate))},
                "human_provenance_reconciliation": REVIEW,
                "human_claim_support": REVIEW,
                "qualified_safety_review": REVIEW,
                "may_publish": False,
            }
            rows.append(row)
            branch_rows.append(row)
            if path == "preparedness/sources/fragments/" + name + ".json":
                rc_sources.extend(source_records(candidate, name))
        need(len(branch_rows) == b["scoped_paths"],
             "contributor scoped file set incomplete")
        branch_summaries.append({
            "origin": name, "frozen_commit": frozen, "current_commit": current,
            "frozen_is_ancestor_of_current": ancestor,
            "ahead_of_frozen_REQUIRES_HUMAN_REVIEW": current != frozen,
            "scoped_files": len(branch_rows), "authored_articles": b["article_count"],
            "changed_against_frozen": sum(r["frozen_blob"] != r["current_blob"]
                                           for r in branch_rows),
            "rc_differs_from_current": sum(r["rc_blob"] != r["current_blob"]
                                            for r in branch_rows),
            "review_state": REVIEW,
        })
    need(len(rows) == 72 and len(rc_sources) > 0,
         "source fragment or one of the 72 historically scoped paths missing")
    urls, ids = defaultdict(list), defaultdict(list)
    for r in rc_sources:
        ident = {"origin": r["origin"], "source_id": r["source_id"],
                 "reading_sha256": r["complete_reading_sha256"]}
        urls[r["exact_URL_UNVERIFIED"]].append(ident)
        ids[r["source_id"]].append({**ident, "exact_URL_UNVERIFIED": r["exact_URL_UNVERIFIED"]})
    report = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "may_publish": False, "human_source_approvals": 0,
        "human_claim_approvals": 0, "qualified_safety_approvals": 0,
        "independent_QD_approvals": 0,
        "claims_of_medical_safety": False,
        "reference_integrated_commit": frozen_integrated,
        "separate_rc_commit": rc_sha,
        "counts": {"contributor_branches": 7, "cluster_authored_articles": 29,
                   "frozen_scoped_paths": 72,
                   "current_advanced_branches": sum(
                       v["ahead_of_frozen_REQUIRES_HUMAN_REVIEW"]
                       for v in branch_summaries),
                   "frozen_exception_paths_preserved": len(manifest["exceptions"]),
                   "rc_fragment_source_readings_UNREVIEWED": len(rc_sources),
                   "shared_exact_URL_groups_UNRESOLVED": sum(
                       len(v) > 1 for v in urls.values()),
                   "reused_source_ID_groups_UNRESOLVED": sum(
                       len(v) > 1 for v in ids.values())},
        "branch_reviews": branch_summaries,
        "all_72_three_way_scoped_Git_blob_reviews": rows,
        "historical_R14_human_diff_exceptions_UNRESOLVED": manifest["exceptions"],
        "all_RC_fragment_source_readings_UNABRIDGED_NOT_APPROVED": rc_sources,
        "shared_exact_URL_groups_NOT_ALIASED": [
            {"exact_URL": key, "distinct_origin_readings": value,
             "human_source_scope_review": REVIEW}
            for key, value in sorted(urls.items()) if len(value) > 1],
        "reused_ID_groups_NOT_ALIASED": [
            {"raw_source_id": key, "distinct_origin_readings": value,
             "human_source_scope_review": REVIEW}
            for key, value in sorted(ids.items()) if len(value) > 1],
    }
    report["sha256_seal"] = sha256(json.dumps(
        report, sort_keys=True, ensure_ascii=False, allow_nan=False,
        separators=(",", ":")).encode("utf-8"))
    return report


def verify(report: dict) -> None:
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("release_state") == "HOLD"
         and report.get("may_publish") is False
         and report.get("claims_of_medical_safety") is False
         and all(report.get(k) == 0 for k in
                 ("human_source_approvals", "human_claim_approvals",
                  "qualified_safety_approvals", "independent_QD_approvals")),
         "human/medical/release status must remain HOLD")
    expect = report.get("sha256_seal")
    rest = {k: v for k, v in report.items() if k != "sha256_seal"}
    need(type(expect) is str and expect == sha256(json.dumps(
        rest, sort_keys=True, ensure_ascii=False, allow_nan=False,
        separators=(",", ":")).encode("utf-8")), "altered R81 review ledger")
    n = report.get("counts", {})
    rows = report.get("all_72_three_way_scoped_Git_blob_reviews", [])
    need(n.get("frozen_scoped_paths") == len(rows) == 72
         and n.get("contributor_branches") == 7
         and n.get("cluster_authored_articles") == 29
         and len(report.get("branch_reviews", [])) == 7
         and len(report.get("all_RC_fragment_source_readings_UNABRIDGED_NOT_APPROVED", []))
                == n.get("rc_fragment_source_readings_UNREVIEWED"),
         "incomplete 7-branch, 29-article or 72-path review evidence")
    need(len({(r["origin"], r["path"]) for r in rows}) == 72
         and all(r["may_publish"] is False and
                 all(r[k] == REVIEW for k in
                     ("human_provenance_reconciliation", "human_claim_support",
                      "qualified_safety_review")) for r in rows),
         "review rows duplicated or release status falsified")


def safe_csv(value: object) -> str:
    s = str(value)
    return "'" + s if s.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else s


def reviewer_csv(report: dict) -> str:
    verify(report)
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["origin", "path", "frozen_blob", "current_blob", "rc_blob",
                     "comparison", "historical_exception", "human_review", "release"])
    for r in report["all_72_three_way_scoped_Git_blob_reviews"]:
        writer.writerow([safe_csv(r["origin"]), safe_csv(r["path"]),
                         r["frozen_blob"], r["current_blob"], r["rc_blob"],
                         safe_csv(r["comparison"]),
                         r["historical_integration_exception"], REVIEW, "HOLD"])
    return out.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description="R81 PRIVATE evidence only; NO PUBLICATION")
    parser.add_argument("--json-stdout", action="store_true",
                        help="private complete source-reading ledger to stdout")
    parser.add_argument("--csv-stdout", action="store_true",
                        help="private one-way, formula-neutralized review queue to stdout")
    args = parser.parse_args()
    need(not (args.json_stdout and args.csv_stdout), "choose one private export")
    root = Path(__file__).resolve().parents[2]
    source = root / MANIFEST
    need(source.is_file() and not source.is_symlink(),
         "immutable historical R14 manifest unavailable")
    manifest = json.loads(source.read_text(encoding="utf-8"))
    report = three_way(root, manifest,
                       {name: pin[1] for name, pin in PINNED.items()},
                       RC_SHA, verify_remote=True)
    verify(report)
    if args.json_stdout:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True,
                         indent=2, allow_nan=False))
    elif args.csv_stdout:
        print(reviewer_csv(report), end="")
    else:
        print("R81 PRIVATE HOLD: 7 contributor origins, 29 author-scoped articles, "
              "72 complete historical Git-path evidence comparisons verified")
        print("Pinned frozen/current/separate-RC Git objects compared without rewriting.")
        print("Advanced contributor branches: " +
              str(report["counts"]["current_advanced_branches"]))
        print("Unreviewed RC origin-scoped fragment records: " +
              str(report["counts"]["rc_fragment_source_readings_UNREVIEWED"]))
        print("Source/claim/qualified-safety/QD human approvals: ZERO; RELEASE HOLD")
        print("Deterministic full ledger SHA-256: " + report["sha256_seal"])


if __name__ == "__main__":
    main()
