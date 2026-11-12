"""Bound untrusted direct-call Policy Delta look-alike navigation inputs.

This optional human-review aid must not allocate enormous skeleton indexes
from a caller-supplied hunk collection. It does not validate source custody:
physical coordinates and original-file SHA evidence are handled elsewhere.
"""
from __future__ import annotations

MAX_HUNKS = 50_000
MAX_SOURCE_ROWS = 100_000  # Both sides combined, inclusive.
MAX_TEXT_CODEPOINTS = 8 * 1024 * 1024  # Both sides combined, inclusive.


def within_confusable_budget(hunks: object) -> bool:
    """Reject oversized or unsafe source collections before skeletonization.

    Counts *all* source rows and original text, including lines too long to
    display and records that ultimately do not match. Uses exact built-in
    types so a hostile subclass cannot run an iterator or equality callback.
    No source content is copied, formatted, returned, logged, or mutated.
    """
    if type(hunks) is not list or len(hunks) > MAX_HUNKS:
        return False
    rows_seen = 0
    chars_seen = 0
    for hunk in hunks:
        if type(hunk) is not dict or any(type(key) is not str for key in hunk):
            return False
        for field in ("removed_sources", "added_sources"):
            rows = hunk.get(field)
            if type(rows) is not list or len(rows) > MAX_SOURCE_ROWS - rows_seen:
                return False
            rows_seen += len(rows)
            for row in rows:
                if type(row) is not tuple or len(row) != 2:
                    return False
                line, raw = row
                if type(line) is not int or type(raw) is not str:
                    return False
                # Check the remainder before adding: even a single giant raw
                # string is rejected without creating a second large string.
                if len(raw) > MAX_TEXT_CODEPOINTS - chars_seen:
                    return False
                chars_seen += len(raw)
    return True
