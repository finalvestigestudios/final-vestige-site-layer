"""Publish complete, private CSV reports without overwriting existing evidence.

CSV rows are staged in a same-directory file so a failed conversion, interrupted
write, or full disk never leaves a misleading partial final report. Final
publication uses exclusive hard-link creation on POSIX and non-replacing rename
on Windows; both fail closed if a destination already exists. This is not an
all-or-nothing transaction for a multi-report package.
"""
from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path
from typing import Callable, Iterable, Mapping


def _render_cell(value: object, cell: Callable[[object], str]) -> str:
    """Demand owned, sanitized text; never let csv.writer coerce unsafe objects.

    The caller's sanitizer still owns the full invisible-prefix policy. This
    additional boundary blocks blatant formulas, NUL evidence ambiguity, and
    implicit conversion of None, bytes, numbers or crafted string subclasses.
    """
    # Direct API callbacks can fail with financial values in their exception
    # text. Do not let a converter's private payload surface as a UI/CI error.
    failed = False
    try:
        rendered = cell(value)
    except Exception:
        failed = True
    # Raise outside the except block: `from None` hides display context but
    # leaves a private exception reachable via __context__ and debug tools.
    if failed:
        raise ValueError("CSV report cell sanitizer failed") from None
    # Python str admits isolated UTF-16 surrogate code points, but UTF-8
    # reports cannot encode them. Reject before csv/TextIOWrapper can raise
    # a UnicodeEncodeError carrying user-controlled report text.
    if (type(rendered) is not str or "\x00" in rendered
            or rendered.startswith(("=", "+", "@"))
            or any(0xD800 <= ord(char) <= 0xDFFF for char in rendered)):
        raise ValueError("Unsafe or non-text CSV report cell")
    return rendered


def write_csv_report(destination: str | Path, fields: Iterable[str],
                     rows: Iterable[Mapping[str, object]],
                     cell: Callable[[object], str]) -> Path:
    """Write UTF-8-BOM CSV and publish only after the entire report is synced.

    ``cell`` must sanitize untrusted spreadsheet content. It is applied to
    every header and row value, including ignored extra columns. Rendered
    header collisions reject the export instead of losing column identity.
    All rendered cells must be plain text without NUL or bare formula prefixes;
    malformed sanitizer output fails closed before publication.
    Missing row keys, forged labels and duplicate row items fail closed;
    explicit empty values remain permitted.
    Nothing ever overwrites an existing destination or follows its symlink.
    On a filesystem lacking the required safe publication operation, fail
    rather than silently fall back to an overwriting move.
    """
    target = Path(destination)
    if not target.parent.is_dir():
        raise ValueError("Choose an existing output folder")
    # Source-derived field labels are spreadsheet cells too. Freeze the
    # schema and sanitize it before creating even a temporary report; a
    # formula in a header must never bypass the caller's safe_cell policy.
    # A caller-owned fields iterator may throw an error containing a source
    # heading or customer identifier. Never chain its private exception.
    fields_failed = False
    try:
        names = tuple(fields)
    except Exception:
        fields_failed = True
    if fields_failed:
        raise ValueError("CSV report columns could not be read")
    if (not names or any(type(name) is not str or not name for name in names)
            or len(set(names)) != len(names)):
        raise ValueError("Invalid or duplicate CSV report columns")
    rendered = tuple(_render_cell(name, cell) for name in names)
    if (any(type(name) is not str or not name or any(c in name for c in "\x00\r\n")
            for name in rendered) or len(set(rendered)) != len(rendered)):
        # Two distinct input labels may collapse to one visible label after
        # spreadsheet-formula neutralization; never publish ambiguous evidence.
        raise ValueError("Unsafe or ambiguous CSV report columns")
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{target.stem}-", suffix=".partial", dir=target.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=names, extrasaction="ignore")
            writer.writer.writerow(rendered)
            # Explicit next() isolates arbitrary caller-owned iterator errors
            # from the writer's own exceptions, including their __context__.
            iterator_failed = False
            try:
                row_iterator = iter(rows)
            except Exception:
                iterator_failed = True
            if iterator_failed:
                raise ValueError("CSV report rows could not be read")
            while True:
                next_failed = False
                try:
                    row = next(row_iterator)
                except StopIteration:
                    break
                except Exception:
                    next_failed = True
                if next_failed:
                    raise ValueError("CSV report rows could not be read")
                # DictWriter would silently substitute an empty cell for
                # absent keys, disguising missing financial/source evidence.
                # Sanitize *all* supplied values, including ignored extras,
                # before demanding an explicit value for every schema field.
                # Freeze real mapping items before rendering. A crafted str
                # subclass may compare equal to a required audit key without
                # actually being that key; duplicate custom mapping entries
                # can also erase one evidence value when coerced into a dict.
                if not isinstance(row, Mapping):
                    raise ValueError("Invalid CSV report row mapping")
                items_failed = False
                try:
                    entries = tuple(row.items())
                except Exception:
                    items_failed = True
                if items_failed:
                    raise ValueError("CSV report row columns could not be read")
                if (any(type(name) is not str for name, _ in entries)
                        or len({name for name, _ in entries}) != len(entries)):
                    raise ValueError("Invalid or duplicate CSV report row columns")
                rendered_row = {
                    name: _render_cell(value, cell) for name, value in entries
                }
                if any(name not in rendered_row for name in names):
                    raise ValueError("Incomplete CSV report row schema")
                writer.writerow(rendered_row)
            stream.flush()
            os.fsync(stream.fileno())
        if os.name == "nt":
            # Windows os.rename never replaces an existing destination.
            os.rename(temporary, target)
        else:
            # POSIX rename can overwrite; a hard link is exclusive and atomic.
            os.link(temporary, target)
            os.unlink(temporary)
        return target
    finally:
        # Failed writes and rejected destinations never leave partial reports.
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
