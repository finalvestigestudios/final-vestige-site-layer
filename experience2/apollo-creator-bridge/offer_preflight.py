#!/usr/bin/env python3
"""Apollo teacher-offer preflight; offline, metadata-only and always non-authorizing.

Do not use this output to enable checkout, publishing, paid links or tracking.
No merchant credentials, customer data, orders or payments are accepted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA = "fv.apollo.offergate.v1"
FIELDS = {"schema", "offer", "checks"}
CHECKS = ("seller_listing", "rights_media", "fulfillment", "refund_terms", "independent_editorial", "founder_release")
SKU = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{2,64}$")
HASH = re.compile(r"^[a-f0-9]{64}$")
SENSITIVE = re.compile(r"(?:@|(?i:token|secret|password|email|phone|session|cookie|api[_-]?key|card|customer))")

class ContractError(ValueError):
    pass

def distinct_pairs(pairs):
    obj = {}
    for key, val in pairs:
        if key in obj:
            raise ContractError("duplicate JSON member")
        obj[key] = val
    return obj

def exact_keys(obj, keys, label):
    if not isinstance(obj, dict) or set(obj) != set(keys):
        raise ContractError(label + ": exact schema keys required")

def strict_text(value, label, size=180):
    if not isinstance(value, str) or not 1 <= len(value) <= size or SENSITIVE.search(value):
        raise ContractError(label + ": invalid or potentially sensitive text")
    return value

def payhip_path(link):
    if not isinstance(link, str) or len(link) > 180:
        raise ContractError("offer URL must be a short canonical HTTPS Payhip product URL")
    url = urlsplit(link)
    if (url.scheme != "https" or url.netloc != "payhip.com" or url.query or url.fragment
            or url.username or url.password or url.port or not re.fullmatch(r"/b/[A-Za-z0-9_-]+/?", url.path)):
        raise ContractError("no canonical Payhip product destination")
    return link

def validate(manifest: dict) -> dict:
    exact_keys(manifest, FIELDS, "manifest")
    if manifest["schema"] != SCHEMA:
        raise ContractError("unsupported offer contract")
    offer = manifest["offer"]
    exact_keys(offer, {"sku", "product_title", "seller", "category", "product_url", "price_minor_units", "currency"}, "offer")
    if not isinstance(offer["sku"], str) or not SKU.fullmatch(offer["sku"]):
        raise ContractError("invalid seller SKU")
    title = strict_text(offer["product_title"], "title")
    if not re.search(r"apollo\s*1|apollo\s*204", title, re.I):
        raise ContractError("offer is not relevant to this Apollo investigation")
    if offer["seller"] != "Final Vestige Studios" or offer["category"] != "educator_casefile":
        raise ContractError("wrong seller or audience-specific product")
    if type(offer["price_minor_units"]) is not int or offer["price_minor_units"] <= 0:
        raise ContractError("verified nonzero integer price required")
    if offer["currency"] != "USD":
        raise ContractError("currency not supported in this pilot")
    payhip_path(offer["product_url"])
    checks = manifest["checks"]
    exact_keys(checks, CHECKS, "checks")
    reviewed = []
    awaiting = []
    for key in CHECKS:
        record = checks[key]
        exact_keys(record, {"state", "evidence_sha256", "checked_utc"}, key)
        state = record["state"]
        if state not in ("pending", "reviewed"):
            raise ContractError(key + ": invalid evidence state")
        sha = record["evidence_sha256"]
        timestamp = record["checked_utc"]
        if state == "pending" and (sha is not None or timestamp is not None):
            raise ContractError(key + ": pending entry must not masquerade as evidence")
        if state == "reviewed":
            if not isinstance(sha, str) or not HASH.fullmatch(sha):
                raise ContractError(key + ": reviewed item missing SHA-256 custody proof")
            if not isinstance(timestamp, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", timestamp):
                raise ContractError(key + ": reviewed item must have explicit UTC timestamp")
            try:
                when = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError as e:
                raise ContractError(key + ": invalid UTC date") from e
            if when > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
                raise ContractError(key + ": future review claimed")
            reviewed.append(key)
        else:
            awaiting.append(key)
    # A checked manifest proves only formatting/custody references. These hashes do NOT prove
    # that source documents exist, rights were granted, checkout works or approval was given.
    return {"schema": SCHEMA, "result": "STAGING_HOLD_REVIEW_REQUIRED",
            "metadata_checks": len(reviewed), "unreviewed": awaiting,
            "source_documents_authenticated": False, "merchant_paid_orders_verified": False,
            "founder_authorization_verified": False, "can_publish": False,
            "can_enable_checkout": False, "can_claim_revenue": False}

def load(path: Path):
    if path.stat().st_size > 32_768:
        raise ContractError("manifest size exceeds offline contract limit")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=distinct_pairs)
    except (UnicodeError, json.JSONDecodeError) as e:
        raise ContractError("invalid JSON") from e
    return validate(obj)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", type=Path)
    args = p.parse_args()
    try:
        result = load(args.manifest)
    except (ContractError, OSError, ValueError) as e:
        print(json.dumps({"schema": SCHEMA, "result": "INVALID_STAGING_HOLD",
                          "reason": str(e), "can_publish": False}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
