#!/usr/bin/env python3
"""Prepare a LOCAL-only WordPress Playground review for PR #224's sealed EX2 plugin.

Does not start, install into, or communicate with any WordPress site.
Requires a clean, exact Git checkout with PR #224's builder and the complete
seven-chapter Experience 2 source. The generated preview has no customer data.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ASSETS = ("index.html", "flagship.css", "chronicle.css", "chronicle-lens.css",
          "inquiry.css", "observer-lab.css", "reading-trail.css", "flagship.js",
          "observer-lab.js", "chronicle-lens.js", "reading-trail.js")
ZIPROOT = "fv-ex2-sealed-staging-preview"
BUILDER = "experience2/home-flagship/qa/integration/sealed/build_sealed_staging_zip.py"
PLUGIN = "fv-ex2-sealed-preview.php"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.STDOUT, text=True).strip()


def verify_checkout(repo: Path, expected: str):
    if not re.fullmatch(r"[0-9a-f]{40}", expected):
        raise ValueError("Expected head must be a complete 40-character hexadecimal SHA")
    actual = git(repo, "rev-parse", "HEAD")
    if actual != expected:
        raise ValueError(f"Checkout HEAD mismatch: expected {expected}, got {actual}")
    paths = ["experience2/home-flagship/" + a for a in ASSETS] + [BUILDER,
        "experience2/home-flagship/qa/integration/sealed/fv-ex2-sealed-preview.php"]
    for path in paths:
        absolute = repo / path
        if not absolute.is_file() or absolute.is_symlink():
            raise ValueError(f"Missing or symlinked tracked asset: {path}")
        tracked_blob = git(repo, "rev-parse", f"HEAD:{path}")
        working_blob = git(repo, "hash-object", "--", path)
        if tracked_blob != working_blob:
            raise ValueError(f"Dirty or unexpected source asset: {path}")
    return paths


def blueprint():
    # Only the isolated Playground environment may create this PRIVATE reviewer page.
    php = ("<?php require_once '/wordpress/wp-load.php'; "
           "if (wp_get_environment_type() !== 'local' || "
           "!defined('FV_EX2_ALLOW_PREVIEW') || FV_EX2_ALLOW_PREVIEW !== true) "
           "{ throw new RuntimeException('Not isolated local Playground'); } "
           "$old = get_page_by_path('fv-ex2-local-review'); "
           "if (!$old) { $id = wp_insert_post(array('post_title'=>'FV EX2 LOCAL REVIEW — NOT LIVE', "
           "'post_name'=>'fv-ex2-local-review', 'post_type'=>'page', "
           "'post_status'=>'private', 'post_content'=>'[fv_ex2_sealed_homepage_preview]'), true); "
           "if (is_wp_error($id)) { throw new RuntimeException($id->get_error_message()); } } ")
    return {
        "$schema": "https://playground.wordpress.net/blueprint-schema.json",
        "landingPage": "/wp-admin/",
        "preferredVersions": {"php": "8.3", "wp": "latest"},
        "login": True,
        "steps": [
            {"step": "defineWpConfigConsts", "consts": {
                "WP_ENVIRONMENT_TYPE": "local", "FV_EX2_ALLOW_PREVIEW": True,
                "DISALLOW_FILE_EDIT": True}},
            {"step": "activatePlugin", "pluginPath": ZIPROOT + "/" + PLUGIN},
            {"step": "runPHP", "code": php}
        ]
    }



def validate_output_tree(out: Path):
    """Fail before the builder or any write can traverse a reused staging output.

    The directory mounted as a WordPress plugin may contain *only* the sealed PHP
    entrypoint. Even a .txt copy of the preview HTML would be publicly requestable.
    """
    for directory in (out / 'plugin', out / 'plugin' / ZIPROOT):
        if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
            raise ValueError(f'Unsafe staging output directory: {directory}')
    for candidate in (out / 'sealed-review.zip', out / 'blueprint.json',
                      out / 'receipt.json', out / 'plugin' / ZIPROOT / PLUGIN):
        if candidate.is_symlink() or (candidate.exists() and not candidate.is_file()):
            raise ValueError(f'Unsafe staging output file: {candidate}')
    plugin_dir = out / 'plugin' / ZIPROOT
    if plugin_dir.is_dir():
        unexpected = sorted(p.name for p in plugin_dir.iterdir() if p.name != PLUGIN)
        if unexpected:
            raise ValueError('Unexpected potentially public files in mounted plugin directory: '
                             + ', '.join(unexpected))

def build(repo: Path, out: Path, expected: str):
    repo = repo.resolve(strict=True)
    if out.is_symlink():
        raise ValueError('Staging output must not be a symbolic link')
    out = out.resolve()
    source_root = repo / "experience2/home-flagship"
    if out == repo or repo in out.parents:
        raise ValueError("Output must be outside the source repository and any production tree")
    if any(part in ("wp-content", "public_html") for part in out.parts):
        raise ValueError("Refusing to write a WordPress/webroot directory")
    paths = verify_checkout(repo, expected)
    validate_output_tree(out)  # Before ZIP generation, mkdir or plugin extraction.
    out.mkdir(parents=True, exist_ok=True)
    zip_path = out / "sealed-review.zip"
    subprocess.run([sys.executable, str(repo / BUILDER), "--root", str(source_root),
                    "--out", str(zip_path), "--expected-head", expected],
                   check=True, capture_output=True, text=True)
    plugin_dir = out / "plugin" / ZIPROOT
    plugin_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        entries = sorted(z.namelist())
        expected_entries = sorted([f"{ZIPROOT}/{PLUGIN}", f"{ZIPROOT}/STAGING_MANIFEST.json",
                                   f"{ZIPROOT}/INSTALLATION_HOLD.txt"])
        if entries != expected_entries:
            raise ValueError("Unexpected files in sealed ZIP")
        data = z.read(f"{ZIPROOT}/{PLUGIN}")
        manifest = json.loads(z.read(f"{ZIPROOT}/STAGING_MANIFEST.json"))
        if manifest["expected_commit"] != expected or manifest["browser_visible_asset_paths"]:
            raise ValueError("Builder's staging manifest does not match or exposes raw assets")
        if hashlib.sha256(data).hexdigest() != manifest["plugin_sha256"]:
            raise ValueError("Sealed PHP payload digest mismatch")
        (plugin_dir / PLUGIN).write_bytes(data)
    bp = blueprint()
    bp_path = out / "blueprint.json"
    bp_path.write_text(json.dumps(bp, indent=2) + "\n", encoding="utf-8")
    receipt = {"decision": "OFFLINE_PACKAGE_BUILT__NOT_WORDPRESS_ACCEPTED",
               "source_head": expected, "verified_tracked_paths": paths,
               "sealed_zip_sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
               "php_sha256": hashlib.sha256(data).hexdigest(),
               "blueprint_sha256": hashlib.sha256(bp_path.read_bytes()).hexdigest(),
               "private_page": "/fv-ex2-local-review/", "production_writes": False,
               "browser_acceptance": "NOT_RUN", "jetpack_acceptance": "NOT_TESTABLE_IN_PLAYGROUND",
               "hosted_equivalence": False}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--expected-head", required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(build(args.repo, args.out, args.expected_head), indent=2))


if __name__ == "__main__":
    main()
