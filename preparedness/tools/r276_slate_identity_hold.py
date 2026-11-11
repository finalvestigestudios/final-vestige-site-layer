#!/usr/bin/env python3
"""R276 all-slate byte-identity custody. Read-only verification is NOT safety approval."""
from __future__ import annotations
import hashlib
import json
from collections import Counter
from pathlib import Path

HOLD = "DRAFT_HARD_HOLD"
INVALID = "INVALID_HARD_HOLD"
SCHEMA = "fv-r276-all-slate-identity-v1"
REF = "df96120007ceb33290764392a5900e356e04deac"
MANIFEST = "audits/r276_all_slate_identity_UNAPPROVED.json"
# Set from GitHub's exact committed manifest blob, never from an untrusted manifest.
MANIFEST_BLOB = "b8c7c6df0dca62b04b01abc5671b7083ad9cb61e"
ROLES = {"article_body": 35, "article_meta": 35, "tool_body": 6,
         "tool_meta": 6, "hub_body": 1, "source_origin": 8,
         "crosswalk": 1, "docket": 1, "source_gate": 1,
         "docket_gate": 1, "export_gate": 1}
ORIGINS = frozenset(("sources/register.json", "sources/fragments/start.json",
    "sources/fragments/shelter.json", "sources/fragments/food.json",
    "sources/fragments/health.json", "sources/fragments/hist-field.json",
    "sources/fragments/hist-food.json", "sources/fragments/hist-home.json"))
EXTRA = {"hub_body": "content/hubs/start-here.body.html",
    "crosswalk": "sources/crosswalk.json",
    "docket": "audits/r273_shared_source_review_docket_UNAPPROVED.json",
    "source_gate": "tools/r272_crosswalk_snapshot_hold.py",
    "docket_gate": "tools/r273_source_review_docket_hold.py",
    "export_gate": "tools/r220_full_slate_draft_custody.py"}


def git_blob(data: bytes) -> str:
    if type(data) is not bytes:
        raise ValueError("source bytes required")
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def strict_json(data: bytes):
    def unique(pairs):
        d = {}
        for k, v in pairs:
            if k in d:
                raise ValueError("duplicate JSON key: " + k)
            d[k] = v
        return d
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique,
        parse_constant=lambda s: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def inspect(manifest: dict, read):
    if (manifest.get("schema") != SCHEMA or manifest.get("state") != HOLD
        or manifest.get("snapshot_ref") != REF):
        raise ValueError("manifest schema, state or snapshot drift")
    if (manifest.get("source_review") != {"shared_url_groups": 32,
         "duplicate_id_groups": 15, "held_occurrences": 3}):
        raise ValueError("source review holds modified")
    for key in ("independent_qd_pass", "publication_authorized", "medical_safety_verified",
                "privacy_approved", "merchant_offer_approved", "may_merge"):
        if manifest.get(key, "MISSING") is not False:
            raise ValueError("unapproved release flag: " + key)
    entries = manifest.get("entries")
    if not isinstance(entries, list) or len(entries) != sum(ROLES.values()):
        raise ValueError("missing/extra draft or source inventory")
    if Counter(e.get("role") for e in entries if isinstance(e, dict)) != ROLES:
        raise ValueError("article/tool/source counts changed")
    seen, article_parts, tool_parts, meta_slugs, meta_numbers = set(), {}, {}, set(), set()
    for e in entries:
        if set(e) != {"path", "sha", "size", "role"}:
            raise ValueError("manifest entry fields modified")
        path, role, sha, nbytes = e["path"], e["role"], e["sha"], e["size"]
        if (not isinstance(path, str) or path.startswith("/") or ".." in Path(path).parts
            or "\\" in path or path != Path(path).as_posix() or path in seen):
            raise ValueError("unsafe or duplicate file path")
        seen.add(path)
        if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError("invalid Git blob identity")
        if type(nbytes) is not int or nbytes <= 0:
            raise ValueError("invalid source byte size")
        if role in ("article_body", "article_meta", "tool_body", "tool_meta"):
            folder = "articles" if role.startswith("article_") else "tools"
            suffix = ".body.html" if role.endswith("_body") else ".meta.json"
            prefix = "content/" + folder + "/"
            if not path.startswith(prefix) or not path.endswith(suffix):
                raise ValueError("source file outside expected article/tool directory")
            slug = path[len(prefix):-len(suffix)]
            if not slug or not all(c.islower() or c.isdigit() or c == "-" for c in slug):
                raise ValueError("invalid canonical slug")
            bucket = article_parts if folder == "articles" else tool_parts
            bucket.setdefault(slug, set()).add(role.rsplit("_", 1)[-1])
        elif role == "source_origin":
            if path not in ORIGINS:
                raise ValueError("unexpected source origin")
        elif path != EXTRA.get(role):
            raise ValueError("unexpected source/custody gate path")
        data = read(path)
        if len(data) != nbytes or git_blob(data) != sha:
            raise ValueError("original content not byte-identical: " + path)
        if role.endswith("_meta"):
            meta = strict_json(data)
            if meta.get("slug") != slug or meta.get("status", {}).get("publish") != "draft":
                raise ValueError("slug or draft publication state changed")
            if meta["slug"] in meta_slugs or meta.get("n") in meta_numbers:
                raise ValueError("duplicate canonical slug or content number")
            meta_slugs.add(meta["slug"])
            meta_numbers.add(meta["n"])
    if any(parts != {"body", "meta"} for parts in (*article_parts.values(), *tool_parts.values())):
        raise ValueError("orphaned body or metadata")
    if len(article_parts) != 35 or len(tool_parts) != 6 or len(meta_slugs) != 41:
        raise ValueError("article/tool reading-depth roster changed")
    crosswalk = strict_json(read(EXTRA["crosswalk"]))
    origins = crosswalk.get("article_origins", {})
    if (set(origins) != set(article_parts) | {"water-planner"}
        or "water-planner" not in tool_parts or len(origins) != 36):
        raise ValueError("frozen crosswalk article-to-source-origin roster drift")
    docket = strict_json(read(EXTRA["docket"]))
    if (docket.get("state") != HOLD or docket.get("source_rows") != 244
        or docket.get("review_alias_groups") != 32
        or docket.get("duplicate_source_id_groups") != 15):
        raise ValueError("unadjudicated source docket unavailable")
    return {"state": HOLD, "original_byte_parity": True,
            "article_count": 35, "tool_count": 6, "source_origins": 8,
            "independent_qd_pass": False, "publication_authorized": False}


def audit(root: Path, read=None):
    root = Path(root)
    read = read or (lambda rel: (root / rel).read_bytes())
    result = {"state": INVALID, "original_byte_parity": False,
              "independent_qd_pass": False, "publication_authorized": False,
              "errors": []}
    try:
        raw = read(MANIFEST)
        if git_blob(raw) != MANIFEST_BLOB:
            raise ValueError("committed manifest identity mismatch")
        result.update(inspect(strict_json(raw), read))
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError, IndexError) as exc:
        result["errors"].append(str(exc))
    return result

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, type=Path)
    a = audit(p.parse_args().root)
    print(json.dumps(a, indent=2, sort_keys=True))
    raise SystemExit(2 if a["state"] == HOLD else 3)
