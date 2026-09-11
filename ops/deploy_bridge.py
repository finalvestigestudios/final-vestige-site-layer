#!/usr/bin/env python3
"""Send one exact Site Layer package to the FVDB v0.3.1 HMAC endpoint."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import time
import urllib.error
import urllib.request

REPOSITORY = "finalvestigestudios/final-vestige-site-layer"
BRANCH = "production"
ENDPOINT = "https://finalvestige.com/wp-json/fv-deploy/v1/deploy"
TARGET = "final-vestige-site-layer"


def package_sha256(package: bytes) -> str:
    return hashlib.sha256(package).hexdigest()


def build_signed_request(
    *,
    secret: str,
    commit: str,
    package: bytes,
    timestamp: int,
    nonce: str,
) -> tuple[bytes, dict[str, str]]:
    if not re.fullmatch(r"[a-f0-9]{64}", secret):
        raise ValueError("deployment secret must be exactly 64 lowercase hex characters")
    if not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise ValueError("commit must be an exact 40-character lowercase SHA-1")
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,96}", nonce):
        raise ValueError("nonce does not satisfy bridge format")

    digest = package_sha256(package)
    body = json.dumps(
        {
            "package_base64": base64.b64encode(package).decode("ascii"),
            "package_sha256": digest,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    body_sha = hashlib.sha256(body).hexdigest()
    canonical = "\n".join(
        [
            str(timestamp),
            nonce,
            REPOSITORY,
            BRANCH,
            commit,
            body_sha,
        ]
    )
    signature = "sha256=" + hmac.new(
        secret.encode("ascii"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-FV-Timestamp": str(timestamp),
        "X-FV-Nonce": nonce,
        "X-FV-Repository": REPOSITORY,
        "X-FV-Branch": BRANCH,
        "X-FV-Commit": commit,
        "X-FV-Signature": signature,
    }
    return body, headers


def deploy(commit: str, package_path: Path) -> dict:
    secret = os.environ.get("FV_WP_DEPLOY_SECRET", "").strip().lower()
    if not secret:
        raise SystemExit("FV_WP_DEPLOY_SECRET is not configured")
    if os.environ.get("GITHUB_REPOSITORY") not in (None, REPOSITORY):
        raise SystemExit("refusing deployment from an unexpected repository")
    if os.environ.get("GITHUB_REF_NAME") not in (None, BRANCH):
        raise SystemExit("refusing deployment from a non-production branch")

    package = package_path.read_bytes()
    digest = package_sha256(package)
    timestamp = int(time.time())
    nonce = secrets.token_urlsafe(24)
    body, headers = build_signed_request(
        secret=secret,
        commit=commit,
        package=package,
        timestamp=timestamp,
        nonce=nonce,
    )

    request = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status = response.status
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        raise SystemExit(
            f"bridge returned HTTP {exc.code}: {raw[:500].decode('utf-8', 'replace')}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"bridge request failed: {exc.reason}") from exc

    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise SystemExit("bridge returned non-JSON output") from exc

    if status != 200 or payload.get("ok") is not True:
        raise SystemExit(f"bridge rejected deployment: HTTP {status} {payload}")
    if payload.get("commit") != commit:
        raise SystemExit("bridge response commit does not match the signed commit")
    if payload.get("package_sha256") != digest:
        raise SystemExit("bridge response package SHA-256 does not match sent bytes")
    if payload.get("target") != TARGET:
        raise SystemExit("bridge response target is unexpected")
    if payload.get("activation_changed") is not False:
        raise SystemExit("bridge unexpectedly changed Site Layer activation state")
    if payload.get("status") not in {"deployed", "already_deployed"}:
        raise SystemExit("bridge returned an unexpected deployment status")

    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("commit")
    parser.add_argument("package", type=Path)
    args = parser.parse_args()

    result = deploy(args.commit.lower(), args.package)
    print(
        json.dumps(
            {
                "ok": result["ok"],
                "status": result["status"],
                "commit": result["commit"],
                "package_sha256": result["package_sha256"],
                "target": result["target"],
                "activation_changed": result["activation_changed"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
