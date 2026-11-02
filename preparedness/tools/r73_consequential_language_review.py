#!/usr/bin/env python3
"""R73 private HOLD: consequential-language review docket over sealed R72 evidence.

Deterministic machine triage only. Action cues are NOT safety findings; even an
adjacent or same-block citation is NOT proof of claim support. This module does
not fetch links, approve safety, update WordPress, or authorize publication.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys

SCHEMA = "r73-private-consequential-language-and-evidence-review-v1"
R72_SCHEMA = "r72-private-source-scope-collision-impact-review-v1"
EXPECTED = (35, 6, 244, 2173, 4070)
REVIEW = "NOT_REVIEWED"
HOLD = ("may_publish", "independent_QD_approval",
        "qualified_safety_clearance", "human_source_links_verified")
HEX = re.compile(r"[a-f0-9]{64}\Z")
CUES = {
    "ACTION_WORDING_REVIEW_NOT_INSTRUCTION_VERDICT":
        re.compile(r"\b(?:must|should|never|avoid|discard|boil|filter|"
                   r"disinfect|mix|store|take|inject|administer|call|"
                   r"evacuate|leave|use|replace|refrigerate|freeze|"
                   r"turn\s+off|shut\s+off|switch\s+off|do\s+not|"
                   r"don't|ask|check|keep|place|follow|heat|cure)\b", re.I),
    "OPERATIONAL_QUANTITY_REVIEW_NOT_DOSAGE_ADVICE":
        re.compile(r"\b\d+(?:\.\d+)?\s*(?:hours?|days?|minutes?|"
                   r"seconds?|feet|foot|meters?|gallons?|liters?|"
                   r"litres?|milliliters?|mg|ml|ppm|degrees?|%)\b", re.I),
    "QUALIFYING_LANGUAGE_CONTEXT_ONLY_NOT_SAFETY_PROOF":
        re.compile(r"\b(?:unless|except|only\s+if|according\s+to|"
                   r"depending\s+on|local\s+(?:authorities|guidance)|"
                   r"consult|ask\s+(?:your|a)\s+(?:doctor|pharmacist)|"
                   r"do\s+not|never)\b", re.I),
}
ACTION_NAMES = tuple(CUES)[:2]


class Hold(ValueError):
    """Inconsistent or possibly escalated source/citation/safety custody."""


def need(ok, reason):
    if not ok:
        raise Hold(reason)


def sha(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False).encode("utf-8")).hexdigest()


def text_sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_sha(value):
    return type(value) is str and HEX.fullmatch(value) is not None


def sealed(row, schema):
    need(type(row) is dict and row.get("schema")==schema
         and row.get("issue")==136 and row.get("release_state")=="HOLD"
         and row.get("machine_only") is True
         and all(row.get(k) is False for k in HOLD)
         and is_sha(row.get("fingerprint_sha256"))
         and sha({k:v for k,v in row.items() if k!="fingerprint_sha256"})==
             row["fingerprint_sha256"], "upstream seal or HOLD status changed")


def cues(text):
    need(type(text) is str, "missing exact DOM text")
    return sorted(name for name,rx in CUES.items() if rx.search(text))


def _identity(row):
    origin, sid = row.get("source_origin"), row.get("source_id")
    need(type(origin) is str and bool(origin)
         and type(sid) is str and bool(sid), "empty origin-scoped source identity")
    return (origin,sid)


def construct(r72, *, expected=EXPECTED):
    """Pure, deep-copied evidence review packets; all human states stay pending."""
    need(type(expected) is tuple and len(expected)==5
         and all(type(n) is int and n>0 for n in expected), "invalid expected census")
    sealed(r72,R72_SCHEMA)
    counts=r72.get("counts")
    need(type(counts) is dict and tuple(counts.get(k) for k in (
        "articles","tools","complete_distinct_origin_scoped_source_readings",
        "citation_occurrences","unabridged_DOM_block_tasks"))==expected,
        "original RC document, source, citation or DOM block census drift")
    need(all(counts.get(k)==0 for k in (
        "human_claim_support_reviews","human_qualified_safety_reviews",
        "independent_QD_approvals")), "human or QD approval falsely imported")
    sources=r72.get("all_complete_source_readings_NOT_APPROVED")
    blocks=r72.get("all_unabridged_DOM_block_citation_tasks_NOT_APPROVED")
    documents=r72.get("all_document_impact_orders_NOT_APPROVED")
    unattached=r72.get("citations_without_DOM_block_UNRESOLVED")
    shared=r72.get("shared_exact_URL_collision_review_orders_NOT_APPROVED")
    reused=r72.get("reused_source_ID_collision_review_orders_NOT_APPROVED")
    uncited=r72.get("uncited_origin_scoped_sources_NOT_REVIEWED")
    need(type(sources) is list and len(sources)==expected[2]
         and type(blocks) is list and len(blocks)==expected[4]
         and type(documents) is list and len(documents)==expected[0]+expected[1]
         and all(type(x) is list for x in (unattached,shared,reused,uncited)),
         "unabridged source, DOM or collision evidence not preserved")
    source_index={}
    for source in sources:
        need(type(source) is dict, "source evidence is not a record")
        key=_identity(source)
        need(key not in source_index,"origin-scoped source silently merged")
        reading=source.get("candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        original=source.get("original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        need(type(reading) is dict and reading.get("id")==key[1]
             and reading.get("human_link_check") is False
             and type(reading.get("url")) is str
             and source.get("exact_URL_NO_ALIAS")==reading["url"]
             and source.get("candidate_reading_sha256")==sha(reading)
             and source.get("human_source_and_claim_review")==REVIEW
             and source.get("qualified_safety_review")==REVIEW,
             "complete source reading, URL, SHA or unreviewed state lost")
        need((original is None and source.get("original_reading_sha256") is None)
             or (type(original) is dict and
                 source.get("original_reading_sha256")==sha(original)),
             "historical original source reading altered or omitted")
        source_index[key]=source
    need(list(source_index)==sorted(source_index), "source custody order changed")
    doc_index={}
    for doc in documents:
        need(type(doc) is dict and doc.get("reviewer_state")==REVIEW,
             "document review state escalated")
        kind,slug=doc.get("kind"),doc.get("slug")
        key=(kind,slug)
        ids=doc.get("block_ids_in_original_order")
        url=doc.get("draft_url_NOT_PUBLIC")
        need(kind in ("article","tool") and type(slug) is str and slug
             and key not in doc_index and type(ids) is list and ids
             and len(ids)==len(set(ids))
             and type(url) is str and url.startswith("/preparedness/")
             and "//" not in url and ".." not in url,
             "private document URL, block order or identity invalid")
        doc_index[key]=doc
    need(len(set(d["draft_url_NOT_PUBLIC"] for d in documents))==len(documents)
         and sum(k[0]=="article" for k in doc_index)==expected[0]
         and sum(k[0]=="tool" for k in doc_index)==expected[1],
         "duplicate draft URL, lost article or lost tool")
    orders={}
    used_edges=set()
    block_ledger={}
    per_document=Counter()
    docket=[]
    count_queues=Counter()
    for block in blocks:
        need(type(block) is dict
             and is_sha(block.get("task_sha256"))
             and sha({k:v for k,v in block.items() if k!="task_sha256"})==
                 block["task_sha256"],"modified original R72 block task")
        key=(block.get("kind"),block.get("slug"))
        doc=doc_index.get(key)
        bid=block.get("block_id")
        need(doc is not None and type(bid) is str and bid
             and bid in doc["block_ids_in_original_order"]
             and block.get("private_draft_url")==doc["draft_url_NOT_PUBLIC"],
             "block moved, lost or URL changed")
        block_key=(*key,bid)
        need(block_key not in block_ledger, "duplicated document block identity")
        block_ledger[block_key]=block["task_sha256"]
        orders.setdefault(key,[]).append(bid)
        text=block.get("DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED")
        need(type(text) is str and text.strip()
             and text_sha(text)==block.get("DOM_text_sha256"),
             "original DOM reading depth, Unicode or text SHA lost")
        need(all(block.get(f)==REVIEW for f in (
            "human_claim_support_review","qualified_safety_review",
            "independent_QD_review")),"fabricated human/QD block decision")
        topics=block.get("topic_signals_TRIAGE_NOT_SAFETY_VERDICT")
        edges=block.get("local_citations_NOT_CLAIM_SUPPORT_PROOF")
        adjacent=block.get("adjacent_citations_NAVIGATION_HINTS_NOT_SUPPORT")
        need(type(topics) is list and topics==sorted(set(topics))
             and type(edges) is list and type(adjacent) is list,
             "block topic or citation navigation evidence altered")
        direct=[]
        for edge in edges:
            need(type(edge) is dict and edge.get("human_claim_support_review")==REVIEW
                 and type(edge.get("ordinal")) is int and edge["ordinal"]>0
                 and type(edge.get("source_id")) is str
                 and type(edge.get("origin_scoped_source_variants_NOT_ALIASED")) is list,
                 "source citation occurrence altered")
            ek=(*key,edge["ordinal"])
            need(ek not in used_edges, "duplicated source citation")
            used_edges.add(ek)
            variants=[]
            for item in edge["origin_scoped_source_variants_NOT_ALIASED"]:
                sk=_identity(item)
                reading=source_index.get(sk)
                need(reading is not None
                     and item.get("human_source_and_claim_review")==REVIEW
                     and edge["source_id"]==sk[1]
                     and item.get("exact_URL_NOT_ALIAS")==reading["exact_URL_NO_ALIAS"]
                     and item.get("complete_source_reading_sha256")==
                         reading["candidate_reading_sha256"],
                     "citation source variant aliased or original reading lost")
                variants.append({
                    "origin":sk[0],"source_id":sk[1],
                    "source_reading_sha256":reading["candidate_reading_sha256"],
                    "exact_URL_NOT_EQUIVALENCE":reading["exact_URL_NO_ALIAS"],
                    "human_source_scope_and_claim_review":REVIEW,
                })
            need(variants==sorted(variants,key=lambda x:(x["origin"],x["source_id"]))
                 and len({(x["origin"],x["source_id"]) for x in variants})==
                     len(variants) and bool(variants),
                 "reused ID/URL variant silently collapsed")
            direct.append({"ordinal":edge["ordinal"],
                "source_id":edge["source_id"],
                "origin_scoped_source_readings_NOT_MERGED":variants,
                "human_claim_support_review":REVIEW})
        markers=cues(text)
        # Numeric or action wording only determines REVIEW PRIORITY, never advice safety.
        action=bool(set(markers).intersection(ACTION_NAMES))
        triage=("CONSEQUENTIAL_TOPIC_WITH_ACTION_CUE_REVIEW"
                if topics and action else
                "CONSEQUENTIAL_TOPIC_WITHOUT_ACTION_CUE_REVIEW"
                if topics else "GENERAL_EDITORIAL_ONLY_REVIEW")
        count_queues[triage]+=1
        per_document[key]+=1
        if topics and action:
            packet={
                "kind":key[0],"slug":key[1],"block_id":bid,
                "private_draft_url_NOT_PUBLIC":doc["draft_url_NOT_PUBLIC"],
                "original_R72_block_sha256":block["task_sha256"],
                "full_DOM_text_UNABRIDGED_NOT_SAFETY_VERIFIED":text,
                "original_DOM_text_sha256":block["DOM_text_sha256"],
                "topic_signals_KEYWORD_TRIAGE_NOT_VERDICT":deepcopy(topics),
                "action_and_qualifier_cues_NOT_VERDICT":markers,
                "local_citations_NO_CLAIM_SUPPORT_ASSUMED":direct,
                "adjacent_citation_hints_NOT_EVIDENCE":deepcopy(adjacent),
                "action_priority_NOT_SAFETY_FINDING":triage,
                "human_claim_support_review":REVIEW,
                "qualified_safety_review":REVIEW,
                "independent_QD_review":REVIEW,
            }
            packet["packet_sha256"]=sha(packet)
            docket.append(packet)
    need(len(block_ledger)==expected[4] and
         all(orders.get(k)==doc["block_ids_in_original_order"]
             for k,doc in doc_index.items()),"unabridged DOM block or order missing")
    need(len(used_edges)+len(unattached)==expected[3]
         and counts.get("direct_DOM_citation_occurrences")==len(used_edges)
         and counts.get("unattached_citation_review_tasks")==len(unattached),
         "lost, repeated or unattached candidate citation")
    need(counts.get("shared_exact_URL_collision_groups")==len(shared)
         and counts.get("reused_source_ID_collision_groups")==len(reused)
         and counts.get("uncited_source_readings_kept")==len(uncited),
         "shared-URL/ID collisions or uncited readings silently dropped")
    result={
        "schema":SCHEMA,"issue":136,"release_state":"HOLD","machine_only":True,
        "R72_unmodified_evidence_fingerprint_sha256":r72["fingerprint_sha256"],
        "all_244_unabridged_source_readings_NOT_REVIEWED":deepcopy(sources),
        "all_4070_unabridged_DOM_tasks_NOT_REVIEWED":deepcopy(blocks),
        "all_document_block_orders_NOT_REVIEWED":deepcopy(documents),
        "shared_URL_scope_collisions_NOT_REVIEWED":deepcopy(shared),
        "reused_ID_scope_collisions_NOT_REVIEWED":deepcopy(reused),
        "uncited_source_readings_NOT_REVIEWED":deepcopy(uncited),
        "citations_without_DOM_block_UNRESOLVED":deepcopy(unattached),
        "consequential_action_wording_review_packets_NOT_APPROVED":docket,
        "counts":{
            "articles":expected[0],"tools":expected[1],
            "complete_distinct_origin_scoped_source_readings":len(sources),
            "citation_occurrences":len(used_edges)+len(unattached),
            "unabridged_DOM_review_tasks":len(blocks),
            "consequential_action_wording_triage_packets":len(docket),
            "topic_with_action_cue":count_queues[
                "CONSEQUENTIAL_TOPIC_WITH_ACTION_CUE_REVIEW"],
            "topic_without_action_cue":count_queues[
                "CONSEQUENTIAL_TOPIC_WITHOUT_ACTION_CUE_REVIEW"],
            "general_editorial_blocks":count_queues["GENERAL_EDITORIAL_ONLY_REVIEW"],
            "human_claim_support_reviews":0,"human_qualified_safety_reviews":0,
            "independent_QD_approvals":0,
        },
        "limitations":(
            "Deterministic keyword and directional-language triage has both false "
            "positives and false negatives; it is NOT an emergency safety finding. "
            "Same-block/nearby citations and apparent source dates do NOT prove "
            "claim support, medicine safety or source access. Complete evidence "
            "readings, duplicate URLs and reused IDs stay separate. Source links "
            "not fetched; no qualified human review, browser or screen-reader QA. "
            "Mandatory separate release integrity remains FAIL CLOSED/HOLD."
        ),
        **{key:False for key in HOLD},
    }
    result["fingerprint_sha256"]=sha(result)
    return result


def csv_action_packets(report):
    """Review worksheet with formula-safe cells; NEVER accept CSV as approval."""
    sealed(report,SCHEMA)
    buf=io.StringIO(newline="")
    writer=csv.writer(buf,lineterminator="\n")
    writer.writerow(("kind","slug","draft_url_PRIVATE","block_id","R72_block_SHA",
        "full_unabridged_DOM_text_UNVERIFIED","keyword_domains_NOT_VERDICT",
        "action_cues_NOT_VERDICT","local_source_origin_id_sha_url_NOT_PROOF",
        "adjacent_citation_hints_NOT_SUPPORT","claim_review_NOT_REVIEWED",
        "qualified_safety_review_NOT_REVIEWED","reviewer_notes_UNTRUSTED"))
    def safe(value):
        value=(json.dumps(value,sort_keys=True,ensure_ascii=False)
               if isinstance(value,(list,dict)) else str(value))
        left=value.lstrip(" \t\r\n\ufeff\u200b\u2060")
        return "'"+value if value[:1] in ("\t","\r","\n","\ufeff","\u200b","\u2060") or \
            left.startswith(("=","+","-","@")) else value
    for p in report["consequential_action_wording_review_packets_NOT_APPROVED"]:
        writer.writerow([safe(value) for value in (
            p["kind"],p["slug"],p["private_draft_url_NOT_PUBLIC"],p["block_id"],
            p["original_R72_block_sha256"],
            p["full_DOM_text_UNABRIDGED_NOT_SAFETY_VERIFIED"],
            p["topic_signals_KEYWORD_TRIAGE_NOT_VERDICT"],
            p["action_and_qualifier_cues_NOT_VERDICT"],
            p["local_citations_NO_CLAIM_SUPPORT_ASSUMED"],
            p["adjacent_citation_hints_NOT_EVIDENCE"],REVIEW,REVIEW,"")])
    return buf.getvalue()


def live_report(repo_root=None):
    path=Path(__file__).with_name("r72_source_scope_collision_impact.py")
    need(path.is_file() and not path.is_symlink(), "missing exact R72 review parent")
    spec=importlib.util.spec_from_file_location("r73_r72_parent",path)
    need(spec is not None and spec.loader is not None,"R72 parent unavailable")
    parent=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    root=Path(repo_root).resolve() if repo_root else None
    upstream=parent.live_report(root)
    out=construct(upstream)
    need(out==construct(upstream),"nondeterministic R73 wording review queue")
    return out


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root",type=Path)
    p.add_argument("--triage-csv-stdout",action="store_true")
    args=p.parse_args(argv)
    try:
        x=live_report(args.repo_root)
        if args.triage_csv_stdout:
            sys.stdout.write(csv_action_packets(x))
        else:
            print(json.dumps({"schema":SCHEMA,"release_state":"HOLD",
                "fingerprint_sha256":x["fingerprint_sha256"],
                "counts":x["counts"],"publication_clearance":False},
                sort_keys=True))
        return 0
    except (Hold,ValueError,KeyError,TypeError,AttributeError,OSError) as e:
        print("R73 PRIVATE RELEASE HOLD: "+str(e),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
