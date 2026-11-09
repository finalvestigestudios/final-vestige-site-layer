"""Privacy-safe, identity-bound plaintext creation for local premium restores.

A filesystem error may include the customer's private restore path in its
``filename`` and exception traceback. Never re-raise that exception, including
as implicit ``__context__``: create a fixed diagnostic after the handler ends.
No network, telemetry, original-file writes, or compliance decisions.
"""
from __future__ import annotations

import os
from pathlib import Path

from .vault_restore_cleanup import snapshot_new_file, snapshot_new_folder


def make_private_restore_folder(path: Path) -> os.stat_result:
    """Exclusively create a private directory and capture its OS identity.

    An identity-unavailable folder is not deleted by pathname: ownership could
    not be proven. Callers must keep this restore directory non-public.
    """
    creation_failed = False
    try:
        path.mkdir(mode=0o700)
    except OSError:
        creation_failed = True
    if creation_failed:
        raise ValueError("Cannot safely create private evidence restore folder")

    identity_failed = False
    try:
        identity = snapshot_new_folder(path)
    except OSError:
        identity_failed = True
    if identity_failed:
        raise ValueError("Cannot verify private evidence restore folder")
    return identity


def write_private_restore_member(
    path: Path, contents: bytes, created: list[tuple[Path, os.stat_result]],
) -> None:
    """Exclusively write/fsync an owned member and register it before writing.

    ``created`` is the caller's rollback ledger, tied to descriptor identity.
    Interruptions pass through for the caller to roll back; routine OS errors
    become path-free diagnostics outside the exception handler.
    """
    write_failed = False
    try:
        with path.open("xb") as stream:
            created.append((path, snapshot_new_file(stream.fileno())))
            stream.write(contents)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError:
        write_failed = True
    if write_failed:
        raise ValueError("Cannot safely write private restored evidence")
