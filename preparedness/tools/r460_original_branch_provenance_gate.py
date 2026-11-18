#!/usr/bin/env python3
"""Frozen nine-branch source/metadata custody; never a release or advice-safety approval.

Run against a full reviewed checkout, not against synthetic examples:
  python -I preparedness/tools/r460_original_branch_provenance_gate.py --root preparedness
Optional independently rechecked ref JSON: --live-refs /path/to/current-git-refs.json
The checked-in historical source graph is NOT authorization to choose any manuscript fork.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

MANIFEST_BLOB = "3b50fe91423c7dbebe336550ca5fb9256b8bd356"
INTEGRATED_COMMIT = "9b4846d2b2a94f7aeee2689e9b738f94a9eab97a"
STATE = "DRAFT_HARD_HOLD"
BRANCH_IDS = frozenset(("start", "food", "health", "hist-field", "hist-food", "hist-home",
                        "shelter", "shelter-cont", "shelter-follow"))
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SHA = re.compile(r"[a-f0-9]{40}\Z")
MAX_FILE = 5_000_000


class ProvenanceHold(ValueError):
    """Provenance or branch selection could not be authenticated."""


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def reject_duplicates(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ProvenanceHold(f"duplicate JSON property: {k}")
        out[k] = v
    return out


def load_json(raw: bytes):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicates)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ProvenanceHold(f"invalid JSON: {exc}") from exc


def checked_file(root: Path, relative: str) -> bytes:
    if not isinstance(relative, str) or not relative.startswith("preparedness/") or "//" in relative:
        raise ProvenanceHold("untrusted or malformed repository path")
    pieces = Path(relative).parts
    if len(pieces) < 3 or any(p in ("..", ".") for p in pieces):
        raise ProvenanceHold("unsafe relative path")
    path = root.joinpath(*pieces[1:])
    if any(p.is_symlink() for p in (path, *path.parents) if p != path.anchor and p != root.parent):
        raise ProvenanceHold(f"symlink in custody path: {relative}")
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_FILE:
        raise ProvenanceHold(f"missing, empty, oversized or irregular source: {relative}")
    return path.read_bytes()


def checked_sha(value: str) -> bool:
    return isinstance(value, str) and bool(SHA.fullmatch(value))


def validate_graph(manifest: dict) -> dict:
    """Inspect source ownership, not who was right or whether editorial changes are safe."""
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ProvenanceHold("unreviewed provenance manifest schema")
    if any(manifest.get(k) is not False for k in ("qualified_qd_pass", "wordpress_publication_performed",
                                                  "source_claim_support_verified", "paid_conversion_verified")):
        raise ProvenanceHold("unsafe or omitted release/commerce flag")
    if manifest.get("release_state") != STATE or manifest.get("integrated_head") != INTEGRATED_COMMIT:
        raise ProvenanceHold("release status or integrated frozen commit mismatch")
    if (manifest.get("issue"), manifest.get("conversion_issue")) != (136, 820):
        raise ProvenanceHold("wrong owner or commerce-coordination lane")
    refs = manifest.get("branches")
    if not isinstance(refs, dict) or set(refs) != BRANCH_IDS:
        raise ProvenanceHold("exact nine contributor refs required")
    for key, val in refs.items():
        if not isinstance(val, dict) or not val.get("ref", "").startswith("claude/prep-") or not checked_sha(val.get("sha")):
            raise ProvenanceHold(f"invalid contributor ref: {key}")
    if (manifest.get("article_count"), manifest.get("tool_count")) != (35, 6):
        raise ProvenanceHold("original 35-article / six-tool slate changed")
    rows, sources = manifest.get("artifacts"), manifest.get("source_fragments")
    if not isinstance(rows, list) or len(rows) != 83 or not isinstance(sources, list) or len(sources) != 8:
        raise ProvenanceHold("original paired content/fragment source inventory altered")
    seen = set()
    arts, tools, hubs, changed, forks, missing = set(), set(), set(), [], [], []
    for row in rows:
        if not isinstance(row, dict):
            raise ProvenanceHold("bad artifact row")
        path = row.get("path")
        if not isinstance(path, str) or path in seen or not re.fullmatch(
            r"preparedness/content/(articles|tools|hubs)/[a-z0-9-]+\.(body\.html|meta\.json)", path
        ):
            raise ProvenanceHold(f"invalid, duplicate or unexpected content path {path}")
        seen.add(path)
        if not checked_sha(row.get("integrated_blob")):
            raise ProvenanceHold(f"unverified integrated blob: {path}")
        owners = row.get("contributors")
        if not isinstance(owners, dict) or not set(owners).issubset(BRANCH_IDS) or not all(checked_sha(s) for s in owners.values()):
            raise ProvenanceHold(f"invalid original contributor blob map {path}")
        actual_matches = sorted(k for k, s in owners.items() if s == row["integrated_blob"])
        variants = len(set(owners.values()))
        needs_review = variants > 1 or not actual_matches
        if not isinstance(row.get("matches_integrated"), list) or sorted(row["matches_integrated"]) != actual_matches or row.get("distinct_contributor_blobs") != variants:
            raise ProvenanceHold(f"manipulated provenance match/fork count: {path}")
        if row.get("requires_human_disposition") is not needs_review:
            raise ProvenanceHold(f"source disposition silently bypassed: {path}")
        if needs_review:
            changed.append(path)
        if variants > 1:
            forks.append(path)
        if not owners:
            missing.append(path)
        kind, name = path.split("/")[2:4]
        slug = name.rsplit(".", 2)[0]
        if kind == "articles" and path.endswith(".body.html"):
            arts.add(slug)
        elif kind == "tools" and path.endswith(".body.html"):
            tools.add(slug)
        elif kind == "hubs" and path.endswith(".body.html"):
            hubs.add(slug)
    if (len(arts), len(tools), len(hubs)) != (35, 6, 1):
        raise ProvenanceHold("article, tool or extra hub slate collision")
    expected = {f"preparedness/content/{kind}/{slug}.{suffix}" for kind, slugs in
                (("articles", arts), ("tools", tools)) for slug in slugs for suffix in ("body.html", "meta.json")}
    expected |= {f"preparedness/content/hubs/{h}.body.html" for h in hubs}
    if seen != expected:
        raise ProvenanceHold("orphan metadata or missing authored body")
    srcseen = set()
    for row in sources:
        if not isinstance(row, dict):
            raise ProvenanceHold("bad source fragment")
        path = row.get("path")
        if not isinstance(path, str) or path in srcseen or not (
            path == "preparedness/sources/register.json" or re.fullmatch(
                r"preparedness/sources/fragments/[a-z-]+\.json", path
            )
        ):
            raise ProvenanceHold(f"untrusted source fragment {path}")
        srcseen.add(path)
        if not checked_sha(row.get("integrated_blob")):
            raise ProvenanceHold(f"invalid source fragment blob: {path}")
        owners = row.get("contributors")
        if not isinstance(owners, dict) or not set(owners).issubset(BRANCH_IDS) or not all(checked_sha(s) for s in owners.values()):
            raise ProvenanceHold(f"invalid fragment contributors: {path}")
    expected_src = {"preparedness/sources/register.json"} | {
        f"preparedness/sources/fragments/{x}.json" for x in ("start", "food", "health", "shelter", "hist-food", "hist-home", "hist-field")
    }
    if srcseen != expected_src:
        raise ProvenanceHold("seven source fragments or original register changed")
    return {"original_articles": len(arts), "tools": len(tools), "listed_files": len(seen),
            "source_files": len(srcseen), "items_needing_human_disposition": len(changed),
            "variant_files": forks, "files_with_no_original_branch_snapshot": missing,
            "unadjudicated_files": changed, "release_state": STATE, "qualified_qd_pass": False}


def validate_live_refs(manifest: dict, observed: dict | None) -> str:
    if observed is None:
        return "NOT_RECHECKED_IN_CLI"
    if not isinstance(observed, dict) or set(observed) != BRANCH_IDS:
        raise ProvenanceHold("live SHA snapshot missing a contributor")
    for key, source in manifest["branches"].items():
        if observed[key] != source["sha"]:
            raise ProvenanceHold(f"contributor moved; do not auto-rebase: {key}")
    return "RECHECKED_EXACT_REF_SHA"


def verify_checkout(root: Path, manifest_bytes: bytes, observed: dict | None = None) -> dict:
    if blob_sha(manifest_bytes) != MANIFEST_BLOB:
        raise ProvenanceHold("frozen reviewer manifest was modified")
    manifest = load_json(manifest_bytes)
    report = validate_graph(manifest)
    if not root.is_dir() or root.is_symlink():
        raise ProvenanceHold("authentic Preparedness checkout unavailable")
    expected = {row["path"]: row["integrated_blob"] for row in manifest["artifacts"] + manifest["source_fragments"]}
    for p, expected_blob in expected.items():
        if blob_sha(checked_file(root, p)) != expected_blob:
            raise ProvenanceHold(f"source file differs from frozen integrated head: {p}")
    actual = {"preparedness/" + str(p.relative_to(root)).replace("\\", "/") for base in
              (root / "content/articles", root / "content/tools", root / "content/hubs")
              if base.is_dir() and not base.is_symlink() for p in base.iterdir()
              if p.name.endswith((".body.html", ".meta.json"))}
    expected_artifacts = {r["path"] for r in manifest["artifacts"]}
    if actual != expected_artifacts:
        raise ProvenanceHold("missing or unexpected article/tool/hub body and metadata")
    actual_src = {"preparedness/" + str(p.relative_to(root)).replace("\\", "/") for base in
                  (root / "sources/fragments",) if base.is_dir() and not base.is_symlink()
                  for p in base.iterdir() if p.suffix == ".json"}
    expected_src = {r["path"] for r in manifest["source_fragments"] if "/fragments/" in r["path"]}
    if actual_src != expected_src:
        raise ProvenanceHold("unexpected or missing original source fragments")
    articles = {}, {}
    article_numbers, tool_numbers = articles
    urls = set()
    for group, numbers in (("articles", article_numbers), ("tools", tool_numbers)):
        for row in manifest["artifacts"]:
            if not row["path"].startswith(f"preparedness/content/{group}/") or not row["path"].endswith(".meta.json"):
                continue
            meta = load_json(checked_file(root, row["path"]))
            slug = row["path"].split("/")[-1].removesuffix(".meta.json")
            if meta.get("slug") != slug or not isinstance(meta.get("n"), int) or isinstance(meta["n"], bool):
                raise ProvenanceHold("article/tool stable identity mismatched")
            if meta["n"] in numbers:
                raise ProvenanceHold(f"duplicated article/tool number {meta['n']}")
            numbers[meta["n"]] = slug
            if meta.get("status", {}).get("publish") != "draft":
                raise ProvenanceHold(f"publication state changed: {slug}")
            if meta.get("safety_review", {}).get("state") in ("approved", "pass", "passed"):
                raise ProvenanceHold(f"unqualified safety approval introduced: {slug}")
            section = meta.get("section")
            if not isinstance(section, str) or not SLUG.fullmatch(section):
                raise ProvenanceHold(f"invalid section: {slug}")
            url = f"/preparedness/{section}/{slug}/"
            if url in urls:
                raise ProvenanceHold(f"duplicate inferred canonical route {url}")
            urls.add(url)
    if set(article_numbers) != set(range(1, 36)):
        raise ProvenanceHold("35 original article order numbers were replaced")
    if set(tool_numbers) != set(range(101, 107)):
        raise ProvenanceHold("six original tool IDs were replaced")
    report["current_branch_sha_evidence"] = validate_live_refs(manifest, observed)
    report["file_blob_checks"] = len(expected)
    report["local_source_custody"] = "STRUCTURAL_PASS_ONLY"
    report["medical_emergency_food_privacy_review"] = "NOT_APPROVED"
    report["revenue_verified"] = False
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--live-refs", type=Path)
    args = parser.parse_args(argv)
    try:
        root = args.root.absolute()
        mp = root / "integration" / "r460_original_branch_provenance.json"
        if not mp.is_file() or mp.is_symlink():
            raise ProvenanceHold("canonical review manifest missing/linked")
        observed = load_json(args.live_refs.read_bytes()) if args.live_refs else None
        result = verify_checkout(root, mp.read_bytes(), observed)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0  # Source custody only, never publication approval.
    except (ProvenanceHold, OSError, TypeError, KeyError, AttributeError) as exc:
        print(json.dumps({"release_state": STATE, "local_source_custody": "HOLD",
                          "qualified_qd_pass": False, "wordpress_publication_performed": False,
                          "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
