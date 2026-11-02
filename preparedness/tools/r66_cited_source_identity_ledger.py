#!/usr/bin/env python3
"""R66 private HOLD: lossless cited-source identity review index for R65's 35+1 originals.

This is an exact, *lexical* source-identity audit. Same URL never means same
research reading; a matching citation never proves a claim or any safety advice.
No network, WordPress, CMS, publishing, source mutation, or external writes.
"""
from __future__ import annotations

from collections import defaultdict
import argparse
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "r66-private-original-cited-source-identity-ledger-v1"
HOLD = ("may_publish", "independent_QD_approval",
        "qualified_safety_clearance", "human_source_links_verified")
EXPECTED = (35, 1, 1959, 1952, 7)
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
R65_NAME = "r65_integrated_citation_conservation.py"


class SourceIdentityHold(ValueError):
    """Private evidence, citation identity or release-control integrity failure."""


def need(condition, message):
    if not condition:
        raise SourceIdentityHold(message)


def _parent():
    path = Path(__file__).with_name(R65_NAME)
    need(path.is_file() and not path.is_symlink(),
         "original R65 conservation gate missing or symlinked")
    spec = importlib.util.spec_from_file_location("r66_original_r65", path)
    need(spec is not None and spec.loader is not None, "R65 cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def sha(value):
    return type(value) is str and HEX64.fullmatch(value) is not None


def _is_http(value):
    if type(value) is not str or not value:
        return False
    try:
        result = urlsplit(value)
        return result.scheme.lower() in ("http", "https") and bool(result.netloc)
    except ValueError:
        return False


def construct(parent, *, expected=EXPECTED):
    """Pure deterministic core for synthetic tests; NOT the production gate.

    Only live_report() regenerates/validates R58 and seven-contributor Git-object
    provenance. Never use a caller-supplied document to assert live readiness.
    """
    need(type(parent) is dict and type(expected) is tuple and len(expected) == 5
         and all(type(x) is int and x >= 0 for x in expected)
         and expected[0] + expected[1] > 0
         and expected[2] == expected[3] + expected[4], "invalid evidence census")
    need(parent.get("schema") == "r65-private-35-article-citation-conservation-v1"
         and parent.get("release_state") == "HOLD"
         and parent.get("machine_only") is True
         and all(parent.get(field) is False for field in HOLD)
         and sha(parent.get("fingerprint_sha256"))
         and digest({k:v for k,v in parent.items()
                     if k != "fingerprint_sha256"}) == parent["fingerprint_sha256"],
         "original R65 fingerprint or publication restrictions invalid")
    article_rows = parent.get("all_35_original_article_review_work_orders_NOT_APPROVED")
    tool_row = parent.get("original_water_planning_tool_review_work_order_NOT_APPROVED")
    need(type(article_rows) is list and type(tool_row) is dict and
         len(article_rows) == expected[0] and expected[1] == 1,
         "missing original article/tool work orders")
    counts = parent.get("counts")
    need(type(counts) is dict and tuple(counts.get(field) for field in
         ("integrated_articles", "original_water_planning_tools",
          "integrated_citation_occurrences",
          "original_article_citation_occurrences",
          "original_water_tool_citation_occurrences")) == expected,
         "original 35+1 citation census not conserved")

    source_by_identity = {}
    source_refs = defaultdict(list)
    by_url = defaultdict(set)
    by_article = []
    observed_citations = set()
    seen_slugs = set()
    tool_count = 0
    article_citation_count = 0
    for doc in sorted([*article_rows, tool_row], key=lambda row: row["article_slug"]):
        need(type(doc) is dict and type(doc.get("article_slug")) is str
             and bool(doc["article_slug"]) and
             doc["article_slug"] not in seen_slugs and
             sha(doc.get("integrated_article_html_sha256"))
             and doc.get("human_source_review") == "NOT_REVIEWED"
             and doc.get("qualified_safety_review") == "NOT_REVIEWED",
             "duplicate, missing or purportedly cleared original document")
        slug = doc["article_slug"]
        seen_slugs.add(slug)
        tool = slug == "water-planner"
        tool_count += int(tool)
        need((not tool or doc is tool_row) and (tool or doc is not tool_row),
             "water tool or original article identity exchanged")
        flags = doc.get("review_flags_NOT_SAFETY_VERDICTS")
        need(type(flags) is list and bool(flags) and
             all(type(f) is str and bool(f) for f in flags) and
             flags == sorted(set(flags)),
             "missing/altered original unreviewed document flags")
        citations = doc.get("all_original_integrated_citation_and_reading_evidence_UNABRIDGED")
        need(type(citations) is list and len(citations)>0,
             "original citations or their readings disappeared")
        offsets = set()
        doc_ids = set()
        document_tokens = []
        for row in citations:
            need(type(row) is dict and
                 type(row.get("source_id")) is str and bool(row["source_id"])
                 and type(row.get("source_origin")) is str and bool(row["source_origin"])
                 and type(row.get("original_codepoint_offset")) is int
                 and row["original_codepoint_offset"] >= 0
                 and sha(row.get("R58_work_order_sha256"))
                 and type(row.get("unabridged_original_visible_context_NOT_SUPPORT_PROOF")) is str,
                 "original R58 citation identity/context disappeared")
            sid = row["source_id"]
            origin = row["source_origin"]
            offset = row["original_codepoint_offset"]
            work = row["R58_work_order_sha256"]
            need(offset not in offsets and work not in observed_citations,
                 "duplicate exact citation offset or original work-order ID")
            offsets.add(offset)
            observed_citations.add(work)
            reading = row.get("unabridged_original_source_reading_NOT_HUMAN_CHECKED")
            relation = row.get("unabridged_original_relationship_NOT_HUMAN_CHECKED")
            need(type(reading) is dict and type(relation) is dict
                 and reading.get("id") == sid and reading.get("_origin") == origin
                 and relation.get("slug") == slug and
                 relation.get("source_id") == sid and
                 relation.get("source_origin") == origin,
                 "original source-reading or article/source relationship altered")
            key = (origin, sid)
            reading_sha = digest(reading)
            if key in source_by_identity:
                need(source_by_identity[key]["source_record_sha256"] == reading_sha,
                     "one original source identity has conflicting reading payloads")
            else:
                source_by_identity[key] = {
                    "source_id": sid,
                    "source_origin": origin,
                    "source_record_sha256": reading_sha,
                    "original_unabridged_source_record_NOT_HUMAN_VERIFIED": reading,
                }
            url = reading.get("url")
            # An absent/invalid URL stays on the work queue; it is NEVER dropped.
            need(url is None or type(url) is str,
                 "original URL has an unsafe non-string value")
            url_key = url if type(url) is str else None
            by_url[("exact", url_key)].add(key)
            ref = {
                "original_R58_citation_work_order_sha256": work,
                "original_document_slug": slug,
                "original_document_html_sha256": doc["integrated_article_html_sha256"],
                "original_unicode_codepoint_offset": offset,
                "original_visible_claim_context_UNABRIDGED_NOT_SUPPORT_PROOF":
                    row["unabridged_original_visible_context_NOT_SUPPORT_PROOF"],
                "original_article_source_relationship_UNABRIDGED_NOT_SUPPORT_PROOF":
                    relation,
                "original_R65_document_flags_NOT_SAFETY_VERDICTS": list(flags),
                "is_original_water_planning_tool": tool,
            }
            source_refs[key].append(ref)
            doc_ids.add(key)
            document_tokens.append({
                "R58_work_order_sha256": work, "source_origin": origin,
                "source_id": sid, "original_offset_codepoints": offset,
                "source_record_sha256": reading_sha,
            })
        if not tool:
            article_citation_count += len(document_tokens)
        by_article.append({
            "original_slug": slug, "original_html_sha256": doc["integrated_article_html_sha256"],
            "is_water_planner_tool": tool,
            "original_R65_work_order_sha256": digest(doc),
            "contributor_evidence_present_NOT_APPROVED":
                doc.get("frozen_and_proposed_contributor_custody_OR_NULL") is not None,
            "flags_NOT_SAFETY_VERDICTS": list(flags),
            "unabridged_original_citation_identity_order":
                sorted(document_tokens, key=lambda item:item["original_offset_codepoints"]),
            "distinct_selected_original_source_identities": [
                {"source_origin": origin, "source_id":sid}
                for origin,sid in sorted(doc_ids)],
            "human_source_review":"NOT_REVIEWED", "qualified_safety_review":"NOT_REVIEWED",
        })
    need(tool_count == 1 and "water-planner" in seen_slugs and
         len(observed_citations) == expected[2] and
         article_citation_count == expected[3] and
         len(tool_row["all_original_integrated_citation_and_reading_evidence_UNABRIDGED"]) ==
         expected[4], "loss of original article or water tool citations")

    shared = {key: identities for key, identities in by_url.items()
              if len(identities) > 1}
    source_rows = []
    for key in sorted(source_by_identity):
        row = source_by_identity[key]
        reading = row["original_unabridged_source_record_NOT_HUMAN_VERIFIED"]
        url = reading.get("url")
        references = sorted(source_refs[key], key=lambda ref: (
            ref["original_document_slug"], ref["original_unicode_codepoint_offset"],
            ref["original_R58_citation_work_order_sha256"]))
        group_members = by_url[("exact",url if type(url) is str else None)]
        flags = set()
        if len(group_members)>1:
            flags.add("EXACT_URL_SHARED_BY_DISTINCT_SOURCE_IDENTITIES_NO_ALIAS")
        if not _is_http(url):
            flags.add("MISSING_OR_INVALID_HTTP_URL_HUMAN_RETRIEVAL_REQUIRED")
        if any(r["is_original_water_planning_tool"] for r in references):
            flags.add("ORIGINAL_WATER_TOOL_SOURCE_NOT_HUMAN_REVIEWED")
        if any("CONTRIBUTOR_BODY_CHANGED_UNREVIEWED" in
               r["original_R65_document_flags_NOT_SAFETY_VERDICTS"]
               for r in references):
            flags.add("CITED_IN_CHANGED_CONTRIBUTOR_ARTICLE_NOT_APPROVED")
        if any("INTEGRATED_ONLY_SIX_ARTICLES_OUTSIDE_SEVEN_R14_CLUSTERS" in
               r["original_R65_document_flags_NOT_SAFETY_VERDICTS"]
               for r in references):
            flags.add("CITED_IN_INTEGRATED_ONLY_ARTICLE_OUTSIDE_SEVEN_CLUSTERS")
        if not flags:
            flags.add("UNREVIEWED_SOURCE_READING_NO_MACHINE_SAFETY_VERDICT")
        source_rows.append({
            **row,
            "exact_original_url_NO_CANONICALIZATION_OR_ALIAS": url,
            "separate_source_identities_with_same_exact_url": [
                {"source_origin":x[0], "source_id":x[1]}
                for x in sorted(group_members)],
            "all_original_citation_occurrences_AND_RELATIONSHIPS_UNABRIDGED":
                references,
            "flags_NOT_FACT_CHECK_OR_SAFETY_APPROVAL":sorted(flags),
            "human_source_retrieval_state":"NOT_REVIEWED",
            "human_claim_support_state":"NOT_REVIEWED",
            "qualified_safety_review_state":"NOT_REVIEWED",
        })
    groups = []
    for (label,url), keys in sorted(shared.items(), key=lambda kv:(str(kv[0][1]),sorted(kv[1]))):
        groups.append({
            "exact_original_url_NOT_CANONICALIZED":url,
            "distinct_source_identities_NOT_MERGED":[
                {"source_origin":k[0],"source_id":k[1],
                 "original_reading_sha256":source_by_identity[k]["source_record_sha256"]}
                for k in sorted(keys)],
            "state":"NEEDS_INDEPENDENT_HUMAN_URL_AND_CLAIM_REVIEW",
        })
    need(len(source_rows) == len(source_by_identity)
         and len(groups) == len(shared)
         and sum(len(x["all_original_citation_occurrences_AND_RELATIONSHIPS_UNABRIDGED"])
                 for x in source_rows) == expected[2]
         and len({y["original_R58_citation_work_order_sha256"]
                  for x in source_rows for y in
                  x["all_original_citation_occurrences_AND_RELATIONSHIPS_UNABRIDGED"]})
         == expected[2], "citation/source identities dropped or multiplied")
    report = {
        "schema":SCHEMA, "issue":136, "release_state":"HOLD", "machine_only":True,
        "parent_R65_full_35_plus_tool_evidence_sha256":parent["fingerprint_sha256"],
        "all_cited_original_source_identitites_NOT_APPROVED":source_rows,
        "all_35_original_articles_plus_water_tool_NOT_APPROVED":
            sorted(by_article,key=lambda x:x["original_slug"]),
        "shared_exact_URL_groups_DISTINCT_NOT_ALIASED":groups,
        "counts":{
            "original_articles":expected[0],
            "original_water_tools":expected[1],
            "all_original_citation_occurrences":expected[2],
            "article_citation_occurrences":expected[3],
            "water_tool_citation_occurrences":expected[4],
            "distinct_original_CITED_source_origin_and_id_pairs":len(source_rows),
            "distinct_exact_source_url_values_INCLUDING_NULL":len(by_url),
            "shared_exact_url_groups_WITHOUT_ALIAS":len(groups),
            "source_identities_in_shared_url_groups":
                sum(len(k) for k in shared.values()),
            "source_references_in_changed_contributor_bodies":
                sum(len(x["all_original_citation_occurrences_AND_RELATIONSHIPS_UNABRIDGED"])
                    for x in source_rows if
                    "CITED_IN_CHANGED_CONTRIBUTOR_ARTICLE_NOT_APPROVED" in
                    x["flags_NOT_FACT_CHECK_OR_SAFETY_APPROVAL"]),
        },
        "limitations":("CITED sources only: uncited and proposed contributor source records "
                        "remain in R57/R63/R65 evidence. Exact URLs never imply same "
                        "research reading; fingerprints only bind structural input. "
                        "No retrieved link, claim support, current safety advice, "
                        "human review, independent QD or publication is approved."),
        **{field:False for field in HOLD},
    }
    report["fingerprint_sha256"] = digest(report)
    return report


def _spreadsheet_cell(value):
    """Spreadsheet-neutralized derivative display; original evidence is in JSON."""
    text = str(value if value is not None else "")
    if text.lstrip().startswith(("=", "+", "-", "@")) or text[:1] in ("\t","\r","\n"):
        return "'" + text
    return text


def task_csv(report):
    """Private review-task projection, never an evidence import or approval record."""
    need(type(report) is dict and report.get("schema") == SCHEMA and
         report.get("release_state") == "HOLD" and
         report.get("may_publish") is False and
         sha(report.get("fingerprint_sha256")) and
         digest({k:v for k,v in report.items() if k!="fingerprint_sha256"}) ==
         report["fingerprint_sha256"], "unsigned/unheld review ledger rejected")
    sink = io.StringIO(newline="")
    writer = csv.writer(sink, lineterminator="\n")
    writer.writerow(["original_origin", "original_source_id", "original_reading_sha256",
        "exact_original_url_NOT_ALIASED", "citation_occurrence_count",
        "referencing_document_count", "separate_identities_at_exact_url",
        "review_flags_NOT_VERDICTS", "HUMAN_SOURCE_CHECK_NOT_REVIEWED",
        "HUMAN_CLAIM_SUPPORT_NOT_REVIEWED", "QUALIFIED_SAFETY_NOT_REVIEWED",
        "reviewer_notes_UNTRUSTED_DRAFT"])
    for row in report["all_cited_original_source_identitites_NOT_APPROVED"]:
        refs = row["all_original_citation_occurrences_AND_RELATIONSHIPS_UNABRIDGED"]
        writer.writerow([_spreadsheet_cell(x) for x in (
            row["source_origin"], row["source_id"], row["source_record_sha256"],
            row["exact_original_url_NO_CANONICALIZATION_OR_ALIAS"],
            len(refs), len({r["original_document_slug"] for r in refs}),
            len(row["separate_source_identities_with_same_exact_url"]),
            ";".join(row["flags_NOT_FACT_CHECK_OR_SAFETY_APPROVAL"]),
            "NOT_REVIEWED","NOT_REVIEWED","NOT_REVIEWED","",
        )])
    return sink.getvalue()


def live_report(repo_root, remote):
    """Always build verified live evidence from originals and seven Git refs."""
    original = _parent()
    evidence = original.real_evidence(repo_root, remote)
    verified_parent = original.report(*evidence)
    need(verified_parent == original.report(*evidence),
         "non-deterministic original R65 evidence")
    return construct(verified_parent)  # defaults cannot be overridden


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root",type=Path,default=ROOT.parent)
    parser.add_argument("--remote",default="origin")
    parser.add_argument("--task-csv-stdout",action="store_true",
                        help="print private review CSV instead of JSON summary; no file writes")
    args = parser.parse_args(argv)
    try:
        report = live_report(args.repo_root, args.remote)
        need(report == live_report(args.repo_root, args.remote),
             "non-deterministic original cited-source identity ledger")
        if args.task_csv_stdout:
            sys.stdout.write(task_csv(report))
        else:
            print(json.dumps({"schema":SCHEMA, "release_state":"HOLD",
                "may_publish":False, "no_external_writes":True,
                "counts":report["counts"],
                "fingerprint_sha256":report["fingerprint_sha256"]},
                sort_keys=True,ensure_ascii=False))
        return 0
    except (SourceIdentityHold, ValueError, OSError, KeyError, TypeError,
            UnicodeError, ImportError, AttributeError) as error:
        print("R66 PRIVATE CITED-SOURCE IDENTITY HOLD: "+str(error),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
