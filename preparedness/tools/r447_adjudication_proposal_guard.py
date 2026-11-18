#!/usr/bin/env python3
"""R447: fail-closed, read-only adjudication proposal and reviewer evidence custody.

Never selects a winning manuscript/source, certifies a reviewer, approves safety,
changes WordPress, or grants a release. All outputs are DRAFT_HARD_HOLD.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

PACKET_BLOB = "0e655316ced77212abeff77459898253a1e768fd"
ORIGINAL_BLOB = "86d22a1d504c93db7689b914e2202a7845b648e2"
STATE = "DRAFT_HARD_HOLD"
SCHEMA = "R447_REVIEW_PROPOSALS_ONLY_v1"
COUNTS = (35, 5, 9, 17, 9)
HOLD_FIELDS = ("qualified_review_approved", "publishable", "safety_approved", "merchant_offer_verified")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def safe_https(url):
    if not isinstance(url, str) or len(url) > 2048 or any(ord(c) < 33 for c in url):
        return False
    try:
        part = urlsplit(url)
    except ValueError:
        return False
    return part.scheme == "https" and bool(part.hostname) and not part.username and not part.password and not part.fragment


def reviewer_data_valid(item, notes):
    reviewer = item.get("reviewer")
    evidence = item.get("evidence_urls")
    return (isinstance(reviewer, str) and 3 <= len(reviewer.strip()) <= 120
            and isinstance(evidence, list) and 1 <= len(evidence) <= 12
            and len(evidence) == len(set(map(str, evidence)))
            and all(safe_https(url) for url in evidence)
            and all(isinstance(item.get(key), str) and len(item[key].strip()) >= 24 for key in notes))


def template(packet):
    """Exact 5/9/17 review slots. Existing source and fork data never edited."""
    return {"schema": SCHEMA, "packet_git_blob": PACKET_BLOB,
            "release_state": STATE, "qualified_review_approved": False,
            "publishable": False, "safety_approved": False,
            "merchant_offer_verified": False,
            "sources": [{"source_id": x["source_id"], "candidate_digest": None,
                         "reviewer": None, "evidence_urls": [],
                         "reading_scope_confirmation": None, "safety_review_note": None}
                        for x in packet["source_scope_review"]],
            "forks": [{"path": x["path"], "candidate_digest": None,
                       "reviewer": None, "evidence_urls": [],
                       "reading_depth_confirmation": None, "citations_confirmation": None}
                      for x in packet["manuscript_fork_review"]],
            "url_groups": [{"url": x["url"], "decision": "UNSELECTED",
                            "reviewer": None, "evidence_urls": [], "notes": None}
                           for x in packet["duplicate_exact_url_review"]]}


def assess(packet, proposals, packet_raw=None, current_heads=None):
    """Inspect without selecting. 'Clean' indicates only structural evidence integrity."""
    errors, proposals_seen = [], {"sources": 0, "forks": 0, "url_groups": 0}
    if not isinstance(packet, dict) or not isinstance(proposals, dict):
        return {"errors": ["INPUT_NOT_OBJECT"], "release_state": STATE,
                "qd_pass": False, "publishable": False, "verified_paid_offer": False}
    if not isinstance(packet_raw, bytes) or git_blob(packet_raw) != PACKET_BLOB:
        errors.append("AUTHENTIC_PACKET_BLOB_NOT_PROVEN")
    if packet.get("schema") != "R446_ORIGINAL_ADJUDICATION_REVIEW_ONLY_v1" or packet.get("release_state") != STATE:
        errors.append("ORIGINAL_PACKET_IDENTITY_DRIFT")
    if packet.get("original_docket", {}).get("git_blob") != ORIGINAL_BLOB:
        errors.append("R397_ORIGINAL_DOCKET_PIN_DRIFT")
    if packet.get("issue") != 136 or packet.get("business_coordination_issue") != 820:
        errors.append("OWNERSHIP_IDENTITY_DRIFT")
    if any(packet.get(k) is not False for k in HOLD_FIELDS):
        errors.append("PACKET_FALSE_RELEASE_AUTHORITY")
    if proposals.get("schema") != SCHEMA or proposals.get("packet_git_blob") != PACKET_BLOB:
        errors.append("PROPOSAL_SCHEMA_OR_PARENT_PIN_DRIFT")
    if proposals.get("release_state") != STATE or any(proposals.get(k) is not False for k in HOLD_FIELDS):
        errors.append("PROPOSAL_FALSE_RELEASE_AUTHORITY")
    articles = packet.get("article_identities", [])
    source = packet.get("source_scope_review", [])
    forks = packet.get("manuscript_fork_review", [])
    groups = packet.get("duplicate_exact_url_review", [])
    pins = packet.get("branch_pins", [])
    all_rows = (articles, source, forks, groups, pins)
    if any(not isinstance(x, list) for x in all_rows) or tuple(len(x) for x in all_rows) != COUNTS:
        errors.append("ORIGINAL_REVIEW_COUNTS_DRIFT")
        articles, source, forks, groups, pins = (x if isinstance(x, list) else [] for x in all_rows)
    slugs = [a.get("slug") for a in articles if isinstance(a, dict)]
    if len(set(map(str, slugs))) != 35 or not all(isinstance(x, str) and x for x in slugs):
        errors.append("ARTICLE_IDENTITY_LOSS_OR_COLLISION")
    heads = {x.get("branch"): x.get("sha") for x in pins if isinstance(x, dict)}
    if len(heads) != 9 or heads != current_heads:
        errors.append("CURRENT_NINE_HEADS_NOT_PROVEN")
    for name, original_rows, draft_rows, ident, original_candidates, draft_value in (
        ("sources", source, proposals.get("sources"), "source_id", "source_variants", "candidate_digest"),
        ("forks", forks, proposals.get("forks"), "path", "original_variants", "candidate_digest"),
        ("url_groups", groups, proposals.get("url_groups"), "url", None, "decision"),
    ):
        if not isinstance(draft_rows, list) or len(draft_rows) != len(original_rows):
            errors.append("REVIEW_ROW_COUNT_DRIFT:" + name)
            continue
        old_index = {x.get(ident): x for x in original_rows if isinstance(x, dict)}
        new_index = {x.get(ident): x for x in draft_rows if isinstance(x, dict)}
        if (len(old_index) != len(original_rows) or len(new_index) != len(draft_rows)
                or set(new_index) != set(old_index)):
            errors.append("REVIEW_IDENTITY_REPLACED:" + name)
            continue
        if name == "url_groups":
            expected_keys = {"url", "decision", "reviewer", "evidence_urls", "notes"}
        elif name == "sources":
            expected_keys = {"source_id", "candidate_digest", "reviewer", "evidence_urls",
                             "reading_scope_confirmation", "safety_review_note"}
        else:
            expected_keys = {"path", "candidate_digest", "reviewer", "evidence_urls",
                             "reading_depth_confirmation", "citations_confirmation"}
        for item_id, row in new_index.items():
            if not isinstance(row, dict) or set(row) != expected_keys:
                errors.append("REVIEW_SCHEMA_DRIFT:" + name); continue
            ancestor = old_index[item_id]
            if name in ("sources", "forks") and (ancestor.get("original_decision") != "HUMAN_REVIEW_REQUIRED"
                    or ancestor.get("proposed_selection") is not None
                    or ancestor.get("reviewer") is not None
                    or ancestor.get("review_evidence") is not None
                    or ancestor.get("qualified_safety_approved") is not False):
                errors.append("ORIGINAL_CASE_ALREADY_SELECTED_OR_APPROVED")
            if name == "url_groups":
                if row[draft_value] == "UNSELECTED":
                    if row["reviewer"] is not None or row["evidence_urls"] != [] or row["notes"] is not None:
                        errors.append("UNSELECTED_GROUP_HAS_REVIEW_AUTHORITY")
                elif row[draft_value] == "KEEP_DISTINCT_PROPOSED":
                    proposals_seen[name] += 1
                    if not reviewer_data_valid(row, ("notes",)):
                        errors.append("UNSUPPORTED_URL_GROUP_PROPOSAL")
                else:
                    errors.append("UNAPPROVED_URL_ID_MERGE_OR_DECISION")
                if ancestor.get("decision") != "UNSELECTED" or ancestor.get("merge_authorized") is not False:
                    errors.append("ORIGINAL_URL_GROUP_PRESELECTED")
                continue
            candidate = row[draft_value]
            allowed = {digest(x) for x in ancestor.get(original_candidates, []) if isinstance(x, dict)}
            if candidate is None:
                if row["reviewer"] is not None or row["evidence_urls"] != [] or any(
                        row[k] is not None for k in expected_keys - {ident, draft_value, "reviewer", "evidence_urls"}):
                    errors.append("UNSELECTED_RECORD_HAS_REVIEW_AUTHORITY")
                continue
            proposals_seen[name] += 1
            if not isinstance(candidate, str) or candidate not in allowed:
                errors.append("PROPOSED_VARIANT_NOT_IN_AUTHENTIC_ORIGINAL:" + name)
            checks = (("reading_scope_confirmation", "safety_review_note") if name == "sources"
                      else ("reading_depth_confirmation", "citations_confirmation"))
            if not reviewer_data_valid(row, checks):
                errors.append("PROPOSAL_LACKS_REVIEW_EVIDENCE:" + name)
    return {"release_state": STATE, "qd_pass": False, "publishable": False,
            "verified_paid_offer": False, "structural_evidence_pass": not errors,
            "errors": sorted(set(errors)), "proposals_documented_not_approved": proposals_seen,
            "unselected": {"sources": max(0, len(source)-proposals_seen["sources"]),
                           "forks": max(0, len(forks)-proposals_seen["forks"]),
                           "shared_url_groups": max(0, len(groups)-proposals_seen["url_groups"])},
            "source_variant_candidates_by_id": {x["source_id"]: [digest(v) for v in x["source_variants"]]
                                                for x in source if isinstance(x, dict)},
            "fork_variant_candidates_by_path": {x["path"]: [digest(v) for v in x["original_variants"]]
                                                for x in forks if isinstance(x, dict)}}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only original source/fork proposal custody; ALWAYS HOLD")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--proposals", type=Path)
    parser.add_argument("--observed-heads", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        packet_raw = args.packet.read_bytes()
        packet = json.loads(packet_raw, object_pairs_hook=unique_object)
        draft = (json.loads(args.proposals.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
                 if args.proposals else template(packet))
        heads = json.loads(args.observed_heads.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        result = assess(packet, draft, packet_raw, heads)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError):
        result = {"release_state": STATE, "errors": ["MISSING_OR_INVALID_EXTERNAL_EVIDENCE"],
                  "qd_pass": False, "publishable": False, "structural_evidence_pass": False}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
