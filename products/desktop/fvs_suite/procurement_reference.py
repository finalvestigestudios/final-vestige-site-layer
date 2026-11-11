"""Conservative source-document identity checks for procurement offsets.

This module does NOT decide whether a credit or return is valid. The matching
engine first identifies candidate source documents using its documented lossy
key, and this additional check flags references with different original
spellings for a human reviewer. Comparisons ignore ASCII case only; Unicode
case folding must not silently equate independent financial identifiers.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from decimal import localcontext

from .review import ascii_case_identity

_MAX_NATIVE_INT_BITS = 269
_ERROR = "Procurement document identity must be native text or a bounded integer"
_KEY_ERROR = "Procurement document normalization requires a native text key"


def _native_document_text(value: object) -> str:
    """Forbid caller-defined conversion hooks in source identity evidence.

    Existing numeric import compatibility applies only to native integers.
    The finite bit cap prevents enormous integer conversion or digit-limit
    failures; bool, arbitrary objects, and str/int subclasses are not IDs.
    """
    if type(value) is str:
        return value
    if type(value) is int and value.bit_length() <= _MAX_NATIVE_INT_BITS:
        return str(value)
    raise ValueError(_ERROR)


def normalized_document_key(value: object, identifier: Callable[[str], str]) -> str:
    """Validate original identity *before* invoking the lossy match callback.

    Only plain source text reaches the injected normalizer. An unexpected
    callback exception or forged output must not expose customer paths or
    create an attacker-controlled dictionary key. This is a candidate key,
    never proof of invoice/receipt identity or approval.
    """
    text = _native_document_text(value)
    try:
        # User-defined matching callbacks must not change the precision,
        # rounding, traps or status flags of subsequent financial review.
        # This isolates both getcontext() mutation and setcontext() swaps.
        with localcontext():
            result = identifier(text)
    except Exception:
        raise ValueError(_KEY_ERROR) from None
    if type(result) is not str:
        raise ValueError(_KEY_ERROR)
    return result


def source_document_spellings(documents: Iterable[object]) -> frozenset[str]:
    """Snapshot source labels with only ASCII-case and boundary-space changes.

    A direct caller cannot forge a reference via an overridden ``__str__``;
    ordinary CSV text and small native integer cells preserve prior behavior.
    The immutable result is deterministic, with no financial amounts or paths.
    """
    return frozenset(ascii_case_identity(_native_document_text(value).strip())
                     for value in documents)


def has_original_spelling(reference: object, source_spellings: frozenset[str]) -> bool:
    """True only for a genuine original label, ignoring ASCII case.

    Do not invoke untrusted equality hooks in a forged source collection.
    False means human review, not an automatic compliance or payment decision.
    """
    if (type(source_spellings) is not frozenset
            or any(type(value) is not str for value in source_spellings)):
        raise ValueError("Procurement original labels must be a plain text snapshot")
    return ascii_case_identity(_native_document_text(reference).strip()) in source_spellings
