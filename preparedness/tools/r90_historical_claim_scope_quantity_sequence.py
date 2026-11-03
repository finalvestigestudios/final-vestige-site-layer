#!/usr/bin/env python3
"""R90 PRIVATE HOLD: historical claim-scope, quantities, qualifiers and citation movement.

This is deterministic *review triage*, NOT a finding that a claim is correct,
supported, unsafe or medically safe. Complete original R89/R88/R80 evidence is
retained. No networking, CMS, WordPress, navigation, publishing or file writes.
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

SCHEMA = "r90-claim-scope-quantity-sequence-private-hold-v1"
REVIEW = "NOT_REVIEWED"
HOLD = "HOLD"
EXPECTED = (41, 35, 6, 2173, 2359, 4070, 242)
CLAUSE_RE = re.compile(r"(?<=[.!?;])\s+|\n+")
QUAL_RE = re.compile(
    r"\b(?:never|not|no|unless|except|only|must|should|may|can|cannot|"
    r"can't|mustn't|shouldn't|avoid|without|always|before|after|until|"
    r"within|at\s+least|at\s+most|more\s+than|less\s+than|up\s+to|"
    r"do\s+not|if|instead)\b", re.I)
NUM = r"[+-]?\d[\d,]*(?:\.\d+)?(?:\s*/\s*\d+(?:\.\d+)?)?"
UNITS = (r"(?:°\s*[CF]|degrees?\s+(?:Fahrenheit|Celsius)|%|ppm|"
         r"mg|mcg|µg|ml|mL|L|liters?|litres?|gallons?|gal|"
         r"ounces?|oz|pounds?|lbs?|grams?|kg|hours?|hrs?|"
         r"minutes?|mins?|seconds?|days?|weeks?|months?|years?|"
         r"°|ft|feet|inches?|cm|mm|miles?|km)")
QUANTITY_RE = re.compile(
    rf"(?<![\w.])({NUM}(?:\s*(?:-|–|—|to)\s*{NUM})?\s*(?:{UNITS})?)(?!\w)",
    re.I)
CITE_RE = re.compile(r"\{\{cite:([^{}]+)\}\}")
URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)


class Gate(ValueError):
    """Evidence custody, source identity or private release state invalid."""


def need(condition, message):
    if not condition:
        raise Gate(message)


def digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def upstream():
    path = Path(__file__).with_name("r89_full_claim_block_source_dossiers.py")
    need(path.is_file() and not path.is_symlink(), "R89 source unavailable")
    spec = importlib.util.spec_from_file_location("r90_r89_parent", path)
    need(spec is not None and spec.loader is not None, "R89 loader unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fingerprint(text):
    need(type(text) is str, "nonliteral historical context")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def quantities(text):
    """Literal ordered quantity/unit tokens; lexical cues only, not parsed dosages."""
    need(type(text) is str, "nonliteral quantity context")
    return [m.group(1).strip() for m in QUANTITY_RE.finditer(text)]


def qualifiers(text):
    """Ordered lexical tokens, not a semantic polarity or danger classifier."""
    need(type(text) is str, "nonliteral qualifier context")
    return [re.sub(r"\s+", " ", m.group(0)).casefold()
            for m in QUAL_RE.finditer(text)]


def scopes(text):
    """Retain full clause and token location to catch unchanged-token scope shifts."""
    need(type(text) is str, "nonliteral claim context")
    output = []
    for n, clause in enumerate(CLAUSE_RE.split(text), 1):
        if not clause:
            continue
        terms = qualifiers(clause)
        nums = quantities(clause)
        if terms or nums:
            output.append({
                "clause_ordinal": n,
                "complete_clause_UNABRIDGED_NOT_REVIEWED": clause,
                "complete_clause_SHA256": fingerprint(clause),
                "ordered_qualifiers_LEXICAL_ONLY": terms,
                "ordered_quantities_LEXICAL_ONLY": nums,
            })
    return output


def compare(before, after):
    """Never infer correctness, support, medical safety or source equivalence."""
    need(before is None or type(before) is str, "before context invalid")
    need(after is None or type(after) is str, "after context invalid")
    flags = set()
    if before is None or after is None:
        flags.add("HISTORICAL_CONTEXT_SIDE_MISSING_REVIEW_ONLY")
    else:
        a, b = quantities(before), quantities(after)
        q1, q2 = qualifiers(before), qualifiers(after)
        s1, s2 = scopes(before), scopes(after)
        c1, c2 = CITE_RE.findall(before), CITE_RE.findall(after)
        u1, u2 = URL_RE.findall(before), URL_RE.findall(after)
        if a != b:
            flags.add("QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY")
        if q1 != q2:
            flags.add("QUALIFIER_TOKEN_ORDER_OR_COUNT_CHANGED_REVIEW_ONLY")
        if q1 == q2 and s1 != s2 and (q1 or q2):
            flags.add("QUALIFIER_SCOPE_CHANGED_WITH_SAME_TOKENS_REVIEW_ONLY")
        if a == b and s1 != s2 and (a or b):
            flags.add("QUANTITY_SCOPE_CHANGED_WITH_SAME_TOKENS_REVIEW_ONLY")
        if c1 != c2:
            flags.add("HISTORICAL_CITATION_TOKEN_SEQUENCE_CHANGED_REVIEW_ONLY")
        if u1 != u2:
            flags.add("HISTORICAL_LITERAL_URL_SEQUENCE_CHANGED_REVIEW_ONLY")
        if before != after:
            flags.add("HISTORICAL_TEXT_DIFF_REQUIRES_CLAIM_REVIEW")
    return {
        "before_FULL_TEXT_SHA256_OR_NONE": None if before is None else fingerprint(before),
        "after_FULL_TEXT_SHA256_OR_NONE": None if after is None else fingerprint(after),
        "before_ordered_quantities_LEXICAL_ONLY": None if before is None else quantities(before),
        "after_ordered_quantities_LEXICAL_ONLY": None if after is None else quantities(after),
        "before_ordered_qualifiers_LEXICAL_ONLY": None if before is None else qualifiers(before),
        "after_ordered_qualifiers_LEXICAL_ONLY": None if after is None else qualifiers(after),
        "before_complete_relevant_clauses_NOT_REVIEWED": None if before is None else scopes(before),
        "after_complete_relevant_clauses_NOT_REVIEWED": None if after is None else scopes(after),
        "before_literal_citation_tokens_OR_NONE": None if before is None else CITE_RE.findall(before),
        "after_literal_citation_tokens_OR_NONE": None if after is None else CITE_RE.findall(after),
        "before_literal_links_OR_NONE": None if before is None else URL_RE.findall(before),
        "after_literal_links_OR_NONE": None if after is None else URL_RE.findall(after),
        "review_flags_NOT_SAFETY_VERDICTS": sorted(flags),
        "human_claim_support": REVIEW,
        "qualified_safety_review": REVIEW,
        "independent_QD_review": REVIEW,
        "may_publish": False,
    }


def check_hold(parent):
    mod = upstream()
    need(type(parent) is dict and parent.get("schema") == mod.SCHEMA
         and parent.get("issue") == 136
         and parent.get("release_state") == HOLD
         and parent.get("may_publish") is False
         and parent.get("medical_safety_approved") is False,
         "R89 parent has false publication or safety state")
    for key in ("human_source_approvals", "human_claim_approvals",
                "qualified_safety_approvals", "independent_QD_approvals"):
        need(type(parent.get(key)) is int and parent[key] == 0,
             "R89 unreviewed source or safety falsely approved: " + key)
    need(parent.get("sha256_seal") == digest({
         k: v for k, v in parent.items() if k != "sha256_seal"}),
         "R89 original evidence SHA-256 seal invalid")
    for key in ("all_41_document_complete_DOM_reading_packets_NOT_APPROVED",
                "all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED",
                "all_source_variant_reverse_impact_dossiers_NOT_APPROVED",
                "unpaired_historical_reviews_UNABRIDGED"):
        need(type(parent.get(key)) is list,
             "original R89 evidence collection missing: " + key)
    need(type(parent.get("complete_R88_original_evidence_UNABRIDGED_NOT_APPROVED")) is dict
         and type(parent.get("counts")) is dict,
         "R89 ancestor or source census unavailable")


def index(parent):
    """Read-only overlay with original evidence and all reverse source edges."""
    check_hold(parent)
    docs = parent["all_41_document_complete_DOM_reading_packets_NOT_APPROVED"]
    contexts = parent["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"]
    sources = parent["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"]

    doc_index = {}
    original_blocks = 0
    for doc in docs:
        need(type(doc) is dict and doc.get("may_publish") is False
             and doc.get("human_claim_support") == REVIEW
             and doc.get("qualified_safety_review") == REVIEW
             and doc.get("independent_QD_review") == REVIEW,
             "document safety or release state not HOLD")
        identity = (doc.get("kind"), doc.get("slug"))
        need(all(type(x) is str and x for x in identity)
             and identity not in doc_index, "duplicate or malformed document")
        blocks = doc.get("all_original_DOM_blocks_UNABRIDGED_NOT_REVIEWED")
        need(type(blocks) is list, "complete original blocks lost")
        for item in blocks:
            b = item["original_block_UNABRIDGED_NOT_REVIEWED"]
            need(fingerprint(b["unabridged_DOM_text_NOT_REVIEWED"]) ==
                 b["DOM_text_sha256"]
                 and item["human_claim_support"] == REVIEW
                 and item["qualified_safety_review"] == REVIEW
                 and item["may_publish"] is False,
                 "original DOM block mutation or false approval")
        original_blocks += len(blocks)
        doc_index[identity] = doc

    identities, row_index, reverse, output, flagged = set(), {}, defaultdict(list), [], Counter()
    for row in contexts:
        need(type(row) is dict and row.get("may_publish") is False
             and row.get("human_source_review") == REVIEW
             and row.get("human_claim_support") == REVIEW
             and row.get("qualified_safety_review") == REVIEW
             and row.get("independent_QD_review") == REVIEW,
             "citation has false support, safety or publication state")
        kind, slug, ordinal = row["kind"], row["slug"], row["citation_ordinal"]
        key = (kind, slug, ordinal)
        need((kind, slug) in doc_index and type(ordinal) is int and ordinal > 0
             and key not in identities, "duplicate/orphan original citation ordinal")
        identities.add(key)
        row_index[key] = row
        doc = doc_index[(kind,slug)]
        blocks = doc["all_original_DOM_blocks_UNABRIDGED_NOT_REVIEWED"]
        block_id = row["original_DOM_block_ID"]
        match = [b for b in blocks if b["original_block_UNABRIDGED_NOT_REVIEWED"]["block_id"] == block_id]
        need(len(match) == 1
             and ordinal in match[0]["original_citation_ordinals_IN_BLOCK"]
             and row["original_DOM_text_sha256"] ==
                 match[0]["original_block_UNABRIDGED_NOT_REVIEWED"]["DOM_text_sha256"]
             and row["unabridged_original_DOM_text_NOT_REVIEWED"] ==
                 match[0]["original_block_UNABRIDGED_NOT_REVIEWED"]["unabridged_DOM_text_NOT_REVIEWED"],
             "citation original complete DOM context drift")
        variants = row.get("distinct_source_variant_keys_NOT_EQUIVALENCE")
        need(type(variants) is list and len(variants) == len(set(variants)),
             "original distinct source identities duplicated")
        for v in variants:
            need(type(v) is str and len(v) == 64,
                 "invalid original source variant identity")
            reverse[v].append(key)

        before = row["historical_before_claim_container_UNABRIDGED_OR_NONE"]
        after = row["historical_after_claim_container_UNABRIDGED_OR_NONE"]
        diff = compare(before, after)
        for f in diff["review_flags_NOT_SAFETY_VERDICTS"]:
            flagged[f] += 1
        output.append({
            "kind":kind, "slug":slug, "citation_ordinal":ordinal,
            "original_DOM_block_ID":block_id,
            "original_DOM_text_sha256":row["original_DOM_text_sha256"],
            "literal_source_ID":row["literal_source_ID"],
            "distinct_origin_scoped_source_variant_keys_NOT_ALIASES":list(variants),
            "R89_original_cited_context_complete_SHA256":digest(row),
            "historical_claim_scope_comparison_NOT_A_SAFETY_VERDICT":diff,
            "human_source_review":REVIEW, "human_claim_support":REVIEW,
            "qualified_safety_review":REVIEW, "independent_QD_review":REVIEW,
            "may_publish":False,
        })

    variant_keys = set()
    for s in sources:
        key = s["variant_key_sha256"]
        need(type(key) is str and len(key) == 64 and key not in variant_keys,
             "invalid duplicate source dossier")
        variant_keys.add(key)
        need(all(s.get(k) == REVIEW for k in (
             "human_source_review", "human_claim_support",
             "qualified_safety_review", "independent_QD_review"))
             and s.get("may_publish") is False,
             "source dossier falsely approved")
        uses = s["all_unabridged_cited_claim_blocks_IN_ORIGINAL_ORDER_NOT_REVIEWED"]
        need(key in reverse and len(reverse[key]) > 0 and type(uses) is list
             and sorted((x["kind"], x["slug"], x["citation_ordinal"]) for x in uses) ==
                 sorted(reverse[key])
             and all(row_index.get((x["kind"],x["slug"],x["citation_ordinal"])) == x
                     for x in uses),
             "source reverse impact usage or full claim context changed")

    need(variant_keys == set(reverse), "some source variants were lost or substituted")
    need(len(output) == len(contexts), "citation row lost")
    for d in docs:
        key = (d["kind"],d["slug"])
        count = sum((kind,slug) == key for kind,slug,_ in identities)
        need(count == d["citation_occurrences"],
             "original per-document citation count changed")
        expected_ordinals = sorted(n for kind,slug,n in identities if (kind,slug) == key)
        need(expected_ordinals == list(range(1,count+1)),
             "original citation ordinal gap or rank shift")
    counts = parent["counts"]
    need(len(docs) == counts["documents"]
         and original_blocks == counts["complete_DOM_blocks"]
         and len(contexts) == counts["citation_occurrences"]
         and len(variant_keys) == counts["distinct_source_variants"]
         and sum(len(x) for x in reverse.values()) == counts["source_variant_edges"],
         "R89 full-slate source, citation or reading-block census changed")
    output.sort(key=lambda x:(x["kind"],x["slug"],x["citation_ordinal"]))
    report = {
        "schema":SCHEMA, "issue":136, "release_state":HOLD,
        "may_publish":False, "medical_safety_approved":False,
        "human_source_approvals":0, "human_claim_approvals":0,
        "qualified_safety_approvals":0, "independent_QD_approvals":0,
        "complete_R89_original_evidence_UNABRIDGED_NOT_APPROVED":parent,
        "all_original_citation_claim_scope_review_rows_NOT_APPROVED":output,
        "counts":{
            "documents":len(docs),
            "article":sum(d["kind"] == "article" for d in docs),
            "tool":sum(d["kind"] == "tool" for d in docs),
            "complete_DOM_blocks":original_blocks,
            "citation_occurrences":len(contexts),
            "source_variant_edges":sum(len(x) for x in reverse.values()),
            "distinct_source_variants":len(variant_keys),
            "unpaired_historical_reviews_preserved":
                len(parent["unpaired_historical_reviews_UNABRIDGED"]),
            "historical_context_review_flags_NOT_VERDICTS":dict(sorted(flagged.items())),
        },
    }
    report["sha256_seal"] = digest(report)
    return report


def audit(parent, *, expected=None):
    result = index(parent)
    if expected is not None:
        c = result["counts"]
        need(tuple(c[k] for k in ("documents", "article", "tool",
             "citation_occurrences", "source_variant_edges",
             "complete_DOM_blocks", "distinct_source_variants")) == expected,
             "R90 full slate conservation failed")
    return result


def verify(result, parent, *, expected=None):
    need(type(result) is dict and result.get("schema") == SCHEMA
         and result.get("issue") == 136 and result.get("release_state") == HOLD
         and result.get("may_publish") is False
         and result.get("medical_safety_approved") is False,
         "R90 false publication or safety PASS")
    need(result.get("sha256_seal") == digest({
         k:v for k,v in result.items() if k != "sha256_seal"}),
         "R90 output seal mismatch")
    need(result == audit(parent, expected=expected),
         "R90 original claim/source evidence or review metadata changed")


def live():
    r89 = upstream()
    parent, prior, ancestor, historical = r89.live()
    r89.verify(parent, prior, ancestor, historical, expected=r89.EXPECTED)
    report = audit(parent, expected=EXPECTED)
    verify(report, parent, expected=EXPECTED)
    return report, parent


def private_csv(result, parent, *, expected=None):
    """Metadata-only reviewer triage; formulas quarantined; no private full texts."""
    verify(result, parent, expected=expected)
    f = io.StringIO(newline="")
    w = csv.writer(f,lineterminator="\n")
    w.writerow(("kind","slug","citation_ordinal","source_variants_SHA256",
                "review_flags_NOT_SAFETY_VERDICTS",
                "human_claim_support","qualified_safety_review","may_publish"))
    for row in result["all_original_citation_claim_scope_review_rows_NOT_APPROVED"]:
        d = row["historical_claim_scope_comparison_NOT_A_SAFETY_VERDICT"]
        values = (row["kind"],row["slug"],str(row["citation_ordinal"]),
                  ";".join(row["distinct_origin_scoped_source_variant_keys_NOT_ALIASES"]),
                  ";".join(d["review_flags_NOT_SAFETY_VERDICTS"]),REVIEW,REVIEW,"FALSE")
        def protect(x):
            # Spreadsheet formula/quasi-formula disarmament; no untrusted CSV approvals.
            return "'" + x if x.lstrip().startswith(("=", "+", "-", "@", "\t", "\r", "\n")) else x
        w.writerow([protect(x) for x in values])
    return f.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--private-csv-stdout", action="store_true")
    args = ap.parse_args(argv)
    report, parent = live()
    if args.private_csv_stdout:
        print(private_csv(report,parent,expected=EXPECTED),end="")
    else:
        print(json.dumps({"schema":SCHEMA,"release_state":HOLD,
                          "may_publish":False,"counts":report["counts"],
                          "sha256_seal":report["sha256_seal"]},
                         sort_keys=True))


if __name__ == "__main__":
    main()
