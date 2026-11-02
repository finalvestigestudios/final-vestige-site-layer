#!/usr/bin/env python3
"""R59 PRIVATE HOLD: citation-occurrence CSV review and untrusted note quarantine.

The CSV is a human-readable PRESENTATION, not original evidence. Exact, full
Unicode source/citation evidence remains in R58's independently revalidated
JSON. Returned annotations are UNTRUSTED and cannot advance review state.
No network, CMS, navigation, or public file writes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "r59-private-citation-occurrence-review-workbook-v1"
INTAKE_SCHEMA = "r59-untrusted-citation-review-note-quarantine-v1"
DEFAULT = (35, 1, 1959, 367, 43, 30, 779, 15, 25)
IMMUTABLE = (
    "citation_work_order_id_sha256",
    "article_slug", "contributor_source_id", "source_origin",
    "citation_ordinal_within_source", "original_html_codepoint_offset",
    "frozen_article_html_sha256", "original_source_record_sha256",
    "original_visible_context_sha256", "source_url_display",
    "original_visible_context_PREVIEW_ONLY",
    "original_source_notes_PREVIEW_ONLY",
    "same_url_variants_review_required", "fallback_scope_review_required",
    "same_article_source_action_ids_NOT_CLAIM_SUPPORT",
    "human_source_retrieval_state", "human_claim_support_state",
    "qualified_hazard_safety_state",
)
ANNOTATIONS = (
    "reviewer_untrusted_notes", "reviewer_untrusted_source_excerpt",
    "reviewer_untrusted_source_version", "reviewer_untrusted_external_reference",
)
HEADERS = IMMUTABLE + ANNOTATIONS
HOLD_FLAGS = (
    "may_publish", "qualified_safety_clearance", "independent_QD_approval",
    "human_source_links_verified", "claim_accuracy_verified",
    "human_source_reviews_completed", "source_claim_accuracy_verified",
)


class WorkbookHold(ValueError):
    """Original evidence or untrusted reviewer input violates private HOLD."""


def need(ok, why):
    if not ok:
        raise WorkbookHold(why)


def load_gate():
    path = Path(__file__).with_name("r58_exact_citation_occurrence_docket.py")
    need(path.is_file() and not path.is_symlink(),
         "R58 exact original citation gate missing")
    spec = importlib.util.spec_from_file_location("r59_original_r58", path)
    need(spec is not None and spec.loader is not None,
         "R58 citation gate not loadable")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    return gate


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def display(value, limit):
    """Safe, explicitly truncated *display only*; exact original is JSON."""
    if not isinstance(value, str):
        value = json.dumps(value, sort_keys=True, ensure_ascii=False,
                           allow_nan=False)
    text = value.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = "".join(c if ord(c) >= 32 and c not in "\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069"
                   else " " for c in text)
    if len(text) > limit:
        text = text[:limit] + " [PREVIEW TRUNCATED; SEE ORIGINAL EVIDENCE JSON]"
    # CSV quotation does NOT prevent spreadsheet formula evaluation.
    if text.lstrip().startswith(("=", "+", "-", "@")):
        text = "'" + text
    return text


def original_rows(bridge, docket, *, expected=DEFAULT):
    gate = load_gate()
    gate.verify_docket(bridge, docket, expected=expected)
    need(docket.get("schema") == gate.SCHEMA and
         docket.get("release_state") == "HOLD" and
         docket.get("machine_only") is True and
         all(docket.get(f) is False for f in HOLD_FLAGS),
         "R58 docket escaped strict machine-only HOLD")
    tasks = docket.get("individual_original_citation_occurrence_review_queue")
    need(type(tasks) is list and len(tasks) == expected[2],
         "citation occurrence census missing")
    rows, seen = [], set()
    for item in tasks:
        need(type(item) is dict, "missing original citation task")
        ident = item["exact_original_token_identity"]
        source = item["original_unabridged_contributor_source_record"]
        key = item["citation_occurrence_work_order_id_sha256"]
        need(type(key) is str and re.fullmatch(r"[a-f0-9]{64}", key) and
             key not in seen, "duplicate or invalid citation task identity")
        seen.add(key)
        related = item[
            "related_action_work_order_ids_same_article_source_ONLY_NOT_CLAIM_SUPPORT"]
        need(type(related) is list and all(type(x) is str for x in related),
             "action associations are not original lists")
        values = (
            key, ident["slug"], ident["source_id"], ident["source_origin"],
            str(ident["citation_ordinal_within_article_source"]),
            str(ident["token_offset_codepoints_in_original_html"]),
            ident["frozen_article_html_sha256"],
            ident["original_source_record_sha256"],
            ident["original_visible_citation_context_sha256"],
            display(source["url"], 600),
            display(item["original_unabridged_visible_context"], 280),
            display(source.get("notes", ""), 230),
            str(item["same_url_variants_human_review_required"]).upper(),
            str(item["base_fallback_human_scope_review_required"]).upper(),
            display(";".join(related), 160),
            item["human_source_retrieval_state"],
            item["human_claim_support_state"],
            item["qualified_hazard_safety_state"],
        )
        need(all(type(x) is str for x in values),
             "invalid original review presentation cell")
        rows.append(dict(zip(HEADERS, values + ("",) * len(ANNOTATIONS))))
    need(len(rows) == expected[2] and len(seen) == expected[2],
         "original repeated citation occurrences lost")
    return rows


def csv_bytes(rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerow(HEADERS)
    for item in rows:
        need(type(item) is dict and set(item) == set(HEADERS),
             "invalid review worksheet column census")
        writer.writerow([item[key] for key in HEADERS])
    return stream.getvalue().encode("utf-8")


def make_packet(bridge, docket, *, expected=DEFAULT):
    rows = original_rows(bridge, docket, expected=expected)
    files = {
        "citation_occurrences_UNREVIEWED.csv": csv_bytes(rows),
        "original_complete_R58_evidence.json": (
            json.dumps(docket, sort_keys=True, ensure_ascii=False,
                       indent=2, allow_nan=False) + "\n").encode("utf-8"),
    }
    manifest = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "machine_only": True, "parent_R58_docket_sha256":
            docket["fingerprint_sha256"],
        "original_work_orders": len(rows),
        "immutable_columns": list(IMMUTABLE),
        "untrusted_annotation_columns": list(ANNOTATIONS),
        "files": {name: {"sha256": sha_bytes(data), "bytes": len(data)}
                  for name, data in sorted(files.items())},
        "limitations": (
            "CSV entries are PREVIEWS only; complete original citation context "
            "and contributor reading depth are in the evidence JSON. Returned "
            "notes remain unsigned, UNTRUSTED, and NOT_REVIEWED. No link, claim, "
            "medical/emergency advice, QD status or publication is approved."),
        **{f: False for f in HOLD_FLAGS},
    }
    manifest["fingerprint_sha256"] = digest(manifest)
    files["manifest.json"] = (json.dumps(
        manifest, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return files


def verify_packet(bridge, docket, files, *, expected=DEFAULT):
    expected_files = make_packet(bridge, docket, expected=expected)
    need(type(files) is dict and set(files) == set(expected_files) and
         all(type(files[k]) is bytes and files[k] == expected_files[k]
             for k in expected_files),
         "private CSV, unabridged source evidence or manifest modified")
    return True


def untrusted_note(value):
    need(type(value) is str and len(value) <= 4000,
         "untrusted annotation exceeds 4,000 Unicode codepoints")
    need(not any(ord(c) < 32 or ord(c) == 127 or
                 c in "\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069"
                 for c in value), "annotation contains control or bidi characters")
    need(not value.lstrip().startswith(("=", "+", "-", "@")),
         "potential spreadsheet formula in returned annotation")
    return value


def quarantine_return(bridge, docket, returned_csv, *, expected=DEFAULT):
    """Accept annotation fields ONLY; original evidence and safety states frozen.

    This creates *untrusted notes*, never a human review result or approval.
    """
    need(type(returned_csv) is bytes and len(returned_csv) <= 16_000_000,
         "returned private worksheet missing or too large")
    try:
        text = returned_csv.decode("utf-8", errors="strict")
        need("\x00" not in text and not text.startswith("\ufeff"),
             "returned worksheet contains NUL or modified UTF-8 header")
        parsed = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    except (UnicodeDecodeError, csv.Error) as error:
        raise WorkbookHold("returned worksheet malformed: " + str(error)) from error
    frozen = original_rows(bridge, docket, expected=expected)
    need(len(parsed) == len(frozen) + 1 and parsed[0] == list(HEADERS),
         "returned worksheet changed headers or citation task census")
    annotations = []
    for idx, (cells, source) in enumerate(zip(parsed[1:], frozen), 1):
        need(len(cells) == len(HEADERS),
             "returned review row has changed column count")
        row = dict(zip(HEADERS, cells))
        need(all(row[k] == source[k] for k in IMMUTABLE),
             "returned worksheet altered original citation/source identity at row %s" % idx)
        notes = {k: untrusted_note(row[k]) for k in ANNOTATIONS}
        if any(notes.values()):
            annotations.append({
                "citation_work_order_id_sha256":
                    source["citation_work_order_id_sha256"],
                "original_row_ordinal": idx,
                "untrusted_reviewer_annotations": notes,
                "review_verdict": "UNTRUSTED_NOT_REVIEWED",
                "qualified_safety_clearance": False,
                "independent_QD_approval": False,
            })
    report = {
        "schema": INTAKE_SCHEMA, "issue": 136,
        "release_state": "HOLD", "machine_only": True,
        "parent_R58_docket_sha256": docket["fingerprint_sha256"],
        "original_work_orders": len(frozen),
        "untrusted_annotated_rows": len(annotations),
        "annotations_NOT_VERIFIED": annotations,
        "raw_returned_csv_sha256": sha_bytes(returned_csv),
        "limitations": (
            "This is unsigned untrusted text, not reviewer identity, evidence "
            "that a URL was checked, claim support, safety clearance, independent "
            "QD review or publishing approval. Review originals separately."),
        **{f: False for f in HOLD_FLAGS},
    }
    report["fingerprint_sha256"] = digest(report)
    return report


def upstream():
    """Re-run the exact original R53/R25/R56/R57/R58 custody chain."""
    gate = load_gate()
    path = Path(__file__).with_name("r57_global_citation_action_bridge.py")
    need(path.is_file() and not path.is_symlink(), "R57 bridge missing")
    spec = importlib.util.spec_from_file_location("r59_original_r57", path)
    r57 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r57)
    r54 = r57.module("r54_action_review_export.py")
    r56 = r57.module("r56_unreviewed_action_source_crosswalk.py")
    build = r57.module("build.py")
    r25 = r57.module("citation_fallback_review_gate.py")
    lib = build.Library(ROOT)
    original = r54.original_report(ROOT.parent)
    action = r56.crosswalk(original)
    r56.verify_crosswalk(original, action)
    cited = r25.audit(lib)
    bridge = r57.bridge(lib, cited, action)
    r57.verify_bridge(lib, cited, action, bridge)
    docket = gate.create_docket(bridge)
    gate.verify_docket(bridge, docket)
    return bridge, docket


def write_private(files, fingerprint):
    root = ROOT / "build"
    need(root.is_dir() and not root.is_symlink() and
         root.resolve() == root.absolute(),
         "ignored, unlinked private build directory required")
    folder = root / ("r59-unreviewed-HOLD-" + fingerprint[:20])
    folder.mkdir(mode=0o700, exist_ok=False)
    need(folder.resolve().parent == root.resolve(),
         "private packet path escaped ignored build folder")
    for name, payload in sorted(files.items()):
        need(name in ("citation_occurrences_UNREVIEWED.csv",
                      "original_complete_R58_evidence.json", "manifest.json",
                      "returned_notes_UNTRUSTED.json"), "unexpected private file")
        with (folder / name).open("xb") as stream:
            stream.write(payload)
    return str(folder.relative_to(ROOT.parent))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--write-private", action="store_true")
    parser.add_argument("--returned-csv", type=Path,
                        help="read an annotated CSV, quarantine notes only")
    args = parser.parse_args(argv)
    try:
        bridge, docket = upstream()
        files = make_packet(bridge, docket)
        verify_packet(bridge, docket, files)
        count = 0
        if args.returned_csv is not None:
            target = args.returned_csv
            need(target.is_file() and not target.is_symlink() and
                 stat.S_ISREG(target.stat().st_mode) and
                 target.stat().st_size <= 16_000_000,
                 "returned worksheet unavailable or is not a small regular file")
            report = quarantine_return(bridge, docket, target.read_bytes())
            count = report["untrusted_annotated_rows"]
            files["returned_notes_UNTRUSTED.json"] = (json.dumps(
                report, sort_keys=True, ensure_ascii=False, indent=2,
                allow_nan=False) + "\n").encode("utf-8")
        summary = {
            "schema": SCHEMA, "release_state": "HOLD",
            "may_publish": False, "original_citation_work_orders":
                docket["counts"]["exact_citation_occurrence_work_orders"],
            "parent_R58_docket_sha256": docket["fingerprint_sha256"],
            "untrusted_annotated_rows": count, "wrote_private_files": False,
        }
        if args.write_private:
            summary["private_location"] = write_private(
                files, docket["fingerprint_sha256"])
            summary["wrote_private_files"] = True
        print(json.dumps(summary, sort_keys=True, ensure_ascii=False))
        return 0
    except (WorkbookHold, ValueError, OSError, KeyError, TypeError,
            ImportError, UnicodeError) as error:
        print("R59 PRIVATE HOLD: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
