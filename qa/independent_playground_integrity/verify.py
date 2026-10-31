#!/usr/bin/env python3
"""Offline, fail-closed integrity gate for an unpublished FV local WordPress Playground kit.

No network access, WordPress changes, plugin installation, or browser activity.
A caller must independently obtain the trusted SHA-256 of the OFFICIAL theme ZIP.
Passing is *not* a WordPress.com staging, security, licensing or release approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

SHA = re.compile(r"[0-9a-f]{64}\Z")
HEAD = re.compile(r"[0-9a-f]{40}\Z")
PIN = re.compile(r"@wp-playground/cli@(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[A-Za-z0-9.-]+)?\Z")


class Hold(Exception):
    pass


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def verify(stage_dir: Path, official_theme_zip: Path, trusted_theme_sha256: str, exact_head: str):
    if not SHA.fullmatch(trusted_theme_sha256):
        raise Hold("Trusted out-of-band Assembler ZIP SHA-256 is REQUIRED")
    if not HEAD.fullmatch(exact_head):
        raise Hold("Exact 40-character Git commit SHA is REQUIRED")
    stage_dir = stage_dir.resolve(strict=True)
    theme_bytes = official_theme_zip.read_bytes()
    if sha256(theme_bytes) != trusted_theme_sha256:
        raise Hold("Assembler ZIP differs from independently trusted digest")

    receipt = json.loads((stage_dir / "STAGING_PREP_RECEIPT.json").read_text())
    if receipt.get("exact_git_head") != exact_head or receipt.get("release") != "HOLD":
        raise Hold("Stage provenance or release HOLD status differs")
    if receipt.get("assembler_zip_sha256") != trusted_theme_sha256:
        raise Hold("Stage receipt is not bound to trusted Assembler ZIP")
    if receipt.get("wordpress_instance") != "NOT_STARTED":
        raise Hold("Offline admission requires an unstarted stage")

    # Compare every prepared theme file against the trusted ZIP, not just its title.
    with zipfile.ZipFile(official_theme_zip) as z:
        expected = {}
        for item in z.infolist():
            if item.is_dir():
                continue
            path = item.filename
            if not path.startswith("assembler/") or "\\" in path or ".." in Path(path).parts:
                raise Hold("Unsafe or unexpected theme archive path")
            rel = path[len("assembler/"):]
            if not rel or rel in expected:
                raise Hold("Duplicate/empty theme archive path")
            expected[rel] = z.read(item)
    theme_mount = stage_dir / "mounts" / "assembler"
    actual_files = {p.relative_to(theme_mount).as_posix(): p for p in theme_mount.rglob("*") if p.is_file()}
    if set(actual_files) != set(expected):
        raise Hold("Mounted theme file set differs from trusted ZIP")
    for rel, data in expected.items():
        p = actual_files[rel]
        if p.is_symlink() or not p.resolve().is_relative_to(theme_mount.resolve()) or p.read_bytes() != data:
            raise Hold("Mounted theme bytes differ: " + rel)

    args = json.loads((stage_dir / "playground-cli-arguments.json").read_text())
    if not isinstance(args, list) or len(args) < 3 or args[0] != "npx" or args[2] != "server":
        raise Hold("Unexpected WordPress Playground command")
    if not isinstance(args[1], str) or not PIN.fullmatch(args[1]):
        raise Hold("Playground CLI must be pinned to an exact version; @latest/ranges rejected")
    blueprint = json.loads((stage_dir / "playground-blueprint.json").read_text())
    steps = blueprint.get("steps", [])
    configs = [s.get("consts", {}) for s in steps if s.get("step") == "defineWpConfigConsts"]
    if not blueprint.get("login") or not any(c.get("WP_ENVIRONMENT_TYPE") == "local" for c in configs):
        raise Hold("Local-only authenticated Blueprint requirements missing")
    if not any(s.get("step") == "activateTheme" and s.get("themeFolderName") == "assembler" for s in steps):
        raise Hold("Expected Assembler activation missing")
    if any(s.get("step") in ("importWxr", "importWordPressFiles") for s in steps):
        raise Hold("Production data import not permitted")
    if "finalvestige.com" in json.dumps(blueprint).lower():
        raise Hold("Production domain in local Blueprint")
    return {"status": "SOURCE_INTEGRITY_ADMITTED_ONLY", "exact_head": exact_head,
            "assembler_sha256": trusted_theme_sha256, "cli": args[1],
            "browser": "NOT_RUN", "production": "UNTOUCHED", "release": "HOLD"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage-dir", type=Path, required=True)
    p.add_argument("--assembler-zip", type=Path, required=True)
    p.add_argument("--trusted-assembler-sha256", required=True)
    p.add_argument("--expected-head", required=True)
    a = p.parse_args()
    try:
        print(json.dumps(verify(a.stage_dir, a.assembler_zip, a.trusted_assembler_sha256, a.expected_head), indent=2))
        return 0
    except (Hold, OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as e:
        print("RELEASE HOLD / OFFLINE STAGE REJECTED: " + str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
