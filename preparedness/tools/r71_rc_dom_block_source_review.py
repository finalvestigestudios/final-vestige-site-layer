#!/usr/bin/env python3
"""R71 PRIVATE HOLD: join every RC DOM text block to exact cited-source identities.

This is a deterministic review queue, NOT claim support, human verification,
medical/emergency clearance, a publishing gate override, or a CMS operation.
All 244 unabridged candidate source readings remain distinct by (origin,id).
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys

SCHEMA = "r71-private-rc-block-to-citation-source-review-v1"
R69_SCHEMA = "r69-private-rc-dom-citation-context-review-v1"
R70_SCHEMA = "r70-private-rc-source-url-and-citation-link-custody-v1"
EXPECTED = (35, 6, 244, 2173)
HOLD = ("may_publish", "independent_QD_approval",
        "qualified_safety_clearance", "human_source_links_verified")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
# Explicitly pinned to the R69 topic vocabulary. Signals are not safety findings.
TOPICS = {
    "WATER_SANITATION": r"\b(?:water|boil(?:ing)?|purif(?:y|ication)|chlorin(?:e|ation)|filter(?:ing)?|sewage)\b",
    "FOOD_STORAGE": r"\b(?:food|cann(?:ing|ed)|botulis(?:m|tic)|refrigerat(?:ed|ion)|freez(?:e|ing)|jerky)\b",
    "MEDICINE_HEALTH": r"\b(?:medicin(?:e|es)|medicat(?:ion|ions)|prescri(?:be|ption)|insulin|pharmac(?:ist|y)|infection|wound|dose|treatment)\b",
    "FIRE_CO_GENERATOR": r"\b(?:fire|smoke|generator|carbon monoxide|ventilat(?:ion|e)|gas leak|flame|fuel|stove|charcoal)\b",
    "EVACUATION_POWER": r"\b(?:evacuat(?:e|ion)|power outage|electric(?:ity|al)|battery|flood|earthquake|shelter)\b",
}
RX = {k:re.compile(v, re.I) for k,v in TOPICS.items()}


class ReviewHold(ValueError):
    """Evidence, citation topology, human-review state, or custody failed closed."""


def need(condition, detail):
    if not condition:
        raise ReviewHold(detail)


def digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def raw_sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sealed(report, schema):
    need(type(report) is dict and report.get("schema") == schema
         and report.get("release_state") == "HOLD"
         and report.get("machine_only") is True
         and all(report.get(k) is False for k in HOLD)
         and type(report.get("fingerprint_sha256")) is str
         and HEX64.fullmatch(report["fingerprint_sha256"]) is not None
         and digest({k:v for k,v in report.items()
                     if k != "fingerprint_sha256"}) == report["fingerprint_sha256"],
         schema + ": missing/altered provenance or false human safety/publish approval")


def signals(text):
    return sorted(k for k, rx in RX.items() if rx.search(text))


def _check_unreviewed(record, keys, where):
    need(type(record) is dict and
         all(record.get(k) == "NOT_REVIEWED" for k in keys),
         where + ": fabricated reviewer approval or missing HOLD marker")


def _identities(variants):
    need(type(variants) is list, "source variant list absent")
    out = []
    for key in variants:
        need(type(key) is list and len(key) == 2 and
             all(type(v) is str and v for v in key),
             "invalid origin-scoped source identity")
        out.append(tuple(key))
    need(out == sorted(set(out)), "source identity variants reordered, merged, or duplicated")
    return out


def construct(dom_report, url_report, *, expected=EXPECTED):
    """Pure, offline, lossless crosswalk; does not retrieve or open any URLs."""
    need(type(expected) is tuple and len(expected) == 4 and
         all(type(n) is int and n > 0 for n in expected), "invalid R71 census")
    sealed(dom_report, R69_SCHEMA)
    sealed(url_report, R70_SCHEMA)
    need(url_report.get("R69_DOM_citation_context_fingerprint_sha256") ==
         dom_report["fingerprint_sha256"], "R69/R70 provenance chain disconnected")
    c69, c70 = dom_report.get("counts"), url_report.get("counts")
    need(type(c69) is dict and type(c70) is dict and
         tuple(c69.get(k) for k in ("candidate_articles", "candidate_tools",
                                   "candidate_source_records_kept_in_R68",
                                   "candidate_citation_occurrences_accounted_for")) == expected
         and tuple(c70.get(k) for k in ("candidate_articles", "candidate_tools",
                                       "source_records_conserved",
                                       "citation_occurrences_conserved")) == expected
         and c69.get("human_claim_or_safety_checks_performed_BY_R69") == 0
         and c70.get("human_url_or_claim_checks_performed_BY_R70") == 0,
         "R69/R70 document, source or citation conservation/count contract broken")

    source_rows = url_report.get("all_244_source_URL_and_reading_work_orders_NOT_APPROVED")
    cite_rows = url_report.get("all_2173_citation_URL_identity_work_orders_NOT_APPROVED")
    documents = dom_report.get("all_document_DOM_text_and_citation_review_orders_NOT_APPROVED")
    need(type(source_rows) is list and len(source_rows) == expected[2]
         and type(cite_rows) is list and len(cite_rows) == expected[3]
         and type(documents) is list and len(documents) == expected[0]+expected[1],
         "unabridged source, citation or document inventory is incomplete")

    source_index = {}
    source_inventory = []
    for source in source_rows:
        _check_unreviewed(source, ("human_link_review", "human_claim_support_review",
                                  "qualified_safety_review"), "source reading")
        key = (source.get("source_origin"), source.get("source_id"))
        need(all(type(x) is str and x for x in key) and key not in source_index,
             "duplicate/missing origin-scoped source record")
        reading = source.get("candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        need(type(reading) is dict and reading.get("id") == key[1]
             and reading.get("human_link_check") is False
             and digest(reading) == source.get("source_record_sha256")
             and reading.get("url") == source.get("exact_URL_NO_CANONICAL_ALIAS"),
             "source text/reading depth, identity, fingerprint or exact URL changed")
        source_index[key] = source
        source_inventory.append({
            "source_origin":key[0], "source_id":key[1],
            "candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED":reading,
            "original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED":
                source.get("original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"),
            "candidate_reading_sha256":source["source_record_sha256"],
            "original_reading_sha256":source.get("original_record_sha256"),
            "exact_URL_NO_ALIAS":reading["url"],
            "URL_structural_blockers_NOT_LINK_VERDICT":
                source.get("URL_structural_blockers_NOT_HTTP_VERDICT"),
            "URL_manual_flags_NOT_LINK_VERDICT":
                source.get("URL_manual_review_signals_NOT_VERDICT"),
            "human_source_and_claim_review":"NOT_REVIEWED",
            "qualified_safety_review":"NOT_REVIEWED",
        })
    source_inventory.sort(key=lambda row:(row["source_origin"],row["source_id"]))

    citation_index = {}
    for citation in cite_rows:
        _check_unreviewed(citation, ("human_claim_support_review", "qualified_safety_review"),
                          "candidate citation")
        key = (citation.get("kind"),citation.get("slug"),citation.get("citation_ordinal"))
        need(key not in citation_index and key[0] in ("article","tool")
             and type(key[1]) is str and type(key[2]) is int and key[2] > 0
             and type(citation.get("unicode_codepoint_offset")) is int
             and citation["unicode_codepoint_offset"] >= 0
             and type(citation.get("source_id")) is str,
             "duplicate/invalid candidate citation identity or offset")
        variants = _identities(citation.get("all_candidate_origin_scoped_identities_NOT_ALIASED"))
        urls = citation.get("all_candidate_exact_urls_NOT_DEDUPLICATED")
        need(type(urls) is list and len(urls) == len(variants) and variants
             and all(k in source_index and
                     source_index[k]["exact_URL_NO_CANONICAL_ALIAS"] == u
                     for k,u in zip(variants,urls)),
             "citation source reading/URL variant silently merged or redirected")
        citation_index[key] = citation

    doc_keys, urls_seen, used_citations = set(), set(), set()
    all_blocks, unattached, source_to_blocks = [], [], defaultdict(list)
    topical_missing, topical_with_cite, direct_edges = 0,0,0
    for doc in sorted(documents, key=lambda d:(d.get("kind",""),d.get("slug",""))):
        _check_unreviewed(doc, ("human_source_review", "qualified_safety_review",
                                "independent_QD_review"), "DOM document")
        need(type(doc.get("task_sha256")) is str and
             digest({k:v for k,v in doc.items() if k != "task_sha256"}) ==
             doc["task_sha256"], "DOM task content fingerprint altered")
        kind,slug = doc.get("kind"),doc.get("slug")
        key = (kind,slug)
        url = doc.get("proposed_url_PRIVATE_DRAFT_ONLY")
        need(kind in ("article","tool") and type(slug) is str and slug
             and key not in doc_keys and type(url) is str and url.startswith("/preparedness/")
             and url not in urls_seen, "duplicate document or WordPress draft URL")
        doc_keys.add(key); urls_seen.add(url)
        blocks = doc.get("full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED")
        citations = doc.get("citation_visibility_audit_NOT_BROWSER_PROOF")
        need(type(blocks) is list and type(citations) is list,
             "DOM text blocks/citation rows omitted")
        block_index, block_order = {}, []
        for block in blocks:
            _check_unreviewed(block, ("human_claim_support_review",), "DOM text block")
            bid,text = block.get("block_id"),block.get("DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED")
            need(type(bid) is str and bid and bid not in block_index
                 and type(text) is str and text.strip()
                 and raw_sha(text) == block.get("DOM_text_sha256")
                 and type(block.get("start_offset_codepoints")) is int
                 and block["start_offset_codepoints"] >= 0,
                 "missing/duplicate DOM block, changed unabridged text or text hash")
            topical = block.get("review_topic_signals_NOT_SAFETY_CLASSIFICATION")
            need(type(topical) is list and topical == signals(text),
                 "R69 keyword topic signals silently altered")
            offsets = block.get("citation_offsets_in_DOM_text")
            need(type(offsets) is list and
                 all(type(x) is int and x >= 0 for x in offsets) and
                 offsets == sorted(set(offsets)),
                 "DOM block local citation offsets altered/duplicated")
            flags = block.get("review_flags_NOT_SAFETY_VERDICTS")
            expected_flags = (
                ["TOPIC_SIGNAL_WITH_NO_CITATION_IN_THIS_DOM_BLOCK_REVIEW_CONTEXT"]
                if topical and not offsets else
                ["TOPIC_SIGNAL_WITH_CITATION_NOT_CLAIM_SUPPORT_PROOF"]
                if topical else [])
            need(flags == expected_flags, "R69 topic/no-local-citation review flag changed")
            block_index[bid] = block
            block_order.append(bid)

        nearest_rows = defaultdict(list)
        for cite in citations:
            _check_unreviewed(cite, ("human_claim_support_review",), "R69 citation")
            ck = (kind,slug,cite.get("ordinal"))
            need(ck in citation_index and ck not in used_citations,
                 "orphan, repeated, or missing R70 citation")
            r70cite = citation_index[ck]
            need(cite.get("source_id") == r70cite["source_id"]
                 and cite.get("unicode_codepoint_offset") ==
                     r70cite["unicode_codepoint_offset"]
                 and cite.get("DOM_CLASSIFICATION_NOT_BROWSER_PROOF") ==
                     r70cite["DOM_visibility_NOT_BROWSER_VERIFIED"]
                 and cite.get("all_source_identity_variants_NOT_ALIASED") ==
                     r70cite["all_candidate_origin_scoped_identities_NOT_ALIASED"]
                 and cite.get("candidate_source_identity_OR_NULL") ==
                     r70cite["preferred_candidate_identity_NOT_APPROVED"],
                 "R69/R70 citation text offset, visibility or origin scope changed")
            used_citations.add(ck)
            nearest = cite.get("nearest_HTML_text_block_id_OR_NULL")
            need(nearest is None or nearest in block_index,
                 "citation assigned to nonexistent DOM block")
            if nearest is None:
                unattached.append({
                    "kind":kind,"slug":slug,"citation_ordinal":ck[2],
                    "source_id":cite["source_id"],"review_state":"NOT_REVIEWED"})
            else:
                nearest_rows[nearest].append((cite,r70cite))

        for idx,bid in enumerate(block_order):
            block=block_index[bid]
            local=sorted(nearest_rows.get(bid,[]),
                         key=lambda x:x[0]["unicode_codepoint_offset"])
            need([c["unicode_codepoint_offset"] for c,_ in local] ==
                 block["citation_offsets_in_DOM_text"],
                 "DOM-block local citation / nearest-block mapping mismatch")
            edges=[]
            for c,u in local:
                keys = _identities(u["all_candidate_origin_scoped_identities_NOT_ALIASED"])
                variants = []
                for key_source,exact_url in zip(keys,u["all_candidate_exact_urls_NOT_DEDUPLICATED"]):
                    evidence = source_index[key_source]
                    variants.append({
                        "source_origin":key_source[0], "source_id":key_source[1],
                        "exact_URL_NOT_ALIAS":exact_url,
                        "complete_source_reading_sha256":evidence["source_record_sha256"],
                        "human_source_and_claim_review":"NOT_REVIEWED",
                    })
                    source_to_blocks[key_source].append(
                        [kind,slug,bid,c["ordinal"]])
                edges.append({
                    "ordinal":c["ordinal"],
                    "source_id":c["source_id"],
                    "unicode_codepoint_offset":c["unicode_codepoint_offset"],
                    "DOM_visibility_NOT_BROWSER_PROOF":
                        c["DOM_CLASSIFICATION_NOT_BROWSER_PROOF"],
                    "origin_scoped_source_variants_NOT_ALIASED":variants,
                    "preferred_identity_NOT_APPROVED":
                        u["preferred_candidate_identity_NOT_APPROVED"],
                    "human_claim_support_review":"NOT_REVIEWED",
                })
                direct_edges += 1
            topic=block["review_topic_signals_NOT_SAFETY_CLASSIFICATION"]
            if topic and not edges: topical_missing += 1
            if topic and edges: topical_with_cite += 1
            # Neighbor citations are *navigation hints*, never inferred support.
            neighbors = []
            if not edges:
                for j in (idx-1,idx+1):
                    if 0 <= j < len(block_order):
                        name=block_order[j]
                        linked=nearest_rows.get(name,[])
                        if linked:
                            neighbors.append({
                                "neighbor_block_id":name,
                                "citation_ordinals_NAVIGATION_ONLY":
                                    [p[0]["ordinal"] for p in linked],
                                "NOT_EVIDENCE_OF_SUPPORT":True,
                            })
            task={
                "kind":kind,"slug":slug,"private_draft_url":url,
                "block_id":bid,"html_tag":block.get("html_tag"),
                "html_element_id_OR_NULL":block.get("html_element_id_OR_NULL"),
                "start_offset_codepoints":block["start_offset_codepoints"],
                "DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED":
                    block["DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED"],
                "DOM_text_sha256":block["DOM_text_sha256"],
                "topic_signals_TRIAGE_NOT_SAFETY_VERDICT":topic,
                "local_citations_NOT_CLAIM_SUPPORT_PROOF":edges,
                "adjacent_citations_NAVIGATION_HINTS_NOT_SUPPORT":neighbors,
                "triage_bucket_NOT_SAFETY_VERDICT":
                    "TOPIC_NO_SAME_BLOCK_CITATION_REVIEW"
                    if topic and not edges else
                    "TOPIC_HAS_CITATION_SUPPORT_STILL_UNVERIFIED"
                    if topic else "GENERAL_EDITORIAL_REVIEW",
                "R69_document_task_sha256":doc["task_sha256"],
                "human_claim_support_review":"NOT_REVIEWED",
                "qualified_safety_review":"NOT_REVIEWED",
                "independent_QD_review":"NOT_REVIEWED",
            }
            task["task_sha256"] = digest(task)
            all_blocks.append(task)

    need(len(doc_keys) == expected[0]+expected[1]
         and sum(k[0]=="article" for k in doc_keys) == expected[0]
         and sum(k[0]=="tool" for k in doc_keys) == expected[1]
         and len(used_citations) == expected[3]
         and len(citation_index) == expected[3]
         and topical_missing == c69.get("review_topic_blocks_without_same_block_citation"),
         "lost article/tool/citation or divergent R69 topic review queue")
    need(direct_edges+len(unattached) == expected[3],
         "citation occurrences not accounted for by block or unattached queue")
    reverse = [{
        "source_origin":origin, "source_id":sid,
        "source_record_sha256":source_index[(origin,sid)]["source_record_sha256"],
        "citation_block_occurrences_NOT_SOURCE_SUPPORT_PROOF":
            sorted(edges), "human_source_claim_review":"NOT_REVIEWED",
    } for (origin,sid),edges in sorted(source_to_blocks.items())]
    counts={
        "candidate_articles":expected[0], "candidate_tools":expected[1],
        "unabridged_source_readings_conserved":len(source_inventory),
        "candidate_citations_conserved":len(citation_index),
        "DOM_text_blocks_review_tasks":len(all_blocks),
        "citation_occurrences_attached_to_DOM_blocks":direct_edges,
        "citations_without_DOM_block_unresolved":len(unattached),
        "keyword_topic_blocks_without_same_block_citation":topical_missing,
        "keyword_topic_blocks_with_local_citation_UNVERIFIED":topical_with_cite,
        "source_variants_with_cited_DOM_blocks":len(reverse),
        "human_source_claim_or_safety_reviews_by_R71":0,
    }
    result={
        "schema":SCHEMA,"issue":136,"release_state":"HOLD","machine_only":True,
        "R69_original_RC_DOM_evidence_fingerprint_sha256":
            dom_report["fingerprint_sha256"],
        "R70_exact_URL_source_evidence_fingerprint_sha256":
            url_report["fingerprint_sha256"],
        "all_244_unabridged_source_reading_review_records_NOT_APPROVED":
            source_inventory,
        "all_DOM_block_claim_and_exact_source_review_tasks_NOT_APPROVED":
            all_blocks,
        "citations_with_no_DOM_block_NOT_APPROVED":unattached,
        "source_to_cited_block_reverse_custody_NOT_APPROVED":reverse,
        "counts":counts,
        "limitations":(
            "R71 is structural private work-order triage only. Same-block or "
            "adjacent citations DO NOT substantiate surrounding claims. Topic "
            "keywords are neither expert risk assessments nor unsupported-claim "
            "findings. Source URLs are not accessed or human checked; complete "
            "reading notes remain distinct by origin and source ID. HTML "
            "visibility is not browser or screen-reader proof. No expert "
            "medical/emergency safety clearance, crosswalk rebaseline, "
            "independent QD approval, WordPress write, or release authority."
        ),
        **{k:False for k in HOLD},
    }
    result["fingerprint_sha256"] = digest(result)
    return result


def csv_tasks(report):
    sealed(report, SCHEMA)
    sink = io.StringIO(newline="")
    out = csv.writer(sink, lineterminator="\n")
    out.writerow(["kind","slug","private_draft_url","block_id","html_tag",
        "topic_signals_NOT_VERDICT","triage_bucket_NOT_VERDICT",
        "unabridged_DOM_text_NOT_VERIFIED","local_source_variants_NO_ALIAS",
        "nearby_citation_ordinals_NAVIGATION_NOT_SUPPORT",
        "human_claim_support_NOT_REVIEWED","qualified_safety_NOT_REVIEWED",
        "reviewer_notes_UNTRUSTED"])
    def safe(value):
        raw = (json.dumps(value, ensure_ascii=False, sort_keys=True)
               if isinstance(value,(dict,list)) else
               "" if value is None else str(value))
        stripped = raw.lstrip("\ufeff\u200b \t\r\n")
        return "'" + raw if raw[:1] in ("\t","\r","\n","\ufeff","\u200b") or \
            stripped.startswith(("=","+","-","@")) else raw
    for task in report["all_DOM_block_claim_and_exact_source_review_tasks_NOT_APPROVED"]:
        out.writerow([safe(x) for x in (
            task["kind"],task["slug"],task["private_draft_url"],
            task["block_id"],task["html_tag"],task["topic_signals_TRIAGE_NOT_SAFETY_VERDICT"],
            task["triage_bucket_NOT_SAFETY_VERDICT"],
            task["DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"],
            [v for edge in task["local_citations_NOT_CLAIM_SUPPORT_PROOF"]
             for v in edge["origin_scoped_source_variants_NOT_ALIASED"]],
            task["adjacent_citations_NAVIGATION_HINTS_NOT_SUPPORT"],
            "NOT_REVIEWED","NOT_REVIEWED","")])
    return sink.getvalue()


def _module(filename):
    path = Path(__file__).with_name(filename)
    need(path.is_file() and not path.is_symlink(),
         "missing exact parent custody module: "+filename)
    spec = importlib.util.spec_from_file_location("r71_"+filename.replace(".","_"), path)
    need(spec is not None and spec.loader is not None, "module load failed")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def live_report(repo_root=None):
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]
    r67 = _module("r67_rc_source_custody_crosswalk.py").live_report(root)
    r68 = _module("r68_rc_document_citation_scope.py").live_report(root)
    r69 = _module("r69_rc_citation_dom_review.py").construct(r68)
    r70 = _module("r70_rc_source_url_citation_custody.py").construct(r67,r68,r69)
    result=construct(r69,r70)
    need(result == construct(r69,r70), "non-deterministic R71 review ledger")
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--task-csv-stdout", action="store_true")
    args=parser.parse_args(argv)
    try:
        report=live_report(args.repo_root)
        if args.task_csv_stdout:
            sys.stdout.write(csv_tasks(report))
        else:
            print(json.dumps({"schema":SCHEMA,"release_state":"HOLD",
                  "fingerprint_sha256":report["fingerprint_sha256"],
                  "counts":report["counts"],"all_publication_clearance":False},
                  sort_keys=True))
        return 0
    except (ReviewHold,ValueError,KeyError,TypeError,AttributeError,OSError) as exc:
        print("R71 PRIVATE HOLD: "+str(exc), file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
