"""Conservative offline three-way procurement review, with explicit credit/return events.

No result authorizes payment or asserts fraud. A financial event must be typed;
negative quantities are never inferred to be credits or returns. Decimal amounts
remain exact until a display boundary. A custom price policy is fully disclosed.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext
from functools import wraps
from pathlib import Path
from typing import Callable, Mapping

from .procurement_reference import has_original_spelling, source_document_spellings
from .audit_display import visible_source_label_list
from .review import price_outside_tolerance

CENT = Decimal("0.01")
DEFAULT_ABSOLUTE = CENT
DEFAULT_FRACTION = Decimal("0.02")
# 200,000 validated CSV rows × (up to 9 integer + 8 fractional qty digits)
# × (up to 12 integer + 8 fractional unit-price digits) need fewer than
# 50 significant digits for exact multiplication and gross/credit sums.
# The default Decimal context (28 digits) silently loses subcent evidence.
PROCUREMENT_PRECISION = 64


def _audit_decimal_precision(operation):
    """Use a fresh bounded context, not caller exponent limits or traps.

    Exact totals may exceed the caller's Emax even when source values satisfy
    every procurement input bound. The 64-digit context also keeps subcents.
    """
    @wraps(operation)
    def guarded(*args, **kwargs):
        with localcontext(Context(prec=PROCUREMENT_PRECISION)):
            return operation(*args, **kwargs)
    return guarded


@_audit_decimal_precision
def _display_money(value: Decimal) -> str:
    """Round exact computed totals to display cents, consistently half away from zero.

    Calculations and *_exact export fields retain the unrounded Decimal values.
    The displayed gross, credit and net columns are rounded independently;
    subtracting rounded columns can differ by a cent from the rounded net.
    """
    return format(value.quantize(CENT, rounding=ROUND_HALF_UP), ".2f")


DEFAULT_POLICY_SHA256 = hashlib.sha256(
    b'{"price_absolute":"0.01","price_fraction":"0.02","version":1}\n'
).hexdigest()


def _decimal_field(value: object, name: str, maximum: Decimal) -> Decimal:
    # Preserve the existing call contract for load_price_policy and tests.
    from .procurement_input import exact_policy_limit
    return exact_policy_limit(value, name, maximum)


def _unique_object(pairs):
    output = {}
    for name, value in pairs:
        if name in output:
            raise ValueError("Duplicate JSON price policy key")
        output[name] = value
    return output


@dataclass(frozen=True)
class PricePolicy:
    """Review-only price thresholds. The app does not approve any exceptions."""

    absolute: Decimal = DEFAULT_ABSOLUTE
    fraction: Decimal = DEFAULT_FRACTION
    source_sha256: str = DEFAULT_POLICY_SHA256

    def outside(self, actual: Decimal, expected: Decimal) -> bool:
        # This public method may be called without review_line's wrapper.
        return price_outside_tolerance(actual, expected, self.absolute, self.fraction)

    @property
    def widened(self) -> bool:
        return self.absolute > DEFAULT_ABSOLUTE or self.fraction > DEFAULT_FRACTION


def load_price_policy(path: str | Path | None = None) -> PricePolicy:
    """Load optional, bounded and strict JSON; never silently accept unknown knobs."""
    if path is None or str(path).strip() == "":
        return PricePolicy()
    file = Path(path)
    if file.suffix.lower() != ".json":
        raise ValueError("A local JSON file is required for the optional price policy")
    # The exact JSON bytes used for review must also be bound into the inventory.
    # A descriptor-verified bounded read rejects symlink/path-swap input attacks.
    from .csv_snapshot import read_csv_snapshot
    try:
        data = read_csv_snapshot(file, 8192)
    except ValueError:
        raise ValueError("Price policy requires a stable regular JSON file (8 KiB maximum)") from None
    digest = hashlib.sha256(data).hexdigest()
    try:
        content = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_unique_object,
                             parse_constant=lambda value: (_ for _ in ()).throw(
                                 ValueError("Nonfinite JSON values are not allowed")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid UTF-8 JSON price policy") from exc
    if not isinstance(content, dict):
        raise ValueError("Price policy must be a JSON object")
    expected = {"version", "price_absolute", "price_fraction"}
    if set(content) != expected or content["version"] != 1 or type(content["version"]) is not int:
        raise ValueError("Price policy requires exactly version=1, price_absolute and price_fraction")
    return PricePolicy(
        absolute=_decimal_field(content["price_absolute"], "price_absolute", Decimal("100.00")),
        fraction=_decimal_field(content["price_fraction"], "price_fraction", Decimal("0.10")),
        source_sha256=digest,
    )


def event_kind(row: Mapping[str, str], *, source: str) -> str:
    # Never echo a private CSV event_type (or spoofed row citation) in errors.
    from .procurement_input import event_kind as safe_event_kind
    return safe_event_kind(row, source=source)



def offset_source_line_links(
    rows: list[dict[str, str]], *, source: str, offset: str,
    identifier: Callable[[str], str],
) -> str:
    """Deterministic candidate source-line evidence for credit and return events.

    Links remain scoped to ONE normalized PO/line group. Multiple matching
    document rows stay visible; unresolved references have an empty candidates
    array. This is not a decision that an offset is genuine or authorized.
    Private document labels are deliberately absent from this JSON.
    """
    originals: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        if event_kind(row, source=source) == source:
            document = identifier(row.get("document_id", ""))
            if document:
                originals[document].append(row["row"])
    links: list[dict[str, object]] = []
    for row in rows:
        if event_kind(row, source=source) != offset:
            continue
        reference = identifier(row.get("related_document", ""))
        links.append({
            "offset_row": row["row"],
            "target_rows": list(dict.fromkeys(originals.get(reference, ())))
            if reference else [],
        })
    return json.dumps(links, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@_audit_decimal_precision
def review_line(
    ordered: list[dict[str, str]],
    invoices: list[dict[str, str]],
    receipts: list[dict[str, str]],
    *,
    quantity: Callable[[str], Decimal],
    unit_cost: Callable[[str], Decimal],
    identifier: Callable[[str], str],
    policy: PricePolicy,
) -> tuple[dict[str, str], list[str]]:
    """Calculate exact gross, credits, returns and net totals; flag uncertainty.

    Negative numeric quantities are invalid (enforced by quantity parser).
    Only an explicit credit/return reverses a positive source movement.
    """
    flags: list[str] = []
    order_qty = quantity(ordered[0]["quantity"]) if len(ordered) == 1 else Decimal(0)
    order_price = unit_cost(ordered[0]["unit_price"]) if len(ordered) == 1 else Decimal(0)
    if len(ordered) != 1:
        flags.append("missing_or_duplicate_po")
    if order_price < 0:
        flags.append("negative_unit_price_review")
    if len(ordered) == 1 and order_qty == 0:
        flags.append("zero_order_quantity_review")
    positive_qty = negative_qty = gross_value = credit_value = Decimal(0)
    received_qty = returned_qty = Decimal(0)
    invoice_entries: list[tuple[dict[str, str], str, Decimal, Decimal]] = []
    receipt_entries: list[tuple[dict[str, str], str, Decimal]] = []
    for row in invoices:
        kind = event_kind(row, source="invoice")
        amount = quantity(row["quantity"])
        price = unit_cost(row["unit_price"])
        invoice_entries.append((row, kind, amount, price))
        if kind == "credit":
            negative_qty += amount
            credit_value += amount * price
        else:
            positive_qty += amount
            gross_value += amount * price
        if amount == 0:
            flags.append("zero_movement_review")
        if price < 0:
            flags.append("negative_unit_price_review")
        if len(ordered) == 1 and policy.outside(price, order_price):
            flags.append("price_variance_above_policy")
    for row in receipts:
        kind = event_kind(row, source="receipt")
        amount = quantity(row["quantity"])
        receipt_entries.append((row, kind, amount))
        if kind == "return":
            returned_qty += amount
        else:
            received_qty += amount
        if amount == 0:
            flags.append("zero_movement_review")
    net_inv_qty = positive_qty - negative_qty
    net_rec_qty = received_qty - returned_qty
    net_invoice_total = gross_value - credit_value

    if any(kind == "credit" for _, kind, _, _ in invoice_entries):
        flags.append("credit_memo_review")
    if any(kind == "return" for _, kind, _ in receipt_entries):
        flags.append("return_review")
    if negative_qty > positive_qty:
        flags.append("credit_exceeds_invoice_review")
    if returned_qty > received_qty:
        flags.append("returns_exceed_receipts_review")

    # Credit/return events with missing references cannot be silently treated
    # as verified offsets to the source documents.
    invoice_docs = {identifier(r.get("document_id", "")) for r, k, _, _ in invoice_entries
                    if k == "invoice" and identifier(r.get("document_id", ""))}
    raw_invoice_docs = source_document_spellings(
        str(r.get("document_id", "")) for r, k, _, _ in invoice_entries if k == "invoice")
    invoice_doc_counts = Counter(
        identifier(r.get("document_id", "")) for r, k, _, _ in invoice_entries
        if k == "invoice" and identifier(r.get("document_id", ""))
    )
    if any(count > 1 for count in invoice_doc_counts.values()):
        flags.append("repeated_invoice_document_id_review")
    for row, kind, _, price in invoice_entries:
        if kind != "credit":
            continue
        document = identifier(row.get("document_id", ""))
        related = identifier(row.get("related_document", ""))
        if not document or not related or related not in invoice_docs:
            flags.append("unlinked_credit_review")
        elif not has_original_spelling(row.get("related_document", ""), raw_invoice_docs):
            flags.append("normalized_credit_link_review")
        if document in invoice_docs:
            flags.append("reused_invoice_document_id_review")
        if price < 0:
            flags.append("negative_credit_price_review")
    receipt_docs = {identifier(r.get("document_id", "")) for r, kind, _ in receipt_entries
                    if kind == "receipt" and identifier(r.get("document_id", ""))}
    # An apparent quantity match is not evidence of distinct receiving events.
    # Detect repeated IDs within each physical event type, even when the lossy
    # matching key collapses different source spellings. Empty optional IDs
    # are not treated as the same document.
    receipt_doc_counts = Counter(
        identifier(r.get("document_id", "")) for r, kind, _ in receipt_entries
        if kind == "receipt" and identifier(r.get("document_id", ""))
    )
    return_doc_counts = Counter(
        identifier(r.get("document_id", "")) for r, kind, _ in receipt_entries
        if kind == "return" and identifier(r.get("document_id", ""))
    )
    if any(count > 1 for count in receipt_doc_counts.values()):
        flags.append("repeated_receipt_document_id_review")
    if any(count > 1 for count in return_doc_counts.values()):
        flags.append("repeated_return_document_id_review")
    raw_receipt_docs = source_document_spellings(
        str(r.get("document_id", "")) for r, kind, _ in receipt_entries if kind == "receipt")
    for row, kind, _ in receipt_entries:
        if kind != "return":
            continue
        return_document = identifier(row.get("document_id", ""))
        if not return_document:
            flags.append("unidentified_return_review")
        elif return_document in receipt_docs:
            # A return and its source receipt must not silently share a
            # physical document identity, even when the amounts reconcile.
            flags.append("reused_receipt_document_id_review")
        related = identifier(row.get("related_document", ""))
        if not related or related not in receipt_docs:
            flags.append("unlinked_return_review")
        elif not has_original_spelling(row.get("related_document", ""), raw_receipt_docs):
            flags.append("normalized_return_link_review")

    # Distinct document references permit legitimate equal-quantity installments.
    # When references are missing, retain the older conservative duplicate flag.
    with_docs = all(identifier(row.get("document_id", "")) for row, _, _, _ in invoice_entries)
    if not with_docs:
        signature = [(kind, amount, price) for _, kind, amount, price in invoice_entries]
        if len(set(signature)) < len(signature):
            flags.append("possible_duplicate_invoice_line")
    if not invoices:
        flags.append("missing_invoice")
    if not receipts:
        flags.append("missing_receipt")
    if len(ordered) == 1 and net_inv_qty > order_qty:
        flags.append("invoiced_above_order")
    if net_inv_qty > net_rec_qty:
        flags.append("invoiced_above_received")
    if len(ordered) == 1 and net_rec_qty > order_qty:
        flags.append("received_above_order")
    if len(ordered) == 1 and invoices and 0 <= net_inv_qty < order_qty:
        flags.append("partial_invoice_review")
    if len(ordered) == 1 and receipts and 0 <= net_rec_qty < order_qty:
        flags.append("partial_receipt_review")
    if len(ordered) == 1 and invoice_entries and policy.outside(net_invoice_total, net_inv_qty * order_price):
        flags.append("price_variance_above_policy")
    if policy.widened:
        flags.append("widened_price_policy_review")
    # Preserve legacy status taxonomy under the built-in 2%/1-cent rule.
    if policy == PricePolicy():
        flags = ["price_variance_above_2pct" if flag == "price_variance_above_policy" else flag
                 for flag in flags]
    output = {
        "po_qty": str(order_qty),
        "invoiced_qty": str(net_inv_qty),
        "received_qty": str(net_rec_qty),
        "po_unit_price": format(order_price, "f"),
        "invoice_total": _display_money(net_invoice_total),
        "invoice_total_exact": format(net_invoice_total, "f"),
        "gross_invoice_qty": str(positive_qty),
        "credit_qty": str(negative_qty),
        "gross_invoice_total": _display_money(gross_value),
        "gross_invoice_total_exact": format(gross_value, "f"),
        "credit_value": _display_money(credit_value),
        "credit_value_exact": format(credit_value, "f"),
        "gross_received_qty": str(received_qty),
        "returned_qty": str(returned_qty),
        "price_policy_absolute": format(policy.absolute, "f"),
        "price_policy_fraction": format(policy.fraction, "f"),
        "price_policy_sha256": policy.source_sha256,
        # These are human DISPLAY fields, not matching keys or source custody.
        # Escape hidden Unicode, literal backslashes and embedded list delimiters
        # consistently for invoice, credit, receipt and return references.
        "invoice_documents": visible_source_label_list(
            row.get("document_id", "") for row in invoices),
        "credit_references": visible_source_label_list(
            row.get("related_document", "") for row in invoices),
        "return_references": visible_source_label_list(
            row.get("related_document", "") for row in receipts),
        "receipt_documents": visible_source_label_list(
            row.get("document_id", "") for row, kind, _ in receipt_entries
            if kind == "receipt"),
        "return_documents": visible_source_label_list(
            row.get("document_id", "") for row, kind, _ in receipt_entries
            if kind == "return"),
    }
    # Stable order while deduplicating flags.
    return output, list(dict.fromkeys(flags))


def reconcile_procurement(po: str, invoices: str, receipts: str, folder: str,
                          policy_path: str | None = None):
    """Entrypoint used by the GUI and packaged executable, fully offline."""
    from . import engine
    from .review import normalized_collision, labels_for_report

    policy = load_price_policy(policy_path)
    # Retain SHA-256 of the *parsed* source snapshots, not a later file read.
    source_paths = [po, invoices, receipts]
    snapshots = [
        engine.table(po, ("po_number", "line", "quantity", "unit_price"), include_digest=True),
        engine.table(invoices, ("po_number", "line", "quantity", "unit_price"),
                     ("event_type", "document_id", "related_document"), include_digest=True),
        engine.table(receipts, ("po_number", "line", "quantity"),
                     ("event_type", "document_id", "related_document"), include_digest=True),
    ]
    sources = [rows for rows, _ in snapshots]
    # Pin exported per-row custody to the exact descriptor-verified bytes
    # parsed for each source, rather than re-reading mutable input paths.
    source_custody = {
        "po_source_sha256": snapshots[0][1],
        "invoice_source_sha256": snapshots[1][1],
        "receipt_source_sha256": snapshots[2][1],
    }
    expected_digests = {str(path): digest for path, (_, digest) in zip(source_paths, snapshots)}
    groups = [defaultdict(list) for _ in range(3)]
    for rows, group in zip(sources, groups):
        for row in rows:
            key = (engine.key(row["po_number"]), engine.key(row["line"]))
            if not all(key):
                raise ValueError("Blank purchase order or line at input row " + row["row"])
            group[key].append(row)

    report = []
    for po_id, line in sorted(set().union(*(set(group) for group in groups))):
        records = [group[(po_id, line)] for group in groups]
        ordered, inv, received = records
        metrics, flags = review_line(ordered, inv, received, quantity=engine.qty,
                                     unit_cost=engine.unit_cost, identifier=engine.key,
                                     policy=policy)
        source_records = [*ordered, *inv, *received]
        if normalized_collision(source_records, "po_number"):
            flags.insert(0, "normalized_po_key_review")
        if normalized_collision(source_records, "line"):
            flags.insert(0, "normalized_line_key_review")
        report.append({
            "po": po_id, "line": line, **metrics, **source_custody,
            "credit_source_line_links": offset_source_line_links(
                inv, source="invoice", offset="credit", identifier=engine.key),
            "return_source_line_links": offset_source_line_links(
                received, source="receipt", offset="return", identifier=engine.key),
            "status": ";".join(dict.fromkeys(flags)) or "matched",
            "po_rows": ";".join(r["row"] for r in ordered),
            "invoice_rows": ";".join(r["row"] for r in inv),
            "receipt_rows": ";".join(r["row"] for r in received),
            "po_ids": labels_for_report(ordered, "po_number"),
            "invoice_po_ids": labels_for_report(inv, "po_number"),
            "receipt_po_ids": labels_for_report(received, "po_number"),
            "line_labels": labels_for_report(source_records, "line"),
        })
    original_columns = ("po", "line", "po_qty", "invoiced_qty", "received_qty",
                        "po_unit_price", "invoice_total", "status", "po_rows",
                        "invoice_rows", "receipt_rows", "po_ids", "invoice_po_ids",
                        "receipt_po_ids", "line_labels")
    extra_columns = ("gross_invoice_qty", "credit_qty", "gross_invoice_total",
                     "credit_value", "gross_received_qty", "returned_qty",
                     "invoice_total_exact", "gross_invoice_total_exact", "credit_value_exact",
                     "invoice_documents", "credit_references", "return_references",
                     "price_policy_absolute", "price_policy_fraction",
                     "price_policy_sha256", "receipt_documents", "return_documents",
                     "po_source_sha256", "invoice_source_sha256", "receipt_source_sha256",
                     "credit_source_line_links", "return_source_line_links")
    inputs = list(source_paths)
    if policy_path is not None and str(policy_path).strip():
        inputs.append(policy_path)
        expected_digests[str(policy_path)] = policy.source_sha256

    from .procurement_bundle import publish_procurement_bundle

    def build(staging):
        outputs = [engine.save(staging, "procurement-three-way",
                               original_columns + extra_columns, report)]
        return outputs + [engine.manifest(staging, inputs, outputs,
                                          expected_inputs=expected_digests)]

    # Either the complete review CSV plus its verified inventory is visible,
    # or neither is. A failed manifest check cannot strand a finished report.
    return publish_procurement_bundle(folder, build)
