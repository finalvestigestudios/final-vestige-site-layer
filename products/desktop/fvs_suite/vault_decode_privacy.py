"""Private error boundaries for authentic, locally encrypted evidence archives.

Ciphertext is untrusted even after authentication: a malformed but legitimately
sealed payload can contain private financial records in JSON parser errors.
Raise only fixed diagnostics *after* the source exception handler exits, since
``raise ... from None`` inside ``except`` leaves a reachable ``__context__``.
No network access, telemetry, compliance decisions or financial arithmetic.
"""
from __future__ import annotations

import base64
import binascii
import json
from typing import Callable

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def decrypt_evidence(key: bytes, nonce: bytes, ciphertext: bytes, prefix: bytes) -> bytes:
    """Authenticate ciphertext without retaining an InvalidTag exception."""
    invalid = False
    try:
        clear = AESGCM(key).decrypt(nonce, ciphertext, prefix)
    except InvalidTag:
        invalid = True
    if invalid:
        raise ValueError("Wrong passphrase or encrypted archive was altered")
    return clear


def parse_evidence_json(clear: bytes, unique_pairs: Callable) -> object:
    """Parse authenticated UTF-8 JSON without leaking plaintext in exceptions.

    In particular JSONDecodeError.doc and UnicodeDecodeError.object contain
    the input contents. Caller-provided unique_pairs is an internal trusted
    strict duplicate-key checker; its domain-level ValueError is preserved.
    """
    invalid = False
    try:
        payload = json.loads(
            clear.decode("utf-8"), object_pairs_hook=unique_pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Invalid JSON constant")),
        )
    except (UnicodeError, json.JSONDecodeError):
        invalid = True
    if invalid:
        raise ValueError("Encrypted evidence has invalid JSON")
    return payload


def decode_evidence_b64(value: object) -> bytes:
    """Decode one archive member without retaining untrusted encoded evidence."""
    invalid = False
    try:
        result = base64.b64decode(value, validate=True)
    except (ValueError, TypeError, binascii.Error):
        invalid = True
    if invalid:
        raise ValueError("Malformed encrypted evidence bytes")
    return result
