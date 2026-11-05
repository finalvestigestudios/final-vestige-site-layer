"""Conservative, bounded cross-script look-alike navigation in policy diffs.

Not a Unicode confusables database, language detector, fraud flag, or legal
interpretation. Original source bytes and cited diff lines are authoritative.
"""
from __future__ import annotations

import unicodedata

# Deliberately small, visually close single-codepoint substitutes. Map only
# to ASCII Latin, not to NFKC/NFC or to a language-dependent transliteration.
_TO_LATIN = {
    "А": "A", "а": "a", "В": "B", "Е": "E", "е": "e", "К": "K",
    "М": "M", "Н": "H", "О": "O", "о": "o", "Р": "P", "р": "p",
    "С": "C", "с": "c", "Т": "T", "Х": "X", "х": "x", "У": "Y",
    "І": "I", "і": "i", "Ј": "J", "ј": "j",  # Cyrillic
    "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I",
    "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P", "Τ": "T",
    "Υ": "Y", "Χ": "X", "ο": "o", "ρ": "p",  # Greek
}
_MAX_LINE_CHARS = 4096
_MAX_PAIRS = 16
_MAX_GLYPHS = 8
# Exactly mirrors Policy Delta Desk's reader limit. Only source-owned
# physical line positions may be cited, never forged or ambiguous identities.
_MAX_SOURCE_LINE = 50_000


def _skeleton(raw: str) -> str | None:
    if type(raw) is not str or len(raw) > _MAX_LINE_CHARS:
        return None
    return "".join(_TO_LATIN.get(character, character) for character in raw)


def _changes(before: str, after: str) -> str:
    # Caller already established equal one-to-one skeletons, but defend the
    # low-level function against accidental use with arbitrary source lines.
    if (type(before) is not str or type(after) is not str or
            len(before) != len(after) or _skeleton(before) is None or
            _skeleton(before) != _skeleton(after) or before == after):
        return ""
    changes = [(position, ord(old), ord(new)) for position, (old, new)
               in enumerate(zip(before, after), 1) if old != new]
    if not changes:
        return ""
    # Unicode's assigned character names give screen-reader reviewers an
    # unambiguous script/letter cue without repeating private source text.
    # Only pre-existing, bounded substitutions are labeled. Assigned names
    # for these mapped ASCII/Greek/Cyrillic characters are stable.
    shown = ", ".join(
        f"column {position} U+{old:04X}->U+{new:04X} "
        f"[{unicodedata.name(chr(old))} -> {unicodedata.name(chr(new))}]"
        for position, old, new in changes[:_MAX_GLYPHS]
    )
    omitted = len(changes) - _MAX_GLYPHS
    return shown + (f" (+{omitted} substitution(s) omitted)" if omitted > 0 else "")


def _owned_rows(
    hunk: dict, field: str,
) -> tuple[dict[str, list[tuple[int, str]]], tuple[int, int] | None] | None:
    """Index only unambiguous physical source rows from the canonical diff.

    Direct helper callers must not supply a fabricated line identity, an
    iterable with side effects, or two source texts claiming the same physical
    line. A malformed side invalidates the entire hunk rather than permitting
    a misleading before/after citation from its remaining rows. Long *valid*
    source lines are skipped without suppressing other independent candidates.
    """
    if type(hunk) is not dict:
        return None
    # An exact dict may still contain attacker-controlled key objects. Inspect
    # stored key types BEFORE looking up either source field: a colliding key
    # could otherwise run custom __eq__ or masquerade as report metadata.
    # Iterating the exact dict uses native storage, not overridden callbacks.
    if any(type(key) is not str for key in hunk):
        return None
    rows = hunk.get(field)
    if type(rows) is not list:
        return None
    grouped: dict[str, list[tuple[int, str]]] = {}
    # Actual unified-diff records occur in strictly increasing physical order.
    # Include even overlong (uncitable) rows in this validation so a malicious
    # direct API caller cannot hide a duplicate behind the display bound.
    first: int | None = None
    previous = 0
    for row in rows:
        if type(row) is not tuple or len(row) != 2:
            return None
        line, raw = row
        if (type(line) is not int or not 1 <= line <= _MAX_SOURCE_LINE
                or type(raw) is not str or line <= previous):
            return None
        if first is None:
            first = line
        previous = line
        key = _skeleton(raw)
        if key is not None:
            grouped.setdefault(key, []).append((line, raw))
    return grouped, ((first, previous) if first is not None else None)


def render_local_confusable_evidence(hunks: list[dict]) -> str:
    """Cite uniquely paired substitutions inside the *same* source diff hunk.

    Pairs are navigational hints only. Exact raw text, SHA-256 and human
    judgment decide whether an apparent look-alike matters to a policy.
    """
    if type(hunks) is not list or len(hunks) > _MAX_SOURCE_LINE:
        return ""
    # Validate *all* well-formed hunks before emitting a single citation.
    # Reusing a physical source coordinate in a later hunk, or presenting
    # backward-moving hunks, otherwise lets distinct text borrow a seemingly
    # authoritative citation from an earlier hunk. A collision invalidates
    # navigation globally; partial evidence would still mislead a reviewer.
    staged = []
    last_before = last_after = 0
    for hunk_no, hunk in enumerate(hunks, 1):
        removed_result = _owned_rows(hunk, "removed_sources")
        added_result = _owned_rows(hunk, "added_sources")
        if removed_result is None or added_result is None:
            continue  # A locally malformed hunk has no navigational cues.
        removed, before_span = removed_result
        added, after_span = added_result
        if ((before_span is not None and before_span[0] <= last_before)
                or (after_span is not None and after_span[0] <= last_after)):
            return ""  # Cross-hunk coordinate collision or reversal.
        if before_span is not None:
            last_before = before_span[1]
        if after_span is not None:
            last_after = after_span[1]
        staged.append((hunk_no, removed, added))
    found: list[tuple[int, int, int, str]] = []
    for hunk_no, removed, added in staged:
        for key in removed.keys() & added.keys():
            prior, following = removed[key], added[key]
            if len(prior) != 1 or len(following) != 1:
                continue  # A duplicated look-alike has no unique citation.
            old_line, old_text = prior[0]
            new_line, new_text = following[0]
            cue = _changes(old_text, new_text)
            if cue:
                found.append((hunk_no, old_line, new_line, cue))
    if not found:
        return ""
    found.sort(key=lambda item: (item[0], item[1], item[2]))
    output = [
        "LOCAL REVIEW: possible cross-script look-alike letter substitutions "
        "at cited physical lines. Limited Latin/Cyrillic/Greek character "
        "list only; this is NOT a comprehensive confusable scan, evidence of "
        "intent, or a legal/compliance determination. Review the original "
        "files and exact source bytes; ambiguous duplicates are not paired.\n"
    ]
    for hunk, before, after, cue in found[:_MAX_PAIRS]:
        output.append(f"Look-alike hunk {hunk:03d}: before L{before}; "
                      f"after L{after}; {cue}; human review.\n")
    if len(found) > _MAX_PAIRS:
        output.append(f"LOCAL REVIEW: +{len(found) - _MAX_PAIRS} additional "
                      "look-alike pair(s) omitted from bounded navigation.\n")
    return "".join(output) + "\n"
