#!/usr/bin/env python3
"""R461 read-only, fail-closed original-fork adjudication docket. NEVER approves publication.

- Imports R460's immutable nine-origin 35-article SHA crosswalk.
- Emits exactly the disputed body/metadata/source-path identities for human review.
- Re-checks the completed docket against the original Git snapshot, and refuses
  retargeted witnesses, stale candidates, unlisted forks, missing notes, false QD.
- Does not choose editorial versions, inspect medical accuracy, update CMS or
  allow a PASS. CLI always returns 2 (hard hold), including for intact dockets.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

_ROOT = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("r460_origin", _ROOT / "r460_origin_branch_blob_crosswalk.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("R460 custody tool missing")
r460 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r460)

STATE = "DRAFT_HARD_HOLD"
SNAPSHOT_BLOB_SHA = "056d14cd97d29b843d52912383c237b9122e73ef"
SCHEMA = "r461-review-docket-v1"
VALID_STATES = {"PENDING_HUMAN_REVIEW", "EXAMINED_NOT_CLEARED"}
MAX_FILE = 2_000_000

class ReviewHold(ValueError):
    """A missing or invalid human-review record, never QD clearance."""


def _digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\x00" + data).hexdigest()


def _read_json(path, *, pin=None):
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_FILE:
        raise ReviewHold(f"missing, linked, or oversized read-only input {path}")
    raw = path.read_bytes()
    if pin and _git_blob(raw) != pin:
        raise ReviewHold("original Git snapshot bytes differ from authenticated blob SHA")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=r460._no_duplicates)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReviewHold("invalid or non-UTF8 review evidence") from exc


def build_docket(snapshot):
    """Generate exact, UNAPPROVED review rows from the authenticated R460 inventory."""
    try:
        analysis = r460.analyze(snapshot)
    except (TypeError, ValueError, KeyError) as exc:
        raise ReviewHold(f"R460 source custody invalid: {exc}") from exc
    origin_records = snapshot["origins"]
    candidate = snapshot["candidate"]
    article_rows = []
    for row in analysis["article_rows"]:
        if not row["review_required"]:
            continue
        slug = row["slug"]
        ancestor = {k: origin_records[k]["articles"][slug]
                    for k in row["origins"]}
        article_rows.append({
            "slug": slug,
            "candidate_body": candidate["articles"][slug]["body"],
            "candidate_meta": candidate["articles"][slug]["meta"],
            "witnesses": {k: {"body": ancestor[k]["body"], "meta": ancestor[k]["meta"]}
                          for k in sorted(ancestor)},
            "body_matches": row["candidate_body_matches"],
            "meta_matches": row["candidate_meta_matches"],
            "body_variants": row["body_variants"],
            "meta_variants": row["meta_variants"],
            "review_status": "PENDING_HUMAN_REVIEW",
            "finding_note": "",
            "claim_to_source_verified": False,
            "qualified_safety_approval": False,
        })
    source_rows = []
    for row in analysis["source_rows"]:
        if row["path"] not in analysis["source_review_paths"]:
            continue
        p = row["path"]
        source_rows.append({
            "path": p,
            "candidate_blob": candidate["sources"][p],
            "witnesses": {k: origin_records[k]["sources"][p]
                          for k in sorted(origin_records) if p in origin_records[k]["sources"]},
            "candidate_matches": row["candidate_matches"],
            "review_status": "PENDING_HUMAN_REVIEW",
            "finding_note": "",
            "source_scope_verified": False,
        })
    return {
        "schema": SCHEMA, "repository": r460.REPO,
        "snapshot_git_blob_sha": SNAPSHOT_BLOB_SHA,
        "snapshot_semantic_sha256": _digest(snapshot),
        "candidate_commit": candidate["sha"],
        "full_35_article_inventory_sha256": _digest(candidate["articles"]),
        "source_path_inventory_sha256": _digest(candidate["sources"]),
        "release_state": STATE, "qualified_qd_pass": False,
        "publication_authorized": False,
        "verified_purchasable_preparedness_sku": False,
        "social_asset_attribution_verified": False,
        "verified_realized_net_revenue": False,
        "article_review_rows": article_rows,
        "source_review_rows": source_rows,
    }


def verify_docket(snapshot, docket):
    """Adjudication *integrity* only; no human claim-support or safety approval."""
    expected = build_docket(snapshot)
    if not isinstance(docket, dict) or set(docket) != set(expected):
        raise ReviewHold("review document missing required custody/release keys")
    for key in expected:
        if key in {"article_review_rows", "source_review_rows"}:
            continue
        if docket[key] != expected[key] or type(docket[key]) is not type(expected[key]):
            raise ReviewHold(f"incorrect or unapproved docket field {key}")
    for key, ident in (("article_review_rows", "slug"), ("source_review_rows", "path")):
        rows = docket[key]
        targets = {row[ident]: row for row in expected[key]}
        if not isinstance(rows, list) or len(rows) != len(targets):
            raise ReviewHold(f"lost or duplicated {key}")
        found = set()
        for row in rows:
            if not isinstance(row, dict) or ident not in row or row[ident] in found:
                raise ReviewHold(f"duplicate or malformed {key}")
            name = row[ident]
            found.add(name)
            if name not in targets or set(row) != set(targets[name]):
                raise ReviewHold(f"unwitnessed review identity {name!r}")
            baseline = targets[name]
            for field, val in baseline.items():
                if field in {"finding_note", "review_status"}:
                    continue
                if row[field] != val or type(row[field]) is not type(val):
                    raise ReviewHold(f"original evidence, hold, or human safety flag altered: {name}/{field}")
            if row["review_status"] not in VALID_STATES:
                raise ReviewHold(f"unapproved review state: {name}")
            note = row["finding_note"]
            if not isinstance(note, str) or len(note) > 4000 or "\x00" in note:
                raise ReviewHold(f"unsafe or oversized note: {name}")
            if row["review_status"] == "EXAMINED_NOT_CLEARED" and not note.strip():
                raise ReviewHold(f"human review cannot be recorded without findings: {name}")
        if found != set(targets):
            raise ReviewHold(f"orphaned {key} review rows")
    return {
        "state": "REVIEW_CUSTODY_INTACT_HARD_HOLD",
        "release_state": STATE,
        "qualified_qd_pass": False,
        "publication_authorized": False,
        "article_review_count": len(expected["article_review_rows"]),
        "source_review_count": len(expected["source_review_rows"]),
        "examined_article_count": sum(r["review_status"] == "EXAMINED_NOT_CLEARED" for r in docket["article_review_rows"]),
        "examined_source_count": sum(r["review_status"] == "EXAMINED_NOT_CLEARED" for r in docket["source_review_rows"]),
        "claim_support_and_safety_review": "NOT CLEARED",
        "native_build_and_exports": "NOT EVALUATED BY R461",
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshot", required=True, type=Path)
    p.add_argument("--docket", type=Path, help="verify existing reviewer docket; otherwise emit draft to stdout")
    args = p.parse_args(argv)
    try:
        snapshot = _read_json(args.snapshot, pin=SNAPSHOT_BLOB_SHA)
        if args.docket:
            result = verify_docket(snapshot, _read_json(args.docket))
        else:
            result = build_docket(snapshot)
        print(json.dumps(result, sort_keys=True, indent=2))
    except (ReviewHold, ValueError, TypeError, OSError, KeyError) as exc:
        print(json.dumps({"state": "PROVENANCE_OR_REVIEW_HARD_HOLD", "qualified_qd_pass": False,
                          "publication_authorized": False, "error": str(exc)}))
    return 2  # HOLD is unconditional even if all structural checks pass.


if __name__ == "__main__":
    raise SystemExit(main())
