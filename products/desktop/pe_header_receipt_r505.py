"""Fail-closed absolute reads of small Windows PE structural fields.

No payload execution, signing/trust claim, or financial data handling.
"""
from __future__ import annotations


class PEHeaderReceiptError(ValueError):
    """Only fixed diagnostics; never expose candidate paths or stream errors."""


def read_exact_at(stream, start: int, count: int, length: int) -> bytes:
    """Read a bounded span with native seek, byte and post-read receipts.

    Distinguishes the validated file-length envelope from the actual stream
    position. A wrapper that fabricates successful bytes without positioning
    the descriptor must not be able to satisfy the release preflight. Real
    unbuffered FileIO is the production source; BytesIO aids inert tests.
    """
    if (type(start) is not int or type(count) is not int or type(length) is not int
            or start < 0 or count < 0 or start + count > length):
        raise PEHeaderReceiptError("PE header or section extends beyond file")
    try:
        positioned = stream.seek(start)
        if type(positioned) is int and positioned == start:
            data = stream.read(count)
            if type(data) is bytes and len(data) == count:
                position_after = stream.tell()
                if type(position_after) is int and position_after == start + count:
                    return data
    except Exception:
        # Do not retain the exception chain: private files often leak in OSError.
        pass
    raise PEHeaderReceiptError("PE file changed or was truncated during inspection")
