#!/usr/bin/env python3
"""R78 PRIVATE/HOLD — document-first source/citation/qualifier custody review.

Read-only machine inventory. A citation is not evidence of claim support;
lexical matches are not medical/safety findings. Never imports approvals,
publishes content, or mutates WordPress, source records or contributor work.
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
from urllib.parse import unquote

SCHEMA = "r78-document-citation-source-review-hold-v1"
PARENT = "r77-temporal-source-provenance-and-impact-hold-v1"
CENSUS = (35, 6, 244, 2173, 2359, 4070, 32, 15)
REVIEW = "NOT_REVIEWED"
HOLD_KEYS = ("may_publish", "independent_QD_approval",
             "qualified_safety_clearance", "human_source_links_verified")


class Hold(ValueError):
    """Fail closed on changed evidence, provenance or release state."""


def need(condition, reason):
    if not condition:
        raise Hold(reason)


def digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False).encode("utf-8")).hexdigest()


def _r77():
    path = Path(__file__).with_name("r77_temporal_evidence_custody.py")
    need(path.is_file() and not path.is_symlink(), "R77 parent tool unavailable")
    spec = importlib.util.spec_from_file_location("r78_r77_parent", path)
    need(spec is not None and spec.loader is not None,
         "R77 parent tool is unreadable")
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def route_compare_key(path):
    """Review-only possible WordPress route collision; NEVER resolve a redirect."""
    need(type(path) is str and path.startswith("/preparedness/")
         and "?" not in path and "#" not in path and "\\"
         not in path and not any(ord(c) < 32 for c in path),
         "invalid private draft route")
    normalized = unquote(path).casefold().rstrip("/") + "/"
    need(normalized.startswith("/preparedness/")
         and "//" not in normalized and "/../" not in normalized
         and "/./" not in normalized, "unsafe or ambiguous private route")
    return normalized


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
         "R78 document review not sealed or falsely approved")


def construct(parent, *, expected=CENSUS):
    need(type(expected) is tuple and len(expected) == 8
         and all(type(v) is int and v > 0 for v in expected),
         "expected baseline must be eight positive integers")
    r77 = _r77()
    r77.sealed(parent)
    need(parent.get("schema") == PARENT, "wrong parent evidence schema")
    p = parent.get("complete_R76_evidence_UNABRIDGED_NOT_APPROVED")
    need(type(p) is dict, "R76 complete evidence missing")
    r77._r76().sealed(p)
    c = parent.get("counts")
    need(type(c) is dict and tuple(c.get(k) for k in (
         "articles", "tools", "source_readings_preserved",
         "citation_occurrences_preserved",
         "citation_source_variant_edges_preserved",
         "unabridged_DOM_blocks_preserved",
         "shared_URL_groups_preserved",
         "reused_ID_groups_preserved")) == expected,
         "seven-cluster/35-article/citation provenance census changed")
    need(all(c.get(k) == 0 for k in (
         "human_link_checks", "human_claim_support_reviews",
         "qualified_safety_reviews", "independent_QD_approvals")),
         "parent claims nonexistent human reviews")
    docs = p.get("all_document_block_orders_NOT_REVIEWED")
    blocks = p.get("all_4070_unabridged_DOM_tasks_NOT_REVIEWED")
    citations = p.get("every_attached_citation_crosswalk_NOT_SOURCE_SUPPORT_PROOF")
    queue = p.get("original_R75_action_quantity_qualifier_queue_NOT_APPROVED")
    sources = parent.get("all_origin_scoped_temporal_review_packets_NOT_APPROVED")
    need(type(docs) is list and len(docs) == expected[0] + expected[1]
         and type(blocks) is list and len(blocks) == expected[5]
         and type(citations) is list and len(citations) == expected[3]
         and type(queue) is list and type(sources) is list
         and len(sources) == expected[2],
         "complete document, block, citation or source evidence missing")
    src = {}
    for item in sources:
        key = (item.get("source_origin"), item.get("source_id"))
        need(all(type(s) is str and s for s in key)
             and key not in src and
             item.get("human_claim_support_review") == REVIEW and
             item.get("qualified_safety_review") == REVIEW and
             item.get("human_link_check") is False and
             type(item.get("complete_candidate_reading_sha256")) is str and
             type(item.get("literal_temporal_review_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT")) is list,
             "temporal source identity or human approval forged")
        src[key] = item
    block_by_doc = defaultdict(dict)
    for item in blocks:
        key = (item.get("kind"), item.get("slug"))
        bid = item.get("block_id")
        text = item.get("DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED")
        need(type(bid) is str and bid and bid not in block_by_doc[key]
             and type(text) is str and text.strip() and
             item.get("DOM_text_sha256") ==
                 hashlib.sha256(text.encode("utf-8")).hexdigest()
             and item.get("task_sha256") ==
                 digest({k: v for k, v in item.items() if k != "task_sha256"})
             and all(item.get(k) == REVIEW for k in (
                 "human_claim_support_review", "qualified_safety_review",
                 "independent_QD_review")),
             "block content, provenance or HOLD state changed")
        block_by_doc[key][bid] = item
    citation_by_block = defaultdict(list)
    ordinals_by_doc = defaultdict(set)
    variant_edges = 0
    for item in citations:
        key = (item.get("kind"), item.get("slug"))
        bid = item.get("block_id")
        ordinal = item.get("citation_ordinal")
        need(type(ordinal) is int and ordinal > 0 and
             ordinal not in ordinals_by_doc[key] and
             item.get("human_claim_support_review") == REVIEW and
             item.get("qualified_safety_review") == REVIEW and
             item.get("packet_sha256") ==
                 digest({k: v for k, v in item.items() if k != "packet_sha256"}) and
             bid in block_by_doc[key],
             "citation occurrence duplicated, unattached or falsely reviewed")
        ordinals_by_doc[key].add(ordinal)
        variants = item.get("source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT")
        need(type(variants) is list and variants,
             "citation source variants omitted")
        variant_keys = set()
        for v in variants:
            vk = (v.get("source_origin"), v.get("source_id"))
            s = src.get(vk)
            need(s is not None and vk not in variant_keys
                 and vk[1] == item.get("raw_source_id")
                 and s["exact_URL_NO_ALIAS"] ==
                     v.get("exact_URL_NOT_CANONICALIZED")
                 and s["complete_candidate_reading_sha256"] ==
                     v.get("complete_source_reading_sha256"),
                 "citation variant misattributed, aliased or collapsed")
            variant_keys.add(vk)
            variant_edges += 1
        citation_by_block[(key[0], key[1], bid)].append(item)
    need(variant_edges == expected[4],
         "distinct source-to-citation-variant edge count changed")
    for key, nums in ordinals_by_doc.items():
        need(nums == set(range(1, len(nums) + 1)),
             "citation ordinals changed inside document")
    queue_ids = set()
    for item in queue:
        key = (item.get("kind"), item.get("slug"), item.get("block_id"))
        need(key not in queue_ids and
             key[2] in block_by_doc[key[:2]] and
             item.get("human_claim_support_review") == REVIEW and
             item.get("qualified_safety_review") == REVIEW,
             "action/quantity human-review queue changed")
        queue_ids.add(key)
    packets = []
    route_keys = defaultdict(list)
    seen_docs = set()
    seen_blocks = set()
    seen_citations = set()
    for doc in docs:
        key = (doc.get("kind"), doc.get("slug"))
        order = doc.get("block_ids_in_original_order")
        route = doc.get("draft_url_NOT_PUBLIC")
        need(key[0] in ("article", "tool") and type(key[1]) is str
             and key[1] and key not in seen_docs and
             doc.get("reviewer_state") == REVIEW and
             type(order) is list and len(order) == len(set(order))
             and set(order) == set(block_by_doc[key]),
             "draft document/DOM reading order lost or changed")
        seen_docs.add(key)
        route_keys[route_compare_key(route)].append(route)
        local = []
        used_sources = set()
        for bid in order:
            original = block_by_doc[key][bid]
            bkey = (*key, bid)
            seen_blocks.add(bkey)
            local_citations = original.get(
                "local_citations_NOT_CLAIM_SUPPORT_PROOF")
            need(type(local_citations) is list and
                 len(local_citations) == len(citation_by_block[bkey]),
                 "local citation context lost")
            raw_occurrences = sorted(local_citations, key=lambda x:x["ordinal"])
            mapped = sorted(citation_by_block[bkey],
                            key=lambda x:x["citation_ordinal"])
            need([x["ordinal"] for x in raw_occurrences] ==
                 [x["citation_ordinal"] for x in mapped] and
                 all(raw["source_id"] == packet["raw_source_id"]
                     for raw, packet in zip(raw_occurrences, mapped)),
                 "source-to-passage citation drift")
            for x in mapped:
                seen_citations.add((key[0], key[1], x["citation_ordinal"]))
                for v in x["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"]:
                    used_sources.add((v["source_origin"], v["source_id"]))
            text = original["DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"]
            local.append({
                "block_id": bid, "original_R72_task_sha256":original["task_sha256"],
                "unabridged_DOM_text_NOT_REVIEWED": text,
                "DOM_text_sha256": original["DOM_text_sha256"],
                "citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF":
                    deepcopy(mapped),
                "consequential_action_or_quantity_LEXICAL_TRIAGE_ONLY":
                    bkey in queue_ids,
                "human_claim_support_review": REVIEW,
                "qualified_safety_review": REVIEW})
        scoped = []
        for sk in sorted(used_sources):
            s = src[sk]
            scoped.append({
                "source_origin": sk[0], "source_id": sk[1],
                "exact_URL_NOT_EQUIVALENCE":s["exact_URL_NO_ALIAS"],
                "complete_source_reading_sha256":
                    s["complete_candidate_reading_sha256"],
                "temporal_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT":
                    deepcopy(s["literal_temporal_review_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT"]),
                "human_link_check": False, "human_claim_support_review": REVIEW,
                "qualified_safety_review": REVIEW})
        need(doc.get("origin_scoped_sources_USED_NOT_SUPPORT_APPROVED") ==
             [list(x) for x in sorted(used_sources)],
             "document-scoped source origins lost or merged")
        packet = {
            "kind":key[0], "slug":key[1], "private_draft_url":route,
            "original_DOM_block_ids_in_reading_order":deepcopy(order),
            "all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED":local,
            "all_distinct_origin_scoped_sources_NOT_APPROVED":scoped,
            "citation_occurrences_NOT_UNIQUE_CLAIMS":
                sum(len(b["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"])
                    for b in local),
            "source_variant_edges_NOT_CLAIMS":
                sum(len(c["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"])
                    for b in local for c in
                    b["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"]),
            "consequential_blocks_without_local_citations_TRIAGE_NOT_VERDICT":
                [b["block_id"] for b in local
                 if b["consequential_action_or_quantity_LEXICAL_TRIAGE_ONLY"]
                 and not b["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"]],
            "human_claim_support_review": REVIEW,
            "qualified_safety_review": REVIEW, "independent_QD_review": REVIEW}
        packet["packet_sha256"] = digest(packet)
        packets.append(packet)
    need(len(seen_docs) == expected[0] + expected[1]
         and len(seen_blocks) == expected[5]
         and len(seen_citations) == expected[3]
         and len(queue_ids) == 1068,
         "document, DOM, citation or consequential review inventory changed")
    # All potential route alias groups remain explicit. Never silently redirect.
    alias_review = []
    for normalized, raw in sorted(route_keys.items()):
        if len(raw) > 1:
            alias_review.append({
                "normalized_route_REVIEW_ONLY":normalized,
                "distinct_original_routes_NOT_MERGED":sorted(raw),
                "human_url_scope_review":REVIEW})
    need(not alias_review,
         "potential draft WordPress route alias/case/percent-encoding collision")
    result = {
        "schema":SCHEMA, "issue":136, "release_state":"HOLD",
        "machine_only":True, "publication_clearance":False,
        "original_R77_fingerprint_sha256":parent["fingerprint_sha256"],
        "complete_R77_evidence_UNABRIDGED_NOT_APPROVED":deepcopy(parent),
        "document_review_packets_NOT_APPROVED":packets,
        "route_alias_collision_review_NOT_RESOLVED":alias_review,
        "counts":{
            "articles":expected[0], "tools":expected[1],
            "distinct_source_readings_retained":expected[2],
            "citation_occurrences_retained":len(seen_citations),
            "source_variant_edges_retained":variant_edges,
            "unabridged_DOM_blocks_retained":len(seen_blocks),
            "shared_URL_source_groups_retained":expected[6],
            "reused_source_ID_groups_retained":expected[7],
            "consequential_action_or_quantity_review_blocks":len(queue_ids),
            "consequential_blocks_without_same_block_citations":
                sum(len(p["consequential_blocks_without_local_citations_TRIAGE_NOT_VERDICT"])
                    for p in packets),
            "human_source_link_checks":0, "human_claim_reviews":0,
            "qualified_safety_reviews":0, "independent_QD_approvals":0},
        "limitations":(
            "A private document-first editorial crosswalk, NOT proof that any "
            "source substantiates a claim or that an emergency procedure is safe. "
            "Lexical action and quantity detection is fallible. Duplicate exact "
            "source URLs, different research origins, complete historical readings "
            "and unreviewed approvals remain separate in the sealed parent. "
            "No publication, clinical recommendation, CMS write or human review. "
            "Independent QD, expert safety review, live-source checks, actual "
            "WordPress/browser testing and mandatory integrity remain required."),
        **{k:False for k in HOLD_KEYS}}
    result["fingerprint_sha256"] = digest(result)
    sealed(result)
    return result


def csv_private_document_queue(report):
    """One-way formula-neutralized reviewer routing: NEVER an approval importer."""
    sealed(report)
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow((
        "private_draft_url_NOT_PUBLISHED", "kind", "slug", "DOM_blocks",
        "citation_occurrences_NOT_CLAIM_PROOF",
        "source_variant_edges_NOT_UNIQUE_CLAIMS",
        "distinct_source_origins_NOT_ALIASED",
        "consequential_blocks_without_local_citations_NOT_VERDICT",
        "human_claim_support_review", "qualified_safety_review",
        "reviewer_notes_UNTRUSTED"))
    def safe(value):
        value = str(value)
        prefix = value.lstrip(" \t\r\n\ufeff\u200b\u2060\u200e\u200f")
        return "'" + value if (
            value[:1] in ("\t", "\r", "\n", "\ufeff", "\u200b",
                          "\u2060", "\u200e", "\u200f") or
            prefix.startswith(("=", "+", "-", "@"))) else value
    for p in report["document_review_packets_NOT_APPROVED"]:
        writer.writerow([safe(v) for v in (
            p["private_draft_url"],p["kind"],p["slug"],
            len(p["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"]),
            p["citation_occurrences_NOT_UNIQUE_CLAIMS"],
            p["source_variant_edges_NOT_CLAIMS"],
            len(p["all_distinct_origin_scoped_sources_NOT_APPROVED"]),
            len(p["consequential_blocks_without_local_citations_TRIAGE_NOT_VERDICT"]),
            REVIEW,REVIEW,"")])
    return output.getvalue()


def live_report(repo_root=None):
    original = _r77().live_report(repo_root)
    report = construct(original)
    need(report == construct(original),
         "R78 report is not deterministic")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root",type=Path)
    parser.add_argument("--private-review-csv-stdout",action="store_true")
    args = parser.parse_args(argv)
    try:
        report = live_report(args.repo_root)
        if args.private_review_csv_stdout:
            sys.stdout.write(csv_private_document_queue(report))
        else:
            print(json.dumps({"schema":SCHEMA,"release_state":"HOLD",
                "fingerprint_sha256":report["fingerprint_sha256"],
                "counts":report["counts"],"publication_clearance":False},
                sort_keys=True))
        return 0
    except (Hold,ValueError,KeyError,TypeError,AttributeError,OSError) as exc:
        print("R78 PRIVATE RELEASE HOLD: "+str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
