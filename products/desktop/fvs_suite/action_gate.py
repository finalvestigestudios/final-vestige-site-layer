"""Single-flight custody for report-generation and human-review UI commands.

Nested Tk modal loops and future worker-thread entrypoints must never start
concurrent report or review actions. The same per-window gate is shared by
Generate and premium Review. Rejected calls are never queued; no financial
values, paths, exceptions, or approval decisions are retained or logged.
"""
from __future__ import annotations

from collections.abc import Callable
from threading import Lock


class ActionGate:
    """Reject concurrent or reentrant commands without blocking their caller."""

    def __init__(self) -> None:
        self._claim = Lock()
        # Retain the existing diagnostic state; the lock, never this bool,
        # decides admission. Plain check-then-set is racy across threads.
        self._active = False

    def run(self, command: Callable[[], object]) -> bool:
        """Execute once if idle; return False immediately while busy.

        The lock is intentionally held for the *whole* callback, including
        nested Tk events. Its nonblocking acquisition keeps a second GUI
        command from waiting behind an export and later executing silently.
        """
        if not self._claim.acquire(blocking=False):
            return False
        self._active = True
        try:
            command()
        finally:
            self._active = False
            self._claim.release()
        return True
