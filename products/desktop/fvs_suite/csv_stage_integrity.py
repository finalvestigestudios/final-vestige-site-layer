"""Bounded byte-exact verification of unpublished local CSV evidence.

The caller hashes *serialized* CSV bytes as writes are accepted, including the
UTF-8 BOM; this verifier then reads the staged descriptor before publication.
No source values, filenames, digest, or customer metadata enter error text.
"""
from __future__ import annotations

import errno
import hashlib
import os

_BOM = b"\xef\xbb\xbf"
_READ_CHUNK = 256 * 1024
_FAILED = "CSV report staging integrity check failed"


class CSVStagingWitness:
    """Bounded streaming witness; never buffers a full financial export."""

    def __init__(self) -> None:
        self._digest = hashlib.sha256(_BOM)
        self._size = len(_BOM)

    def record(self, encoded: bytes) -> None:
        """Record one accepted, already-budgeted UTF-8 csv.writer output."""
        if type(encoded) is not bytes:
            raise TypeError("CSV staged evidence must be plain bytes")
        self._digest.update(encoded)
        self._size += len(encoded)

    def verify(self, descriptor: int) -> None:
        """Fail closed for incomplete, expanded, or same-length altered data."""
        failed = False
        try:
            if os.fstat(descriptor).st_size != self._size:
                raise OSError(errno.EIO, _FAILED)
            os.lseek(descriptor, 0, os.SEEK_SET)
            digest = hashlib.sha256()
            remaining = self._size
            while remaining:
                chunk = os.read(descriptor, min(_READ_CHUNK, remaining))
                if not chunk:
                    raise OSError(errno.EIO, _FAILED)
                digest.update(chunk)
                remaining -= len(chunk)
            if os.read(descriptor, 1) or digest.digest() != self._digest.digest():
                raise OSError(errno.EIO, _FAILED)
        except OSError:
            failed = True
        # Raise only after leaving the OS handler. Even suppressed tracebacks
        # retain customer filenames in exception.__context__.
        if failed:
            raise OSError(errno.EIO, _FAILED)
