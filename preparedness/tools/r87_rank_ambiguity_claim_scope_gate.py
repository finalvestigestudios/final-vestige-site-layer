#!/usr/bin/env python3
"""R87 private HOLD: expose rank-only citation alignments that cannot prove claim identity.

Read-only review overlay on R86's complete 41-document evidence bridge.
Preserves complete originals, including unmatched historical rows and all origin-
scoped source identities. No link checks, safety approvals, CMS writes or publication.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import importlib.util
import io
import json
from pathlib import Path

SCHEMA = "r87-rank-ambiguity-claim-scope-private-hold-v1"
REVIEW = "NOT_REVIEWED"
HOLD = "HOLD"
EXPECTED = (41, 35, 6, 2173, 2359, 4070, 1768)


class Gate(ValueError):
    """Historical citation identity, original evidence or release HOLD was lost."""


def need(value, reason):
    if not value:
        raise Gate(reason)


def parent_module():
    p = Path(__file__).with_name("r86_full_slate_historical_citation_bridge.py")
    need(p.is_file() and not p.is_symlink(), "R86 original module unavailable")
    spec = importlib.util.spec_from_file_location("r87_r86_parent", p)
    need(spec is not None and spec.loader is not None, "R86 loader unavailable")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalized(value):
    return " ".join(value.split()) if type(value) is str else None


def _input_guard(report, r86):
    need(type(report) is dict and report.get("schema") == r86.SCHEMA
         and report.get("issue") == 136
         and report.get("release_state") == HOLD
         and report.get("may_publish") is False
         and report.get("medical_safety_approved") is False
         and all(report.get(k) == 0 for k in
                 ("human_source_approvals", "human_claim_approvals",
                  "qualified_safety_approvals", "independent_QD_approvals")),
         "R86 parent claims nonexistent review or publication")
    need(report.get("sha256_seal") ==
         r86.digest({k: v for k, v in report.items() if k != "sha256_seal"}),
         "R86 original evidence fingerprint invalid")
    need(type(report.get("counts")) is dict
         and type(report.get("all_41_unabridged_document_review_bridges_NOT_APPROVED")) is list
         and type(report.get("all_unpaired_R85_historical_citation_reviews_UNABRIDGED")) is list,
         "R86 original complete populations unavailable")

    # A matching digest alone is not proof. Independently reconstruct R86
    # from the unabridged originals carried within its own sealed packets.
    packets = report["all_41_unabridged_document_review_bridges_NOT_APPROVED"]
    leftovers = report["all_unpaired_R85_historical_citation_reviews_UNABRIDGED"]
    docs, rows = [], []
    for packet in packets:
        docs.append(packet["R80_complete_original_document_UNABRIDGED_NOT_APPROVED"])
        for link in packet["R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"]:
            historical = link["R85_original_four_stage_impact_UNABRIDGED_NOT_APPROVED"]
            if historical is not None:
                rows.append(historical)
    rows.extend(row["R85_original_comparison_UNABRIDGED_NOT_APPROVED"]
                for row in leftovers)
    need(len(rows) == report["counts"]["matched_historical_rows"] + len(leftovers),
         "original historical comparison rows lost")
    r86.verify(report, docs, rows,
               r80_fingerprint=report["R80_unabridged_full_slate_evidence_fingerprint"],
               r85_seal=report["R85_unabridged_historical_citation_source_seal"])



def audit(report, *, expected=None):
    """Pure complete overlay; rank matching is NEVER equivalent to claim matching."""
    r86 = parent_module()
    _input_guard(report, r86)
    packets = report["all_41_unabridged_document_review_bridges_NOT_APPROVED"]
    leftovers = report["all_unpaired_R85_historical_citation_reviews_UNABRIDGED"]
    counters = Counter()
    output, unique_docs, all_origins, historical_keys = [], set(), set(), set()
    for packet in packets:
        need(type(packet) is dict and packet.get("may_publish") is False
             and packet.get("human_claim_support") == REVIEW
             and packet.get("qualified_safety_review") == REVIEW
             and packet.get("independent_QD_review") == REVIEW,
             "R86 document has unsafe release status")
        kind, slug = packet["kind"], packet["slug"]
        need(kind in ("article", "tool") and type(slug) is str and slug,
             "invalid RC document identity")
        doc_key = (kind, slug)
        need(doc_key not in unique_docs, "duplicate document lost separate original")
        unique_docs.add(doc_key)
        orig = packet["R80_complete_original_document_UNABRIDGED_NOT_APPROVED"]
        blocks = orig["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"]
        order = orig["original_DOM_block_ids_in_reading_order"]
        need([b["block_id"] for b in blocks] == order
             and len(set(order)) == len(order), "original DOM reading order changed")
        block_by_id = {b["block_id"]: b for b in blocks}
        rows = packet["R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"]
        need(type(rows) is list and
             len(rows) == orig["citation_occurrences_NOT_UNIQUE_CLAIMS"],
             "R86 citations omitted from document")
        ranks = Counter(x["R80_original_citation_UNABRIDGED_NOT_APPROVED"]["raw_source_id"]
                        for x in rows)
        shifted = set()
        seen_citations = set()
        for item in rows:
            old = item["R85_original_four_stage_impact_UNABRIDGED_NOT_APPROVED"]
            c = item["R80_original_citation_UNABRIDGED_NOT_APPROVED"]
            if old is not None:
                historical = old["R83_complete_unabridged_current_to_RC_review"]
                before, after = historical["before_FULL_ANCHOR"], historical["after_FULL_ANCHOR"]
                if (before is None) != (after is None):
                    shifted.add(c["raw_source_id"])
        for leftover in leftovers:
            need(type(leftover) is dict and leftover.get("may_publish") is False
                 and leftover.get("human_claim_support") == REVIEW,
                 "unpaired historical row has false approval")
            identity = leftover["identity"]
            if (type(identity) is list and len(identity) == 3
                    and identity[0] == slug and kind == "article"):
                h = leftover["R85_original_comparison_UNABRIDGED_NOT_APPROVED"]
                pair = h["R83_complete_unabridged_current_to_RC_review"]
                if (pair["before_FULL_ANCHOR"] is None) != (pair["after_FULL_ANCHOR"] is None):
                    shifted.add(identity[1])
        reviewed = []
        for item in rows:
            c = item["R80_original_citation_UNABRIDGED_NOT_APPROVED"]
            ordinal, sid = c["citation_ordinal"], c["raw_source_id"]
            bid = item["R80_original_block_id"]
            need(type(ordinal) is int and ordinal > 0
                 and type(sid) is str and sid
                 and ordinal not in seen_citations and bid in block_by_id,
                 "citation ordinal or DOM block identity lost")
            seen_citations.add(ordinal)
            block = block_by_id[bid]
            need(block["human_claim_support_review"] == REVIEW
                 and block["qualified_safety_review"] == REVIEW
                 and item["human_claim_support"] == REVIEW
                 and item["qualified_safety_review"] == REVIEW
                 and item["may_publish"] is False,
                 "source/passages granted unsupported approval")
            flags = set(item["review_cues_NOT_VERDICTS"])
            history = item["R85_original_four_stage_impact_UNABRIDGED_NOT_APPROVED"]
            if ranks[sid] > 1:
                flags.add("SAME_SOURCE_ID_REPEATED_RANK_IS_NOT_CLAIM_IDENTITY")
            if sid in shifted:
                flags.add("SAME_SOURCE_ID_HISTORICAL_ADDITION_REMOVAL_RANK_SHIFT_RISK")
            if block.get("consequential_action_or_quantity_LEXICAL_TRIAGE_ONLY") is True:
                flags.add("ACTION_OR_QUANTITY_LEXICAL_REVIEW_NOT_SAFETY_VERDICT")
            if history is not None:
                historical = history["R83_complete_unabridged_current_to_RC_review"]
                after = historical["after_FULL_ANCHOR"]
                if after is None:
                    flags.add("HISTORICAL_RC_OCCURRENCE_MISSING")
                else:
                    token = after.get("literal_token")
                    expected_token = "{{cite:" + sid + "}}"
                    if token is None:
                        flags.add("HISTORICAL_TOKEN_NOT_PRESENT_IN_ANCHOR_PACKET")
                    elif token != expected_token:
                        flags.add("HISTORICAL_LITERAL_CITATION_TOKEN_DIFFERS")
                    scope = after.get("scope_state")
                    if scope != "VISIBLE_CONTAINER_NOT_SUPPORT_PROOF":
                        flags.add("HISTORICAL_CITATION_NONVISIBLE_OR_UNMAPPED")
                    context = after.get("complete_container_text_UNABRIDGED")
                    original_text = block["unabridged_DOM_text_NOT_REVIEWED"]
                    if not type(context) is str or not context.strip():
                        flags.add("HISTORICAL_CLAIM_CONTAINER_CONTEXT_UNAVAILABLE")
                    elif normalized(context) not in normalized(original_text):
                        flags.add("HISTORICAL_CLAIM_CONTAINER_NOT_VERBATIM_IN_RC_BLOCK")
                    if expected_token not in original_text:
                        flags.add("RC_BLOCK_CITATION_TOKEN_NOT_VERBATIM_OBSERVED")
            else:
                flags.add("NO_FOUR_STAGE_HISTORICAL_OCCURRENCE")
            source_edges = r86.variants(c)
            counters["source_variant_edges"] += len(source_edges)
            for edge in source_edges:
                all_origins.add((edge[0], edge[1], edge[2], edge[3]))
            reviewed.append({
                "R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED": item,
                "R80_original_complete_DOM_block_UNABRIDGED_NOT_APPROVED": block,
                "review_cues_NOT_VERDICTS": sorted(flags),
                "rank_alignment_proves_claim_identity": False,
                "human_claim_support": REVIEW,
                "qualified_safety_review": REVIEW, "may_publish": False,
            })
            counters["citations"] += 1
            if flags:
                counters["citation_occurrences_for_human_review"] += 1
            if ranks[sid] > 1:
                counters["repeated_ID_occurrences"] += 1
            if sid in shifted:
                counters["rank_shift_risk_occurrences"] += 1
        need(len(seen_citations) == len(rows), "citation occurrence silently omitted")
        counters[kind] += 1
        counters["blocks"] += len(blocks)
        output.append({
            "kind": kind, "slug": slug,
            "R86_complete_document_UNABRIDGED_NOT_APPROVED": packet,
            "all_original_citation_and_claim_context_reviews_NOT_APPROVED": reviewed,
            "human_claim_support": REVIEW, "qualified_safety_review": REVIEW,
            "independent_QD_review": REVIEW, "may_publish": False,
        })
    for item in leftovers:
        identity = item["identity"]
        need(type(identity) is list and len(identity) == 3,
             "unpaired R85 source identity malformed")
        key = tuple(identity)
        need(key not in historical_keys, "duplicate unpaired historical identity")
        historical_keys.add(key)
    # Absent populations are explicit zeros, including synthetic tool-only and
    # uncited documents. Missing keys must never stand in for a zero census.
    for name in ("article", "tool", "citations", "source_variant_edges",
                 "blocks", "citation_occurrences_for_human_review",
                 "repeated_ID_occurrences", "rank_shift_risk_occurrences"):
        counters.setdefault(name, 0)
    counters["documents"] = len(output)
    counters["unpaired_historical_reviews_preserved"] = len(leftovers)
    counters["historical_source_variants_observed"] = len(all_origins)
    if expected is not None:
        need(tuple(counters[k] for k in
             ("documents", "article", "tool", "citations",
              "source_variant_edges", "blocks")) == expected[:6],
             "full 41-document original evidence census changed")
        need(report["counts"]["matched_historical_rows"] +
             len(leftovers) == expected[6],
             "historical comparison rows missing")
    out = {
        "schema": SCHEMA, "issue": 136, "release_state": HOLD,
        "may_publish": False, "medical_safety_approved": False,
        "human_source_approvals": 0, "human_claim_approvals": 0,
        "qualified_safety_approvals": 0, "independent_QD_approvals": 0,
        "R86_complete_original_report_UNABRIDGED_NOT_APPROVED": report,
        "all_41_rank_ambiguity_review_packets_NOT_APPROVED": output,
        "unpaired_historical_review_records_UNABRIDGED": leftovers,
        "counts": dict(sorted(counters.items())),
    }
    out["sha256_seal"] = r86.digest(out)
    return out


def verify(derived, original, *, expected=None):
    r86 = parent_module()
    _input_guard(original, r86)
    need(type(derived) is dict and derived.get("schema") == SCHEMA
         and derived.get("issue") == 136
         and derived.get("release_state") == HOLD
         and derived.get("may_publish") is False
         and derived.get("medical_safety_approved") is False
         and all(derived.get(k) == 0 for k in
                 ("human_source_approvals", "human_claim_approvals",
                  "qualified_safety_approvals", "independent_QD_approvals")),
         "R87 forged approval or publication state")
    need(derived.get("sha256_seal") == r86.digest(
         {k: v for k, v in derived.items() if k != "sha256_seal"}),
         "R87 evidence seal corrupted")
    need(derived == audit(original, expected=expected),
         "R87 does not reconstruct from the unmodified original evidence")


def private_csv(derived, original, *, expected=None):
    verify(derived, original, expected=expected)
    r86 = parent_module()
    target = io.StringIO(newline="")
    writer = csv.writer(target, lineterminator="\n")
    writer.writerow(("kind", "slug", "citation_ordinal", "literal_source_ID",
                     "review_cues_NOT_VERDICTS", "human_claim_review", "may_publish"))
    for doc in derived["all_41_rank_ambiguity_review_packets_NOT_APPROVED"]:
        for row in doc["all_original_citation_and_claim_context_reviews_NOT_APPROVED"]:
            if not row["review_cues_NOT_VERDICTS"]:
                continue
            c = row["R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"][
                "R80_original_citation_UNABRIDGED_NOT_APPROVED"]
            writer.writerow([r86.excel_safe(str(x)) for x in
                (doc["kind"], doc["slug"], c["citation_ordinal"],
                 c["raw_source_id"], ";".join(row["review_cues_NOT_VERDICTS"]),
                 REVIEW, "FALSE")])
    return target.getvalue()


def live():
    r86 = parent_module()
    original = r86.live()
    r87 = audit(original, expected=EXPECTED)
    verify(r87, original, expected=EXPECTED)
    return r87, original


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--private-csv-stdout", action="store_true")
    args = p.parse_args(argv)
    derived, original = live()
    if args.private_csv_stdout:
        print(private_csv(derived, original, expected=EXPECTED), end="")
    else:
        print(json.dumps({"schema": SCHEMA, "release_state": HOLD,
                          "may_publish": False, "medical_safety_approved": False,
                          "counts": derived["counts"],
                          "sha256_seal": derived["sha256_seal"],
                          "WordPress_or_CMS_writes": 0}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (Gate, KeyError, TypeError, ValueError, OSError,
            AttributeError, IndexError) as exc:
        raise SystemExit("R87 FAILED CLOSED: " + str(exc))
