"""Canonical physical-row citation order for deterministic SpendMap evidence.

The SpendMap parser already establishes genuine native source row coordinates,
uniqueness and byte-snapshot custody. A direct caller may supply those valid
rows in any list order; their human-readable bucket citations must not depend
on that arbitrary order. This is navigation evidence, not source authentication.
"""
from __future__ import annotations

import re

_MAX_ROWS = 200_000
_ROW = re.compile(r"[1-9][0-9]{0,9}\Z", re.ASCII)


def canonical_spend_source_rows(labels: list[str]) -> str:
    """Return semicolon-separated numeric ascending, unique physical rows.

    No native record is mutated. Recheck the narrow coordinate contract at the
    presentation boundary; never interpolate rejected private values into
    exception messages or evaluate subclass hooks.
    """
    if type(labels) is not list or len(labels) > _MAX_ROWS:
        raise ValueError("Invalid SpendMap source row citation collection")
    numbers: list[int] = []
    seen: set[int] = set()
    for label in labels:
        if type(label) is not str or _ROW.fullmatch(label) is None:
            raise ValueError("Invalid SpendMap physical row citation")
        number = int(label)
        if number < 2 or number in seen:
            raise ValueError("Invalid or repeated SpendMap physical row citation")
        seen.add(number)
        numbers.append(number)
    numbers.sort()
    return ";".join(str(number) for number in numbers)
