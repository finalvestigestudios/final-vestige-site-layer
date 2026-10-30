#!/usr/bin/env python3
"""Read-only, offline Focus PDF checksum-evidence reconciler.

Compare WordPress media metadata against a separately observed digest and/or a
local candidate PDF. Neither agreement nor disagreement proves hosted bytes:
only an independently attributed public download can do that.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

EXPECTED_ID = 1737
EXPECTED_NAME = "Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf"
EXPECTED_HOST = "finalvestige.com"
DIGEST = re.compile(r"\bSHA\s*-?\s*256\s*[:=]?\s*([a-fA-F0-9]{64})\b", re.IGNORECASE)
HEX64 = re.compile(r"^[a-f0-9]{64}$", re.IGNORECASE)
MAX_BYTES = 16 * 1024 * 1024


def _meta(data):
    if isinstance(data, dict) and isinstance(data.get("data"), dict):
        data = data["data"]
    if not isinstance(data, dict):
        raise ValueError("Media response must be a JSON object")
    try:
        media_id = int(data.get("id"))
        url = urlsplit(str(data.get("source_url", "")))
        size = int(data.get("media_details", {}).get("filesize"))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError("Missing or malformed media ID, URL, or size") from exc
    if media_id != EXPECTED_ID:
        raise ValueError("Unexpected WordPress media ID")
    if url.scheme != "https" or url.hostname != EXPECTED_HOST or url.port not in (None, 443):
        raise ValueError("Unexpected media URL origin")
    if not url.path.endswith("/" + EXPECTED_NAME) or url.username or url.password or url.query or url.fragment:
        raise ValueError("Unexpected media filename or URL components")
    if data.get("mime_type") != "application/pdf" or size <= 0 or size > MAX_BYTES:
        raise ValueError("Media type or size outside safe bounds")
    description = str(data.get("description") or "")
    digests = set(x.lower() for x in DIGEST.findall(description))
    if len(digests) > 1:
        raise ValueError("Multiple contradictory SHA-256 values in media description")
    return {"media_id":media_id,"source_url":data["source_url"],"expected_size":size,
            "metadata_sha256":next(iter(digests), None)}


def _hash_local(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError("Candidate file not found")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("Candidate file exceeds read limit")
    blob = path.read_bytes()
    if not blob.startswith(b"%PDF-") or b"%%EOF" not in blob[-2048:]:
        raise ValueError("Candidate is not recognizably a complete PDF")
    return len(blob), hashlib.sha256(blob).hexdigest()


def check(media, observed_digest=None, candidate_file=None):
    """Return audit facts and a cautious result; never assert live HTTP success."""
    m = _meta(media)
    observed = None
    if observed_digest is not None:
        if not isinstance(observed_digest, str) or not HEX64.fullmatch(observed_digest):
            raise ValueError("Comparison digest must be 64 hex characters")
        observed = observed_digest.lower()
    local = None
    if candidate_file is not None:
        size, sha = _hash_local(candidate_file)
        local = {"bytes":size,"sha256":sha,"matches_recorded_size":size==m["expected_size"],
                 "matches_metadata_digest":sha==m["metadata_sha256"] if m["metadata_sha256"] else None}
    result = "INSUFFICIENT_EVIDENCE"
    if observed and m["metadata_sha256"]:
        result = ("OBSERVED_CLAIM_AGREES_NOT_PUBLIC_PROOF" if observed==m["metadata_sha256"]
                  else "CONFLICTING_DIGEST_CLAIMS")
    if local:
        result = ("LOCAL_CANDIDATE_AGREES_NOT_PUBLIC_PROOF" if local["matches_recorded_size"]
                  and local["matches_metadata_digest"] else "LOCAL_CANDIDATE_DIFFERS_NOT_PUBLIC_PROOF")
    return {"result":result,"media_id":m["media_id"],"url":m["source_url"],
            "recorded_size":m["expected_size"],"metadata_sha256_claim":m["metadata_sha256"],
            "independent_sha256_claim":observed,"local_candidate":local,
            "hosted_pdf_verified":False,
            "verification_limit":"No public GET or authenticated hosted-asset bytes were examined."}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--media-json",required=True,help="Sanitized WordPress media.get JSON")
    p.add_argument("--independent-sha256",help="Separately reported checksum (claim only)")
    p.add_argument("--local-pdf",help="Optional offline candidate file (origin unverified)")
    a=p.parse_args(argv)
    try:
        result=check(json.loads(Path(a.media_json).read_text(encoding="utf-8")),
                     a.independent_sha256,a.local_pdf)
    except (OSError,ValueError,json.JSONDecodeError) as exc:
        print(json.dumps({"result":"INVALID_EVIDENCE","reason":str(exc),"hosted_pdf_verified":False}))
        return 2
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result["result"].startswith("LOCAL_CANDIDATE_AGREES") else 1

if __name__=="__main__":
    sys.exit(main())
