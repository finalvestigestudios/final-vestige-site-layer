"""Read-only source-object custody gate for Preparedness Issue #136.

The manifest is a review docket, never a publication authorization. Every
fingerprint is a Git blob SHA; no local writes, branch switches, or network calls.
"""
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")
BODY = re.compile(r"^preparedness/content/articles/([a-z0-9-]+)\.body\.html$")
META = re.compile(r"^preparedness/content/articles/([a-z0-9-]+)\.meta\.json$")
SOURCE = re.compile(r"^preparedness/sources/fragments/[a-z0-9-]+\.json$")
EXPECTED_ORIGINAL = 7
EXPECTED_SHELTER_FORKS = 2
EXPECTED_ARTICLES = 35
RELEASE_KEYS = ("approval", "approved", "publish", "published", "qd_pass", "release_ready", "live")


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def inspect_manifest(m: dict, root: Path | None = None) -> dict:
    issues = []
    if not isinstance(m, dict) or m.get("schema_version") != 1:
        return {"status": "INVALID_HARD_HOLD", "issues": ["invalid manifest schema"], "checked": 0}
    if m.get("repository") != "finalvestigestudios/final-vestige-site-layer":
        issues.append("repository mismatch")
    if m.get("release_state") != "DRAFT_HARD_HOLD":
        issues.append("release hold missing")
    if any(m.get(key) not in (None, False) for key in RELEASE_KEYS):
        issues.append("release approval asserted")
    pins = m.get("branch_pins", [])
    if not isinstance(pins, list):
        pins = []; issues.append("branch pins not a list")
    names = [p.get("branch") for p in pins if isinstance(p, dict)]
    if len(names) != EXPECTED_ORIGINAL + EXPECTED_SHELTER_FORKS or len(names) != len(set(names)):
        issues.append("expected nine distinct contributor refs")
    if sum(str(n).startswith("claude/prep-") for n in names) != 9:
        issues.append("contributor branch name mismatch")
    if any(not HEX40.fullmatch(str(p.get("sha", ""))) for p in pins if isinstance(p, dict)):
        issues.append("invalid branch pin")
    objects = m.get("objects", [])
    if not isinstance(objects, list):
        objects = []; issues.append("object inventory not a list")
    seen_paths = set(); bodies = set(); metas = set(); fragments = 0; conflicted = 0; checked = 0
    for o in objects:
        if not isinstance(o, dict):
            issues.append("malformed inventory row"); continue
        path = o.get("path", "")
        if not isinstance(path, str) or path in seen_paths or path.startswith("/") or ".." in Path(path).parts:
            issues.append("duplicate or unsafe object path"); continue
        if not (BODY.fullmatch(path) or META.fullmatch(path) or SOURCE.fullmatch(path)):
            issues.append("unexpected inventory path: " + path); continue
        seen_paths.add(path)
        if BODY.fullmatch(path): bodies.add(BODY.fullmatch(path).group(1))
        if META.fullmatch(path): metas.add(META.fullmatch(path).group(1))
        if SOURCE.fullmatch(path): fragments += 1
        variants = o.get("variants", [])
        if not isinstance(variants, list) or not variants:
            issues.append("missing variants: " + path); continue
        vnames = [v.get("branch") for v in variants if isinstance(v, dict)]
        if len(vnames) != len(variants) or len(vnames) != len(set(vnames)) or not set(vnames).issubset(names):
            issues.append("variant branch mismatch: " + path)
        sha_set = set()
        for v in variants:
            sha = v.get("sha", "") if isinstance(v, dict) else ""
            if not HEX40.fullmatch(str(sha)) or not isinstance(v.get("size"), int) or v["size"] <= 0:
                issues.append("invalid Git object identity: " + path)
            sha_set.add(sha)
        is_conflict = len(sha_set) > 1
        conflicted += int(is_conflict)
        if o.get("decision") != ("REVIEW_REQUIRED" if is_conflict else "IDENTICAL_OR_SINGLE"):
            issues.append("variant conflict not held: " + path)
        if o.get("selected_sha") is not None:
            issues.append("unreviewed source auto-selected: " + path)
        if root is not None:
            fp = root / path
            if not fp.is_file():
                issues.append("authentic checkout file unavailable: " + path)
            else:
                current = git_blob_sha(fp.read_bytes()); checked += 1
                if current not in sha_set:
                    issues.append("non-original Git blob: " + path)
    if len(bodies) != EXPECTED_ARTICLES or bodies != metas:
        issues.append(f"article/meta coverage mismatch (bodies={len(bodies)}, metas={len(metas)})")
    if fragments < EXPECTED_ORIGINAL:
        issues.append("original source fragments missing")
    if m.get("article_count") != len(bodies) or m.get("conflict_count") != conflicted:
        issues.append("inventory tallies altered")
    if root is None:
        issues.append("authentic working tree not supplied")
    return {"status": "INVALID_HARD_HOLD" if issues else "CUSTODY_MATCH_HARD_HOLD",
            "issues": sorted(set(issues)), "checked": checked, "article_count": len(bodies),
            "fragment_count": fragments, "conflict_count": conflicted,
            "publication_approved": False, "qualified_safety_approved": False}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--root", type=Path, help="complete authenticated checkout root; read-only")
    args = ap.parse_args()
    try:
        result = inspect_manifest(json.loads(args.manifest.read_text()), args.root)
    except (OSError, ValueError, TypeError) as exc:
        result = {"status": "INVALID_HARD_HOLD", "issues": [type(exc).__name__], "checked": 0}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "CUSTODY_MATCH_HARD_HOLD" else 2


if __name__ == "__main__":
    raise SystemExit(main())
