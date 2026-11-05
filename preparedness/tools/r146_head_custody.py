#!/usr/bin/env python3
"""R146: current-HEAD, working-tree, and original-blob custody gate.

Complements R145's *historical* Git chain verification. R145 validates the
immutable R144 snapshot, but does not establish that a later HEAD still
contains the original locked evidence. This check fails closed on drift.
No results from this tool approve emergency advice or authorize publication.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

R145_HEAD = "cdc12532be2e5aed3addba914110a620bae583cc"
R133_LOCK_BLOB = "3eead06268a9a69eeb3130dcdcc8588bd95e980c"
LOCK_FILE = "preparedness/docs/r133/locked_files.json"
ADDITIONS = frozenset({
    "preparedness/tools/r146_head_custody.py",
    "preparedness/tests/test_r146_head_custody.py",
    "preparedness/docs/r146/README.md",
})
SHA = re.compile(r"[0-9a-f]{40}\Z")
STATUS = "DRAFT_HOLD"


class Hold(ValueError):
    """Evidence mismatch: must not claim validation success."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Hold(reason)


def command(root: Path, *args: str, binary: bool = False):
    p = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
    if p.returncode:
        raise Hold(f"Git unavailable or rejected {args[:3]}: "
                   + p.stderr.decode("utf-8", "replace")[:240])
    return p.stdout if binary else p.stdout.decode("utf-8", "strict").strip()


def parse_name_status(payload: bytes) -> dict[str, str]:
    """Parse NUL-separated git diff --name-status -z; reject rename/copy."""
    require(isinstance(payload, bytes), "diff must be bytes")
    fields = payload.split(b"\0")
    require(fields[-1:] == [b""], "truncated Git diff")
    fields.pop()
    require(len(fields) % 2 == 0, "unexpected Git diff field count")
    changes = {}
    for i in range(0, len(fields), 2):
        state = fields[i].decode("ascii", "strict")
        path = fields[i + 1].decode("utf-8", "strict")
        require(state == "A", f"non-additive change {state}: {path}")
        require(path not in changes, f"duplicate diff entry {path}")
        require(path == path.strip() and not any(
            c in path for c in ("\r", "\n", "\\", "\x00")),
            f"unsafe path {path!r}")
        changes[path] = state
    return changes


def check_review_diff(diff: bytes, expected=ADDITIONS) -> int:
    changes = parse_name_status(diff)
    require(set(changes) == set(expected),
            f"R145-to-current change-set mismatch; missing={sorted(set(expected)-set(changes))}; "
            f"extra={sorted(set(changes)-set(expected))}")
    return len(changes)


def parse_tree(payload: bytes) -> dict[str, tuple[str, str, str]]:
    """Parse raw ls-tree records, including mode to deny symlinks/gitlinks."""
    require(isinstance(payload, bytes), "tree must be bytes")
    fields = payload.split(b"\0")
    require(fields[-1:] == [b""], "truncated Git tree")
    fields.pop()
    result = {}
    for item in fields:
        head, sep, raw_path = item.partition(b"\t")
        require(bool(sep), "invalid ls-tree record")
        pieces = head.decode("ascii", "strict").split(" ")
        require(len(pieces) == 3, "invalid ls-tree header")
        mode, kind, sha = pieces
        path = raw_path.decode("utf-8", "strict")
        require(path not in result, f"duplicate Git path {path}")
        require(SHA.fullmatch(sha) is not None, "invalid Git object ID")
        require(mode in ("100644", "100755") and kind == "blob",
                f"symlink, gitlink or unusual Git mode: {path}")
        result[path] = (mode, kind, sha)
    return result


def parse_lock(raw: bytes) -> dict[str, str]:
    try:
        lock = json.loads(raw.decode("utf-8", "strict"))
    except (UnicodeError, ValueError) as exc:
        raise Hold(f"invalid frozen R133 lockfile: {exc}") from exc
    require(isinstance(lock, dict), "lock must be object")
    require(lock.get("source_release_candidate")
            == "ddb3528ba6494dada1fa1c3a142ce746e3a67706",
            "historical release candidate pin changed")
    require(lock.get("expected_citation_occurrences") == 2000,
            "historical citation expectation changed")
    for key in ("may_publish", "qd_pass", "medical_safety_verified",
                "merchant_offer_verified"):
        require(lock.get(key) is False, f"forged approval state {key}")
    items = lock.get("files")
    require(isinstance(items, list) and len(items) == 80,
            "80 original evidence files required")
    expected = {}
    bodies, metas = set(), set()
    for item in items:
        require(isinstance(item, dict), "lock file entry not object")
        path, sha = item.get("path"), item.get("blob_sha")
        require(isinstance(path, str) and path.startswith("preparedness/")
                and ".." not in Path(path).parts and "\\" not in path,
                f"invalid evidence path {path!r}")
        require(isinstance(sha, str) and SHA.fullmatch(sha) is not None,
                f"invalid evidence SHA for {path}")
        require(path not in expected, f"duplicate evidence path {path}")
        expected[path] = sha
        if path.startswith("preparedness/content/articles/"):
            if path.endswith(".body.html"):
                bodies.add(path.removesuffix(".body.html"))
            if path.endswith(".meta.json"):
                metas.add(path.removesuffix(".meta.json"))
    require(len(bodies) == len(metas) == 35 and bodies == metas,
            "missing/extra original article pair or duplicate route stem")
    return expected


def check_current_tree(
        tree_bytes: bytes, locked: dict[str, str], additions=ADDITIONS
) -> dict:
    tree = parse_tree(tree_bytes)
    for path, sha in locked.items():
        entry = tree.get(path)
        require(entry is not None, f"original evidence missing at current HEAD: {path}")
        require(entry[2] == sha,
                f"original evidence CHANGED at current HEAD: {path}")
        require(entry[0] == "100644",
                f"original evidence mode CHANGED at current HEAD: {path}")
    for path in additions:
        require(path in tree, f"review file missing at current HEAD: {path}")
        require(tree[path][0] == "100644",
                f"review file must be non-executable regular blob: {path}")
    return {"original_git_blobs_unchanged_at_current_head": len(locked),
            "review_additions_present": len(additions)}


def inspect_checkout(root: Path, expected_head: str, *,
                     base: str = R145_HEAD,
                     expected_lock_sha: str = R133_LOCK_BLOB,
                     additions=ADDITIONS) -> dict:
    """Read only. Test overrides base/lock/additions; CLI always freezes pins."""
    root = root.resolve(strict=True)
    require(SHA.fullmatch(expected_head) is not None, "expected HEAD must be 40-char SHA")
    require(SHA.fullmatch(base) is not None, "base SHA malformed")
    actual_root = Path(command(root, "rev-parse", "--show-toplevel")).resolve()
    require(actual_root == root, "repository root mismatch")
    current = command(root, "rev-parse", "HEAD")
    require(current == expected_head, "branch HEAD moved or wrong commit selected")
    command(root, "merge-base", "--is-ancestor", base, current)
    require(command(root, "rev-parse", f"{base}:{LOCK_FILE}") == expected_lock_sha,
            "frozen R133 lock Git blob mismatch")
    original = command(root, "show", f"{base}:{LOCK_FILE}", binary=True)
    locked = parse_lock(original)
    diff = command(root, "diff", "--name-status", "-z", "--no-renames",
                   base, current, binary=True)
    additions_count = check_review_diff(diff, additions)
    tree = command(root, "ls-tree", "-r", "-z", current, "--",
                   "preparedness/", binary=True)
    evidence = check_current_tree(tree, locked, additions)
    # Both staged and unstaged edits, plus untracked files, invalidate an audit.
    dirty = command(root, "status", "--porcelain=v1", "-z",
                    "--untracked-files=all", "--", binary=True)
    require(dirty == b"", "checkout has uncommitted or untracked changes")
    require(command(root, "rev-parse", "HEAD") == expected_head,
            "HEAD moved during custody check")
    return {
        "status": "CURRENT_HEAD_CUSTODY_PASS_RELEASE_HOLD",
        "checked_head": current,
        "historical_base": base,
        "new_review_files": additions_count,
        **evidence,
        "original_citation_baseline": 2000,
        "release": STATUS,
        "publication_allowed": False,
        "medical_safety_verified": False,
        "independent_qd": "NOT_APPROVED",
        "paid_offer_verified": False,
    }


def run_native(root: Path, head: str) -> list[dict]:
    """Delegates native checks to R145's temporary-archive runner, never WP."""
    source = root / "preparedness/tools/r145_chain_integrity.py"
    spec = importlib.util.spec_from_file_location("r145_native_isolated", source)
    require(spec is not None and spec.loader is not None,
            "R145 native runner missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_native_snapshot(root, head)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--native", action="store_true")
    args = parser.parse_args(argv)
    result = {
        "schema": "FV-PREP-R146-HEAD-1", "status": "HOLD",
        "release": STATUS, "publication_allowed": False,
        "medical_safety_verified": False, "independent_qd": "NOT_APPROVED",
        "paid_offer_verified": False, "may_merge": False,
    }
    try:
        result.update(inspect_checkout(args.repo, args.expected_head))
        if args.native:
            results = run_native(args.repo.resolve(), args.expected_head)
            result["native_checks"] = results
            require(len(results) == 3 and all(
                item["exit_code"] == 0 for item in results),
                "native validation, build, or 36+ tests did not all pass")
        code = 0
    except (Hold, OSError, UnicodeError, subprocess.SubprocessError,
            TypeError, ImportError) as exc:
        code = 2
        result["status"] = "HOLD"
        result["error"] = str(exc)
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
