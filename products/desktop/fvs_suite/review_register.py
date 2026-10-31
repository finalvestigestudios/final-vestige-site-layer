"""Atomic, snapshot-consistent human-review register export (pre-release).

Never decides eligibility, approves a payment, or uploads customer evidence.
The exporter must not publish a report built from a source/journal that changed
while the CSV was being written. This is *observed* consistency, not a signed
historical attestation against privileged rollback or concurrent post-check edits.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .atomic_reports import write_csv_report
from .review_identity import require_snapshot_match
from .audit_display import visible_source_text


def publish_review_register(report, product, journal, folder, *, read_cases: Callable,
                            read_journal: Callable, columns: tuple[str, ...],
                            cell: Callable[[object], str],
                            expected_report_sha256: str | None = None) -> Path:
    """Stage a CSV and revalidate complete input snapshots before publication.

    ``read_cases`` / ``read_journal`` are the premium review validators, passed
    in to avoid a circular module import. The row iterator performs its final
    check before the atomic writer can publish the staged file. An observed
    change fails without creating a final CSV or replacing an older export.
    """
    batch = read_cases(report, product)
    require_snapshot_match(expected_report_sha256, batch.report_sha256)
    events = read_journal(journal, batch)
    states = {event["case_id"]: event for event in events}
    target = Path(folder)
    if not target.is_dir():
        raise ValueError("Choose an existing output folder")
    destination = target / ("review-register-" + datetime.now(timezone.utc).strftime(
        "%Y%m%d-%H%M%S-%f") + ".csv")

    def records():
        for case in batch.cases:
            latest = states.get(case.case_id, {})
            yield {
                "case_id": case.case_id,
                "source_row": case.report_row,
                # Human-display-only values; exact raw strings remain bound
                # to the original report SHA-256 and journal evidence.
                "source_key": visible_source_text(case.source_key),
                "original_flags": visible_source_text(case.flags),
                "review_state": latest.get("decision", "pending"),
                "reviewer": latest.get("reviewer", ""),
                "rationale": latest.get("rationale", ""),
                "reviewed_utc": latest.get("created_utc", ""),
                "report_sha256": batch.report_sha256,
            }
        # Must run after the final row has been consumed, BEFORE atomic rename.
        # Compare the entire journal history, not just the latest per-case state.
        closing = read_cases(report, product)
        require_snapshot_match(expected_report_sha256, closing.report_sha256)
        if closing != batch or read_journal(journal, closing) != events:
            raise ValueError("Review evidence changed during register export; retry from fresh evidence")

    return write_csv_report(destination, columns, records(), cell)
