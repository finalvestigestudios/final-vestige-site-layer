"""Fail-closed physical-source custody for local NFKC review navigation.

The result is an optional human-review index, never a policy equivalence or
compliance judgment. Only direct, native Python data from the bounded source
differ may supply citations; no source text or paths are logged.
"""
from __future__ import annotations

import unicodedata

_MAX_SOURCE_LINE = 50_000
_MAX_SOURCE_CHARS = 10 * 1024 * 1024  # At most 10 MiB UTF-8 input per side.
_MAX_NAV_LINE_CHARS = 4096


def owned_nfkc_hunks(hunks: list[dict]) -> list[tuple[int, dict, dict]] | None:
    """Validate all physical rows before returning any NFKC candidate groups.

    Reject non-native mappings/keys/containers, forged coordinates, and
    backward or repeated physical lines across hunks. Skip overlong but valid
    lines for *navigation only*, while still checking their source coordinates.
    The original exact text/byte-hash evidence is never normalized or edited.
    """
    if type(hunks) is not list or len(hunks) > _MAX_SOURCE_LINE:
        return None
    staged = []
    last_before = last_after = 0
    chars_before = chars_after = 0
    for number, hunk in enumerate(hunks, 1):
        if type(hunk) is not dict:
            return None
        # Validate even unused keys BEFORE a field lookup. Hash-colliding
        # Python objects must not trigger caller-defined equality callbacks.
        if any(type(key) is not str for key in hunk):
            return None
        sides = []
        for name, last, total in (
            ("removed_sources", last_before, chars_before),
            ("added_sources", last_after, chars_after),
        ):
            rows = hunk.get(name)
            if type(rows) is not list:
                return None
            grouped: dict[str, list[tuple[int, str]]] = {}
            for row in rows:
                if type(row) is not tuple or len(row) != 2:
                    return None
                physical, source = row
                if (type(physical) is not int or not last < physical <= _MAX_SOURCE_LINE
                        or type(source) is not str):
                    return None
                last = physical
                total += len(source)
                if total > _MAX_SOURCE_CHARS:
                    return None
                if len(source) <= _MAX_NAV_LINE_CHARS:
                    key = unicodedata.normalize("NFKC", source)
                    grouped.setdefault(key, []).append((physical, source))
            sides.append((grouped, last, total))
        removed, last_before, chars_before = sides[0]
        added, last_after, chars_after = sides[1]
        staged.append((number, removed, added))
    return staged
