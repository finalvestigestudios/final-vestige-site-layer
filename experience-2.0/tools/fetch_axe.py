#!/usr/bin/env python3
"""Fetch axe-core into tools/.cache (gitignored), verified against a pinned SHA-256.

axe-core is a test-only dependency: it is never shipped in the plugin or loaded by any page.
Re-pinning: set AXE_SHA256 to "" and run with --print-hash, then review the hash against the cdnjs SRI value.
"""
from __future__ import annotations

import base64
import hashlib
import sys
import urllib.request
from pathlib import Path

AXE_VERSION = "4.10.2"
AXE_URL = f"https://cdnjs.cloudflare.com/ajax/libs/axe-core/{AXE_VERSION}/axe.min.js"
AXE_SHA256 = "b511cd9dec01c76f4b2ad1723b66b6db37d4c2eb4ed199076e1829d9ee7b75e3"  # matches cdnjs SRI sha512 for 4.10.2
CACHE = Path(__file__).resolve().parent / ".cache" / f"axe-{AXE_VERSION}.min.js"


def ensure_axe() -> Path:
    if CACHE.exists() and (not AXE_SHA256 or hashlib.sha256(CACHE.read_bytes()).hexdigest() == AXE_SHA256):
        return CACHE
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    data = urllib.request.urlopen(urllib.request.Request(AXE_URL, headers={"User-Agent": "fvx-tests"}), timeout=60).read()
    digest = hashlib.sha256(data).hexdigest()
    if AXE_SHA256 and digest != AXE_SHA256:
        raise SystemExit(f"axe-core hash mismatch: expected {AXE_SHA256}, got {digest}")
    CACHE.write_bytes(data)
    return CACHE


if __name__ == "__main__":
    path = ensure_axe()
    raw = path.read_bytes()
    print("axe-core", AXE_VERSION, "sha256", hashlib.sha256(raw).hexdigest(), "sha512-b64", base64.b64encode(hashlib.sha512(raw).digest()).decode(), len(raw), "bytes")
    if "--print-hash" not in sys.argv and not AXE_SHA256:
        print("NOTE: AXE_SHA256 is not pinned yet", file=sys.stderr)
