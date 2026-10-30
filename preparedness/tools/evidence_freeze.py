#!/usr/bin/env python3
"""Deterministic, read-only Git input freeze and exact-source review fingerprint.

A matching source or article SHA means those repository bytes did not drift;
it is NOT a medical safety check, human source read, QA signoff or publish permit.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


def fingerprint(lib, meta: dict) -> str:
    """SHA-256 of exact original copy plus per-article cited reading scopes.

    Intentionally omits the review metadata itself, so adding a reviewer does
    not alter the digest. Changing the article or any cited claim DOES.
    """
    ids = dict.fromkeys(re.findall(r"\{\{cite:([a-z0-9\-]+)\}\}", meta["_body"]))
    sources = []
    for sid in ids:
        src = lib.source_for(meta, sid)
        group = lib.crosswalk_groups.get(src["url"])
        sources.append({
            "id": sid, "origin": src.get("_origin"),
            "source": {key: value for key, value in src.items() if key != "_origin"},
            "article_source_use": meta.get("source_use", {}).get(sid),
            "crosswalk_review_status": group.get("review_status") if group else None,
            "crosswalk_resolution": group.get("resolution") if group else None,
        })
    payload = {
        "schema_version": 1, "slug": meta["slug"], "title": meta["title"],
        "h1": meta["h1"], "dek": meta["dek"],
        "description": meta["description"], "track": meta["track"],
        "section": meta["section"], "updated": meta["updated"],
        "last_checked": meta["last_checked"], "body": meta["_body"],
        "sources_as_read": sources,
    }
    msg = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def verify(lib, lock_override: dict | None = None) -> list[str]:
    """Fail closed on any untracked raw source or original article input drift."""
    errors: list[str] = []
    root = lib.root
    source_files = lib.crosswalk.get("source_files", [])
    recorded_sources = {r["path"]: r for r in source_files}
    if len(recorded_sources) != len(source_files):
        errors.append("freeze: duplicate source-file inventory row")
    source_paths = {"preparedness/sources/register.json": "base"}
    for p in sorted((root / "sources" / "fragments").glob("*.json")):
        source_paths[f"preparedness/sources/fragments/{p.name}"] = p.stem
    if set(source_paths) != set(recorded_sources):
        errors.append("freeze: source file inventory added, removed or stale")
    for name, origin in sorted(source_paths.items()):
        row = recorded_sources.get(name)
        if row is None:
            continue
        if row.get("origin") != origin:
            errors.append(f"freeze: wrong source origin: {name}")
        local = root.parent / name
        if not local.is_file():
            errors.append(f"freeze: source file missing: {name}")
            continue
        if git_blob_sha(local) != row.get("git_blob_sha"):
            errors.append(f"freeze: raw source bytes changed: {name}")
        try:
            count = len(json.loads(local.read_text(encoding="utf-8"))["sources"])
        except (OSError, ValueError, KeyError, TypeError):
            errors.append(f"freeze: invalid source file: {name}")
            continue
        if count != row.get("count"):
            errors.append(f"freeze: raw source row count changed: {name}")

    lock_path = root / "sources" / "article-evidence-lock.json"
    if lock_override is not None:
        lock = lock_override
    else:
        if not lock_path.is_file():
            return errors + ["freeze: missing article evidence lock"]
        try:
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return errors + ["freeze: malformed article evidence lock"]
    if lock.get("schema_version") != 1:
        errors.append("freeze: unknown article evidence lock schema")
    rows = lock.get("records", [])
    if not isinstance(rows, list):
        return errors + ["freeze: evidence lock records must be an array"]
    recorded = {}
    for row in rows:
        slug = row.get("slug")
        if slug in recorded:
            errors.append(f"freeze: duplicate locked article: {slug}")
        recorded[slug] = row
    if set(recorded) != set(lib.articles):
        errors.append("freeze: article inventory changed from 35-article baseline")
    if lock.get("longform_article_count") != sum(m.get("kind") != "tool" for m in lib.articles.values()):
        errors.append("freeze: article count changed")
    if lock.get("local_tool_count") != sum(m.get("kind") == "tool" for m in lib.articles.values()):
        errors.append("freeze: tool count changed")
    known_paths = set()
    for slug, meta in sorted(lib.articles.items()):
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            errors.append(f"freeze: invalid slug path: {slug!r}")
            continue
        row = recorded.get(slug)
        if row is None:
            continue
        if row.get("origin") != lib.article_origins.get(slug):
            errors.append(f"freeze: article origin changed for {slug}")
        directory = "tools" if meta.get("kind") == "tool" else "articles"
        for field, suffix in (("body", "body.html"), ("metadata", "meta.json")):
            expected = f"preparedness/content/{directory}/{slug}.{suffix}"
            known_paths.add(expected)
            locked = row.get(field) or {}
            if locked.get("path") != expected:
                errors.append(f"freeze: article path changed or escaped for {slug} {field}")
            local = root.parent / expected
            if not local.is_file():
                errors.append(f"freeze: article file missing: {expected}")
                continue
            if git_blob_sha(local) != locked.get("git_blob_sha"):
                errors.append(f"freeze: article {field} bytes changed for {slug}")
            if local.stat().st_size != locked.get("bytes"):
                errors.append(f"freeze: article {field} length changed for {slug}")
    actual_paths = set()
    for directory in ("articles", "tools"):
        for f in (root / "content" / directory).glob("*"):
            if f.is_file() and f.name.endswith((".body.html", ".meta.json")):
                actual_paths.add(f"preparedness/content/{directory}/{f.name}")
    if actual_paths != known_paths:
        errors.append("freeze: untracked or unpaired body/metadata inputs")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fingerprint", metavar="SLUG")
    args = parser.parse_args(argv)
    sys.path.insert(0, str(ROOT / "tools"))
    import build
    lib = build.Library()
    issues = verify(lib)
    result = {"unaltered_input_snapshots": not bool(issues), "errors": issues,
              "human_safety_or_link_qa_proven": False}
    if args.fingerprint:
        if args.fingerprint not in lib.articles:
            print("Unknown article slug", file=sys.stderr)
            return 2
        result["slug"] = args.fingerprint
        result["sha256_for_review_only"] = fingerprint(lib, lib.articles[args.fingerprint])
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
