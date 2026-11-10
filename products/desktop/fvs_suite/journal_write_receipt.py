"""Read back just-appended premium review evidence from its pinned descriptor.

This is an integrity check, not a signature, review approval, filesystem lock,
or defense against a privileged writer who can mutate evidence afterward.
Only call with a readable O_RDWR descriptor and an already-validated event.
"""
from __future__ import annotations

import hashlib
import os



PREFIX_CHUNK_BYTES = 1024 * 1024


def digest_pinned_prefix(descriptor: int, byte_count: int) -> bytes:
    """Hash exactly the pre-append bytes using a duplicate of the pinned fd.

    The duplicate shares its file offset with the append handle, but O_APPEND
    keeps subsequent writes at EOF. No pathname is reopened, no unbounded
    plaintext is retained, and a short read fails closed. The caller compares
    this digest before and after the append; this is NOT an authenticity proof.
    """
    if type(byte_count) is not int or byte_count < 0:
        raise ValueError("Review journal prefix length is invalid")
    copied = os.dup(descriptor)
    try:
        stream = os.fdopen(copied, "rb", buffering=0)
    except BaseException:
        os.close(copied)
        raise
    with stream:
        if stream.seek(0, os.SEEK_SET) != 0:
            raise ValueError("Review journal prefix could not be positioned")
        digest = hashlib.sha256()
        remaining = byte_count
        while remaining:
            block = stream.read(min(PREFIX_CHUNK_BYTES, remaining))
            if not block:
                raise ValueError("Review journal prefix changed during append")
            digest.update(block)
            remaining -= len(block)
        return digest.digest()


def require_exact_append_readback(descriptor: int, offset: int, event: bytes) -> None:
    """Fail closed if the newly appended event differs from the intended bytes.

    Inspect the *same descriptor* used to append and fsync. O_APPEND must be
    retained by the caller for concurrent-offset safety; seeking here changes
    only the read offset and does not relax append placement on later writes.
    A short read is a HOLD, not evidence of a successful append.
    """
    if not isinstance(offset, int) or offset < 0 or not isinstance(event, bytes) or not event:
        raise ValueError("Review journal append witness is invalid")
    if os.lseek(descriptor, offset, os.SEEK_SET) != offset:
        raise ValueError("Review journal append witness could not be positioned")
    if os.read(descriptor, len(event) + 1) != event:
        raise ValueError("Review journal appended bytes differ from proposed event")
