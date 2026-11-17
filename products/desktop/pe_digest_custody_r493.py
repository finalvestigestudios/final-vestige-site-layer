"""Bind an already-validated PE stream to the exact six-candidate SHA256 receipt.

Reads the SAME open descriptor used for structural PE parsing; never executes it.
Not a signature, malware, Windows smoke, entitlement, or release approval.
"""
from __future__ import annotations

import hashlib
import os
import re

_MAX_IMAGE_BYTES = 512 * 1024 * 1024
_HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class PEDigestCustodyError(ValueError):
    """Fixed diagnostics only; do not expose local customer/build paths."""


def _identity(info) -> tuple[int, int, int, int, int]:
    return (info.st_dev, info.st_ino, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def verify_pe_digest_stream(stream, opened, expected_sha256: str,
                            *, maximum: int = _MAX_IMAGE_BYTES) -> None:
    """Match inventory digest and descriptor identity after the PE shape check.

    The caller retains ownership of the open stream. This complements rather
    than replaces candidate_guard's separate pathname/ancestry snapshot checks.
    """
    if (type(expected_sha256) is not str
            or _HEX_SHA256.fullmatch(expected_sha256) is None
            or type(maximum) is not int or not 1 <= maximum <= _MAX_IMAGE_BYTES):
        raise PEDigestCustodyError("PE digest custody unavailable")
    failed = False
    try:
        before = os.fstat(stream.fileno())
        if (_identity(before) != _identity(opened)
                or not 1 <= before.st_size <= maximum):
            failed = True
        else:
            positioned = stream.seek(0)
            if type(positioned) is not int or positioned != 0:
                failed = True
            else:
                digest = hashlib.sha256()
                total = 0
                while True:
                    requested = min(1_048_576, maximum - total + 1)
                    chunk = stream.read(requested)
                    if type(chunk) is not bytes or len(chunk) > requested:
                        failed = True
                        break
                    next_position = stream.tell()
                    if type(next_position) is not int or next_position != total + len(chunk):
                        failed = True
                        break
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > maximum:
                        failed = True
                        break
                    digest.update(chunk)
                after = os.fstat(stream.fileno())
                if (total != before.st_size or _identity(after) != _identity(before)
                        or digest.hexdigest() != expected_sha256):
                    failed = True
    except Exception:
        failed = True
    if failed:
        # Outside an active except: never retain a private exception graph.
        raise PEDigestCustodyError("PE digest custody unavailable")
