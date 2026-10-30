"""Fail-closed state for the human-only premium review workbench.

A failed attempt to open a new report must NEVER leave the previous report's
exceptions and journal actionable under the new selection. No customer data
is uploaded, logged, or persisted by this in-memory controller.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(slots=True)
class ReviewQueue:
    batch: Any = None
    journal: Path | None = None
    report_path: Path | None = None

    def clear(self) -> None:
        """Discard every actionable reference before switching reports."""
        self.batch = None
        self.journal = None
        self.report_path = None

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
        latest_states(journal, batch)
        # No state is published until both validations have completed.
        self.batch = batch
        self.journal = journal
        self.report_path = selected_path
