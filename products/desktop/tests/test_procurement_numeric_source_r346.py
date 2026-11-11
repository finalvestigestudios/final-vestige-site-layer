"""R346: pre-callback source custody, exact native numeric binding.

All identifiers and records are synthetic. Exercises the authentic R346 helper
with no network, repository fixtures, premium binaries or user financial data.
"""
from decimal import Decimal, localcontext
import unittest

from fvs_suite.procurement_numeric_result_r345 import checked_quantity, checked_unit_price


class NumericSourceCustodyR346(unittest.TestCase):
    def reject_before_callback(self, function, value):
        called = []
        def parser(_):
            called.append(True)
            return Decimal("1")
        with self.assertRaises(ValueError) as caught:
            function(value, parser)
        self.assertEqual(called, [])
        self.assertIsNone(caught.exception.__cause__)
        self.assertNotIn("SECRET_PATH", str(caught.exception))

    def reject_after_callback(self, function, value, result):
        called = []
        def parser(_):
            called.append(True)
            return result
        with self.assertRaises(ValueError) as caught:
            function(value, parser)
        self.assertEqual(called, [True])
        self.assertIsNone(caught.exception.__cause__)

    def test_source_str_exact_80_character_budget(self):
        self.assertEqual(checked_quantity("1" + " " * 79, lambda _: Decimal(1)), Decimal(1))

    def test_reject_overlong_quantity_without_callback(self):
        self.reject_before_callback(checked_quantity, "1" + " " * 80)

    def test_reject_large_price_literal_without_callback(self):
        self.reject_before_callback(checked_unit_price, "9" * 100_000)

    def test_reject_empty_before_callback(self):
        self.reject_before_callback(checked_quantity, "")

    def test_reject_whitespace_before_callback(self):
        self.reject_before_callback(checked_unit_price, " " * 10)

    def test_reject_embedded_nul_before_callback(self):
        self.reject_before_callback(checked_quantity, "1\0")

    def test_reject_newline_before_callback(self):
        self.reject_before_callback(checked_unit_price, "1\n")

    def test_reject_tab_before_callback(self):
        self.reject_before_callback(checked_quantity, "1\t")

    def test_reject_del_before_callback(self):
        self.reject_before_callback(checked_unit_price, "1\x7f")

    def test_reject_nonfinite_native_decimal_before_callback(self):
        self.reject_before_callback(checked_unit_price, Decimal("NaN"))

    def test_reject_infinite_native_decimal_before_callback(self):
        self.reject_before_callback(checked_quantity, Decimal("Infinity"))

    def test_reject_giant_exponent_native_zero_before_callback(self):
        self.reject_before_callback(checked_quantity, Decimal("0E-10000"))

    def test_reject_giant_coefficient_before_callback(self):
        self.reject_before_callback(checked_unit_price, Decimal("0." + "0" * 100))

    def test_reject_negative_source_quantity_even_with_forgiving_parser(self):
        self.reject_before_callback(checked_quantity, Decimal("-5"))

    def test_reject_price_source_above_limit_even_with_forgiving_parser(self):
        self.reject_before_callback(checked_unit_price, Decimal("1000000000001"))

    def test_reject_number_rewritten_by_callback(self):
        self.reject_after_callback(checked_quantity, "3", Decimal(4))

    def test_reject_fraction_rewritten_by_callback(self):
        self.reject_after_callback(checked_unit_price, "0.00000001", Decimal("0.00000002"))

    def test_reject_native_decimal_rewritten_by_callback(self):
        self.reject_after_callback(checked_quantity, Decimal("3"), Decimal(2))

    def test_reject_native_integer_rewritten_by_callback(self):
        self.reject_after_callback(checked_unit_price, 4, Decimal(3))

    def test_reject_scientific_notation_rewritten_by_callback(self):
        self.reject_after_callback(checked_quantity, "1E+5", Decimal("2E+5"))

    def test_reject_nan_source_string_even_if_callback_maps_it(self):
        self.reject_before_callback(checked_quantity, "NaN")

    def test_reject_infinite_source_string_even_if_callback_maps_it(self):
        self.reject_before_callback(checked_unit_price, "Infinity")

    def test_reject_negative_quantity_source_string_even_if_callback_maps_it(self):
        self.reject_before_callback(checked_quantity, "-3")

    def test_accept_equal_numeric_value_different_exponent(self):
        self.assertEqual(checked_quantity("3.000", lambda _: Decimal(3)), Decimal(3))

    def test_accept_ordinary_exponent_string(self):
        self.assertEqual(checked_quantity("1E+5", Decimal), Decimal("1E+5"))

    def test_accept_signed_price_exact(self):
        self.assertEqual(checked_unit_price("-5.50", Decimal), Decimal("-5.50"))

    def test_accounting_style_remains_available_for_existing_parser(self):
        self.assertEqual(checked_unit_price("($1,234.50)", lambda _: Decimal("-1234.50")), Decimal("-1234.50"))

    def test_grouped_quantity_remains_available_for_existing_parser(self):
        self.assertEqual(checked_quantity("1,234.5", lambda _: Decimal("1234.5")), Decimal("1234.5"))

    def test_context_precision_does_not_change_equality_check(self):
        with localcontext() as context:
            context.prec = 4
            self.assertEqual(checked_unit_price("0.12345678", Decimal), Decimal("0.12345678"))
            self.reject_after_callback(checked_unit_price, "0.12345678", Decimal("0.12345677"))
            self.assertEqual(context.prec, 4)

    def test_private_content_not_echoed(self):
        self.reject_before_callback(checked_unit_price, "SECRET_PATH" * 100)

    def test_int_max_budget_not_regressed(self):
        self.reject_before_callback(checked_quantity, 10**300)


if __name__ == "__main__":
    unittest.main()
