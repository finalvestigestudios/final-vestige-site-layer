"""R5 procurement policy, partial invoices, explicit credits and returns."""
from __future__ import annotations
import json
import unittest
import tempfile
from decimal import Decimal
from pathlib import Path
from fvs_suite.procurement import PricePolicy, load_price_policy, review_line


def qty(v):
    n = Decimal(str(v))
    if not n.is_finite() or n < 0:
        raise ValueError("Invalid quantity")
    return n


def price(v):
    n = Decimal(str(v))
    if not n.is_finite():
        raise ValueError("Nonfinite price")
    return n


def identifier(v):
    import re
    return re.sub(r"[^A-Z0-9]+", "", str(v).upper())


def record(quantity, unit=None, kind=None, doc=None, relates=None):
    return {
        "quantity": str(quantity), "unit_price": "" if unit is None else str(unit),
        "event_type": kind or "", "document_id": doc or "",
        "related_document": relates or "", "row": "2",
    }


def audit(po, inv, rec, policy=PricePolicy()):
    return review_line(po, inv, rec, quantity=qty, unit_cost=price,
                       identifier=identifier, policy=policy)


class PremiumRuleTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)

    def config(self, data, raw=None):
        p = self.root / "review.json"
        p.write_text(raw if raw is not None else json.dumps(data), encoding="utf-8")
        return p

    def test_legacy_match(self):
        data, flags = audit([record(2, 5)], [record(2, 5)], [record(2)])
        self.assertEqual(flags, [])
        self.assertEqual(data["invoice_total"], "10.00")

    def test_partial_installment_requires_review(self):
        data, flags = audit([record(10, 12)], [record(4, 12, doc="INV1")], [record(4)])
        self.assertIn("partial_invoice_review", flags)
        self.assertIn("partial_receipt_review", flags)
        self.assertEqual(data["invoiced_qty"], "4")

    def test_two_equal_installments_distinct_documents_not_duplicate(self):
        data, flags = audit([record(10, 5)],
                            [record(5, 5, doc="A"), record(5, 5, doc="B")],
                            [record(10)])
        self.assertNotIn("possible_duplicate_invoice_line", flags)
        self.assertEqual(data["invoice_total"], "50.00")
        self.assertEqual(flags, [])

    def test_two_equal_installments_without_ids_flag_duplicate(self):
        _, flags = audit([record(10, 5)], [record(5, 5), record(5, 5)], [record(10)])
        self.assertIn("possible_duplicate_invoice_line", flags)

    def test_repeated_invoice_document_id_flag(self):
        _, flags = audit([record(10, 5)],
                         [record(5, 5, doc="INV1"), record(5, 5, doc="inv-1")],
                         [record(10)])
        self.assertIn("repeated_invoice_document_id_review", flags)

    def test_linked_credit_offsets_quantity_value_but_not_review(self):
        data, flags = audit([record(10, 5)],
                            [record(10, 5, doc="INV-1"),
                             record(2, 5, kind="credit", doc="CM1", relates="INV1")],
                            [record(10)])
        self.assertIn("credit_memo_review", flags)
        self.assertNotIn("unlinked_credit_review", flags)
        self.assertEqual(
            (data["gross_invoice_qty"], data["credit_qty"], data["invoiced_qty"]),
            ("10", "2", "8"))
        self.assertEqual(
            (data["gross_invoice_total"], data["credit_value"], data["invoice_total"]),
            ("50.00", "10.00", "40.00"))

    def test_unlinked_credit_flagged(self):
        _, flags = audit([record(10, 5)],
                         [record(10, 5, doc="INV1"),
                          record(1, 5, kind="credit", doc="CM1", relates="WRONG")],
                         [record(10)])
        self.assertIn("unlinked_credit_review", flags)

    def test_missing_credit_reference_flagged(self):
        _, flags = audit([record(10, 5)],
                         [record(10, 5, doc="INV1"),
                          record(1, 5, kind="credit")], [record(10)])
        self.assertIn("unlinked_credit_review", flags)

    def test_over_credit_flagged(self):
        data, flags = audit([record(10, 5)],
                            [record(2, 5, doc="A"),
                             record(5, 5, kind="credit", doc="C", relates="A")],
                            [record(2)])
        self.assertIn("credit_exceeds_invoice_review", flags)
        self.assertEqual(data["invoiced_qty"], "-3")

    def test_return_nets_receipts_but_stays_review(self):
        data, flags = audit([record(10, 5)], [record(9, 5)],
                            [record(10), record(3, kind="return", doc="RT-1")])
        self.assertEqual(data["received_qty"], "7")
        self.assertIn("return_review", flags)
        self.assertIn("invoiced_above_received", flags)

    def test_unidentified_return_flagged(self):
        _, flags = audit([record(10, 5)], [record(10, 5)],
                         [record(10), record(1, kind="return")])
        self.assertIn("unidentified_return_review", flags)

    def test_invalid_event_type_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unsupported invoice event_type"):
            audit([record(10, 5)], [record(10, 5, kind="adjustment")], [record(10)])
        with self.assertRaisesRegex(ValueError, "Unsupported receipt event_type"):
            audit([record(10, 5)], [record(10, 5)], [record(10, kind="credit")])

    def test_negative_numeric_quantity_rejected(self):
        with self.assertRaises(ValueError):
            audit([record(10, 5)], [record(-1, 5, kind="credit")], [record(10)])

    def test_subcent_extended_value(self):
        data, flags = audit([record(1000, "0.005")],
                            [record(1000, "0.005")], [record(1000)])
        self.assertEqual(data["invoice_total"], "5.00")
        self.assertEqual(flags, [])

    def test_per_line_offsetting_prices_still_flagged(self):
        data, flags = audit([record(10, 10)],
                            [record(5, 5), record(5, 15)], [record(10)])
        self.assertIn("price_variance_above_2pct", flags)
        self.assertEqual(data["invoice_total"], "100.00")

    def test_custom_stricter_tolerance(self):
        p = self.config({"version": 1, "price_absolute": "0.00",
                         "price_fraction": "0.001"})
        policy = load_price_policy(p)
        _, flags = audit([record(1, 10)], [record(1, "10.10")], [record(1)], policy)
        self.assertIn("price_variance_above_policy", flags)
        self.assertNotIn("widened_price_policy_review", flags)
        self.assertEqual(len(policy.source_sha256), 64)

    def test_custom_widened_policy_never_silent_match(self):
        policy = PricePolicy(Decimal("2"), Decimal("0.10"))
        _, flags = audit([record(1, 10)], [record(1, 11)], [record(1)], policy)
        self.assertIn("widened_price_policy_review", flags)
        self.assertNotIn("price_variance_above_policy", flags)

    def test_return_requires_original_receipt_reference(self):
        _, flags = audit([record(10, 5)], [record(9, 5)],
                         [record(10, doc="RC-1"),
                          record(1, kind="return", doc="RT1", relates="RC1")])
        self.assertNotIn("unlinked_return_review", flags)
        self.assertIn("normalized_return_link_review", flags)

    def test_return_with_wrong_reference_is_flagged(self):
        _, flags = audit([record(10, 5)], [record(9, 5)],
                         [record(10, doc="RC1"),
                          record(1, kind="return", doc="RT1", relates="OTHER")])
        self.assertIn("unlinked_return_review", flags)

    def test_credit_reference_normalization_is_visible(self):
        _, flags = audit([record(10, 5)],
                         [record(10, 5, doc="INV-1"),
                          record(1, 5, kind="credit", doc="CM1", relates="INV1")],
                         [record(10)])
        self.assertIn("normalized_credit_link_review", flags)
        self.assertNotIn("unlinked_credit_review", flags)

    def test_invalid_policy_rejected(self):
        variants = [
            ({"version": 1, "price_absolute": 0.5, "price_fraction": "0.02"}, "decimal string"),
            ({"version": 1, "price_absolute": "0.01", "price_fraction": "0.11"}, "between zero"),
            ({"version": 1, "price_absolute": "-0.01", "price_fraction": "0.02"}, "ASCII fixed-point"),
            ({"version": 1, "price_absolute": "NaN", "price_fraction": "0.02"}, "ASCII fixed-point"),
            ({"version": 1, "price_absolute": "0.01", "price_fraction": "0.02", "unexpected": 7}, "exactly"),
        ]
        for data, pattern in variants:
            with self.subTest(data=data):
                with self.assertRaisesRegex(ValueError, pattern):
                    load_price_policy(self.config(data))
        with self.assertRaisesRegex(ValueError, "exactly version=1"):
            load_price_policy(self.config({"version": 1.0,
                                           "price_absolute": "0.01",
                                           "price_fraction": "0.02"}))
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            load_price_policy(self.config({}, '{"version":1,"version":1,"price_absolute":"0.01","price_fraction":"0.02"}'))

    def test_empty_policy_is_default(self):
        self.assertEqual(load_price_policy(""), PricePolicy())
        self.assertEqual(len(PricePolicy().source_sha256), 64)


if __name__ == "__main__":
    unittest.main()
