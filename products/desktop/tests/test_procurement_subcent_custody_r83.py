"""R83: exact subcent procurement custody and consistent HALF_UP display.

Synthetic-only, offline regressions. No payment or compliance approvals.
The engine-level CSV test requires a complete repository checkout.
"""
from __future__ import annotations

import csv
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_EVEN, localcontext
from pathlib import Path
import tempfile
import unittest

from fvs_suite import engine, procurement


class ProcurementSubcentCustodyR83(unittest.TestCase):
    def review(self, invoice_price="0.005", *, order_price="0.005",
               invoice_qty="1", order_qty="1", credit_price=None):
        ordered = [{"quantity": order_qty, "unit_price": order_price}]
        invoices = [{"quantity": invoice_qty, "unit_price": invoice_price,
                     "event_type": "invoice", "document_id": "INV-1"}]
        if credit_price is not None:
            invoices.append({"quantity": "1", "unit_price": credit_price,
                             "event_type": "credit", "document_id": "CM-1",
                             "related_document": "INV-1"})
        receipts = [{"quantity": invoice_qty, "event_type": "receipt",
                     "document_id": "REC-1"}]
        return procurement.review_line(
            ordered, invoices, receipts, quantity=engine.qty,
            unit_cost=engine.unit_cost, identifier=engine.key,
            policy=procurement.PricePolicy())

    def test_positive_half_cent_ties_are_half_up(self):
        values = (("0.005", "0.01"), ("0.015", "0.02"),
                  ("0.025", "0.03"), ("0.035", "0.04"))
        for raw, expected in values:
            with self.subTest(raw=raw):
                self.assertEqual(procurement._display_money(Decimal(raw)), expected)

    def test_negative_half_cent_ties_are_away_from_zero(self):
        for raw, expected in (("-0.005", "-0.01"),
                              ("-0.015", "-0.02"), ("-0.025", "-0.03")):
            with self.subTest(raw=raw):
                self.assertEqual(procurement._display_money(Decimal(raw)), expected)

    def test_non_ties_do_not_round_up(self):
        self.assertEqual(procurement._display_money(Decimal("0.00499999")), "0.00")
        self.assertEqual(procurement._display_money(Decimal("-0.00499999")), "-0.00")
        self.assertEqual(procurement._display_money(Decimal("0.00500001")), "0.01")

    def test_display_rounding_is_independent_of_decimal_context(self):
        for rounding in (ROUND_HALF_EVEN, ROUND_DOWN):
            with self.subTest(rounding=rounding), localcontext() as ctx:
                ctx.rounding = rounding
                self.assertEqual(procurement._display_money(Decimal("0.005")), "0.01")
                self.assertEqual(procurement._display_money(Decimal("-0.005")), "-0.01")

    def test_engine_money_and_display_use_same_tie_break(self):
        for raw in ("0.005", "1.005", "-0.005", "-1.005"):
            with self.subTest(raw=raw):
                self.assertEqual(engine.dollars(Decimal(raw)),
                                 format(engine.money(raw), ".2f"))

    def test_half_cent_invoice_preserves_exact_evidence(self):
        metrics, flags = self.review()
        self.assertEqual(metrics["invoice_total"], "0.01")
        self.assertEqual(metrics["invoice_total_exact"], "0.005")
        self.assertEqual(metrics["gross_invoice_total"], "0.01")
        self.assertEqual(metrics["gross_invoice_total_exact"], "0.005")
        self.assertEqual(metrics["credit_value_exact"], "0")
        self.assertEqual(flags, [])

    def test_negative_subcent_price_is_visible_and_reviewed(self):
        metrics, flags = self.review(invoice_price="-0.005")
        self.assertEqual(metrics["invoice_total"], "-0.01")
        self.assertEqual(metrics["invoice_total_exact"], "-0.005")
        self.assertIn("negative_unit_price_review", flags)

    def test_small_exact_amount_not_conflated_with_zero(self):
        metrics, flags = self.review(invoice_price="0.00000001",
                                     order_price="0.00000001")
        self.assertEqual(metrics["invoice_total"], "0.00")
        self.assertEqual(metrics["invoice_total_exact"], "0.00000001")
        self.assertEqual(metrics["gross_invoice_total_exact"], "0.00000001")
        self.assertEqual(flags, [])

    def test_credit_and_gross_ties_round_separately(self):
        metrics, flags = self.review(invoice_price="0.015", order_price="0.015",
                                     credit_price="0.005")
        self.assertEqual(metrics["gross_invoice_total_exact"], "0.015")
        self.assertEqual(metrics["credit_value_exact"], "0.005")
        self.assertEqual(metrics["invoice_total_exact"], "0.010")
        self.assertEqual(metrics["gross_invoice_total"], "0.02")
        self.assertEqual(metrics["credit_value"], "0.01")
        self.assertEqual(metrics["invoice_total"], "0.01")
        self.assertIn("credit_memo_review", flags)

    def test_offsetting_ties_retain_both_gross_evidence_fields(self):
        metrics, flags = self.review(credit_price="0.005")
        self.assertEqual(metrics["invoice_total"], "0.00")
        self.assertEqual(metrics["invoice_total_exact"], "0.000")
        self.assertEqual(metrics["gross_invoice_total_exact"], "0.005")
        self.assertEqual(metrics["credit_value_exact"], "0.005")
        self.assertIn("credit_memo_review", flags)

    def test_price_variance_uses_exact_amounts_not_display(self):
        metrics, flags = self.review(invoice_price="0.025", order_price="0.005")
        self.assertEqual(metrics["invoice_total"], "0.03")
        self.assertEqual(metrics["invoice_total_exact"], "0.025")
        self.assertIn("price_variance_above_2pct", flags)

    def test_invoice_total_exact_uses_decimal_not_scientific_notation(self):
        metrics, _ = self.review(invoice_price="0.00000001",
                                 order_price="0.00000001", invoice_qty="100")
        self.assertEqual(metrics["invoice_total_exact"], "0.00000100")
        self.assertNotIn("E", metrics["invoice_total_exact"])

    def test_end_to_end_export_retains_originals_and_exact_columns(self):
        with tempfile.TemporaryDirectory(prefix="fvs-r83-") as directory:
            root = Path(directory)
            fixtures = (
                ("po.csv", ("po_number", "line", "quantity", "unit_price"),
                 (("PO1", "1", "1", "0.005"),)),
                ("inv.csv", ("po_number", "line", "quantity", "unit_price"),
                 (("PO1", "1", "1", "0.005"),)),
                ("rec.csv", ("po_number", "line", "quantity"),
                 (("PO1", "1", "1"),)),
            )
            paths = []
            originals = []
            for name, headers, rows in fixtures:
                file = root / name
                with file.open("w", newline="", encoding="utf-8") as stream:
                    writer = csv.writer(stream)
                    writer.writerow(headers)
                    writer.writerows(rows)
                paths.append(file)
                originals.append(file.read_bytes())

            outputs = engine.procure_guard(*(str(path) for path in paths), str(root))
            self.assertEqual(len(outputs), 2)
            with outputs[0].open("r", newline="", encoding="utf-8-sig") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["status"], "matched")
            self.assertEqual(row["invoice_total"], "0.01")
            self.assertEqual(row["invoice_total_exact"], "0.005")
            self.assertEqual(row["gross_invoice_total_exact"], "0.005")
            self.assertEqual(row["credit_value_exact"], "0")
            self.assertEqual(row["po_rows"], "2")
            self.assertEqual(row["invoice_rows"], "2")
            self.assertEqual(row["receipt_rows"], "2")
            self.assertTrue(row["price_policy_sha256"])
            self.assertTrue(outputs[1].exists())
            self.assertEqual([path.read_bytes() for path in paths], originals)


if __name__ == "__main__":
    unittest.main()
