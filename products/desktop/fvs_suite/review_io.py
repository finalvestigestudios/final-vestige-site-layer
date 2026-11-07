"""Fail-closed custody for premium review side effects.

An export, encrypted backup or restore may have changed the destination even
when its final verification fails. On *any* unsuccessful invocation (including
KeyboardInterrupt/SystemExit), discard the selected in-memory report before
surfacing an error. Never automatically roll back or delete external files.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable


def perform_custodied_output(action: Callable[[], Path], revoke: Callable[[], None]) -> Path:
    """Run local output action; revoke any loaded review on ambiguous failure.

    The caller owns privacy-safe UI error handling and must tell the operator to
    inspect the chosen destination before retrying. This is **not** a durable
    transaction or a substitute for engine-level atomic publication.
    """
    if not callable(action) or not callable(revoke):
        raise ValueError("Invalid premium output callbacks")
    succeeded = False
    try:
        result = action()
        if not isinstance(result, Path) or not result.name:
            raise ValueError("Premium output did not return a valid result path")
        succeeded = True
        return result
    finally:
        if not succeeded:
            revoke()
