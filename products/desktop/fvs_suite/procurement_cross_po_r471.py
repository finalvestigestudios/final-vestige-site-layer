"""Cross-purchase-order credit-document reuse: candidate review evidence only.

The same credit memo may legitimately cover multiple orders. This index
never removes offsets or decides whether a credit is valid. It exposes only
physical source row references from the already parsed invoice CSV.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Mapping


def cross_po_credit_source_rows(
    invoice_groups: Mapping[tuple[str, str], list[dict[str, str]]],
    *,
    document_key: Callable[[object], str],
    event_type: Callable[[dict[str, str]], str],
) -> dict[tuple[str, str], tuple[str, ...]]:
    """Index normalized, nonblank credit IDs reused across distinct POs.

    Keying by PO (not line) avoids misclassifying a multi-line credit as
    cross-order reuse. For each affected PO/line, return all candidate invoice
    CSV physical row numbers in numeric order. These are review links, not
    proof of double payment or an approval/rejection decision.
    """
    occurrences: dict[str, list[tuple[tuple[str, str], str]]] = defaultdict(list)
    for group, rows in invoice_groups.items():
        for row in rows:
            if event_type(row) != "credit":
                continue
            key = document_key(row.get("document_id", ""))
            if key:
                occurrences[key].append((group, row["row"]))

    affected: dict[tuple[str, str], set[str]] = defaultdict(set)
    for matches in occurrences.values():
        if len({group[0] for group, _ in matches}) < 2:
            continue
        source_rows = {row for _, row in matches}
        for group, _ in matches:
            affected[group].update(source_rows)
    return {
        group: tuple(sorted(rows, key=int))
        for group, rows in affected.items()
    }
