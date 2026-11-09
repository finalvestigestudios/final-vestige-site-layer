"""Sanitized policy-file intake boundary for Policy Delta Desk.

Preflight is not authorization: the caller must use the descriptor-owned
read_csv_snapshot guard before decoding or creating a human-review report.
"""
from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Callable

_POLICY_SELECTION = "Policy comparison supports existing TXT, MD and CSV files"
_POLICY_UNSTABLE = (
    "Policy input is not a stable regular file "
    "(links or concurrent changes are not accepted)"
)
_POLICY_OVERSIZE = "Policy file exceeds 10 MiB input limit"
_POLICY_ENCODING = "Policy input must be valid UTF-8 text"
# The underlying snapshot guard currently uses the shared CSV engine's label,
# even when Policy Delta supplies its independent 10 MiB input cap.
_SNAPSHOT_OVERSIZE = "CSV input exceeds 64 MiB file-size limit"


def checked_policy_path(value: str | PathLike[str], allowed: frozenset[str]) -> Path:
    """Select a candidate regular file without exposing a private pathname.

    A successful is_file probe does not authorize the file, pin its identity,
    reject symlinks, or prevent races. The descriptor-owned snapshot does that.
    """
    invalid = False
    try:
        source = Path(value)
        if source.suffix.lower() not in allowed or not source.is_file():
            invalid = True
    except (OSError, TypeError, ValueError):
        invalid = True
    if invalid:
        # Raise *after* the handler: from None would still leave
        # private OSError.filename in __context__ for programmatic consumers.
        raise ValueError(_POLICY_SELECTION)
    return source


def read_policy_snapshot(
    source: Path, limit: int, reader: Callable[[Path, int], bytes]
) -> bytes:
    """Translate expected snapshot faults without retaining original errors.

    Recognize only the exact known file-size sentinel. Never search an
    exception's arbitrary text for 'exceeds' (a filename may contain it).
    Other snapshot failures preserve the conservative unstable-file verdict.
    """
    rejected = False
    oversized = False
    try:
        content = reader(source, limit)
    except ValueError as error:
        rejected = True
        oversized = (
            type(error) is ValueError
            and len(error.args) == 1
            and type(error.args[0]) is str
            and error.args[0] == _SNAPSHOT_OVERSIZE
        )
    except OSError:
        rejected = True
    if rejected:
        raise ValueError(_POLICY_OVERSIZE if oversized else _POLICY_UNSTABLE)
    return content


def decode_policy_utf8(raw: bytes) -> str:
    """Decode a verified byte snapshot without exposing private undecodable data.

    UnicodeDecodeError.object can contain the entire sensitive input; never
    chain it into the public exception (including hidden __context__).
    """
    invalid = False
    try:
        body = raw.decode("utf-8-sig")
    except UnicodeError:
        invalid = True
    if invalid:
        raise ValueError(_POLICY_ENCODING)
    return body
