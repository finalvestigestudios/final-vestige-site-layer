#!/usr/bin/env python3
"""Adversarial/static checks for the Site Layer -> Deployment Bridge handoff."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ops"))

import deploy_bridge  # noqa: E402

REPOSITORY = "finalvestigestudios/final-vestige-site-layer"
BRANCH = "production"
ZIP_ROOT = "final-vestige-site-layer"
PACKAGE_FILES = {
    "final-vestige-site-layer.php",
    "payloads/case-search-wp-block-v1.txt",
    "payloads/detail-lens-wp-block-v1.txt",
    "payloads/evidence-map-wp-block-v1.txt",
    "payloads/scale-board-wp-block-r4.txt",
    "payloads/signal-finder-wp-block-v1.txt",
}
CHECKOUT_SHA = "11d5960a326750d5838078e36cf38b85af677262"
UPLOAD_ARTIFACT_SHA = "ea165f8d65b6e75b540449e92b4886f43607fa02"


def fail(message: str) -> None:
    print(f"DEPLOY LANE VERIFY: FAIL — {message}")
    raise SystemExit(1)


def main() -> int:
    if len(sys.argv) != 3:
        fail("usage: verify_deploy_lane.py <commit> <package.zip>")

    commit = sys.argv[1].lower()
    package_path = Path(sys.argv[2])
    if not re.fullmatch(r"[a-f0-9]{40}", commit):
        fail("invalid commit")
    package = package_path.read_bytes()

    with zipfile.ZipFile(package_path) as zf:
        names = set(zf.namelist())
        expected_names = {f"{ZIP_ROOT}/{p}" for p in PACKAGE_FILES}
        expected_names.add(f"{ZIP_ROOT}/release-manifest.json")
        if names != expected_names:
            fail(f"ZIP allowlist mismatch expected={sorted(expected_names)} actual={sorted(names)}")

        manifest = json.loads(
            zf.read(f"{ZIP_ROOT}/release-manifest.json").decode("utf-8")
        )
        if manifest.get("repository") != REPOSITORY:
            fail("manifest repository mismatch")
        if manifest.get("branch") != BRANCH:
            fail("manifest branch mismatch")
        if manifest.get("commit") != commit:
            fail("manifest commit mismatch")

        file_entries = manifest.get("files")
        if not isinstance(file_entries, list):
            fail("manifest files allowlist missing")
        declared = {}
        for item in file_entries:
            if not isinstance(item, dict):
                fail("manifest file entry is not an object")
            rel = item.get("path")
            digest = item.get("sha256")
            if rel in declared:
                fail(f"duplicate manifest path: {rel}")
            if rel not in PACKAGE_FILES:
                fail(f"unexpected manifest path: {rel}")
            data = zf.read(f"{ZIP_ROOT}/{rel}")
            actual = hashlib.sha256(data).hexdigest()
            if digest != actual:
                fail(f"manifest SHA mismatch: {rel}")
            if item.get("bytes") != len(data):
                fail(f"manifest byte-count mismatch: {rel}")
            declared[rel] = digest

        if set(declared) != PACKAGE_FILES:
            fail("manifest file allowlist is incomplete")

        source_manifest = json.loads((ROOT / "release-manifest.json").read_text())
        for payload in source_manifest.get("payloads", []):
            rel = payload["file"]
            data = zf.read(f"{ZIP_ROOT}/{rel}")
            if len(data) != payload["bytes"]:
                fail(f"source payload byte mismatch: {rel}")
            if hashlib.sha256(data).hexdigest() != payload["sha256"]:
                fail(f"source payload SHA mismatch: {rel}")

    known_secret = "11" * 32
    known_timestamp = 1_700_000_000
    known_nonce = "FixedNonce_1234567890"
    body, headers = deploy_bridge.build_signed_request(
        secret=known_secret,
        commit=commit,
        package=package,
        timestamp=known_timestamp,
        nonce=known_nonce,
    )
    body_sha = hashlib.sha256(body).hexdigest()
    canonical = "\n".join(
        [
            str(known_timestamp),
            known_nonce,
            REPOSITORY,
            BRANCH,
            commit,
            body_sha,
        ]
    )
    expected_signature = "sha256=" + hmac.new(
        known_secret.encode("ascii"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if headers.get("X-FV-Signature") != expected_signature:
        fail("HMAC canonicalization mismatch")
    if headers.get("X-FV-Repository") != REPOSITORY:
        fail("sender repository header mismatch")
    if headers.get("X-FV-Branch") != BRANCH:
        fail("sender branch header mismatch")
    if headers.get("X-FV-Commit") != commit:
        fail("sender commit header mismatch")

    envelope = json.loads(body.decode("utf-8"))
    if envelope.get("package_sha256") != hashlib.sha256(package).hexdigest():
        fail("sender package hash mismatch")
    if base64.b64decode(envelope.get("package_base64", ""), validate=True) != package:
        fail("sender base64 payload mismatch")

    tampered = body + b" "
    if hashlib.sha256(tampered).hexdigest() == body_sha:
        fail("tamper test did not alter body hash")

    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    required_workflow_fragments = [
        "needs: verify",
        "github.ref == 'refs/heads/production'",
        "secrets.FV_WP_DEPLOY_SECRET",
        "python3 ops/deploy_bridge.py",
        "git diff --quiet \"$RELEASE_COMMIT\" HEAD",
        "FVSL-QD-PASS:",
        "FVSL-QD-HEAD:",
        "FVSL-PACKAGE-SHA256:",
        "APPROVED_PACKAGE_SHA",
        f"actions/checkout@{CHECKOUT_SHA}",
        f"actions/upload-artifact@{UPLOAD_ARTIFACT_SHA}",
        "python3 tests/verify_case_search.py",
    ]
    for fragment in required_workflow_fragments:
        if fragment not in workflow:
            fail(f"workflow missing fail-closed contract: {fragment}")

    if "    env:\n      FV_WP_DEPLOY_SECRET:" in workflow:
        fail("deployment secret must not be exposed at job scope")

    print(
        "DEPLOY LANE VERIFY: PASS "
        f"commit={commit} package_sha256={hashlib.sha256(package).hexdigest()} "
        f"bytes={len(package)} files={len(PACKAGE_FILES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
