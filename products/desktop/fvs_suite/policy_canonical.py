"""Bounded NFC-only edit navigation for Policy Delta Desk.

Inputs are source-owned unified-diff hunk records, not legal clauses. The
exact source text and byte hashes remain the authority for any human review.
"""
from __future__ import annotations

import unicodedata


# Metadata must remain bounded even when a private policy line contains a
# large range of different Unicode characters. No raw policy text is emitted.
_MAX_DISTINCT_NONASCII = 64
_MAX_CODEPOINT_CUES = 12
_MAX_SOURCE_LINE = 50_000  # Matches the policy file reader's physical-line cap.
_MAX_NAV_LINE_CHARS = 4096  # Skip long evidence navigation; original diff remains.


def _nonascii_counts(text: str) -> dict[int, int] | None:
    counts: dict[int, int] = {}
    for character in text:
        point = ord(character)
        if point < 128:
            continue
        if point not in counts and len(counts) == _MAX_DISTINCT_NONASCII:
            return None
        counts[point] = counts.get(point, 0) + 1
    return counts


def _canonical_codepoint_cue(before: str, after: str) -> str:
    """Provide accessible numeric Unicode evidence, never private source text.

    Equal codepoint counts are possible after reordered combining marks.
    Report that explicitly instead of suggesting nothing changed.
    """
    old, new = _nonascii_counts(before), _nonascii_counts(after)
    if old is None or new is None:
        return "non-ASCII detail withheld (over 64 distinct source codepoints)"
    different = sorted(point for point in old.keys() | new.keys()
                       if old.get(point, 0) != new.get(point, 0))
    if not different:
        return "non-ASCII counts unchanged; inspect codepoint order"
    shown = ", ".join(f"U+{point:04X} {old.get(point, 0)}->{new.get(point, 0)}"
                      for point in different[:_MAX_CODEPOINT_CUES])
    omitted = len(different) - _MAX_CODEPOINT_CUES
    return ("non-ASCII codepoint counts " + shown +
            (f" (+{omitted} omitted)" if omitted > 0 else ""))



def _verified_canonical_hunks(hunks: list[dict]) -> list[tuple[int, dict, dict]] | None:
    """Snapshot exact source primitives; reject contradictory physical citations.

    A direct Python caller must not be able to create apparent source-owned
    coordinates via virtual dict/list methods, duplicate rows, or backward
    physical order. Scan all rows, including those too long to annotate,
    before emitting a single supplemental cue.
    """
    if type(hunks) is not list or len(hunks) > _MAX_SOURCE_LINE:
        return None
    staged = []
    last_before = last_after = 0
    for hunk_no, hunk in enumerate(hunks, 1):
        if type(hunk) is not dict:
            return None
        sides = []
        for name, checkpoint in (("removed_sources", last_before),
                                 ("added_sources", last_after)):
            rows = hunk.get(name)
            if type(rows) is not list:
                return None
            grouped: dict[str, list[tuple[int, str]]] = {}
            last_line = checkpoint
            for row in rows:
                if type(row) is not tuple or len(row) != 2:
                    return None
                line, raw = row
                if (type(line) is not int or not 1 <= line <= _MAX_SOURCE_LINE
                        or type(raw) is not str or line <= last_line):
                    return None
                last_line = line
                if len(raw) <= _MAX_NAV_LINE_CHARS:
                    normalized = unicodedata.normalize("NFC", raw)
                    grouped.setdefault(normalized, []).append((line, raw))
            sides.append((grouped, last_line))
        removed, last_before = sides[0]
        added, last_after = sides[1]
        staged.append((hunk_no, removed, added))
    return staged


def render_local_canonical_evidence(hunks: list[dict]) -> str:
    """Cite unique NFC-equivalent *changed* lines within each existing hunk.

    Do not pair ambiguous duplicates, compare across distinct hunks, or
    interpret Unicode normalization as semantic/legal equivalence. This is
    deliberately an index over already-computed physical diff coordinates.
    """
    staged = _verified_canonical_hunks(hunks)
    if staged is None:
        return ""  # Never emit partial or contradictory source citations.
    candidates: list[tuple[int, int, int, str, str]] = []
    for hunk_number, removed, added in staged:
        for normalized in removed.keys() & added.keys():
            old_group, new_group = removed[normalized], added[normalized]
            if len(old_group) != 1 or len(new_group) != 1:
                continue  # No defensible one-to-one physical source citation.
            old_number, old_raw = old_group[0]
            new_number, new_raw = new_group[0]
            if old_raw != new_raw:
                candidates.append((hunk_number, old_number, new_number, old_raw, new_raw))
    if not candidates:
        return ""
    candidates.sort(key=lambda row: (row[0], row[1], row[2]))
    result = [
        "LOCAL REVIEW: NFC-only canonical Unicode changes at cited physical "
        "source lines, including mixed revisions. These are navigation cues, "
        "NOT legal or semantic equivalence; inspect both original files. "
        "Ambiguous duplicate lines are intentionally not paired.\n"
    ]
    for hunk, before, after, old_raw, new_raw in candidates[:16]:
        result.append(
            f"Canonical hunk {hunk:03d}: before L{before}; after L{after}; "
            "NFC-only candidate; " + _canonical_codepoint_cue(old_raw, new_raw) +
            "; human review.\n"
        )
    if len(candidates) > 16:
        result.append(
            f"LOCAL REVIEW: +{len(candidates) - 16} additional canonical "
            "candidate pair(s) omitted from bounded navigation.\n"
        )
    return "".join(result) + "\n"
