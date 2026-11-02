#!/usr/bin/env python3
"""R68 PRIVATE HOLD: RC document/citation/source-scope custody, not claim approval.

Cross-check every RC article and browser-local tool against the ORIGINAL 35+1
citation evidence and the separate R67 224-to-244 source ledger. Never merge
source identities by URL, conflate machine link probes with human checks,
or upgrade a proposed emergency instruction to a safety verdict.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "r68-private-rc-document-citation-source-scope-v1"
R67_HEAD = "e9a7da397845f289336ba08bde1bee99ee9d8b9e"
RC_SHA = "ddb3528ba6494dada1fa1c3a142ce746e3a67706"
RC_REF = "integration/preparedness-release-candidate-20261101"
HOLD = ("may_publish", "independent_QD_approval",
        "qualified_safety_clearance", "human_source_links_verified")
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
EXPECTED = (35, 6, 1959, 244, 8)


class ReviewHold(ValueError):
    """Malformed evidence, unscoped citation, or non-draft publication claim."""


def need(ok, reason):
    if not ok:
        raise ReviewHold(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def raw_sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha(value):
    return type(value) is str and SHA64.fullmatch(value) is not None


def held(doc, schema, name):
    need(type(doc) is dict and doc.get("schema") == schema and
         doc.get("release_state") == "HOLD" and doc.get("machine_only") is True
         and all(doc.get(k) is False for k in HOLD) and
         sha(doc.get("fingerprint_sha256")) and
         doc["fingerprint_sha256"] ==
         digest({k:v for k,v in doc.items() if k != "fingerprint_sha256"}),
         name + " lacks a sealed private HOLD fingerprint")


def construct(source_custody, original_ledger, candidate_documents,
              candidate_crosswalk, *, expected=EXPECTED):
    """Pure deterministic synthetic test seam; live_report anchors actual Git.

    All raw RC metadata/body bytes and source-reading notes remain separate.
    Evidence similarity, valid IDs or machine fetches do NOT prove claim support.
    """
    need(type(expected) is tuple and len(expected) == 5 and
         all(type(n) is int and n >= 0 for n in expected) and
         expected[0] > 0 and expected[1] > 0 and expected[2] > 0 and
         expected[3] > 0 and expected[4] > 0, "invalid RC contract")
    held(source_custody, "r67-original-to-release-candidate-source-custody-v1",
         "R67 source custody")
    held(original_ledger, "r66-private-original-cited-source-identity-ledger-v1",
         "R66 originals")
    need(source_custody.get("original_R66_fingerprint_sha256") ==
         original_ledger["fingerprint_sha256"], "R67/R66 citation custody mismatch")
    source_rows = source_custody.get(
        "all_original_and_RC_source_review_work_orders_NOT_APPROVED")
    original_docs = original_ledger.get(
        "all_35_original_articles_plus_water_tool_NOT_APPROVED")
    need(type(source_rows) is list and len(source_rows) == expected[3] and
         type(original_docs) is list and len(original_docs) == expected[0]+1 and
         original_ledger.get("counts", {}).get("all_original_citation_occurrences")
         == expected[2] and
         source_custody.get("counts", {}).get("original_citation_occurrences")
         == expected[2] and
         source_custody.get("counts", {}).get("RC_all_source_rows") ==
         expected[3] and type(candidate_documents) is list,
         "R66/R67 citation and RC source inventory has changed")

    sources, by_id, by_url = {}, defaultdict(list), defaultdict(list)
    for row in source_rows:
        need(type(row) is dict and type(row.get("source_origin")) is str and
             type(row.get("source_id")) is str and
             row.get("human_link_review") == "NOT_REVIEWED" and
             row.get("human_claim_support_review") == "NOT_REVIEWED" and
             row.get("qualified_safety_review") == "NOT_REVIEWED" and
             row.get("independent_QD_review") == "NOT_REVIEWED",
             "candidate source has fabricated human/qualified review")
        key = (row["source_origin"], row["source_id"])
        current = row.get("candidate_complete_reading_UNABRIDGED")
        if current is None:
            continue
        need(key not in sources and type(current) is dict and
             current.get("id") == key[1] and
             current.get("human_link_check") is False and
             type(current.get("url")) is str and bool(current["url"]) and
             digest(current) == row.get("candidate_record_sha256"),
             "RC source record lost or silently rewritten")
        sources[key] = row
        by_id[key[1]].append(key)
        by_url[current["url"]].append(key)
    need(len(sources) == expected[3] and
         len(by_id) <= expected[3] and len(by_url) <= expected[3],
         "RC source variant inventory was reduced, aliased or duplicated")

    need(type(candidate_crosswalk) is dict and
         type(candidate_crosswalk.get("article_origins")) is dict and
         candidate_crosswalk.get("status") ==
         "DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED",
         "frozen origin crosswalk cannot be treated as release approval")
    origins = candidate_crosswalk["article_origins"]
    original = {}
    for row in original_docs:
        need(type(row) is dict and type(row.get("original_slug")) is str and
             row["original_slug"] not in original and
             row.get("human_source_review") == "NOT_REVIEWED" and
             row.get("qualified_safety_review") == "NOT_REVIEWED" and
             sha(row.get("original_html_sha256")) and
             type(row.get("unabridged_original_citation_identity_order")) is list,
             "original document identity or citation evidence was altered")
        original[row["original_slug"]] = row
    need(set(original) <= set(origins) and
         "water-planner" in original and
         len(original) == expected[0]+1,
         "original 35 articles and water tool not all origin-mapped")

    need(type(candidate_documents) is list and
         len(candidate_documents) == expected[0] + expected[1],
         "RC must contain exactly 35 article and six private tool drafts")
    seen, urls, tasks = set(), set(), []
    candidate_occurrences = 0
    changed_original_html = 0
    unscoped_tools = 0
    ambiguous_id_refs = 0
    shared_url_refs = 0
    missing_scope_refs = 0
    unreviewed_approval_claims = 0
    for doc in sorted(candidate_documents, key=lambda x:(x.get("kind",""),
                                                        x.get("slug",""))):
        need(type(doc) is dict and
             doc.get("kind") in ("article", "tool") and
             type(doc.get("slug")) is str and
             SLUG.fullmatch(doc["slug"]) and
             type(doc.get("body_html")) is str and bool(doc["body_html"]) and
             type(doc.get("metadata")) is dict,
             "malformed RC document or missing unabridged HTML/metadata")
        kind, slug, meta, body = (doc["kind"], doc["slug"],
                                  doc["metadata"], doc["body_html"])
        need(slug not in seen and meta.get("slug") == slug and
             type(meta.get("section")) is str and
             SLUG.fullmatch(meta["section"]) and
             meta.get("status", {}).get("publish") == "draft" and
             type(meta.get("safety_review")) is dict and
             meta.get("safety_review", {}).get("state") in
             ("pending", "approved", "not-required") and
             type(meta.get("source_use", {})) is dict,
             "duplicate/invalid slug, published RC, or malformed safety metadata")
        seen.add(slug)
        section = meta["section"]
        url = "/preparedness/" + section + "/" + slug + "/"
        need(url not in urls, "duplicate RC WordPress destination URL")
        urls.add(url)
        if kind == "article":
            need(slug in original and slug != "water-planner",
                 "RC article not in original 35-article slate")
        elif slug == "water-planner":
            need(slug in original, "original water planner lost")
        else:
            need(slug not in original, "article/tool slug collision")
        origin = origins.get(slug)
        if origin is not None:
            need(type(origin) is str and bool(origin),
                 "malformed frozen article-origin mapping")
        elif kind == "tool":
            unscoped_tools += 1
        else:
            need(False, "original 35 articles cannot lose origin scope")

        observed = list(CITE.finditer(body))
        # Never allow malformed partial citation tokens to disappear silently.
        need(body.count("{{cite:") == len(observed),
             "partial/malformed citation token in RC body: " + slug)
        candidate_occurrences += len(observed)
        source_use = meta.get("source_use", {})
        need(all(type(sid) is str and SLUG.fullmatch(sid) and
                 type(note) is str for sid,note in source_use.items()),
             "malformed original source-use claims")
        ids = set(source_use) | {m.group(1) for m in observed}
        source_entries, lookup = [], {}
        for sid in sorted(ids):
            variants = sorted(by_id.get(sid, []))
            need(bool(variants), "orphaned RC citation/source-use ID " + slug + ":" + sid)
            preferred = None
            if origin is not None:
                if (origin,sid) in variants:
                    preferred = (origin,sid)
                elif ("base",sid) in variants:
                    preferred = ("base",sid)
            elif len(variants) == 1:
                # Identifies only a candidate record, not qualified source approval.
                preferred = variants[0]
            flags = []
            if len(variants)>1:
                flags.append("DUPLICATE_SOURCE_ID_VARIANTS_NOT_ALIASED")
            if preferred is None:
                flags.append("UNSCOPED_SOURCE_ID_HUMAN_SELECTION_REQUIRED")
                missing_scope_refs += 1
            if origin is None:
                flags.append("NEW_TOOL_NO_FROZEN_ARTICLE_ORIGIN_MAPPING")
            if sid not in source_use:
                flags.append("CITED_WITHOUT_SOURCE_USE_EXPLANATION")
            if sid not in {m.group(1) for m in observed}:
                flags.append("SOURCE_USE_NOT_CITED_IN_BODY")
            for identity in variants:
                item = sources[identity]
                reading = item["candidate_complete_reading_UNABRIDGED"]
                if len(by_url[reading["url"]])>1:
                    flags.append("EXACT_URL_SHARED_BUT_SEPARATE_SOURCE_RECORDS")
            source_entries.append({
                "source_id":sid,
                "origin_scope_FROM_FROZEN_CROSSWALK_OR_NULL":origin,
                "preferred_candidate_identity_NOT_EDITORIAL_APPROVAL":
                    list(preferred) if preferred else None,
                "all_candidate_source_variants_UNABRIDGED_NOT_APPROVED":
                    [sources[k] for k in variants],
                "source_use_explanation_UNABRIDGED":
                    source_use.get(sid),
                "flags_NOT_SAFETY_VERDICTS":sorted(set(flags)),
                "review_state":"NOT_REVIEWED",
            })
            lookup[sid] = (preferred,variants,flags)
        citations=[]
        for i,m in enumerate(observed,1):
            sid=m.group(1)
            preferred,variants,flags=lookup[sid]
            if len(variants)>1:
                ambiguous_id_refs+=1
            if any("EXACT_URL_SHARED" in f for f in flags):
                shared_url_refs+=1
            citations.append({
                "ordinal":i,"source_id":sid,
                "unicode_codepoint_offset_in_candidate_html":m.start(),
                "exact_citation_token":m.group(0),
                "scoped_candidate_source_identity_OR_NULL":
                    list(preferred) if preferred else None,
                "all_possible_origin_and_id_pairs_NOT_MERGED":
                    [list(x) for x in variants],
                "local_visible_context_UNABRIDGED_NOT_CLAIM_SUPPORT":
                    body[max(0,m.start()-240):min(len(body),m.end()+240)],
                "human_claim_support":"NOT_REVIEWED",
            })
        old = original.get(slug)
        body_sha = raw_sha(body)
        flags = []
        if old is None:
            flags.append("ADDED_RC_TOOL_HAS_NO_ORIGINAL_DOCUMENT_BASELINE")
        elif body_sha != old["original_html_sha256"]:
            changed_original_html += 1
            flags.append("ORIGINAL_VS_RC_BODY_CHANGED_RECHECK_EVERY_CLAIM")
        else:
            old_seq = [(x["source_id"],x["original_offset_codepoints"])
                       for x in old["unabridged_original_citation_identity_order"]]
            new_seq = [(x["source_id"],x["unicode_codepoint_offset_in_candidate_html"])
                       for x in citations]
            need(old_seq == new_seq, "unchanged original HTML citation sequence drift")
        if meta["safety_review"]["state"] != "pending":
            flags.append("RC_RECORDED_SAFETY_LABEL_NOT_INDEPENDENTLY_VERIFIED")
            unreviewed_approval_claims+=1
        if origin is None:
            flags.append("NEW_TOOL_NO_FROZEN_ORIGIN_CROSSWALK")
        if missing_scope_refs:
            # Per-source flags above are authoritative; do not mark 'approved'.
            pass
        if any(x["scoped_candidate_source_identity_OR_NULL"] is None
               for x in citations):
            flags.append("CITATION_WITHOUT_UNAMBIGUOUS_SOURCE_SCOPE")
        task={
            "kind":kind,"slug":slug,"proposed_WordPress_url_DRAFT_ONLY":url,
            "origin_mapping_FROM_FROZEN_CROSSWALK_OR_NULL":origin,
            "RC_metadata_UNABRIDGED_NOT_SAFETY_CLEARED":meta,
            "RC_body_HTML_UNABRIDGED_NOT_SAFETY_CLEARED":body,
            "RC_body_utf8_sha256":body_sha,
            "all_RC_citation_occurrences_NOT_CLAIM_SUPPORT":citations,
            "all_RC_source_uses_and_unabridged_readings_NOT_APPROVED":source_entries,
            "original_R66_document_evidence_NOT_APPROVED":old,
            "review_flags_NOT_SAFETY_VERDICTS":sorted(flags),
            "human_claim_review":"NOT_REVIEWED",
            "human_source_review":"NOT_REVIEWED",
            "qualified_safety_review":"NOT_REVIEWED",
            "independent_QD_review":"NOT_REVIEWED",
        }
        task["task_sha256"]=digest({k:v for k,v in task.items()
                                    if k!="task_sha256"})
        tasks.append(task)
    need(len(seen)==expected[0]+expected[1] and
         sum(x["kind"]=="article" for x in tasks)==expected[0] and
         sum(x["kind"]=="tool" for x in tasks)==expected[1] and
         set(original)<=seen and
         len({x["task_sha256"] for x in tasks})==len(tasks),
         "RC original article/tool or task identity conservation failure")
    report={
        "schema":SCHEMA,"issue":136,"release_state":"HOLD","machine_only":True,
        "RC_git_commit_sha256_NOT_RELEASE_APPROVAL":RC_SHA,
        "original_R66_evidence_fingerprint_sha256":original_ledger["fingerprint_sha256"],
        "source_R67_custody_fingerprint_sha256":source_custody["fingerprint_sha256"],
        "RC_crosswalk_frozen_original_SHA256_NOT_REBASED":digest(candidate_crosswalk),
        "all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED":tasks,
        "counts":{
            "original_articles_conserved":expected[0],
            "candidate_tools":expected[1],
            "original_water_tool_present":1,
            "original_citations_preserved_under_R66":expected[2],
            "candidate_sources_conserved_under_R67":expected[3],
            "distinct_RC_document_urls":len(urls),
            "RC_citation_occurrences_UNREVIEWED":candidate_occurrences,
            "original_document_bodies_changed_or_needing_review":changed_original_html,
            "additional_RC_tools_without_frozen_origin":unscoped_tools,
            "candidate_citations_with_duplicate_id_variants":ambiguous_id_refs,
            "candidate_citations_at_shared_exact_urls":shared_url_refs,
            "source_uses_without_scoped_selection":missing_scope_refs,
            "historical_safety_labels_NOT_INDEPENDENTLY_REVIEWED":unreviewed_approval_claims,
            "human_source_or_claim_checks_performed_BY_R68":0,
        },
        "limitations":(
            "RC HTML/citations/source-use notes are preserved as DRAFT only. "
            "The candidate source-crosswalk is frozen to the original 224 records; "
            "the 244-record RC and five new tools are NOT automatically rebased. "
            "Duplicate IDs/URLs are NOT aliases. Matching HTML does not validate "
            "a claim, an HTTP machine response is not a human source check, "
            "and a metadata safety label is not qualified independent review. "
            "Mandatory original seven_cluster_git_parity remains a separate HOLD."
        ),
        **{field:False for field in HOLD},
    }
    report["fingerprint_sha256"]=digest(report)
    return report


def _module(name):
    path=Path(__file__).with_name(name)
    need(path.is_file() and not path.is_symlink(),
         "missing source custody module: "+name)
    spec=importlib.util.spec_from_file_location("r68_"+name.replace(".","_"),path)
    need(spec is not None and spec.loader is not None,
         "cannot load parent source custody module")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(repo,*args):
    try:
        return subprocess.check_output(["git",*args],cwd=repo,
                                       stderr=subprocess.PIPE)
    except (OSError,subprocess.CalledProcessError) as exc:
        raise ReviewHold("pinned RC Git evidence unavailable: "+str(exc)) from exc


def candidate_from_git(repo):
    repo=Path(repo).resolve()
    current=_git(repo,"rev-parse","--verify",
                 "refs/remotes/origin/"+RC_REF+"^{commit}").decode().strip()
    need(current==RC_SHA, "RC SHA changed: human provenance review required")
    _git(repo,"merge-base","--is-ancestor",R67_HEAD,"HEAD")
    paths=_git(repo,"ls-tree","-r",RC_SHA,"--",
               "preparedness/content/articles","preparedness/content/tools")
    buckets=defaultdict(dict)
    for raw in paths.decode("utf-8").splitlines():
        left, path=raw.split("\t",1)
        if not path.endswith((".meta.json",".body.html")):
            continue
        need(left.split()[0]=="100644", "non-regular RC content file: "+path)
        kind="article" if path.startswith("preparedness/content/articles/") else "tool"
        suffix=".meta.json" if path.endswith(".meta.json") else ".body.html"
        slug=path.rsplit("/",1)[-1][:-len(suffix)]
        need(SLUG.fullmatch(slug) and suffix not in buckets[(kind,slug)],
             "duplicate or unsafe RC document path: "+path)
        raw_content=_git(repo,"show",RC_SHA+":"+path).decode("utf-8")
        value=(_module("r67_rc_source_custody_crosswalk.py").strict_json(raw_content)
               if suffix==".meta.json" else raw_content)
        buckets[(kind,slug)][suffix]=value
    docs=[]
    for (kind,slug), parts in sorted(buckets.items()):
        need(set(parts)=={".meta.json",".body.html"},
             "incomplete RC meta/body document pair: "+slug)
        docs.append({"kind":kind,"slug":slug,
                     "metadata":parts[".meta.json"],
                     "body_html":parts[".body.html"]})
    crosswalk=_module("r67_rc_source_custody_crosswalk.py").strict_json(
        _git(repo,"show",RC_SHA+":preparedness/sources/crosswalk.json").decode("utf-8"))
    return docs,crosswalk


def live_report(repo_root,remote="origin"):
    repo=Path(repo_root).resolve()
    r67=_module("r67_rc_source_custody_crosswalk.py")
    r66=_module("r66_cited_source_identity_ledger.py")
    if remote!="origin":
        need(False,"private R68 only supports exact origin remote")
    source=r67.live_report(repo,remote)
    originals=r66.live_report(repo,remote)
    docs,crosswalk=candidate_from_git(repo)
    result=construct(source,originals,docs,crosswalk)
    need(result==construct(source,originals,docs,crosswalk),
         "non-deterministic RC source/citation review docket")
    return result


def task_csv(report):
    held(report,SCHEMA,"R68 reviewer queue")
    sink=io.StringIO(newline="")
    writer=csv.writer(sink,lineterminator="\n")
    columns=["kind","slug","private_draft_URL","RC_HTML_sha256",
             "RC_citation_count","candidate_source_id_count",
             "body_changed","origin_scope","review_flags",
             "HUMAN_CLAIM_CHECK_NOT_REVIEWED","SAFETY_REVIEW_NOT_REVIEWED",
             "reviewer_notes_UNTRUSTED"]
    writer.writerow(columns)
    for task in report["all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"]:
        flags=task["review_flags_NOT_SAFETY_VERDICTS"]
        row=[
            task["kind"],task["slug"],task["proposed_WordPress_url_DRAFT_ONLY"],
            task["RC_body_utf8_sha256"],
            len(task["all_RC_citation_occurrences_NOT_CLAIM_SUPPORT"]),
            len(task["all_RC_source_uses_and_unabridged_readings_NOT_APPROVED"]),
            "ORIGINAL_VS_RC_BODY_CHANGED_RECHECK_EVERY_CLAIM" in flags,
            task["origin_mapping_FROM_FROZEN_CROSSWALK_OR_NULL"],
            ";".join(flags),"NOT_REVIEWED","NOT_REVIEWED","",
        ]
        def safe(value):
            s="" if value is None else str(value)
            if s[:1] in ("\t","\r","\n") or s.lstrip().startswith(("=","+","-","@")):
                return "'"+s
            return s
        writer.writerow([safe(value) for value in row])
    return sink.getvalue()


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root",type=Path,default=ROOT.parent)
    parser.add_argument("--task-csv-stdout",action="store_true")
    args=parser.parse_args(argv)
    try:
        report=live_report(args.repo_root)
        if args.task_csv_stdout:
            sys.stdout.write(task_csv(report))
        else:
            print(json.dumps({"schema":SCHEMA,"release_state":"HOLD",
                  "fingerprint_sha256":report["fingerprint_sha256"],
                  "counts":report["counts"],
                  "all_publication_clearance":False},sort_keys=True))
    except (ReviewHold,ValueError,KeyError,TypeError) as exc:
        print("R68 PRIVATE HOLD: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
