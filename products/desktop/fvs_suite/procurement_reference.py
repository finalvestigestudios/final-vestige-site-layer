"""Conservative source-document identity checks for procurement offsets.

This module does NOT decide whether a credit or return is valid. The matching
engine first identifies candidate source documents using its documented lossy
key, and this additional check flags references with different original
spellings for a human reviewer. Comparisons ignore ASCII case only; Unicode
case folding must not silently equate independent financial identifiers.
"""
from __future__ import annotations

from collections.abc import Iterable

from .review import ascii_case_identity

_MAX_NATIVE_INT_BITS = 269
_ERROR = "Procurement document identity must be native text or a bounded integer"


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
