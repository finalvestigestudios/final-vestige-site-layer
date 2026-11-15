"""Publish complete, private CSV reports without overwriting existing evidence.

CSV rows are staged in a same-directory file so a failed conversion, interrupted
write, or full disk never leaves a misleading partial final report. Final
publication uses exclusive hard-link creation on POSIX and non-replacing rename
on Windows; both fail closed if a destination already exists. This is not an
all-or-nothing transaction for a multi-report package.
"""
from __future__ import annotations

import csv
import errno
import os
import tempfile
from itertools import islice
from pathlib import Path
from typing import Callable, Iterable, Mapping

from .csv_formula_guard import has_unescaped_formula_prefix
from .csv_stage_integrity import CSVStagingWitness
from .csv_publish_guard import adopt_csv_descriptor, private_csv_failure, require_free_destination
from .csv_userdict_custody import verify_userdict_storage


# Application imports already cap source rows at 200,000. The publication API
# must independently bound direct API generators and custom Mapping.items(),
# otherwise an infinite iterator can exhaust memory or fill the output disk.
MAX_REPORT_COLUMNS = 256
MAX_REPORT_ROWS = 200_000
# R214: total final CSV evidence size INCLUDES UTF-8 BOM, separators,
# quoted/escaped text and line endings; no truncation or partial publication.
MAX_REPORT_BYTES = 64 * 1024 * 1024
MAX_REPORT_CELL_CHARS = 1_048_576


class _BudgetedCSVTextSink:
    """Enforce a final on-disk byte budget on csv.writer's serialized output.

    Counting source-cell lengths is unsafe: CSV quoting and UTF-8 encoding can
    expand values. utf-8-sig writes a three-byte BOM at the first write; we
    reserve its exact size even for a header-only export.
    """
    def __init__(self, stream):
        self._stream = stream
        self._remaining = MAX_REPORT_BYTES - len(b"\xef\xbb\xbf")
        self._witness = CSVStagingWitness()

    def write(self, text: str) -> int:
        encoded = text.encode("utf-8")
        encoded_bytes = len(encoded)
        if encoded_bytes > self._remaining:
            raise ValueError("CSV report byte limit exceeded")
        written = self._stream.write(text)
        # A text stream may legally return a short character count. Neither
        # csv.writer nor DictWriter guarantees that such a result aborts the
        # export, so a partial financial report could otherwise be published.
        if type(written) is not int or written != len(text):
            raise OSError(errno.EIO, "CSV report staging incomplete write")
        self._witness.record(encoded)
        self._remaining -= encoded_bytes
        return written

    @staticmethod
    def _excel_field_bytes(value: str) -> int:
        """Exact quoted csv.excel UTF-8 field cost, excluding separators."""
        cost = len(value.encode("utf-8")) + value.count('"')
        if any(char in value for char in ('"', ",", "\r", "\n")):
            cost += 2
        return cost

    def preflight_add(self, value: str, subtotal: int, columns: int) -> int:
        """Reject an impossible row while its cells are still being rendered.

        Reserve delimiters, CRLF, and the singleton empty-field quotation
        regardless of Mapping.items() order. This rejects a row as soon as
        emitted fields exceed its remaining byte budget, rather than creating
        up to 256 potentially escaped 1 MiB strings before preflight().
        Unselected extra columns still pass through _render_cell on success.
        This does not debit the actual stream budget or publish partial data.
        """
        if columns < 1:
            raise ValueError("Invalid CSV report column count")
        subtotal += self._excel_field_bytes(value)
        if columns == 1 and value == "":
            subtotal += 2
        if subtotal + (columns - 1) + 2 > self._remaining:
            raise ValueError("CSV report byte limit exceeded")
        return subtotal

    def preflight(self, values: Iterable[str]) -> None:
        """Bound exact default csv.excel output before writerow allocates it.

        The final check remains independent of the incremental render-time
        guard. Both use the same field-cost calculation; write() still
        independently checks actual bytes and maintains its SHA-256 witness.
        """
        available = self._remaining - 2  # excel's CRLF record terminator
        count = 0
        only_field_empty = False
        for value in values:
            if count:
                available -= 1  # comma between fields
            else:
                only_field_empty = value == ""
            count += 1
            available -= self._excel_field_bytes(value)
            if available < 0:
                raise ValueError("CSV report byte limit exceeded")
        if count == 1 and only_field_empty:
            available -= 2  # csv.writer(['']) -> '""\\r\\n'
        if available < 0:
            raise ValueError("CSV report byte limit exceeded")

    def verify(self, descriptor: int) -> None:
        self._witness.verify(descriptor)


def _render_cell(value: object, cell: Callable[[object], str]) -> str:
    """Demand owned, sanitized text; never let csv.writer coerce unsafe objects.

    The caller's sanitizer still owns its complete escaping policy. This
    additional boundary rejects formulas after whitespace or zero-width marks,
    NUL evidence ambiguity, and
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
    if type(rendered) is str and len(rendered) > MAX_REPORT_CELL_CHARS:
        raise ValueError("CSV report cell size limit exceeded")
    if (type(rendered) is not str or "\x00" in rendered
            or has_unescaped_formula_prefix(rendered)
            or any(0xD800 <= ord(char) <= 0xDFFF for char in rendered)):
        raise ValueError("Unsafe or non-text CSV report cell")
    return rendered


def _write_csv_report(destination: str | Path, fields: Iterable[str],
                     rows: Iterable[Mapping[str, object]],
                     cell: Callable[[object], str]) -> Path:
    """Write UTF-8-BOM CSV and publish only after the entire report is synced.

    ``cell`` must sanitize untrusted spreadsheet content. It is applied to
    every header and row value, including ignored extra columns. Rendered
    header collisions reject the export instead of losing column identity.
    All rendered cells must be plain text without NUL or unescaped formula
    operators after Unicode whitespace and common invisible prefix marks;
    malformed sanitizer output fails closed before publication.
    Missing row keys, forged labels and duplicate row items fail closed;
    explicit empty values remain permitted. Very wide or unbounded iterables
    fail closed before untrusted data can exhaust RAM or fill the disk.
    Cells are limited to 1,048,576 characters and serialized files to 64 MiB
    including BOM and CSV quoting; split larger reports into reviewed batches.
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
        names = tuple(islice(fields, MAX_REPORT_COLUMNS + 1))
    except Exception:
        fields_failed = True
    if fields_failed:
        raise ValueError("CSV report columns could not be read")
    if len(names) > MAX_REPORT_COLUMNS:
        raise ValueError("CSV report column limit exceeded")
    if (not names or any(type(name) is not str or not name for name in names)
            or len(set(names)) != len(names)):
        raise ValueError("Invalid or duplicate CSV report columns")
    rendered = tuple(_render_cell(name, cell) for name in names)
    if (any(type(name) is not str or not name or any(c in name for c in "\x00\r\n")
            for name in rendered) or len(set(rendered)) != len(rendered)):
        # Two distinct input labels may collapse to one visible label after
        # spreadsheet-formula neutralization; never publish ambiguous evidence.
        raise ValueError("Unsafe or ambiguous CSV report columns")
    # Reject occupied destinations (including dangling symlinks) without
    # writing an unnecessary private staging file. Publication is still
    # exclusive and protects against concurrent destination creation.
    require_free_destination(target)
    descriptor, temporary = tempfile.mkstemp(
        prefix=".fvs-csv-", suffix=".partial", dir=target.parent)
    try:
        with adopt_csv_descriptor(descriptor) as stream:
            sink = _BudgetedCSVTextSink(stream)
            writer = csv.DictWriter(sink, fieldnames=names, extrasaction="ignore")
            # Bound the header before csv.writer allocates its serialized row.
            sink.preflight(rendered)
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
            count = 0
            emitted_columns = frozenset(names)
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
                count += 1
                if count > MAX_REPORT_ROWS:
                    raise ValueError("CSV report row limit exceeded")
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
                    # A dict subclass can override .items() to fabricate
                    # financial evidence or hide unsafe extra values. Read the
                    # actual built-in dict storage, never its virtual view.
                    # Other Mapping implementations retain the R217 validated
                    # pair boundary (UserDict and mappingproxy remain valid).
                    source_items = dict.items(row) if isinstance(row, dict) else row.items()
                    entries = tuple(islice(source_items, MAX_REPORT_COLUMNS + 1))
                except Exception:
                    items_failed = True
                if items_failed:
                    raise ValueError("CSV report row columns could not be read")
                if len(entries) > MAX_REPORT_COLUMNS:
                    raise ValueError("CSV report row column limit exceeded")
                # Mapping.items() is user-controlled for direct API callers.
                # Require actual two-field tuple pairs before unpacking; a
                # tuple subclass or arbitrary iterable can execute a forged
                # __iter__ or leak private data through an exception context.
                # Native dict/UserDict/MappingProxyType items all meet this.
                if any(type(entry) is not tuple or len(entry) != 2 for entry in entries):
                    raise ValueError("Invalid or duplicate CSV report row columns")
                if (any(type(name) is not str for name, _ in entries)
                        or len({name for name, _ in entries}) != len(entries)):
                    raise ValueError("Invalid or duplicate CSV report row columns")
                # Native backing custody: a UserDict subclass must not supply
                # a plausible but forged .items() view of financial evidence.
                # Retain R217 pair validation before checking the backing dict.
                entries = verify_userdict_storage(row, entries, MAX_REPORT_COLUMNS)
                # Reject oversized output before constructing all rendered
                # cells. The final whole-row preflight and byte witness remain
                # authoritative. Incomplete/invalid input still fails closed.
                rendered_row = {}
                subtotal = 0
                for name, value in entries:
                    rendered_value = _render_cell(value, cell)
                    if name in emitted_columns:
                        subtotal = sink.preflight_add(rendered_value, subtotal, len(names))
                    rendered_row[name] = rendered_value
                if any(name not in rendered_row for name in names):
                    raise ValueError("Incomplete CSV report row schema")
                # Only emitted columns count toward the final file budget;
                # ignored extras were still sanitized above for safety.
                sink.preflight(rendered_row[name] for name in names)
                writer.writerow(rendered_row)
            stream.flush()
            # Prove the real staged bytes match the exact serialized CSV
            # stream (including BOM), not merely the accepted write counts.
            sink.verify(stream.fileno())
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


def write_csv_report(destination: str | Path, fields: Iterable[str],
                     rows: Iterable[Mapping[str, object]],
                     cell: Callable[[object], str]) -> Path:
    """Publish an offline financial CSV without leaking client paths in OS errors.

    Preserve the original deterministic CSV writer, financial byte witness,
    source-row validation and exclusive no-overwrite semantics. Filesystem
    failures are displayed with fixed text; caller input errors still fail.
    """
    sanitized_error = None
    try:
        return _write_csv_report(destination, fields, rows, cell)
    except OSError as exc:
        sanitized_error = private_csv_failure(exc)
    # The filesystem exception must be out of scope before raising: `from None`
    # hides tracebacks but leaves financial paths readable via __context__.
    if sanitized_error is None:
        raise RuntimeError("CSV report internal publication state invalid")
    raise sanitized_error
