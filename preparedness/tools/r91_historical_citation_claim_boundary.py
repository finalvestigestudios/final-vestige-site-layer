#!/usr/bin/env python3
"""R91 PRIVATE HOLD: citation placement relative to historical claim boundaries.

Deterministic *lexical* review cues, not source equivalence, claim verification,
medical advice, emergency safety clearance, human approval or a publication gate.
All R90/R89/R80 original evidence is retained without editing articles or URLs.
No network, CMS, WordPress, nav, release, filesystem or public side effects.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re

SCHEMA = "r91-historical-citation-claim-boundary-private-hold-v1"
REVIEW = "NOT_REVIEWED"
HOLD = "HOLD"
EXPECTED = (41, 35, 6, 2173, 2359, 4070, 242)
CITE = re.compile(r"\{\{cite:([^{}]+)\}\}")
BOUNDARY = re.compile(r"[.!?;]+(?:\s+|$)|\n+")
HEX = re.compile(r"[0-9a-f]{64}\Z")


class Gate(ValueError):
    """Original evidence, citation-to-claim cue, or release HOLD invalid."""


def need(ok, message):
    if not ok:
        raise Gate(message)


def digest(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def fingerprint(text):
    need(type(text) is str, "claim context must remain literal")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def upstream():
    path = Path(__file__).with_name("r90_historical_claim_scope_quantity_sequence.py")
    need(path.is_file() and not path.is_symlink(), "R90 parent missing")
    spec = importlib.util.spec_from_file_location("r91_r90_parent", path)
    need(spec is not None and spec.loader is not None, "R90 loader missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def clauses(text):
    """Split only for reviewer cues; original full text stays in R90 ancestor."""
    need(type(text) is str, "non-literal text")
    starts = [0]
    for match in BOUNDARY.finditer(text):
        if 0 < match.end() < len(text) and match.end() != starts[-1]:
            starts.append(match.end())
    pieces = []
    for i, start in enumerate(starts):
        end = starts[i+1] if i + 1 < len(starts) else len(text)
        # Blank pieces remain addressable, preserving honest source offsets.
        pieces.append((start, end, text[start:end]))
    return pieces


def positions(text):
    """Literal source IDs, token offsets and unabridged containing clauses.

    Repeated IDs retain independent occurrence ranks; same-rank alignment
    is explicitly NOT treated as proof of the same claim or citation identity.
    """
    need(type(text) is str, "non-literal historical source")
    chunks = clauses(text)
    found = []
    ranks = Counter()
    for token_rank, match in enumerate(CITE.finditer(text), 1):
        sid = match.group(1)
        need(bool(sid) and not sid.isspace(), "empty literal citation ID")
        ranks[sid] += 1
        candidates = [(j, a, b, segment) for j, (a, b, segment) in
                      enumerate(chunks, 1) if a <= match.start() < b]
        need(len(candidates) == 1, "citation offset not in unique claim clause")
        ordinal, start, end, segment = candidates[0]
        claim_text = CITE.sub("", segment)
        found.append({
            "literal_source_ID": sid,
            "token_rank_IN_CONTEXT_NOT_GLOBAL_IDENTITY": token_rank,
            "same_source_rank_IN_CONTEXT_NOT_CLAIM_IDENTITY": ranks[sid],
            "token_start_CODEPOINT_OFFSET": match.start(),
            "token_end_CODEPOINT_OFFSET": match.end(),
            "literal_citation_token": match.group(),
            "clause_ordinal_LEXICAL_ONLY": ordinal,
            "complete_original_clause_UNABRIDGED_NOT_REVIEWED": segment,
            "complete_original_clause_SHA256": fingerprint(segment),
            "complete_claim_clause_without_citation_NOT_REVIEWED": claim_text,
            "claim_clause_without_citation_SHA256": fingerprint(claim_text),
            "preceding_text_within_clause_UNABRIDGED": text[start:match.start()],
            "following_text_within_clause_UNABRIDGED": text[match.end():end],
            "claim_support_verified": False,
            "qualified_safety_review": REVIEW,
        })
    return found


def compare(before, after):
    """Create conservative lexical review cues; no semantic/safety verdict."""
    need(before is None or type(before) is str, "before claim non-literal")
    need(after is None or type(after) is str, "after claim non-literal")
    if before is None or after is None:
        b = None if before is None else positions(before)
        a = None if after is None else positions(after)
        flags = ["ONE_OR_BOTH_HISTORICAL_CONTEXTS_MISSING_REVIEW_ONLY"]
    else:
        b, a = positions(before), positions(after)
        x, y = [r["literal_source_ID"] for r in b], [r["literal_source_ID"] for r in a]
        flags = []
        if x != y:
            flags.append("CITATION_ID_ORDER_OR_OCCURRENCE_CHANGED_REVIEW_ONLY")
        if x == y:
            for left, right in zip(b, a):
                if left["clause_ordinal_LEXICAL_ONLY"] != right["clause_ordinal_LEXICAL_ONLY"]:
                    flags.append("SAME_CITATION_ORDER_MOVED_ACROSS_CLAUSE_BOUNDARY_REVIEW_ONLY")
                if left["claim_clause_without_citation_SHA256"] != right["claim_clause_without_citation_SHA256"]:
                    flags.append("SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY")
                if (left["clause_ordinal_LEXICAL_ONLY"] ==
                    right["clause_ordinal_LEXICAL_ONLY"] and
                    left["token_start_CODEPOINT_OFFSET"] != right["token_start_CODEPOINT_OFFSET"]):
                    flags.append("SAME_CITATION_ORDER_REPOSITIONED_IN_SAME_CLAUSE_REVIEW_ONLY")
            if any(x.count(k) > 1 for k in set(x)):
                flags.append("REPEATED_SOURCE_RANK_DOES_NOT_PROVE_SAME_CLAIM_REVIEW_ONLY")
        if before != after and not flags:
            flags.append("TEXT_CHANGED_NO_PROOF_OF_CITATION_SUPPORT_REVIEW_ONLY")
    return {
        "historical_before_full_text_SHA256_OR_NONE":
            None if before is None else fingerprint(before),
        "historical_after_full_text_SHA256_OR_NONE":
            None if after is None else fingerprint(after),
        "before_all_literal_citation_anchors_NOT_REVIEWED": b,
        "after_all_literal_citation_anchors_NOT_REVIEWED": a,
        "review_cues_NOT_SAFETY_FINDINGS": sorted(set(flags)),
        "rank_alignment_proves_claim_identity": False,
        "human_source_review": REVIEW,
        "human_claim_support": REVIEW,
        "qualified_safety_review": REVIEW,
        "independent_QD_review": REVIEW,
        "may_publish": False,
    }


def check_hold(parent):
    r90 = upstream()
    need(type(parent) is dict and parent.get("schema") == r90.SCHEMA
         and parent.get("issue") == 136 and parent.get("release_state") == HOLD
         and parent.get("may_publish") is False
         and parent.get("medical_safety_approved") is False,
         "R90 parent publication or medical safety HOLD altered")
    for k in ("human_source_approvals", "human_claim_approvals",
              "qualified_safety_approvals", "independent_QD_approvals"):
        need(type(parent.get(k)) is int and parent[k] == 0,
             "unreviewed claim/safety/QD falsely approved: " + k)
    need(parent.get("sha256_seal") == digest(
        {k: v for k, v in parent.items() if k != "sha256_seal"}),
         "R90 original evidence seal invalid")
    need(type(parent.get("all_original_citation_claim_scope_review_rows_NOT_APPROVED")) is list
         and type(parent.get("complete_R89_original_evidence_UNABRIDGED_NOT_APPROVED")) is dict
         and type(parent.get("counts")) is dict, "R90 full-slate evidence missing")
    return r90


def index(parent):
    """Overlay preserving complete R90 evidence and all unmatched history."""
    check_hold(parent)
    originals = parent["complete_R89_original_evidence_UNABRIDGED_NOT_APPROVED"]
    raw_rows = originals["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"]
    rows = parent["all_original_citation_claim_scope_review_rows_NOT_APPROVED"]
    need(type(raw_rows) is list and len(raw_rows) == len(rows),
         "R89-to-R90 citation population changed")
    lookup = {}
    for source in raw_rows:
        key = (source["kind"], source["slug"], source["citation_ordinal"])
        need(key not in lookup and type(key[2]) is int and key[2] > 0,
             "duplicate original historical citation identity")
        lookup[key] = source
    output, seen, counters = [], set(), Counter()
    for row in rows:
        need(type(row) is dict
             and all(row.get(k) == REVIEW for k in (
                 "human_source_review", "human_claim_support",
                 "qualified_safety_review", "independent_QD_review"))
             and row.get("may_publish") is False,
             "citation safety/claim state is no longer HOLD")
        key = (row["kind"], row["slug"], row["citation_ordinal"])
        need(key not in seen and key in lookup, "orphan/duplicate original citation")
        seen.add(key)
        source = lookup[key]
        need(source["literal_source_ID"] == row["literal_source_ID"]
             and source["original_DOM_block_ID"] == row["original_DOM_block_ID"]
             and source["original_DOM_text_sha256"] == row["original_DOM_text_sha256"]
             and source["distinct_source_variant_keys_NOT_EQUIVALENCE"] ==
                 row["distinct_origin_scoped_source_variant_keys_NOT_ALIASES"],
             "source ID, original DOM or origin-scoped variant was substituted")
        variants = row["distinct_origin_scoped_source_variant_keys_NOT_ALIASES"]
        need(type(variants) is list and len(set(variants)) == len(variants)
             and all(type(v) is str and HEX.fullmatch(v) for v in variants),
             "distinct source identity damaged")
        before = source["historical_before_claim_container_UNABRIDGED_OR_NONE"]
        after = source["historical_after_claim_container_UNABRIDGED_OR_NONE"]
        prior = row["historical_claim_scope_comparison_NOT_A_SAFETY_VERDICT"]
        need(prior["before_FULL_TEXT_SHA256_OR_NONE"] ==
             (None if before is None else fingerprint(before))
             and prior["after_FULL_TEXT_SHA256_OR_NONE"] ==
             (None if after is None else fingerprint(after))
             and prior["before_literal_citation_tokens_OR_NONE"] ==
             (None if before is None else CITE.findall(before))
             and prior["after_literal_citation_tokens_OR_NONE"] ==
             (None if after is None else CITE.findall(after)),
             "full historical claim text drifted from R90 evidence")
        findings = compare(before, after)
        for flag in findings["review_cues_NOT_SAFETY_FINDINGS"]:
            counters[flag] += 1
        output.append({
            "kind": key[0], "slug": key[1], "citation_ordinal": key[2],
            "literal_source_ID": row["literal_source_ID"],
            "original_DOM_block_ID": row["original_DOM_block_ID"],
            "original_DOM_text_sha256": row["original_DOM_text_sha256"],
            "distinct_origin_scoped_source_variant_keys_NOT_ALIASES": list(variants),
            "R90_exact_original_review_row_SHA256": digest(row),
            "citation_claim_boundary_review_NOT_SAFETY_VERDICT": findings,
            "human_source_review": REVIEW, "human_claim_support": REVIEW,
            "qualified_safety_review": REVIEW, "independent_QD_review": REVIEW,
            "may_publish": False,
        })
    need(len(seen) == len(lookup) and len(output) == len(rows),
         "historical evidence or literal citation occurrence lost")
    counts = parent["counts"]
    want = {"documents":41, "article":35, "tool":6,
            "complete_DOM_blocks":4070, "citation_occurrences":2173,
            "source_variant_edges":2359, "distinct_source_variants":242,
            "unpaired_historical_reviews_preserved":11}
    # For isolated synthetic unit fixtures permit a smaller census in audit;
    # the full production census is always enforced by live(expected=EXPECTED).
    need(all(type(counts.get(k)) is int for k in want),
         "R90 complete census counters unavailable")
    need(counts["citation_occurrences"] == len(rows),
         "full original citation census altered")
    output.sort(key=lambda r: (r["kind"], r["slug"], r["citation_ordinal"]))
    report = {
        "schema": SCHEMA, "issue":136, "release_state":HOLD,
        "may_publish":False, "medical_safety_approved":False,
        "human_source_approvals":0, "human_claim_approvals":0,
        "qualified_safety_approvals":0, "independent_QD_approvals":0,
        "complete_R90_original_evidence_UNABRIDGED_NOT_APPROVED": parent,
        "all_literal_citation_claim_boundary_review_rows_NOT_APPROVED":output,
        "counts":{
            **{k:counts[k] for k in want},
            "lexical_citation_boundary_review_cues_NOT_VERDICTS":dict(sorted(counters.items()))
        },
    }
    report["sha256_seal"] = digest(report)
    return report


def audit(parent, *, expected=None):
    report = index(parent)
    if expected is not None:
        c = report["counts"]
        need(tuple(c[k] for k in ("documents", "article", "tool",
                "citation_occurrences", "source_variant_edges",
                "complete_DOM_blocks", "distinct_source_variants")) == expected,
             "R91 41-document census changed")
        need(c["unpaired_historical_reviews_preserved"] == 11,
             "11 unmatched historical records lost")
    return report


def verify(report, parent, *, expected=None):
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("issue") == 136
         and report.get("release_state") == HOLD
         and report.get("may_publish") is False
         and report.get("medical_safety_approved") is False
         and all(type(report.get(k)) is int and report[k] == 0 for k in (
             "human_source_approvals", "human_claim_approvals",
             "qualified_safety_approvals", "independent_QD_approvals")),
         "R91 false release/medical/human approval")
    need(report.get("sha256_seal") == digest(
         {k: v for k, v in report.items() if k != "sha256_seal"}),
         "R91 report evidence seal invalid")
    need(report == audit(parent, expected=expected),
         "R91 source/citation review dossier or evidence changed")


def live():
    r90 = upstream()
    parent, ancestor = r90.live()
    r90.verify(parent, ancestor, expected=r90.EXPECTED)
    report = audit(parent, expected=EXPECTED)
    verify(report, parent, expected=EXPECTED)
    return report, parent


def private_csv(report, parent, *, expected=None):
    """Metadata-only workorders, not an importable human approval register."""
    verify(report, parent, expected=expected)
    s = io.StringIO(newline="")
    w = csv.writer(s, lineterminator="\n")
    w.writerow(("kind", "slug", "citation_ordinal", "literal_source_ID",
                "review_cues_NOT_SAFETY_FINDINGS",
                "human_claim_support", "qualified_safety_review", "may_publish"))
    def protect(v):
        return "'" + v if v.lstrip().startswith(("=", "+", "-", "@", "\t", "\r", "\n")) else v
    for row in report["all_literal_citation_claim_boundary_review_rows_NOT_APPROVED"]:
        findings = row["citation_claim_boundary_review_NOT_SAFETY_VERDICT"]
        w.writerow([protect(v) for v in (
            row["kind"], row["slug"], str(row["citation_ordinal"]),
            row["literal_source_ID"], ";".join(findings["review_cues_NOT_SAFETY_FINDINGS"]),
            REVIEW, REVIEW, "FALSE")])
    return s.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--private-csv-stdout", action="store_true")
    args = ap.parse_args(argv)
    report, parent = live()
    if args.private_csv_stdout:
        print(private_csv(report, parent, expected=EXPECTED), end="")
    else:
        print(json.dumps({"schema": SCHEMA, "release_state": HOLD,
                          "may_publish": False, "counts": report["counts"],
                          "sha256_seal": report["sha256_seal"]}, sort_keys=True))


if __name__ == "__main__":
    main()
