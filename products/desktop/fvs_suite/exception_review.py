"""Offline, human-only exception review for the two premium desktop prototypes.

This module NEVER authorizes spending, determines eligibility, or silently clears
an exception. The hash-linked journal detects accidental edits but is NOT a
cryptographic signature, an access-control boundary, or encrypted-at-rest.
"""
from __future__ import annotations

import csv
import hashlib
import hmac
import io
import json
import os
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .journal_io import append_verified_event, read_regular_bytes
from .review_identity_gate_r419 import (
    require_native_choice, require_canonical_digest, require_native_string,
)
from .review_line_framing_r324 import canonical_review_records
from .review_commit import confirm_review_commit
from .review_lock import exclusive_review_lock
from .review_chronology import check_new_review_clock, check_record_order, parse_review_utc
from .unicode_hazards import is_visually_blank_filler

MAX_REPORT_BYTES = 64 * 1024 * 1024
MAX_JOURNAL_BYTES = 16 * 1024 * 1024
MAX_RECORDS = 200_000
MAX_EVENTS = 20_000
DECISIONS = ("needs_evidence", "escalated", "reviewed")
ZERO_HASH = "0" * 64
FIELDS = (
    "schema", "product", "report_sha256", "case_id", "report_row",
    "flags", "decision", "reviewer", "rationale", "created_utc", "previous_hash",
)
CSV_FIELDS = (
    "case_id", "source_row", "source_key", "original_flags", "review_state",
    "reviewer", "rationale", "reviewed_utc", "report_sha256",
)


@dataclass(frozen=True)
class ExceptionCase:
    case_id: str
    report_row: int
    source_key: str
    flags: str


@dataclass(frozen=True)
class ReportBatch:
    product: str
    report_sha256: str
    cases: tuple[ExceptionCase, ...]


def _hex_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _unique_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Repeated JSON journal key")
        value[key] = item
    return value


def _read_file(path: str | Path, limit: int, kind: str) -> bytes:
    # Descriptor and pathname must still match after the bounded read.
    try:
        return read_regular_bytes(path, limit, kind)
    except FileNotFoundError:
        pass
    # Translate AFTER the originating handler: 'from None' inside an except
    # still retains the private OS exception in __context__.
    raise ValueError(f"{kind} must be an existing regular file, not a symlink")


def read_cases(report: str | Path, product: str) -> ReportBatch:
    """Bind reviews to exact bytes and physical CSV source lines; reject malformed rows."""
    product = require_native_choice(
        product, ("grants", "procurement"),
        "Only premium grant/procurement exception reports are supported")
    source = Path(report)
    if source.suffix.lower() != ".csv":
        raise ValueError("The exception report must be a CSV file")
    data = _read_file(source, MAX_REPORT_BYTES, "Exception report")
    digest = _hex_hash(data)
    try:
        decoded = data.decode("utf-8-sig")
    except UnicodeError:
        decoded = None
    # UnicodeDecodeError.object can contain the ENTIRE financial input buffer.
    # Do not retain it through a chained exception for callers or loggers.
    if decoded is None:
        raise ValueError("Exception report must be UTF-8 CSV")
    if "\x00" in decoded:
        raise ValueError("Exception report contains a NUL character")
    reader = csv.reader(io.StringIO(decoded, newline=""), strict=True)
    malformed_header = False
    try:
        fieldnames = next(reader, None)
    except csv.Error:
        malformed_header = True
    if malformed_header:
        raise ValueError("Exception report contains a malformed CSV header")
    if not fieldnames:
        raise ValueError("Exception report has no CSV headers")
    names = [str(h).strip().lower().replace(" ", "_") for h in fieldnames]
    if any(not n for n in names) or len(names) != len(set(names)):
        raise ValueError("Exception report has blank or duplicate CSV headers")
    required = {"status", "id"} if product == "grants" else {"status", "po", "line"}
    if not required.issubset(set(names)):
        raise ValueError("Report is missing the expected premium exception columns")
    col = dict(zip(names, fieldnames))
    cases = []
    records = 0
    previous_end_line = reader.line_num
    try:
        for values in reader:
            # CSV's physical line_num advances across quoted embedded newlines.
            physical_line = previous_end_line + 1
            previous_end_line = reader.line_num
            if not values:  # Keep csv.DictReader's historical blank-line behavior.
                continue
            records += 1
            if records > MAX_RECORDS:
                raise ValueError("Exception report exceeds the row limit")
            if len(values) != len(fieldnames):
                raise ValueError(f"Malformed CSV record at physical line {physical_line}: "
                                 f"expected {len(fieldnames)} columns, got {len(values)}")
            row = dict(zip(fieldnames, values))
            status = str(row.get(col["status"]) or "").strip()
            if not status:
                raise ValueError(f"Missing status in report record at physical line {physical_line}")
            key = (str(row.get(col["id"]) or "").strip() if product == "grants"
                   else f"{str(row.get(col['po']) or '').strip()} / {str(row.get(col['line']) or '').strip()}")
            if (product == "grants" and not str(row.get(col["id"]) or "").strip()) or (
                product == "procurement" and (
                    not str(row.get(col["po"]) or "").strip()
                    or not str(row.get(col["line"]) or "").strip()
                )
            ):
                raise ValueError(f"Missing identifier in report record at physical line {physical_line}")
            if status == "matched":
                continue
            # The journal is bound to a file hash and the *physical* record line.
            case_id = _hex_hash(f"FVS-CASE-v1|{product}|{digest}|{physical_line}".encode("ascii"))
            cases.append(ExceptionCase(case_id, physical_line, key, status))
    except csv.Error:
        malformed_line = reader.line_num
    else:
        malformed_line = None
    if malformed_line is not None:
        raise ValueError(f"Malformed CSV quoting near physical line {malformed_line}")
    return ReportBatch(product, digest, tuple(cases))


def _unsafe_review_character(character: str) -> bool:
    """Reject invisible text that could spoof a human's audit identity or note.

    Keep readable multilingual letters and combining accents. Reject Unicode
    controls, directional formatting, surrogate halves, hidden grapheme
    joiners, and variation selectors without normalizing accepted text.
    """
    codepoint = ord(character)
    return (
        unicodedata.category(character) in ("Cc", "Cf", "Cs", "Zl", "Zp")
        or codepoint == 0x034F  # Combining Grapheme Joiner (invisible Mn).
        or 0x180B <= codepoint <= 0x180F  # Mongolian variation selectors.
        or 0xFE00 <= codepoint <= 0xFE0F
        or 0xE0100 <= codepoint <= 0xE01EF
        or is_visually_blank_filler(character)
    )


def _text(value: str, name: str, minimum: int, maximum: int) -> str:
    # Only native text may enter a hash-linked human-review journal. A str
    # subclass can override iteration, strip or other text hooks and fabricate
    # a different reviewer identity or rationale after validation.
    if type(value) is not str:
        raise ValueError(f"{name} must be text")
    # Inspect the caller's original text before trimming. str.strip() removes
    # C0/C1 controls and Unicode line separators at either edge, which would
    # otherwise bypass the audit-journal prohibition on hidden formatting.
    if any(_unsafe_review_character(character) for character in value):
        raise ValueError(f"{name} cannot contain hidden or control Unicode characters")
    result = value.strip()
    if len(result) < minimum or len(result) > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum} characters")
    return result


def _validate_event(event: dict, batch: ReportBatch, cases: dict, previous: str) -> str:
    if not isinstance(event, dict) or set(event) != set(FIELDS) | {"event_hash"}:
        raise ValueError("Unrecognized review journal event schema")
    if type(event["schema"]) is not int or event["schema"] != 1:
        raise ValueError("Unsupported review journal schema")
    if event["product"] != batch.product or event["report_sha256"] != batch.report_sha256:
        raise ValueError("Review journal belongs to a different report snapshot")
    if not isinstance(event["case_id"], str):
        raise ValueError("Review event case identifier is not text")
    case = cases.get(event["case_id"])
    if case is None or type(event["report_row"]) is not int or case.report_row != event["report_row"]:
        raise ValueError("Review event references an unknown exception")
    if case.flags != event["flags"]:
        raise ValueError("Review event flags do not match the source report")
    if event["decision"] not in DECISIONS:
        raise ValueError("Unsupported review decision")
    _text(event["reviewer"], "Reviewer", 2, 80)
    _text(event["rationale"], "Rationale", 12, 2000)
    # One strict, lossless UTC syntax/precision guard for both premium apps.
    # Never retain a customer-derived timestamp or parser exception in a chain.
    parse_review_utc(event["created_utc"])
    if event["previous_hash"] != previous:
        raise ValueError("Review journal chain broken or reordered")
    payload = {name: event[name] for name in FIELDS}
    expected = _hex_hash(_json(payload))
    value = event["event_hash"]
    if not isinstance(value, str) or not hmac.compare_digest(expected, value):
        raise ValueError("Review journal hash mismatch; refuse further writes")
    return expected


def read_journal(journal: str | Path, batch: ReportBatch) -> list[dict]:
    """Verify all known events against the current report and preceding hashes."""
    path = Path(journal)
    if not path.exists() and not path.is_symlink():
        return []
    data = _read_file(path, MAX_JOURNAL_BYTES, "Review journal")
    if data and not data.endswith(b"\n"):
        raise ValueError("Review journal has an incomplete final record")
    cases = {case.case_id: case for case in batch.cases}
    result = []
    previous = ZERO_HASH
    prior_timestamp = None
    for line_number, line in enumerate(canonical_review_records(data), 1):
        if line_number > MAX_EVENTS:
            raise ValueError("Review journal exceeds maximum recorded events")
        if not line:
            raise ValueError("Review journal contains an empty record")
        malformed_event = False
        try:
            event = json.loads(line.decode("utf-8"), object_pairs_hook=_unique_keys,
                               parse_constant=lambda raw: (_ for _ in ()).throw(
                                   ValueError(f"Invalid JSON constant: {raw}")))
        except (UnicodeError, json.JSONDecodeError):
            malformed_event = True
        # JSONDecodeError.doc retains the raw untrusted record.  Do not keep
        # that record in an exception cause/context returned to UI callers.
        if malformed_event:
            raise ValueError(f"Malformed review journal record {line_number}")
        previous = _validate_event(event, batch, cases, previous)
        # A valid SHA chain alone must not normalize backdated review events.
        prior_timestamp = check_record_order(prior_timestamp, event["created_utc"])
        result.append(event)
    return result



def append_review(report: str | Path, product: str, journal: str | Path, *,
                  case_id: str, expected_report_sha256: str, reviewer: str,
                  decision: str, rationale: str) -> dict:
    """Append a reviewer action; no automatic status changes or authorization."""
    # Preflight direct API inputs before invoking user-defined equality,
    # entering a file lock or reading any report. A forged str subclass must
    # never bypass the caller\'s exact source-snapshot selection.
    product = require_native_choice(
        product, ("grants", "procurement"),
        "Only premium grant/procurement exception reports are supported")
    decision = require_native_choice(
        decision, DECISIONS,
        "Decision must be needs_evidence, escalated, or reviewed")
    case_id = require_native_string(case_id, "Review case identifier must be native text")
    expected_report_sha256 = require_canonical_digest(expected_report_sha256)
    reviewer = _text(reviewer, "Reviewer", 2, 80)
    rationale = _text(rationale, "Rationale", 12, 2000)
    path = Path(journal)
    source = Path(report)
    if path.resolve() == source.resolve() or path.suffix.lower() != ".jsonl":
        raise ValueError("Choose a separate .jsonl review journal, not the source report")
    if not path.parent.is_dir():
        raise ValueError("Review journal parent folder does not exist")
    with exclusive_review_lock(path) as assert_lock_owned:
        batch = read_cases(report, product)
        if batch.report_sha256 != expected_report_sha256:
            raise ValueError("Source report changed since it was opened; reload before reviewing")
        cases = {case.case_id: case for case in batch.cases}
        if case_id not in cases:
            raise ValueError("Unknown or already-matched exception; no review was recorded")
        events = read_journal(path, batch)
        if len(events) >= MAX_EVENTS:
            raise ValueError("Review journal event limit reached; export and archive it")
        # Human decisions cannot be recorded earlier than the prior action.
        # A clock rollback requires inspection, never an automatic timestamp fix.
        # Match the exact second precision persisted in the journal, so a
        # preceding fractional-second record cannot slip past the clock gate.
        now = datetime.now(timezone.utc).replace(microsecond=0)
        check_new_review_clock(events[-1]["created_utc"] if events else None, now)
        case = cases[case_id]
        payload = {
            "schema": 1, "product": product, "report_sha256": batch.report_sha256,
            "case_id": case_id, "report_row": case.report_row, "flags": case.flags,
            "decision": decision, "reviewer": reviewer, "rationale": rationale,
            "created_utc": now.isoformat(timespec="seconds"),
            "previous_hash": events[-1]["event_hash"] if events else ZERO_HASH,
        }
        event = {**payload, "event_hash": _hex_hash(_json(payload))}
        encoded = _json(event) + b"\n"
        # Recheck the whole source and hash-linked journal while holding the
        # destination descriptor; never append to a substituted pathname.
        def verify_source_and_history():
            assert_lock_owned()
            closing = read_cases(report, product)
            if closing != batch or read_journal(path, closing) != events:
                raise ValueError("Review evidence changed before append; reload source and journal")
            assert_lock_owned()

        assert_lock_owned()
        append_verified_event(path, encoded, MAX_JOURNAL_BYTES, verify_source_and_history)
        # fsync alone cannot certify the human's decision was retained.
        # Re-parse the entire source-bound journal; if ambiguous, require
        # inspection rather than returning a false success/auto-retrying.
        confirm_review_commit(
            report, product, path,
            expected_batch=batch, previous_events=events, expected_event=event,
            assert_lock_owned=assert_lock_owned,
            read_cases=read_cases, read_journal=read_journal,
        )
        return event


def latest_states(journal: str | Path, batch: ReportBatch) -> dict[str, dict]:
    state = {}
    for event in read_journal(journal, batch):
        state[event["case_id"]] = event
    return state


def _csv_cell(value: object) -> str:
    data = str(value)
    if data.lstrip().startswith(("=", "+", "-", "@", "\t", "\r", "\n")):
        return "'" + data
    return data


def export_register(report: str | Path, product: str, journal: str | Path,
                    folder: str | Path, *,
                    expected_report_sha256: str | None = None) -> Path:
    """Atomically publish a register only if report and full journal stay stable.

    Every review is a human record, never spending or eligibility approval.
    Original report/journal remain untouched; an observed evidence change
    prevents a stale or partially written CSV from being published.
    """
    from .review_register import publish_review_register
    return publish_review_register(
        report, product, journal, folder,
        read_cases=read_cases, read_journal=read_journal,
        columns=CSV_FIELDS, cell=_csv_cell,
        expected_report_sha256=expected_report_sha256)
