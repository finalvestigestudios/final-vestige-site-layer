"""Bounded, source-fingerprinted, local-only policy text comparison.

A policy diff shows textual changes; it never decides legal compliance.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
from pathlib import Path

MAX_POLICY_BYTES = 10 * 1024 * 1024
MAX_POLICY_LINES = 50_000
_ALLOWED_EXTENSIONS = frozenset((".txt", ".md", ".csv"))
# Unsafe controls can forge visual report structure or conceal changes.
_UNSAFE_TEXT = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\u2028\u2029\u202a-\u202e\u2066-\u2069]")


def _read_policy(path):
    source = Path(path)
    if source.suffix.lower() not in _ALLOWED_EXTENSIONS or not source.is_file():
        raise ValueError("Policy comparison supports existing TXT, MD and CSV files")
    try:
        # Read from one opened descriptor, not an earlier stat of the pathname.
        with source.open("rb") as stream:
            if os.fstat(stream.fileno()).st_size > MAX_POLICY_BYTES:
                raise ValueError("Policy file exceeds 10 MiB input limit")
            raw = stream.read(MAX_POLICY_BYTES + 1)
    except OSError as exc:
        raise ValueError("Unable to read policy input") from exc
    if len(raw) > MAX_POLICY_BYTES:
        raise ValueError("Policy file exceeds 10 MiB input limit")
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


def _unified_diff(before, after, old_label, new_label):
    chunks = []
    for fragment in difflib.unified_diff(
        before, after, fromfile="before " + old_label,
        tofile="after " + new_label, lineterm="\n",
    ):
        if fragment.endswith("\n"):
            chunks.append(fragment)
        elif fragment.endswith("\r"):
            # A CR-only source line still has an ending; delimit the report line.
            chunks.append(fragment + "\n")
        else:
            # difflib otherwise concatenates changed final unterminated lines.
            chunks.append(fragment + "\n\\ No newline at end of file\n")
    return "".join(chunks)


def compare_policy_files(old, new, folder, output_path):
    """Write one deterministic, provenance-rich report after both inputs pass.

    output_path must have the existing outpath(folder, stem, suffix) signature.
    A failed input check creates no report and changes neither original file.
    """
    before, before_hash, before_name = _read_policy(old)
    after, after_hash, after_name = _read_policy(new)
    delta = _unified_diff(before, after, before_name, after_name)
    report = (
        "Text differences only. Not legal advice or a compliance determination.\n"
        "SHA-256 fingerprints cover the exact source bytes read (including any BOM).\n"
        f"Before: {before_name} | SHA-256: {before_hash} | lines: {len(before)}\n"
        f"After: {after_name} | SHA-256: {after_hash} | lines: {len(after)}\n\n"
        + (delta or "No textual differences found.\n")
    )
    destination = output_path(folder, "policy-delta", ".txt")
    with destination.open("x", encoding="utf-8", newline="") as stream:
        stream.write(report)
    return [destination]
