"""Read back just-appended premium review evidence from its pinned descriptor.

This is an integrity check, not a signature, review approval, filesystem lock,
or defense against a privileged writer who can mutate evidence afterward.
Only call with a readable O_RDWR descriptor and an already-validated event.
"""
from __future__ import annotations

import os


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
