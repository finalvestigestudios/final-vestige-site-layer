#!/usr/bin/env python3
"""R77 PRIVATE/HOLD: dated source-metadata custody and downstream citation work orders.

A timestamp is not a human link check, a claim verification, or a safety clearance.
This tool reads the R76 report, preserves it whole, and produces review-only packets.
No CMS, navigation, article, source, WordPress, or publication writes.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import csv
from datetime import date
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys

SCHEMA = "r77-temporal-source-provenance-and-impact-hold-v1"
PARENT = "r76-private-source-consequential-impact-crosswalk-v1"
EXPECTED = (35, 6, 244, 2173, 4070, 2359, 32, 15)
SNAPSHOT = "2026-11-02"  # Snapshot is explicit; do not substitute system clock.
HOLD_KEYS = ("may_publish", "independent_QD_approval",
             "qualified_safety_clearance", "human_source_links_verified")
REVIEW = "NOT_REVIEWED"
FIELDS = ("published", "updated", "reviewed", "verified_on")
DAY = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
MONTH = re.compile(r"^[0-9]{4}-[0-9]{2}$")
YEAR = re.compile(r"^[0-9]{4}$")


class Hold(ValueError):
    """Source lineage, evidence or publication protection failed closed."""


def need(ok, why):
    if not ok:
        raise Hold(why)


def digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False).encode("utf-8")).hexdigest()


def _r76():
    path = Path(__file__).with_name("r76_source_impact_crosswalk.py")
    need(path.is_file() and not path.is_symlink(), "R76 immutable parent tool missing")
    spec = importlib.util.spec_from_file_location("r77_r76_parent", path)
    need(spec is not None and spec.loader is not None, "cannot import R76 parent")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metadata_date(raw):
    """Keep raw dates: no guessed precision, inferred freshness or date correction."""
    need(raw is None or type(raw) is str, "source date metadata must be string/null")
    if raw is None:
        return {"raw": None, "precision": "MISSING", "calendar_date": None}
    if DAY.fullmatch(raw):
        try:
            date.fromisoformat(raw)
        except ValueError:
            return {"raw": raw, "precision": "INVALID_CALENDAR_DATE",
                    "calendar_date": None}
        return {"raw": raw, "precision": "DAY", "calendar_date": raw}
    if MONTH.fullmatch(raw):
        try:
            date.fromisoformat(raw + "-01")
        except ValueError:
            return {"raw": raw, "precision": "INVALID_CALENDAR_MONTH",
                    "calendar_date": None}
        return {"raw": raw, "precision": "MONTH", "calendar_date": None}
    if YEAR.fullmatch(raw):
        if int(raw) == 0:
            return {"raw": raw, "precision": "INVALID_CALENDAR_YEAR",
                    "calendar_date": None}
        return {"raw": raw, "precision": "YEAR", "calendar_date": None}
    return {"raw": raw, "precision": "NON_ISO_TEXT_REVIEW_ONLY",
            "calendar_date": None}


def temporal_signals(meta, snapshot):
    """Review cues only; chronology oddities may reflect a website's metadata."""
    flags = []
    def mark(condition, label):
        if condition:
            flags.append(label)
    verified = meta["verified_on"]
    updated = meta["updated"]
    published = meta["published"]
    reviewed = meta["reviewed"]
    mark(verified["raw"] is None, "NO_DOCUMENTED_MACHINE_FETCH_DATE")
    mark(updated["raw"] is None and reviewed["raw"] is None,
         "NO_VISIBLE_UPDATE_OR_REVIEW_DATE")
    for field in FIELDS:
        mark(meta[field]["precision"].startswith(("INVALID_", "NON_ISO_")),
             "UNPARSEABLE_" + field.upper() + "_DATE_REVIEW")
    def day(field):
        raw = meta[field]
        return raw["calendar_date"] if raw["precision"] == "DAY" else None
    mark(day("published") is not None and day("updated") is not None
         and day("updated") < day("published"),
         "UPDATED_DATE_BEFORE_PUBLISHED_DATE_METADATA_REVIEW")
    mark(day("published") is not None and day("reviewed") is not None
         and day("reviewed") < day("published"),
         "REVIEWED_DATE_BEFORE_PUBLISHED_DATE_METADATA_REVIEW")
    mark(day("updated") is not None and day("verified_on") is not None
         and day("updated") > day("verified_on"),
         "DOCUMENT_UPDATED_AFTER_RECORDED_MACHINE_FETCH")
    mark(day("reviewed") is not None and day("verified_on") is not None
         and day("reviewed") > day("verified_on"),
         "DOCUMENT_REVIEWED_AFTER_RECORDED_MACHINE_FETCH")
    for f in FIELDS:
        mark(day(f) is not None and day(f) > snapshot,
             f.upper() + "_DATE_AFTER_PINNED_SNAPSHOT")
    return flags


def sealed(report):
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("issue") == 136
         and report.get("release_state") == "HOLD"
         and report.get("machine_only") is True
         and report.get("publication_clearance") is False
         and all(report.get(k) is False for k in HOLD_KEYS)
         and report.get("fingerprint_sha256") ==
             digest({k: v for k, v in report.items() if k != "fingerprint_sha256"}),
         "R77 report unsealed or falsely approved")


def construct(parent, *, expected=EXPECTED, as_of=SNAPSHOT):
    need(type(expected) is tuple and len(expected) == 8
         and all(type(n) is int and n > 0 for n in expected),
         "expected baseline census malformed")
    need(type(as_of) is str and DAY.fullmatch(as_of) is not None,
         "snapshot date must be a pinned ISO calendar day")
    try:
        date.fromisoformat(as_of)
    except ValueError as exc:
        raise Hold("invalid snapshot calendar day") from exc
    _r76().sealed(parent)
    need(parent.get("schema") == PARENT, "wrong parent tool/evidence schema")
    counts = parent.get("counts")
    need(type(counts) is dict and tuple(counts.get(k) for k in (
        "articles", "tools", "complete_origin_scoped_source_readings",
        "citation_occurrences", "unabridged_DOM_blocks",
        "citation_source_variant_edges_NOT_CLAIM_COUNT",
        "shared_URL_groups_preserved",
        "reused_source_ID_groups_preserved")) == expected,
         "upstream seven-cluster/source/citation baseline changed")
    need(all(counts.get(k) == 0 for k in (
        "human_claim_support_reviews", "qualified_safety_reviews",
        "independent_QD_approvals")), "upstream invented human approval")
    records = parent.get("all_244_unabridged_source_readings_NOT_REVIEWED")
    sources = parent.get("all_origin_scoped_source_impact_packets_NOT_REVIEWED")
    citations = parent.get("every_attached_citation_crosswalk_NOT_SOURCE_SUPPORT_PROOF")
    blocks = parent.get("all_4070_unabridged_DOM_tasks_NOT_REVIEWED")
    docs = parent.get("all_document_block_orders_NOT_REVIEWED")
    need(type(records) is list and len(records) == expected[2]
         and type(sources) is list and len(sources) == expected[2]
         and type(citations) is list
         and len(citations) == counts.get("attached_citation_occurrences")
         and type(blocks) is list and len(blocks) == expected[4]
         and type(docs) is list and len(docs) == expected[0] + expected[1],
         "complete source, citation, DOM or document custody missing")
    lookup, upstream_packets = {}, {}
    urls, ids = defaultdict(list), defaultdict(list)
    for r in records:
        need(type(r) is dict, "invalid source reading")
        key = (r.get("source_origin"), r.get("source_id"))
        reading = r.get("candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        original = r.get("original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED")
        need(all(type(k) is str and k for k in key)
             and key not in lookup and type(reading) is dict
             and reading.get("id") == key[1]
             and reading.get("url") == r.get("exact_URL_NO_ALIAS")
             and type(reading.get("url")) is str and reading["url"]
             and r.get("candidate_reading_sha256") == digest(reading)
             and reading.get("human_link_check") is False
             and r.get("human_source_and_claim_review") == REVIEW
             and r.get("qualified_safety_review") == REVIEW,
             "complete unreviewed source reading/identity lost or mutated")
        need((original is None and r.get("original_reading_sha256") is None)
             or (type(original) is dict and
                 r.get("original_reading_sha256") == digest(original)),
             "historical source reading lost or altered")
        lookup[key] = r
        urls[reading["url"]].append(key)
        ids[key[1]].append(key)
    need(list(lookup) == sorted(lookup), "original source ordering changed")
    for s in sources:
        need(type(s) is dict and s.get("packet_sha256") ==
             digest({k: v for k, v in s.items() if k != "packet_sha256"}),
             "source impact packet unsealed")
        key = (s.get("source_origin"), s.get("source_id"))
        r = lookup.get(key)
        need(r is not None and key not in upstream_packets
             and s.get("exact_URL_NOT_CANONICALIZED") == r["exact_URL_NO_ALIAS"]
             and s.get("complete_source_reading_sha256") ==
                 r["candidate_reading_sha256"]
             and s.get("human_link_check") is False
             and s.get("human_source_and_claim_review") == REVIEW
             and s.get("qualified_safety_review") == REVIEW
             and s.get("shared_exact_URL_REQUIRES_SCOPE_REVIEW") is
                 (len(urls[r["exact_URL_NO_ALIAS"]]) > 1)
             and s.get("reused_source_ID_REQUIRES_SCOPE_REVIEW") is
                 (len(ids[key[1]]) > 1),
             "source impact crosswalk misstates original identity or review status")
        upstream_packets[key] = s
    need(set(upstream_packets) == set(lookup), "source impact packet omitted")
    need(sum(len(v) > 1 for v in urls.values()) == expected[6]
         and sum(len(v) > 1 for v in ids.values()) == expected[7],
         "duplicate URL or source-ID evidence disappeared")
    seen_citations, rebuilt_edges = set(), defaultdict(list)
    for c in citations:
        need(type(c) is dict and c.get("packet_sha256") ==
             digest({k: v for k, v in c.items() if k != "packet_sha256"})
             and c.get("human_claim_support_review") == REVIEW
             and c.get("qualified_safety_review") == REVIEW,
             "unsealed citation occurrence or artificial approval")
        ckey = (c.get("kind"), c.get("slug"), c.get("citation_ordinal"))
        need(ckey not in seen_citations and ckey[0] in ("article", "tool")
             and type(ckey[1]) is str and type(ckey[2]) is int
             and ckey[2] > 0, "citation occurrence missing or duplicated")
        seen_citations.add(ckey)
        variants = c.get("source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT")
        need(type(variants) is list and variants, "citation variants erased")
        for v in variants:
            need(type(v) is dict, "source variant not a record")
            key = (v.get("source_origin"), v.get("source_id"))
            r = lookup.get(key)
            need(r is not None and v.get("source_id") == c.get("raw_source_id")
                 and v.get("exact_URL_NOT_CANONICALIZED") == r["exact_URL_NO_ALIAS"]
                 and v.get("complete_source_reading_sha256") ==
                     r["candidate_reading_sha256"],
                 "citation variant silently aliased or misattributed")
            rebuilt_edges[key].append({
                "kind":c["kind"], "slug":c["slug"], "block_id":c["block_id"],
                "citation_ordinal":c["citation_ordinal"],
                "original_R72_block_sha256":c["original_R72_block_sha256"],
                "consequential_action_or_quantity_TRIAGE_NOT_VERDICT":
                    c["consequential_action_or_quantity_TRIAGE_NOT_VERDICT"]})
    need(sum(len(v) for v in rebuilt_edges.values()) == expected[5],
         "source-variant citation impact changed")
    for key, s in upstream_packets.items():
        expected_edges = sorted(rebuilt_edges[key], key=lambda e: (
            e["kind"], e["slug"], e["citation_ordinal"], e["block_id"]))
        need(s.get("citation_variant_edges_NOT_UNIQUE_CLAIMS") == expected_edges
             and s.get("all_citation_variant_edges_NOT_VERDICT") ==
                 len(expected_edges)
             and s.get("consequential_citation_variant_edges_NOT_VERDICT") ==
                 sum(e["consequential_action_or_quantity_TRIAGE_NOT_VERDICT"]
                     for e in expected_edges),
             "source impact does not match individual citation variants")
    packets = []
    for key in sorted(lookup):
        r = lookup[key]
        reading = r["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"]
        original = r["original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"]
        temporal = {f: metadata_date(reading.get(f)) for f in FIELDS}
        historic = ({f: metadata_date(original.get(f)) for f in FIELDS}
                    if original is not None else None)
        differences = ([f for f in FIELDS if
                        temporal[f]["raw"] != historic[f]["raw"]]
                       if historic is not None else [])
        flags = temporal_signals(temporal, as_of)
        if differences:
            flags.append("ORIGINAL_TO_CANDIDATE_DATE_METADATA_CHANGED")
        source = upstream_packets[key]
        row = {
            "source_origin": key[0], "source_id": key[1],
            "exact_URL_NO_ALIAS": r["exact_URL_NO_ALIAS"],
            "complete_candidate_reading_sha256": r["candidate_reading_sha256"],
            "original_reading_sha256": r["original_reading_sha256"],
            "candidate_metadata_VERBATIM": temporal,
            "original_metadata_VERBATIM_IF_PRESENT": historic,
            "changed_date_fields_ORIGINAL_VS_CANDIDATE_NOT_VERDICT": differences,
            "literal_temporal_review_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT": flags,
            "all_downstream_citation_variant_edges_NOT_CLAIM_PROOF":
                deepcopy(source["citation_variant_edges_NOT_UNIQUE_CLAIMS"]),
            "consequential_lexical_citation_edges_NOT_RISK_SCORE":
                source["consequential_citation_variant_edges_NOT_VERDICT"],
            "distinct_documents_NOT_VALIDATED_CLAIMS":
                deepcopy(source["distinct_documents_citing_source_NOT_VERIFIED"]),
            "human_link_check": False,
            "human_claim_support_review": REVIEW,
            "qualified_safety_review": REVIEW}
        row["packet_sha256"] = digest(row)
        packets.append(row)
    temporal_index = {(p["source_origin"], p["source_id"]): p for p in packets}
    shared_url_packets = []
    for url, keys in sorted(urls.items()):
        if len(keys) < 2:
            continue
        variants = [temporal_index[k] for k in sorted(keys)]
        date_tuples = {
            tuple(p["candidate_metadata_VERBATIM"][f]["raw"] for f in FIELDS)
            for p in variants}
        row = {
            "exact_shared_URL_NOT_EQUIVALENCE": url,
            "distinct_origin_scoped_source_keys": [list(k) for k in sorted(keys)],
            "candidate_reading_sha256_per_origin":
                [p["complete_candidate_reading_sha256"] for p in variants],
            "metadata_date_disagreement_REVIEW_ONLY": len(date_tuples) > 1,
            "all_original_temporal_snapshots_NOT_MERGED":
                [deepcopy(p["candidate_metadata_VERBATIM"]) for p in variants],
            "human_source_scope_review": REVIEW,
            "qualified_safety_review": REVIEW}
        row["packet_sha256"] = digest(row)
        shared_url_packets.append(row)
    need(len(shared_url_packets) == expected[6], "shared-URL metadata pairs lost")
    prioritized = sorted(packets, key=lambda p: (
        -len(p["literal_temporal_review_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT"]),
        -p["consequential_lexical_citation_edges_NOT_RISK_SCORE"],
        -len(p["distinct_documents_NOT_VALIDATED_CLAIMS"]),
        p["source_origin"], p["source_id"]))
    result = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "machine_only": True, "publication_clearance": False,
        "pinned_snapshot_date_NOT_LIVE_FRESHNESS_CHECK": as_of,
        "original_R76_fingerprint_sha256": parent["fingerprint_sha256"],
        "complete_R76_evidence_UNABRIDGED_NOT_APPROVED": deepcopy(parent),
        "all_origin_scoped_temporal_review_packets_NOT_APPROVED": packets,
        "shared_URL_temporal_contrast_packets_NOT_EQUIVALENCE": shared_url_packets,
        "temporal_reviewer_work_order_NOT_A_SAFETY_RISK_SCORE": prioritized,
        "counts": {
            "articles": expected[0], "tools": expected[1],
            "source_readings_preserved": len(packets),
            "citation_occurrences_preserved": counts["citation_occurrences"],
            "citation_source_variant_edges_preserved": expected[5],
            "unabridged_DOM_blocks_preserved": len(blocks),
            "shared_URL_groups_preserved": len(shared_url_packets),
            "reused_ID_groups_preserved": expected[7],
            "sources_with_temporal_review_cues": sum(bool(p[
                "literal_temporal_review_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT"])
                for p in packets),
            "total_temporal_review_cues": sum(len(p[
                "literal_temporal_review_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT"])
                for p in packets),
            "shared_URL_groups_with_date_metadata_disagreement": sum(
                p["metadata_date_disagreement_REVIEW_ONLY"]
                for p in shared_url_packets),
            "original_to_candidate_metadata_date_changes": sum(bool(p[
                "changed_date_fields_ORIGINAL_VS_CANDIDATE_NOT_VERDICT"])
                for p in packets),
            "human_link_checks": 0, "human_claim_support_reviews": 0,
            "qualified_safety_reviews": 0, "independent_QD_approvals": 0},
        "limitations": (
            "Documented website dates can be malformed or internally surprising. "
            "Date metadata does not prove a link was personally visited, that a "
            "source is current, that it supports a specific claim, or that medical "
            "or emergency guidance is safe. Missing dates are not an automatically "
            "unsafe source. Original and candidate metadata, complete readings, "
            "duplicate URL source origins and every citation variant remain "
            "separate. Actual human link/claim and qualified safety checks, "
            "WordPress/browser QA, 13-stage integrity and independent QD remain "
            "mandatory. No source date, citation or text is silently corrected."),
        **{key: False for key in HOLD_KEYS}}
    result["fingerprint_sha256"] = digest(result)
    sealed(result)
    return result


def csv_review_work_order(report):
    """Read-only export; neutralizes spreadsheet formula leaders, no importer."""
    sealed(report)
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow((
        "source_origin", "source_id", "exact_URL_NO_ALIAS",
        "complete_candidate_reading_sha256",
        "published_raw", "updated_raw", "reviewed_raw", "verified_on_raw",
        "temporal_review_cues_NOT_VERDICT",
        "consequential_citation_edges_NOT_RISK_SCORE",
        "human_claim_support_review", "qualified_safety_review",
        "reviewer_notes_UNTRUSTED"))
    def safe(value):
        s = (json.dumps(value, sort_keys=True, ensure_ascii=False)
             if isinstance(value, (list, dict)) else "" if value is None else str(value))
        first = s.lstrip(" \t\r\n\ufeff\u200b\u2060\u200e\u200f")
        return "'" + s if (s[:1] in ("\t", "\r", "\n", "\ufeff", "\u200b",
                                    "\u2060", "\u200e", "\u200f") or
                           first.startswith(("=", "+", "-", "@"))) else s
    for p in report["temporal_reviewer_work_order_NOT_A_SAFETY_RISK_SCORE"]:
        metadata = p["candidate_metadata_VERBATIM"]
        writer.writerow([safe(x) for x in (
            p["source_origin"], p["source_id"], p["exact_URL_NO_ALIAS"],
            p["complete_candidate_reading_sha256"],
            *(metadata[f]["raw"] for f in FIELDS),
            p["literal_temporal_review_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT"],
            p["consequential_lexical_citation_edges_NOT_RISK_SCORE"],
            REVIEW, REVIEW, "")])
    return stream.getvalue()


def live_report(repo_root=None):
    parent = _r76().live_report(repo_root)
    report = construct(parent)
    need(report == construct(parent), "nondeterministic R77 temporal crosswalk")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--private-review-csv-stdout", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = live_report(args.repo_root)
        if args.private_review_csv_stdout:
            sys.stdout.write(csv_review_work_order(report))
        else:
            print(json.dumps({"schema": SCHEMA, "release_state": "HOLD",
                "fingerprint_sha256": report["fingerprint_sha256"],
                "counts": report["counts"], "publication_clearance": False},
                sort_keys=True))
        return 0
    except (Hold, ValueError, KeyError, TypeError, AttributeError, OSError) as exc:
        print("R77 PRIVATE RELEASE HOLD: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
