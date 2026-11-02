#!/usr/bin/env python3
"""R75 PRIVATE HOLD: exact lexical safety-qualifier scope and citation-custody worklist.

This preserves every original draft DOM block and research reading. A lexical warning
near an action is NOT proof of adequate qualification, claim support, or safety.
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
import re
import sys

SCHEMA = "r75-private-qualifier-scope-citation-custody-v1"
PARENT = "r74-private-quantity-context-and-source-custody-v1"
EXPECTED = (35, 6, 244, 2173, 4070)
REVIEW = "NOT_REVIEWED"
HOLD_KEYS = ("may_publish", "independent_QD_approval",
             "qualified_safety_clearance", "human_source_links_verified")
HEX = re.compile(r"[0-9a-f]{64}\Z")

# These are ONLY literal word locators. They are not a language understanding model.
CUES = {
    "PROHIBITION_LEXEME": (r"\b(?:do\s+not|don't|don.t|must\s+not|never|"
                           r"should\s+not|cannot|can't|can.t|not\s+safe)\b"),
    "EXCEPTION_LEXEME": r"\b(?:unless|except(?:\s+when)?|only\s+if|provided\s+that)\b",
    "CONDITION_LEXEME": r"\b(?:if|when|before|after|during|until|as\s+long\s+as)\b",
    "AUTHORITY_REFERRAL_LEXEME": (
        r"\b(?:consult|ask\s+(?:your|a)\s+(?:doctor|pharmacist|prescriber)|"
        r"local\s+(?:health\s+)?(?:authority|authorities|officials)|"
        r"(?:doctor|pharmacist|prescriber|veterinarian)\s+(?:advice|guidance)|"
        r"follow\s+(?:official|local)\s+(?:instructions|guidance))\b"),
    "UNCERTAINTY_LEXEME": r"\b(?:uncertain|unverified|not\s+validated|may|might|unknown)\b",
}
PATTERNS = tuple((name, re.compile(expr, re.IGNORECASE)) for name, expr in CUES.items())

class Hold(ValueError):
    """A custody, provenance or publication HOLD contract was violated."""

def need(ok, reason):
    if not ok:
        raise Hold(reason)

def digest(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()

def text_digest(x):
    return hashlib.sha256(x.encode("utf-8")).hexdigest()

def sealed(row, schema):
    need(type(row) is dict and row.get("schema") == schema
         and row.get("issue") == 136 and row.get("release_state") == "HOLD"
         and row.get("machine_only") is True
         and all(row.get(k) is False for k in HOLD_KEYS)
         and type(row.get("fingerprint_sha256")) is str
         and HEX.fullmatch(row["fingerprint_sha256"])
         and row["fingerprint_sha256"] == digest(
             {k:v for k,v in row.items() if k != "fingerprint_sha256"}),
         "invalid source-custody fingerprint, schema or release HOLD")

def qualifier_spans(text):
    """Return exact Unicode offsets and literal phrases with overlaps coalesced."""
    need(type(text) is str, "nontext DOM block")
    candidates=[]
    for category, pattern in PATTERNS:
        for m in pattern.finditer(text):
            candidates.append((m.start(), m.end(), category, m.group()))
    candidates.sort(key=lambda x:(x[0], -(x[1]-x[0]), x[2]))
    chosen=[]
    for start,end,category,literal in candidates:
        if chosen and start < chosen[-1]["end_unicode"]:
            continue
        chosen.append({"start_unicode":start, "end_unicode":end,
                       "literal_NOT_SAFETY_ASSESSMENT":literal,
                       "category_LEXICAL_ONLY":category})
    return chosen

def _r74():
    path=Path(__file__).with_name("r74_quantity_context_custody.py")
    need(path.is_file() and not path.is_symlink(), "R74 parent code unavailable")
    spec=importlib.util.spec_from_file_location("r75_r74",path)
    need(spec is not None and spec.loader is not None, "R74 loader unavailable")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def construct(parent, *, expected=EXPECTED):
    need(type(expected) is tuple and len(expected)==5
         and all(type(n) is int and n>0 for n in expected),
         "immutable corpus census invalid")
    sealed(parent,PARENT)
    ancestor=parent.get("original_R73_evidence_fingerprint_sha256")
    need(type(ancestor) is str and HEX.fullmatch(ancestor),
         "R73 upstream custody ancestor fingerprint missing or malformed")
    counts=parent.get("counts")
    need(type(counts) is dict and tuple(counts.get(k) for k in (
         "articles","tools","complete_origin_scoped_source_readings",
         "citation_occurrences","unabridged_DOM_blocks")) == expected
         and all(counts.get(k) == 0 for k in (
         "human_source_or_claim_reviews","human_qualified_safety_reviews",
         "independent_QD_approvals")), "source/citation/document census or review state drift")

    sources=parent.get("all_244_unabridged_source_readings_NOT_REVIEWED")
    blocks=parent.get("all_4070_unabridged_DOM_tasks_NOT_REVIEWED")
    docs=parent.get("all_document_block_orders_NOT_REVIEWED")
    actions=parent.get("all_975_action_triage_packets_NOT_APPROVED")
    qty=parent.get("exact_quantity_review_packets_NOT_APPROVED")
    groups=parent.get("cross_document_same_spelling_candidate_groups_NOT_CONTRADICTIONS")
    shared=parent.get("shared_URL_scope_collisions_NOT_REVIEWED")
    reused=parent.get("reused_ID_scope_collisions_NOT_REVIEWED")
    uncited=parent.get("uncited_source_readings_NOT_REVIEWED")
    unattached=parent.get("citations_without_DOM_block_UNRESOLVED")
    need(type(sources) is list and len(sources)==expected[2]
         and type(blocks) is list and len(blocks)==expected[4]
         and type(docs) is list and len(docs)==expected[0]+expected[1]
         and type(actions) is list and len(actions)==counts.get("parent_action_triage_packets")
         and type(qty) is list and len(qty)==counts.get("DOM_blocks_with_matching_numeric_units")
         and type(groups) is list and len(groups)==counts.get("cross_document_same_unit_spelling_review_groups")
         and all(type(x) is list for x in (shared,reused,uncited,unattached)),
         "unabridged evidence, collision or prior reviewer inventory missing")

    source_index={}
    for row in sources:
        need(type(row) is dict, "source reading not a record")
        origin,sid=row.get("source_origin"),row.get("source_id")
        key=(origin,sid)
        read=row.get("candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        need(type(origin) is str and origin and type(sid) is str and sid
             and key not in source_index and type(read) is dict
             and read.get("id")==sid and type(read.get("url")) is str and read["url"]
             and read.get("human_link_check") is False
             and row.get("exact_URL_NO_ALIAS")==read["url"]
             and row.get("candidate_reading_sha256")==digest(read)
             and row.get("human_source_and_claim_review")==REVIEW
             and row.get("qualified_safety_review")==REVIEW,
             "source readings or distinct origin/URL identity altered")
        historical=row.get("original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        need((historical is None and row.get("original_reading_sha256") is None)
             or (type(historical) is dict and
                 digest(historical)==row.get("original_reading_sha256")),
             "historical reading altered")
        source_index[key]=row
    need(list(source_index)==sorted(source_index), "original distinct source ordering changed")

    doc_index={}
    for doc in docs:
        need(type(doc) is dict and doc.get("reviewer_state")==REVIEW,
             "document safety review falsely approved")
        kind,slug=doc.get("kind"),doc.get("slug")
        url=doc.get("draft_url_NOT_PUBLIC")
        ids=doc.get("block_ids_in_original_order")
        key=(kind,slug)
        need(kind in ("article","tool") and type(slug) is str and slug
             and key not in doc_index and type(url) is str
             and url.startswith("/preparedness/") and ".." not in url and "//" not in url
             and type(ids) is list and ids and len(ids)==len(set(ids)),
             "document identity, route or DOM ordering corrupt")
        doc_index[key]=doc
    need(len(set(x["draft_url_NOT_PUBLIC"] for x in docs))==len(docs)
         and sum(k[0]=="article" for k in doc_index)==expected[0]
         and sum(k[0]=="tool" for k in doc_index)==expected[1],
         "duplicate draft URL or lost article/tool")

    block_index={}
    seen_orders=defaultdict(list)
    edges=set()
    qualifier_packets=[]
    qualification_by_key={}
    for b in blocks:
        need(type(b) is dict and b.get("task_sha256")==digest(
             {k:v for k,v in b.items() if k!="task_sha256"}),
             "original R72 DOM block fingerprint changed")
        kind,slug,bid=b.get("kind"),b.get("slug"),b.get("block_id")
        doc=doc_index.get((kind,slug))
        key=(kind,slug,bid)
        t=b.get("DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED")
        need(doc is not None and type(bid) is str and bid and key not in block_index
             and bid in doc["block_ids_in_original_order"]
             and b.get("private_draft_url")==doc["draft_url_NOT_PUBLIC"]
             and type(t) is str and t.strip()
             and b.get("DOM_text_sha256")==text_digest(t)
             and all(b.get(k)==REVIEW for k in
                  ("human_claim_support_review","qualified_safety_review","independent_QD_review")),
             "original block identity, full text or review state lost")
        block_index[key]=b
        seen_orders[(kind,slug)].append(bid)
        local=b.get("local_citations_NOT_CLAIM_SUPPORT_PROOF")
        need(type(local) is list and type(b.get("adjacent_citations_NAVIGATION_HINTS_NOT_SUPPORT")) is list,
             "citation or adjacent hint inventory lost")
        for edge in local:
            need(type(edge) is dict and type(edge.get("ordinal")) is int
                 and edge["ordinal"]>0 and type(edge.get("source_id")) is str
                 and edge.get("human_claim_support_review")==REVIEW,
                 "citation occurrence malformed or falsely approved")
            ekey=(kind,slug,edge["ordinal"])
            need(ekey not in edges, "duplicated citation ordinal")
            edges.add(ekey)
            variants=edge.get("origin_scoped_source_variants_NOT_ALIASED")
            need(type(variants) is list and variants, "source identity variants omitted")
            seen=set()
            for variant in variants:
                need(type(variant) is dict, "source variant invalid")
                skey=(variant.get("source_origin"),variant.get("source_id"))
                source=source_index.get(skey)
                need(source is not None and skey not in seen
                     and skey[1]==edge["source_id"]
                     and variant.get("exact_URL_NOT_ALIAS")==source["exact_URL_NO_ALIAS"]
                     and variant.get("complete_source_reading_sha256")==source["candidate_reading_sha256"]
                     and variant.get("human_source_and_claim_review")==REVIEW,
                     "citation origin/URL/source reading collapsed or altered")
                seen.add(skey)
        spans=qualifier_spans(t)
        qualification_by_key[key]=spans
        if spans:
            packet={"kind":kind,"slug":slug,"block_id":bid,
                "draft_URL_PRIVATE":doc["draft_url_NOT_PUBLIC"],
                "original_R72_block_sha256":b["task_sha256"],
                "unabridged_DOM_text_NOT_VERIFIED":t,
                "exact_qualifier_lexemes_NOT_SAFETY_CLEARANCE":spans,
                "local_citations_NOT_SUPPORT_PROOF":deepcopy(local),
                "human_claim_support_review":REVIEW,
                "qualified_safety_review":REVIEW,
                "independent_QD_review":REVIEW}
            packet["packet_sha256"]=digest(packet)
            qualifier_packets.append(packet)
    need(len(edges)+len(unattached)==expected[3]
         and all(seen_orders.get(k)==doc["block_ids_in_original_order"]
                 for k,doc in doc_index.items()),"dropped citation or changed full document DOM order")

    action_keys=set()
    for action in actions:
        need(type(action) is dict and action.get("packet_sha256")==digest(
             {k:v for k,v in action.items() if k!="packet_sha256"}),
             "R73 action packet fingerprint altered")
        key=(action.get("kind"),action.get("slug"),action.get("block_id"))
        original=block_index.get(key)
        need(original is not None and key not in action_keys
             and action.get("original_R72_block_sha256")==original["task_sha256"]
             and action.get("original_DOM_text_sha256")==original["DOM_text_sha256"]
             and action.get("full_DOM_text_UNABRIDGED_NOT_SAFETY_VERIFIED")==
                 original["DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"]
             and action.get("private_draft_url_NOT_PUBLIC")==original["private_draft_url"]
             and all(action.get(k)==REVIEW for k in (
                 "human_claim_support_review","qualified_safety_review","independent_QD_review")),
             "R73 action provenance/sequence or safety state lost")
        action_keys.add(key)

    quantity_keys=set()
    unit_count=0
    r74=_r74()
    for item in qty:
        need(type(item) is dict and item.get("packet_sha256")==digest(
             {k:v for k,v in item.items() if k!="packet_sha256"}),
             "R74 quantity packet fingerprint changed")
        key=(item.get("kind"),item.get("slug"),item.get("block_id"))
        original=block_index.get(key)
        need(original is not None and key not in quantity_keys
             and item.get("original_R72_task_sha256")==original["task_sha256"]
             and item.get("exact_DOM_text_sha256")==original["DOM_text_sha256"]
             and item.get("full_DOM_text_UNABRIDGED_NOT_VERIFIED")==
                 original["DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"]
             and item.get("draft_URL_PRIVATE")==original["private_draft_url"]
             and all(item.get(k)==REVIEW for k in (
                 "human_claim_support_review","qualified_safety_review","independent_QD_review")),
             "R74 quantity reading context or approval state altered")
        expected_spans=r74.quantities(item["full_DOM_text_UNABRIDGED_NOT_VERIFIED"])
        need(expected_spans==item.get("quantities_EXACT_TEXT_NO_UNIT_CONVERSION")
             and bool(expected_spans), "quantity Unicode-span/canonical text mismatch")
        unit_count+=len(expected_spans)
        quantity_keys.add(key)
    need(unit_count==counts.get("numeric_unit_occurrences"),
         "quantity count changed or reading truncated")
    for g in groups:
        need(type(g) is dict
             and g.get("human_source_context_review")==REVIEW
             and g.get("qualified_safety_review")==REVIEW,
             "quantity collision group falsely adjudicated")

    review_keys=action_keys | quantity_keys
    review_packets=[]
    for kind,slug,bid in sorted(review_keys):
        doc=doc_index[(kind,slug)]
        ids=doc["block_ids_in_original_order"]
        offset=ids.index(bid)
        b=block_index[(kind,slug,bid)]
        neighbor=[]
        for direction,at in (("PREVIOUS_NAV_ONLY",offset-1),("NEXT_NAV_ONLY",offset+1)):
            if 0<=at<len(ids):
                near=block_index[(kind,slug,ids[at])]
                near_text=near["DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"]
                neighbor.append({"direction":direction,"block_id":ids[at],
                    "unabridged_nearby_text_NOT_EVIDENCE":near_text,
                    "original_R72_block_sha256":near["task_sha256"],
                    "qualifiers_NEARBY_NOT_SUFFICIENT":deepcopy(
                        qualification_by_key[(kind,slug,ids[at])])})
        local=qualification_by_key[(kind,slug,bid)]
        row={"kind":kind,"slug":slug,"block_id":bid,
            "draft_URL_PRIVATE":doc["draft_url_NOT_PUBLIC"],
            "original_R72_block_sha256":b["task_sha256"],
            "full_DOM_text_UNABRIDGED_NOT_SAFETY_APPROVED":
                b["DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"],
            "source_citations_NOT_CLAIM_SUPPORT":deepcopy(
                b["local_citations_NOT_CLAIM_SUPPORT_PROOF"]),
            "action_language_TRIAGE_NOT_VERDICT":(kind,slug,bid) in action_keys,
            "numeric_units_TRIAGE_NOT_DOSAGE_CHECK":(kind,slug,bid) in quantity_keys,
            "same_block_qualifiers_NOT_SAFETY_PROOF":deepcopy(local),
            "immediate_neighbor_qualifiers_NOT_SAFETY_PROOF":neighbor,
            "NO_SAME_BLOCK_LEXICAL_QUALIFIER_REVIEW_ONLY":not bool(local),
            "human_claim_support_review":REVIEW,
            "qualified_safety_review":REVIEW,"independent_QD_review":REVIEW}
        row["packet_sha256"]=digest(row)
        review_packets.append(row)

    report={"schema":SCHEMA,"issue":136,"release_state":"HOLD","machine_only":True,
        "original_R74_fingerprint_sha256":parent["fingerprint_sha256"],
        "all_244_unabridged_source_readings_NOT_REVIEWED":deepcopy(sources),
        "all_4070_unabridged_DOM_tasks_NOT_REVIEWED":deepcopy(blocks),
        "all_document_block_orders_NOT_REVIEWED":deepcopy(docs),
        "all_975_action_triage_packets_NOT_APPROVED":deepcopy(actions),
        "all_numeric_unit_packets_NOT_APPROVED":deepcopy(qty),
        "cross_document_quantity_groups_NOT_VERDICTS":deepcopy(groups),
        "shared_URL_scope_collisions_NOT_REVIEWED":deepcopy(shared),
        "reused_ID_scope_collisions_NOT_REVIEWED":deepcopy(reused),
        "uncited_source_readings_NOT_REVIEWED":deepcopy(uncited),
        "citations_without_DOM_block_UNRESOLVED":deepcopy(unattached),
        "all_qualifier_locator_packets_NOT_SAFETY_CLEARANCE":qualifier_packets,
        "action_or_quantity_qualifier_context_queue_NOT_APPROVED":review_packets,
        "counts":{"articles":expected[0],"tools":expected[1],
            "complete_origin_scoped_source_readings":len(sources),
            "citation_occurrences":len(edges)+len(unattached),
            "unabridged_DOM_blocks":len(blocks),
            "parent_action_language_packets":len(actions),
            "parent_numeric_unit_packets":len(qty),
            "lexical_qualifier_blocks":len(qualifier_packets),
            "literal_qualifier_occurrences":sum(len(x[
                "exact_qualifier_lexemes_NOT_SAFETY_CLEARANCE"]) for x in qualifier_packets),
            "union_action_or_quantity_review_queue":len(review_packets),
            "union_without_same_block_lexical_qualifier_triage":sum(
                x["NO_SAME_BLOCK_LEXICAL_QUALIFIER_REVIEW_ONLY"] for x in review_packets),
            "human_claim_support_reviews":0,"qualified_safety_reviews":0,
            "independent_QD_approvals":0},
        "limitations":("Lexical locators can miss warnings or flag benign language. "
            "Presence, absence, or adjacency of a word does not decide whether a "
            "qualifier is adequate, an instruction is medically safe, a source "
            "supports a claim, or a numerical comparison is meaningful. Source "
            "links were not opened by this tool. All prior reading depth, exact URLs, "
            "collision identities, full Unicode DOM text, source citations and HOLD "
            "states preserved; human expertise, WordPress/browser QA, independent "
            "QD and mandatory release integrity are still required."),
        **{k:False for k in HOLD_KEYS}}
    report["fingerprint_sha256"]=digest(report)
    return report

def csv_review_worklist(report):
    sealed(report,SCHEMA)
    out=io.StringIO(newline="")
    wr=csv.writer(out,lineterminator="\n")
    wr.writerow(("kind","slug","draft_URL_PRIVATE","block_id",
        "original_R72_block_SHA","full_text_NOT_APPROVED","action_TRIAGE",
        "quantity_TRIAGE","literal_local_qualifier_cues_NOT_VERDICT",
        "immediate_neighbor_warning_context_NOT_VERDICT",
        "local_source_citations_NOT_PROOF","needs_qualifier_scope_review",
        "qualified_safety_review","reviewer_notes_UNTRUSTED"))
    def safe(x):
        x=(json.dumps(x,sort_keys=True,ensure_ascii=False)
           if isinstance(x,(dict,list)) else str(x))
        stripped=x.lstrip(" \t\r\n\ufeff\u200b\u2060\u200e\u200f")
        return "'"+x if x[:1] in ("\t","\r","\n","\ufeff","\u200b","\u2060","\u200e","\u200f") or stripped.startswith(("=","+","-","@")) else x
    for row in report["action_or_quantity_qualifier_context_queue_NOT_APPROVED"]:
        wr.writerow([safe(x) for x in (
            row["kind"],row["slug"],row["draft_URL_PRIVATE"],row["block_id"],
            row["original_R72_block_sha256"],
            row["full_DOM_text_UNABRIDGED_NOT_SAFETY_APPROVED"],
            row["action_language_TRIAGE_NOT_VERDICT"],
            row["numeric_units_TRIAGE_NOT_DOSAGE_CHECK"],
            row["same_block_qualifiers_NOT_SAFETY_PROOF"],
            row["immediate_neighbor_qualifiers_NOT_SAFETY_PROOF"],
            row["source_citations_NOT_CLAIM_SUPPORT"],
            row["NO_SAME_BLOCK_LEXICAL_QUALIFIER_REVIEW_ONLY"],REVIEW,"")])
    return out.getvalue()

def live_report(repo_root=None):
    r74=_r74()
    original=r74.live_report(repo_root)
    result=construct(original)
    need(result==construct(original), "nondeterministic R75 exact evidence review")
    return result

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root",type=Path)
    parser.add_argument("--private-review-csv-stdout",action="store_true")
    args=parser.parse_args(argv)
    try:
        row=live_report(args.repo_root)
        if args.private_review_csv_stdout:
            sys.stdout.write(csv_review_worklist(row))
        else:
            print(json.dumps({"schema":SCHEMA,"release_state":"HOLD",
                "fingerprint_sha256":row["fingerprint_sha256"],
                "counts":row["counts"],"publication_clearance":False},
                sort_keys=True))
        return 0
    except (Hold,ValueError,KeyError,TypeError,AttributeError,OSError) as exc:
        print("R75 PRIVATE RELEASE HOLD: "+str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
