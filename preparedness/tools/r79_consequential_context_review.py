#!/usr/bin/env python3
"""R79 PRIVATE/HOLD: original-order evidence context for consequential passages.

Review-only. Neighboring citations do NOT prove claim support; adjacency
and lexical triage do NOT certify medical, food, water or generator safety.
Never writes to the CMS, edits research, publishes or imports approvals.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

SCHEMA = "r79-consequential-passage-context-hold-v1"
PARENT = "r78-document-citation-source-review-hold-v1"
REVIEW = "NOT_REVIEWED"
HOLD_KEYS = ("may_publish", "independent_QD_approval",
             "qualified_safety_clearance", "human_source_links_verified")
CENSUS = (35, 6, 244, 2173, 2359, 4070, 32, 15, 1068, 347)


class Hold(ValueError):
    """An evidence or release-gate condition was not satisfied."""


def need(condition, reason):
    if not condition:
        raise Hold(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def _r78():
    path = Path(__file__).with_name("r78_document_citation_review_matrix.py")
    need(path.is_file() and not path.is_symlink(), "R78 parent tool missing")
    spec = importlib.util.spec_from_file_location("r79_r78_parent", path)
    need(spec is not None and spec.loader is not None, "R78 parent unreadable")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def citations(block):
    value = block.get("citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF")
    need(type(value) is list, "citation evidence absent")
    return value


def context(blocks, index, *, radius=2):
    """Exact neighboring text and citations. Never labels a warning sufficient."""
    need(type(blocks) is list and type(index) is int
         and 0 <= index < len(blocks) and type(radius) is int
         and 1 <= radius <= 8, "invalid reading-order neighborhood")
    result = []
    for pos in range(max(0, index-radius), min(len(blocks), index+radius+1)):
        if pos == index:
            continue
        b = blocks[pos]
        result.append({
            "signed_block_distance_NOT_SUPPORT": pos-index,
            "block_id": b["block_id"],
            "original_DOM_text_sha256": b["DOM_text_sha256"],
            "full_neighbor_text_NOT_SAFETY_VERIFIED":
                b["unabridged_DOM_text_NOT_REVIEWED"],
            "all_neighbor_citations_NOT_CLAIM_SUPPORT": deepcopy(citations(b))})
    return result


def nearest_cited(blocks, index, direction):
    """Nearest block with a citation; null is an explicit absence, not approval."""
    need(direction in (-1, 1) and type(index) is int
         and 0 <= index < len(blocks), "invalid nearest-citation search")
    for pos in range(index+direction, len(blocks) if direction == 1 else -1,
                     direction):
        b = blocks[pos]
        if citations(b):
            return {
                "signed_block_distance_NOT_EVIDENCE_OF_SUPPORT": pos-index,
                "block_id": b["block_id"],
                "original_DOM_text_sha256": b["DOM_text_sha256"],
                "full_cited_block_text_NOT_SAFETY_VERIFIED":
                    b["unabridged_DOM_text_NOT_REVIEWED"],
                "all_neighbor_citations_WITH_DISTINCT_SOURCE_ORIGINS_NOT_SUPPORT":
                    deepcopy(citations(b))}
    return None


def sealed(report):
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("issue") == 136
         and report.get("release_state") == "HOLD"
         and report.get("machine_only") is True
         and report.get("publication_clearance") is False
         and all(report.get(k) is False for k in HOLD_KEYS)
         and report.get("fingerprint_sha256") ==
             digest({k:v for k,v in report.items() if k != "fingerprint_sha256"}),
         "R79 custody seal or mandatory publication HOLD violated")


def construct(parent):
    """Independently rebuild R78 custody before deriving ANY review work order."""
    r78 = _r78()
    r78.sealed(parent)
    need(parent.get("schema") == PARENT and
         parent == r78.construct(parent["complete_R77_evidence_UNABRIDGED_NOT_APPROVED"]),
         "R78 source/citation/DOM provenance is not independently reproducible")
    c = parent["counts"]
    actual = tuple(c[k] for k in (
        "articles", "tools", "distinct_source_readings_retained",
        "citation_occurrences_retained", "source_variant_edges_retained",
        "unabridged_DOM_blocks_retained", "shared_URL_source_groups_retained",
        "reused_source_ID_groups_retained",
        "consequential_action_or_quantity_review_blocks",
        "consequential_blocks_without_same_block_citations"))
    need(actual == CENSUS and all(c[k] == 0 for k in
         ("human_source_link_checks", "human_claim_reviews",
          "qualified_safety_reviews", "independent_QD_approvals")),
         "R78 release candidate census or zero-human-review baseline drifted")
    docs = parent["document_review_packets_NOT_APPROVED"]
    need(len(docs) == 41, "complete 35 article + six tool inventory missing")
    work = []
    summaries = []
    seen = set()
    all_blocks, all_citations, all_edges, all_consequential = 0, 0, 0, 0
    for d in docs:
        kind, slug, route = d["kind"], d["slug"], d["private_draft_url"]
        blocks = d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"]
        order = d["original_DOM_block_ids_in_reading_order"]
        need([b["block_id"] for b in blocks] == order,
             "article reading depth or original block order changed")
        local_uncited = d["consequential_blocks_without_local_citations_TRIAGE_NOT_VERDICT"]
        need(type(local_uncited) is list and len(local_uncited) == len(set(local_uncited)),
             "duplicate or invalid consequential review queue")
        candidates = set(local_uncited)
        need(candidates <= set(order), "consequential block no longer in document")
        doc_count = 0
        source_scope = {(s["source_origin"], s["source_id"],
                         s["exact_URL_NOT_EQUIVALENCE"],
                         s["complete_source_reading_sha256"]) for s in
                         d["all_distinct_origin_scoped_sources_NOT_APPROVED"]}
        for pos,b in enumerate(blocks):
            need(type(b["unabridged_DOM_text_NOT_REVIEWED"]) is str
                 and hashlib.sha256(b["unabridged_DOM_text_NOT_REVIEWED"].encode(
                     "utf-8")).hexdigest() == b["DOM_text_sha256"],
                 "block text edited or detached from original source")
            all_blocks += 1
            own = citations(b)
            all_citations += len(own)
            for ci in own:
                variants = ci["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"]
                all_edges += len(variants)
                for v in variants:
                    need((v["source_origin"],v["source_id"],
                          v["exact_URL_NOT_CANONICALIZED"],
                          v["complete_source_reading_sha256"]) in source_scope,
                         "local citation origin lost or silently remapped")
            if b["consequential_action_or_quantity_LEXICAL_TRIAGE_ONLY"]:
                all_consequential += 1
            if b["block_id"] not in candidates:
                continue
            key = (kind,slug,b["block_id"])
            need(key not in seen and
                 b["consequential_action_or_quantity_LEXICAL_TRIAGE_ONLY"] is True
                 and own == [] and
                 b["human_claim_support_review"] == REVIEW
                 and b["qualified_safety_review"] == REVIEW,
                 "consequential no-local-citation work order is not faithful")
            seen.add(key)
            left = nearest_cited(blocks,pos,-1)
            right = nearest_cited(blocks,pos,1)
            item = {
                "kind":kind, "slug":slug, "private_draft_url_NOT_PUBLISHED":route,
                "block_id":b["block_id"], "original_block_index_1_based":pos+1,
                "total_document_blocks":len(blocks),
                "original_R72_DOM_text_sha256":b["DOM_text_sha256"],
                "full_consequential_text_NOT_SAFETY_VERIFIED":
                    b["unabridged_DOM_text_NOT_REVIEWED"],
                "local_citations":[], "triage_category":
                    "CONSEQUENTIAL_LEXICAL_MATCH_WITHOUT_SAME_BLOCK_CITATION",
                "neighboring_blocks_WITH_FULL_TEXT_NOT_SAFETY_VERIFIED":
                    context(blocks,pos),
                "nearest_prior_cited_block_NOT_CLAIM_SUPPORT":left,
                "nearest_next_cited_block_NOT_CLAIM_SUPPORT":right,
                "human_claim_support_review":REVIEW,
                "qualified_safety_review":REVIEW,
                "independent_QD_review":REVIEW}
            item["packet_sha256"] = digest(item)
            work.append(item)
            doc_count += 1
        need(set(local_uncited) == {w["block_id"] for w in work
             if (w["kind"],w["slug"]) == (kind,slug)},
             "uncited review task omitted or duplicated")
        summaries.append({
            "kind":kind,"slug":slug,"private_draft_url_NOT_PUBLISHED":route,
            "unabridged_DOM_blocks":len(blocks),
            "consequential_without_same_block_citation":doc_count,
            "citation_occurrences_NOT_CLAIM_PROOF":
                d["citation_occurrences_NOT_UNIQUE_CLAIMS"],
            "human_claim_support_review":REVIEW,
            "qualified_safety_review":REVIEW})
    need((all_blocks,all_citations,all_edges,all_consequential,len(work)) ==
         (4070,2173,2359,1068,347) and len(seen) == 347,
         "source/DOM/citation/action review inventory not conserved")
    need(sum(x["consequential_without_same_block_citation"] for x in summaries)
         == len(work), "document-to-review work queue disagreement")
    report = {
        "schema":SCHEMA,"issue":136,"release_state":"HOLD",
        "machine_only":True,"publication_clearance":False,
        "original_R78_fingerprint_sha256":parent["fingerprint_sha256"],
        "complete_R78_evidence_UNABRIDGED_NOT_APPROVED":deepcopy(parent),
        "review_orders_347_NOT_UNSUPPORTED_OR_UNSAFE_VERDICTS":work,
        "document_workload_overview_41_PRIVATE":summaries,
        "counts":{
            "articles":35,"tools":6,"source_readings_preserved":244,
            "citation_occurrences_preserved":all_citations,
            "origin_scoped_source_variant_edges_preserved":all_edges,
            "original_DOM_blocks_preserved":all_blocks,
            "shared_URL_groups_unresolved":32,"reused_ID_groups_unresolved":15,
            "consequential_lexical_review_blocks":all_consequential,
            "consequential_without_same_block_citation_review_orders":len(work),
            "human_link_checks":0,"human_claim_support_reviews":0,
            "qualified_safety_reviews":0,"independent_QD_approvals":0},
        "limitations":(
            "Lexical matching creates candidates, not established unsupported "
            "claims, medical findings or unsafe advice. Citation proximity and "
            "neighbor text can neither verify claim support nor clear a warning. "
            "Current live links, historical branch parity, qualified emergency "
            "review, actual WordPress/browser/assistive QA, human decisions and "
            "independent QD are required; all release gates remain HOLD."),
        **{k:False for k in HOLD_KEYS}}
    report["fingerprint_sha256"] = digest(report)
    sealed(report)
    return report


def verify(report):
    """Fast fail on unsafe forged packets; then independently reconstruct evidence.

    Early checks save the expensive re-derivation for legitimate sealed inputs.
    An attacker can re-seal a forged report, so the FULL independently derived
    comparison remains mandatory after every cheap check passes.
    """
    sealed(report)
    work = report.get("review_orders_347_NOT_UNSUPPORTED_OR_UNSAFE_VERDICTS")
    need(type(work) is list and len(work) == 347,
         "R79 review-order inventory omitted or expanded")
    for item in work:
        need(type(item) is dict and
             item.get("human_claim_support_review") == REVIEW and
             item.get("qualified_safety_review") == REVIEW and
             item.get("independent_QD_review") == REVIEW and
             item.get("packet_sha256") ==
                 digest({k:v for k,v in item.items() if k != "packet_sha256"}),
             "R79 original review work order or mandatory HOLD state forged")
    parent = report.get("complete_R78_evidence_UNABRIDGED_NOT_APPROVED")
    need(type(parent) is dict and report.get("original_R78_fingerprint_sha256") ==
         parent.get("fingerprint_sha256") and construct(parent) == report,
         "R79 derived review orders differ from conserved R78 evidence")


def _csv_safe(value):
    value = str(value)
    trimmed = value.lstrip(" \t\r\n\ufeff\u200b\u2060\u200e\u200f")
    return "'" + value if (value[:1] in ("\t","\r","\n","\ufeff",
            "\u200b","\u2060","\u200e","\u200f")
            or trimmed.startswith(("=","+","-","@"))) else value


def csv_private_queue(report):
    """One-way private CSV. Never accepts or applies reviewer decisions."""
    verify(report)
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow((
        "private_draft_url_NOT_PUBLISHED", "kind", "slug", "block_id",
        "original_block_index_1_based", "full_consequential_text_NOT_VERDICT",
        "prior_citation_distance_NOT_SUPPORT", "next_citation_distance_NOT_SUPPORT",
        "human_claim_support_review", "qualified_safety_review", "reviewer_notes_UNTRUSTED"))
    for t in report["review_orders_347_NOT_UNSUPPORTED_OR_UNSAFE_VERDICTS"]:
        left=t["nearest_prior_cited_block_NOT_CLAIM_SUPPORT"]
        right=t["nearest_next_cited_block_NOT_CLAIM_SUPPORT"]
        writer.writerow([_csv_safe(x) for x in (
            t["private_draft_url_NOT_PUBLISHED"],t["kind"],t["slug"],
            t["block_id"],t["original_block_index_1_based"],
            t["full_consequential_text_NOT_SAFETY_VERIFIED"],
            left["signed_block_distance_NOT_EVIDENCE_OF_SUPPORT"] if left else "",
            right["signed_block_distance_NOT_EVIDENCE_OF_SUPPORT"] if right else "",
            REVIEW,REVIEW,"")])
    return out.getvalue()


def live_report(repo_root=None):
    return construct(_r78().live_report(repo_root))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root",type=Path)
    parser.add_argument("--private-review-csv-stdout",action="store_true")
    args=parser.parse_args(argv)
    try:
        report=live_report(args.repo_root)
        if args.private_review_csv_stdout:
            sys.stdout.write(csv_private_queue(report))
        else:
            print(json.dumps({"schema":SCHEMA,"release_state":"HOLD",
                "fingerprint_sha256":report["fingerprint_sha256"],
                "counts":report["counts"],"publication_clearance":False},
                sort_keys=True))
        return 0
    except (Hold,ValueError,KeyError,TypeError,AttributeError,OSError,
            IndexError) as exc:
        print("R79 PRIVATE RELEASE HOLD: "+str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
