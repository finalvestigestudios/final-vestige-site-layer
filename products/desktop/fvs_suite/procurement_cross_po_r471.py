"""Cross-PO document reuse review evidence; never a payment/compliance decision.

A single invoice or credit may legitimately span multiple orders. Only typed
source invoice CSV rows and their physical line references are indexed. No
source bytes, Decimal values, documents or financial movements are changed.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Mapping


def _typed_cross_po_source_rows(
    invoice_groups: Mapping[tuple[str, str], list[dict[str, str]]],
    *,
    document_key: Callable[[object], str],
    event_type: Callable[[dict[str, str]], str],
    kind: str,
) -> dict[tuple[str, str], tuple[str, ...]]:
    """Physical row citations for nonblank IDs shared by distinct PO keys.

    Document identities are scoped to their event type: an invoice ID never
    collides with a credit ID in this index. Groups from different lines of
    the same PO cannot create a false cross-PO alert.
    """
    occurrences: dict[str, list[tuple[tuple[str, str], str]]] = defaultdict(list)
    for group, rows in invoice_groups.items():
        for row in rows:
            if event_type(row) != kind:
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


def cross_po_credit_source_rows(
    invoice_groups: Mapping[tuple[str, str], list[dict[str, str]]],
    *, document_key: Callable[[object], str],
    event_type: Callable[[dict[str, str]], str],
) -> dict[tuple[str, str], tuple[str, ...]]:
    """Return credit-memo cross-order review row citations (R471 contract)."""
    return _typed_cross_po_source_rows(
        invoice_groups, document_key=document_key, event_type=event_type,
        kind="credit")


def cross_po_invoice_source_rows(
    invoice_groups: Mapping[tuple[str, str], list[dict[str, str]]],
    *, document_key: Callable[[object], str],
    event_type: Callable[[dict[str, str]], str],
) -> dict[tuple[str, str], tuple[str, ...]]:
    """Return invoice cross-order review row citations (R472 contract)."""
    return _typed_cross_po_source_rows(
        invoice_groups, document_key=document_key, event_type=event_type,
        kind="invoice")
