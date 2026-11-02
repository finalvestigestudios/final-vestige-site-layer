#!/usr/bin/env python3
"""R74 private HOLD: exact quantity-in-context review across 41 draft documents.

This is a lexical reviewer routing tool, NOT a calculator, safe-dosage checker,
contradiction detector, source verification, or approval mechanism.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys

SCHEMA = "r74-private-quantity-context-and-source-custody-v1"
PARENT = "r73-private-consequential-language-and-evidence-review-v1"
EXPECTED = (35, 6, 244, 2173, 4070)
REVIEW = "NOT_REVIEWED"
HOLD = ("may_publish", "independent_QD_approval", "qualified_safety_clearance", "human_source_links_verified")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
NUMBER = r"(?:-?(?:\d+(?:[.,]\d+)?|\d+/\d+)(?:\s*(?:[-–—]|to)\s*-?\d+(?:[.,]\d+)?)?)"
UNIT = (r"(?:degrees?\s+(?:Celsius|Fahrenheit|[CF])|°\s*[CF]|"
        r"gallons?|liters?|litres?|milliliters?|millilitres?|"
        r"micrograms?|milligrams?|grams?|kilograms?|"
        r"mcg|µg|mg|g|kg|mL|ml|L|ppm|"
        r"hours?|minutes?|seconds?|days?|weeks?|months?|"
        r"feet|foot|ft|inches?|meters?|metres?|m|centimeters?|centimetres?|cm|"
        r"degrees?|%)")
QUANTITY = re.compile(r"(?<![\w])(?P<value>" + NUMBER + r")\s*(?P<unit>" + UNIT + r")(?![\w])", re.I)
CAUTION = re.compile(r"\b(?:do\s+not|don't|never|unless|except|only\s+if|"
                     r"consult|ask\s+(?:your|a)\s+(?:doctor|pharmacist)|"
                     r"local\s+(?:authority|authorities|officials)|"
                     r"warning|hazard|not\s+safe)\b", re.I)

class Hold(ValueError):
    """Unresolved custody/safety state or altered signed evidence."""

def need(condition, reason):
    if not condition:
        raise Hold(reason)

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                    separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()

def text_digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def sealed(value, schema):
    need(type(value) is dict and value.get("schema") == schema
         and value.get("issue") == 136 and value.get("release_state") == "HOLD"
         and value.get("machine_only") is True
         and all(value.get(key) is False for key in HOLD)
         and type(value.get("fingerprint_sha256")) is str
         and HEX64.fullmatch(value["fingerprint_sha256"])
         and value["fingerprint_sha256"] == digest({k: v for k, v in value.items()
                                                     if k != "fingerprint_sha256"}),
         "parent signature, exact schema or private release HOLD status changed")

def unit_route(raw):
    """Only trivial plural spelling; never convert physical units or concentrations."""
    s = re.sub(r"\s+", "", raw.casefold())
    plurals = {"gallons":"gallon", "liters":"liter", "litres":"litre",
               "hours":"hour", "minutes":"minute", "seconds":"second",
               "days":"day", "weeks":"week", "months":"month",
               "milligrams":"milligram", "grams":"gram", "kilograms":"kilogram",
               "micrograms":"microgram", "feet":"foot", "inches":"inch",
               "meters":"meter", "metres":"metre", "degrees":"degree"}
    return plurals.get(s,s)

def quantities(text):
    need(type(text) is str, "nontext original DOM block")
    return [{"start_unicode":m.start(), "end_unicode":m.end(),
             "exact_text_NOT_ADVICE":m.group(),
             "exact_numeric_token_NOT_NORMALIZED":m.group("value"),
             "exact_unit_token_NOT_CONVERTED":m.group("unit"),
             "unit_spelling_route_NOT_EQUIVALENCE":unit_route(m.group("unit"))}
            for m in QUANTITY.finditer(text)]

def _origin_key(row):
    origin, sid = row.get("source_origin"), row.get("source_id")
    need(type(origin) is str and origin and type(sid) is str and sid,
         "empty source origin/ID")
    return (origin, sid)

def construct(parent, *, expected=EXPECTED):
    need(type(expected) is tuple and len(expected) == 5 and
         all(type(x) is int and x > 0 for x in expected), "invalid immutable census contract")
    sealed(parent,PARENT)
    counts = parent.get("counts")
    need(type(counts) is dict and tuple(counts.get(k) for k in (
         "articles", "tools", "complete_distinct_origin_scoped_source_readings",
         "citation_occurrences", "unabridged_DOM_review_tasks")) == expected,
         "41-document or source/citation/block census drift")
    need(all(counts.get(k) == 0 for k in (
         "human_claim_support_reviews", "human_qualified_safety_reviews",
         "independent_QD_approvals")), "unreviewed human/QD status changed")
    sources = parent.get("all_244_unabridged_source_readings_NOT_REVIEWED")
    blocks = parent.get("all_4070_unabridged_DOM_tasks_NOT_REVIEWED")
    docs = parent.get("all_document_block_orders_NOT_REVIEWED")
    action = parent.get("consequential_action_wording_review_packets_NOT_APPROVED")
    shared = parent.get("shared_URL_scope_collisions_NOT_REVIEWED")
    reused = parent.get("reused_ID_scope_collisions_NOT_REVIEWED")
    uncited = parent.get("uncited_source_readings_NOT_REVIEWED")
    unattached = parent.get("citations_without_DOM_block_UNRESOLVED")
    need(type(sources) is list and len(sources) == expected[2] and
         type(blocks) is list and len(blocks) == expected[4] and
         type(docs) is list and len(docs) == expected[0]+expected[1] and
         type(action) is list and all(type(x) is list for x in
              (shared,reused,uncited,unattached)), "original unabridged evidence missing")
    need(len(action) == counts.get("consequential_action_wording_triage_packets")
         == counts.get("topic_with_action_cue") and
         sum(counts.get(k, -1) for k in ("topic_with_action_cue",
             "topic_without_action_cue", "general_editorial_blocks")) == expected[4],
         "upstream action-triage inventory altered")
    source_index = {}
    for source in sources:
        need(type(source) is dict, "invalid original source reading")
        key = _origin_key(source)
        read = source.get("candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        need(key not in source_index and type(read) is dict and
             read.get("id") == key[1] and read.get("human_link_check") is False and
             type(read.get("url")) is str and read["url"] and
             read["url"] == source.get("exact_URL_NO_ALIAS") and
             digest(read) == source.get("candidate_reading_sha256") and
             source.get("human_source_and_claim_review") == REVIEW and
             source.get("qualified_safety_review") == REVIEW,
             "source identity, exact URL, complete reading or review status altered")
        original = source.get("original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        need((original is None and source.get("original_reading_sha256") is None)
             or (type(original) is dict and
                 digest(original) == source.get("original_reading_sha256")),
             "historical source reading overwritten")
        source_index[key] = source
    need(list(source_index) == sorted(source_index), "source ordering lost")
    doc_index = {}
    for doc in docs:
        need(type(doc) is dict and doc.get("reviewer_state") == REVIEW,
             "document review already escalated")
        key = (doc.get("kind"),doc.get("slug"))
        ids = doc.get("block_ids_in_original_order")
        url = doc.get("draft_url_NOT_PUBLIC")
        need(key[0] in ("article","tool") and type(key[1]) is str and key[1] and
             key not in doc_index and type(ids) is list and ids and
             len(ids) == len(set(ids)) and type(url) is str and
             url.startswith("/preparedness/") and "//" not in url and ".." not in url,
             "duplicate document, route or missing block order")
        doc_index[key] = doc
    need(len({doc["draft_url_NOT_PUBLIC"] for doc in docs}) == len(docs) and
         sum(k[0] == "article" for k in doc_index) == expected[0] and
         sum(k[0] == "tool" for k in doc_index) == expected[1],
         "missing article/tool or duplicate URL")
    blocks_by_key, used_edges, seen_order = {}, set(), defaultdict(list)
    tasks, candidate_total = [], 0
    groups = defaultdict(list)
    for block in blocks:
        need(type(block) is dict and type(block.get("task_sha256")) is str and
             digest({k:v for k,v in block.items() if k != "task_sha256"}) == block["task_sha256"],
             "original individual R72 custody seal altered")
        key = (block.get("kind"),block.get("slug"))
        bid = block.get("block_id")
        doc = doc_index.get(key)
        need(doc is not None and type(bid) is str and bid and
             bid in doc["block_ids_in_original_order"] and
             block.get("private_draft_url") == doc["draft_url_NOT_PUBLIC"] and
             (*key,bid) not in blocks_by_key,"block moved to another document or duplicated")
        seen_order[key].append(bid)
        blocks_by_key[(*key,bid)] = block
        body = block.get("DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED")
        need(type(body) is str and body.strip() and
             text_digest(body) == block.get("DOM_text_sha256"),
             "exact Unicode DOM text truncated or altered")
        need(all(block.get(k) == REVIEW for k in
             ("human_claim_support_review","qualified_safety_review","independent_QD_review")),
             "human/qualified/QD block review fabricated")
        topics = block.get("topic_signals_TRIAGE_NOT_SAFETY_VERDICT")
        edges = block.get("local_citations_NOT_CLAIM_SUPPORT_PROOF")
        hints = block.get("adjacent_citations_NAVIGATION_HINTS_NOT_SUPPORT")
        need(type(topics) is list and topics == sorted(set(topics)) and
             type(edges) is list and type(hints) is list,
             "local citation, topic or adjacent navigation evidence lost")
        exact_sources = []
        for edge in edges:
            need(type(edge) is dict and type(edge.get("ordinal")) is int and
                 edge["ordinal"] > 0 and type(edge.get("source_id")) is str and
                 edge.get("human_claim_support_review") == REVIEW and
                 type(edge.get("origin_scoped_source_variants_NOT_ALIASED")) is list,
                 "malformed source citation")
            ek = (*key,edge["ordinal"])
            need(ek not in used_edges, "citation reused or duplicated")
            used_edges.add(ek)
            variants=[]
            for variant in edge["origin_scoped_source_variants_NOT_ALIASED"]:
                sk = _origin_key(variant)
                source = source_index.get(sk)
                need(source is not None and sk[1] == edge["source_id"] and
                     variant.get("human_source_and_claim_review") == REVIEW and
                     variant.get("exact_URL_NOT_ALIAS") == source["exact_URL_NO_ALIAS"] and
                     variant.get("complete_source_reading_sha256") == source["candidate_reading_sha256"],
                     "source variant aliasing or missing research-reading depth")
                variants.append({"origin":sk[0],"source_id":sk[1],
                    "exact_URL_NO_EQUIVALENCE":source["exact_URL_NO_ALIAS"],
                    "complete_reading_sha256":source["candidate_reading_sha256"],
                    "human_claim_support_review":REVIEW})
            need(variants and variants == sorted(variants,key=lambda v:(v["origin"],v["source_id"]))
                 and len({(v["origin"],v["source_id"]) for v in variants}) == len(variants),
                 "citation source variants collapsed")
            exact_sources.append({"ordinal":edge["ordinal"],"source_id":edge["source_id"],
                                  "origin_scoped_variants_NOT_ALIASED":variants})
        spans = quantities(body)
        if spans:
            need(all(body[q["start_unicode"]:q["end_unicode"]] == q["exact_text_NOT_ADVICE"]
                     for q in spans), "numeric Unicode span does not reproduce original")
            task = {"kind":key[0],"slug":key[1],"block_id":bid,
                "draft_URL_PRIVATE":doc["draft_url_NOT_PUBLIC"],
                "original_R72_task_sha256":block["task_sha256"],
                "full_DOM_text_UNABRIDGED_NOT_VERIFIED":body,
                "exact_DOM_text_sha256":block["DOM_text_sha256"],
                "topic_keywords_NOT_SAFETY_VERDICT":deepcopy(topics),
                "quantities_EXACT_TEXT_NO_UNIT_CONVERSION":spans,
                "caution_wording_PRESENT_NOT_SUFFICIENT":bool(CAUTION.search(body)),
                "local_cited_source_variants_NOT_CLAIM_SUPPORT":exact_sources,
                "adjacent_citation_hints_NOT_SUPPORT":deepcopy(hints),
                "human_claim_support_review":REVIEW,
                "qualified_safety_review":REVIEW,"independent_QD_review":REVIEW}
            task["packet_sha256"] = digest(task)
            tasks.append(task)
            candidate_total += len(spans)
            for q in spans:
                for topic in (topics or ["GENERAL_UNCATEGORIZED_KEYWORD_TRIAGE"]):
                    groups[(topic,q["unit_spelling_route_NOT_EQUIVALENCE"])].append(
                        (key[0],key[1],bid,q["start_unicode"],q["exact_numeric_token_NOT_NORMALIZED"],task["packet_sha256"]))
    need(all(seen_order.get(k) == doc["block_ids_in_original_order"] for k,doc in doc_index.items())
         and len(blocks_by_key) == expected[4], "DOM article/tool reading order changed or blocks dropped")
    seen_action = set()
    for packet in action:
        need(type(packet) is dict and type(packet.get("packet_sha256")) is str and
             packet["packet_sha256"] == digest({k:v for k,v in packet.items()
                                                if k != "packet_sha256"}),
             "prior action triage packet tampered")
        key=(packet.get("kind"),packet.get("slug"),packet.get("block_id"))
        original=blocks_by_key.get(key)
        need(original is not None and key not in seen_action and
             packet.get("original_R72_block_sha256") == original["task_sha256"] and
             packet.get("original_DOM_text_sha256") == original["DOM_text_sha256"] and
             packet.get("full_DOM_text_UNABRIDGED_NOT_SAFETY_VERIFIED") ==
                original["DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"] and
             packet.get("private_draft_url_NOT_PUBLIC") == original["private_draft_url"] and
             all(packet.get(k) == REVIEW for k in
                 ("human_claim_support_review","qualified_safety_review","independent_QD_review")),
             "R73 triage packet changed, duplicated or marked approved")
        seen_action.add(key)
    need(len(used_edges)+len(unattached) == expected[3] and
         counts.get("citation_occurrences") == expected[3],
         "lost or duplicated exact citations")
    collision_reviews=[]
    for (topic,unit),rows in sorted(groups.items()):
        if len({(r[0],r[1]) for r in rows}) < 2 or len({r[4] for r in rows}) < 2:
            continue
        collision_reviews.append({
            "topic_keyword_NOT_VALIDATED_CONCEPT":topic,
            "unit_spelling_ONLY_NOT_PHYSICAL_EQUIVALENCE":unit,
            "distinct_raw_number_tokens_NOT_CONTRADICTIONS":sorted({r[4] for r in rows}),
            "exact_span_references_NOT_VERIFIED_ADVICE":[
                {"kind":kind,"slug":slug,"block_id":bid,"start_unicode":start,
                 "original_number_token":value,"packet_sha256":packet}
                for kind,slug,bid,start,value,packet in rows],
            "human_source_context_review":REVIEW,"qualified_safety_review":REVIEW})
    report = {"schema":SCHEMA,"issue":136,"release_state":"HOLD","machine_only":True,
        "original_R73_evidence_fingerprint_sha256":parent["fingerprint_sha256"],
        "all_244_unabridged_source_readings_NOT_REVIEWED":deepcopy(sources),
        "all_4070_unabridged_DOM_tasks_NOT_REVIEWED":deepcopy(blocks),
        "all_document_block_orders_NOT_REVIEWED":deepcopy(docs),
        "all_975_action_triage_packets_NOT_APPROVED":deepcopy(action),
        "shared_URL_scope_collisions_NOT_REVIEWED":deepcopy(shared),
        "reused_ID_scope_collisions_NOT_REVIEWED":deepcopy(reused),
        "uncited_source_readings_NOT_REVIEWED":deepcopy(uncited),
        "citations_without_DOM_block_UNRESOLVED":deepcopy(unattached),
        "exact_quantity_review_packets_NOT_APPROVED":tasks,
        "cross_document_same_spelling_candidate_groups_NOT_CONTRADICTIONS":collision_reviews,
        "counts":{"articles":expected[0],"tools":expected[1],
            "complete_origin_scoped_source_readings":len(sources),
            "citation_occurrences":len(used_edges)+len(unattached),
            "unabridged_DOM_blocks":len(blocks),"parent_action_triage_packets":len(action),
            "DOM_blocks_with_matching_numeric_units":len(tasks),
            "numeric_unit_occurrences":candidate_total,
            "cross_document_same_unit_spelling_review_groups":len(collision_reviews),
            "human_source_or_claim_reviews":0,"human_qualified_safety_reviews":0,
            "independent_QD_approvals":0},
        "limitations":("Machine-only lexical quantity matches (including editorial/history text) "
            "are NOT safety findings, contradictions, dose checks, or validated instructions. "
            "Equivalent physical units are not converted or asserted; differing quantities "
            "may be intended for entirely different conditions. Regex has false positives and "
            "false negatives. Original full text/readings, duplicate URLs and source variants "
            "are preserved. No human links, source support, medically qualified assessment, "
            "browser/WordPress verification, QD review or publication authorization."),
        **{k:False for k in HOLD}}
    report["fingerprint_sha256"] = digest(report)
    return report

def csv_review_packets(report):
    """Export reviewer-only quantities; never accept a CSV as an approval import."""
    sealed(report,SCHEMA)
    b=io.StringIO(newline="")
    out=csv.writer(b,lineterminator="\n")
    out.writerow(("kind","slug","draft_url_PRIVATE","block_id","full_DOM_text_UNVERIFIED",
                  "exact_numeric_units_UNCONVERTED","source_readings_NOT_PROOF",
                  "caution_wording_NOT_PROOF","review_status","reviewer_notes_UNTRUSTED"))
    def neutralize(v):
        s=json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(list,dict)) else str(v)
        stripped=s.lstrip(" \t\r\n\ufeff\u200b\u2060\u200e\u200f")
        if s[:1] in ("\t","\r","\n","\ufeff","\u200b","\u2060","\u200e","\u200f") or stripped.startswith(("=","+","-","@")):
            return "'"+s
        return s
    for item in report["exact_quantity_review_packets_NOT_APPROVED"]:
        out.writerow([neutralize(v) for v in (
            item["kind"],item["slug"],item["draft_URL_PRIVATE"],item["block_id"],
            item["full_DOM_text_UNABRIDGED_NOT_VERIFIED"],
            item["quantities_EXACT_TEXT_NO_UNIT_CONVERSION"],
            item["local_cited_source_variants_NOT_CLAIM_SUPPORT"],
            item["caution_wording_PRESENT_NOT_SUFFICIENT"],REVIEW,"")])
    return b.getvalue()

def live_report(repo_root=None):
    path=Path(__file__).with_name("r73_consequential_language_review.py")
    need(path.is_file() and not path.is_symlink(), "missing exact signed R73 review parent")
    spec=importlib.util.spec_from_file_location("r74_r73_parent",path)
    need(spec is not None and spec.loader is not None,"R73 parent loader unavailable")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root=Path(repo_root).resolve() if repo_root else None
    original=module.live_report(root)
    result=construct(original)
    need(result == construct(original),"nondeterministic R74 review generation")
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root",type=Path)
    p.add_argument("--private-csv-stdout",action="store_true")
    a=p.parse_args(argv)
    try:
        result=live_report(a.repo_root)
        if a.private_csv_stdout:
            sys.stdout.write(csv_review_packets(result))
        else:
            print(json.dumps({"schema":SCHEMA,"release_state":"HOLD",
                "fingerprint_sha256":result["fingerprint_sha256"],
                "counts":result["counts"],"publication_clearance":False},sort_keys=True))
        return 0
    except (Hold,ValueError,KeyError,TypeError,AttributeError,OSError) as e:
        print("R74 PRIVATE RELEASE HOLD: "+str(e),file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
