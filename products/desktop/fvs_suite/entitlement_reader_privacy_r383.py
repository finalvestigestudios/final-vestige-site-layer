"""Drop private filesystem failures before exposing premium-client diagnostics.

The underlying read is a caller-supplied, descriptor-bound, bounded local read.
This wrapper never interprets an entitlement or authorizes a payment/license.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable


def read_private_entitlement(
    source: str | Path,
    size_limit: int,
    reader: Callable[[str | Path, int, str], bytes],
    error_type: type[Exception],
) -> bytes:
    """Preserve public read-error classifications, not underlying exceptions.

    Raising a new exception from None inside an except block still retains the
    original exception in __context__. Capture only a fixed classification,
    leave the handler, and then raise without a source exception chain.
    """
    failure: str | None = None
    try:
        return reader(source, size_limit, "Entitlement file")
    except ValueError as exc:
        # The descriptor reader emits a fixed "exceeds" phrase for size limits.
        # Never retain the original exception or embed its message in output.
        failure = "size" if "exceeds" in str(exc) else "regular"
    except OSError:
        failure = "inaccessible"

    if failure == "size":
        raise error_type("Entitlement file exceeds the size limit")
    if failure == "regular":
        raise error_type("Entitlement must be a stable, distinct regular file")
    if failure == "inaccessible":
        raise error_type("Entitlement file is inaccessible or changed during verification")
    raise RuntimeError("Unreachable entitlement reader state")
