#!/usr/bin/env python3
"""R79 PRIVATE HOLD: context-dependent source and passage review work orders.

Only builds an offline, deterministic review dependency ledger from R78's
unabridged research. A nearby citation is NOT evidence of claim support.
Lexical triage is NOT a medical, emergency, or other safety determination.
No CMS access, edits, approvals, publication or WordPress writes.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

SCHEMA = "r79-context-dependent-source-workorders-hold-v1"
PARENT = "r78-document-citation-source-review-hold-v1"
REVIEW = "NOT_REVIEWED"
CENSUS = (35, 6, 244, 2173, 2359, 4070, 32, 15, 1068, 347)
HOLD_KEYS = ("may_publish", "independent_QD_approval",
             "qualified_safety_clearance", "human_source_links_verified")


class Hold(ValueError):
    """A review/provenance gate has failed closed."""


def need(condition, why):
    if not condition:
        raise Hold(why)


def digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False).encode("utf-8")).hexdigest()


def _r78():
    path = Path(__file__).with_name("r78_document_citation_review_matrix.py")
    need(path.is_file() and not path.is_symlink(),
         "R78 immutable parent tool missing")
    spec = importlib.util.spec_from_file_location("r79_r78_parent", path)
    need(spec is not None and spec.loader is not None,
         "R78 immutable parent unreadable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_csv_cell(value):
    """Neutralize formula-leading Unicode/whitespace without losing text."""
    cell = str(value)
    prefix = cell.lstrip(" \t\r\n\ufeff\u200b\u2060\u200e\u200f")
    if (cell[:1] in ("\t", "\r", "\n", "\ufeff", "\u200b",
                     "\u2060", "\u200e", "\u200f")
            or prefix.startswith(("=", "+", "-", "@"))):
        return "'" + cell
    return cell


def sealed(report):
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("issue") == 136
         and report.get("release_state") == "HOLD"
         and report.get("machine_only") is True
         and report.get("publication_clearance") is False
         and all(report.get(k) is False for k in HOLD_KEYS)
         and report.get("fingerprint_sha256") ==
             digest({k: v for k, v in report.items()
                     if k != "fingerprint_sha256"}),
         "R79 source/action review not sealed or falsely approved")


def _edge_identity(edge):
    return (edge["kind"], edge["slug"], edge["block_id"],
            edge["citation_ordinal"])


def _context(block):
    if block is None:
        return None
    return {
        "block_id": block["block_id"],
        "DOM_text_UNABRIDGED_NOT_REVIEWED":
            block["unabridged_DOM_text_NOT_REVIEWED"],
        "DOM_text_sha256": block["DOM_text_sha256"],
        "neighbor_citation_ordinals_NOT_CLAIM_SUPPORT_PROOF":
            [c["citation_ordinal"] for c in block[
                "citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"]],
    }


def construct(parent, *, expected=CENSUS):
    """Reconstruct every source/action edge; never accept user review decisions.

    Parent is included verbatim, so all 41 entire documents, 244 full research
    records, 2,173 occurrences and 2,359 distinct-origin edges are conserved.
    A modified but re-fingerprinted R78 parent is rejected through a second
    independent reconstruction of the sealed R77 evidence.
    """
    need(type(expected) is tuple and len(expected) == 10
         and all(type(n) is int and n > 0 for n in expected),
         "expected complete ten-field custody baseline is invalid")
    r78 = _r78()
    r78.sealed(parent)
    need(parent.get("schema") == PARENT, "wrong R78 parent")
    source_parent = parent.get("complete_R77_evidence_UNABRIDGED_NOT_APPROVED")
    need(type(source_parent) is dict and
         parent == r78.construct(source_parent),
         "R78 parent differs from independently reconstructed source evidence")
    c = parent.get("counts")
    need(type(c) is dict and tuple(c.get(k) for k in (
        "articles", "tools", "distinct_source_readings_retained",
        "citation_occurrences_retained", "source_variant_edges_retained",
        "unabridged_DOM_blocks_retained",
        "shared_URL_source_groups_retained", "reused_source_ID_groups_retained",
        "consequential_action_or_quantity_review_blocks",
        "consequential_blocks_without_same_block_citations")) == expected,
        "35 articles / source / citation / high-consequence census changed")
    need(all(c.get(k) == 0 for k in (
        "human_source_link_checks", "human_claim_reviews",
        "qualified_safety_reviews", "independent_QD_approvals")),
        "upstream claims nonexistent human approval")
    r76 = source_parent.get("complete_R76_evidence_UNABRIDGED_NOT_APPROVED")
    readings = r76.get("all_244_unabridged_source_readings_NOT_REVIEWED")
    dates = source_parent.get(
        "all_origin_scoped_temporal_review_packets_NOT_APPROVED")
    docs = parent.get("document_review_packets_NOT_APPROVED")
    need(type(readings) is list and len(readings) == expected[2]
         and type(dates) is list and len(dates) == expected[2]
         and type(docs) is list and len(docs) == expected[0] + expected[1],
         "complete source readings, temporal review or documents absent")

    by_source, date_by_source = {}, {}
    url_groups, id_groups = defaultdict(set), defaultdict(set)
    for s in readings:
        need(type(s) is dict, "malformed source research")
        key = (s.get("source_origin"), s.get("source_id"))
        reading = s.get("candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        original = s.get("original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        need(all(type(v) is str and v for v in key) and
             key not in by_source and type(reading) is dict and
             reading.get("id") == key[1] and
             reading.get("url") == s.get("exact_URL_NO_ALIAS") and
             reading.get("human_link_check") is False and
             s.get("candidate_reading_sha256") == digest(reading) and
             ((original is None and s.get("original_reading_sha256") is None)
              or (type(original) is dict and
                  s.get("original_reading_sha256") == digest(original))) and
             s.get("human_source_and_claim_review") == REVIEW and
             s.get("qualified_safety_review") == REVIEW,
             "source identity, historical reading or human review changed")
        by_source[key] = s
        url_groups[s["exact_URL_NO_ALIAS"]].add(key)
        id_groups[key[1]].add(key)
    need(sum(len(v) > 1 for v in url_groups.values()) == expected[6] and
         sum(len(v) > 1 for v in id_groups.values()) == expected[7],
         "source URL or reused-ID collision group was aliased away")
    for s in dates:
        need(type(s) is dict, "temporal source packet malformed")
        key = (s.get("source_origin"), s.get("source_id"))
        r = by_source.get(key)
        need(r is not None and key not in date_by_source and
             s.get("complete_candidate_reading_sha256") ==
                 r["candidate_reading_sha256"] and
             s.get("exact_URL_NO_ALIAS") == r["exact_URL_NO_ALIAS"] and
             s.get("human_link_check") is False and
             s.get("human_claim_support_review") == REVIEW and
             s.get("qualified_safety_review") == REVIEW and
             type(s.get(
                 "literal_temporal_review_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT"))
                 is list,
             "date review source identity or HOLD status changed")
        date_by_source[key] = s
    need(set(by_source) == set(date_by_source),
         "temporal metadata source scope lost")

    source_edges = defaultdict(list)
    action_orders = []
    document_orders = []
    seen_docs, seen_blocks, citation_ids = set(), set(), set()
    total_edges = 0
    uncited_actions = 0
    for doc in docs:
        need(type(doc) is dict and doc.get("packet_sha256") ==
             digest({k: v for k, v in doc.items() if k != "packet_sha256"}),
             "document-first review packet unsealed")
        kind, slug = doc["kind"], doc["slug"]
        dkey = (kind, slug)
        need(kind in ("article", "tool") and dkey not in seen_docs
             and doc.get("human_claim_support_review") == REVIEW
             and doc.get("qualified_safety_review") == REVIEW
             and doc.get("independent_QD_review") == REVIEW,
             "document identity duplicate or review approval forged")
        seen_docs.add(dkey)
        blocks = doc["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"]
        need(doc["original_DOM_block_ids_in_reading_order"] ==
             [b["block_id"] for b in blocks],
             "document reading order truncated or reordered")
        used = set()
        local_occurrences = set()
        local_actions = []
        local_edges = 0
        for index, b in enumerate(blocks):
            bkey = (kind, slug, b["block_id"])
            need(bkey not in seen_blocks and
                 hashlib.sha256(b[
                     "unabridged_DOM_text_NOT_REVIEWED"].encode("utf-8")
                 ).hexdigest() == b["DOM_text_sha256"] and
                 b.get("human_claim_support_review") == REVIEW and
                 b.get("qualified_safety_review") == REVIEW,
                 "DOM block changed, duplicated or falsely cleared")
            seen_blocks.add(bkey)
            citations = b[
                "citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"]
            local_scopes = []
            for citation in citations:
                ordinal = citation["citation_ordinal"]
                occurrence = (kind, slug, ordinal)
                need(type(ordinal) is int and ordinal > 0
                     and occurrence not in citation_ids
                     and citation["block_id"] == b["block_id"]
                     and citation["kind"] == kind
                     and citation["slug"] == slug
                     and citation.get("human_claim_support_review") == REVIEW
                     and citation.get("qualified_safety_review") == REVIEW,
                     "original citation ordinal duplicated or moved")
                citation_ids.add(occurrence)
                local_occurrences.add(ordinal)
                variants = citation[
                    "source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"]
                need(type(variants) is list and variants,
                     "citation variants absent")
                seen_variants = set()
                for v in variants:
                    sk = (v["source_origin"], v["source_id"])
                    r = by_source.get(sk)
                    need(r is not None and sk not in seen_variants
                         and v["source_id"] == citation["raw_source_id"]
                         and v["exact_URL_NOT_CANONICALIZED"] ==
                             r["exact_URL_NO_ALIAS"]
                         and v["complete_source_reading_sha256"] ==
                             r["candidate_reading_sha256"],
                         "source variant aliased, duplicated or moved")
                    seen_variants.add(sk)
                    used.add(sk)
                    local_scopes.append(sk)
                    edge = {
                        "kind":kind, "slug":slug, "block_id":b["block_id"],
                        "DOM_text_sha256":b["DOM_text_sha256"],
                        "citation_ordinal":ordinal,
                        "raw_source_id":citation["raw_source_id"],
                        "consequential_lexical_context_NOT_VERDICT":
                            b["consequential_action_or_quantity_LEXICAL_TRIAGE_ONLY"],
                    }
                    source_edges[sk].append(edge)
                    total_edges += 1
                    local_edges += 1
            if b["consequential_action_or_quantity_LEXICAL_TRIAGE_ONLY"]:
                no_local = not citations
                if no_local:
                    uncited_actions += 1
                cues = (["NO_SAME_BLOCK_CITATION_REVIEW_ONLY"]
                        if no_local else [])
                for sk in sorted(set(local_scopes)):
                    s = date_by_source[sk]
                    if len(url_groups[by_source[sk]["exact_URL_NO_ALIAS"]]) > 1:
                        cues.append("SHARED_EXACT_URL_SCOPE_NOT_EQUIVALENCE")
                    if len(id_groups[sk[1]]) > 1:
                        cues.append("REUSED_SOURCE_ID_DISTINCT_ORIGINS")
                    if s[
                        "literal_temporal_review_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT"]:
                        cues.append("SOURCE_DATE_METADATA_CUE_NOT_FRESHNESS")
                flags = sorted(set(cues))
                action = {
                    "kind":kind, "slug":slug,
                    "private_draft_url_NOT_PUBLISHED":doc["private_draft_url"],
                    "original_DOM_block_position_1_based":index + 1,
                    "block_id":b["block_id"],
                    "unabridged_action_text_NOT_SAFETY_REVIEWED":
                        b["unabridged_DOM_text_NOT_REVIEWED"],
                    "DOM_text_sha256":b["DOM_text_sha256"],
                    "previous_block_UNABRIDGED_CONTEXT_NOT_VERDICT":
                        _context(blocks[index - 1] if index else None),
                    "next_block_UNABRIDGED_CONTEXT_NOT_VERDICT":
                        _context(blocks[index + 1] if index + 1 < len(blocks)
                                 else None),
                    "all_local_citation_occurrences_NOT_CLAIM_PROOF":
                        deepcopy(citations),
                    "distinct_origin_scoped_sources_NOT_EQUIVALENT":
                        [list(k) for k in sorted(set(local_scopes))],
                    "mechanical_review_cues_NOT_SAFETY_FINDINGS":flags,
                    "human_claim_support_review":REVIEW,
                    "qualified_safety_review":REVIEW,
                    "independent_QD_review":REVIEW,
                }
                action["packet_sha256"] = digest(action)
                action_orders.append(action)
                local_actions.append(b["block_id"])
        need(local_occurrences == set(
             range(1, doc["citation_occurrences_NOT_UNIQUE_CLAIMS"] + 1))
             and len(used) == len(doc[
                 "all_distinct_origin_scoped_sources_NOT_APPROVED"])
             and local_edges == doc["source_variant_edges_NOT_CLAIMS"],
             "document source/citation count, order or origin scope changed")
        need([list(k) for k in sorted(used)] ==
             [[s["source_origin"], s["source_id"]] for s in doc[
                 "all_distinct_origin_scoped_sources_NOT_APPROVED"]],
             "document source dependency mapping changed")
        document_orders.append({
            "kind":kind, "slug":slug,
            "private_draft_url_NOT_PUBLIC":doc["private_draft_url"],
            "original_block_count":len(blocks),
            "citation_occurrences_NOT_CLAIMS":len(local_occurrences),
            "distinct_source_variant_edges_NOT_CLAIMS":local_edges,
            "distinct_origin_scoped_source_keys_NOT_EQUIVALENT":
                [list(k) for k in sorted(used)],
            "action_or_quantity_lexical_review_block_ids":local_actions,
            "human_claim_support_review":REVIEW,
            "qualified_safety_review":REVIEW,
        })
    need(len(seen_docs) == sum(expected[:2]) and
         len(seen_blocks) == expected[5] and
         len(citation_ids) == expected[3] and
         total_edges == expected[4] and
         len(action_orders) == expected[8] and
         uncited_actions == expected[9],
         "all-document source/citation/action review coverage changed")

    source_orders = []
    for key in sorted(by_source):
        r = by_source[key]
        t = date_by_source[key]
        edges = sorted(source_edges[key], key=lambda e: (
            e["kind"], e["slug"], e["citation_ordinal"], e["block_id"]))
        expected_edges = t[
            "all_downstream_citation_variant_edges_NOT_CLAIM_PROOF"]
        # Keep citation ordinal as the primary within-document order; a
        # lexical block-id sort would silently reorder valid citations.
        need([_edge_identity(e) for e in edges] ==
             [_edge_identity(e) for e in sorted(expected_edges,
                key=lambda e: (e["kind"], e["slug"],
                               e["citation_ordinal"], e["block_id"]))],
             "downstream citation edges lost or attributed to wrong origin")
        need(all(e["raw_source_id"] == key[1] for e in edges),
             "source key was confused with same-URL variant")
        reading = r["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"]
        history = r["original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"]
        row = {
            "source_origin":key[0], "source_id":key[1],
            "exact_URL_NO_ALIAS_OR_ENDORSEMENT":r["exact_URL_NO_ALIAS"],
            "candidate_research_reading_UNABRIDGED_NOT_HUMAN_VERIFIED":
                deepcopy(reading),
            "candidate_reading_sha256":r["candidate_reading_sha256"],
            "historical_research_reading_IF_PRESENT_UNABRIDGED":
                deepcopy(history),
            "historical_reading_sha256":r["original_reading_sha256"],
            "temporal_metadata_cues_NOT_FRESHNESS_OR_VERDICT":deepcopy(t[
                "literal_temporal_review_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT"]),
            "shared_exact_URL_distinct_source_origins_NOT_ALIASED":
                [list(k) for k in sorted(
                    url_groups[r["exact_URL_NO_ALIAS"]])],
            "reused_source_ID_distinct_origins_NOT_ALIASED":
                [list(k) for k in sorted(id_groups[key[1]])],
            "every_downstream_citation_variant_edge_NOT_CLAIM_PROOF":edges,
            "cited_occurrence_count_NOT_UNIQUE_CLAIMS":len(edges),
            "human_link_check":False,
            "human_claim_support_review":REVIEW,
            "qualified_safety_review":REVIEW,
            "independent_QD_review":REVIEW,
        }
        row["packet_sha256"] = digest(row)
        source_orders.append(row)
    need(len(source_orders) == expected[2] and
         sum(len(p["every_downstream_citation_variant_edge_NOT_CLAIM_PROOF"])
             for p in source_orders) == expected[4],
         "source-level downstream dependency ledger incomplete")

    report = {
        "schema":SCHEMA, "issue":136, "release_state":"HOLD",
        "machine_only":True, "publication_clearance":False,
        "original_R78_fingerprint_sha256":parent["fingerprint_sha256"],
        "complete_R78_evidence_UNABRIDGED_NOT_APPROVED":deepcopy(parent),
        "document_source_dependency_orders_NOT_APPROVED":document_orders,
        "source_work_orders_FULL_READINGS_NOT_APPROVED":source_orders,
        "action_context_work_orders_LEXICAL_ONLY_NOT_APPROVED":action_orders,
        "counts":{
            "article_drafts":expected[0], "tool_drafts":expected[1],
            "source_full_readings":len(source_orders),
            "citation_occurrences_NOT_UNIQUE_CLAIMS":len(citation_ids),
            "citation_source_variant_edges_NOT_CLAIMS":total_edges,
            "unabridged_DOM_blocks":len(seen_blocks),
            "shared_exact_URL_groups_NOT_EQUIVALENT":expected[6],
            "reused_ID_groups_NOT_EQUIVALENT":expected[7],
            "lexical_action_or_quantity_work_orders":len(action_orders),
            "lexical_action_or_quantity_without_same_block_citation":
                uncited_actions,
            "source_readings_without_citation_edges":sum(
                not s["every_downstream_citation_variant_edge_NOT_CLAIM_PROOF"]
                for s in source_orders),
            "human_link_checks":0, "human_claim_reviews":0,
            "qualified_safety_reviews":0, "independent_QD_approvals":0},
        "limitations":(
            "Source identity, same-block citations, neighboring qualifiers and "
            "dates are review routing only. None proves that cited sources "
            "support a claim, supplies a missing citation, resolves shared "
            "URLs, establishes medical/food/water/fire/generator safety, or "
            "approves historical practice for present use. Source readings "
            "and all documents are preserved in full; original evidence "
            "remains unreviewed. Offline private draft only; mandatory "
            "release-integrity, human source verification, qualified "
            "safety review, real WordPress/browser and QD gates remain HOLD."),
        **{k:False for k in HOLD_KEYS},
    }
    report["fingerprint_sha256"] = digest(report)
    sealed(report)
    return report


def _write_csv(header, rows):
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(header)
    for row in rows:
        writer.writerow([safe_csv_cell(cell) for cell in row])
    return out.getvalue()


def csv_private_source_queue(report):
    """A one-way spreadsheet review queue, never an approvals importer."""
    sealed(report)
    return _write_csv((
        "source_origin", "source_id", "exact_URL_NOT_VERIFIED",
        "downstream_variant_edges_NOT_CLAIMS",
        "distinct_shared_URL_origin_variants_NOT_EQUIVALENT",
        "date_metadata_cue_count_NOT_FRESHNESS",
        "human_link_check", "human_claim_support_review",
        "qualified_safety_review", "reviewer_notes_UNTRUSTED"), (
        (s["source_origin"], s["source_id"],
         s["exact_URL_NO_ALIAS_OR_ENDORSEMENT"],
         s["cited_occurrence_count_NOT_UNIQUE_CLAIMS"],
         len(s["shared_exact_URL_distinct_source_origins_NOT_ALIASED"]),
         len(s["temporal_metadata_cues_NOT_FRESHNESS_OR_VERDICT"]),
         "NOT_CHECKED", REVIEW, REVIEW, "")
        for s in report["source_work_orders_FULL_READINGS_NOT_APPROVED"]))


def csv_private_action_queue(report):
    """One-way claim-context work orders; no machine safety verdict."""
    sealed(report)
    return _write_csv((
        "private_draft_url_NOT_PUBLIC", "kind", "slug", "block_id",
        "original_block_position_1_based", "action_text_NOT_SAFETY_REVIEWED",
        "local_citations_NOT_CLAIM_PROOF",
        "distinct_origin_scoped_source_keys_NOT_EQUIVALENT",
        "mechanical_review_cues_NOT_SAFETY_VERDICTS",
        "human_claim_support_review", "qualified_safety_review",
        "reviewer_notes_UNTRUSTED"), (
        (p["private_draft_url_NOT_PUBLISHED"], p["kind"], p["slug"],
         p["block_id"], p["original_DOM_block_position_1_based"],
         p["unabridged_action_text_NOT_SAFETY_REVIEWED"],
         len(p["all_local_citation_occurrences_NOT_CLAIM_PROOF"]),
         json.dumps(p["distinct_origin_scoped_sources_NOT_EQUIVALENT"],
                    ensure_ascii=False),
         ";".join(p["mechanical_review_cues_NOT_SAFETY_FINDINGS"]),
         REVIEW, REVIEW, "")
        for p in report["action_context_work_orders_LEXICAL_ONLY_NOT_APPROVED"]))


def live_report(repo_root=None):
    parent = _r78().live_report(repo_root)
    return construct(parent)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    csv_group = parser.add_mutually_exclusive_group()
    csv_group.add_argument("--private-source-csv-stdout", action="store_true")
    csv_group.add_argument("--private-action-csv-stdout", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = live_report(args.repo_root)
        if args.private_source_csv_stdout:
            sys.stdout.write(csv_private_source_queue(report))
        elif args.private_action_csv_stdout:
            sys.stdout.write(csv_private_action_queue(report))
        else:
            print(json.dumps({
                "schema":SCHEMA, "release_state":"HOLD",
                "fingerprint_sha256":report["fingerprint_sha256"],
                "counts":report["counts"], "publication_clearance":False},
                sort_keys=True))
        return 0
    except (Hold, ValueError, KeyError, TypeError, AttributeError,
            OSError) as exc:
        print("R79 PRIVATE RELEASE HOLD: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
