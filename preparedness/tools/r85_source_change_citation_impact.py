#!/usr/bin/env python3
"""R85 PRIVATE HOLD: changed-source-to-retained-citation impact custody.

Read-only review aid across R82/R83/R84 four-stage sealed evidence.
No source links checked; a matching citation is NOT an approval of its claim.
No edits to article bodies, sources, URL identities, CMS, or publication state.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path

SCHEMA = "r85-four-stage-source-change-to-citation-impact-hold-v1"
STAGES = ("frozen", "integrated", "current", "rc")
REVIEW = "NOT_REVIEWED"


class Hold(ValueError):
    """The evidence chain is incomplete, inconsistent, or falsely approved."""


def need(condition, detail):
    if not condition:
        raise Hold(detail)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def parent():
    path = Path(__file__).with_name("r84_source_url_citation_edge_custody.py")
    need(path.is_file() and not path.is_symlink(), "R84 parent missing")
    spec = importlib.util.spec_from_file_location("r85_r84_parent", path)
    need(spec is not None and spec.loader is not None, "R84 import unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def edge_index(edges):
    """Every original occurrence retains its own exact key and source edges."""
    need(type(edges) is list, "missing exact citation occurrence crosswalk")
    index = {}
    for row in edges:
        need(type(row) is dict and row.get("stage") in STAGES
             and type(row.get("article_origin")) is str
             and type(row.get("article_path")) is str
             and type(row.get("citation_ordinal")) is int
             and row["citation_ordinal"] >= 0
             and type(row.get("literal_raw_source_ID")) is str
             and row["literal_raw_source_ID"]
             and row.get("may_publish") is False
             and row.get("human_claim_support") == REVIEW
             and row.get("qualified_safety_review") == REVIEW
             and type(row.get("exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED")) is list,
             "unverified or malformed citation edge")
        key = (row["stage"], row["article_origin"], row["article_path"],
               row["citation_ordinal"])
        need(key not in index, "duplicate citation occurrence discarded")
        index[key] = row
    return index


def source_histories(rows, edges):
    """Do not alias source IDs or URLs across origins, stages, or revisions."""
    need(type(rows) is list and type(edges) is list, "missing original source custody")
    grouped, source_keys, use = defaultdict(dict), set(), defaultdict(list)
    for row in rows:
        need(type(row) is dict and row.get("stage") in STAGES
             and type(row.get("origin")) is str
             and type(row.get("literal_source_ID")) is str
             and type(row.get("reading_sha256")) is str
             and row.get("may_publish") is False
             and row.get("human_source_review") == REVIEW
             and row.get("qualified_safety_review") == REVIEW
             and type(row.get("complete_original_reading_UNABRIDGED_NOT_APPROVED")) is dict,
             "source snapshot missing, truncated, or falsely approved")
        source = row["complete_original_reading_UNABRIDGED_NOT_APPROVED"]
        need(source.get("id") == row["literal_source_ID"]
             and digest(source) == row["reading_sha256"]
             and row["url_observation"]["literal_URL_UNVERIFIED_UNCHANGED"] == source.get("url"),
             "source reading or original literal URL substituted")
        key = (row["stage"], row["origin"], row["literal_source_ID"])
        need(key not in source_keys, "two same-origin same-ID source records in one stage")
        source_keys.add(key)
        grouped[(row["origin"], row["literal_source_ID"])][row["stage"]] = row
    for edge in edges:
        ek = (edge["stage"], edge["article_origin"], edge["article_path"],
              edge["citation_ordinal"], edge["literal_raw_source_ID"])
        for src in edge["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"]:
            need(type(src) is dict and src.get("literal_source_ID") ==
                 edge["literal_raw_source_ID"], "source candidate ID changed")
            k = (edge["stage"], src["origin"], src["literal_source_ID"])
            need(k in source_keys
                 and grouped[(src["origin"], src["literal_source_ID"])][
                     edge["stage"]]["reading_sha256"] == src["reading_sha256"]
                 and grouped[(src["origin"], src["literal_source_ID"])][
                     edge["stage"]]["url_observation"][
                     "literal_URL_UNVERIFIED_UNCHANGED"] ==
                     src["literal_URL_UNVERIFIED_UNCHANGED"],
                 "candidate citation points to another source reading")
            hit = {"article_origin": edge["article_origin"],
                   "article_path": edge["article_path"],
                   "citation_ordinal": edge["citation_ordinal"],
                   "literal_source_ID": edge["literal_raw_source_ID"],
                   "R83_anchor_sha256": edge["R83_complete_anchor_sha256"],
                   "human_claim_support": REVIEW, "may_publish": False}
            need(hit not in use[k], "same occurrence/source edge duplicated")
            use[k].append(hit)
    histories = []
    for (origin, sid), versions in sorted(grouped.items()):
        snapshots = {stage: versions.get(stage) for stage in STAGES}
        old, new = snapshots["current"], snapshots["rc"]
        cues = []
        if (old is None) != (new is None):
            cues.append("SOURCE_ADDED_OR_REMOVED_CURRENT_TO_RC_REVIEW")
        elif old is not None:
            if old["reading_sha256"] != new["reading_sha256"]:
                cues.append("COMPLETE_SOURCE_READING_CHANGED_REVIEW")
            if old["url_observation"]["literal_URL_UNVERIFIED_UNCHANGED"] != \
                    new["url_observation"]["literal_URL_UNVERIFIED_UNCHANGED"]:
                cues.append("EXACT_LITERAL_URL_CHANGED_REVIEW")
        usage = {stage: sorted(use[(stage, origin, sid)],
                 key=lambda r: (r["article_origin"], r["article_path"],
                                r["citation_ordinal"])) for stage in STAGES}
        histories.append({
            "origin": origin, "literal_source_ID": sid,
            "four_complete_original_source_snapshots_UNABRIDGED_NOT_APPROVED": snapshots,
            "all_exact_citation_impacts_BY_STAGE_NOT_APPROVED": usage,
            "current_TO_rc_review_cues_NOT_VERDICTS": cues,
            "human_source_identity_review": REVIEW, "human_claim_support": REVIEW,
            "qualified_safety_review": REVIEW, "may_publish": False})
    need(sum(sum(len(h["all_exact_citation_impacts_BY_STAGE_NOT_APPROVED"][s])
                     for s in STAGES) for h in histories) ==
         sum(len(e["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"]) for e in edges),
         "source impact docket silently lost a citation/source edge")
    return histories


def linked_edge(anchor, stage, origin, path, index):
    """Assert byte-level anchor custody, not just a matching citation ID."""
    if anchor is None:
        return None
    need(type(anchor) is dict and type(anchor.get("ordinal")) is int,
         "missing original citation anchor")
    key = (stage, origin, path, anchor["ordinal"])
    need(key in index, "original citation occurrence was dropped")
    edge = index[key]
    need(edge["literal_raw_source_ID"] == anchor["raw_source_id"]
         and edge["R83_complete_anchor_sha256"] == digest(anchor),
         "R83 full citation context digest or literal ID altered")
    return edge


def candidate_fingerprint(edge):
    if edge is None:
        return None
    return sorted((src["origin"], src["literal_source_ID"],
                   src["reading_sha256"], src["literal_URL_UNVERIFIED_UNCHANGED"])
                  for src in edge["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"])


def citation_changes(packets, index):
    """Compare retained literal IDs by occurrence rank; never infer support."""
    need(type(packets) is list, "29 complete article packets missing")
    results, used = [], set()
    for packet in packets:
        origin, path = packet["origin"], packet["path"]
        for row in packet["current_TO_rc_occurrence_rank_review"]:
            before, after = row["before_FULL_ANCHOR"], row["after_FULL_ANCHOR"]
            old = linked_edge(before, "current", origin, path, index)
            new = linked_edge(after, "rc", origin, path, index)
            cues = list(row["review_cues_NOT_VERDICTS"])
            if (before is None) != (after is None):
                cues.append("CITATION_ADDED_OR_REMOVED_REVIEW")
            elif before is not None:
                a, b = candidate_fingerprint(old), candidate_fingerprint(new)
                if a != b:
                    cues.append("EXACT_SOURCE_READING_OR_LITERAL_URL_DRIFT_REVIEW")
                # URL-only observation is separate from the reading digest:
                # both are retained and neither is a source-truth verdict.
                if sorted((s[0], s[1], s[3]) for s in a) != \
                        sorted((s[0], s[1], s[3]) for s in b):
                    cues.append("LITERAL_SOURCE_URL_SCOPE_DRIFT_REVIEW")
                if before["container_text_digest"] != after["container_text_digest"]:
                    cues.append("RETAINED_CITATION_CHANGED_PASSAGE_REVIEW")
            if (old and old["review_cues_NOT_VERDICTS"]) or \
                    (new and new["review_cues_NOT_VERDICTS"]):
                cues.append("ORIGINAL_SOURCE_URL_OR_SCOPE_CUE_REVIEW")
            key = (origin, path, row["raw_source_id"],
                   row["within_ID_occurrence"])
            need(key not in used, "repeated occurrence-rank review row")
            used.add(key)
            results.append({
                "origin": origin, "path": path,
                "literal_raw_source_ID": row["raw_source_id"],
                "within_ID_occurrence": row["within_ID_occurrence"],
                "R83_complete_unabridged_current_to_RC_review": row,
                "exact_current_source_edges_NOT_APPROVED": old,
                "exact_RC_source_edges_NOT_APPROVED": new,
                "review_cues_NOT_VERDICTS": sorted(set(cues)),
                "human_claim_review": REVIEW, "qualified_safety_review": REVIEW,
                "may_publish": False})
    return results


def construct(r82_report, r83_report, r84_report):
    r84 = parent()
    r84.verify(r84_report, r82_report, r83_report)
    need(r84_report.get("release_state") == "HOLD"
         and r84_report.get("may_publish") is False
         and r84_report.get("medical_safety_approved") is False,
         "R84 parent no longer release HOLD")
    edges = r84_report["all_four_stage_literal_citation_to_source_edges_NOT_APPROVED"]
    index = edge_index(edges)
    histories = source_histories(
        r84_report["all_complete_four_stage_source_readings_UNABRIDGED"], edges)
    changes = citation_changes(
        r83_report["all_29_four_stage_citation_context_packets_UNABRIDGED"], index)
    need(len(changes) == r83_report["counts"]["current_rc_review_occurrence_rows"],
         "current/RC cited claim occurrence alignment lost")
    need(len(index) == r84_report["counts"]["complete_citation_source_crosswalk_rows"],
         "four-stage citation source-edge count drift")
    report = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "may_publish": False, "medical_safety_approved": False,
        "human_source_approvals": 0, "human_claim_approvals": 0,
        "qualified_safety_approvals": 0, "independent_QD_approvals": 0,
        "separate_RC_sha": r82_report["separate_RC_sha"],
        "R82_unabridged_source_sha256": r82_report["sha256_seal"],
        "R83_unabridged_anchor_sha256": r83_report["sha256_seal"],
        "R84_unabridged_source_edge_sha256": r84_report["sha256_seal"],
        "counts": {
            "four_stage_source_readings": sum(sum(
                h["four_complete_original_source_snapshots_UNABRIDGED_NOT_APPROVED"][s]
                is not None for s in STAGES) for h in histories),
            "origin_and_literal_ID_source_histories": len(histories),
            "four_stage_citation_occurrences": len(index),
            "exact_citation_to_source_variant_edges": sum(
                len(e["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"]) for e in edges),
            "current_TO_rc_citation_rank_rows": len(changes),
            "current_TO_rc_citation_review_rows_NOT_ERRORS": sum(
                bool(r["review_cues_NOT_VERDICTS"]) for r in changes),
            "current_TO_rc_source_changed_histories_NOT_ERRORS": sum(
                bool(h["current_TO_rc_review_cues_NOT_VERDICTS"]) for h in histories),
        },
        "all_complete_four_stage_source_histories_NOT_APPROVED": histories,
        "all_unabridged_current_TO_rc_citation_impact_reviews_NOT_APPROVED": changes,
    }
    report["sha256_seal"] = digest(report)
    return report


def verify(report, r82_report, r83_report, r84_report):
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("issue") == 136 and report.get("release_state") == "HOLD"
         and report.get("may_publish") is False
         and report.get("medical_safety_approved") is False
         and all(report.get(k) == 0 for k in (
             "human_source_approvals", "human_claim_approvals",
             "qualified_safety_approvals", "independent_QD_approvals")),
         "R85 forged review or release approval")
    need(report.get("sha256_seal") == digest({
        k: v for k, v in report.items() if k != "sha256_seal"}),
        "R85 private custody digest mismatch")
    need(report == construct(r82_report, r83_report, r84_report),
         "R85 cannot reconstruct exact changed-source/citation impact evidence")


def private_csv(report, r82_report, r83_report, r84_report):
    verify(report, r82_report, r83_report, r84_report)
    r82 = parent().parent_modules()[1]
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["origin", "article_path", "literal_source_ID",
                     "within_ID_occurrence", "review_cues_NOT_VERDICTS",
                     "human_claim_review", "release_state"])
    for row in report[
            "all_unabridged_current_TO_rc_citation_impact_reviews_NOT_APPROVED"]:
        if row["review_cues_NOT_VERDICTS"]:
            writer.writerow([r82.safe_csv(row["origin"]),
                             r82.safe_csv(row["path"]),
                             r82.safe_csv(row["literal_raw_source_ID"]),
                             row["within_ID_occurrence"],
                             ";".join(row["review_cues_NOT_VERDICTS"]),
                             REVIEW, "HOLD"])
    return out.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-stdout", action="store_true",
                        help="private temporary reviewer rows, never a website asset")
    args = parser.parse_args(argv)
    r84 = parent()
    r83, r82 = r84.parent_modules()
    p82 = r82.live_report()
    p83 = r83.construct(p82)
    p84 = r84.construct(p82, p83)
    report = construct(p82, p83, p84)
    verify(report, p82, p83, p84)
    if args.csv_stdout:
        print(private_csv(report, p82, p83, p84), end="")
    else:
        print(json.dumps({"schema": SCHEMA, "release_state": "HOLD",
                          "counts": report["counts"], "sha256_seal":
                          report["sha256_seal"], "human_review_approvals": 0,
                          "may_publish": False, "CMS_and_WordPress_writes": 0},
                         sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (Hold, ValueError, TypeError, KeyError, OSError) as exc:
        raise SystemExit("R85 FAILED CLOSED — " + str(exc))
