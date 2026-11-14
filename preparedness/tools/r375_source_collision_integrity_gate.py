"""R375 fail-closed, read-only source-identity crosswalk gate for Preparedness #136.

Confirms relationships between R374's nine-ref Git-object manifest and the
original source reading-scope crosswalk. No publication authorization is issued.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

SHA = re.compile(r"^[0-9a-f]{40}$")
REPO = "finalvestigestudios/final-vestige-site-layer"
SOURCE_FIELDS = ("url", "publisher", "kind", "verified_on", "human_link_check", "supports", "notes")
R374_ORIGINAL_BLOBS = {"objects": "5e7d9a8972872c82b4bc46ac13aab18883d8149a",
                       "sources": "24b49f0a423119c2f612455f021669709a3f22b5"}
PINNED = {"records": 280, "ids": 203, "repeated": 46, "divergent": 5, "aliases": 17, "object_conflicts": 9}


def stable_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                  separators=(",", ":")).encode("utf-8")).hexdigest()


def source_payload(v: dict) -> dict:
    return {k: v.get(k) for k in SOURCE_FIELDS}


def check_crosswalk(objects: object, sources: object, *, expected_digest: str | None = None) -> dict:
    issues: list[str] = []
    if not isinstance(objects, dict) or not isinstance(sources, dict):
        return {"status": "INVALID_HARD_HOLD", "issues": ["manifest types invalid"],
                "publication_approved": False, "qualified_safety_approved": False}
    for label, item in (("object", objects), ("source", sources)):
        if item.get("schema_version") != 1 or item.get("repository") != REPO:
            issues.append(f"{label} identity mismatch")
        if item.get("release_state") != "DRAFT_HARD_HOLD":
            issues.append(f"{label} release hold missing")
        for key in ("approval", "approved", "publish", "published", "qd_pass", "release_ready", "live"):
            if item.get(key) not in (None, False):
                issues.append(f"{label} release approval asserted: {key}")
    pins = objects.get("branch_pins")
    if not isinstance(pins, list) or len(pins) != 9:
        pins = []
        issues.append("nine branch pins required")
    branches = {p.get("branch"): p.get("sha") for p in pins if isinstance(p, dict)}
    if len(branches) != 9 or any(not isinstance(k, str) or not SHA.fullmatch(str(v)) for k, v in branches.items()):
        issues.append("branch pin identities invalid")
    if objects.get("conflict_count") != PINNED["object_conflicts"]:
        issues.append("original object conflicts changed")
    object_variants = {}
    for o in objects.get("objects", []) if isinstance(objects.get("objects"), list) else []:
        if not isinstance(o, dict):
            issues.append("malformed object entry")
            continue
        path = o.get("path")
        if not isinstance(path, str) or not path.startswith("preparedness/") or ".." in Path(path).parts:
            issues.append("unsafe object path")
            continue
        if o.get("selected_sha") is not None:
            issues.append("unreviewed Git version selected")
        for v in o.get("variants", []):
            if not isinstance(v, dict):
                issues.append("malformed object variant")
                continue
            key = (v.get("branch"), path)
            if key in object_variants:
                issues.append("duplicate Git object branch/path")
            object_variants[key] = v.get("sha")
            if v.get("branch") not in branches or not SHA.fullmatch(str(v.get("sha", ""))):
                issues.append("invalid object branch or SHA")
    groups = sources.get("source_id_variants")
    if not isinstance(groups, list):
        groups = []
        issues.append("source groups not a list")
    by_url: dict[str, set[str]] = defaultdict(set)
    seen_ids = set()
    repeated = divergent = total = human_checked = 0
    review_queue = []
    all_variants = []
    for g in groups:
        if not isinstance(g, dict) or not isinstance(g.get("id"), str) or not g["id"]:
            issues.append("invalid source ID group")
            continue
        sid = g["id"]
        if sid in seen_ids:
            issues.append("duplicate source ID group")
        seen_ids.add(sid)
        variants = g.get("variants")
        if not isinstance(variants, list) or not variants:
            issues.append(f"missing source variants: {sid}")
            continue
        repeated += int(len(variants) > 1)
        group_payload = []
        seen_keys = set()
        for v in variants:
            if not isinstance(v, dict):
                issues.append(f"invalid record: {sid}")
                continue
            total += 1
            if v.get("id") != sid:
                issues.append(f"source identity drift: {sid}")
            branch, path = v.get("branch"), v.get("fragment")
            if (branch, path) in seen_keys:
                issues.append(f"duplicated source branch/path: {sid}")
            seen_keys.add((branch, path))
            if branch not in branches or not isinstance(path, str) or not re.fullmatch(r"preparedness/sources/fragments/[a-z0-9-]+\.json", path):
                issues.append(f"source provenance invalid: {sid}")
            if v.get("source_blob") != object_variants.get((branch, path)):
                issues.append(f"source Git blob custody mismatch: {sid}")
            url = v.get("url")
            if not isinstance(url, str):
                issues.append(f"source URL missing: {sid}")
            else:
                try:
                    parts = urlsplit(url)
                    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password or parts.fragment:
                        issues.append(f"unsafe or changed source URL: {sid}")
                except ValueError:
                    issues.append(f"malformed source URL: {sid}")
                by_url[url].add(sid)
            if not isinstance(v.get("supports"), str) or not v["supports"].strip():
                issues.append(f"original reading scope lost: {sid}")
            if not isinstance(v.get("human_link_check"), bool):
                issues.append(f"human link status malformed: {sid}")
            human_checked += int(v.get("human_link_check") is True)
            payload = source_payload(v)
            group_payload.append(payload)
            all_variants.append({"id": sid, "branch": branch, "fragment": path,
                                 "source_blob": v.get("source_blob"), "payload": payload})
        changed = [k for k in SOURCE_FIELDS if len({stable_digest(p.get(k)) for p in group_payload}) > 1]
        if changed:
            divergent += 1
            review_queue.append({"id": sid, "different_fields": changed,
                                 "branches": sorted(str(v.get("branch")) for v in variants),
                                 "variant_digests": {str(v.get("branch")): stable_digest(source_payload(v)) for v in variants}})
    aliases = [{"url": url, "ids": sorted(ids)} for url, ids in by_url.items() if len(ids) > 1]
    aliases.sort(key=lambda x: x["url"])
    review_queue.sort(key=lambda x: x["id"])
    docket = sources.get("shared_url_docket")
    if not isinstance(docket, list) or len(docket) != len(aliases):
        issues.append("shared-URL docket coverage drift")
    else:
        expected = {(a["url"], tuple(a["ids"])) for a in aliases}
        actual = {(a.get("url"), tuple(sorted(a.get("ids", [])))) for a in docket if isinstance(a, dict)}
        if expected != actual or any(a.get("review_required") is not True for a in docket if isinstance(a, dict)):
            issues.append("shared URL identities or human review hold removed")
    counts = {"records": total, "ids": len(seen_ids), "repeated": repeated,
              "divergent": divergent, "aliases": len(aliases),
              "object_conflicts": objects.get("conflict_count")}
    for field in ("records", "ids", "repeated", "divergent", "aliases"):
        if counts[field] != PINNED[field]:
            issues.append(f"authenticated {field} baseline changed")
    if sources.get("record_occurrences") != total or sources.get("distinct_source_ids") != len(seen_ids):
        issues.append("source count assertions changed")
    if human_checked:
        issues.append("human link checks changed; require independent verification")
    if sources.get("original_fragment_count") != 7:
        issues.append("original source fragment count changed")
    if objects.get("article_count") != 35:
        issues.append("original article coverage changed")
    record_digest = stable_digest(sorted(all_variants, key=lambda v: (v["id"], str(v["branch"]))))
    if expected_digest is not None and record_digest != expected_digest:
        issues.append("original source record evidence fingerprint drift")
    return {"status": "INVALID_HARD_HOLD" if issues else "SOURCE_REVIEW_HARD_HOLD",
            "issues": sorted(set(issues)), "counts": counts, "human_link_checked": human_checked,
            "source_records_digest": record_digest,
            "divergent_source_review_queue": review_queue, "shared_url_review_queue": aliases,
            "publication_approved": False, "qualified_safety_approved": False}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("objects", type=Path)
    ap.add_argument("sources", type=Path)
    args = ap.parse_args()
    try:
        orig_data, source_data = args.objects.read_bytes(), args.sources.read_bytes()
        report = check_crosswalk(json.loads(orig_data), json.loads(source_data))
        for label, raw in (("objects", orig_data), ("sources", source_data)):
            actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if actual != R374_ORIGINAL_BLOBS[label]:
                report["status"] = "INVALID_HARD_HOLD"
                report["issues"].append("original R374 authenticated Git blob drift: " + label)
    except (OSError, ValueError, TypeError) as exc:
        report = {"status": "INVALID_HARD_HOLD", "issues": [type(exc).__name__],
                  "publication_approved": False, "qualified_safety_approved": False}
    print(json.dumps(report, sort_keys=True, indent=2))
    return 2  # always hard hold; even a clean custody match cannot grant publication


if __name__ == "__main__":
    raise SystemExit(main())
