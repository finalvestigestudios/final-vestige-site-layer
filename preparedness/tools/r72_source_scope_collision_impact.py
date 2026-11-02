#!/usr/bin/env python3
"""R72 PRIVATE HOLD: source-scope collision and downstream citation impact docket.

Cross-check the sealed R71 passage ledger without treating same-URL / same-ID
source records as interchangeable or adjacent citations as claim support.
No URL network access, WordPress writes, safety approvals or publication.
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

SCHEMA = "r72-private-source-scope-collision-impact-review-v1"
R71_SCHEMA = "r71-private-rc-block-to-citation-source-review-v1"
EXPECTED = (35, 6, 244, 2173)
HOLD = ("may_publish", "independent_QD_approval",
        "qualified_safety_clearance", "human_source_links_verified")
SHA = re.compile(r"[0-9a-f]{64}\Z")
REVIEW = "NOT_REVIEWED"


class Hold(ValueError):
    """Data inconsistency or attempted review-state escalation: release HOLD."""


def require(ok, reason):
    if not ok:
        raise Hold(reason)


def fingerprint(obj):
    return hashlib.sha256(json.dumps(
        obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False).encode("utf-8")).hexdigest()


def text_hash(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_sha(value):
    return type(value) is str and SHA.fullmatch(value) is not None


def sealed(report, schema):
    require(type(report) is dict and report.get("schema") == schema
            and report.get("issue") == 136
            and report.get("release_state") == "HOLD"
            and report.get("machine_only") is True
            and all(report.get(k) is False for k in HOLD)
            and is_sha(report.get("fingerprint_sha256"))
            and fingerprint({k:v for k,v in report.items()
                             if k != "fingerprint_sha256"}) ==
                report["fingerprint_sha256"],
            "sealed report invalid or an approval was forged")


def identity(row):
    key=(row.get("source_origin"),row.get("source_id"))
    require(all(type(v) is str and v for v in key), "missing source origin/ID")
    return key


def construct(r71, *, expected=EXPECTED):
    """Pure deterministic collision-impact report; original evidence is unmodified."""
    require(type(expected) is tuple and len(expected)==4
            and all(type(x) is int and x>0 for x in expected), "invalid census")
    sealed(r71,R71_SCHEMA)
    counts=r71.get("counts")
    require(type(counts) is dict
            and tuple(counts.get(k) for k in (
                "candidate_articles","candidate_tools",
                "unabridged_source_readings_conserved",
                "candidate_citations_conserved")) == expected
            and counts.get("human_source_claim_or_safety_reviews_by_R71")==0,
            "R71 source/document/citation totals or human states drifted")
    sources=r71.get("all_244_unabridged_source_reading_review_records_NOT_APPROVED")
    blocks=r71.get("all_DOM_block_claim_and_exact_source_review_tasks_NOT_APPROVED")
    reverse=r71.get("source_to_cited_block_reverse_custody_NOT_APPROVED")
    unattached=r71.get("citations_with_no_DOM_block_NOT_APPROVED")
    require(type(sources) is list and len(sources)==expected[2]
            and type(blocks) is list and type(reverse) is list
            and type(unattached) is list, "R71 custody inventory missing")

    source_by_key={}
    urls=defaultdict(list)
    ids=defaultdict(list)
    for row in sources:
        key=identity(row)
        require(key not in source_by_key, "duplicate origin-scoped source")
        reading=row.get("candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        original=row.get("original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        require(type(reading) is dict and reading.get("id")==key[1]
                and reading.get("human_link_check") is False
                and type(reading.get("url")) is str
                and reading["url"].startswith("https://")
                and row.get("exact_URL_NO_ALIAS")==reading["url"]
                and row.get("candidate_reading_sha256")==fingerprint(reading),
                "source identity, complete reading, URL or SHA mismatch")
        require(row.get("human_source_and_claim_review")==REVIEW
                and row.get("qualified_safety_review")==REVIEW,
                "unreviewed source escalated")
        old_sha=row.get("original_reading_sha256")
        require(old_sha is None or is_sha(old_sha), "invalid original reading SHA")
        if original is not None:
            require(type(original) is dict and fingerprint(original)==old_sha,
                    "original full source reading was rewritten")
        source_by_key[key]=row
        urls[reading["url"]].append(key)
        ids[key[1]].append(key)
    require(list(source_by_key)==sorted(source_by_key), "source order drift")

    document_blocks=defaultdict(list)
    doc_urls={}
    occurrences=set()
    computed_reverse=defaultdict(list)
    cited_sources=set()
    topical_without=topical_with=0
    all_edges=0
    multi_origin_occurrences=0
    for task in blocks:
        require(type(task) is dict and is_sha(task.get("task_sha256"))
                and fingerprint({k:v for k,v in task.items()
                                 if k!="task_sha256"})==task["task_sha256"],
                "block evidence task fingerprint invalid")
        require(all(task.get(k)==REVIEW for k in (
                "human_claim_support_review","qualified_safety_review",
                "independent_QD_review")),
                "block has fabricated approval")
        kind,slug,bid=task.get("kind"),task.get("slug"),task.get("block_id")
        url=task.get("private_draft_url")
        require(kind in ("article","tool") and type(slug) is str and slug
                and type(bid) is str and bid
                and type(url) is str and url.startswith("/preparedness/")
                and "//" not in url and ".." not in url,
                "invalid document, block ID, or draft-only URL")
        document=(kind,slug)
        require(document not in doc_urls or doc_urls[document]==url,
                "document URL drift across blocks")
        doc_urls[document]=url
        require(bid not in document_blocks[document],
                "duplicate block ID within document")
        document_blocks[document].append(bid)
        text=task.get("DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED")
        require(type(text) is str and text.strip()
                and text_hash(text)==task.get("DOM_text_sha256")
                and is_sha(task.get("R69_document_task_sha256"))
                and type(task.get("start_offset_codepoints")) is int
                and task["start_offset_codepoints"]>=0,
                "block text, original document seal, or offset changed")
        topics=task.get("topic_signals_TRIAGE_NOT_SAFETY_VERDICT")
        edges=task.get("local_citations_NOT_CLAIM_SUPPORT_PROOF")
        neighbors=task.get("adjacent_citations_NAVIGATION_HINTS_NOT_SUPPORT")
        require(type(topics) is list and topics==sorted(set(topics))
                and type(edges) is list and type(neighbors) is list,
                "block topic/edge inventory changed")
        bucket=task.get("triage_bucket_NOT_SAFETY_VERDICT")
        actual=("TOPIC_NO_SAME_BLOCK_CITATION_REVIEW"
                if topics and not edges else
                "TOPIC_HAS_CITATION_SUPPORT_STILL_UNVERIFIED"
                if topics else "GENERAL_EDITORIAL_REVIEW")
        require(bucket==actual, "topic triage is forged or inconsistent")
        if topics and not edges: topical_without+=1
        if topics and edges: topical_with+=1
        for hint in neighbors:
            require(type(hint) is dict and hint.get("NOT_EVIDENCE_OF_SUPPORT") is True
                    and type(hint.get("neighbor_block_id")) is str
                    and type(hint.get("citation_ordinals_NAVIGATION_ONLY")) is list
                    and all(type(n) is int and n>0
                            for n in hint["citation_ordinals_NAVIGATION_ONLY"]),
                    "neighbor navigation misrepresented as source support")
        require(not edges or not neighbors,
                "a direct citation cannot be disguised as an adjacent pointer")
        last_offset=-1
        for edge in edges:
            require(type(edge) is dict and edge.get("human_claim_support_review")==REVIEW
                    and type(edge.get("ordinal")) is int and edge["ordinal"]>0
                    and type(edge.get("unicode_codepoint_offset")) is int
                    and edge["unicode_codepoint_offset"]>last_offset
                    and edge.get("DOM_visibility_NOT_BROWSER_PROOF")==
                        "DOM_TEXT_POTENTIALLY_VISIBLE_NOT_BROWSER_VERIFIED"
                    and type(edge.get("source_id")) is str and edge["source_id"],
                    "citation ordinal, visibility, reviewer state or position drifted")
            last_offset=edge["unicode_codepoint_offset"]
            ck=(kind,slug,edge["ordinal"])
            require(ck not in occurrences,"citation occurrence duplicated")
            occurrences.add(ck)
            variants=edge.get("origin_scoped_source_variants_NOT_ALIASED")
            require(type(variants) is list and variants,
                    "source provenance variants omitted")
            keys=[]
            for variant in variants:
                require(type(variant) is dict and
                        variant.get("human_source_and_claim_review")==REVIEW,
                        "source variant approval fabricated")
                sk=identity(variant)
                require(sk in source_by_key and
                        variant.get("source_id")==edge["source_id"] and
                        variant.get("exact_URL_NOT_ALIAS")==
                            source_by_key[sk]["exact_URL_NO_ALIAS"] and
                        variant.get("complete_source_reading_sha256")==
                            source_by_key[sk]["candidate_reading_sha256"],
                        "unabridged reading, source variant, URL or ID was aliased")
                keys.append(sk)
                cited_sources.add(sk)
                computed_reverse[sk].append([kind,slug,bid,edge["ordinal"]])
            require(keys==sorted(set(keys)),
                    "citation variants silently collapsed, duplicated or reordered")
            preferred=edge.get("preferred_identity_NOT_APPROVED")
            require(preferred is None or
                    (type(preferred) is list and len(preferred)==2
                     and tuple(preferred) in keys),
                    "preferred source is absent from preserved variants")
            multi_origin_occurrences+=int(len(keys)>1)
            all_edges+=1

    require(len(document_blocks)==expected[0]+expected[1]
            and sum(d[0]=="article" for d in document_blocks)==expected[0]
            and sum(d[0]=="tool" for d in document_blocks)==expected[1]
            and len(set(doc_urls.values()))==len(doc_urls),
            "lost document or duplicate WordPress draft URL")
    require(all_edges==counts.get("citation_occurrences_attached_to_DOM_blocks")
            and len(blocks)==counts.get("DOM_text_blocks_review_tasks")
            and topical_without==
                counts.get("keyword_topic_blocks_without_same_block_citation")
            and topical_with==
                counts.get("keyword_topic_blocks_with_local_citation_UNVERIFIED"),
            "passage, citation, or keyword-review conservation failed")
    for row in unattached:
        require(type(row) is dict and row.get("review_state")==REVIEW
                and row.get("kind") in ("article","tool")
                and type(row.get("slug")) is str
                and (row["kind"],row["slug"]) in document_blocks
                and type(row.get("citation_ordinal")) is int
                and row["citation_ordinal"]>0
                and type(row.get("source_id")) is str and row["source_id"],
                "unattached citation corrupted or falsely approved")
        ck=(row["kind"],row["slug"],row["citation_ordinal"])
        require(ck not in occurrences, "unattached citation double counted")
        occurrences.add(ck)
    require(len(unattached)==counts.get("citations_without_DOM_block_unresolved")
            and len(occurrences)==expected[3]
            and all_edges+len(unattached)==expected[3],
            "not all original candidate citation occurrences conserved")

    reverse_seen=set()
    for row in reverse:
        require(type(row) is dict and row.get("human_source_claim_review")==REVIEW,
                "reverse source reviewer approval fabricated")
        key=identity(row)
        require(key in source_by_key and key not in reverse_seen
                and row.get("source_record_sha256")==
                    source_by_key[key]["candidate_reading_sha256"],
                "reverse source evidence identity duplicated or rewritten")
        reverse_seen.add(key)
        actual=row.get("citation_block_occurrences_NOT_SOURCE_SUPPORT_PROOF")
        expected_edges=sorted(computed_reverse[key])
        require(type(actual) is list and actual==expected_edges,
                "reverse source-to-block provenance is missing, aliased or duplicated")
    require(reverse_seen==set(computed_reverse)
            and len(reverse)==counts.get("source_variants_with_cited_DOM_blocks"),
            "orphaned source-citation edges or synthetic reverse evidence")

    def group(mapping, name):
        result=[]
        for value,keys in sorted(mapping.items()):
            if len(keys)<2:
                continue
            rows=[{
                "origin":key[0], "id":key[1],
                "full_candidate_reading_sha256":
                    source_by_key[key]["candidate_reading_sha256"],
                "exact_URL_NOT_CANONICALIZED":
                    source_by_key[key]["exact_URL_NO_ALIAS"],
                "downstream_block_citation_edges_NOT_SUPPORT":
                    sorted(computed_reverse.get(key,[])),
                "human_scope_and_claim_review":REVIEW,
            } for key in sorted(keys)]
            result.append({"collision_type_NOT_AUTOMATIC_ERROR":name,
                           "value":value,"source_readings_NOT_MERGED":rows,
                           "human_scope_resolution":REVIEW})
        return result

    impact=[]
    for (kind,slug),block_ids in sorted(document_blocks.items()):
        linked=sorted({key for key,edges in computed_reverse.items()
                       if any(e[0]==kind and e[1]==slug for e in edges)})
        impact.append({
            "kind":kind,"slug":slug,"draft_url_NOT_PUBLIC":doc_urls[(kind,slug)],
            "block_ids_in_original_order":block_ids,
            "origin_scoped_sources_USED_NOT_SUPPORT_APPROVED":
                [list(x) for x in linked],
            "unabridged_block_count":len(block_ids),
            "reviewer_state":REVIEW,
        })
    result={
        "schema":SCHEMA,"issue":136,"release_state":"HOLD","machine_only":True,
        "R71_unmodified_private_evidence_fingerprint_sha256":
            r71["fingerprint_sha256"],
        "all_complete_source_readings_NOT_APPROVED":deepcopy(sources),
        "all_unabridged_DOM_block_citation_tasks_NOT_APPROVED":deepcopy(blocks),
        "citations_without_DOM_block_UNRESOLVED":deepcopy(unattached),
        "all_document_impact_orders_NOT_APPROVED":impact,
        "shared_exact_URL_collision_review_orders_NOT_APPROVED":
            group(urls,"SHARED_EXACT_URL_NOT_SOURCE_EQUIVALENCE"),
        "reused_source_ID_collision_review_orders_NOT_APPROVED":
            group(ids,"SAME_ID_DIFFERENT_RESEARCH_ORIGINS"),
        "uncited_origin_scoped_sources_NOT_REVIEWED":
            [list(x) for x in sorted(set(source_by_key)-cited_sources)],
        "counts":{
            "articles":expected[0],"tools":expected[1],
            "complete_distinct_origin_scoped_source_readings":len(sources),
            "citation_occurrences":len(occurrences),
            "unabridged_DOM_block_tasks":len(blocks),
            "direct_DOM_citation_occurrences":all_edges,
            "unattached_citation_review_tasks":len(unattached),
            "shared_exact_URL_collision_groups":sum(len(k)>1 for k in urls.values()),
            "reused_source_ID_collision_groups":sum(len(k)>1 for k in ids.values()),
            "multi_variant_citation_occurrences":multi_origin_occurrences,
            "uncited_source_readings_kept":len(source_by_key)-len(cited_sources),
            "same_block_topic_absent_citation_review_candidates":topical_without,
            "same_block_topic_with_citation_still_unverified":topical_with,
            "human_claim_support_reviews":0,"human_qualified_safety_reviews":0,
            "independent_QD_approvals":0,
        },
        "limitations":(
            "The complete unabridged source readings and DOM text are conserved "
            "for private reviewer use. URL/ID collisions are not proof of "
            "equivalent source scope or erroneous citations; same-block and "
            "adjacent citations do not prove claim support. No links fetched. "
            "No qualified medical, food, water, fire, generator or emergency "
            "safety review; no independent QD or WordPress/browser release QA. "
            "The separate mandatory 13-stage integrity pipeline remains HOLD."
        ),
        **{name:False for name in HOLD},
    }
    result["fingerprint_sha256"]=fingerprint(result)
    return result


def csv_collisions(report):
    """Spreadsheet-safe, private collision work queue; no reviewer approval import."""
    sealed(report,SCHEMA)
    buf=io.StringIO(newline="")
    w=csv.writer(buf,lineterminator="\n")
    w.writerow(("collision_type_NOT_VERDICT","exact_value_NOT_NORMALIZED",
                "source_origins_and_IDs_NOT_ALIASED","downstream_impact_NOT_SUPPORT",
                "human_scope_review_NOT_REVIEWED","reviewer_notes_UNTRUSTED"))
    def safe(obj):
        value=(json.dumps(obj,ensure_ascii=False,sort_keys=True)
               if isinstance(obj,(list,dict)) else str(obj))
        trim=value.lstrip(" \t\r\n\ufeff\u200b")
        return "'"+value if value[:1] in ("\t","\r","\n","\ufeff","\u200b") or \
            trim.startswith(("=","+","-","@")) else value
    for key in ("shared_exact_URL_collision_review_orders_NOT_APPROVED",
                "reused_source_ID_collision_review_orders_NOT_APPROVED"):
        for row in report[key]:
            variants=row["source_readings_NOT_MERGED"]
            w.writerow([safe(row["collision_type_NOT_AUTOMATIC_ERROR"]),
                        safe(row["value"]),
                        safe([[r["origin"],r["id"]] for r in variants]),
                        safe([r["downstream_block_citation_edges_NOT_SUPPORT"]
                              for r in variants]),REVIEW,""])
    return buf.getvalue()


def live_report(repo_root=None):
    mod=Path(__file__).with_name("r71_rc_dom_block_source_review.py")
    require(mod.is_file() and not mod.is_symlink(),"missing exact R71 parent module")
    spec=importlib.util.spec_from_file_location("r72_r71_parent",mod)
    require(spec is not None and spec.loader is not None,"R71 module unavailable")
    parent=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    root=Path(repo_root).resolve() if repo_root else None
    r71=parent.live_report(root)
    result=construct(r71)
    require(result==construct(r71),"nondeterministic R72 derived review ledger")
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root",type=Path)
    parser.add_argument("--collision-csv-stdout",action="store_true")
    args=parser.parse_args(argv)
    try:
        result=live_report(args.repo_root)
        if args.collision_csv_stdout:
            sys.stdout.write(csv_collisions(result))
        else:
            print(json.dumps({"schema":SCHEMA,"release_state":"HOLD",
                "fingerprint_sha256":result["fingerprint_sha256"],
                "counts":result["counts"],"all_publication_clearance":False},
                sort_keys=True))
        return 0
    except (Hold,ValueError,KeyError,TypeError,AttributeError,OSError) as e:
        print("R72 PRIVATE RELEASE HOLD: "+str(e),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
