"""Offline, operator-only premium entitlement issuer. NEVER package with an EXE.

This is an issuance primitive, NOT an approved checkout, signing service, or
production key-management system. The private PEM remains outside the repo.
"""
from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from fvs_suite import offline_entitlement as verifier
from license_registry import IssuanceRegistry, RegistryError
from signing_key_guard import read_signing_key
from license_output_guard import create_issued_license

MAX_KEY_BYTES = 16 * 1024
KEY_HEADER = b"-----BEGIN ENCRYPTED PRIVATE KEY-----\n"


class IssuanceError(ValueError):
    """Refuse to issue an unsafe or invalid entitlement."""


def _key_from_encrypted_pem(path: str | Path, password: bytes) -> Ed25519PrivateKey:
    """Load an encrypted PKCS#8 Ed25519 PEM via a bounded regular-file read."""
    if not isinstance(password, bytes) or not password:
        raise IssuanceError("A nonempty private-key passphrase is required")
    source = Path(path)
    # A key created inside any Git worktree risks being committed by mistake.
    if any((ancestor / ".git").exists() for ancestor in (source.parent, *source.parents)):
        raise IssuanceError("Signing keys must live outside Git repositories")
    # Inspect/read through a single bounded descriptor, rejecting hardlinks,
    # path replacements and exposed reparse points. No private OS exception
    # can survive in a public IssuanceError chain.
    pem = read_signing_key(source, MAX_KEY_BYTES, IssuanceError)
    if not pem.startswith(KEY_HEADER):
        raise IssuanceError("Expected encrypted PKCS#8 PEM (not plaintext or oversized)")
    decrypt_failed = False
    key = None
    try:
        key = serialization.load_pem_private_key(pem, password=password)
    except (TypeError, ValueError):
        decrypt_failed = True
    # Leave the cryptography handler before raising a public error; "from None"
    # alone would still retain the original sensitive __context__ reference.
    if decrypt_failed:
        raise IssuanceError("Cannot decrypt encrypted signing key")
    if not isinstance(key, Ed25519PrivateKey):
        raise IssuanceError("Signing authority must use an Ed25519 private key")
    return key


def _validate_text(value: str, field: str) -> None:
    if not isinstance(value, str):
        raise IssuanceError(f"Invalid {field}")
    if field == "holder":
        if not (1 <= len(value) <= 120) or value != value.strip() or any(
            ord(c) < 32 or ord(c) == 127 for c in value
        ):
            raise IssuanceError("Invalid holder")
    elif not verifier.IDENTIFIER.fullmatch(value):
        raise IssuanceError(f"Invalid {field}")


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise IssuanceError("Issuance clock must be timezone aware")
    return value.astimezone(timezone.utc).replace(microsecond=0)


def issue_entitlement(*, key_path: str | Path, password: bytes,
                      kid: str, product: str, license_id: str, holder: str,
                      expires_at: str, output: str | Path,
                      not_before: str | None = None,
                      now: datetime | None = None,
                      return_digest: bool = False) -> Path | tuple[Path, str]:
    """Sign once, write with O_EXCL, then independently verify the disk bytes.

    password is an in-process argument for testability. CLI reads it only
    from a terminal with getpass, NEVER through argv, environment, or files.
    The caller must track unique license IDs and authorize fulfillment.
    """
    # Select a native premium product before processing identifiers, clocks,
    # output paths or private signing authority. str subclasses can override
    # hash/equality and impersonate a recognized entitlement product.
    if type(product) is not str or product not in verifier.PRODUCTS:
        raise IssuanceError("Unknown premium product")
    _validate_text(kid, "kid")
    _validate_text(license_id, "license_id")
    _validate_text(holder, "holder")
    current = _utc(datetime.now(timezone.utc) if now is None else now)
    issued = current.strftime("%Y-%m-%dT%H:%M:%SZ")
    start = issued if not_before is None else not_before
    try:
        start_dt = verifier._time(start, "not_before")
        end_dt = verifier._time(expires_at, "expires_at")
    except verifier.EntitlementError as exc:
        raise IssuanceError(str(exc)) from exc
    if not (current <= start_dt < end_dt <= current + timedelta(days=3660)):
        raise IssuanceError("Invalid issuance validity window")
    destination = Path(output)
    if destination.suffix != ".fvslicense" or not destination.parent.is_dir():
        raise IssuanceError("Output must be a new .fvslicense in an existing folder")

    # No secrets are serialized. Sign exactly the canonical R11 document.
    key = _key_from_encrypted_pem(key_path, password)
    item = {"schema": verifier.SCHEMA, "kid": kid, "product": product,
            "license_id": license_id, "holder": holder, "issued_at": issued,
            "not_before": start, "expires_at": expires_at}
    signature = key.sign(verifier._canonical_payload(item))
    item["signature"] = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    serialized = (json.dumps(item, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    if len(serialized) > verifier.MAX_BYTES:
        raise IssuanceError("Signed entitlement exceeds the verifier size limit")

    # Operator-only O_EXCL output custody: one owned FD, bounded writes,
    # fsync, path/descriptor witness, and no private OS exception chains.
    # Any uncertain/partial file stays reserved for human investigation.
    create_issued_license(destination, serialized, IssuanceError)
    # Verify R11 acceptance against the public key derived from the authority.
    # The verification test clock is start, so future-valid entitlements work.
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
    verifier.verify_license(destination, product, trusted_keys={kid: public_key}, now=start_dt)
    # The receipt comes from the exact serialized signed payload kept in
    # memory. Hashing the file after verification would create a new TOCTOU
    # window in which swapped bytes could become the expected registry hash.
    if return_digest:
        return destination, hashlib.sha256(serialized).hexdigest()
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OFFLINE operator-only entitlement issuance; NOT a storefront")
    parser.add_argument("--key", required=True, help="Owner-only encrypted PKCS#8 Ed25519 PEM path")
    parser.add_argument("--kid", required=True)
    parser.add_argument("--product", required=True, choices=sorted(verifier.PRODUCTS))
    parser.add_argument("--license-id", required=True)
    parser.add_argument("--holder", required=True)
    parser.add_argument("--expires-at", required=True, help="YYYY-MM-DDTHH:MM:SSZ")
    parser.add_argument("--not-before", help="Optional canonical future UTC timestamp")
    parser.add_argument("--output", required=True, help="New .fvslicense path; never overwritten")
    parser.add_argument("--registry", required=True,
                        help="Absolute .sqlite3 registry outside Git, in a protected folder")
    parser.add_argument("--confirm-issue", action="store_true", help="Acknowledge manual fulfillment authorization")
    args = parser.parse_args(argv)
    if not args.confirm_issue:
        parser.error("--confirm-issue required; obtain separate authorization before issuing")
    if not sys.stdin.isatty():
        parser.error("An interactive terminal is required for the private-key passphrase")
    secret = getpass.getpass("Encrypted signing-key passphrase: ").encode("utf-8")
    try:
        registry = IssuanceRegistry(args.registry)
        # Reserve before touching the private key. Failed or uncertain issuance
        # remains reserved; an operator must investigate, never auto-reuse IDs.
        registry.reserve(license_id=args.license_id, product=args.product,
                         kid=args.kid, output=args.output)
        issued, signed_digest = issue_entitlement(key_path=args.key, password=secret, kid=args.kid,
                                   product=args.product, license_id=args.license_id,
                                   holder=args.holder, expires_at=args.expires_at,
                                   not_before=args.not_before, output=args.output,
                                   return_digest=True)
        digest = registry.finalize(license_id=args.license_id, product=args.product,
                                   kid=args.kid, output=issued, expected_sha256=signed_digest)
    except (RegistryError, IssuanceError, verifier.EntitlementError, OSError, ValueError) as exc:
        parser.exit(1, f"Issuance refused (reservation may require manual review): {exc}\n")
    print(f"Entitlement verified and recorded (SHA-256 {digest}). Distribution NOT authorized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
