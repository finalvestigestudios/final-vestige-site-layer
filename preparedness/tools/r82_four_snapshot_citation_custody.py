#!/usr/bin/env python3
"""R82 private HOLD: four-snapshot citation/source/safety-state drift custody.

The immutable R14 frozen contributor, historical integrated tree, exact current
Claude contributor, and separate RC are compared as *data*. Nothing is merged,
normalized into an approved source, written, published, or medically cleared.
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

SCHEMA = "r82-four-snapshot-article-citation-source-metadata-custody-hold-v1"
STAGES = ("frozen", "integrated", "current", "rc")
STAGE_PAIRS = (("frozen", "current"), ("current", "rc"), ("integrated", "rc"))
REVIEW = "NOT_REVIEWED"
CITE = re.compile(rb"\{\{cite:([^{}]+)\}\}")
FIELDS_TO_FLAG = ("url", "title", "publisher", "kind", "supports", "notes",
                  "published", "updated", "reviewed", "verified_on",
                  "human_link_check")
STATES = ("human_source_review", "human_claim_support",
          "qualified_safety_review", "human_release_review")


class Hold(ValueError):
    """Fail closed if the evidence or non-publication contract is violated."""


def need(ok, detail):
    if not ok:
        raise Hold(detail)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      allow_nan=False, separators=(",", ":")).encode("utf-8")


def r81_module():
    file = Path(__file__).with_name("r81_frozen_contributor_threeway_custody.py")
    need(file.is_file() and not file.is_symlink(), "R81 custody tool missing")
    spec = importlib.util.spec_from_file_location("r82_r81_parent", file)
    need(spec is not None and spec.loader is not None, "R81 unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def strict_json(raw: bytes, context: str):
    """Reject duplicate object keys, nonfinite numbers, invalid UTF-8 and trailing data."""
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON object key in " + context)
            result[key] = value
        return result

    def no_constant(value):
        raise Hold("nonfinite JSON constant in " + context)

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                          parse_constant=no_constant)
    except (ValueError, UnicodeError) as exc:
        raise Hold("invalid JSON / UTF-8 in " + context) from exc


def fragment(raw: bytes, origin: str, stage: str) -> dict:
    need(stage in STAGES and type(origin) is str and bool(origin),
         "invalid stage or origin")
    content = strict_json(raw, origin + "/" + stage)
    need(type(content) is dict and type(content.get("sources")) is list,
         "missing complete source reading list")
    items, ids = [], set()
    for ordinal, item in enumerate(content["sources"]):
        need(type(item) is dict and type(item.get("id")) is str
             and bool(item["id"]) and type(item.get("url")) is str
             and bool(item["url"]) and item["id"] not in ids,
             "invalid or duplicate origin-scoped source")
        if stage == "rc":
            need(item.get("human_link_check") is False,
                 "RC source has human approval or unknown review state")
        ids.add(item["id"])
        items.append({"ordinal": ordinal, "raw_source_id": item["id"],
                      "literal_url_UNVERIFIED": item["url"],
                      "complete_reading_UNABRIDGED_NOT_APPROVED": item,
                      "reading_sha256": sha(canonical(item)),
                      "human_source_review": REVIEW})
    return {"origin": origin, "stage": stage,
            "complete_source_fragment_UTF8": raw.decode("utf-8"),
            "fragment_sha256": sha(raw), "source_count": len(items),
            "source_readings_UNABRIDGED": items, "may_publish": False}


def citations(raw: bytes) -> list[dict]:
    """Byte-accurate offsets and source IDs; do not infer citation applicability."""
    try:
        raw.decode("utf-8")
    except UnicodeError as exc:
        raise Hold("article body is not UTF-8") from exc
    output = []
    for n, match in enumerate(CITE.finditer(raw)):
        try:
            ident = match.group(1).decode("utf-8")
        except UnicodeError as exc:
            raise Hold("citation identifier is not UTF-8") from exc
        need(bool(ident) and ident == ident.strip(), "empty/ambiguous citation ID")
        output.append({"ordinal": n, "byte_offset": match.start(),
                       "line_number": raw.count(b"\n", 0, match.start()) + 1,
                       "literal_token": match.group(0).decode("utf-8"),
                       "raw_source_id": ident,
                       "claim_support_review": REVIEW})
    return output


def metadata(raw: bytes, origin: str, stage: str) -> dict:
    obj = strict_json(raw, origin + "/" + stage + "/meta")
    need(type(obj) is dict and type(obj.get("slug")) is str
         and bool(obj["slug"]), "article metadata missing slug")
    if stage == "rc":
        status, safety = obj.get("status"), obj.get("safety_review")
        need(type(status) is dict and status.get("publish") not in
             ("publish", "published", "live", True)
             and type(safety) is dict and safety.get("state") not in
             ("approved", "passed", "cleared", "safe", True),
             "RC metadata purports to publish or clear safety")
    return {"complete_metadata_UTF8": raw.decode("utf-8"),
            "metadata_sha256": sha(raw), "metadata_UNABRIDGED": obj,
            "human_release_review": REVIEW}


def record_changes(before: dict | None, after: dict | None) -> dict:
    """Differentiate missing/add/remove from same-ID mutation, never alias IDs."""
    if before is None or after is None:
        return {"presence": ("ADDED" if before is None else "REMOVED"),
                "changed_fields": [], "different_reading": True}
    a = before["complete_reading_UNABRIDGED_NOT_APPROVED"]
    b = after["complete_reading_UNABRIDGED_NOT_APPROVED"]
    return {"presence": "BOTH",
            "changed_fields": sorted(k for k in set(a) | set(b)
                                     if a.get(k) != b.get(k)
                                     or (k in a) != (k in b)),
            "different_reading": before["reading_sha256"] != after["reading_sha256"]}


def compare_sources(versions: dict[tuple[str, str], dict]) -> list[dict]:
    """One row per origin+literal ID, with all four complete distinct readings."""
    need(all(stage in STAGES for _, stage in versions), "unknown source stage")
    groups = defaultdict(dict)
    for (origin, stage), frag in versions.items():
        for item in frag["source_readings_UNABRIDGED"]:
            key = (origin, item["raw_source_id"])
            need(stage not in groups[key], "reused source ID within stage")
            groups[key][stage] = item
    rows = []
    for (origin, sid), records in sorted(groups.items()):
        versions4 = {stage: records.get(stage) for stage in STAGES}
        differences = {a + "_TO_" + b: record_changes(versions4[a], versions4[b])
                       for a, b in STAGE_PAIRS}
        rows.append({"origin": origin, "literal_source_id": sid,
                     "four_distinct_snapshot_readings": versions4,
                     "comparison": differences, "human_source_review": REVIEW,
                     "qualified_safety_review": REVIEW, "may_publish": False})
    return rows


def article(raw: bytes, meta_raw: bytes, origin: str, path: str,
            stage: str, stage_index: dict[str, list[dict]]) -> dict:
    need(stage in STAGES, "unknown article stage")
    body = raw.decode("utf-8")  # preserve every byte's decoded text
    events = citations(raw)
    for event in events:
        possible = stage_index.get(event["raw_source_id"], [])
        event["distinct_scoped_source_variants_NOT_ALIASED"] = [
            {"origin": src["origin"], "literal_source_id": src["source_id"],
             "reading_sha256": src["reading_sha256"]}
            for src in possible]
        event["scope_state"] = ("OUTSIDE_SEVEN_FRAGMENT_SCOPE" if not possible
                                else "MULTIPLE_ORIGIN_VARIANTS_UNRESOLVED"
                                if len(possible) > 1 else
                                "ONE_SCOPED_CANDIDATE_NOT_CLAIM_PROOF")
    meta = metadata(meta_raw, origin, stage)
    need(meta["metadata_UNABRIDGED"]["slug"] ==
         Path(path).name.removesuffix(".body.html"),
         "article metadata slug does not match body path")
    return {"origin": origin, "path": path, "stage": stage,
            "complete_HTML_UTF8": body, "body_sha256": sha(raw),
            "citations_in_original_order": events, "citation_count": len(events),
            "metadata": meta, "claim_review": REVIEW,
            "qualified_safety_review": REVIEW, "may_publish": False}


def compare_articles(four: dict[str, dict]) -> dict:
    need(set(four) == set(STAGES), "four article snapshots required")
    comparisons = {}
    for a, b in STAGE_PAIRS:
        left, right = four[a], four[b]
        ids_a = [e["raw_source_id"] for e in left["citations_in_original_order"]]
        ids_b = [e["raw_source_id"] for e in right["citations_in_original_order"]]
        removed, added = Counter(ids_a) - Counter(ids_b), Counter(ids_b) - Counter(ids_a)
        body_changed = left["body_sha256"] != right["body_sha256"]
        comparisons[a + "_TO_" + b] = {
            "body_changed": body_changed,
            "metadata_changed": left["metadata"]["metadata_sha256"] !=
                                right["metadata"]["metadata_sha256"],
            "citation_order_changed": ids_a != ids_b,
            "citation_counts_removed": dict(sorted(removed.items())),
            "citation_counts_added": dict(sorted(added.items())),
            "wording_changed_without_citation_sequence_change_REVIEW":
                body_changed and ids_a == ids_b,
            "claim_support_review": REVIEW,
        }
    return comparisons


def construct(article_snapshots: list[dict], fragments: list[dict],
              r81_report: dict) -> dict:
    """Pure sealed report constructor, also used by isolated synthetic tests."""
    need(type(article_snapshots) is list and type(fragments) is list,
         "missing evidence lists")
    origins = list(r81_report["branch_reviews"])
    need(len(origins) == 7 and len(article_snapshots) == 29 * 4
         and len(fragments) == 7 * 4, "7 origins / 29 articles / four histories missing")
    need(len({(x["origin"], x["path"], x["stage"])
              for x in article_snapshots}) == 116
         and len({(x["origin"], x["stage"]) for x in fragments}) == 28,
         "duplicate or missing snapshot identities")
    by_article = defaultdict(dict)
    for x in article_snapshots:
        by_article[(x["origin"], x["path"])][x["stage"]] = x
    need(len(by_article) == 29 and all(set(four) == set(STAGES)
                                       for four in by_article.values()),
         "incomplete four-stage article grouping")
    row_sources = compare_sources({(x["origin"], x["stage"]): x
                                   for x in fragments})
    rows = []
    for (origin, path), four in sorted(by_article.items()):
        rows.append({"origin": origin, "path": path,
                     "four_unabridged_HTML_and_metadata_snapshots": {
                         k: four[k] for k in STAGES},
                     "drift": compare_articles(four),
                     "human_claim_support": REVIEW,
                     "qualified_safety_review": REVIEW, "may_publish": False})
    rc_readings = sum(f["source_count"] for f in fragments if f["stage"] == "rc")
    r81_expected = r81_report["counts"]["rc_fragment_source_readings_UNREVIEWED"]
    need(rc_readings == r81_expected, "R81 contributor source readings lost")
    report = {"schema": SCHEMA, "issue": 136, "release_state": "HOLD",
              "may_publish": False, "human_source_approvals": 0,
              "human_claim_approvals": 0, "qualified_safety_approvals": 0,
              "independent_QD_approvals": 0, "medical_safety_approved": False,
              "r81_provenance_seal": r81_report["sha256_seal"],
              "separate_RC_sha": r81_report["separate_rc_commit"],
              "counts": {"origins": 7, "authored_article_groups": len(rows),
                         "unabridged_article_snapshots": len(article_snapshots),
                         "unabridged_source_fragments": len(fragments),
                         "origin_scoped_RC_readings": rc_readings,
                         "source_ID_histories": len(row_sources),
                         "changed_RC_vs_current_article_bodies": sum(
                             x["drift"]["current_TO_rc"]["body_changed"] for x in rows),
                         "wording_changes_with_same_citations_REVIEW": sum(
                             x["drift"]["current_TO_rc"][
                                 "wording_changed_without_citation_sequence_change_REVIEW"]
                             for x in rows),
                         "changed_RC_vs_current_source_readings": sum(
                             x["comparison"]["current_TO_rc"]["different_reading"]
                             for x in row_sources)},
              "all_four_snapshot_source_fragments_UNABRIDGED": fragments,
              "all_four_snapshot_source_histories_NOT_ALIASED": row_sources,
              "all_29_article_citation_metadata_histories_UNABRIDGED": rows}
    report["sha256_seal"] = sha(canonical(report))
    return report


def verify(report: dict) -> None:
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("issue") == 136 and report.get("release_state") == "HOLD"
         and report.get("may_publish") is False
         and report.get("medical_safety_approved") is False
         and all(report.get(k) == 0 for k in
                 ("human_source_approvals", "human_claim_approvals",
                  "qualified_safety_approvals", "independent_QD_approvals")),
         "approval, medical-safety or public release state altered")
    payload = {k: v for k, v in report.items() if k != "sha256_seal"}
    need(report.get("sha256_seal") == sha(canonical(payload)),
         "four-snapshot custody ledger digest mismatch")
    counts = report["counts"]
    fragments = report["all_four_snapshot_source_fragments_UNABRIDGED"]
    rows = report["all_29_article_citation_metadata_histories_UNABRIDGED"]
    need((counts["origins"], counts["authored_article_groups"],
          counts["unabridged_article_snapshots"],
          counts["unabridged_source_fragments"]) == (7, 29, 116, 28)
         and len(fragments) == 28 and len(rows) == 29,
         "source / authored article inventory incomplete")
    for item in fragments:
        raw = item["complete_source_fragment_UTF8"].encode("utf-8")
        need(item["fragment_sha256"] == sha(raw)
             and item == fragment(raw, item["origin"], item["stage"]),
             "source fragment reconstruction mismatch")
    seen = set()
    for group in rows:
        need(group["may_publish"] is False
             and group["human_claim_support"] == REVIEW
             and group["qualified_safety_review"] == REVIEW,
             "article row incorrectly reviewed")
        four = group["four_unabridged_HTML_and_metadata_snapshots"]
        need(set(four) == set(STAGES), "article lost a historical state")
        for stage, row in four.items():
            key = (row["origin"], row["path"], stage)
            need(key not in seen, "duplicate authored article snapshot")
            seen.add(key)
            body = row["complete_HTML_UTF8"].encode("utf-8")
            meta = row["metadata"]["complete_metadata_UTF8"].encode("utf-8")
            need(sha(body) == row["body_sha256"]
                 and sha(meta) == row["metadata"]["metadata_sha256"]
                 and row["citation_count"] == len(citations(body))
                 and [e["raw_source_id"] for e in row["citations_in_original_order"]]
                     == [e["raw_source_id"] for e in citations(body)]
                 and row["may_publish"] is False
                 and row["claim_review"] == REVIEW
                 and row["qualified_safety_review"] == REVIEW,
                 "unabridged article/citation/metadata custody mismatch")
    need(len(seen) == 116, "article count inconsistent")


def live_report(root: Path | None = None) -> dict:
    parent = r81_module()
    base = root or Path(__file__).resolve().parents[2]
    manifest = strict_json((base / parent.MANIFEST).read_bytes(), "immutable R14")
    r81_report = parent.three_way(
        base, manifest, {origin: pin[1] for origin, pin in parent.PINNED.items()},
        parent.RC_SHA, verify_remote=True)
    parent.verify(r81_report)
    ref_integrated = manifest["reference_integrated_commit_sha"]
    fragments, pending = [], []
    for branch in manifest["branches"]:
        origin = branch["name"]
        refs = {"frozen": branch["contributor_commit_sha"],
                "integrated": ref_integrated,
                "current": parent.PINNED[origin][1],
                "rc": parent.RC_SHA}
        for stage in STAGES:
            source_path = "preparedness/sources/fragments/" + origin + ".json"
            _, raw = parent.blob(base, refs[stage], source_path)
            fragments.append(fragment(raw, origin, stage))
        for file in branch["files"]:
            path = file["path"]
            if not path.endswith(".body.html"):
                continue
            meta_path = path.removesuffix(".body.html") + ".meta.json"
            need(meta_path in {v["path"] for v in branch["files"]},
                 "article body without inventoried metadata")
            for stage in STAGES:
                _, body = parent.blob(base, refs[stage], path)
                _, meta = parent.blob(base, refs[stage], meta_path)
                pending.append((origin, path, stage, body, meta))
    stage_indices = {stage: defaultdict(list) for stage in STAGES}
    for frag in fragments:
        for source in frag["source_readings_UNABRIDGED"]:
            stage_indices[frag["stage"]][source["raw_source_id"]].append({
                "origin": frag["origin"], "source_id": source["raw_source_id"],
                "reading_sha256": source["reading_sha256"]})
    entries = [article(body, meta, origin, path, stage, stage_indices[stage])
               for origin, path, stage, body, meta in pending]
    report = construct(entries, fragments, r81_report)
    verify(report)
    return report


def safe_csv(cell: object) -> str:
    value = str(cell)
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else value


def reviewer_csv(report: dict) -> str:
    verify(report)
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["type", "origin", "path_or_source_id",
                     "current_vs_rc_change", "human_review", "release"])
    for row in report["all_29_article_citation_metadata_histories_UNABRIDGED"]:
        d = row["drift"]["current_TO_rc"]
        writer.writerow(["article", safe_csv(row["origin"]), safe_csv(row["path"]),
                         "BODY" if d["body_changed"] else
                         "META" if d["metadata_changed"] else "UNCHANGED",
                         REVIEW, "HOLD"])
    for row in report["all_four_snapshot_source_histories_NOT_ALIASED"]:
        d = row["comparison"]["current_TO_rc"]
        writer.writerow(["source", safe_csv(row["origin"]),
                         safe_csv(row["literal_source_id"]),
                         "READING" if d["different_reading"] else "UNCHANGED",
                         REVIEW, "HOLD"])
    return stream.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-stdout", action="store_true",
                        help="Unabridged PRIVATE reviewer ledger; NEVER upload publicly")
    parser.add_argument("--csv-stdout", action="store_true",
                        help="One-way PRIVATE review queue, NOT publication data")
    args = parser.parse_args(argv)
    need(not (args.csv_stdout and args.json_stdout), "choose one private export")
    report = live_report()
    if args.json_stdout:
        print(json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2,
                         allow_nan=False))
    elif args.csv_stdout:
        print(reviewer_csv(report), end="")
    else:
        print(json.dumps({"schema": SCHEMA, "release": "HOLD",
                          "counts": report["counts"], "seal": report["sha256_seal"],
                          "source_claim_safety_QD_approvals": 0,
                          "WordPress_or_publication_writes": 0},
                         sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (Hold, ValueError, KeyError, TypeError, OSError) as exc:
        raise SystemExit("R82 FAILED CLOSED — " + str(exc))
