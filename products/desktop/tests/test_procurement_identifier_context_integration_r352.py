"""R352 full ProcureGuard review tests: run only with complete fvs_suite checkout.

Synthetic PO/receipt/invoice rows, no private data or compliance authorization.
"""
from __future__ import annotations

from decimal import (Context, Decimal, DivisionByZero, Inexact, ROUND_DOWN,
                     getcontext, setcontext)
import unittest

from fvs_suite.identity_inputs import normalize_key
from fvs_suite.procurement import PricePolicy, review_line


def row(quantity="3", price="0.12345678", kind="", doc=""):
    return {"quantity": quantity, "unit_price": price, "row": "2",
            "event_type": kind, "document_id": doc, "related_document": ""}


def run(identifier=normalize_key, *, invoice_price="0.12345678"):
    return review_line(
        [row()],
        [row(price=invoice_price, kind="invoice", doc="INV-1")],
        [row(kind="receipt", doc="REC-1")],
        quantity=Decimal, unit_cost=Decimal, identifier=identifier,
        policy=PricePolicy())


def mutation_precision(value):
    getcontext().prec = 1
    return normalize_key(value)


def mutation_rounding(value):
    getcontext().prec = 1
    getcontext().rounding = ROUND_DOWN
    return normalize_key(value)


def mutation_replace(value):
    setcontext(Context(prec=1, rounding=ROUND_DOWN))
    return normalize_key(value)


def mutation_traps(value):
    getcontext().traps[Inexact] = True
    getcontext().traps[DivisionByZero] = False
    return normalize_key(value)


class ProcureGuardIdentifierContextIntegrationR352(unittest.TestCase):
    def assert_same_as_baseline(self, callback):
        expected = run()
        observed = run(identifier=callback)
        self.assertEqual(observed, expected)
        self.assertEqual(observed[0]["invoice_total_exact"], "0.37037034")
        self.assertNotIn("price_variance_above_2pct", observed[1])

    def test_precision_poison_cannot_introduce_false_variance(self):
        self.assert_same_as_baseline(mutation_precision)

    def test_rounding_poison_cannot_introduce_false_variance(self):
        self.assert_same_as_baseline(mutation_rounding)

    def test_setcontext_cannot_introduce_false_variance(self):
        self.assert_same_as_baseline(mutation_replace)

    def test_trap_mutation_cannot_affect_review(self):
        self.assert_same_as_baseline(mutation_traps)

    def test_real_price_variance_still_flagged(self):
        _, flags = run(identifier=mutation_precision, invoice_price="0.22345678")
        self.assertIn("price_variance_above_2pct", flags)

    def test_valid_identifier_is_still_called_for_source_docs(self):
        calls = []
        def watch(value):
            calls.append(value)
            return normalize_key(value)
        observed = run(identifier=watch)
        self.assertIn("INV-1", calls)
        self.assertIn("REC-1", calls)
        self.assertEqual(observed, run())

    def test_private_identifier_error_does_not_echo_input(self):
        def fail(_):
            getcontext().prec = 1
            raise OSError("PRIVATE_FINANCIAL_CUSTOMER_PATH")
        with self.assertRaises(ValueError) as caught:
            run(identifier=fail)
        self.assertNotIn("PRIVATE_FINANCIAL_CUSTOMER_PATH", str(caught.exception))
        self.assertTrue(caught.exception.__suppress_context__)

    def test_repeated_calls_stay_deterministic(self):
        first = run(identifier=mutation_precision)
        second = run(identifier=mutation_precision)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
