"""Fail-closed SQLite write boundary for operator-side premium license issuance.

The caller supplies a single reservation/finalization action. Only that action
runs inside BEGIN IMMEDIATE; it must not manage its own commit or rollback.
Never retry a failed or ambiguous commit automatically: a human must inspect
the operator's protected issuance registry before another issuance attempt.
"""
from __future__ import annotations

import sqlite3
from typing import Callable, TypeVar

_T = TypeVar("_T")


def run_protected_write(
    db: sqlite3.Connection,
    action: Callable[[sqlite3.Connection], _T],
    *,
    conflict_message: str,
    database_message: str,
    error_type: type[Exception],
) -> _T:
    """Commit exactly once, rollback on failure and never leak SQLite faults.

    An unsuccessful BEGIN has no owned transaction to roll back. Rollback is
    best-effort (a broken connection may reject it), never a replacement for
    the original public failure. SQLite exceptions are translated only *after*
    leaving the handler, so their private __context__/__cause__ do not escape.
    Non-SQLite errors and process interrupts propagate unchanged after cleanup.
    """
    transaction_started = False
    failure = None
    result = None
    try:
        db.execute("BEGIN IMMEDIATE")
        transaction_started = True
        result = action(db)
        db.execute("COMMIT")
        transaction_started = False
    except sqlite3.IntegrityError:
        failure = conflict_message
    except sqlite3.Error:
        failure = database_message
    finally:
        if transaction_started:
            try:
                db.execute("ROLLBACK")
            except sqlite3.Error:
                # The transaction state is then uncertain: never retry here.
                pass
    if failure is not None:
        raise error_type(failure)
    return result
