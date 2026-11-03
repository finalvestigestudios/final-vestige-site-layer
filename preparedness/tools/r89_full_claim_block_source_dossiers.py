#!/usr/bin/env python3
"""R89 PRIVATE HOLD: complete claim-block -> exact source-variant review dossiers.

Read-only forensic overlay on R88. This is lexical and provenance triage, NOT
verification that advice, claim support, source links or medical safety is sound.
Original URLs, entire DOM passages, historical comparisons and source identities
stay intact; no publishing, web requests or CMS/WordPress writes.
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
import unicodedata
from urllib.parse import unquote

SCHEMA = "r89-full-claim-block-source-variant-dossiers-private-hold-v1"
PARENT_SCHEMA = "r88-citation-source-reuse-human-workorders-private-hold-v1"
REVIEW = "NOT_REVIEWED"
HOLD = "HOLD"
EXPECTED = (41, 35, 6, 2173, 2359, 4070, 1768, 242, 32)
QUALIFIER_RE = re.compile(
    r"\b(?:never|unless|except|without|not|cannot|can't|shouldn't|"
    r"mustn't|only|avoid|instead|do\s+not|no\s+longer)\b", re.IGNORECASE)
QUANTITY_RE = re.compile(r"(?<!\w)\d+(?:[.,]\d+)?(?:\s?%|\s?[a-zA-Z°]+)?")
CITE_RE = re.compile(r"\{\{cite:([^{}]+)\}\}")


class Gate(ValueError):
    """Original evidence / release hold / source or citation identity changed."""


def need(ok, message):
    if not ok:
        raise Gate(message)


def digest(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def upstream():
    path = Path(__file__).with_name("r88_source_reuse_review_workorders.py")
    need(path.is_file() and not path.is_symlink(), "R88 upstream unavailable")
    spec = importlib.util.spec_from_file_location("r89_r88_parent", path)
    need(spec is not None and spec.loader is not None, "R88 loader unavailable")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def qualifiers(value):
    """Lexical highlights only; two equal word lists can express opposite advice."""
    need(type(value) is str, "claim context is not literal text")
    return sorted(set(re.sub(r"\s+", " ", m.group(0)).casefold()
                      for m in QUALIFIER_RE.finditer(value)))


def route_collision_key(route):
    """Conservative suspicious-private-path equivalence; never a rewritten URL."""
    need(type(route) is str and route.startswith("/preparedness/")
         and "?" not in route and "#" not in route and "\\" not in route,
         "invalid private preparedness route")
    path = unicodedata.normalize("NFKC", unquote(route)).casefold()
    path = re.sub(r"/+", "/", path).rstrip("/") + "/"
    need(not any(part in (".", "..") for part in path.split("/")),
         "ambiguous traversal segment in private route")
    return path


def check_hold(report):
    need(type(report) is dict and report.get("schema") == PARENT_SCHEMA
         and report.get("issue") == 136 and report.get("release_state") == HOLD
         and report.get("may_publish") is False
         and report.get("medical_safety_approved") is False
         and all(type(report.get(k)) is int and report[k] == 0 for k in (
             "human_source_approvals", "human_claim_approvals",
             "qualified_safety_approvals", "independent_QD_approvals")),
         "R88 upstream has false approvals or publication")
    need(report.get("sha256_seal") == digest(
         {k: v for k, v in report.items() if k != "sha256_seal"}),
         "R88 source/citation original evidence seal invalid")
    for k in ("all_41_document_workorder_headers_NOT_APPROVED",
              "all_literal_citation_occurrence_workorders_NOT_APPROVED",
              "all_distinct_source_variant_review_workorders_NOT_APPROVED",
              "exact_literal_URL_reuse_groups_NOT_EQUIVALENCE",
              "original_unpaired_historical_reviews_UNABRIDGED"):
        need(type(report.get(k)) is list, "R88 original population missing: " + k)
    need(type(report.get("complete_R87_original_evidence_UNABRIDGED_NOT_APPROVED"))
         is dict and type(report.get("counts")) is dict,
         "R87 source and complete DOM reading evidence unavailable")


def index(parent):
    """Conservation-based independent review overlay. Never infers claim support."""
    check_hold(parent)
    r88 = upstream()
    originals = parent["complete_R87_original_evidence_UNABRIDGED_NOT_APPROVED"]
    packets = originals["all_41_rank_ambiguity_review_packets_NOT_APPROVED"]
    raw_rows = parent["all_literal_citation_occurrence_workorders_NOT_APPROVED"]
    headers = parent["all_41_document_workorder_headers_NOT_APPROVED"]
    variants = parent["all_distinct_source_variant_review_workorders_NOT_APPROVED"]
    workorders = {}
    for row in raw_rows:
        key = (row["kind"], row["slug"], row["citation_ordinal"])
        need(key not in workorders and type(row["citation_ordinal"]) is int
             and row["citation_ordinal"] > 0, "duplicate original citation workorder")
        workorders[key] = row

    sources = {}
    for v in variants:
        k = v["variant_key_sha256"]
        need(type(k) is str and len(k) == 64 and k not in sources,
             "duplicate/invalid source variant fingerprint")
        original = (v["literal_source_origin"], v["literal_source_ID"],
                    v["complete_source_reading_sha256"],
                    v["exact_URL_NOT_CANONICALIZED_NOT_VERIFIED"])
        need(r88.digest(original) == k
             and v["human_source_review"] == REVIEW
             and v["claim_support_approved"] is False
             and v["qualified_safety_approved"] is False,
             "source identity or safety review state corrupted")
        sources[k] = v

    output_docs, context_rows, reverse = [], [], defaultdict(list)
    seen_docs, seen_routes, used_workorders = set(), {}, set()
    counters = Counter()
    for p in packets:
        need(type(p) is dict and p.get("may_publish") is False
             and all(p.get(k) == REVIEW for k in (
                 "human_claim_support", "qualified_safety_review",
                 "independent_QD_review")), "draft has false review state")
        kind, slug = p["kind"], p["slug"]
        key = (kind, slug)
        need(key not in seen_docs, "duplicate document identity")
        seen_docs.add(key)
        r86 = p["R86_complete_document_UNABRIDGED_NOT_APPROVED"]
        original = r86["R80_complete_original_document_UNABRIDGED_NOT_APPROVED"]
        blocks = original["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"]
        need(type(blocks) is list and
             [b["block_id"] for b in blocks] ==
             original["original_DOM_block_ids_in_reading_order"] and
             len({b["block_id"] for b in blocks}) == len(blocks),
             "unabridged DOM reading order or identities lost")
        by_block, ordinal_by_block = {}, defaultdict(list)
        for block in blocks:
            txt = block["unabridged_DOM_text_NOT_REVIEWED"]
            need(type(txt) is str and
                 hashlib.sha256(txt.encode("utf-8")).hexdigest() ==
                 block["DOM_text_sha256"] and
                 block["human_claim_support_review"] == REVIEW and
                 block["qualified_safety_review"] == REVIEW,
                 "complete original claim passage or review state mutated")
            by_block[block["block_id"]] = block

        header = next((h for h in headers if (h["kind"], h["slug"]) == key), None)
        need(header is not None and header["human_claim_review"] == REVIEW
             and header["may_publish"] is False
             and header["unabridged_original_DOM_blocks"] == len(blocks),
             "missing/modified R88 private document header")
        route = header["private_route_NOT_PUBLISHED"]
        normalized = route_collision_key(route)
        need(normalized not in seen_routes or seen_routes[normalized] == key,
             "colliding draft WordPress route: " + route)
        seen_routes[normalized] = key
        need(route == r86["private_draft_url_NOT_PUBLISHED"],
             "private route no longer matches original")
        rows = p["all_original_citation_and_claim_context_reviews_NOT_APPROVED"]
        need(type(rows) is list and len(rows) ==
             header["citation_occurrences"] ==
             original["citation_occurrences_NOT_UNIQUE_CLAIMS"],
             "original citation count changed in source document")
        seen_ordinal = set()
        for item in rows:
            need(item["human_claim_support"] == REVIEW and
                 item["qualified_safety_review"] == REVIEW and
                 item["may_publish"] is False and
                 item["rank_alignment_proves_claim_identity"] is False,
                 "claim identity or safety falsely approved")
            bridge = item["R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"]
            c = bridge["R80_original_citation_UNABRIDGED_NOT_APPROVED"]
            n, sid, bid = c["citation_ordinal"], c["raw_source_id"], bridge["R80_original_block_id"]
            need(type(n) is int and n > 0 and n not in seen_ordinal and
                 bid in by_block and type(sid) is str and sid,
                 "original citation/block ordinal corrupted")
            seen_ordinal.add(n)
            need(item["R80_original_complete_DOM_block_UNABRIDGED_NOT_APPROVED"]
                 == by_block[bid], "unabridged passage not identical to R80")
            workkey = (kind, slug, n)
            need(workkey in workorders and workkey not in used_workorders,
                 "R88 citation absent or duplicated")
            used_workorders.add(workkey)
            w = workorders[workkey]
            need(w["literal_source_ID"] == sid and
                 w["original_DOM_block_ID"] == bid and
                 w["original_DOM_text_sha256"] == by_block[bid]["DOM_text_sha256"] and
                 w["human_claim_support"] == REVIEW and
                 w["qualified_safety_review"] == REVIEW and
                 w["may_publish"] is False,
                 "R88 citation-to-full-text identity drift")
            keys = [r88.digest(r88.variant_key(v)) for v in
                    c["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"]]
            need(sorted(keys) == w["distinct_source_variant_keys_NOT_ALIASES"]
                 and len(keys) == len(set(keys))
                 and all(k in sources for k in keys),
                 "original literal URL/source variants lost or substituted")
            original_text = by_block[bid]["unabridged_DOM_text_NOT_REVIEWED"]
            need(type(original_text) is str, "full original block unavailable")
            old = bridge.get("R85_original_four_stage_impact_UNABRIDGED_NOT_APPROVED")
            before_text = after_text = None
            if old is not None:
                pair = old["R83_complete_unabridged_current_to_RC_review"]
                before, after = pair["before_FULL_ANCHOR"], pair["after_FULL_ANCHOR"]
                if before is not None:
                    before_text = before["complete_container_text_UNABRIDGED"]
                if after is not None:
                    after_text = after["complete_container_text_UNABRIDGED"]
                need(before_text is None or type(before_text) is str,
                     "historical before context invalid")
                need(after_text is None or type(after_text) is str,
                     "historical after context invalid")
            before_q = qualifiers(before_text) if before_text is not None else []
            after_q = qualifiers(after_text) if after_text is not None else []
            lost = sorted(set(before_q) - set(after_q)) if before_text is not None and after_text is not None else []
            gained = sorted(set(after_q) - set(before_q)) if before_text is not None and after_text is not None else []
            flags = set(w["review_cues_NOT_VERDICTS"])
            if lost or gained:
                flags.add("HISTORICAL_QUALIFIER_LEXICAL_DELTA_REQUIRES_HUMAN_SCOPE_REVIEW")
            if "{{cite:" + sid + "}}" not in original_text:
                flags.add("LITERAL_CITATION_TOKEN_NOT_IN_ORIGINAL_DOM_TEXT_REVIEW_CONTEXT")
            if QUANTITY_RE.search(original_text):
                flags.add("NUMBER_OR_UNIT_IN_CITED_BLOCK_LEXICAL_REVIEW_ONLY")
            ordinal_by_block[bid].append(n)
            context_rows.append({
                "kind":kind, "slug":slug, "private_route_NOT_PUBLISHED":route,
                "citation_ordinal":n, "literal_source_ID":sid,
                "original_DOM_block_ID":bid,
                "original_DOM_text_sha256":by_block[bid]["DOM_text_sha256"],
                "unabridged_original_DOM_text_NOT_REVIEWED":original_text,
                "distinct_source_variant_keys_NOT_EQUIVALENCE":sorted(keys),
                "historical_before_claim_container_UNABRIDGED_OR_NONE":before_text,
                "historical_after_claim_container_UNABRIDGED_OR_NONE":after_text,
                "historical_qualifier_terms_before_LEXICAL_ONLY":before_q,
                "historical_qualifier_terms_after_LEXICAL_ONLY":after_q,
                "lexical_qualifiers_lost_NOT_SAFETY_VERDICT":lost,
                "lexical_qualifiers_gained_NOT_SAFETY_VERDICT":gained,
                "review_cues_NOT_VERDICTS":sorted(flags),
                "review_order_NOT_SAFETY_VERDICT":w["review_order_NOT_SAFETY_VERDICT"],
                "human_source_review":REVIEW, "human_claim_support":REVIEW,
                "qualified_safety_review":REVIEW, "independent_QD_review":REVIEW,
                "may_publish":False,
            })
            for vk in keys:
                reverse[vk].append([kind,slug,n])
            counters["citation_occurrences"] += 1
            counters["source_variant_edges"] += len(keys)
            if lost or gained:
                counters["historical_qualifier_lexical_delta_candidates"] += 1
            if QUANTITY_RE.search(original_text):
                counters["cited_blocks_with_number_or_unit_occurrences"] += 1

        output_docs.append({
            "kind":kind,"slug":slug,"private_route_NOT_PUBLISHED":route,
            "all_original_DOM_blocks_UNABRIDGED_NOT_REVIEWED":[
                {"original_block_UNABRIDGED_NOT_REVIEWED":b,
                 "original_citation_ordinals_IN_BLOCK":sorted(ordinal_by_block[b["block_id"]]),
                 "unreviewed_claim_qualifiers_LEXICAL_ONLY":
                     qualifiers(b["unabridged_DOM_text_NOT_REVIEWED"]),
                 "human_claim_support":REVIEW,"qualified_safety_review":REVIEW,
                 "may_publish":False} for b in blocks],
            "citation_occurrences":len(rows),"human_claim_support":REVIEW,
            "qualified_safety_review":REVIEW,"independent_QD_review":REVIEW,
            "may_publish":False})
        counters["complete_DOM_blocks"] += len(blocks)
        counters[kind] += 1

    need(len(output_docs) == len(headers) and
         len(context_rows) == len(raw_rows) == len(used_workorders)
         and len(reverse) == len(variants),
         "all original documents, citations or source-variant groups not conserved")
    for v in variants:
        usage = sorted(reverse[v["variant_key_sha256"]])
        need(usage == v["separate_citation_occurrences"],
             "source reverse-impact edges drifted from original citation usages")
    counters["documents"] = len(output_docs)
    counters["distinct_source_variants"] = len(reverse)
    counters["literal_URL_variant_collision_groups"] = len(
        parent["exact_literal_URL_reuse_groups_NOT_EQUIVALENCE"])
    counters["unpaired_historical_reviews_preserved"] = len(
        parent["original_unpaired_historical_reviews_UNABRIDGED"])
    counters["multi_citation_DOM_blocks"] = sum(
        len(x["original_citation_ordinals_IN_BLOCK"]) > 1
        for d in output_docs for x in d["all_original_DOM_blocks_UNABRIDGED_NOT_REVIEWED"])
    for name in ("article","tool","historical_qualifier_lexical_delta_candidates",
                 "cited_blocks_with_number_or_unit_occurrences"):
        counters.setdefault(name, 0)

    bykey = {(r["kind"],r["slug"],r["citation_ordinal"]):r for r in context_rows}
    dossiers = []
    for vk, v in sorted(sources.items()):
        dossiers.append({
            "variant_key_sha256": vk,
            "literal_source_origin":v["literal_source_origin"],
            "literal_source_ID":v["literal_source_ID"],
            "complete_source_reading_sha256":v["complete_source_reading_sha256"],
            "exact_URL_NOT_CANONICALIZED_NOT_VERIFIED":
                v["exact_URL_NOT_CANONICALIZED_NOT_VERIFIED"],
            "all_unabridged_cited_claim_blocks_IN_ORIGINAL_ORDER_NOT_REVIEWED":
                [bykey[tuple(k)] for k in sorted(reverse[vk])],
            "human_source_review":REVIEW,"human_claim_support":REVIEW,
            "qualified_safety_review":REVIEW,"independent_QD_review":REVIEW,
            "may_publish":False,
        })
    context_rows.sort(key=lambda r:(r["kind"],r["slug"],r["citation_ordinal"]))
    out = {"schema":SCHEMA,"issue":136,"release_state":HOLD,
           "may_publish":False,"medical_safety_approved":False,
           "human_source_approvals":0,"human_claim_approvals":0,
           "qualified_safety_approvals":0,"independent_QD_approvals":0,
           "complete_R88_original_evidence_UNABRIDGED_NOT_APPROVED":parent,
           "all_41_document_complete_DOM_reading_packets_NOT_APPROVED":output_docs,
           "all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED":context_rows,
           "all_source_variant_reverse_impact_dossiers_NOT_APPROVED":dossiers,
           "unpaired_historical_reviews_UNABRIDGED":
               parent["original_unpaired_historical_reviews_UNABRIDGED"],
           "counts":dict(sorted(counters.items()))}
    return out


def audit(parent, ancestor, historical, *, expected=None):
    r88 = upstream()
    r88.verify(parent, ancestor, historical, expected=r88.EXPECTED if expected else None)
    out = index(parent)
    if expected is not None:
        need(tuple(out["counts"][k] for k in
             ("documents","article","tool","citation_occurrences",
              "source_variant_edges","complete_DOM_blocks")) == expected[:6],
             "full 41-document source/citation/DOM census changed")
        need(ancestor["counts"]["unpaired_historical_reviews_preserved"] +
             historical["counts"]["matched_historical_rows"] == expected[6],
             "historical citations not conserved")
        need((out["counts"]["distinct_source_variants"],
              out["counts"]["literal_URL_variant_collision_groups"]) ==
             expected[7:9], "literal source-variant population changed")
    out["sha256_seal"] = digest(out)
    return out


def verify(report, parent, ancestor, historical, *, expected=None):
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("issue") == 136 and report.get("release_state") == HOLD
         and report.get("may_publish") is False
         and report.get("medical_safety_approved") is False
         and all(type(report.get(k)) is int and report[k] == 0 for k in
                 ("human_source_approvals","human_claim_approvals",
                  "qualified_safety_approvals","independent_QD_approvals")),
         "R89 false publishing, safety or human review PASS")
    need(report.get("sha256_seal") == digest(
         {k:v for k,v in report.items() if k != "sha256_seal"}),
         "complete claim-block review evidence seal invalid")
    need(report == audit(parent, ancestor, historical, expected=expected),
         "R89 changed original DOM text/citations/variant or historical safety evidence")


def private_csv(report, parent, ancestor, historical, *, expected=None):
    verify(report,parent,ancestor,historical,expected=expected)
    stream=io.StringIO(newline="")
    writer=csv.writer(stream,lineterminator="\n")
    writer.writerow(("kind","slug","original_DOM_block_ID","citation_ordinal",
                     "literal_source_ID","source_variant_SHA256_keys",
                     "historical_qualifiers_lost_LEXICAL_NOT_VERDICT",
                     "historical_qualifiers_gained_LEXICAL_NOT_VERDICT",
                     "review_cues_NOT_VERDICTS","human_claim_review",
                     "qualified_safety_review","may_publish"))
    r88 = upstream()
    for row in report["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"]:
        writer.writerow([r88.excel_safe(str(v)) for v in (
            row["kind"],row["slug"],row["original_DOM_block_ID"],
            row["citation_ordinal"],row["literal_source_ID"],
            ";".join(row["distinct_source_variant_keys_NOT_EQUIVALENCE"]),
            ";".join(row["lexical_qualifiers_lost_NOT_SAFETY_VERDICT"]),
            ";".join(row["lexical_qualifiers_gained_NOT_SAFETY_VERDICT"]),
            ";".join(row["review_cues_NOT_VERDICTS"]),REVIEW,REVIEW,"FALSE")])
    return stream.getvalue()


def private_jsonl(report, parent, ancestor, historical, *, expected=None):
    """Complete original claim contexts; private stdout only, never workflow logs."""
    verify(report,parent,ancestor,historical,expected=expected)
    return "".join(json.dumps(row,ensure_ascii=False,sort_keys=True) + "\n" for row
        in report["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"])


def live():
    r88 = upstream()
    parent,ancestor,historical = r88.live()
    output = audit(parent,ancestor,historical,expected=EXPECTED)
    verify(output,parent,ancestor,historical,expected=EXPECTED)
    return output,parent,ancestor,historical


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--private-csv-stdout",action="store_true")
    p.add_argument("--private-jsonl-stdout",action="store_true")
    args=p.parse_args(argv)
    need(not(args.private_csv_stdout and args.private_jsonl_stdout),
         "only one private export permitted")
    report,parent,ancestor,historical=live()
    if args.private_csv_stdout:
        print(private_csv(report,parent,ancestor,historical,expected=EXPECTED),end="")
    elif args.private_jsonl_stdout:
        print(private_jsonl(report,parent,ancestor,historical,expected=EXPECTED),end="")
    else:
        print(json.dumps({"schema":SCHEMA,"release_state":HOLD,
                          "may_publish":False,"medical_safety_approved":False,
                          "counts":report["counts"],"sha256_seal":report["sha256_seal"],
                          "WordPress_CMS_navigation_writes":0},sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (Gate,KeyError,TypeError,ValueError,OSError,AttributeError,
            IndexError,UnicodeError) as exc:
        raise SystemExit("R89 FAILED CLOSED: "+str(exc))
