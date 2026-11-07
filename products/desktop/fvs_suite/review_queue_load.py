"""Fail-closed state for the human-only premium review workbench.

A failed attempt to open a new report must NEVER leave the previous report's
exceptions and journal actionable under the new selection. No customer data
is uploaded, logged, or persisted by this in-memory controller.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .review_identity import journal_snapshot_identity


@dataclass(slots=True)
class ReviewQueue:
    batch: Any = None
    journal: Path | None = None
    report_path: Path | None = None
    journal_identity: str | None = None

    def clear(self) -> None:
        """Discard every actionable reference before switching reports."""
        self.batch = None
        self.journal = None
        self.report_path = None
        self.journal_identity = None

    def load(
        self,
        path: str | Path,
        product: str,
        read_cases: Callable[[Path, str], Any],
        latest_states: Callable[[Path, Any], object],
    ) -> None:
        """Commit a new review queue only after both evidence checks succeed.

        Validation callbacks retain full responsibility for verifying report
        contents, journal history, and product-specific access rules. A failed
        load leaves no prior batch, journal or report location actionable.
        """
        self.clear()
        if product not in ("grants", "procurement"):
            raise ValueError("Review queue requires a premium product")
        if not isinstance(path, (str, Path)) or not str(path).strip():
            raise ValueError("Select a premium exception report")
        selected_path = Path(path)
        batch = read_cases(selected_path, product)
        if batch is None:
            raise ValueError("Premium report validation returned no review batch")
        journal = selected_path.with_suffix(".review.jsonl")
        before = journal_snapshot_identity(journal)
        latest_states(journal, batch)
        after = journal_snapshot_identity(journal)
        if before != after:
            raise ValueError("Review journal changed while opening; reopen the report")
        # No state is published until both validations have completed.
        self.batch = batch
        self.journal = journal
        self.report_path = selected_path
        self.journal_identity = after

    def verify_current(
        self,
        product: str,
        read_cases: Callable[[Path, str], Any],
        latest_states: Callable[[Path, Any], object],
    ) -> Any:
        """Revalidate the displayed source and journal before a human action.

        Clear *all* actionable references if the source or journal changed,
        vanished, or verification raised any exception (including interrupts). This complements operation-specific
        checks that must run again immediately before output publication.
        """
        verified = False
        try:
            if (self.batch is None or self.journal is None or self.report_path is None
                    or self.journal_identity is None):
                raise ValueError("No verified premium report is selected")
            if product not in ("grants", "procurement"):
                raise ValueError("Review queue requires a premium product")
            current = read_cases(self.report_path, product)
            if current is None or current != self.batch:
                raise ValueError("Loaded source report changed; reopen before acting")
            before = journal_snapshot_identity(self.journal)
            if before != self.journal_identity:
                raise ValueError("Review journal changed since opening; reopen before acting")
            latest_states(self.journal, current)
            after = journal_snapshot_identity(self.journal)
            if after != before:
                raise ValueError("Review journal changed during validation; reopen before acting")
            verified = True
            return current
        finally:
            # Clear even for unexpected verifier bugs or interrupted validation.
            # Never leave a stale financial review selected after *any* failure.
            if not verified:
                self.clear()
