#!/usr/bin/env python3
"""Read-only, fail-closed review intake for original FV Preparedness evidence.

Consumes the immutable R397 docket. An integrity pass is NEVER a QD, safety,
publication, commerce, or manuscript-selection approval. No files are modified.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = 1
SOURCE_IDS = frozenset({
    "fsis-power-failure", "loc-pioneer-diaries", "loc-prairie-traveler",
    "nchfp-home", "nchfp-jerky",
})
FORK_BRANCHES = frozenset({
    "claude/prep-shelter-5e1e0e", "claude/prep-shelter-continuation",
    "claude/prep-shelter-followup-evidence",
})
COUNTS = {
    "original_article_count": 35, "original_object_paths": 77,
    "original_source_fragments": 7, "source_record_occurrences": 280,
    "original_distinct_source_ids": 203, "base_source_records": 34,
    "source_evidence_disputes": 5, "unselected_original_forks": 9,
}
PINNED_BLOBS = {
    "manifest": "5e7d9a8972872c82b4bc46ac13aab18883d8149a",
    "source_fragment_crosswalk": "24b49f0a423119c2f612455f021669709a3f22b5",
    "base_source_register": "b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77",
}
R397_DOCKET_BLOB = "86d22a1d504c93db7689b914e2202a7845b648e2"
REQUIRED_BACKLOG = frozenset({
    "ARTICLE_7_WATER", "ARTICLE_11_FOOD", "TOOL_104_CHILD_PRIVACY",
    "EMERGENCY_AND_MEDICAL_QD", "AUTHENTIC_FULL_NATIVE_BUILD_AND_PRIVATE_EXPORTS",
})
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def _valid_sha(v: Any) -> bool:
    return isinstance(v, str) and bool(HEX40.fullmatch(v))


def _list(v: Any) -> list:
    return v if isinstance(v, list) else []


def _dict(v: Any) -> dict:
    return v if isinstance(v, dict) else {}


def audit(d: Any) -> dict:
    """Check docket structural and cross-field fidelity without choosing variants."""
    errors: list[str] = []
    def check(ok: Any, marker: str) -> None:
        if not ok:
            errors.append(marker)
    if not isinstance(d, dict):
        return {"integrity": "FAIL", "release": "HARD_HOLD", "errors": ["not_object"], "cases": []}
    check(d.get("schema") == SCHEMA, "schema")
    check(d.get("repo") == "finalvestigestudios/final-vestige-site-layer", "repo")
    check(d.get("issue") == 136 and d.get("parent_conversion_issue") == 820, "issue_scope")
    check(d.get("provenance") == "ORIGINAL_UNSELECTED_GIT_SOURCE_INVENTORY", "provenance")
    check(d.get("original_git_blob_pins") == PINNED_BLOBS, "original_git_pins")
    check(d.get("expected") == COUNTS and d.get("observed") == COUNTS, "inventory_counts")
    check(d.get("release_state") == "DRAFT_HARD_HOLD", "release_state")
    for key in ("publication_approved", "qualified_safety_approved", "merchant_offer_verified", "automatic_variant_selection"):
        check(d.get(key) is False, "not_false:" + key)
    check(set(_list(d.get("qualified_review_backlog"))) == REQUIRED_BACKLOG, "review_backlog")

    pins = _list(d.get("branch_pins"))
    branch_map: dict[str, str] = {}
    for i, p0 in enumerate(pins):
        p = _dict(p0)
        b, h = p.get("branch"), p.get("sha")
        check(isinstance(b, str) and b.startswith("claude/prep-") and _valid_sha(h), f"branch_pin:{i}")
        if isinstance(b, str):
            check(b not in branch_map, f"duplicate_branch:{b}")
            branch_map[b] = h
    check(len(pins) == 9 and len(branch_map) == 9, "branch_count")
    check(FORK_BRANCHES.issubset(branch_map), "missing_shelter_branch")

    cross = _list(d.get("all_original_source_id_crosswalk"))
    source_map: dict[str, set[tuple[str, str, str]]] = {}
    occurrences = 0
    for i, x0 in enumerate(cross):
        x = _dict(x0)
        sid = x.get("source_id")
        check(isinstance(sid, str) and bool(SLUG.fullmatch(sid)), f"source_id:{i}")
        if not isinstance(sid, str):
            continue
        check(sid not in source_map, f"duplicate_source_id:{sid}")
        variants = _list(x.get("variants"))
        check(bool(variants), f"missing_source_variants:{sid}")
        source_map[sid] = set()
        for j, v0 in enumerate(variants):
            v = _dict(v0)
            b, h, url = v.get("branch"), v.get("source_blob"), v.get("url")
            check(b in branch_map and _valid_sha(h) and isinstance(url, str) and url.startswith("https://"), f"source_variant:{sid}:{j}")
            if isinstance(b, str) and isinstance(h, str) and isinstance(url, str):
                marker = (b, h, url)
                check(marker not in source_map[sid], f"duplicate_occurrence:{sid}:{j}")
                source_map[sid].add(marker)
            occurrences += 1
    check(len(cross) == 203 and len(source_map) == 203, "distinct_source_count")
    check(occurrences == 280, "source_occurrence_count")

    disputes = _list(d.get("source_evidence_disputes"))
    dispute_ids: set[str] = set()
    for i, e0 in enumerate(disputes):
        e = _dict(e0)
        sid = e.get("source_id")
        check(sid in SOURCE_IDS and sid not in dispute_ids, f"source_dispute_id:{i}")
        if isinstance(sid, str):
            dispute_ids.add(sid)
        check(e.get("decision") == "HUMAN_REVIEW_REQUIRED" and e.get("selected_record") is None, f"source_decision:{sid}")
        vs = _list(e.get("variants"))
        check(len(vs) >= 2, f"source_competing_variants:{sid}")
        seen: set[str] = set()
        for j, v0 in enumerate(vs):
            v = _dict(v0)
            b, h, u = v.get("branch"), v.get("source_blob"), v.get("url")
            check(b in branch_map and b not in seen, f"source_branch:{sid}:{j}")
            if isinstance(b, str):
                seen.add(b)
            check(_valid_sha(h) and isinstance(u, str) and u.startswith("https://"), f"source_provenance:{sid}:{j}")
            check(all(isinstance(v.get(k), str) and v[k].strip() for k in ("supports_exact", "reading_scope_notes_exact", "publisher", "fragment", "verified_on")), f"missing_reading_scope:{sid}:{j}")
            check(isinstance(v.get("human_link_check"), bool), f"human_link_check_type:{sid}:{j}")
            check((b, h, u) in source_map.get(sid, set()), f"source_crosswalk_join:{sid}:{j}")
    check(dispute_ids == SOURCE_IDS, "source_dispute_set")

    articles = _list(d.get("original_articles"))
    article_slugs: set[str] = set()
    for i, a0 in enumerate(articles):
        a = _dict(a0)
        slug = a.get("slug")
        check(isinstance(slug, str) and bool(SLUG.fullmatch(slug)) and slug not in article_slugs, f"article_slug:{i}")
        if isinstance(slug, str):
            article_slugs.add(slug)
        blobs = _list(a.get("body_candidate_git_blobs"))
        check(bool(blobs) and all(_valid_sha(h) for h in blobs), f"article_body_blobs:{slug}")
    check(len(articles) == 35 and len(article_slugs) == 35, "article_count")

    forks = _list(d.get("original_fork_disputes"))
    paths: set[str] = set()
    for i, f0 in enumerate(forks):
        f = _dict(f0)
        p = f.get("path")
        check(isinstance(p, str) and p.startswith("preparedness/") and ".." not in p.split("/") and p not in paths, f"fork_path:{i}")
        if isinstance(p, str):
            paths.add(p)
        check(f.get("decision") == "HUMAN_REVIEW_REQUIRED" and f.get("selected_sha") is None, f"fork_selection:{p}")
        check(f.get("requires_reading_depth_review") is True and f.get("requires_source_citation_review") is True, f"fork_review_scope:{p}")
        v = _list(f.get("variants"))
        seen_branches = set()
        for j, x0 in enumerate(v):
            x = _dict(x0)
            b, h = x.get("branch"), x.get("git_blob_sha")
            if isinstance(b, str):
                seen_branches.add(b)
            check(b in FORK_BRANCHES and _valid_sha(h) and type(x.get("byte_length")) is int and x["byte_length"] > 0, f"fork_variant:{p}:{j}")
            if isinstance(p, str) and p.endswith(".body.html"):
                slug = p.rsplit("/", 1)[-1].removesuffix(".body.html")
                a = next((z for z in articles if _dict(z).get("slug") == slug), None)
                check(h in _list(_dict(a).get("body_candidate_git_blobs")), f"fork_article_join:{p}:{j}")
        check(len(v) == 3 and seen_branches == FORK_BRANCHES, f"fork_branch_set:{p}")
    check(len(forks) == 9 and len(paths) == 9, "fork_count")
    check(sum(str(p).endswith(".body.html") for p in paths) == 4 and sum(str(p).endswith(".meta.json") for p in paths) == 4 and "preparedness/sources/fragments/shelter.json" in paths, "fork_file_structure")

    aliases = _list(d.get("shared_exact_url_review_groups"))
    seen_urls = set()
    for i, g0 in enumerate(aliases):
        g = _dict(g0)
        url, ids = g.get("url"), _list(g.get("ids"))
        check(isinstance(url, str) and url.startswith("https://") and url not in seen_urls, f"alias_url:{i}")
        if isinstance(url, str):
            seen_urls.add(url)
        check(g.get("review_required") is True and len(ids) >= 2 and len(ids) == len(set(ids)), f"alias_review:{i}")
        for sid in ids:
            check(sid in source_map and any(v[2] == url for v in source_map.get(sid, set())), f"alias_crosswalk:{i}:{sid}")
    check(len(aliases) == 17 and len(seen_urls) == 17, "alias_count")

    cases = ([{"kind": "source", "id": x.get("source_id"), "decision": "HUMAN_REVIEW_REQUIRED"} for x in disputes if isinstance(x, dict)]
             + [{"kind": "fork", "id": x.get("path"), "decision": "HUMAN_REVIEW_REQUIRED"} for x in forks if isinstance(x, dict)])
    return {"integrity": "PASS" if not errors else "FAIL", "release": "HARD_HOLD", "errors": sorted(set(errors)), "cases": cases,
            "counts": {"articles": len(articles), "source_ids": len(source_map), "source_occurrences": occurrences,
                       "source_disputes": len(disputes), "fork_disputes": len(forks), "alias_groups": len(aliases)}}


def check_proposals(d: dict, proposals: Any) -> list[str]:
    """Advisory annotations only; a proposal is never a selected/approved record."""
    errors: list[str] = []
    if not isinstance(proposals, dict) or proposals.get("schema") != 1:
        return ["proposal_schema"]
    if proposals.get("review_only") is not True or proposals.get("release_approval") is not False:
        errors.append("proposal_must_remain_hold")
    cases = _list(proposals.get("cases"))
    by_source = {x["source_id"]: x for x in _list(d.get("source_evidence_disputes")) if isinstance(x, dict) and "source_id" in x}
    by_fork = {x["path"]: x for x in _list(d.get("original_fork_disputes")) if isinstance(x, dict) and "path" in x}
    seen = set()
    for i, c0 in enumerate(cases):
        c = _dict(c0)
        kind, id_ = c.get("kind"), c.get("id")
        marker = (kind, id_)
        if marker in seen:
            errors.append(f"duplicate_proposal:{i}")
        seen.add(marker)
        original = (by_source if kind == "source" else by_fork if kind == "fork" else {}).get(id_)
        if not original:
            errors.append(f"unknown_proposal:{i}")
            continue
        if c.get("status") not in ("NEEDS_READING", "RETAIN_CONFLICT", "PROPOSED_FOR_QD_ONLY"):
            errors.append(f"invalid_status:{i}")
        if c.get("status") == "PROPOSED_FOR_QD_ONLY":
            allowed = ({v.get("source_blob") for v in original["variants"]} if kind == "source"
                       else {v.get("git_blob_sha") for v in original["variants"]})
            if c.get("proposed_git_blob") not in allowed:
                errors.append(f"unanchored_proposed_blob:{i}")
            if not isinstance(c.get("reviewer_evidence_url"), str) or not c["reviewer_evidence_url"].startswith("https://"):
                errors.append(f"missing_review_evidence:{i}")
            if not isinstance(c.get("scope_note"), str) or len(c["scope_note"].strip()) < 20:
                errors.append(f"missing_scope_note:{i}")
        for forbidden in ("approved", "selected", "merchant_verified", "qd_pass", "publication_allowed"):
            if c.get(forbidden) is True:
                errors.append(f"prohibited_approval:{i}:{forbidden}")
    return sorted(set(errors))


def proposal_template(d: dict) -> dict:
    return {"schema": 1, "review_only": True, "release_approval": False,
            "source_docket_blob_sha": R397_DOCKET_BLOB,
            "cases": ([{"kind": "source", "id": x["source_id"], "status": "NEEDS_READING",
                        "candidate_blobs": [v["source_blob"] for v in x["variants"]]}
                       for x in d["source_evidence_disputes"]]
                      + [{"kind": "fork", "id": x["path"], "status": "NEEDS_READING",
                          "candidate_blobs": [v["git_blob_sha"] for v in x["variants"]]}
                         for x in d["original_fork_disputes"]])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docket", required=True, type=Path)
    parser.add_argument("--proposals", type=Path)
    parser.add_argument("--emit-template", action="store_true")
    args = parser.parse_args(argv)
    try:
        raw = args.docket.read_bytes()
        sha = git_blob_sha(raw)
        if sha != R397_DOCKET_BLOB:
            print(json.dumps({"integrity": "FAIL", "release": "HARD_HOLD", "errors": ["r397_git_blob_mismatch"], "actual_blob": sha}, sort_keys=True))
            return 2
        d = json.loads(raw)
        result = audit(d)
        if args.proposals:
            p = json.loads(args.proposals.read_text(encoding="utf-8"))
            result["errors"] += check_proposals(d, p)
            if result["errors"]:
                result["integrity"] = "FAIL"
        if args.emit_template and not result["errors"]:
            result["proposal_template"] = proposal_template(d)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 2  # Always HARD HOLD until separate original-source and independent QD process.
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"integrity": "FAIL", "release": "HARD_HOLD", "errors": [f"input_error:{type(exc).__name__}"]}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
