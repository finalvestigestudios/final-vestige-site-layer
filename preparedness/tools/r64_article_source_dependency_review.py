#!/usr/bin/env python3
"""R64 PRIVATE HOLD: exhaustive article/source dependency-review coverage.

Consumes freshly verified R61/R62/R63 provenance, never promotes contributor
edits, aliases source identities, assesses claim support, or publishes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import argparse
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

_parent = Path(__file__).with_name("r63_contributor_source_impact_crosswalk.py")
if not _parent.is_file() or _parent.is_symlink():
    raise ImportError("R63 source and citation provenance prerequisite missing")
_spec = importlib.util.spec_from_file_location("r64_r63_original_dependency", _parent)
if _spec is None or _spec.loader is None:
    raise ImportError("R63 source gate could not be loaded")
r63 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r63)
r62 = r63.r62

SCHEMA = "r64-private-article-source-dependency-coverage-v1"
NOTE_SCHEMA = "r64-unsigned-dependency-review-notes-v1"
HOLD = ("may_publish", "independent_QD_approval",
        "qualified_safety_clearance", "human_source_links_verified")
FIELDS = ("work_order_sha256", "article_cluster", "article_slug",
          "source_id", "frozen_citations", "observed_citations",
          "frozen_source_use", "observed_source_use", "frozen_readings",
          "observed_readings", "review_flags_NOT_FINDINGS",
          "reviewer_note_UNTRUSTED")
MAX_JSON_BYTES = 48_000_000
MAX_CSV_BYTES = 10_000_000


class DependencyHold(ValueError):
    """Release controls or original-source/citation custody failed closed."""


def need(ok, message):
    if not ok:
        raise DependencyHold(message)


def _construct(lineage, docket, source_report):
    """Pure deterministic construction; public make_report verifies parents first.

    Exposed for synthetic tests, NOT an alternative production verification path.
    """
    need(type(lineage) is dict and type(docket) is dict and
         type(source_report) is dict, "complete R61/R62/R63 evidence required")
    srcrows = source_report.get(
        "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS")
    articles = lineage.get(
        "per_article_citation_and_context_lineage_NOT_REVIEWED")
    need(type(srcrows) is list and type(articles) is list and
         len(articles) == 29, "contributor source/article census missing")
    index = {"frozen": defaultdict(list), "observed": defaultdict(list)}
    identity = set()
    for row in srcrows:
        cluster, sid = row["cluster"], row["source_id"]
        need(type(cluster) is str and type(sid) is str and
             (cluster, sid) not in identity, "duplicate source identity")
        identity.add((cluster, sid))
        need(row["change_kind"] in r63.KINDS and
             row["human_source_review"] == "NOT_REVIEWED" and
             row["qualified_claim_safety_review"] == "NOT_REVIEWED",
             "source state no longer quarantined")
        for version in index:
            reading = row["versions"][version]
            if reading is not None:
                need(reading["unabridged_contributor_reading_NOT_HUMAN_CHECKED"]["id"] == sid,
                     "source reading ID substituted")
                index[version][sid].append({
                    "cluster": cluster,
                    "source_work_order_sha256": row["work_order_sha256"],
                    "reading_sha256": reading["record_sha256"],
                    "source_record_UNABRIDGED_NOT_VERIFIED":
                        reading["unabridged_contributor_reading_NOT_HUMAN_CHECKED"],
                    "shared_exact_url_NOT_EQUIVALENCE":
                        reading["same_exact_url_distinct_identity_NOT_ALIAS"],
                    "source_record_change_NOT_APPROVED": row["change_kind"],
                })
    rows, census = [], {"frozen": 0, "observed": 0}
    seen_articles = set()
    flags_count = Counter()
    for article in sorted(articles, key=lambda a: (a["cluster"], a["slug"])):
        cluster, slug = article["cluster"], article["slug"]
        need((cluster, slug) not in seen_articles and
             article.get("review_state") == "NOT_REVIEWED",
             "duplicate or purportedly cleared article")
        seen_articles.add((cluster, slug))
        versions = article["versions"]
        ids = set()
        for version in ("frozen", "observed"):
            v = versions[version]
            need(type(v["full_source_use_mapping_UNABRIDGED"]) is dict and
                 type(v["citation_occurrences_in_original_order"]) is list,
                 "source-use/citation ledger missing")
            ids.update(v["full_source_use_mapping_UNABRIDGED"])
            ids.update(x["source_id"] for x in
                       v["citation_occurrences_in_original_order"])
            census[version] += len(v["citation_occurrences_in_original_order"])
        same_seq = [x["source_id"] for x in
                    versions["frozen"]["citation_occurrences_in_original_order"]] == [
                    x["source_id"] for x in
                    versions["observed"]["citation_occurrences_in_original_order"]]
        for sid in sorted(ids):
            need(type(sid) is str and sid, "blank citation/source-use identity")
            details, flags = {}, set()
            for version in ("frozen", "observed"):
                v = versions[version]
                cited = [dict(ordinal=n,
                              source_id=x["source_id"],
                              offset_codepoints=x["offset_codepoints"],
                              unabridged_context_NOT_CLAIM_SUPPORT=
                                  x["unabridged_local_context"],
                              body_sha256=v["body_sha256"])
                         for n, x in enumerate(
                             v["citation_occurrences_in_original_order"], 1)
                         if x["source_id"] == sid]
                has_use = sid in v["full_source_use_mapping_UNABRIDGED"]
                candidates = index[version].get(sid, [])
                if not candidates:
                    flags.add("SOURCE_ID_OUTSIDE_SEVEN_CLUSTERS_CHECK_FULL_R58")
                if len(candidates) > 1:
                    flags.add("SOURCE_ID_MULTI_CONTRIBUTOR_NO_ALIAS")
                if any(x["shared_exact_url_NOT_EQUIVALENCE"] for x in candidates):
                    flags.add("SOURCE_URL_SHARED_NO_ALIAS")
                details[version] = {
                    "body_sha256": v["body_sha256"],
                    "citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF": cited,
                    "source_use_present": has_use,
                    "source_use_note_UNABRIDGED_NOT_SUPPORT_PROOF":
                        v["full_source_use_mapping_UNABRIDGED"][sid]
                        if has_use else None,
                    "source_candidates_DISTINCT_NOT_CLAIM_SUPPORT": candidates,
                }
            old, new = details["frozen"], details["observed"]
            if len(old["citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"]) != len(
                    new["citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"]):
                flags.add("CITATION_MULTIPLICITY_CHANGED_NO_AUTO_PAIR")
            if old["source_use_present"] != new["source_use_present"] or (
                    old["source_use_present"] and
                    old["source_use_note_UNABRIDGED_NOT_SUPPORT_PROOF"] !=
                    new["source_use_note_UNABRIDGED_NOT_SUPPORT_PROOF"]):
                flags.add("ARTICLE_SOURCE_USE_CHANGED_NOT_REVIEWED")
            if old["source_candidates_DISTINCT_NOT_CLAIM_SUPPORT"] != (
                    new["source_candidates_DISTINCT_NOT_CLAIM_SUPPORT"]):
                flags.add("SOURCE_READING_CANDIDATES_CHANGED_NO_ALIAS")
            if versions["frozen"]["body_sha256"] != versions["observed"]["body_sha256"]:
                flags.add("ARTICLE_PROSE_CHANGED_REQUIRES_CLAIM_REVIEW")
            if not same_seq:
                flags.add("ARTICLE_CITATION_SEQUENCE_CHANGED_NO_AUTO_PAIR")
            if versions["frozen"]["metadata_sha256"] != versions["observed"]["metadata_sha256"]:
                flags.add("ARTICLE_METADATA_CHANGED_NOT_REVIEWED")
            if versions["frozen"].get("safety_review_as_recorded_NOT_CLEARED") != (
                    versions["observed"].get("safety_review_as_recorded_NOT_CLEARED")):
                flags.add("SAFETY_METADATA_CHANGED_NOT_CLEARANCE")
            if versions["frozen"].get("status_as_recorded_NOT_REVIEWED") != (
                    versions["observed"].get("status_as_recorded_NOT_REVIEWED")):
                flags.add("PUBLISH_STATUS_CHANGED_NOT_AUTHORIZATION")
            if (old["citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"] and
                    new["citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"] and
                    old["citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"] !=
                    new["citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"]):
                flags.add("CITATION_CONTEXT_OR_POSITION_CHANGED_NOT_SUPPORT_PROOF")
            if not flags:
                flags.add("UNCHANGED_REFERENCE_NOT_INDEPENDENTLY_REVERIFIED")
            names = sorted(flags)
            flags_count.update(names)
            key = {
                "article_cluster": cluster, "article_slug": slug,
                "source_id": sid,
                "frozen_body_sha256": old["body_sha256"],
                "observed_body_sha256": new["body_sha256"],
                "frozen_citation_context_sha256":
                    r62.digest(old["citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"]),
                "observed_citation_context_sha256":
                    r62.digest(new["citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"]),
                "frozen_source_use_sha256": r62.digest(
                    [old["source_use_present"],
                     old["source_use_note_UNABRIDGED_NOT_SUPPORT_PROOF"]]),
                "observed_source_use_sha256": r62.digest(
                    [new["source_use_present"],
                     new["source_use_note_UNABRIDGED_NOT_SUPPORT_PROOF"]]),
                "frozen_source_candidate_ids_sha256":
                    r62.digest([(c["cluster"], c["reading_sha256"]) for c in
                                old["source_candidates_DISTINCT_NOT_CLAIM_SUPPORT"]]),
                "observed_source_candidate_ids_sha256":
                    r62.digest([(c["cluster"], c["reading_sha256"]) for c in
                                new["source_candidates_DISTINCT_NOT_CLAIM_SUPPORT"]]),
            }
            rows.append({
                "work_order_sha256": r62.digest(key),
                "article_cluster": cluster, "article_slug": slug,
                "source_id": sid, "review_flags_NOT_FINDINGS": names,
                "versions": details,
                "human_claim_support": "NOT_REVIEWED",
                "qualified_safety_review": "NOT_REVIEWED",
            })
    need(len(seen_articles) == 29 and
         census["frozen"] == lineage["counts"]["old_citation_occurrences"] and
         census["observed"] == lineage["counts"][
             "observed_citation_occurrences_UNVERIFIED"],
         "contributor article/citation occurrence coverage lost")
    need(len({x["work_order_sha256"] for x in rows}) == len(rows),
         "dependency-review work-order fingerprint collision")
    # Every original and observed occurrence is accounted for exactly once.
    for version in census:
        need(sum(len(row["versions"][version][
            "citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"])
            for row in rows) == census[version],
             "original or proposed citation occurrence lost")
    result = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "machine_only": True,
        "parent_R61_sha256": lineage["fingerprint_sha256"],
        "parent_R62_sha256": docket["fingerprint_sha256"],
        "parent_R63_sha256": source_report["fingerprint_sha256"],
        "article_source_dependency_work_orders_ALL_NOT_APPROVED": rows,
        "counts": {"original_articles": 29, "work_orders": len(rows),
                   "citation_occurrences": census,
                   "review_flags_NOT_VERDICTS": dict(sorted(flags_count.items()))},
        "other_six_integrated_articles_NOT_REVIEWED_HERE": 6,
        "original_full_R58_35_article_1959_citations_NOT_REVALIDATED_HERE": True,
        "existing_R14_provenance_discrepancy_OPEN": True,
        "limitations": ("Source IDs, article references and preserved text are candidate "
                        "relationships, never proof of claim support, safety or link access. "
                        "No contributor change is integrated and no reviewer note grants approval."),
        **{k: False for k in HOLD},
    }
    result["fingerprint_sha256"] = r62.digest(result)
    return result


def make_report(lineage, docket, source_report):
    try:
        r63.verify_report(source_report, lineage, docket)
    except (r63.SourceHold, r62.ReviewHold, KeyError, TypeError, ValueError) as exc:
        raise DependencyHold("original R63 Git-derived crosswalk failed verification") from exc
    need(lineage.get("existing_R14_exception_remains_open") is True and
         all(lineage.get(k) is False and docket.get(k) is False and
             source_report.get(k) is False for k in HOLD),
         "upstream source or safety release state was changed")
    return _construct(lineage, docket, source_report)


def verify_report(report, lineage, docket, source_report):
    need(type(report) is dict and
         report == make_report(lineage, docket, source_report),
         "article/source dependency packet differs from regenerated evidence")
    return True


def csv_workbook(report, lineage, docket, source_report):
    verify_report(report, lineage, docket, source_report)
    out = io.StringIO(newline="")
    writer = csv.writer(out, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerow(FIELDS)
    for row in report["article_source_dependency_work_orders_ALL_NOT_APPROVED"]:
        a, b = row["versions"]["frozen"], row["versions"]["observed"]
        writer.writerow((
            row["work_order_sha256"], row["article_cluster"], row["article_slug"],
            row["source_id"],
            len(a["citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"]),
            len(b["citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"]),
            str(a["source_use_present"]).lower(),
            str(b["source_use_present"]).lower(),
            len(a["source_candidates_DISTINCT_NOT_CLAIM_SUPPORT"]),
            len(b["source_candidates_DISTINCT_NOT_CLAIM_SUPPORT"]),
            ";".join(row["review_flags_NOT_FINDINGS"]), "",
        ))
    return out.getvalue().encode("utf-8")


def quarantine_notes(report, lineage, docket, source_report, returned):
    baseline = csv_workbook(report, lineage, docket, source_report)
    need(type(returned) is bytes and len(returned) <= MAX_CSV_BYTES,
         "missing or oversized untrusted reviewer worksheet")
    try:
        actual = list(csv.reader(io.StringIO(
            returned.decode("utf-8", "strict"), newline=""), strict=True))
        expected = list(csv.reader(io.StringIO(
            baseline.decode("utf-8"), newline=""), strict=True))
    except (UnicodeError, csv.Error) as exc:
        raise DependencyHold("returned worksheet not strict UTF-8/CSV") from exc
    need(len(actual) == len(expected) and
         actual[0] == list(FIELDS), "review worksheet header/row count changed")
    notes = []
    for n, (row, ref) in enumerate(zip(actual[1:], expected[1:]), 1):
        need(len(row) == len(FIELDS) and row[:-1] == ref[:-1],
             "protected citation/source fields or row ordering changed")
        note = row[-1]
        normalized = unicodedata.normalize("NFKC", note)
        need(len(note) <= 3000 and
             not any(unicodedata.category(c) in ("Cc", "Cf", "Cs", "Zl", "Zp")
                     for c in note) and
             not normalized.lstrip().startswith(("=", "+", "-", "@")),
             "formula/spoofing/control characters in returned notes")
        if note:
            notes.append({"work_order_sha256": ref[0], "ordinal": n,
                          "untrusted_note_NOT_VERIFIED": note,
                          "review_state": "UNTRUSTED_NOT_REVIEWED"})
    packet = {
        "schema": NOTE_SCHEMA, "issue": 136, "release_state": "HOLD",
        "machine_only": True,
        "parent_R64_sha256": report["fingerprint_sha256"],
        "returned_csv_sha256": hashlib.sha256(returned).hexdigest(),
        "unsigned_untrusted_notes": notes,
        **{k: False for k in HOLD},
    }
    packet["fingerprint_sha256"] = r62.digest(packet)
    return packet


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--remote", default="origin")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--summary", action="store_true")
    modes.add_argument("--csv", action="store_true")
    args = parser.parse_args(argv)
    need(re.fullmatch(r"[A-Za-z0-9_-]+", args.remote) is not None,
         "remote must be a trusted plain Git remote name")
    parent = Path(__file__).with_name("r61_contributor_version_source_lineage.py")
    need(parent.is_file() and not parent.is_symlink(),
         "R61 Git provenance prerequisite unavailable")
    try:
        proc = subprocess.run(
            [sys.executable, "-I", str(parent), "--repo-root",
             str(args.repo_root), "--remote", args.remote],
            capture_output=True, check=False, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DependencyHold("trusted Git-object evidence unavailable") from exc
    need(proc.returncode == 0 and 0 < len(proc.stdout) <= MAX_JSON_BYTES,
         "R61 Git-custody regeneration failed closed; cached packet not accepted")
    try:
        lineage = r62.strict_load(proc.stdout.decode("utf-8", "strict"))
        docket = r62.make_report(lineage)
        sources = r63.make_report(lineage, docket)
        report = make_report(lineage, docket, sources)
    except (UnicodeError, ValueError, TypeError, KeyError) as exc:
        raise DependencyHold("trusted R61/R62/R63 lineage regeneration failed") from exc
    if args.csv:
        sys.stdout.buffer.write(csv_workbook(report, lineage, docket, sources))
    else:
        data = ({"schema": SCHEMA, "release_state": "HOLD",
                 "counts": report["counts"],
                 "fingerprint_sha256": report["fingerprint_sha256"]}
                if args.summary else report)
        sys.stdout.write(json.dumps(data, sort_keys=True, indent=2,
                                    ensure_ascii=False, allow_nan=False) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (DependencyHold, OSError) as exc:
        print("R64 PRIVATE ARTICLE/SOURCE REVIEW HOLD: " + str(exc),
              file=sys.stderr)
        raise SystemExit(2)
