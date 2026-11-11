#!/usr/bin/env python3
"""Offline integrity-only review receipt checker. No editorial, rights or release authority."""
import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

SOURCE = "https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/"
IDS = ("board", "chronology")
FIELDS = {"record_id", "source_url", "reviewer", "review_date", "evidence_file", "sha256"}


def inspect(manifest: dict, evidence_root: Path, as_of: date) -> dict:
    errors = []
    if not isinstance(manifest, dict) or set(manifest) != {"version", "records"} or manifest.get("version") != 1 or not isinstance(manifest.get("records"), list):
        return {"result": "FAIL", "errors": ["invalid manifest schema"], "release_authorized": False, "editorial_verified": False, "media_rights_cleared": False}
    records = manifest["records"]
    if len(records) != 2:
        errors.append("expected exactly two record receipts")
    ids = set()
    paths = set()
    for idx, item in enumerate(records):
        label = f"record[{idx}]"
        if not isinstance(item, dict) or set(item) != FIELDS:
            errors.append(label + ": unexpected or missing fields"); continue
        rid = item["record_id"]
        if not isinstance(rid, str) or rid not in IDS or rid in ids:
            errors.append(label + ": duplicate or unsupported record id"); continue
        ids.add(rid)
        if item["source_url"] != SOURCE:
            errors.append(label + ": noncanonical primary source")
        if not isinstance(item["reviewer"], str) or not (1 <= len(item["reviewer"].strip()) <= 120):
            errors.append(label + ": reviewer metadata invalid")
        try:
            review_date = date.fromisoformat(item["review_date"])
            if review_date.isoformat() != item["review_date"] or review_date > as_of:
                raise ValueError()
        except (ValueError, TypeError):
            errors.append(label + ": invalid or future review date")
        name = item["evidence_file"]
        if not isinstance(name, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,127}", name) or name in paths:
            errors.append(label + ": duplicate or unsafe evidence filename"); continue
        paths.add(name)
        requested = evidence_root / name
        if requested.is_symlink() or not requested.is_file():
            errors.append(label + ": missing or symlinked evidence file"); continue
        if requested.stat().st_size > 4_000_000:
            errors.append(label + ": evidence exceeds 4MB"); continue
        expected = item["sha256"]
        if not isinstance(expected, str) or re.fullmatch(r"[a-f0-9]{64}", expected) is None:
            errors.append(label + ": invalid digest"); continue
        actual = hashlib.sha256(requested.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(label + ": SHA-256 mismatch")
    if ids != set(IDS):
        errors.append("board and chronology must have distinct receipts")
    return {"result": "INTEGRITY_ONLY_PASS" if not errors else "FAIL", "errors": errors,
            "release_authorized": False, "editorial_verified": False, "media_rights_cleared": False,
            "source_independence": "SHARED_NASA_REPORT", "as_of": as_of.isoformat()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("evidence_dir", type=Path)
    parser.add_argument("--as-of", required=True, type=date.fromisoformat)
    args = parser.parse_args()
    try:
        output = inspect(json.loads(args.manifest.read_text(encoding="utf-8")), args.evidence_dir, args.as_of)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        output = {"result": "FAIL", "errors": [str(exc)], "release_authorized": False, "editorial_verified": False, "media_rights_cleared": False}
    print(json.dumps(output, sort_keys=True, indent=2))
    raise SystemExit(0 if output["result"] == "INTEGRITY_ONLY_PASS" else 1)

if __name__ == "__main__":
    main()
