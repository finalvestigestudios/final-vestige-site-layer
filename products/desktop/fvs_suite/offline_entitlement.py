"""Offline, fail-closed Ed25519 premium entitlements (pre-release interface).

Only distributor public keys belong in clients. Signing private keys and issue
services must NEVER be bundled, committed, or accepted from license documents.
A valid signature does not confer download access, reviewer identity, or payment
approval; a local executable is not tamper-resistant DRM.
"""
from __future__ import annotations

import base64
import binascii
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .journal_io import read_regular_bytes
from .entitlement_reader_privacy_r383 import read_private_entitlement

DOMAIN = b"FinalVestigeLabs.entitlement.v1\x00"
SCHEMA = "fvs.entitlement.v1"
PRODUCTS = frozenset({"grants", "procurement"})
FIELDS = frozenset({"schema", "kid", "product", "license_id", "holder", "issued_at",
                    "not_before", "expires_at", "signature"})
MAX_BYTES = 8192
# Intentionally empty until a separately approved, protected signing authority
# exists. Never put a sample/test public key here: test private keys are public.
TRUSTED_PUBLIC_KEYS: Mapping[str, bytes] = {}
STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
IDENTIFIER = re.compile(r"^[A-Za-z0-9_-]{4,64}$")
SIGNATURE = re.compile(r"^[A-Za-z0-9_-]{86}$")


class EntitlementError(ValueError):
    """A premium application must not start an unlicensed data workflow."""


@dataclass(frozen=True)
class Entitlement:
    product: str
    license_id: str
    holder: str
    expires_at: datetime


def _unique_fields(pairs):
    obj = {}
    for name, value in pairs:
        if name in obj:
            raise EntitlementError("Duplicate entitlement field")
        obj[name] = value
    return obj


def _time(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not STAMP.fullmatch(value):
        raise EntitlementError(f"{field} must be a canonical UTC timestamp")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise EntitlementError(f"Invalid {field} UTC timestamp") from exc


def _canonical_payload(data: dict) -> bytes:
    return DOMAIN + json.dumps({k: v for k, v in data.items() if k != "signature"},
                               sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False, allow_nan=False).encode("utf-8")


def installed_license_path(product: str) -> Path:
    if product not in PRODUCTS:
        raise EntitlementError("Unknown premium application")
    base = os.environ.get("LOCALAPPDATA") if os.name == "nt" else None
    folder = Path(base) if base else Path.home() / ".config"
    return folder / "FinalVestige" / "licenses" / f"{product}.fvslicense"


def _read_signed_entitlement(source: str | Path) -> bytes:
    """Pin the local license descriptor while bounding and checking its bytes.

    Reject observed replacements, aliases, links, and in-flight edits rather
    than trusting a separate is_file/stat/open sequence. Return only verified
    bytes to the signature validator; never echo private paths in GUI errors.
    """
    return read_private_entitlement(source, MAX_BYTES, read_regular_bytes, EntitlementError)


def verify_license(path: str | Path, product: str, *,
                   trusted_keys: Mapping[str, bytes] | None = None,
                   now: datetime | None = None) -> Entitlement:
    """Verify against client-pinned authority, exact product and UTC time.

    Test-only injectable keys and time are not exposed by the packaged GUI.
    Offline clients cannot prevent clock rollback, binary patching, copying,
    or license sharing by themselves.
    """
    if product not in PRODUCTS:
        raise EntitlementError("Unknown premium application")
    keys = TRUSTED_PUBLIC_KEYS if trusted_keys is None else trusted_keys
    if not keys:
        raise EntitlementError("Premium entitlements are not activated in this pre-release build")
    data = _read_signed_entitlement(path)
    try:
        item = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_fields,
                          parse_constant=lambda _: (_ for _ in ()).throw(
                              EntitlementError("Nonfinite entitlement field")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise EntitlementError("Malformed entitlement document") from exc
    if not isinstance(item, dict) or set(item) != FIELDS:
        raise EntitlementError("Unsupported or incomplete entitlement schema")
    for field in ("schema", "kid", "product", "license_id", "holder", "signature"):
        if not isinstance(item[field], str):
            raise EntitlementError(f"Invalid {field} type")
    if item["schema"] != SCHEMA or item["product"] != product:
        raise EntitlementError("Entitlement schema or product does not match")
    if not IDENTIFIER.fullmatch(item["kid"]) or not IDENTIFIER.fullmatch(item["license_id"]):
        raise EntitlementError("Invalid entitlement identifiers")
    holder = item["holder"]
    if not holder or holder != holder.strip() or len(holder) > 120 or any(ord(c) < 32 for c in holder):
        raise EntitlementError("Invalid entitlement holder")
    issued = _time(item["issued_at"], "issued_at")
    start = _time(item["not_before"], "not_before")
    end = _time(item["expires_at"], "expires_at")
    if not (issued <= start < end <= issued + timedelta(days=3660)):
        raise EntitlementError("Invalid entitlement validity window")
    current = datetime.now(timezone.utc) if now is None else now
    if current.tzinfo is None or current.utcoffset() is None:
        raise EntitlementError("A timezone-aware UTC clock is required")
    current = current.astimezone(timezone.utc)
    if not (issued <= current and start <= current < end):
        raise EntitlementError("Entitlement is not yet valid or has expired")
    signature = item["signature"]
    if not SIGNATURE.fullmatch(signature):
        raise EntitlementError("Invalid entitlement signature format")
    try:
        raw_signature = base64.urlsafe_b64decode(signature + "==")
    except (ValueError, binascii.Error) as exc:
        raise EntitlementError("Invalid entitlement signature encoding") from exc
    if len(raw_signature) != 64 or base64.urlsafe_b64encode(raw_signature).decode("ascii").rstrip("=") != signature:
        raise EntitlementError("Noncanonical entitlement signature")
    public_key = keys.get(item["kid"])
    if not isinstance(public_key, bytes) or len(public_key) != 32:
        raise EntitlementError("Unrecognized entitlement signing authority")
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(raw_signature, _canonical_payload(item))
    except (InvalidSignature, ValueError) as exc:
        raise EntitlementError("Entitlement signature failed verification") from exc
    return Entitlement(product=product, license_id=item["license_id"],
                       holder=holder, expires_at=end)
