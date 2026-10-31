#!/usr/bin/env python3
"""Offline, read-only consistency check for WordPress PDF provenance metadata.

A local reference PDF may be a different editorial revision than the hosted asset.
This gate does NOT download the public file, confirm HTTP, or certify 52 pages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

MAX_PDF_BYTES = 32 * 1024 * 1024
MAX_JSON_BYTES = 2 * 1024 * 1024
CLAIM = re.compile(r"\bsha(?:-?256)\s*[:=]?\s*([0-9a-f]{64})\b", re.I)
ALLOWED_HOSTS = {"finalvestige.com", "www.finalvestige.com"}


def pdf_facts(payload: bytes) -> dict:
    return {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
            "pdf_signature": payload.startswith(b"%PDF-") and b"%%EOF" in payload[-1024:]}


def audit(media: dict, reference: bytes, hosted: bytes | None = None,
          expected_media_id: int = 1737) -> dict:
    """Compare exact metadata SHA claims with known reference and optional hosted bytes.

    Metadata mismatch is a source-level fact; hosted identity is unknown without
    actual hosted file bytes, and even a provided PDF is not an HTTP receipt.
    """
    if isinstance(media, dict) and isinstance(media.get("data"), dict):
        media = media["data"]
    if not isinstance(media, dict):
        raise ValueError("WordPress media input is not a JSON object")
    if media.get("id") != expected_media_id:
        raise ValueError("WordPress media ID does not match requested asset")
    url = media.get("source_url", "")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password or not parsed.path.lower().endswith(".pdf"):
        raise ValueError("Media source URL must be first-party HTTPS PDF")
    declared_size = media.get("media_details", {}).get("filesize")
    if not isinstance(declared_size, int) or isinstance(declared_size, bool) or declared_size <= 0:
        raise ValueError("Media filesize not a positive integer")

    def field(v: object) -> str:
        if isinstance(v, dict):
            return str(v.get("rendered", ""))
        return v if isinstance(v, str) else ""

    claims = set(CLAIM.findall(field(media.get("caption", "")) + "\n" + field(media.get("description", ""))))
    claims = {c.lower() for c in claims}
    ref = pdf_facts(reference)
    download = pdf_facts(hosted) if hosted is not None else None
    errors, warnings = [], []
    if not ref["pdf_signature"]:
        errors.append("REFERENCE_PDF_SIGNATURE_INVALID")
    if len(claims) > 1:
        errors.append("CONFLICTING_PUBLISHED_SHA256_CLAIMS")
    if len(claims) == 0:
        warnings.append("NO_PUBLISHED_SHA256_CLAIM")
    # A SHA fingerprint proven for one reference PDF cannot be asserted for a
    # differently sized recorded asset without downloading and verifying it.
    if ref["sha256"] in claims and declared_size != ref["bytes"]:
        errors.append("REFERENCE_DIGEST_REUSED_FOR_DIFFERENT_SIZE_ASSET")
    if download is not None:
        if not download["pdf_signature"]:
            errors.append("HOSTED_COPY_PDF_SIGNATURE_INVALID")
        if download["bytes"] != declared_size:
            errors.append("HOSTED_COPY_SIZE_DISAGREES_WITH_WP_RECORD")
        if claims and download["sha256"] not in claims:
            errors.append("HOSTED_COPY_SHA256_DISAGREES_WITH_PUBLISHED_CLAIM")
        if download["sha256"] != ref["sha256"]:
            warnings.append("HOSTED_COPY_DIFFERS_FROM_ARCHIVED_REFERENCE_VERSION")
    else:
        warnings.append("HOSTED_PDF_BYTES_NOT_PROVIDED")
    status = "FAIL" if errors else "HOLD" if (download is None or not claims) else "PASS_LOCAL_BYTES"
    return {"status": status, "media_id": expected_media_id,
            "wp_recorded_bytes": declared_size, "reference_bytes": ref["bytes"],
            "reference_sha256": ref["sha256"], "published_sha256_claims": sorted(claims),
            "hosted_copy_bytes": download["bytes"] if download else None,
            "hosted_copy_sha256": download["sha256"] if download else None,
            "errors": errors, "warnings": warnings,
            "limits": "No network access, HTTP status, email delivery, page-count certification, or publisher approval verified."}


def read_bounded(path: Path, limit: int) -> bytes:
    if path.stat().st_size > limit:
        raise ValueError("Input exceeds offline safety size limit")
    return path.read_bytes()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--media", required=True, type=Path, help="Sanitized WordPress media.get JSON")
    ap.add_argument("--reference", required=True, type=Path, help="Trusted archived PDF on local disk")
    ap.add_argument("--hosted", type=Path, help="Optional separately downloaded public PDF bytes")
    ap.add_argument("--expected-id", type=int, default=1737)
    a = ap.parse_args(argv)
    try:
        record = json.loads(read_bounded(a.media, MAX_JSON_BYTES))
        ref = read_bounded(a.reference, MAX_PDF_BYTES)
        hosted = read_bounded(a.hosted, MAX_PDF_BYTES) if a.hosted else None
        result = audit(record, ref, hosted, a.expected_id)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "HOLD", "errors": [], "warnings": ["INPUT_UNVERIFIABLE"],
                          "reason": type(exc).__name__,
                          "limits": "No media bytes were submitted to a server or site."}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 1 if result["status"] == "FAIL" else 2 if result["status"] == "HOLD" else 0


if __name__ == "__main__":
    raise SystemExit(main())
