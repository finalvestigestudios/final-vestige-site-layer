"""Check a GrantAudit inventory against an independently retained SHA-256 pin.

This is an *optional* external trust anchor, not a signature or a substitute
for access-controlled recordkeeping. Never derive the pin from the suspect
package during verification; obtain it from a separately trusted record.
"""
from __future__ import annotations

import hashlib
import hmac
import re

_PIN = re.compile(r"[0-9a-f]{64}\Z")


def verify_inventory_pin(inventory_bytes: bytes, trusted_sha256: str) -> None:
    """Fail closed unless inventory bytes match a canonical independent pin.

    Do not strip whitespace, accept uppercase, convert arbitrary objects or
    echo the provided value: loose normalization can conceal operator errors.
    """
    if (not isinstance(trusted_sha256, str)
            or _PIN.fullmatch(trusted_sha256) is None):
        raise ValueError("Invalid trusted inventory SHA-256 pin")
    if not isinstance(inventory_bytes, bytes):
        raise ValueError("Invalid evidence inventory bytes")
    actual = hashlib.sha256(inventory_bytes).hexdigest()
    if not hmac.compare_digest(actual, trusted_sha256):
        raise ValueError("Trusted inventory SHA-256 pin does not match")
