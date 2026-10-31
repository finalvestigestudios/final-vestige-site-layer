"""R89: ProcureGuard must not inherit caller Decimal exponent limits or traps.

Synthetic, offline repository regression. Every procurement decision is a
review flag, not a payment, fraud, or compliance determination.
"""
from __future__ import annotations

import csv
from decimal import (Context, Decimal, Inexact, Rounded, Overflow, Underflow,
                     Clamped, ROUND_DOWN, localcontext)
from pathlib import Path
import tempfile
import unittest

from fvs_suite import engine, procurement

Q = "999999999.99999999"
P = "999999999999.99999999"
EXACT_PRODUCT = "999999999999999989990.0000000000000001"


def set_hostile(context):
    context.prec = 3
    context.Emax = 6
    context.Emin = -6
    context.rounding = ROUND_DOWN
    for signal in (Inexact, Rounded, Overflow, Underflow, Clamped):
        context.traps[signal] = True


class ProcurementIndependentContextR89(unittest.TestCase):
    def review(self, *, quantity=Q, price=P, po_price=P, invoice_rows=None,
               receipt_rows=None):
        ordered = [{"quantity": quantity, "unit_price": po_price}]
        invoices = invoice_rows if invoice_rows is not None else [
            {"quantity": quantity, "unit_price": price,
             "event_type": "invoice", "document_id": "INV-1"}]
        receipts = receipt_rows if receipt_rows is not None else [
            {"quantity": quantity, "event_type": "receipt", "document_id": "REC-1"}]
        return procurement.review_line(
            ordered, invoices, receipts, quantity=engine.qty,
            unit_cost=engine.unit_cost, identifier=engine.key,
            policy=procurement.PricePolicy())

    def test_old_ambient_exponent_causes_real_decimal_overflow(self):
        with localcontext() as caller:
            set_hostile(caller)
            with self.assertRaises(Overflow):
                Decimal(Q) * Decimal(P)

    def test_large_exact_gross_under_hostile_exponent_limits(self):
        with localcontext() as caller:
            set_hostile(caller)
            metrics, flags = self.review()
        self.assertEqual(metrics["gross_invoice_total_exact"], EXACT_PRODUCT)
        self.assertEqual(metrics["invoice_total_exact"], EXACT_PRODUCT)
        self.assertEqual(metrics["invoice_total"], "999999999999999989990.00")
        self.assertEqual(flags, [])

    def test_small_exact_subcent_product_ignores_ambient_emin(self):
        with localcontext() as caller:
            set_hostile(caller)
            metrics, flags = self.review(quantity="0.00000001",
                price="0.00000001", po_price="0.00000001")
        self.assertEqual(metrics["invoice_total_exact"], "0.0000000000000001")
        self.assertEqual(metrics["invoice_total"], "0.00")
        self.assertEqual(flags, [])

    def test_display_uses_half_up_and_not_caller_context(self):
        with localcontext() as caller:
            set_hostile(caller)
            self.assertEqual(procurement._display_money(Decimal("0.005")), "0.01")
            self.assertEqual(procurement._display_money(Decimal("-0.005")), "-0.01")
            self.assertEqual(procurement._display_money(Decimal(EXACT_PRODUCT)),
                             "999999999999999989990.00")

    def test_equal_credit_retains_exact_gross_and_review_flag(self):
        invoices = [
            {"quantity": Q, "unit_price": P, "event_type": "invoice",
             "document_id": "INV-1"},
            {"quantity": Q, "unit_price": P, "event_type": "credit",
             "document_id": "CM-1", "related_document": "INV-1"},
        ]
        with localcontext() as caller:
            set_hostile(caller)
            metrics, flags = self.review(invoice_rows=invoices)
        self.assertEqual(metrics["gross_invoice_total_exact"], EXACT_PRODUCT)
        self.assertEqual(metrics["credit_value_exact"], EXACT_PRODUCT)
        self.assertEqual(Decimal(metrics["invoice_total_exact"]), Decimal(0))
        self.assertIn("credit_memo_review", flags)

    def test_negative_price_still_requires_review(self):
        with localcontext() as caller:
            set_hostile(caller)
            metrics, flags = self.review(price="-" + P, po_price="-" + P)
        self.assertEqual(metrics["invoice_total_exact"], "-" + EXACT_PRODUCT)
        self.assertIn("negative_unit_price_review", flags)

    def test_price_variance_remains_visible(self):
        with localcontext() as caller:
            set_hostile(caller)
            _, flags = self.review(quantity="1", price="102.02", po_price="100.01")
        self.assertIn("price_variance_above_2pct", flags)

    def test_caller_context_and_traps_are_unchanged(self):
        with localcontext() as caller:
            set_hostile(caller)
            before = caller.copy()
            self.review()
            procurement._display_money(Decimal(EXACT_PRODUCT))
            self.assertEqual((caller.prec, caller.Emax, caller.Emin, caller.rounding),
                             (before.prec, before.Emax, before.Emin, before.rounding))
            self.assertEqual(caller.traps, before.traps)
            self.assertEqual(caller.flags, before.flags)

    def test_standard_and_hostile_results_are_identical(self):
        normal = self.review()
        with localcontext() as caller:
            set_hostile(caller)
            hostile = self.review()
        self.assertEqual(hostile, normal)

    def test_high_precision_and_hostile_results_are_identical(self):
        with localcontext(Context(prec=100)):
            normal = self.review()
        with localcontext() as caller:
            set_hostile(caller)
            hostile = self.review()
        self.assertEqual(hostile, normal)

    def test_hundred_invoice_lines_keep_exact_aggregate(self):
        invoices = [{"quantity": "1", "unit_price": P, "event_type": "invoice",
                     "document_id": f"INV-{i}"} for i in range(100)]
        receipts = [{"quantity": "100", "event_type": "receipt",
                     "document_id": "REC-1"}]
        with localcontext() as caller:
            set_hostile(caller)
            metrics, flags = self.review(quantity="100", invoice_rows=invoices,
                                         receipt_rows=receipts)
        self.assertEqual(metrics["invoice_total_exact"], "99999999999999.99999900")
        self.assertEqual(metrics["gross_invoice_qty"], "100")
        self.assertEqual(flags, [])

    def test_local_csv_and_manifest_route_preserves_original_bytes(self):
        with tempfile.TemporaryDirectory(prefix="fvs-r89-") as directory:
            root = Path(directory)
            fixtures = [
                ("po.csv", ("po_number", "line", "quantity", "unit_price"),
                 (("PO1", "1", Q, P),)),
                ("inv.csv", ("po_number", "line", "quantity", "unit_price"),
                 (("PO1", "1", Q, P),)),
                ("rec.csv", ("po_number", "line", "quantity"),
                 (("PO1", "1", Q),)),
            ]
            inputs = []
            for name, columns, rows in fixtures:
                path = root / name
                with path.open("w", encoding="utf-8", newline="") as out:
                    writer = csv.writer(out)
                    writer.writerow(columns)
                    writer.writerows(rows)
                inputs.append(path)
            before = [path.read_bytes() for path in inputs]
            with localcontext() as caller:
                set_hostile(caller)
                reports = engine.procure_guard(
                    *(str(path) for path in inputs), str(root))
            self.assertEqual(len(reports), 2)
            with reports[0].open("r", encoding="utf-8-sig", newline="") as data:
                rows = list(csv.DictReader(data))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["status"], "matched")
            self.assertEqual(rows[0]["invoice_total_exact"], EXACT_PRODUCT)
            self.assertEqual(rows[0]["po_rows"], "2")
            self.assertTrue(reports[1].is_file())
            self.assertEqual([path.read_bytes() for path in inputs], before)

    def test_invalid_source_does_not_publish_partial_report(self):
        with tempfile.TemporaryDirectory(prefix="fvs-r89-invalid-") as directory:
            root = Path(directory)
            fixtures = [
                ("po.csv", "po_number,line,quantity,unit_price\nPO1,1,1,100.00\n"),
                ("inv.csv", "po_number,line,quantity,unit_price\nPO1,1,-1,100.00\n"),
                ("rec.csv", "po_number,line,quantity\nPO1,1,1\n"),
            ]
            inputs = []
            for name, body in fixtures:
                path = root / name
                path.write_text(body, encoding="utf-8")
                inputs.append(str(path))
            with localcontext() as caller:
                set_hostile(caller)
                with self.assertRaises(ValueError):
                    engine.procure_guard(*inputs, str(root))
            self.assertFalse(list(root.glob("procurement-three-way-*.csv")))
            self.assertFalse(list(root.glob("evidence-manifest-*.txt")))


if __name__ == "__main__":
    unittest.main()
