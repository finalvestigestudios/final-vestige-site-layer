#!/usr/bin/env python3
"""R86 PRIVATE HOLD: bridge all 41 RC drafts to 29 four-stage citation histories.

No source URL equivalence, link validity, citation support, safety decision,
human review, WordPress write, CMS publication, or approval is inferred.
Exact original evidence and unmatched historical records are never discarded.
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

SCHEMA = "r86-full-slate-historical-citation-bridge-private-hold-v1"
REVIEW = "NOT_REVIEWED"
CENSUS = (35, 6, 41, 2173, 2359, 1768, 29)
HOLD = "HOLD"


class Gate(ValueError):
    """Original source or citation custody was lost, or an approval was forged."""


def need(ok, message):
    if not ok:
        raise Gate(message)


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_peer(filename, alias):
    path = Path(__file__).with_name(filename)
    need(path.is_file() and not path.is_symlink(), "missing pinned parent: " + filename)
    spec = importlib.util.spec_from_file_location(alias, path)
    need(spec is not None and spec.loader is not None, "parent import unavailable")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def slug_for(path):
    need(type(path) is str and path.startswith("preparedness/content/articles/")
         and path.endswith(".body.html")
         and "/" not in path[len("preparedness/content/articles/"):],
         "invalid contributor article path")
    return Path(path).name.removesuffix(".body.html")


def variants(citation):
    """Keep original origin+source-ID+literal URL+reading SHA, never merge URLs."""
    records = citation["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"]
    need(type(records) is list and bool(records), "R80 citation lost source variants")
    out = []
    for r in records:
        need(type(r) is dict and all(type(r.get(k)) is str for k in
             ("source_origin", "source_id", "complete_source_reading_sha256",
              "exact_URL_NOT_CANONICALIZED")), "R80 literal source provenance absent")
        need(r["source_id"] == citation["raw_source_id"],
             "R80 citation silently reassigned to a different source ID")
        out.append((r["source_origin"], r["source_id"],
                    r["complete_source_reading_sha256"],
                    r["exact_URL_NOT_CANONICALIZED"]))
    need(len(out) == len(set(out)), "duplicate R80 source variants")
    return sorted(out)


def after_variants(review):
    edge = review["exact_RC_source_edges_NOT_APPROVED"]
    if edge is None:
        return None
    need(type(edge) is dict and edge["human_claim_support"] == REVIEW
         and edge["qualified_safety_review"] == REVIEW
         and edge["may_publish"] is False, "R85 RC citation edge approval forged")
    rows = edge["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"]
    need(type(rows) is list, "R85 origin-scoped source edges absent")
    result = []
    for r in rows:
        need(type(r) is dict and r.get("human_claim_support") == REVIEW
             and r.get("qualified_safety_review") == REVIEW,
             "R85 candidate source edge falsely approved")
        result.append((r["origin"], r["literal_source_ID"], r["reading_sha256"],
                       r["literal_URL_UNVERIFIED_UNCHANGED"]))
    need(len(result) == len(set(result)), "duplicated R85 exact source edge")
    return sorted(result)


def index_history(rows):
    """All 1,768 historical rank comparisons retained, including removals."""
    need(type(rows) is list, "historical citation impact report missing")
    index, slug_origins, source_rows = {}, defaultdict(set), []
    for row in rows:
        need(type(row) is dict and row.get("may_publish") is False
             and row.get("human_claim_review") == REVIEW
             and row.get("qualified_safety_review") == REVIEW
             and type(row.get("review_cues_NOT_VERDICTS")) is list,
             "historical impact row incomplete or approved")
        path, origin, sid, rank = (row["path"], row["origin"],
                                    row["literal_raw_source_ID"],
                                    row["within_ID_occurrence"])
        slug = slug_for(path)
        need(type(origin) is str and origin and type(sid) is str and sid
             and type(rank) is int and rank > 0,
             "historical citation has invalid literal identity")
        key = (slug, sid, rank)
        need(key not in index, "ambiguous contributor-origin citation identity for " +
             slug + "/" + sid)
        evidence = row["R83_complete_unabridged_current_to_RC_review"]
        need(evidence["raw_source_id"] == sid
             and evidence["within_ID_occurrence"] == rank
             and evidence["human_claim_support_review"] == REVIEW
             and evidence["qualified_safety_review"] == REVIEW
             and evidence["may_publish"] is False,
             "R83 original anchor changed or falsely reviewed")
        after = evidence["after_FULL_ANCHOR"]
        before = evidence["before_FULL_ANCHOR"]
        need(after is not None or before is not None,
             "historical citation comparison has no original occurrence")
        if after is not None:
            need(after["raw_source_id"] == sid
                 and after["human_claim_support_review"] == REVIEW
                 and after["qualified_safety_review"] == REVIEW
                 and after["may_publish"] is False,
                 "R85 citation after-anchor identity/status lost")
            after_variants(row)
        else:
            need(row["exact_RC_source_edges_NOT_APPROVED"] is None,
                 "removed historical citation secretly retained a source edge")
        slug_origins[slug].add((origin, path))
        index[key] = row
        source_rows.append((key, row))
    need(all(len(x) == 1 for x in slug_origins.values()),
         "different historical article origins share an article slug")
    return index, slug_origins, source_rows


def bridge_documents(docs, historical_rows, *, enforce_census=False):
    """Pure, deterministic, lossless join with explicit unmatched sides."""
    need(type(docs) is list and type(historical_rows) is list,
         "both complete evidence populations are required")
    index, origins, history = index_history(historical_rows)
    seen_docs, seen_routes, seen_citations, used_history = set(), set(), set(), set()
    out, counts = [], Counter()
    for doc in docs:
        need(type(doc) is dict and doc.get("human_claim_support_review") == REVIEW
             and doc.get("qualified_safety_review") == REVIEW
             and doc.get("independent_QD_review") == REVIEW,
             "R80 document claims human or QD review")
        kind, slug = doc["kind"], doc["slug"]
        route = doc["private_draft_url"]
        need(kind in ("article", "tool") and type(slug) is str and slug
             and type(route) is str and route.startswith("/preparedness/")
             and "?" not in route and "#" not in route,
             "invalid draft route or document identity")
        doc_key = (kind, slug)
        need(doc_key not in seen_docs, "R80 duplicate document identity")
        need(route.casefold() not in seen_routes,
             "ambiguous exact draft WordPress route")
        seen_docs.add(doc_key)
        seen_routes.add(route.casefold())
        counts[kind] += 1
        blocks = doc["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"]
        order = doc["original_DOM_block_ids_in_reading_order"]
        need(type(blocks) is list and type(order) is list
             and [b["block_id"] for b in blocks] == order
             and len(order) == len(set(order)), "full original DOM reading order lost")
        scope = "FOUR_STAGE_CONTRIBUTOR_HISTORY_REVIEW" if (
            kind == "article" and slug in origins) else "NO_FOUR_STAGE_CONTRIBUTOR_HISTORY"
        rank_by_sid, citations = Counter(), []
        for block in blocks:
            need(block["human_claim_support_review"] == REVIEW
                 and block["qualified_safety_review"] == REVIEW
                 and hashlib.sha256(block[
                     "unabridged_DOM_text_NOT_REVIEWED"].encode("utf-8")).hexdigest()
                     == block["DOM_text_sha256"],
                 "R80 original complete block text or HOLD modified")
            counts["blocks"] += 1
            for c in block["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"]:
                need(c["human_claim_support_review"] == REVIEW
                     and c["qualified_safety_review"] == REVIEW,
                     "R80 citation review approved without evidence")
                sid = c["raw_source_id"]
                rank_by_sid[sid] += 1
                key = (slug, sid, rank_by_sid[sid])
                occurrence = (kind, slug, c["citation_ordinal"])
                need(occurrence not in seen_citations, "R80 citation duplicated")
                seen_citations.add(occurrence)
                row = index.get(key) if scope.startswith("FOUR_") else None
                flags = []
                if scope == "NO_FOUR_STAGE_CONTRIBUTOR_HISTORY":
                    flags.append("R80_DOCUMENT_OUTSIDE_29_HISTORICAL_ARTICLE_SCOPE")
                elif row is None:
                    flags.append("R80_RC_CITATION_WITHOUT_HISTORICAL_R85_RANK")
                else:
                    if row["R83_complete_unabridged_current_to_RC_review"][
                            "after_FULL_ANCHOR"] is None:
                        flags.append("R85_RC_CITATION_ABSENT_IN_HISTORICAL_SNAPSHOT")
                    else:
                        current = variants(c)
                        upstream = after_variants(row)
                        if current != upstream:
                            flags.append("R80_TO_R85_DISTINCT_SOURCE_VARIANTS_DIFFER")
                        if c["raw_source_id"] != row["literal_raw_source_ID"]:
                            flags.append("R80_TO_R85_LITERAL_SOURCE_ID_DIFFERS")
                    flags.extend(row["review_cues_NOT_VERDICTS"])
                    used_history.add(key)
                source_count = len(variants(c))
                counts["source_edges"] += source_count
                counts["citations"] += 1
                if flags:
                    counts["citation_review_rows"] += 1
                citations.append({
                    "R80_original_citation_UNABRIDGED_NOT_APPROVED": c,
                    "R80_original_block_id": block["block_id"],
                    "R80_within_source_ID_occurrence_rank": rank_by_sid[sid],
                    "R85_original_four_stage_impact_UNABRIDGED_NOT_APPROVED": row,
                    "review_cues_NOT_VERDICTS": sorted(set(flags)),
                    "human_claim_support": REVIEW,
                    "qualified_safety_review": REVIEW, "may_publish": False})
        need(len(citations) == doc["citation_occurrences_NOT_UNIQUE_CLAIMS"]
             and sum(len(variants(e["R80_original_citation_UNABRIDGED_NOT_APPROVED"]))
                     for e in citations) == doc["source_variant_edges_NOT_CLAIMS"],
             "R80 document citation or distinct-source conservation failed")
        out.append({
            "kind": kind, "slug": slug, "private_draft_url_NOT_PUBLISHED": route,
            "historical_scope_NOT_APPROVAL": scope,
            "historical_origins_NOT_EQUIVALENCE": sorted(origins.get(slug, ()))
                if kind == "article" else [],
            "R80_complete_original_document_UNABRIDGED_NOT_APPROVED": doc,
            "R80_citation_to_R85_impact_crosswalk_NOT_APPROVED": citations,
            "human_claim_support": REVIEW, "qualified_safety_review": REVIEW,
            "independent_QD_review": REVIEW, "may_publish": False})
    left = [{"identity": list(key),
             "R85_original_comparison_UNABRIDGED_NOT_APPROVED": row,
             "disposition": "HISTORICAL_ONLY_OR_REMOVED_CITATION_REVIEW",
             "may_publish": False, "human_claim_support": REVIEW}
            for key, row in history if key not in used_history]
    need(len(used_history) + len(left) == len(historical_rows),
         "R85 historical rank comparisons discarded")
    # Explicit zero counts are part of the deterministic schema, including
    # synthetic empty-citation documents; absence must not masquerade as zero.
    for field in ("article", "tool", "citations", "source_edges", "blocks",
                  "citation_review_rows"):
        counts.setdefault(field, 0)
    counts["documents"] = len(out)
    counts["matched_historical_rows"] = len(used_history)
    counts["historical_only_or_unpaired_rows"] = len(left)
    counts["historical_article_slugs"] = len(origins)
    counts["article_slugs_with_both_stages"] = sum(
        p["kind"] == "article" and p["slug"] in origins for p in out)
    counts["documents_outside_history"] = sum(
        p["historical_scope_NOT_APPROVAL"] == "NO_FOUR_STAGE_CONTRIBUTOR_HISTORY"
        for p in out)
    if enforce_census:
        need(tuple(counts[k] for k in (
            "article", "tool", "documents", "citations", "source_edges")) ==
             CENSUS[:5], "complete 35+6 source/citation RC census changed")
        need(len(historical_rows) == CENSUS[5]
             and len(origins) == CENSUS[6], "historical 29-article rank census drift")
        need(counts["article_slugs_with_both_stages"] == CENSUS[6],
             "29 historical articles absent from 35-article RC slate")
        need(counts["blocks"] == 4070,
             "4,070 original DOM blocks or full reading depth lost")
    return out, left, dict(sorted(counts.items()))


def construct(docs, historical_rows, *, enforce_census=False,
              r80_fingerprint=None, r85_seal=None):
    packets, leftover, counts = bridge_documents(
        docs, historical_rows, enforce_census=enforce_census)
    report = {
        "schema": SCHEMA, "issue": 136, "release_state": HOLD,
        "may_publish": False, "medical_safety_approved": False,
        "human_source_approvals": 0, "human_claim_approvals": 0,
        "qualified_safety_approvals": 0, "independent_QD_approvals": 0,
        "R80_unabridged_full_slate_evidence_fingerprint": r80_fingerprint,
        "R85_unabridged_historical_citation_source_seal": r85_seal,
        "counts": counts,
        "all_41_unabridged_document_review_bridges_NOT_APPROVED": packets,
        "all_unpaired_R85_historical_citation_reviews_UNABRIDGED": leftover}
    report["sha256_seal"] = digest(report)
    return report


def verify(report, docs, historical_rows, *, enforce_census=False,
           r80_fingerprint=None, r85_seal=None):
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("issue") == 136 and report.get("release_state") == HOLD
         and report.get("may_publish") is False
         and report.get("medical_safety_approved") is False
         and all(report.get(k) == 0 for k in (
             "human_source_approvals", "human_claim_approvals",
             "qualified_safety_approvals", "independent_QD_approvals")),
         "R86 approval or publication state forged")
    need(report.get("sha256_seal") ==
         digest({k: v for k, v in report.items() if k != "sha256_seal"}),
         "R86 evidence digest does not match")
    need(report == construct(docs, historical_rows, enforce_census=enforce_census,
         r80_fingerprint=r80_fingerprint, r85_seal=r85_seal),
         "R86 evidence cannot be independently reconstructed")


def private_csv(report, docs, historical_rows, *, r80_fingerprint=None,
                r85_seal=None, enforce_census=False):
    verify(report, docs, historical_rows, r80_fingerprint=r80_fingerprint,
           r85_seal=r85_seal, enforce_census=enforce_census)
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(("draft_kind", "draft_slug", "citation_ordinal",
                     "original_source_ID", "review_cues_NOT_VERDICTS",
                     "human_claim_support", "may_publish"))
    for packet in report["all_41_unabridged_document_review_bridges_NOT_APPROVED"]:
        for row in packet["R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"]:
            if row["review_cues_NOT_VERDICTS"]:
                c = row["R80_original_citation_UNABRIDGED_NOT_APPROVED"]
                writer.writerow([excel_safe(str(x)) for x in (
                    packet["kind"], packet["slug"], c["citation_ordinal"],
                    c["raw_source_id"], ";".join(row["review_cues_NOT_VERDICTS"]),
                    REVIEW, "FALSE")])
    return out.getvalue()


def excel_safe(value):
    """One-way export; no CSV value can execute a spreadsheet formula."""
    value = str(value)
    stripped = value.lstrip(" \t\r\n\ufeff\u200b\u2060\u200e\u200f")
    return "'" + value if (stripped.startswith(("=", "+", "-", "@"))
           or (value and ord(value[0]) < 32)
           or value.startswith(("\ufeff", "\u200b", "\u2060", "\u200e", "\u200f"))) else value


def live():
    r80 = load_peer("r80_offline_evidence_reading_room.py", "r86_r80")
    r85 = load_peer("r85_source_change_citation_impact.py", "r86_r85")
    p79 = r80._r79().live_report()
    docs, _, sources = r80.unpack(p79)
    need(len(sources) == 244, "R80 original research readings lost")
    r84 = r85.parent()
    r83, r82 = r84.parent_modules()
    p82 = r82.live_report()
    p83 = r83.construct(p82)
    p84 = r84.construct(p82, p83)
    p85 = r85.construct(p82, p83, p84)
    r85.verify(p85, p82, p83, p84)
    report = construct(docs, p85[
        "all_unabridged_current_TO_rc_citation_impact_reviews_NOT_APPROVED"],
        enforce_census=True,
        r80_fingerprint=p79["fingerprint_sha256"],
        r85_seal=p85["sha256_seal"])
    verify(report, docs, p85[
        "all_unabridged_current_TO_rc_citation_impact_reviews_NOT_APPROVED"],
        enforce_census=True, r80_fingerprint=p79["fingerprint_sha256"],
        r85_seal=p85["sha256_seal"])
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-csv-stdout", action="store_true",
                        help="Temporary reviewer metadata only, never public assets")
    args = parser.parse_args(argv)
    report = live()
    if args.private_csv_stdout:
        # Always reconstruct from original evidence, never import reviewer CSV.
        result = report["all_41_unabridged_document_review_bridges_NOT_APPROVED"]
        output = io.StringIO(newline="")
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(("draft_kind","draft_slug","citation_ordinal",
                         "original_source_ID","review_cues_NOT_VERDICTS","review_state"))
        for p in result:
            for x in p["R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"]:
                if x["review_cues_NOT_VERDICTS"]:
                    c = x["R80_original_citation_UNABRIDGED_NOT_APPROVED"]
                    writer.writerow([excel_safe(str(y)) for y in (
                        p["kind"],p["slug"],c["citation_ordinal"],c["raw_source_id"],
                        ";".join(x["review_cues_NOT_VERDICTS"]),REVIEW)])
        print(output.getvalue(), end="")
    else:
        print(json.dumps({"schema":SCHEMA, "release_state":HOLD,
                          "may_publish":False, "medical_safety_approved":False,
                          "counts":report["counts"],
                          "sha256_seal":report["sha256_seal"],
                          "public_CMS_or_WordPress_writes":0},
                         sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (Gate, KeyError, TypeError, ValueError, OSError,
            AttributeError, IndexError) as exc:
        raise SystemExit("R86 FAILED CLOSED: " + str(exc))
