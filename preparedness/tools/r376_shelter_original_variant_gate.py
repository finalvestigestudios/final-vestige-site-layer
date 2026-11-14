"""R376 read-only, source-pinned Shelter body/meta loss gate (Issue #136).

This validator cannot approve publication or select an original article version.
It accepts the authenticated R374 Git-object manifest and two original R376
variant dockets; it does not write to the repository or WordPress.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

REPO = "finalvestigestudios/final-vestige-site-layer"
MANIFEST_BLOB = "5e7d9a8972872c82b4bc46ac13aab18883d8149a"
BODY_BLOB = "23ce2e2555a947fb1ce8c610b2c43d9cf788b332"
META_BLOB = "ba73dae3b9b3da465fc3a43d8b40b49bc95dc319"
SLUGS = ("family-communication-plan", "home-fire-escape-plan",
         "outage-heat-cold-generators", "shelter-or-evacuate")
PREFIX = "preparedness/content/articles/"
REQUIRED = {PREFIX + s + "." + t for s in SLUGS for t in ("body.html", "meta.json")}
REQUIRED.add("preparedness/sources/fragments/shelter.json")
SHA = re.compile(r"^[a-f0-9]{40}$")
FORBIDDEN = ("approval", "approved", "publish", "published", "live", "qd_pass", "release_ready",
             "publication_approved", "qualified_safety_approved", "safety_approved",
             "paid_offer_approved", "commercial_approved", "commercial_checkout_approved",
             "approved_source_selection")


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def validate(manifest: object, body: object, meta: object) -> dict:
    issues: list[str] = []
    if not all(isinstance(x, dict) for x in (manifest, body, meta)):
        return {"status": "INVALID_HARD_HOLD", "issues": ["wrong document type"],
                "publication_approved": False, "qualified_safety_approved": False}
    for label, doc in (("manifest", manifest), ("body", body), ("meta", meta)):
        if doc.get("schema_version") != 1 or doc.get("repository") != REPO:
            issues.append(f"{label} schema/repository drift")
        if doc.get("release_state") != "DRAFT_HARD_HOLD":
            issues.append(f"{label} hard hold absent")
        if any(doc.get(x) not in (None, False) for x in FORBIDDEN):
            issues.append(f"{label} attempted release approval")
    if manifest.get("article_count") != 35 or manifest.get("conflict_count") != 9:
        issues.append("original complete article/conflict inventory changed")
    if body.get("source_manifest_git_blob") != MANIFEST_BLOB:
        issues.append("body manifest Git provenance changed")
    if body.get("selected_original") is not None or meta.get("original_selected_version") is not None:
        issues.append("unreviewed original version selected")
    pins = manifest.get("branch_pins")
    if not isinstance(pins, list) or len(pins) != 9:
        pins = []
        issues.append("nine contributor pins missing")
    pinned = {v.get("branch"): v.get("sha") for v in pins if isinstance(v, dict)}
    if len(pinned) != 9 or any(not SHA.fullmatch(str(s)) for s in pinned.values()):
        issues.append("invalid contributor branch pin")
    if meta.get("original_manifest_branch_pins") != pins:
        issues.append("meta contributor provenance drift")
    conflicts = {}
    for obj in manifest.get("objects", []):
        if not isinstance(obj, dict):
            issues.append("invalid manifest object")
            continue
        v = obj.get("variants", [])
        if obj.get("selected_sha") is not None:
            issues.append("original manifest has unapproved selection")
        if len({x.get("sha") for x in v if isinstance(x, dict)}) > 1:
            conflicts[obj.get("path")] = v
    if set(conflicts) != REQUIRED:
        issues.append("nine original conflict paths missing/changed")
    body_docket = body.get("body_conflicts", [])
    meta_docket = meta.get("original_object_conflicts", [])
    if not isinstance(body_docket, list) or not isinstance(meta_docket, list):
        issues.append("invalid docket container")
        body_docket, meta_docket = [], []
    grouped = body_docket + meta_docket
    paths = [g.get("path") for g in grouped if isinstance(g, dict)]
    if len(paths) != 9 or len(set(paths)) != 9 or set(paths) != REQUIRED:
        issues.append("nine docket objects not covered exactly once")
    at_risk = []
    for item in grouped:
        if not isinstance(item, dict):
            issues.append("invalid docket row")
            continue
        path = item.get("path")
        original = conflicts.get(path)
        if original is None:
            issues.append("non-conflict path represented as original fork")
            continue
        originals = item.get("all_original_variant_blobs") if path.endswith(".body.html") else item.get("all_original_variants")
        if originals != original:
            issues.append(f"Git original provenance changed: {path}")
        distinct = {v.get("sha"): v.get("branch") for v in original if isinstance(v, dict)}
        versions = item.get("variants")
        if not isinstance(versions, list) or len(versions) != len(distinct):
            issues.append(f"not all versions preserved: {path}")
            continue
        observed = {(v.get("sha"), v.get("branch")) for v in versions if isinstance(v, dict)}
        if observed != {(sha, branch) for sha, branch in distinct.items()}:
            issues.append(f"original blob/branch variant substituted: {path}")
        if path.endswith(".body.html"):
            if item.get("decision") != "NO_AUTO_SELECT_PENDING_HUMAN_SAFETY_SOURCE_REVIEW":
                issues.append(f"body human-review hold removed: {path}")
            for v in versions:
                if not isinstance(v, dict) or not isinstance(v.get("words"), int) or v["words"] <= 0:
                    issues.append(f"invalid body reading-depth statistic: {path}")
                    continue
                if not isinstance(v.get("unique_citation_ids"), list) or len(set(v["unique_citation_ids"])) != len(v["unique_citation_ids"]):
                    issues.append(f"citation inventory invalid: {path}")
                if v.get("blocks_missing_vs_first", 0) < 0 or v.get("blocks_added_vs_first", 0) < 0:
                    issues.append(f"negative content-loss counts: {path}")
                if v.get("blocks_missing_vs_first", 0) or v.get("removed_citation_ids"):
                    at_risk.append({"path": path, "sha": v.get("sha"),
                                    "removed_blocks": v.get("blocks_missing_vs_first"),
                                    "removed_citations": v.get("removed_citation_ids", [])})
        elif path.endswith(".meta.json"):
            if item.get("decision") != "ORIGINAL_VERSIONS_PRESERVED_HUMAN_REVIEW_REQUIRED":
                issues.append(f"metadata review hold removed: {path}")
            for v in versions:
                if v.get("publish") != "draft" or v.get("safety_state") != "pending":
                    issues.append(f"unsafe source metadata state: {path}")
                if v.get("removed_source_use"):
                    at_risk.append({"path": path, "sha": v.get("sha"),
                                    "removed_source_use": v["removed_source_use"]})
                if not isinstance(v.get("source_use_count"), int) or v["source_use_count"] < 1:
                    issues.append(f"invalid metadata citation support count: {path}")
        else:
            if item.get("decision") != "ORIGINAL_VERSIONS_PRESERVED_HUMAN_REVIEW_REQUIRED":
                issues.append("Shelter source-fragment review hold removed")
    return {"status": "INVALID_HARD_HOLD" if issues else "HUMAN_ADJUDICATION_HARD_HOLD",
            "issues": sorted(set(issues)), "conflicts": len(conflicts),
            "source_reading_depth_or_citation_review": at_risk,
            "publication_approved": False, "qualified_safety_approved": False,
            "paid_offer_approved": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("body", type=Path)
    parser.add_argument("meta", type=Path)
    args = parser.parse_args()
    try:
        raws = [x.read_bytes() for x in (args.manifest, args.body, args.meta)]
        report = validate(*(json.loads(x) for x in raws))
        for label, raw, expected in zip(("manifest", "body", "meta"), raws,
                                        (MANIFEST_BLOB, BODY_BLOB, META_BLOB)):
            if git_blob(raw) != expected:
                report["status"] = "INVALID_HARD_HOLD"
                report["issues"].append(f"{label} original Git blob fingerprint drift")
    except (OSError, ValueError, TypeError) as ex:
        report = {"status": "INVALID_HARD_HOLD", "issues": [type(ex).__name__],
                  "publication_approved": False, "qualified_safety_approved": False}
    print(json.dumps(report, sort_keys=True, indent=2))
    return 2  # success in custody never grants QD, commerce or publication approval


if __name__ == "__main__":
    raise SystemExit(main())
