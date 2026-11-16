"""Cross-PO document reuse review evidence; never a payment/compliance decision.

One document may legitimately span multiple orders. Invoice/credit and
receipt/return CSV streams are indexed by explicit event type, with physical
source row citations. No source bytes, Decimal values, documents or financial
movements are changed.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Mapping

# Explicit, conservative cap on materialized (document, affected-line, row)
# citations. A 2,000-order duplicate identity would otherwise request millions
# of repeated cross-order report references and exhaust memory before review.
_MAX_CROSS_PO_CITATIONS = 1_000_000


def _source_row_sort_key(row: object) -> tuple[int, int, str]:
    """Sort source-row citations without coercing untrusted text into errors.

    Ordinary imported rows are canonical ASCII digits. Defensive direct-API
    callers may use leading zeroes (the R477 tie-break contract), but never
    arbitrary labels, non-native strings, Unicode numerals or overlong ints.
    Failure messages contain no customer row text or file paths.
    """
    if (type(row) is not str or not 1 <= len(row) <= 10
            or any(char < "0" or char > "9" for char in row)):
        raise ValueError("Cross-order review requires numeric source row citations")
    return int(row), len(row), row


def _reserve_citation_budget(
    documents: Mapping[str, list[tuple[tuple[str, str], str]]],
    remaining: int,
) -> int:
    """Preflight ALL citations before constructing any cross-order row sets.

    Reserve conservative (affected PO/line groups × distinct physical rows)
    costs. This function does not materialize report evidence. It never puts
    private IDs, source rows, filenames or amounts in exception messages.
    """
    for occurrences in documents.values():
        groups = {group for group, _ in occurrences}
        if len({group[0] for group in groups}) < 2:
            continue
        # Preflight canonical-sort safety for every cross-PO reference before
        # allocating ANY typed output. Without this check int(row) could echo
        # a private CSV label in ValueError, or reject a 4,300-digit string.
        for _, row in occurrences:
            _source_row_sort_key(row)
        cost = len(groups) * len({row for _, row in occurrences})
        if cost > remaining:
            raise ValueError("Cross-order document review exceeds citation budget")
        remaining -= cost
    return remaining


def _materialize_index(
    documents: Mapping[str, list[tuple[tuple[str, str], str]]],
) -> dict[tuple[str, str], tuple[str, ...]]:
    """Expand only after preflight; emit canonical group and row order."""
    affected: dict[tuple[str, str], set[str]] = defaultdict(set)
    for occurrences in documents.values():
        groups = {group for group, _ in occurrences}
        if len({group[0] for group in groups}) < 2:
            continue
        source_rows = {row for _, row in occurrences}
        for group in groups:
            affected[group].update(source_rows)
    # Sets have hash-seed-dependent iteration order. Both report-group order
    # and equal-numeric source-row spellings must be canonical for repeatable
    # local audit evidence across processes, platforms and input order.
    # Shortest spelling sorts first for equal numeric rows (2 before 02).
    # Real CSV physical rows use canonical digits; tie-breaking also makes
    # this shared helper deterministic for callers with noncanonical labels.
    return {
        group: tuple(sorted(rows, key=_source_row_sort_key))
        for group, rows in sorted(affected.items())
    }


def _bounded_index(
    documents: Mapping[str, list[tuple[tuple[str, str], str]]],
    remaining: int,
) -> tuple[dict[tuple[str, str], tuple[str, ...]], int]:
    """Legacy typed wrapper: reject over-budget streams before expansion."""
    remaining = _reserve_citation_budget(documents, remaining)
    return _materialize_index(documents), remaining


def _typed_cross_po_source_rows(
    source_groups: Mapping[tuple[str, str], list[dict[str, str]]],
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
    for group, rows in source_groups.items():
        for row in rows:
            if event_type(row) != kind:
                continue
            key = document_key(row.get("document_id", ""))
            if key:
                occurrences[key].append((group, row["row"]))

    evidence, _ = _bounded_index(occurrences, _MAX_CROSS_PO_CITATIONS)
    return evidence


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



def cross_po_receipt_source_rows(
    receipt_groups: Mapping[tuple[str, str], list[dict[str, str]]],
    *, document_key: Callable[[object], str],
    event_type: Callable[[dict[str, str]], str],
) -> dict[tuple[str, str], tuple[str, ...]]:
    """Return original receipt cross-order review row citations (R473)."""
    return _typed_cross_po_source_rows(
        receipt_groups, document_key=document_key, event_type=event_type,
        kind="receipt")


def cross_po_return_source_rows(
    receipt_groups: Mapping[tuple[str, str], list[dict[str, str]]],
    *, document_key: Callable[[object], str],
    event_type: Callable[[dict[str, str]], str],
) -> dict[tuple[str, str], tuple[str, ...]]:
    """Return return-document cross-order review row citations (R473)."""
    return _typed_cross_po_source_rows(
        receipt_groups, document_key=document_key, event_type=event_type,
        kind="return")


def cross_po_all_document_source_rows(
    invoice_groups: Mapping[tuple[str, str], list[dict[str, str]]],
    receipt_groups: Mapping[tuple[str, str], list[dict[str, str]]],
    *,
    document_key: Callable[[object], str],
    invoice_event_type: Callable[[dict[str, str]], str],
    receipt_event_type: Callable[[dict[str, str]], str],
) -> dict[str, dict[tuple[str, str], tuple[str, ...]]]:
    """Index all four typed document streams in two source scans, never a decision.

    Each source row is classified once, and nonblank normalized document IDs
    share evidence only inside their own typed stream. A PO must differ for a
    review hit; one document on several lines of one PO is not cross-order.
    Returned values retain numeric-sorted physical source CSV row references.
    """
    by_type: dict[str, dict[str, list[tuple[tuple[str, str], str]]]] = {
        kind: defaultdict(list) for kind in ("invoice", "credit", "receipt", "return")
    }
    for groups, classify, valid_kinds in (
        (invoice_groups, invoice_event_type, frozenset(("invoice", "credit"))),
        (receipt_groups, receipt_event_type, frozenset(("receipt", "return"))),
    ):
        for group, rows in groups.items():
            for row in rows:
                kind = classify(row)
                if kind not in valid_kinds:
                    continue
                key = document_key(row.get("document_id", ""))
                if key:
                    by_type[kind][key].append((group, row["row"]))
    # Reserve the combined four-type budget before expanding even the FIRST
    # type. A later overflow must not allocate earlier, doomed report evidence.
    remaining = _MAX_CROSS_PO_CITATIONS
    for documents in by_type.values():
        remaining = _reserve_citation_budget(documents, remaining)
    return {kind: _materialize_index(documents)
            for kind, documents in by_type.items()}

def cross_po_foreign_offset_source_rows(
    invoice_groups: Mapping[tuple[str, str], list[dict[str, str]]],
    receipt_groups: Mapping[tuple[str, str], list[dict[str, str]]],
    *,
    document_key: Callable[[object], str],
    invoice_event_type: Callable[[dict[str, str]], str],
    receipt_event_type: Callable[[dict[str, str]], str],
) -> dict[str, dict[tuple[str, str], tuple[str, ...]]]:
    """Review-only foreign original rows for unresolved local credit/return links.

    A reference is foreign only when its original document exists on another
    PO and there is NO original with that key anywhere on the offset's PO.
    Duplicate references remain provenance-only, never automatic rejection.
    One reservation per reference bounds combined credit/return citation fanout\n    before any expanded report evidence is materialized.
    """
    originals: dict[str, dict[str, list[tuple[tuple[str, str], str]]]] = {
        kind: defaultdict(list) for kind in ("credit", "return")
    }
    offsets: dict[str, dict[str, set[tuple[str, str]]]] = {
        kind: defaultdict(set) for kind in ("credit", "return")
    }
    for groups, classify, original_kind, offset_kind in (
        (invoice_groups, invoice_event_type, "invoice", "credit"),
        (receipt_groups, receipt_event_type, "receipt", "return"),
    ):
        for group, rows in groups.items():
            for row in rows:
                kind = classify(row)
                if kind == original_kind:
                    key = document_key(row.get("document_id", ""))
                    if key:
                        originals[offset_kind][key].append((group, row["row"]))
                elif kind == offset_kind:
                    reference = document_key(row.get("related_document", ""))
                    if reference:
                        offsets[offset_kind][reference].add(group)

    # For every foreign affected group, every original has a different PO.
    # Compute unique source rows ONCE per reference, not once per group, then
    # reserve rows x groups atomically across both types before materializing.
    remaining = _MAX_CROSS_PO_CITATIONS
    candidates: list[tuple[str, tuple[tuple[str, str], ...], frozenset[str]]] = []
    for kind in ("credit", "return"):
        for reference, groups in offsets[kind].items():
            sources = originals[kind].get(reference, ())
            if not sources:
                continue
            source_pos = {source_group[0] for source_group, _ in sources}
            foreign_groups = tuple(sorted(group for group in groups
                                          if group[0] not in source_pos))
            if not foreign_groups:
                continue
            rows = frozenset(row for _, row in sources)
            for row in rows:
                _source_row_sort_key(row)  # Redacted, before either output.
            cost = len(rows) * len(foreign_groups)
            if cost > remaining:
                raise ValueError("Cross-order document review exceeds citation budget")
            remaining -= cost
            if rows:
                candidates.append((kind, foreign_groups, rows))

    affected: dict[str, dict[tuple[str, str], set[str]]] = {
        kind: defaultdict(set) for kind in ("credit", "return")
    }
    for kind, groups, rows in candidates:
        for group in groups:
            affected[kind][group].update(rows)
    return {
        kind: {
            group: tuple(sorted(rows, key=_source_row_sort_key))
            for group, rows in sorted(affected[kind].items())
        }
        for kind in ("credit", "return")
    }
