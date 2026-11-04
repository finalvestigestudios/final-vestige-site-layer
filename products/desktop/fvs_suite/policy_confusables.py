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


def render_local_confusable_evidence(hunks: list[dict]) -> str:
    """Cite uniquely paired substitutions inside the *same* source diff hunk.

    Pairs are navigational hints only. Exact raw text, SHA-256 and human
    judgment decide whether an apparent look-alike matters to a policy.
    """
    found: list[tuple[int, int, int, str]] = []
    for hunk_no, hunk in enumerate(hunks, 1):
        removed: dict[str, list[tuple[int, str]]] = {}
        added: dict[str, list[tuple[int, str]]] = {}
        for rows, groups in ((hunk["removed_sources"], removed),
                             (hunk["added_sources"], added)):
            for line, raw in rows:
                key = _skeleton(raw)
                if key is not None and type(line) is int and line > 0:
                    groups.setdefault(key, []).append((line, raw))
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
