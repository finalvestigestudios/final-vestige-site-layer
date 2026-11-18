#!/usr/bin/env python3
"""R460 original-branch blob crosswalk: provenance only, NEVER source/QD clearance.

Reads a pinned, externally captured GitHub *blob identity* snapshot. Does not
fetch URLs, merge origins, write to the site/CMS, or certify the claims. Full
human claim-to-source review, original build and release remain HARD HOLD.

python -I preparedness/tools/r460_origin_branch_blob_crosswalk.py --snapshot preparedness/audits/R460_ORIGIN_BRANCH_BLOB_SNAPSHOT.json
A valid report exits 2 (HARD HOLD); invalid provenance also exits 2 with errors.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

STATE = "DRAFT_HARD_HOLD"
REPO = "finalvestigestudios/final-vestige-site-layer"
CANDIDATE_SHA = "9b4846d2b2a94f7aeee2689e9b738f94a9eab97a"
CANDIDATE_BRANCH = "review/preparedness-r459-entire-draft-surface-custody-20261118"
ORIGINS = {
    "food": ("claude/prep-food-ccdc55", "f911ff7a655de8d81535ea86ec3d65a49ee76648"),
    "health": ("claude/prep-health-837444", "d5ef5bafd68361434dd1cc9209915b8e8a4eaf17"),
    "hist_field": ("claude/prep-hist-field-9db767", "4e5caf812727953aa45e3bda2d382f2c67b6a09c"),
    "hist_food": ("claude/prep-hist-food-b81f19", "67e116e536c7410bed30f8f3b1bb8c166f3c223d"),
    "hist_home": ("claude/prep-hist-home-0e0e38", "7504a5f099594d635e3dd7332a33a2e1346c43a2"),
    "shelter": ("claude/prep-shelter-5e1e0e", "5daeaf2dd5ab71806a6b73c91edfb1d8df5da976"),
    "start": ("claude/prep-start-bbfeb8", "2122d856fce9f64887c16df3d52e64be9f59a55b"),
    "shelter_cont": ("claude/prep-shelter-continuation", "ac8625faf30dd5538fadc31e06cb5a2cea1defae"),
    "shelter_follow": ("claude/prep-shelter-followup-evidence", "6a5998ead97eca997e573ce8d3ceacf1c6aabad4"),
}
REVIEW_REFS = {
    "qa157": "7d1ae6b8ef93d10cfb6810987672360885e9c1aa",
    "fixture169": "e9cd7766dac59d47ab467d8945269b9146c2aef5",
    "repair2205": "bbcf1859768624c611df4abadc564c18247cf32a",
    "editorial2789": "00a82df32a49a792540b178ebf7f1f271040e2a0",
    "home2985": "c724b7cc6789337a94596e4c37b5a4be4de1baaa",
}
SHA = re.compile(r"[0-9a-f]{40}\Z")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SOURCE = re.compile(r"(?:register\.json|crosswalk\.json|article-evidence-lock\.json|fragments/(?:README\.md|[a-z0-9-]+\.(?:json|md)))\Z")

class OriginHold(ValueError):
    """A review-only provenance defect; never a publishing decision."""

def _sha(value, where):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise OriginHold(f"invalid git blob or commit SHA at {where}")
    return value

def _source_files(files, where):
    if not isinstance(files, dict) or "register.json" not in files:
        raise OriginHold(f"{where}: original source register absent")
    if len(files) != len(set(files)) or any(not SOURCE.fullmatch(p) for p in files):
        raise OriginHold(f"{where}: source path invalid")
    for p, sha in files.items():
        _sha(sha, f"{where}/{p}")
    return files

def _articles(articles, where, *, complete=False):
    if not isinstance(articles, dict) or not articles:
        raise OriginHold(f"{where}: missing article identity inventory")
    if complete and len(articles) != 35:
        raise OriginHold(f"{where}: original 35-article slate incomplete/expanded")
    for slug, pair in articles.items():
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            raise OriginHold(f"{where}: unsafe slug {slug!r}")
        if not isinstance(pair, dict) or set(pair) != {"body", "meta"}:
            raise OriginHold(f"{where}/{slug}: orphan/extra author files")
        for kind in ("body", "meta"):
            _sha(pair[kind], f"{where}/{slug}.{kind}")
    return articles

def _entry(obj, where, expected_branch, expected_sha, *, complete=False):
    if not isinstance(obj, dict) or set(obj) != {"branch", "sha", "articles", "sources"}:
        raise OriginHold(f"{where}: malformed Git tree evidence")
    if obj["branch"] != expected_branch or _sha(obj["sha"], where) != expected_sha:
        raise OriginHold(f"{where}: ref drift, source substitution or unreviewed commit")
    _source_files(obj["sources"], where)
    _articles(obj["articles"], where, complete=complete)

def analyze(snapshot):
    if not isinstance(snapshot, dict) or set(snapshot) != {"schema", "repository", "release_state", "qualified_qd_pass", "candidate", "origins", "review_refs"}:
        raise OriginHold("snapshot missing mandatory custody fields")
    if (snapshot["schema"] != "r460-origin-blob-v1" or snapshot["repository"] != REPO
            or snapshot["release_state"] != STATE or snapshot["qualified_qd_pass"] is not False):
        raise OriginHold("unreviewed schema/repository or false release/QD state")
    for k, sha in REVIEW_REFS.items():
        if snapshot["review_refs"].get(k) != sha:
            raise OriginHold(f"{k}: independent QA/editorial/home ref not pinned")
    if set(snapshot["review_refs"]) != set(REVIEW_REFS):
        raise OriginHold("unreviewed related PRs in snapshot")
    cand = snapshot["candidate"]
    _entry(cand, "candidate", CANDIDATE_BRANCH, CANDIDATE_SHA, complete=True)
    origins = snapshot["origins"]
    if not isinstance(origins, dict) or set(origins) != set(ORIGINS):
        raise OriginHold("all seven original contributors and two descendants required")
    for ident, (name, sha) in ORIGINS.items():
        _entry(origins[ident], ident, name, sha)
        extra = set(origins[ident]["articles"]) - set(cand["articles"])
        if extra:
            raise OriginHold(f"{ident}: contributor article lost from candidate: {sorted(extra)}")
        # Missing source fragments must be explicitly held, never silently discarded.
        for path in origins[ident]["sources"]:
            if path not in cand["sources"]:
                raise OriginHold(f"{ident}: original source fragment missing: {path}")
    coverage = set().union(*(set(o["articles"]) for o in origins.values()))
    if coverage != set(cand["articles"]):
        raise OriginHold(f"candidate slate lacks original source-witness ancestry: {sorted(set(cand['articles'])-coverage)}")
    rows = []
    for slug, pair in sorted(cand["articles"].items()):
        ancestry = {ident: obj["articles"][slug] for ident, obj in origins.items() if slug in obj["articles"]}
        body = {ident: p["body"] for ident, p in ancestry.items()}
        meta = {ident: p["meta"] for ident, p in ancestry.items()}
        rows.append({"slug": slug, "origins": sorted(ancestry), "body_variants": len(set(body.values())),
                     "meta_variants": len(set(meta.values())),
                     "candidate_body_matches": sorted(k for k, v in body.items() if v == pair["body"]),
                     "candidate_meta_matches": sorted(k for k, v in meta.items() if v == pair["meta"]),
                     "review_required": len(set(body.values())) > 1 or len(set(meta.values())) > 1
                                        or pair["body"] not in body.values() or pair["meta"] not in meta.values()})
    source_rows = []
    for path, sha in sorted(cand["sources"].items()):
        witnesses = {i: v["sources"][path] for i, v in origins.items() if path in v["sources"]}
        source_rows.append({"path": path, "origin_variants": len(set(witnesses.values())),
                            "candidate_matches": sorted(i for i, b in witnesses.items() if b == sha),
                            "unwitnessed_candidate": bool(witnesses) and sha not in witnesses.values(),
                            "new_composite_file": not bool(witnesses)})
    return {"release_state": STATE, "qualified_qd_pass": False, "source_claim_support_verified": False,
            "wordpress_publication_performed": False, "state": "REVIEW_REQUIRED_HARD_HOLD",
            "article_count": len(rows), "original_ref_count": len(origins),
            "body_variant_slugs": [r["slug"] for r in rows if r["body_variants"] > 1],
            "candidate_body_unmatched_slugs": [r["slug"] for r in rows if not r["candidate_body_matches"]],
            "candidate_meta_unmatched_slugs": [r["slug"] for r in rows if not r["candidate_meta_matches"]],
            "review_required_slugs": [r["slug"] for r in rows if r["review_required"]],
            "source_review_paths": [r["path"] for r in source_rows if r["unwitnessed_candidate"] or r["origin_variants"] > 1],
            "article_rows": rows, "source_rows": source_rows}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshot", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        path = args.snapshot
        if not path.is_file() or path.is_symlink() or path.stat().st_size > 2_000_000:
            raise OriginHold("snapshot missing/linked/oversized")
        snapshot = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicates)
        print(json.dumps(analyze(snapshot), indent=2, sort_keys=True))
    except (OSError, ValueError, UnicodeError, TypeError, KeyError) as e:
        print(json.dumps({"release_state": STATE, "state": "PROVENANCE_HARD_HOLD", "qualified_qd_pass": False, "error": str(e)}))
    return 2  # Never a source/safety/release PASS.

def _no_duplicates(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise OriginHold(f"duplicate JSON property {k!r}")
        d[k] = v
    return d

if __name__ == "__main__":
    raise SystemExit(main())
