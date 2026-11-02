#!/usr/bin/env python3
"""R76 private HOLD: origin-scoped citation blast-radius × consequential review crosswalk.

This tool produces *navigation*, not claim support, quantitative risk, editorial
approval, or medical/safety advice. No writes to source data, CMS or public site.
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

SCHEMA = "r76-private-source-consequential-impact-crosswalk-v1"
PARENT = "r75-private-qualifier-scope-citation-custody-v1"
EXPECTED = (35, 6, 244, 2173, 4070)
REVIEW = "NOT_REVIEWED"
HOLD_KEYS = ("may_publish", "independent_QD_approval",
             "qualified_safety_clearance", "human_source_links_verified")


class Hold(ValueError):
    """Source custody or publication-state violation."""


def need(condition, reason):
    if not condition:
        raise Hold(reason)


def digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False).encode("utf-8")).hexdigest()


def _r75():
    path = Path(__file__).with_name("r75_qualifier_scope_citation_custody.py")
    need(path.is_file() and not path.is_symlink(), "R75 upstream evidence tool missing")
    spec = importlib.util.spec_from_file_location("r76_r75_parent", path)
    need(spec is not None and spec.loader is not None, "cannot load R75")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sealed(report):
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("issue") == 136 and report.get("release_state") == "HOLD"
         and report.get("machine_only") is True
         and all(report.get(k) is False for k in HOLD_KEYS)
         and report.get("fingerprint_sha256") ==
             digest({k:v for k,v in report.items() if k != "fingerprint_sha256"}),
         "R76 report not sealed or release HOLD altered")


def construct(parent, *, expected=EXPECTED):
    need(type(expected) is tuple and len(expected) == 5
         and all(type(n) is int and n > 0 for n in expected),
         "expected original evidence census malformed")
    r75 = _r75()
    r75.sealed(parent, PARENT)
    counts = parent.get("counts")
    need(type(counts) is dict
         and tuple(counts.get(k) for k in (
             "articles", "tools", "complete_origin_scoped_source_readings",
             "citation_occurrences", "unabridged_DOM_blocks")) == expected
         and all(counts.get(k) == 0 for k in (
             "human_claim_support_reviews", "qualified_safety_reviews",
             "independent_QD_approvals")),
         "upstream document/source/citation census or approvals changed")
    sources = parent.get("all_244_unabridged_source_readings_NOT_REVIEWED")
    blocks = parent.get("all_4070_unabridged_DOM_tasks_NOT_REVIEWED")
    docs = parent.get("all_document_block_orders_NOT_REVIEWED")
    review = parent.get("action_or_quantity_qualifier_context_queue_NOT_APPROVED")
    collision_urls = parent.get("shared_URL_scope_collisions_NOT_REVIEWED")
    collision_ids = parent.get("reused_ID_scope_collisions_NOT_REVIEWED")
    uncited = parent.get("uncited_source_readings_NOT_REVIEWED")
    unattached = parent.get("citations_without_DOM_block_UNRESOLVED")
    need(type(sources) is list and len(sources) == expected[2]
         and type(blocks) is list and len(blocks) == expected[4]
         and type(docs) is list and len(docs) == expected[0] + expected[1]
         and type(review) is list
         and len(review) == counts.get("union_action_or_quantity_review_queue")
         and all(type(x) is list for x in
                 (collision_urls, collision_ids, uncited, unattached)),
         "source, DOM, queue or collision evidence lost")

    source_index = {}
    url_to_keys, id_to_keys = defaultdict(list), defaultdict(list)
    for record in sources:
        need(type(record) is dict, "source record not object")
        key = (record.get("source_origin"), record.get("source_id"))
        reading = record.get("candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        need(all(type(k) is str and k for k in key)
             and key not in source_index and type(reading) is dict
             and reading.get("id") == key[1]
             and reading.get("human_link_check") is False
             and type(reading.get("url")) is str and reading["url"]
             and reading["url"] == record.get("exact_URL_NO_ALIAS")
             and record.get("candidate_reading_sha256") == digest(reading)
             and record.get("human_source_and_claim_review") == REVIEW
             and record.get("qualified_safety_review") == REVIEW,
             "origin-scoped source reading, URL or human-review state changed")
        historical = record.get("original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        need((historical is None and record.get("original_reading_sha256") is None)
             or (type(historical) is dict and digest(historical) ==
                 record.get("original_reading_sha256")),
             "historical research reading truncated or modified")
        source_index[key] = record
        url_to_keys[reading["url"]].append(key)
        id_to_keys[key[1]].append(key)
    need(list(source_index) == sorted(source_index),
         "original complete source-reading order lost")
    need(sum(len(keys)>1 for keys in url_to_keys.values()) == len(collision_urls)
         and sum(len(keys)>1 for keys in id_to_keys.values()) == len(collision_ids),
         "exact shared-URL or ID collision groups lost")

    doc_index = {}
    all_routes = set()
    for record in docs:
        need(type(record) is dict and record.get("reviewer_state") == REVIEW,
             "draft document falsely reviewed")
        key = (record.get("kind"), record.get("slug"))
        route = record.get("draft_url_NOT_PUBLIC")
        order = record.get("block_ids_in_original_order")
        need(key[0] in ("article", "tool") and type(key[1]) is str
             and key[1] and key not in doc_index and type(route) is str
             and route.startswith("/preparedness/") and "//" not in route
             and ".." not in route and route not in all_routes
             and type(order) is list and order and len(order) == len(set(order)),
             "duplicate draft URL, lost document or invalid DOM ordering")
        all_routes.add(route)
        doc_index[key] = record
    need(sum(k[0] == "article" for k in doc_index) == expected[0]
         and sum(k[0] == "tool" for k in doc_index) == expected[1],
         "document slate changed")

    blocks_index = {}
    seen_orders = defaultdict(list)
    for block in blocks:
        need(type(block) is dict and block.get("task_sha256") ==
             digest({k:v for k,v in block.items() if k != "task_sha256"}),
             "original R72 block custody hash mismatch")
        key = (block.get("kind"), block.get("slug"), block.get("block_id"))
        doc = doc_index.get(key[:2])
        body = block.get("DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED")
        need(doc is not None and type(key[2]) is str and key[2]
             and key not in blocks_index and key[2] in doc["block_ids_in_original_order"]
             and block.get("private_draft_url") == doc["draft_url_NOT_PUBLIC"]
             and type(body) is str and body.strip()
             and block.get("DOM_text_sha256") ==
                 hashlib.sha256(body.encode("utf-8")).hexdigest()
             and all(block.get(k) == REVIEW for k in (
                 "human_claim_support_review", "qualified_safety_review",
                 "independent_QD_review")),
             "complete block text, URL, origin or safety state altered")
        blocks_index[key] = block
        seen_orders[key[:2]].append(key[2])
    need(all(seen_orders[k] == doc["block_ids_in_original_order"]
             for k,doc in doc_index.items()), "DOM block order changed")

    # Keep R75's action/quantity queue categorization tethered to the independently
    # preserved R73/R74 packets; neither label can be forged by re-sealing R75.
    old_actions = parent.get("all_975_action_triage_packets_NOT_APPROVED")
    old_quantities = parent.get("all_numeric_unit_packets_NOT_APPROVED")
    need(type(old_actions) is list and type(old_quantities) is list,
         "historical action or numeric packets missing")
    action_keys = {(x.get("kind"),x.get("slug"),x.get("block_id"))
                   for x in old_actions if type(x) is dict}
    quantity_keys = {(x.get("kind"),x.get("slug"),x.get("block_id"))
                     for x in old_quantities if type(x) is dict}
    need(len(action_keys) == len(old_actions)
         and len(quantity_keys) == len(old_quantities),
         "duplicated or malformed original action/quantity task")
    review_index = {}
    for item in review:
        need(type(item) is dict and item.get("packet_sha256") ==
             digest({k:v for k,v in item.items() if k != "packet_sha256"}),
             "R75 reviewer packet tampered")
        key = (item.get("kind"), item.get("slug"), item.get("block_id"))
        block = blocks_index.get(key)
        need(block is not None and key not in review_index
             and item.get("original_R72_block_sha256") == block["task_sha256"]
             and item.get("full_DOM_text_UNABRIDGED_NOT_SAFETY_APPROVED") ==
                 block["DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"]
             and item.get("source_citations_NOT_CLAIM_SUPPORT") ==
                 block.get("local_citations_NOT_CLAIM_SUPPORT_PROOF")
             and item.get("same_block_qualifiers_NOT_SAFETY_PROOF") ==
                 r75.qualifier_spans(block[
                     "DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"])
             and type(item.get("action_language_TRIAGE_NOT_VERDICT")) is bool
             and type(item.get("numeric_units_TRIAGE_NOT_DOSAGE_CHECK")) is bool
             and item["action_language_TRIAGE_NOT_VERDICT"] == (key in action_keys)
             and item["numeric_units_TRIAGE_NOT_DOSAGE_CHECK"] == (key in quantity_keys)
             and (item["action_language_TRIAGE_NOT_VERDICT"]
                  or item["numeric_units_TRIAGE_NOT_DOSAGE_CHECK"])
             and all(item.get(k) == REVIEW for k in (
                 "human_claim_support_review", "qualified_safety_review",
                 "independent_QD_review")),
             "action/quantity review source, qualifier, or HOLD binding changed")
        review_index[key] = item
    need(set(review_index) == action_keys | quantity_keys,
         "action or numeric source review task omitted or invented")

    citation_index = []
    source_edges = defaultdict(list)
    total_keys = set()
    no_local_review = []
    for key, block in blocks_index.items():
        citations = block.get("local_citations_NOT_CLAIM_SUPPORT_PROOF")
        need(type(citations) is list, "missing citation-in-block evidence")
        consequential = key in review_index
        if consequential and not citations:
            no_local_review.append({
                "kind": key[0], "slug": key[1], "block_id": key[2],
                "original_R72_block_sha256": block["task_sha256"],
                "full_DOM_text_UNABRIDGED_NOT_SAFETY_APPROVED":
                    block["DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"],
                "review_category": "CONSEQUENTIAL_BLOCK_WITHOUT_LOCAL_CITATION",
                "human_claim_support_review": REVIEW,
                "qualified_safety_review": REVIEW})
        for edge in citations:
            need(type(edge) is dict and type(edge.get("ordinal")) is int
                 and edge["ordinal"] > 0 and type(edge.get("source_id")) is str
                 and edge.get("human_claim_support_review") == REVIEW,
                 "citation ordinal or review state invalid")
            ekey = (key[0], key[1], edge["ordinal"])
            need(ekey not in total_keys, "citation occurrence duplicated")
            total_keys.add(ekey)
            variants = edge.get("origin_scoped_source_variants_NOT_ALIASED")
            need(type(variants) is list and variants, "missing citation variants")
            kept, used = [], set()
            for v in variants:
                need(type(v) is dict, "citation source variant malformed")
                sk = (v.get("source_origin"), v.get("source_id"))
                source = source_index.get(sk)
                need(source is not None and sk not in used and sk[1] == edge["source_id"]
                     and v.get("exact_URL_NOT_ALIAS") == source["exact_URL_NO_ALIAS"]
                     and v.get("complete_source_reading_sha256") ==
                         source["candidate_reading_sha256"]
                     and v.get("human_source_and_claim_review") == REVIEW,
                     "citation variant collapsed, aliased or wrong source scope")
                used.add(sk)
                kept.append({
                    "source_origin":sk[0], "source_id":sk[1],
                    "exact_URL_NOT_CANONICALIZED":source["exact_URL_NO_ALIAS"],
                    "complete_source_reading_sha256":source["candidate_reading_sha256"]})
                source_edges[sk].append({
                    "kind":key[0], "slug":key[1], "block_id":key[2],
                    "citation_ordinal":edge["ordinal"],
                    "original_R72_block_sha256":block["task_sha256"],
                    "consequential_action_or_quantity_TRIAGE_NOT_VERDICT":consequential})
            need([(v["source_origin"],v["source_id"]) for v in kept] ==
                 sorted(used), "original citation variants reordered or lost")
            packet = {
                "kind":key[0], "slug":key[1], "block_id":key[2],
                "draft_URL_PRIVATE":doc_index[key[:2]]["draft_url_NOT_PUBLIC"],
                "citation_ordinal":edge["ordinal"], "raw_source_id":edge["source_id"],
                "original_R72_block_sha256":block["task_sha256"],
                "source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT":kept,
                "consequential_action_or_quantity_TRIAGE_NOT_VERDICT":consequential,
                "human_claim_support_review":REVIEW, "qualified_safety_review":REVIEW}
            packet["packet_sha256"] = digest(packet)
            citation_index.append(packet)
    for row in unattached:
        need(type(row) is dict and row.get("review_state") == REVIEW
             and row.get("kind") in ("article","tool")
             and (row.get("kind"),row.get("slug")) in doc_index
             and type(row.get("citation_ordinal")) is int
             and row["citation_ordinal"] > 0
             and type(row.get("source_id")) is str and row["source_id"],
             "unattached citation review silently closed")
        ek = (row["kind"],row["slug"],row["citation_ordinal"])
        need(ek not in total_keys, "unattached citation silently double-counted")
        total_keys.add(ek)
    need(len(total_keys) == expected[3], "citations lost or added")
    # Rebuild uncited inventory independently; historical uncited research is NOT deleted.
    need([list(sk) for sk in sorted(set(source_index)-set(source_edges))] == uncited,
         "uncited complete research reading dropped or made into a phantom citation")
    # Recompute complete collision groups and document-source assignments from
    # individual occurrence edges rather than trusting source IDs or cached lists.
    def crosschecked_collision(mapping, category):
        rebuilt = []
        for value, keys in sorted(mapping.items()):
            if len(keys) < 2:
                continue
            rows = []
            for sk in sorted(keys):
                source = source_index[sk]
                downstream = sorted([[
                    edge["kind"],edge["slug"],edge["block_id"],
                    edge["citation_ordinal"]] for edge in source_edges[sk]])
                rows.append({
                    "origin":sk[0], "id":sk[1],
                    "full_candidate_reading_sha256":source["candidate_reading_sha256"],
                    "exact_URL_NOT_CANONICALIZED":source["exact_URL_NO_ALIAS"],
                    "downstream_block_citation_edges_NOT_SUPPORT":downstream,
                    "human_scope_and_claim_review":REVIEW})
            rebuilt.append({
                "collision_type_NOT_AUTOMATIC_ERROR":category,
                "value":value, "source_readings_NOT_MERGED":rows,
                "human_scope_resolution":REVIEW})
        return rebuilt
    need(collision_urls == crosschecked_collision(url_to_keys,
         "SHARED_EXACT_URL_NOT_SOURCE_EQUIVALENCE")
         and collision_ids == crosschecked_collision(id_to_keys,
         "SAME_ID_DIFFERENT_RESEARCH_ORIGINS"),
         "cross-reconstructed duplicate URL/ID source readings or citation impact mismatch")
    for dkey, doc in doc_index.items():
        expected_scopes = sorted(sk for sk, edges in source_edges.items()
                               if any((e["kind"],e["slug"]) == dkey for e in edges))
        need(doc.get("origin_scoped_sources_USED_NOT_SUPPORT_APPROVED") ==
             [list(sk) for sk in expected_scopes],
             "document source scopes changed, including duplicate-ID origin variants")
    by_doc_ordinals = defaultdict(list)
    for kind,slug,ordinal in total_keys:
        by_doc_ordinals[(kind,slug)].append(ordinal)
    for dkey, seq in by_doc_ordinals.items():
        # All R72 citation ordinals are 1-based, sequential inside each document.
        need(sorted(seq) == list(range(1,len(seq)+1)),
             "citation ordinal gap/substitution in document evidence")
    citation_index.sort(key=lambda p:(
        p["kind"],p["slug"],p["citation_ordinal"]))

    source_packets = []
    for sk in sorted(source_index):
        source = source_index[sk]
        edges = sorted(source_edges[sk],key=lambda e:(
            e["kind"],e["slug"],e["citation_ordinal"],e["block_id"]))
        cited_docs = sorted({(e["kind"],e["slug"]) for e in edges})
        consequential = [e for e in edges
                         if e["consequential_action_or_quantity_TRIAGE_NOT_VERDICT"]]
        row = {
            "source_origin":sk[0], "source_id":sk[1],
            "exact_URL_NOT_CANONICALIZED":source["exact_URL_NO_ALIAS"],
            "complete_source_reading_sha256":source["candidate_reading_sha256"],
            "shared_exact_URL_REQUIRES_SCOPE_REVIEW":
                len(url_to_keys[source["exact_URL_NO_ALIAS"]])>1,
            "reused_source_ID_REQUIRES_SCOPE_REVIEW":len(id_to_keys[sk[1]])>1,
            "citation_variant_edges_NOT_UNIQUE_CLAIMS":edges,
            "distinct_documents_citing_source_NOT_VERIFIED":
                [list(d) for d in cited_docs],
            "consequential_citation_variant_edges_NOT_VERDICT":len(consequential),
            "all_citation_variant_edges_NOT_VERDICT":len(edges),
            "human_link_check":False, "human_source_and_claim_review":REVIEW,
            "qualified_safety_review":REVIEW}
        row["packet_sha256"] = digest(row)
        source_packets.append(row)
    # Deterministic work order only; "priority" means count of review touchpoints.
    prioritized = sorted(source_packets,key=lambda p:(
        -p["consequential_citation_variant_edges_NOT_VERDICT"],
        -len(p["distinct_documents_citing_source_NOT_VERIFIED"]),
        -p["all_citation_variant_edges_NOT_VERDICT"],
        p["source_origin"],p["source_id"]))

    result = {
        "schema":SCHEMA, "issue":136, "release_state":"HOLD",
        "machine_only":True, "original_R75_fingerprint_sha256":parent[
            "fingerprint_sha256"],
        "all_244_unabridged_source_readings_NOT_REVIEWED":deepcopy(sources),
        "all_4070_unabridged_DOM_tasks_NOT_REVIEWED":deepcopy(blocks),
        "all_document_block_orders_NOT_REVIEWED":deepcopy(docs),
        "original_R75_action_quantity_qualifier_queue_NOT_APPROVED":deepcopy(review),
        "shared_URL_scope_collisions_NOT_REVIEWED":deepcopy(collision_urls),
        "reused_ID_scope_collisions_NOT_REVIEWED":deepcopy(collision_ids),
        "uncited_source_readings_NOT_REVIEWED":deepcopy(uncited),
        "citations_without_DOM_block_UNRESOLVED":deepcopy(unattached),
        "every_attached_citation_crosswalk_NOT_SOURCE_SUPPORT_PROOF":citation_index,
        "all_origin_scoped_source_impact_packets_NOT_REVIEWED":source_packets,
        "human_source_review_work_order_NOT_PRIORITY_AS_RISK":prioritized,
        "consequential_blocks_without_same_block_citation_NOT_UNSUPPORTED_VERDICT":
            no_local_review,
        "counts":{
            "articles":expected[0], "tools":expected[1],
            "complete_origin_scoped_source_readings":len(sources),
            "citation_occurrences":len(total_keys),
            "attached_citation_occurrences":len(citation_index),
            "citation_source_variant_edges_NOT_CLAIM_COUNT":
                sum(len(v) for v in source_edges.values()),
            "unabridged_DOM_blocks":len(blocks),
            "consequential_action_or_quantity_review_blocks":len(review_index),
            "consequential_blocks_without_same_block_citation":len(no_local_review),
            "complete_source_impact_packets":len(source_packets),
            "shared_URL_groups_preserved":len(collision_urls),
            "reused_source_ID_groups_preserved":len(collision_ids),
            "uncited_source_records_preserved":len(uncited),
            "human_claim_support_reviews":0, "qualified_safety_reviews":0,
            "independent_QD_approvals":0},
        "limitations":(
            "This is an impact-navigation worklist, NOT a likelihood-of-injury score, "
            "proof of claim support, source-equivalence determination, or evidence "
            "that any instruction is safe. Source-variant edges can exceed unique "
            "citation occurrences because one citation ID can refer to multiple "
            "origin-scoped research readings. No human URLs checked. The complete "
            "original source readings, changed document text, collision identities "
            "and HOLD states are retained. Historical and proposed versions are "
            "not silently conflated. Independent qualified safety, human sources, "
            "actual browser/WordPress tests and QD remain mandatory."),
        **{k:False for k in HOLD_KEYS}}
    result["fingerprint_sha256"] = digest(result)
    sealed(result)
    return result


def csv_review_work_order(report):
    """One-way, spreadsheet-formula-neutralized reviewer aid; NO approval importer."""
    sealed(report)
    output = io.StringIO(newline="")
    writer = csv.writer(output,lineterminator="\n")
    writer.writerow((
        "source_origin", "source_id", "exact_URL_NO_ALIAS",
        "source_reading_sha256", "shared_URL_scope_review",
        "reused_ID_scope_review", "all_citation_variant_edges_NOT_CLAIMS",
        "consequential_citation_edges_NOT_RISK_SCORE",
        "distinct_documents", "human_source_and_claim_review",
        "qualified_safety_review", "reviewer_notes_UNTRUSTED"))
    def safe(value):
        s = json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(
            value,(dict,list)) else str(value)
        lead = s.lstrip(" \t\r\n\ufeff\u200b\u2060\u200e\u200f")
        return "'"+s if (s[:1] in ("\t","\r","\n","\ufeff","\u200b",
                                    "\u2060","\u200e","\u200f") or
                         lead.startswith(("=","+","-","@"))) else s
    for source in report["human_source_review_work_order_NOT_PRIORITY_AS_RISK"]:
        writer.writerow([safe(value) for value in (
            source["source_origin"],source["source_id"],
            source["exact_URL_NOT_CANONICALIZED"],
            source["complete_source_reading_sha256"],
            source["shared_exact_URL_REQUIRES_SCOPE_REVIEW"],
            source["reused_source_ID_REQUIRES_SCOPE_REVIEW"],
            source["all_citation_variant_edges_NOT_VERDICT"],
            source["consequential_citation_variant_edges_NOT_VERDICT"],
            source["distinct_documents_citing_source_NOT_VERIFIED"],
            REVIEW, REVIEW, "")])
    return output.getvalue()


def live_report(repo_root=None):
    parent = _r75().live_report(repo_root)
    result = construct(parent)
    need(result == construct(parent), "nondeterministic R76 source-impact report")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root",type=Path)
    parser.add_argument("--private-review-csv-stdout",action="store_true")
    args = parser.parse_args(argv)
    try:
        report = live_report(args.repo_root)
        if args.private_review_csv_stdout:
            sys.stdout.write(csv_review_work_order(report))
        else:
            print(json.dumps({"schema":SCHEMA,"release_state":"HOLD",
                "fingerprint_sha256":report["fingerprint_sha256"],
                "counts":report["counts"],"publication_clearance":False},
                sort_keys=True))
        return 0
    except (Hold,ValueError,KeyError,TypeError,AttributeError,OSError) as exc:
        print("R76 PRIVATE RELEASE HOLD: "+str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
