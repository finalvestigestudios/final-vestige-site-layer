"""Fail-closed native input identity for offline premium human-review requests.

A str subclass can override equality or text methods and make a stale report
hash compare equal, forge a review decision, or supply different journal text.
Validate simple, exact Python strings before any such hooks, I/O or locks.
No financial/payment approval is implemented here.
"""
from __future__ import annotations

_HEX = frozenset('0123456789abcdef')


def require_native_choice(value: object, allowed: tuple[str, ...], error: str) -> str:
    """Accept only an exact native string from a fixed internal choice set."""
    if type(value) is not str or value not in allowed:
        raise ValueError(error)
    return value


def require_canonical_digest(value: object) -> str:
    """Accept an exact canonical lower-case SHA-256 text identifier only."""
    if (type(value) is not str or len(value) != 64
            or any(character not in _HEX for character in value)):
        raise ValueError('Review evidence identifier must be canonical lowercase SHA-256')
    return value


def require_native_string(value: object, error: str) -> str:
    """Reject string subclasses without consulting equality, hashing or text hooks."""
    if type(value) is not str:
        raise ValueError(error)
    return value
