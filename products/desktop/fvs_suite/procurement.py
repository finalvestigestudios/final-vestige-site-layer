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
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable, Mapping

CENT = Decimal("0.01")
DEFAULT_ABSOLUTE = CENT
DEFAULT_FRACTION = Decimal("0.02")


def _decimal_field(value: object, name: str, maximum: Decimal) -> Decimal:
    # Reject float/bool inputs: JSON float conversion is not exact financial input.
    if isinstance(value, bool) or isinstance(value, float) or not isinstance(value, (str, int)):
        raise ValueError(f"{name} must be a decimal string or integer")
    raw = str(value).strip()
    try:
        result = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"{name} is not a valid decimal") from exc
    if not result.is_finite() or result < 0 or result > maximum:
        raise ValueError(f"{name} must be finite and between zero and {maximum}")
    return result


def _unique_object(pairs):
    output = {}
    for name, value in pairs:
        if name in output:
            raise ValueError(f"Duplicate JSON key: {name}")
        output[name] = value
    return output


@dataclass(frozen=True)
class PricePolicy:
    """Review-only price thresholds. The app does not approve any exceptions."""

    absolute: Decimal = DEFAULT_ABSOLUTE
    fraction: Decimal = DEFAULT_FRACTION
    source_sha256: str = "built-in"

    def outside(self, actual: Decimal, expected: Decimal) -> bool:
        return abs(actual - expected) > max(self.absolute, abs(expected) * self.fraction)

    @property
    def widened(self) -> bool:
        return self.absolute > DEFAULT_ABSOLUTE or self.fraction > DEFAULT_FRACTION


def load_price_policy(path: str | Path | None = None) -> PricePolicy:
    """Load optional, bounded and strict JSON; never silently accept unknown knobs."""
    if path is None or str(path).strip() == "":
        return PricePolicy()
    file = Path(path)
    if file.suffix.lower() != ".json" or not file.is_file():
        raise ValueError("A local JSON file is required for the optional price policy")
    if file.stat().st_size > 8192:
        raise ValueError("Price policy exceeds the 8 KiB safety limit")
    data = file.read_bytes()
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
    if set(content) != expected or content["version"] != 1 or isinstance(content["version"], bool):
        raise ValueError("Price policy requires exactly version=1, price_absolute and price_fraction")
    return PricePolicy(
        absolute=_decimal_field(content["price_absolute"], "price_absolute", Decimal("100.00")),
        fraction=_decimal_field(content["price_fraction"], "price_fraction", Decimal("0.10")),
        source_sha256=digest,
    )


def event_kind(row: Mapping[str, str], *, source: str) -> str:
    """Omitted event_type retains legacy positive invoice/receipt behavior."""
    allowed = {"invoice": {"invoice", "credit"}, "receipt": {"receipt", "return"}}
    value = str(row.get("event_type", "") or source).strip().casefold()
    if value not in allowed[source]:
        raise ValueError(f"Unsupported {source} event_type '{value}' at input row {row.get('row','?')}")
    return value


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
        if price < 0:
            flags.append("negative_credit_price_review")
    for row, kind, _ in receipt_entries:
        if kind == "return" and not identifier(row.get("document_id", "")):
            flags.append("unidentified_return_review")

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
        "invoice_total": format(net_invoice_total.quantize(CENT), ".2f"),
        "gross_invoice_qty": str(positive_qty),
        "credit_qty": str(negative_qty),
        "gross_invoice_total": format(gross_value.quantize(CENT), ".2f"),
        "credit_value": format(credit_value.quantize(CENT), ".2f"),
        "gross_received_qty": str(received_qty),
        "returned_qty": str(returned_qty),
        "price_policy_absolute": format(policy.absolute, "f"),
        "price_policy_fraction": format(policy.fraction, "f"),
        "price_policy_sha256": policy.source_sha256,
        "invoice_documents": "; ".join(sorted({r.get("document_id", "").strip() for r in invoices if r.get("document_id", "")})),
        "credit_references": "; ".join(sorted({r.get("related_document", "").strip() for r in invoices if r.get("related_document", "")})),
    }
    # Stable order while deduplicating flags.
    return output, list(dict.fromkeys(flags))


def reconcile_procurement(po: str, invoices: str, receipts: str, folder: str,
                          policy_path: str | None = None):
    """Entrypoint used by the GUI and packaged executable, fully offline."""
    from . import engine
    from .review import normalized_collision, labels_for_report

    policy = load_price_policy(policy_path)
    sources = [
        engine.table(po, ("po_number", "line", "quantity", "unit_price")),
        engine.table(invoices, ("po_number", "line", "quantity", "unit_price"),
                     ("event_type", "document_id", "related_document")),
        engine.table(receipts, ("po_number", "line", "quantity"),
                     ("event_type", "document_id")),
    ]
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
            "po": po_id, "line": line, **metrics,
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
                     "invoice_documents", "credit_references",
                     "price_policy_absolute", "price_policy_fraction",
                     "price_policy_sha256")
    outputs = [engine.save(folder, "procurement-three-way", original_columns + extra_columns, report)]
    inputs = [po, invoices, receipts]
    if policy_path is not None and str(policy_path).strip():
        inputs.append(policy_path)
    return outputs + [engine.manifest(folder, inputs, outputs)]
