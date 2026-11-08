"""Single-flight custody for report-generation and human-review UI commands.

Tk's nested modal event loops can dispatch another button command before the
first finishes. The same gate is shared between Generate and premium Review,
so neither can re-enter or overlap the other's report/review workflow.
No paths, financial values, exceptions or approvals are retained or logged.
"""
from __future__ import annotations

from collections.abc import Callable


class ActionGate:
    """Reject overlapping commands; always unlock after success or failure."""

    def __init__(self) -> None:
        self._active = False

    def run(self, command: Callable[[], object]) -> bool:
        """Execute once, return False if already busy; never queue an action."""
        if self._active:
            return False
        self._active = True
        try:
            command()
        finally:
            self._active = False
        return True
