#!/usr/bin/env python3
"""R54: private reviewer-ready CSV/JSON packet for R53 qualitative work orders.

Lossless evidence travels in original_evidence.json; escaped CSV is presentation.
This does NOT retrieve sources, perform human review, approve safety/QD or publish.
Default invocation is read-only; optional files stay under preparedness/build only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = (36, 779, 237, 542, 15, 25)
R53_SCHEMA = "r53-qualitative-source-scoped-human-review-queue-v1"
STATE = "PENDING_INDEPENDENT_CLAIM_SOURCE_SCOPE_AND_SAFETY_REVIEW"
HEX = re.compile(r"[0-9a-f]{64}\Z")
PRESENTATION = "PRIVATE_UNVERIFIED_HUMAN_REVIEW_WORKSHEET_NOT_APPROVAL"
FALSE_FLAGS = (
    "may_publish", "qualified_safety_clearance", "independent_QD_approval",
    "human_source_links_verified", "claim_accuracy_verified",
)
BIDI = frozenset(list(range(0x202A, 0x202F)) +
                 list(range(0x2066, 0x206A)) + [0x061C, 0x200E, 0x200F])
ACTION = (
    "work_order_id_sha256", "article", "block_ordinal",
    "original_article_html_sha256", "original_R13_flag_sha256",
    "risk_families_machine_flags_json", "machine_priority_not_safety_diagnosis",
    "excerpt_not_factually_verified", "excerpt_truncated",
    "citation_source_id_occurrences_json", "same_block_citation_count",
    "source_readings_count", "uncited_in_same_visible_block",
    "historical_safety_metadata_NOT_clearance", "review_state",
    "human_reviewer_name_blank", "human_review_date_blank",
    "human_claim_support_decision_blank", "human_qualified_safety_decision_blank",
    "human_exceptions_notes_blank",
)
SOURCE = (
    "work_order_id_sha256", "article", "block_ordinal", "source_id",
    "citation_occurrences_in_block", "original_url",
    "article_contributor_origin", "source_contributor_origin",
    "original_source_record_sha256", "original_source_use",
    "original_source_reading_scope", "original_source_supports_note",
    "shared_url_group_requires_human_review", "base_fallback_requires_human_review",
    "historically_machine_inaccessible_source_id", "review_state",
    "human_source_access_date_blank", "human_exact_source_locator_blank",
    "human_claim_support_assessment_blank", "human_scope_and_discrepancy_notes_blank",
)
INCIDENT = (
    "incident_id", "severity", "review_state", "human_domain_reviewer_blank",
    "human_qualified_decision_blank", "human_review_date_blank", "human_notes_blank",
)
BLOCKED = (
    "original_source_id", "historical_machine_failure_only",
    "human_current_link_check_blank", "human_review_date_blank",
    "human_retrieval_route_blank", "human_excerpt_locator_blank",
)
TABLES = {
    "action_review.csv": ACTION,
    "scoped_source_review.csv": SOURCE,
    "open_safety_exceptions.csv": INCIDENT,
    "historical_source_access_hold.csv": BLOCKED,
}


class PacketHold(ValueError):
    """Unreviewed action/source evidence is missing, changed or promoted."""


def require(ok, why):
    if not ok:
        raise PacketHold(why)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_ok(value):
    return type(value) is str and HEX.fullmatch(value) is not None


def _safe_cell(value):
    """Escape dangerous spreadsheet syntax without mutating source JSON.

    No CSV export can be the sole archival record: original_evidence.json keeps
    full Unicode, repeated IDs, all reading notes, ordinals and source origins.
    """
    if value is None:
        return ""
    if type(value) is bool:
        value = "true" if value else "false"
    elif type(value) in (list, dict):
        value = canonical(value).decode("utf-8")
    elif type(value) is not str:
        value = str(value)
    out = []
    for char in value:
        cp = ord(char)
        if cp == 92:
            out.append("\\\\")
        elif char == "\r":
            out.append("\\r")
        elif char == "\n":
            out.append("\\n")
        elif char == "\t":
            out.append("\\t")
        elif cp < 32 or cp == 127 or cp in BIDI:
            out.append("\\u%04x" % cp)
        else:
            out.append(char)
    result = "".join(out)
    if result.lstrip(" \ufeff\u200b\u2060\u00a0").startswith(("=", "+", "-", "@")):
        result = "'" + result
    return result


def csv_table(columns, rows):
    require(type(columns) is tuple and columns and len(set(columns)) == len(columns),
            "invalid reviewer table columns")
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\r\n")
    writer.writerow(columns)
    for row in rows:
        require(type(row) is dict and set(row) == set(columns),
                "reviewer row missing or adding unexpected fields")
        writer.writerow([_safe_cell(row[key]) for key in columns])
    content = stream.getvalue()
    expected = [list(columns)] + [
        [_safe_cell(row[key]) for key in columns] for row in rows
    ]
    parsed = list(csv.reader(io.StringIO(content, newline="")))
    require(parsed == expected, "CSV encoding lost reviewer evidence")
    return content.encode("utf-8")


def simple_https(url):
    if type(url) is not str or not url.startswith("https://") or len(url) > 8192:
        return False
    if any(ord(c) < 33 or ord(c) == 127 or c == "\\" for c in url):
        return False
    try:
        parsed = urlsplit(url)
        return bool(parsed.hostname and not parsed.username and not parsed.password)
    except ValueError:
        return False


def audit_report(report, *, expected=EXPECTED):
    """Validate all R53 row relationships and create complete reviewer rows.

    Production CLI re-derives R53 from the actual archive; a self-hashed
    external report alone is not an independent trust or human approval anchor.
    """
    require(type(expected) is tuple and len(expected) == 6
            and all(type(n) is int and n >= 0 for n in expected),
            "invalid frozen expected review census")
    items, flags, uncited, cited, incidents, historical = expected
    require(type(report) is dict and report.get("schema") == R53_SCHEMA
            and report.get("issue") == 136
            and report.get("release_state") == "HOLD"
            and report.get("machine_authority") ==
                "R13_HEURISTIC_RETRIAGE_PLUS_ORIGINAL_CONTRIBUTOR_SOURCE_SCOPE"
            and report.get("article_count") == items
            and all(report.get(k) is False for k in FALSE_FLAGS),
            "R53 report lost private machine-only HOLD authority")
    require(sha_ok(report.get("fingerprint_sha256")) and
            report["fingerprint_sha256"] == digest({
                k: v for k, v in report.items() if k != "fingerprint_sha256"
            }), "original R53 evidence fingerprint incorrect")
    counts = report.get("counts")
    orders = report.get("work_orders")
    sx = report.get("open_safety_incidents")
    historic_ids = report.get("blocked_historical_source_ids_not_current_link_failures")
    require(type(counts) is dict and type(orders) is list and
            len(orders) == flags and type(sx) is list and len(sx) == incidents and
            type(historic_ids) is list and len(historic_ids) == historical and
            counts.get("uncited_action_blocks") == uncited and
            counts.get("cited_action_blocks") == cited and
            counts.get("open_safety_exceptions") == incidents and
            counts.get("unresolved_historic_source_ids") == historical,
            "original R53 action, safety or blocked-source census changed")
    action_rows, source_rows, seen_work = [], [], set()
    counted_uncited = counted_cited = 0
    for row in orders:
        require(type(row) is dict and row.get("review_state") == STATE
                and all(row.get(k) is False for k in
                        ("claim_support_verified", "qualified_safety_clearance",
                         "independent_QD_approval", "may_publish"))
                and sha_ok(row.get("work_order_id_sha256"))
                and sha_ok(row.get("original_article_html_sha256"))
                and sha_ok(row.get("original_R13_flag_sha256")),
                "review order identity, HOLD or original SHA invalid")
        wid = row["work_order_id_sha256"]
        slug, ordinal = row.get("article"), row.get("block_ordinal")
        occurrence = row.get("citation_source_id_occurrences")
        readings = row.get("source_readings_in_article_scope")
        risks = row.get("risk_families_machine_flags")
        require(type(slug) is str and bool(slug) and
                type(ordinal) is int and ordinal >= 1 and
                type(occurrence) is list and
                all(type(s) is str and bool(s) for s in occurrence) and
                type(readings) is list and type(risks) is list and
                all(type(r) is str and bool(r) for r in risks) and
                type(row.get("excerpt_not_factually_verified")) is str and
                type(row.get("excerpt_truncated")) is bool and
                type(row.get("uncited_in_same_visible_block")) is bool and
                row["uncited_in_same_visible_block"] == (not occurrence) and
                row.get("machine_priority_not_safety_diagnosis") in
                  ("HIGH_MACHINE_REVIEW_PRIORITY", "STANDARD_MACHINE_REVIEW_PRIORITY"),
                "review order missing original qualitative evidence")
        key = {"slug": slug, "block_ordinal": ordinal,
               "original_article_html_sha256": row["original_article_html_sha256"],
               "original_R13_flag_sha256": row["original_R13_flag_sha256"],
               "citation_source_id_occurrences": occurrence}
        require(digest(key) == wid and wid not in seen_work,
                "work order digest, duplicate or original position mismatch")
        seen_work.add(wid)
        unique = list(dict.fromkeys(occurrence))
        require(len(readings) == len(unique),
                "lost or deduplicated contributor-scoped source reading")
        source_ids = []
        for scope in readings:
            require(type(scope) is dict and
                    type(scope.get("source_id")) is str and
                    scope["source_id"] in unique and
                    type(scope.get("citation_occurrences_in_block")) is int and
                    scope["citation_occurrences_in_block"] ==
                        occurrence.count(scope["source_id"]) and
                    simple_https(scope.get("original_url")) and
                    sha_ok(scope.get("original_source_record_sha256")) and
                    all(type(scope.get(k)) is str for k in (
                        "article_contributor_origin", "source_contributor_origin",
                        "original_source_use", "original_source_reading_scope",
                        "original_source_supports_note")) and
                    all(type(scope.get(k)) is bool for k in (
                        "shared_url_group_requires_human_review",
                        "base_fallback_requires_human_review",
                        "historically_machine_inaccessible_source_id")) and
                    all(scope.get(k) is False for k in (
                        "independent_source_scope_verified", "human_source_link_checked",
                        "claim_supported_by_source_verified")),
                    "source-scoped review evidence altered or promoted")
            source_ids.append(scope["source_id"])
            source_rows.append(dict(zip(SOURCE, (
                wid, slug, ordinal, scope["source_id"],
                scope["citation_occurrences_in_block"], scope["original_url"],
                scope["article_contributor_origin"], scope["source_contributor_origin"],
                scope["original_source_record_sha256"], scope["original_source_use"],
                scope["original_source_reading_scope"],
                scope["original_source_supports_note"],
                scope["shared_url_group_requires_human_review"],
                scope["base_fallback_requires_human_review"],
                scope["historically_machine_inaccessible_source_id"],
                "NOT_REVIEWED", "", "", "", "",
            ))))
        require(source_ids == unique, "source reading order or repeated IDs changed")
        counted_uncited += not occurrence
        counted_cited += bool(occurrence)
        action_rows.append(dict(zip(ACTION, (
            wid, slug, ordinal, row["original_article_html_sha256"],
            row["original_R13_flag_sha256"], risks,
            row["machine_priority_not_safety_diagnosis"],
            row["excerpt_not_factually_verified"], row["excerpt_truncated"],
            occurrence, len(occurrence), len(readings), not occurrence,
            row.get("article_historical_safety_review_state_not_qualified_approval"),
            "NOT_REVIEWED", "", "", "", "", "",
        ))))
    require(len(seen_work) == flags and counted_uncited == uncited and
            counted_cited == cited,
            "qualitative review row classification or coverage drift")
    incident_rows, incident_ids = [], set()
    for obj in sx:
        require(type(obj) is dict and type(obj.get("id")) is str and
                obj["id"] not in incident_ids and obj.get("state") == "HOLD" and
                obj.get("severity") in ("HIGH", "MEDIUM", "LOW"),
                "missing or falsely cleared safety incident")
        incident_ids.add(obj["id"])
        incident_rows.append(dict(zip(INCIDENT, (
            obj["id"], obj["severity"], "NOT_REVIEWED", "", "", "", "",
        ))))
    require(len(incident_ids) == incidents and len(set(historic_ids)) == historical
            and all(type(s) is str and bool(s) for s in historic_ids),
            "missing distinct historical inaccessible source identities")
    blocked_rows = [dict(zip(BLOCKED, (sid, True, "", "", "", "")))
                    for sid in historic_ids]
    return {
        "action_review.csv": action_rows,
        "scoped_source_review.csv": source_rows,
        "open_safety_exceptions.csv": incident_rows,
        "historical_source_access_hold.csv": blocked_rows,
    }


def make_packet(report, *, expected=EXPECTED):
    rows = audit_report(report, expected=expected)
    files = {
        filename: csv_table(TABLES[filename], rows[filename])
        for filename in TABLES
    }
    files["original_evidence.json"] = (
        json.dumps(report, sort_keys=True, ensure_ascii=False,
                   indent=2, allow_nan=False) + "\n").encode("utf-8")
    manifest = {
        "schema": "r54-private-action-review-packet-v1", "issue": 136,
        "release_state": "HOLD", "may_publish": False,
        "qualified_safety_clearance": False, "independent_QD_approval": False,
        "human_source_links_verified": False, "claim_accuracy_verified": False,
        "machine_only": PRESENTATION,
        "parent_R53_report_sha256": report["fingerprint_sha256"],
        "files": {
            name: {"bytes": len(content), "sha256": sha_bytes(content),
                   "rows": len(rows[name]) if name in rows else None}
            for name, content in sorted(files.items())
        },
        "limitations": (
            "The CSV is only an editable presentation of unverified evidence. "
            "The complete original Unicode, repeated citation occurrences and "
            "contributor-specific source reading depth remain in original_evidence.json. "
            "No independent human or qualified hazard review is recorded or authorized. "
            "An altered worksheet has no attestation or reviewer identity authority."),
    }
    manifest["fingerprint_sha256"] = digest(manifest)
    files["manifest.json"] = (
        json.dumps(manifest, ensure_ascii=False, sort_keys=True,
                   indent=2, allow_nan=False) + "\n").encode("utf-8")
    return files


def verify_packet(report, files, *, expected=EXPECTED):
    require(type(files) is dict and
            all(type(k) is str and type(v) is bytes for k, v in files.items()),
            "private file packet invalid")
    canonical_files = make_packet(report, expected=expected)
    require(set(files) == set(canonical_files) and
            all(files[k] == canonical_files[k] for k in canonical_files),
            "private work-order packet changed, truncated or misrepresented")
    return True


def module(name, filename):
    path = Path(__file__).with_name(filename)
    require(path.is_file() and not path.is_symlink(), "missing gate: " + filename)
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec and spec.loader, "cannot load gate: " + filename)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def original_report(root):
    r53 = module("r54_original_r53", "r53_qualitative_source_scope_gate.py")
    build = module("r54_build", "build.py")
    r13 = module("r54_r13", "high_consequence_claim_triage.py")
    r50 = module("r54_r50", "safety_exception_custody_gate.py")
    lib = build.Library(root / "preparedness")
    doc = root / "preparedness" / "docs" / "r48"
    md = doc / "SAFETY-EXCEPTION-REGISTER-2026-11-01.md"
    require(md.is_file() and not md.is_symlink(), "historical safety record missing")
    candidates = r50._json(doc / "SAFETY-CANDIDATES-2026-11-01.json", root)
    safety = r50.audit(lib, md.read_text(encoding="utf-8"), candidates)
    return r53.audit(lib, r13.build_triage(lib), safety)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true",
                        help="machine-only counts; no files written")
    parser.add_argument("--write-private", action="store_true",
                        help="create an exclusive private directory under preparedness/build")
    args = parser.parse_args(argv)
    try:
        report = original_report(ROOT.parent)
        files = make_packet(report)
        verify_packet(report, files)
        out = {"schema": "r54-private-action-review-packet-v1",
               "release_state": "HOLD", "may_publish": False,
               "report_sha256": report["fingerprint_sha256"],
               "file_sha256": {k: sha_bytes(v) for k, v in sorted(files.items())},
               "counts": report["counts"], "wrote_private_files": False}
        if args.write_private:
            build_dir = ROOT / "build"
            require(build_dir.is_dir() and not build_dir.is_symlink() and
                    build_dir.resolve() == build_dir.absolute(),
                    "private build directory missing or linked")
            folder = build_dir / ("r54-private-review-HOLD-" +
                                  report["fingerprint_sha256"][:12])
            folder.mkdir(mode=0o700, exist_ok=False)
            for name, content in sorted(files.items()):
                path = folder / name
                with path.open("xb") as f:
                    f.write(content)
            out["wrote_private_files"] = True
            out["private_location"] = str(folder.relative_to(ROOT.parent))
        print(json.dumps(out, ensure_ascii=False, sort_keys=True))
        return 0
    except (PacketHold, OSError, ValueError, KeyError, TypeError,
            ImportError, json.JSONDecodeError) as exc:
        print("R54 PRIVATE REVIEW PACKET HOLD: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
