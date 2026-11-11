"""R356 isolated source-money custody tests (no network, synthetic values)."""
from __future__ import annotations
from decimal import Context, Decimal, Inexact, ROUND_DOWN, getcontext, localcontext
import unittest

from fvs_suite.spend_source_custody_r356 import (canonical_spend_source_cents,
                                               spend_parser_preserves_source)


class SpendSourceCustodyR356(unittest.TestCase):
    def test_grouped_price(self):
        self.assertEqual(canonical_spend_source_cents("$1,234.50"), Decimal("1234.50"))

    def test_leading_currency_sign(self):
        self.assertEqual(canonical_spend_source_cents("-$1,234.50"), Decimal("-1234.50"))

    def test_late_currency_sign(self):
        self.assertEqual(canonical_spend_source_cents("$-1,234.50"), Decimal("-1234.50"))

    def test_parentheses(self):
        self.assertEqual(canonical_spend_source_cents("($1,234.50)"), Decimal("-1234.50"))

    def test_trailing_decimal_point(self):
        self.assertEqual(canonical_spend_source_cents("12."), Decimal("12.00"))

    def test_leading_decimal_point(self):
        self.assertEqual(canonical_spend_source_cents(".125"), Decimal("0.13"))

    def test_half_up_rounding(self):
        self.assertEqual(canonical_spend_source_cents("0.005"), Decimal("0.01"))
        self.assertEqual(canonical_spend_source_cents("(0.005)"), Decimal("-0.01"))

    def test_round_down_case(self):
        self.assertEqual(canonical_spend_source_cents("1.004"), Decimal("1.00"))

    def test_whitespace(self):
        self.assertEqual(canonical_spend_source_cents("  ($1,000) \t"), Decimal("-1000.00"))

    def test_maximum_amount(self):
        self.assertEqual(canonical_spend_source_cents("1,000,000,000,000"), Decimal("1000000000000.00"))

    def test_outside_maximum(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_cents("1,000,000,000,000.01")

    def test_rejects_float_and_decimal_subclasses(self):
        for value in (100.0, Decimal("100"), None, [], b"100"):
            with self.subTest(value=type(value).__name__), self.assertRaises(ValueError):
                canonical_spend_source_cents(value)

    def test_rejects_unsafe_numeric_syntax(self):
        for value in ("1,23.00", "1,234,5", "1_000", "1e3", "NaN", "Infinity",
                      "(+100)", "(-100)", "1$", "--3", "(+ $3)",
                      "1,2,3", "", "()", "($+20)", "$-+5", "٠١", "- 12"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                canonical_spend_source_cents(value)

    def test_rejects_unbalanced_accounting(self):
        for value in ("($20", "$20)", "($20))", "((20)"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                canonical_spend_source_cents(value)

    def test_rejects_oversized_source(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_cents("1" * 81)

    def test_never_returns_float(self):
        self.assertIs(type(canonical_spend_source_cents("999999999999.99")), Decimal)

    def test_source_mutation_detected(self):
        self.assertFalse(spend_parser_preserves_source(Decimal("100.00"), Decimal("1000.00")))

    def test_zero_sign_loss_detected(self):
        self.assertFalse(spend_parser_preserves_source(Decimal("-0.00"), Decimal("0.00")))

    def test_zero_sign_invention_detected(self):
        self.assertFalse(spend_parser_preserves_source(Decimal("0.00"), Decimal("-0.00")))

    def test_zero_preserved(self):
        self.assertTrue(spend_parser_preserves_source(Decimal("-0.00"), Decimal("-0.00")))
        self.assertTrue(spend_parser_preserves_source(Decimal("0.00"), Decimal("0.00")))

    def test_same_number_different_scale_is_safe(self):
        self.assertTrue(spend_parser_preserves_source(Decimal("1.00"), Decimal("1.0")))

    def test_same_cents_rounding_is_safe(self):
        self.assertTrue(spend_parser_preserves_source(
            canonical_spend_source_cents("1.005"), Decimal("1.01")))

    def test_reject_non_decimal_parser(self):
        for value in (1, 1.0, "1.00", None, True):
            with self.subTest(value=type(value).__name__):
                self.assertFalse(spend_parser_preserves_source(Decimal("1.00"), value))

    def test_reject_nonfinite_parser(self):
        for value in (Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")):
            self.assertFalse(spend_parser_preserves_source(Decimal("1.00"), value))

    def test_is_independent_of_hostile_context(self):
        with localcontext(Context(prec=2)) as context:
            context.traps[Inexact] = True
            self.assertEqual(canonical_spend_source_cents("999999999999.99"), Decimal("999999999999.99"))
            self.assertEqual(getcontext().prec, 2)

    def test_no_original_input_in_errors(self):
        for value in ("SENSITIVE 1234", "SENSITIVE 1234)"):
            with self.assertRaises(ValueError) as caught:
                canonical_spend_source_cents(value)
            self.assertNotIn("SENSITIVE", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
