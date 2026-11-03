#!/usr/bin/env python3
"""R88 PRIVATE HOLD: deterministic source-variant reuse and citation work orders.

A repeated URL, source ID or citation rank NEVER proves source equivalence,
claim support, modern emergency safety or authorization to publish.
Read-only reviewer evidence; no link fetching, public assets, CMS or WordPress.
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

SCHEMA = "r88-citation-source-reuse-human-workorders-private-hold-v1"
PARENT_SCHEMA = "r87-rank-ambiguity-claim-scope-private-hold-v1"
REVIEW = "NOT_REVIEWED"
HOLD = "HOLD"
EXPECTED = (41, 35, 6, 2173, 2359, 4070, 1768)


class Gate(ValueError):
    """Original evidence, human-review state or hard release HOLD changed."""


def need(ok, message):
    if not ok:
        raise Gate(message)


def digest(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def upstream():
    path = Path(__file__).with_name("r87_rank_ambiguity_claim_scope_gate.py")
    need(path.is_file() and not path.is_symlink(), "R87 parent missing")
    spec = importlib.util.spec_from_file_location("r88_r87_parent", path)
    need(spec is not None and spec.loader is not None, "R87 parent loader missing")
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def check_hold(report):
    need(type(report) is dict and report.get("schema") == PARENT_SCHEMA
         and report.get("issue") == 136 and report.get("release_state") == HOLD
         and report.get("may_publish") is False
         and report.get("medical_safety_approved") is False
         and all(type(report.get(k)) is int and report[k] == 0 for k in (
             "human_source_approvals", "human_claim_approvals",
             "qualified_safety_approvals", "independent_QD_approvals")),
         "parent has incomplete/false source or qualified safety approval")
    need(type(report.get("counts")) is dict
         and type(report.get("all_41_rank_ambiguity_review_packets_NOT_APPROVED")) is list
         and type(report.get("unpaired_historical_review_records_UNABRIDGED")) is list,
         "unabridged parent source/citation populations missing")


def variant_key(record):
    fields = ("source_origin", "source_id", "complete_source_reading_sha256",
              "exact_URL_NOT_CANONICALIZED")
    need(type(record) is dict
         and all(type(record.get(k)) is str and record[k] for k in fields),
         "origin-scoped source ID, reading SHA or exact URL missing")
    return tuple(record[k] for k in fields)


def priority(cues):
    """Metadata work ordering, NOT an automated risk or medical safety verdict."""
    if any("SHIFT" in c or "MISSING" in c or "NOT_VERBATIM" in c for c in cues):
        return "P1_PROVENANCE_OR_CONTEXT_REVIEW"
    if any("RANK" in c or "REPEATED" in c for c in cues):
        return "P3_CITATION_ALIGNMENT_REVIEW"
    if any("VARIANT" in c or "URL" in c or "SOURCE" in c for c in cues):
        return "P2_SOURCE_IDENTITY_REVIEW"
    if any("HISTORICAL" in c for c in cues):
        return "P3_CITATION_ALIGNMENT_REVIEW"
    return "P4_ROUTINE_HUMAN_REVIEW"


def index(parent):
    """Pure overlay: no source normalization, URL merge, missing original or verdict."""
    check_hold(parent)
    by_variant, original_keys, by_url = defaultdict(set), {}, defaultdict(set)
    docs, rows = [], []
    seen_docs, seen_cites = set(), set()
    edges = blocks_count = 0
    for p in parent["all_41_rank_ambiguity_review_packets_NOT_APPROVED"]:
        need(type(p) is dict and p.get("may_publish") is False
             and all(p.get(k) == REVIEW for k in (
                 "human_claim_support", "qualified_safety_review",
                 "independent_QD_review")), "document was falsely approved")
        kind, slug = p["kind"], p["slug"]
        need(kind in ("article", "tool") and type(slug) is str and slug,
             "invalid literal draft identity")
        need((kind, slug) not in seen_docs, "duplicate document identity")
        seen_docs.add((kind, slug))
        r86 = p["R86_complete_document_UNABRIDGED_NOT_APPROVED"]
        original = r86["R80_complete_original_document_UNABRIDGED_NOT_APPROVED"]
        blocks = original["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"]
        need(type(blocks) is list and
             [b["block_id"] for b in blocks] ==
             original["original_DOM_block_ids_in_reading_order"],
             "original DOM reading order altered")
        bid = {b["block_id"]: b for b in blocks}
        need(len(bid) == len(blocks), "duplicate source block identity")
        for b in blocks:
            value = b["unabridged_DOM_text_NOT_REVIEWED"]
            need(type(value) is str and
                 hashlib.sha256(value.encode("utf-8")).hexdigest() ==
                 b["DOM_text_sha256"] and
                 b["human_claim_support_review"] == REVIEW and
                 b["qualified_safety_review"] == REVIEW,
                 "original complete block text changed or human approval forged")
        blocks_count += len(blocks)
        citations = p["all_original_citation_and_claim_context_reviews_NOT_APPROVED"]
        need(type(citations) is list and
             len(citations) == original["citation_occurrences_NOT_UNIQUE_CLAIMS"],
             "cited occurrence missing from full DOM document")
        docs.append({"kind": kind, "slug": slug,
                     "private_route_NOT_PUBLISHED":
                         r86["private_draft_url_NOT_PUBLISHED"],
                     "unabridged_original_DOM_blocks": len(blocks),
                     "citation_occurrences": len(citations),
                     "human_claim_review": REVIEW, "may_publish": False})
        for item in citations:
            need(type(item) is dict and
                 item.get("human_claim_support") == REVIEW and
                 item.get("qualified_safety_review") == REVIEW and
                 item.get("may_publish") is False and
                 item.get("rank_alignment_proves_claim_identity") is False,
                 "citation granted unsupported claim support or publication")
            bridge = item["R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"]
            c = bridge["R80_original_citation_UNABRIDGED_NOT_APPROVED"]
            ordinal, sid, block_id = c["citation_ordinal"], c["raw_source_id"], bridge["R80_original_block_id"]
            need(type(ordinal) is int and ordinal > 0 and
                 type(sid) is str and sid and block_id in bid and
                 item["R80_original_complete_DOM_block_UNABRIDGED_NOT_APPROVED"] == bid[block_id],
                 "literal citation or original DOM block identity changed")
            key = (kind, slug, ordinal)
            need(key not in seen_cites, "duplicate original citation ordinal")
            seen_cites.add(key)
            cues = item["review_cues_NOT_VERDICTS"]
            need(type(cues) is list and
                 all(type(x) is str and x for x in cues),
                 "citation review cues corrupted")
            candidates = c["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"]
            need(type(candidates) is list and candidates,
                 "citation lost original source variants")
            identities = [variant_key(v) for v in candidates]
            need(len(set(identities)) == len(identities) and
                 all(x[1] == sid for x in identities),
                 "distinct original origin/ID/reading/URL silently merged")
            edges += len(identities)
            seals = []
            for identity in identities:
                sha = digest(identity)
                need(sha not in original_keys or original_keys[sha] == identity,
                     "SHA-256 source identity collision")
                original_keys[sha] = identity
                by_variant[sha].add(key)
                by_url[identity[3]].add(sha)
                seals.append(sha)
            rows.append({"kind":kind, "slug":slug,
                         "citation_ordinal":ordinal, "literal_source_ID":sid,
                         "original_DOM_block_ID":block_id,
                         "original_DOM_text_sha256":bid[block_id]["DOM_text_sha256"],
                         "distinct_source_variant_keys_NOT_ALIASES":sorted(seals),
                         "review_cues_NOT_VERDICTS":sorted(set(cues)),
                         "human_claim_support":REVIEW,
                         "qualified_safety_review":REVIEW, "may_publish":False})
    need(len(rows) == parent["counts"]["citations"] and
         edges == parent["counts"]["source_variant_edges"] and
         blocks_count == parent["counts"]["blocks"] and
         len(docs) == parent["counts"]["documents"],
         "complete original source/citation/document census not conserved")
    URL_clash = {sha for group in by_url.values() if len(group) > 1 for sha in group}
    used = {sha for sha, usages in by_variant.items() if len(usages) > 1}
    for row in rows:
        cues = set(row["review_cues_NOT_VERDICTS"])
        if any(sha in URL_clash for sha in row["distinct_source_variant_keys_NOT_ALIASES"]):
            cues.add("SAME_LITERAL_URL_DISTINCT_VARIANTS_NOT_EQUIVALENT")
        if any(sha in used for sha in row["distinct_source_variant_keys_NOT_ALIASES"]):
            cues.add("SAME_SOURCE_VARIANT_REUSED_NOT_CLAIM_SUPPORT")
        row["review_cues_NOT_VERDICTS"] = sorted(cues)
        row["review_order_NOT_SAFETY_VERDICT"] = priority(cues)
    rows.sort(key=lambda c:(c["kind"],c["slug"],c["citation_ordinal"]))
    groups = [{"variant_key_sha256":sha,
               "literal_source_origin":identity[0], "literal_source_ID":identity[1],
               "complete_source_reading_sha256":identity[2],
               "exact_URL_NOT_CANONICALIZED_NOT_VERIFIED":identity[3],
               "separate_citation_occurrences":[list(x) for x in sorted(by_variant[sha])],
               "human_source_review":REVIEW, "claim_support_approved":False,
               "qualified_safety_approved":False}
              for sha, identity in sorted(original_keys.items())]
    URLs = [{"literal_URL_NOT_VERIFIED":url,
             "distinct_variant_keys_NOT_MERGED":sorted(sha),
             "same_URL_proves_source_identity":False,"human_source_review":REVIEW}
            for url, sha in sorted(by_url.items()) if len(sha) > 1]
    counts = Counter(c["review_order_NOT_SAFETY_VERDICT"] for c in rows)
    return {"schema":SCHEMA,"issue":136,"release_state":HOLD,
            "may_publish":False,"medical_safety_approved":False,
            "human_source_approvals":0,"human_claim_approvals":0,
            "qualified_safety_approvals":0,"independent_QD_approvals":0,
            "complete_R87_original_evidence_UNABRIDGED_NOT_APPROVED":parent,
            "all_41_document_workorder_headers_NOT_APPROVED":docs,
            "all_literal_citation_occurrence_workorders_NOT_APPROVED":rows,
            "all_distinct_source_variant_review_workorders_NOT_APPROVED":groups,
            "exact_literal_URL_reuse_groups_NOT_EQUIVALENCE":URLs,
            "original_unpaired_historical_reviews_UNABRIDGED":
                parent["unpaired_historical_review_records_UNABRIDGED"],
            "counts":{"documents":len(docs),
                      "article":sum(x["kind"]=="article" for x in docs),
                      "tool":sum(x["kind"]=="tool" for x in docs),
                      "citations":len(rows),"source_variant_edges":edges,
                      "complete_DOM_blocks":blocks_count,
                      "distinct_source_variants":len(groups),
                      "literal_URL_variant_collision_groups":len(URLs),
                      "source_variants_reused_by_multiple_citations":len(used),
                      "original_unpaired_historical_reviews":len(
                          parent["unpaired_historical_review_records_UNABRIDGED"]),
                      "P1_provenance_or_context":counts["P1_PROVENANCE_OR_CONTEXT_REVIEW"],
                      "P2_source_identity":counts["P2_SOURCE_IDENTITY_REVIEW"],
                      "P3_rank_alignment":counts["P3_CITATION_ALIGNMENT_REVIEW"],
                      "P4_other":counts["P4_ROUTINE_HUMAN_REVIEW"]}}


def audit(parent, original, *, expected=None):
    r87 = upstream()
    r87.verify(parent, original, expected=expected)
    out = index(parent)
    if expected is not None:
        need(tuple(out["counts"][k] for k in
              ("documents","article","tool","citations",
               "source_variant_edges","complete_DOM_blocks")) == expected[:6],
             "full 41-document release candidate census changed")
        need(parent["counts"]["unpaired_historical_reviews_preserved"] +
             original["counts"]["matched_historical_rows"] == expected[6],
             "original four-stage historical comparison rows missing")
    out["sha256_seal"] = digest(out)
    return out


def verify(derived, parent, original, *, expected=None):
    need(type(derived) is dict and derived.get("schema") == SCHEMA
         and derived.get("release_state") == HOLD
         and derived.get("may_publish") is False
         and derived.get("medical_safety_approved") is False
         and all(type(derived.get(k)) is int and derived[k] == 0 for k in (
             "human_source_approvals", "human_claim_approvals",
             "qualified_safety_approvals", "independent_QD_approvals")),
         "false reviewer approval or publish state")
    need(derived.get("sha256_seal") ==
         digest({k:v for k,v in derived.items() if k!="sha256_seal"}),
         "review workorder original evidence fingerprint corrupted")
    need(derived == audit(parent, original, expected=expected),
         "workorders not independently reconstructed from R87 original evidence")


def excel_safe(value):
    need(type(value) is str, "reviewer cell not literal string")
    return "'" + value if value.lstrip().startswith(("=","+","-","@")) else value


def private_csv(report, parent, original, *, expected=None):
    verify(report, parent, original, expected=expected)
    stream=io.StringIO(newline="")
    writer=csv.writer(stream,lineterminator="\n")
    writer.writerow(("document_type","draft_slug","citation_ordinal",
                     "literal_source_ID","source_variant_keys_NOT_ALIASES",
                     "review_order_NOT_SAFETY_VERDICT","review_cues_NOT_VERDICTS",
                     "human_claim_review","qualified_safety_review","may_publish"))
    for r in report["all_literal_citation_occurrence_workorders_NOT_APPROVED"]:
        writer.writerow([excel_safe(str(v)) for v in (
            r["kind"],r["slug"],r["citation_ordinal"],r["literal_source_ID"],
            ";".join(r["distinct_source_variant_keys_NOT_ALIASES"]),
            r["review_order_NOT_SAFETY_VERDICT"],
            ";".join(r["review_cues_NOT_VERDICTS"]), REVIEW, REVIEW, "FALSE")])
    return stream.getvalue()


def live():
    r87=upstream()
    parent,original=r87.live()
    report=audit(parent,original,expected=EXPECTED)
    verify(report,parent,original,expected=EXPECTED)
    return report,parent,original


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--private-csv-stdout",action="store_true")
    args=p.parse_args(argv)
    report,parent,original=live()
    if args.private_csv_stdout:
        print(private_csv(report,parent,original,expected=EXPECTED),end="")
    else:
        print(json.dumps({"schema":SCHEMA,"release_state":HOLD,
                          "may_publish":False,"medical_safety_approved":False,
                          "counts":report["counts"],"sha256_seal":report["sha256_seal"],
                          "WordPress_CMS_navigation_writes":0},sort_keys=True))


if __name__=="__main__":
    try:
        main()
    except (Gate,KeyError,TypeError,ValueError,OSError,
            AttributeError,IndexError) as exc:
        raise SystemExit("R88 FAILED CLOSED: "+str(exc))
