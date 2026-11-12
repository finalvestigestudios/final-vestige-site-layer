"""Select bounded, reproducible NFKC-only policy review citations.

Receives source-custody-validated groups from ``owned_nfkc_hunks``. Never
normalizes original evidence in place or decides legal equivalence.
"""
from __future__ import annotations

from bisect import insort
import unicodedata

MAX_REVIEW_PAIRS = 16


def earliest_nfkc_pairs(
    staged: list[tuple[int, dict, dict]], limit: int = MAX_REVIEW_PAIRS,
) -> tuple[list[tuple[int, int, int, str, str]], int]:
    """Count every unique NFC-distinct pair; retain earliest ``limit`` only.

    The upstream custody validator guarantees strictly increasing, unique
    physical coordinates across hunks and a finite source-byte budget. The
    set intersection can visit keys in hash-dependent order, so selection
    must sort by source coordinates, not discovery order. Only retained pairs
    carry source text to the final (local-only) codepoint formatter.
    """
    selected: list[tuple[int, int, int, str, str]] = []
    total = 0
    for hunk_no, removed, added in staged:
        for normalized in removed.keys() & added.keys():
            previous, following = removed[normalized], added[normalized]
            if len(previous) != 1 or len(following) != 1:
                continue  # Repeated folded lines are ambiguous.
            old_line, old_text = previous[0]
            new_line, new_text = following[0]
            if old_text == new_text or (
                unicodedata.normalize("NFC", old_text) ==
                unicodedata.normalize("NFC", new_text)
            ):
                continue
            total += 1
            coordinates = (hunk_no, old_line, new_line)
            if limit <= 0 or (len(selected) == limit and
                              coordinates >= selected[-1][:3]):
                continue
            insort(selected, (*coordinates, old_text, new_text))
            if len(selected) > limit:
                selected.pop()
    return selected, total
