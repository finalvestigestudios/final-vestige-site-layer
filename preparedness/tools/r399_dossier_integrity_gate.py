#!/usr/bin/env python3
"""Read-only R399 original-evidence dossier parity. Always DRAFT/HARD_HOLD, even on integrity PASS."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

R397_BLOB = "86d22a1d504c93db7689b914e2202a7845b648e2"
HOLD = "DRAFT_HARD_HOLD"


def blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def literal(text: object) -> str:
    return "\n".join("    " + line for line in str(text).replace("\r\n", "\n").split("\n"))


def inspect(d: dict, markdown: str, raw: bytes, *, pin: str = R397_BLOB) -> dict:
    failures = []
    def require(ok: bool, marker: str) -> None:
        if not ok:
            failures.append(marker)
    require(blob(raw) == pin, "docket_git_blob_mismatch")
    try:
        require(json.loads(raw) == d, "docket_decoding_mismatch")
    except (ValueError, TypeError):
        require(False, "docket_decoding_mismatch")
    require(d.get("publication_approved") is False and d.get("qualified_safety_approved") is False and d.get("merchant_offer_verified") is False, "release_state_changed")
    sources, forks = d.get("source_evidence_disputes", []), d.get("original_fork_disputes", [])
    aliases, cross = d.get("shared_exact_url_review_groups", []), d.get("all_original_source_id_crosswalk", [])
    require(len(sources) == 5 and len(forks) == 9 and len(aliases) == 17, "case_counts_changed")
    require(len(cross) == 203 and sum(len(x.get("variants", [])) for x in cross) == 280, "source_inventory_changed")
    require(len(d.get("original_articles", [])) == 35, "article_inventory_changed")
    require("No source or manuscript selected" in markdown and "HARD HOLD" in markdown, "hold_banner_missing")
    require(pin in markdown, "original_blob_marker_missing")
    require(markdown.count("#### Original source candidate ") == sum(len(x.get("variants", [])) for x in sources), "source_candidate_count")
    require(markdown.count("| `claude/prep-shelter-") >= 9, "fork_table_rows_missing")
    for s in sources:
        sid = s.get("source_id")
        require(markdown.count("### " + str(sid) + "\n") == 1, "source_heading:" + str(sid))
        require(s.get("selected_record") is None and s.get("decision") == "HUMAN_REVIEW_REQUIRED", "source_auto_selected:" + str(sid))
        for v in s.get("variants", []):
            for key in ("branch", "source_blob", "fragment", "publisher", "kind", "url", "verified_on", "human_link_check", "supports_exact", "reading_scope_notes_exact"):
                require(key in v and literal(v.get(key)) in markdown, "source_field_missing:" + str(sid) + ":" + key)
            require(v.get("human_link_check") is False, "false_human_link_check:" + str(sid))
    for f in forks:
        path = f.get("path")
        require(markdown.count("### " + str(path) + "\n") == 1, "fork_heading:" + str(path))
        require(f.get("selected_sha") is None and f.get("decision") == "HUMAN_REVIEW_REQUIRED", "fork_auto_selected:" + str(path))
        require(len(f.get("variants", [])) == 3, "fork_variants:" + str(path))
        for v in f.get("variants", []):
            row = "| `" + str(v.get("branch")) + "` | `" + str(v.get("git_blob_sha")) + "` | " + str(v.get("byte_length")) + " |"
            require(row in markdown, "fork_provenance_missing:" + str(path))
    require("qualified" in markdown.lower() and "privacy" in markdown.lower(), "qualified_review_not_visible")
    return {"integrity": "FAIL" if failures else "PASS", "release": HOLD,
            "source_cases": len(sources), "fork_cases": len(forks), "failures": sorted(set(failures))}


def main(argv=None) -> int:
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--docket", type=Path, required=True)
    a.add_argument("--dossier", type=Path, required=True)
    v = a.parse_args(argv)
    try:
        raw = v.docket.read_bytes()
        result = inspect(json.loads(raw), v.dossier.read_text(encoding="utf-8"), raw)
    except (OSError, TypeError, ValueError, KeyError) as exc:
        result = {"integrity": "FAIL", "release": HOLD, "failures": ["input_error:" + type(exc).__name__]}
    print(json.dumps(result, sort_keys=True))
    return 2  # Never QD PASS; even complete parity is an unresolved human-review hold.


if __name__ == "__main__":
    raise SystemExit(main())
