"""Bounded, source-fingerprinted, local-only policy text comparison.

A policy diff shows textual changes; it never decides legal compliance.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from .unicode_hazards import is_visually_blank_filler

MAX_POLICY_BYTES = 10 * 1024 * 1024
MAX_POLICY_LINES = 50_000
_ALLOWED_EXTENSIONS = frozenset((".txt", ".md", ".csv"))
# Unsafe controls can forge visual report structure or conceal changes.
_UNSAFE_TEXT = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\u2028\u2029\u202a-\u202e\u2066-\u2069]")


def _read_policy(path):
    source = Path(path)
    if source.suffix.lower() not in _ALLOWED_EXTENSIONS or not source.is_file():
        raise ValueError("Policy comparison supports existing TXT, MD and CSV files")
    # Reuse the suite's descriptor-owned, bounded and identity-checked snapshot
    # guard rather than trusting a pathname that can be swapped during reading.
    from .csv_snapshot import read_csv_snapshot
    try:
        raw = read_csv_snapshot(source, MAX_POLICY_BYTES)
    except ValueError as exc:
        if "exceeds" in str(exc):
            raise ValueError("Policy file exceeds 10 MiB input limit") from None
        raise ValueError("Policy input is not a stable regular file (links or concurrent changes are not accepted)") from None
    if b"\x00" in raw:
        raise ValueError("Policy input contains a NUL byte")
    try:
        body = raw.decode("utf-8-sig")
    except UnicodeError as exc:
        raise ValueError("Policy input must be valid UTF-8 text") from exc
    if _UNSAFE_TEXT.search(body) or "\ufeff" in body:
        raise ValueError("Policy input contains unsupported control characters")
    lines = body.splitlines(keepends=True)
    if len(lines) > MAX_POLICY_LINES:
        raise ValueError("Policy file exceeds 50,000 physical lines")
    return lines, hashlib.sha256(raw).hexdigest(), json.dumps(source.name, ensure_ascii=True)


def _visible_source_char(character: str) -> str:
    """Display invisible formats, combining marks, variations and spaces.

    Unlike JSON-encoding whole lines, this keeps readable Unicode readable
    while making default-hidden typography explicit. Existing backslash-first
    escaping prevents literal \\uXXXX text from imitating an escaped character.
    """
    if character == "\\":
        return "\\\\"
    if character == "\t":
        return "\\t"
    if character == "\r":
        return "\\r"
    codepoint = ord(character)
    category = unicodedata.category(character)
    if (category in ("Cf", "Mn", "Me")
            # Nonspacing/enclosing marks can disguise canonically equivalent
            # edits (e.g. precomposed é versus e + U+0301) in a rendered diff.
            # Escape codepoints only in the display; never alter source bytes.
            # Non-ASCII Unicode spacing separators can be visually identical
            # to an ordinary source space while changing the audited bytes.
            or (category == "Zs" and character != " ")
            or is_visually_blank_filler(character)  # Non-control blank glyphs
            or codepoint == 0x034F  # Combining Grapheme Joiner
            or 0x180B <= codepoint <= 0x180F  # Mongolian variation selectors
            or 0xFE00 <= codepoint <= 0xFE0F
            or 0xE0100 <= codepoint <= 0xE01EF):
        if codepoint <= 0xFFFF:
            return f"\\u{codepoint:04x}"
        return f"\\U{codepoint:08x}"
    return character


_HUNK_HEADER = re.compile(
    r"^@@ -([0-9]+)(?:,[0-9]+)? \+([0-9]+)(?:,[0-9]+)? @@(?: .*)?$"
)


def _render_change_index(hunks):
    """Render navigation only; never interpret a text edit as a legal decision."""
    deleted = sum(hunk["deleted"] for hunk in hunks)
    inserted = sum(hunk["inserted"] for hunk in hunks)
    lines = [
        f"Change index: {len(hunks)} diff hunk(s); "
        f"{deleted} removed source line(s); {inserted} added source line(s).\n",
        "Line citations identify changed physical source lines, not legal clauses. "
        "A touched range can contain unchanged lines between edits.\n",
    ]
    if not hunks:
        lines.append("No changed source lines to index.\n")
    for number, hunk in enumerate(hunks, 1):
        def cite(first, last):
            if first is None:
                return "none"
            return f"L{first}" if first == last else f"L{first}-L{last}"
        classification = (
            "mixed removal/addition" if hunk["deleted"] and hunk["inserted"]
            else "addition only" if hunk["inserted"] else "removal only"
        )
        lines.append(
            f"Hunk {number:03d}: before {cite(hunk['first_old'], hunk['last_old'])}; "
            f"after {cite(hunk['first_new'], hunk['last_new'])}; "
            f"-{hunk['deleted']} +{hunk['inserted']}; {classification}; human review.\n"
        )
    return "".join(lines) + "\n"


def _unified_diff(before, after, old_label, new_label, *, include_index=False):
    """Build a source-safe unified diff and an optional exact-line change index.

    Both derive from one difflib stream, so index positions cannot drift from
    the actual hunk coordinates. Unchanged context is never counted as a
    removal or addition. No second quadratic diff pass is introduced.
    """
    chunks = []
    hunks = []
    current = None
    old_cursor = new_cursor = 0
    for index, fragment in enumerate(difflib.unified_diff(
        before, after, fromfile="before " + old_label,
        tofile="after " + new_label, lineterm="\n",
    )):
        # The first two records are diff headers; @@ records are hunk metadata.
        # Escape only source lines (prefix +, - or space). Preserve original
        # line breaks and diff metadata; untrusted typography cannot masquerade
        # as unchanged source when viewed in a text editor or audit register.
        if index >= 2 and fragment.startswith("@@ "):
            match = _HUNK_HEADER.fullmatch(fragment.rstrip("\n"))
            if match is None:
                raise ValueError("Unexpected policy diff hunk format")
            if current is not None:
                hunks.append(current)
            old_cursor, new_cursor = int(match.group(1)), int(match.group(2))
            current = dict(first_old=None, last_old=None, first_new=None,
                           last_new=None, deleted=0, inserted=0,
                           removed_sources=[], added_sources=[])
        elif index >= 2 and current is not None:
            prefix = fragment[:1]
            if prefix == "-":
                if current["first_old"] is None:
                    current["first_old"] = old_cursor
                current["last_old"] = old_cursor
                current["deleted"] += 1
                current["removed_sources"].append((old_cursor, fragment[1:]))
                old_cursor += 1
            elif prefix == "+":
                if current["first_new"] is None:
                    current["first_new"] = new_cursor
                current["last_new"] = new_cursor
                current["inserted"] += 1
                current["added_sources"].append((new_cursor, fragment[1:]))
                new_cursor += 1
            elif prefix == " ":
                old_cursor += 1
                new_cursor += 1
        display = fragment
        if index >= 2 and not fragment.startswith("@@ "):
            display = fragment[0] + "".join(
                _visible_source_char(character) for character in fragment[1:])
        if fragment.endswith("\n"):
            chunks.append(display)
        elif fragment.endswith("\r"):
            # A CR-only source line still has an ending; delimit the report line.
            chunks.append(display + "\n")
        else:
            # difflib otherwise concatenates changed final unterminated lines.
            chunks.append(display + "\n\\ No newline at end of file\n")
    if current is not None:
        hunks.append(current)
    rendered = "".join(chunks)
    return (rendered, _render_change_index(hunks) +
            _local_compatibility_evidence(hunks)) if include_index else rendered


def _compatibility_codepoint_evidence(before_text: str, after_text: str) -> str:
    """Bounded codepoint navigation, not a claim that characters mean the same.

    Count only characters whose NFKC differs from their NFC form, so an
    ordinary canonical accent is never mislabeled as a compatibility edit.
    This executes only if the entire source texts are NFKC-equal but not
    NFC-equal; input is already size bounded by the policy reader.
    """
    def counts(text):
        found = {}
        for character in text:
            if unicodedata.normalize("NFKC", character) != unicodedata.normalize("NFC", character):
                codepoint = ord(character)
                found[codepoint] = found.get(codepoint, 0) + 1
        return found

    old_counts, new_counts = counts(before_text), counts(after_text)
    changed = sorted(cp for cp in old_counts.keys() | new_counts.keys()
                     if old_counts.get(cp, 0) != new_counts.get(cp, 0))
    if not changed:
        return ("Compatibility-sensitive codepoint totals did not change; "
                "inspect ordering and exact physical diff lines.\n")
    shown = ", ".join(f"U+{cp:04X}" for cp in changed[:16])
    omitted = len(changed) - 16
    remainder = f" (+{omitted} more)" if omitted else ""
    return ("Compatibility-sensitive codepoints with changed source counts "
            f"(at most 16 shown): {shown}{remainder}.\n")


def _local_compatibility_evidence(hunks) -> str:
    """Bounded, physically cited NFKC-only line candidates inside diff hunks.

    A whole-document NFKC comparison can miss a compatibility substitution
    when another policy sentence changes. Only pair UNIQUE removed/added
    source lines within the same existing unified-diff hunk, where NFKC is
    equal but NFC is not. Never claim that the pair is legally equivalent.
    Report line numbers and bounded codepoints, not extra raw policy content.
    """
    matches = []
    for number, hunk in enumerate(hunks, 1):
        removed, added = {}, {}
        for line, value in hunk["removed_sources"]:
            removed.setdefault(unicodedata.normalize("NFKC", value), []).append((line, value))
        for line, value in hunk["added_sources"]:
            added.setdefault(unicodedata.normalize("NFKC", value), []).append((line, value))
        for normalized in removed.keys() & added.keys():
            before_group, after_group = removed[normalized], added[normalized]
            # Duplicate normalized lines make a one-to-one citation ambiguous.
            if len(before_group) != 1 or len(after_group) != 1:
                continue
            old_line, old_text = before_group[0]
            new_line, new_text = after_group[0]
            if old_text == new_text or (
                    unicodedata.normalize("NFC", old_text) ==
                    unicodedata.normalize("NFC", new_text)):
                continue
            evidence = _compatibility_codepoint_evidence(old_text, new_text).strip()
            matches.append((number, old_line, new_line, evidence))
    if not matches:
        return ""
    matches.sort(key=lambda row: (row[0], row[1], row[2]))
    lines = [
        "LOCAL REVIEW: NFKC-only source-line substitution candidate(s) inside "
        "changed diff hunks, including mixed policy revisions. These are "
        "navigation cues, NOT legal or semantic equivalence; inspect the "
        "original files and exact cited lines. Ambiguous duplicate lines "
        "are intentionally not paired.\n"
    ]
    for number, old_line, new_line, evidence in matches[:16]:
        lines.append(
            f"Local hunk {number:03d}: before L{old_line}; after L{new_line}; "
            f"NFKC-only candidate; {evidence}\n")
    if len(matches) > 16:
        lines.append(f"LOCAL REVIEW: +{len(matches) - 16} additional unique "
                     "candidate pair(s) omitted from bounded navigation.\n")
    return "".join(lines) + "\n"


def compare_policy_files(old, new, folder, output_path):
    """Write one deterministic, provenance-rich report after both inputs pass.

    output_path must have the existing outpath(folder, stem, suffix) signature.
    A failed input check creates no report and changes neither original file.
    """
    before, before_hash, before_name = _read_policy(old)
    after, after_hash, after_name = _read_policy(new)
    delta, change_index = _unified_diff(
        before, after, before_name, after_name, include_index=True)
    identity_note = (
        "REVIEW: Both source files have identical bytes; confirm that two intended versions were selected.\n"
        if before_hash == after_hash else
        "REVIEW: Source bytes differ but decoded text is identical; verify encoding/BOM or line-ending changes.\n"
        if not delta else ""
    )
    # A raw-codepoint revision can look identical after Unicode NFC
    # composition. This is a navigation cue, not a legal equivalence claim;
    # the escaped diff and independent source fingerprints remain authoritative.
    before_text, after_text = "".join(before), "".join(after)
    nfc_equal = bool(delta) and (
        unicodedata.normalize("NFC", before_text) ==
        unicodedata.normalize("NFC", after_text))
    normalization_note = (
        "REVIEW: Text differs at Unicode codepoint level but is NFC-normalization-equivalent; inspect escaped combining marks and both original files.\n"
        if nfc_equal else ""
    )
    # Compatibility normalization can collapse materially different symbols:
    # fullwidth forms, superscripts, circled numbers, styled letters and
    # ligatures. Keep this separate from canonical NFC equivalence, flag it
    # only when WHOLE raw source texts fold equally, and never infer policy
    # equivalence, fraud, or compliance.
    compatibility_note = (
        "REVIEW: Text differs and is NFKC-compatibility-equivalent ONLY "
        "(not NFC-equivalent). Compatibility folding may collapse distinct "
        "symbols, quantities or typography; this is NOT legal or semantic "
        "equivalence. Inspect the original files and cited physical lines.\n"
        + _compatibility_codepoint_evidence(before_text, after_text)
        if delta and not nfc_equal and
           unicodedata.normalize("NFKC", before_text) ==
           unicodedata.normalize("NFKC", after_text) else ""
    )
    report = (
        "Text differences only. Not legal advice or a compliance determination.\n"
        "SHA-256 fingerprints cover the exact source bytes read (including any BOM).\n"
        "Diff display escapes source backslash as \\\\, tab as \\t and CR as \\r.\n"
        "Invisible Unicode format and variation characters display as \\uXXXX or \\UXXXXXXXX.\n"
        "Non-ASCII Unicode spacing separators display as \\uXXXX (ordinary spaces remain unchanged).\n"
        "Unicode blank filler glyphs display as \\uXXXX; raw files remain authoritative.\n"
        "Unicode nonspacing/enclosing combining marks display as \\uXXXX or \\UXXXXXXXX.\n"
        + identity_note + normalization_note + compatibility_note +
        f"Before: {before_name} | SHA-256: {before_hash} | lines: {len(before)}\n"
        f"After: {after_name} | SHA-256: {after_hash} | lines: {len(after)}\n\n"
        + change_index
        + (delta or "No textual differences found.\n")
    )
    from .atomic_text import publish_text
    destination = output_path(folder, "policy-delta", ".txt")
    return [publish_text(destination, report)]
