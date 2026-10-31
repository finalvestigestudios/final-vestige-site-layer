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


def source_document_spellings(documents: Iterable[object]) -> frozenset[str]:
    """Snapshot original source labels, trimming only boundary whitespace.

    The immutable result is deterministic and contains no financial amounts.
    Preserve the existing permissive ``str`` handling of imported CSV cells.
    """
    return frozenset(ascii_case_identity(str(value).strip()) for value in documents)


def has_original_spelling(reference: object, source_spellings: frozenset[str]) -> bool:
    """True only when a linked source label is identical up to ASCII case.

    A false result is a *review flag*, not a rejection of a normalized link.
    The calling engine separately checks that the normalized link exists.
    """
    return ascii_case_identity(str(reference).strip()) in source_spellings
