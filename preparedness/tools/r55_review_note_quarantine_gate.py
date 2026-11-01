#!/usr/bin/env python3
"""R55: fail-closed PRIVATE intake for untrusted annotations on R54 review CSVs.

Reviewers may fill ONLY the originally blank human-note columns. All original
research/citation/source rows are compared to a freshly recomputed R54 packet.
Output is a quarantined, unsigned note overlay, NEVER human verification,
qualified safety approval, independent QD approval, or publication authority.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 25_000_000
MAX_NOTE_CHARS = 8192
STATE = "UNTRUSTED_NOTES_PENDING_INDEPENDENT_IDENTITY_AND_SOURCE_REVIEW"
SCHEMA = "r55-untrusted-review-note-quarantine-v1"
FLAGS = ("may_publish", "qualified_safety_clearance", "independent_QD_approval",
         "human_source_links_verified", "claim_accuracy_verified")
ROW_KEYS = {
    "action_review.csv": ("work_order_id_sha256", "article", "block_ordinal"),
    "scoped_source_review.csv": ("work_order_id_sha256", "article",
                                 "block_ordinal", "source_id"),
    "open_safety_exceptions.csv": ("incident_id",),
    "historical_source_access_hold.csv": ("original_source_id",),
}
NOTE_COLUMNS = {
    "action_review.csv": (
        "human_reviewer_name_blank", "human_review_date_blank",
        "human_claim_support_decision_blank",
        "human_qualified_safety_decision_blank",
        "human_exceptions_notes_blank"),
    "scoped_source_review.csv": (
        "human_source_access_date_blank", "human_exact_source_locator_blank",
        "human_claim_support_assessment_blank",
        "human_scope_and_discrepancy_notes_blank"),
    "open_safety_exceptions.csv": (
        "human_domain_reviewer_blank", "human_qualified_decision_blank",
        "human_review_date_blank", "human_notes_blank"),
    "historical_source_access_hold.csv": (
        "human_current_link_check_blank", "human_review_date_blank",
        "human_retrieval_route_blank", "human_excerpt_locator_blank"),
}


class IntakeHold(ValueError):
    """Edited evidence, unsafe notes, malformed packet, or false approval."""


def require(condition, reason):
    if not condition:
        raise IntakeHold(reason)


def load_r54():
    path = Path(__file__).with_name("r54_action_review_export.py")
    require(path.is_file() and not path.is_symlink(), "R54 gate unavailable")
    spec = importlib.util.spec_from_file_location("r55_upstream_r54", path)
    require(spec is not None and spec.loader is not None, "R54 gate cannot load")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_csv(name, content, expected_header):
    require(type(content) is bytes and len(content) <= MAX_FILE_BYTES,
            "unsafe worksheet bytes: " + name)
    try:
        decoded = content.decode("utf-8", errors="strict")
        require(not decoded.startswith("\ufeff"), "worksheet BOM changed: " + name)
        rows = list(csv.reader(io.StringIO(decoded, newline=""), strict=True))
    except (UnicodeError, csv.Error, ValueError) as exc:
        raise IntakeHold("malformed or non-UTF8 worksheet: " + name) from exc
    require(rows and rows[0] == list(expected_header),
            "review schema/header changed: " + name)
    require(all(len(row) == len(expected_header) for row in rows[1:]),
            "worksheet row shape changed: " + name)
    return rows[1:]


def check_note(text):
    require(type(text) is str and len(text) <= MAX_NOTE_CHARS,
            "unsafe reviewer note length")
    for char in text:
        code = ord(char)
        require((code >= 32 or code in (9, 10, 13))
                and code != 127 and code not in range(0x80, 0xA0)
                and code not in range(0x202A, 0x202F)
                and code not in range(0x2066, 0x206A)
                and code not in (0x061C, 0x200E, 0x200F, 0xFEFF),
                "control or direction override in reviewer note")
    first = text.lstrip(" \t\r\n\u00a0\u200b\u2060\ufeff")
    require(not first.startswith(("=", "+", "-", "@")),
            "spreadsheet-executable reviewer note")
    return text


def quarantine(report, edited_files, *, expected=None):
    """Return unsigned notes sidecar; NEVER import annotations as review status.

    Requires original_evidence.json and manifest.json byte-identical to the
    freshly regenerated R54 canonical packet. Checked source/claim columns,
    row identities/order, original duplicate citations and URL variants must
    also remain byte-identical *as parsed CSV cell values*.
    """
    r54 = load_r54()
    if expected is None:
        expected = r54.EXPECTED
    baseline = r54.make_packet(report, expected=expected)
    r54.verify_packet(report, baseline, expected=expected)
    require(type(edited_files) is dict
            and set(edited_files) == set(baseline)
            and all(type(v) is bytes for v in edited_files.values()),
            "review packet missing evidence or contains unexpected files")
    for name in ("original_evidence.json", "manifest.json"):
        require(edited_files[name] == baseline[name],
                "immutable original evidence/manifest changed: " + name)
    notes = {}
    row_counts = {}
    annotated_rows = 0
    annotated_cells = 0
    for name, columns in r54.TABLES.items():
        require(set(NOTE_COLUMNS[name]).issubset(columns)
                and set(ROW_KEYS[name]).issubset(columns),
                "R54 reviewer schema drift: " + name)
        originals = parse_csv(name, baseline[name], columns)
        edited = parse_csv(name, edited_files[name], columns)
        require(len(originals) == len(edited),
                "review worksheet rows dropped or added: " + name)
        row_counts[name] = len(originals)
        seen = set()
        selected = []
        for index, (original, changed) in enumerate(zip(originals, edited), 1):
            orig = dict(zip(columns, original))
            now = dict(zip(columns, changed))
            identity = tuple(orig[k] for k in ROW_KEYS[name])
            require(identity not in seen,
                    "duplicate original row identity: " + name)
            seen.add(identity)
            for col in columns:
                if col in NOTE_COLUMNS[name]:
                    require(orig[col] == "",
                            "R54 human review column unexpectedly populated")
                    check_note(now[col])
                else:
                    require(now[col] == orig[col],
                            "original citation/source/safety evidence changed: "
                            + name + " row " + str(index) + " column " + col)
            additions = {k: now[k] for k in NOTE_COLUMNS[name] if now[k]}
            if additions:
                annotated_rows += 1
                annotated_cells += len(additions)
                selected.append({
                    "original_row_ordinal": index,
                    "original_row_identity": dict(zip(ROW_KEYS[name], identity)),
                    "untrusted_annotations_not_verified_findings": additions,
                })
        notes[name] = selected
    result = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "review_state": STATE, "machine_only": True,
        "original_R53_report_sha256": report["fingerprint_sha256"],
        "original_R54_manifest_sha256": r54.sha_bytes(baseline["manifest.json"]),
        "edited_workbook_sha256": {
            k: r54.sha_bytes(edited_files[k]) for k in sorted(r54.TABLES)
        },
        "original_row_counts": row_counts,
        "rows_with_untrusted_notes": annotated_rows,
        "note_cells_untrusted": annotated_cells,
        "notes_by_original_worksheet": notes,
        "limitations": (
            "An annotation is not verified fact-checking, reviewer identity, "
            "qualified hazard approval, independent QD approval, or authorization "
            "to edit article safety states or publish. Revalidate source passages "
            "with qualified independent reviewers before any release decision."),
        **{flag: False for flag in FLAGS},
    }
    result["fingerprint_sha256"] = r54.digest(result)
    return result


def read_private_packet(folder):
    """Read only an R54 folder directly inside the ignored private build dir."""
    r54 = load_r54()
    build = ROOT / "build"
    path = Path(folder)
    require(build.is_dir() and not build.is_symlink()
            and build.resolve() == build.absolute(),
            "private build folder unavailable or redirected")
    require(path.is_dir() and not path.is_symlink()
            and path.resolve().parent == build.resolve()
            and path.name.startswith("r54-private-review-HOLD-"),
            "R54 reviewer folder must be a direct private build child")
    want = set(r54.TABLES) | {"manifest.json", "original_evidence.json"}
    observed = {entry.name for entry in path.iterdir()}
    require(observed == want, "missing or unexpected private packet files")
    files = {}
    for name in sorted(want):
        f = path / name
        require(f.is_file() and not f.is_symlink()
                and f.stat().st_size <= MAX_FILE_BYTES,
                "unsafe review worksheet path or size")
        files[name] = f.read_bytes()
    return files


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--summary", action="store_true",
                   help="check canonical unedited worksheet; zero real reviews")
    p.add_argument("--private-review-dir",
                   help="only a direct R54 directory within preparedness/build")
    p.add_argument("--write-private", action="store_true",
                   help="write unsigned notes JSON under ignored build only")
    args = p.parse_args(argv)
    try:
        require(not args.write_private or args.private_review_dir,
                "quarantine output requires an explicitly provided R54 folder")
        r54 = load_r54()
        report = r54.original_report(ROOT.parent)
        edited = (read_private_packet(args.private_review_dir)
                  if args.private_review_dir else r54.make_packet(report))
        result = quarantine(report, edited)
        public_summary = {
            "schema": SCHEMA, "release_state": "HOLD", "may_publish": False,
            "review_state": STATE,
            "rows_with_untrusted_notes": result["rows_with_untrusted_notes"],
            "note_cells_untrusted": result["note_cells_untrusted"],
            "fingerprint_sha256": result["fingerprint_sha256"],
            "wrote_private_files": False,
        }
        if args.write_private:
            build = ROOT / "build"
            dest = build / ("r55-quarantine-HOLD-" +
                            result["fingerprint_sha256"][:20])
            require(dest.parent == build and not dest.exists(),
                    "quarantine destination already exists")
            dest.mkdir(mode=0o700, exist_ok=False)
            out = dest / "UNTRUSTED_NOTES_NOT_APPROVAL.json"
            with out.open("x", encoding="utf-8") as handle:
                json.dump(result, handle, ensure_ascii=False, sort_keys=True,
                          indent=2, allow_nan=False)
                handle.write("\n")
            public_summary["wrote_private_files"] = True
            public_summary["private_location"] = str(dest.relative_to(ROOT.parent))
        print(json.dumps(public_summary, ensure_ascii=False, sort_keys=True))
        return 0
    except (IntakeHold, OSError, ValueError, TypeError, KeyError,
            ImportError, csv.Error, UnicodeError) as exc:
        print("R55 QUARANTINE HOLD: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
