"""Fail-closed snapshot of ProcureGuard's direct-API price review policy.

Policy thresholds and evidence hashes are reviewer-facing input, not permission
for automated approval. Own native fields before calling user-provided parsers;
never invoke foreign getters, comparisons or string conversions to validate a
policy. Return only immutable, bounded Python primitives.
"""
from __future__ import annotations

import re
from decimal import Decimal

_FIELD_NAMES = frozenset(("absolute", "fraction", "source_sha256"))
_SHA256_HEX = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
_MAX_ABSOLUTE = Decimal("100.00")
_MAX_FRACTION = Decimal("0.10")
_POLICY_ERROR = "Procurement review requires a native bounded price policy"


def _bounded_threshold(value: object, maximum: Decimal) -> bool:
    """Check finite, unsigned, fixed-point values without Decimal arithmetic."""
    if type(value) is not Decimal or not value.is_finite() or value.is_signed():
        return False
    # Reject huge coefficients/exponents before formatting or exporting.
    digits = value.as_tuple().digits
    exponent = value.as_tuple().exponent
    if len(digits) > 16 or not -8 <= exponent <= 8:
        return False
    return value <= maximum


def snapshot_price_policy(policy: object, policy_class: type) -> tuple[Decimal, Decimal, str]:
    """Validate and snapshot *stored* PricePolicy fields before any callbacks.

    The caller must provide the real PricePolicy class, never a caller-supplied
    type. The returned tuple is used to construct a fresh frozen policy, so a
    parsing callback cannot mutate thresholds or report fingerprint mid-review.
    Error messages deliberately contain no customer values or filesystem paths.
    """
    if type(policy) is not policy_class:
        raise ValueError(_POLICY_ERROR)
    try:
        stored = object.__getattribute__(policy, "__dict__")
    except AttributeError:
        raise ValueError(_POLICY_ERROR) from None
    if type(stored) is not dict or set(stored) != _FIELD_NAMES:
        raise ValueError(_POLICY_ERROR)
    absolute = dict.__getitem__(stored, "absolute")
    fraction = dict.__getitem__(stored, "fraction")
    source_hash = dict.__getitem__(stored, "source_sha256")
    if (not _bounded_threshold(absolute, _MAX_ABSOLUTE)
            or not _bounded_threshold(fraction, _MAX_FRACTION)
            or type(source_hash) is not str
            or _SHA256_HEX.fullmatch(source_hash) is None):
        raise ValueError(_POLICY_ERROR)
    return absolute, fraction, source_hash
