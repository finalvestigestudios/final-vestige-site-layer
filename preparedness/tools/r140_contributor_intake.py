#!/usr/bin/env python3
"""R140: exact-blob, fail-closed intake review for seven Preparedness contributors.

This tool is NOT a safety audit, source verification, approval or publication gate.
It reads article bodies without modifying them. It never accepts review signoffs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EXPECTED = frozenset({"start", "shelter", "food", "health", "histfood", "histhome", "histfield"})
CITE = re.compile(r"\{\{cite:([^}]+)\}\}")


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def prose_words(html: str) -> int:
    """R140 comparison metric only; not a readability or safety assessment."""
    body = re.sub(r"<[^>]*>", " ", html)
    body = CITE.sub(" ", body)
    return len(body.split())


def inspect_bytes(data: bytes) -> dict:
    html = data.decode("utf-8", errors="strict")
    ids = CITE.findall(html)
    return {"sha": git_blob(data), "words": prose_words(html), "citations": len(ids), "source_ids": sorted(set(ids))}


def validate_manifest(obj: dict) -> list[dict]:
    if not isinstance(obj, dict) or set(obj) != {"schema", "rc_sha", "branch_heads", "drifts", "source_note"}:
        raise ValueError("unexpected manifest fields")
    if obj["schema"] != "R140-INTAKE-1" or not SHA.fullmatch(obj["rc_sha"]):
        raise ValueError("schema or candidate SHA invalid")
    heads = obj["branch_heads"]
    if not isinstance(heads, dict) or set(heads) != EXPECTED or not all(isinstance(v, str) and SHA.fullmatch(v) for v in heads.values()):
        raise ValueError("seven exact branch heads required")
    if len(set(heads.values())) != 7:
        raise ValueError("duplicate branch head")
    if not isinstance(obj["source_note"], str) or "human" not in obj["source_note"].lower():
        raise ValueError("source-review hold missing")
    if not isinstance(obj["drifts"], list) or not obj["drifts"]:
        raise ValueError("missing article drifts")
    seen = set()
    for rec in obj["drifts"]:
        keys = {"cluster", "slug", "baseline_blob", "contributor_blob", "baseline_words", "contributor_words", "baseline_citations", "contributor_citations", "removed_source_ids", "added_source_ids"}
        if not isinstance(rec, dict) or set(rec) != keys:
            raise ValueError("unexpected drift fields (no approvals permitted)")
        cluster, slug = rec["cluster"], rec["slug"]
        if cluster not in EXPECTED or not isinstance(slug, str) or not SLUG.fullmatch(slug):
            raise ValueError("invalid contributor or path-safe slug")
        if slug in seen:
            raise ValueError("duplicated article slug across contributors")
        seen.add(slug)
        for key in ("baseline_blob", "contributor_blob"):
            if not isinstance(rec[key], str) or not SHA.fullmatch(rec[key]):
                raise ValueError("invalid Git blob identity")
        if rec["baseline_blob"] == rec["contributor_blob"]:
            raise ValueError("unchanged blob in drift evidence")
        for key in ("baseline_words", "contributor_words", "baseline_citations", "contributor_citations"):
            if type(rec[key]) is not int or rec[key] < 0:
                raise ValueError("invalid count")
        for key in ("removed_source_ids", "added_source_ids"):
            val = rec[key]
            if not isinstance(val, list) or not all(isinstance(x, str) and re.fullmatch(r"[a-z0-9-]+", x) for x in val) or len(set(val)) != len(val):
                raise ValueError("invalid source ID set")
        if set(rec["removed_source_ids"]) & set(rec["added_source_ids"]):
            raise ValueError("source identity simultaneously added and removed")
    return sorted(obj["drifts"], key=lambda d: (d["cluster"], d["slug"]))


def issue_class(rec: dict) -> str:
    if rec["contributor_citations"] < rec["baseline_citations"] or rec["contributor_words"] < rec["baseline_words"]:
        return "DEPTH_OR_CITATION_REGRESSION_HOLD"
    if rec["removed_source_ids"] or rec["added_source_ids"]:
        return "CITATION_ID_RETARGET_HOLD"
    return "BLOB_DRIFT_REQUIRES_REVIEW"


def evaluate(obj: dict, root: Path) -> dict:
    drifts = validate_manifest(obj)
    out = []
    for rec in drifts:
        relative = f"preparedness/content/articles/{rec['slug']}.body.html"
        target = root / relative
        status = "MISSING_ARTICLE_HOLD"
        observed = None
        if target.is_symlink():
            status = "SYMLINK_ARTICLE_HOLD"
        elif target.is_file():
            try:
                observed = inspect_bytes(target.read_bytes())
            except (UnicodeError, OSError):
                status = "UNREADABLE_ARTICLE_HOLD"
            else:
                if observed["sha"] == rec["baseline_blob"]:
                    status = "BASELINE_BLOB_PRESERVED_NOT_SAFETY_APPROVED"
                elif observed["sha"] == rec["contributor_blob"]:
                    status = "UNREVIEWED_CONTRIBUTOR_REPLACEMENT_HOLD"
                else:
                    status = "UNREVIEWED_THIRD_VERSION_HOLD"
        out.append({"path": relative, "cluster": rec["cluster"], "intake_risk": issue_class(rec), "status": status, "observed": observed})
    preserved = sum(x["status"] == "BASELINE_BLOB_PRESERVED_NOT_SAFETY_APPROVED" for x in out)
    return {"status": "DRAFT_HOLD_NO_PUBLICATION", "rc_sha": obj["rc_sha"], "total_drifted_articles": len(out), "baseline_preserved": preserved, "article_checks": out, "human_source_reviews_required": True, "qd_approved": False, "publish_authorized": False}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--report", type=Path)
    args = ap.parse_args(argv)
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = evaluate(data, args.root)
        payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.report:
            args.report.write_text(payload, encoding="utf-8")
        print(json.dumps({k: result[k] for k in ("status", "total_drifted_articles", "baseline_preserved", "human_source_reviews_required", "publish_authorized")}, sort_keys=True))
        # This is ALWAYS a review-only diagnostic: no green release state.
        return 2 if result["baseline_preserved"] != result["total_drifted_articles"] else 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"R140 INTAKE INVALID / HOLD: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
