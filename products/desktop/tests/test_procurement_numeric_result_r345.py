"""R345 offline callback-boundary regressions; synthetic inputs only."""
from __future__ import annotations

from decimal import Decimal, localcontext
import unittest

from fvs_suite.procurement_numeric_result_r345 import checked_quantity, checked_unit_price


class HostileText(str):
    calls = 0

    def __str__(self):
        type(self).calls += 1
        raise RuntimeError("PRIVATE_CLIENT_PATH")


class HostileInt(int):
    calls = 0

    def __str__(self):
        type(self).calls += 1
        raise RuntimeError("PRIVATE_CLIENT_PATH")


class HostileDecimal(Decimal):
    calls = 0

    def is_finite(self):
        type(self).calls += 1
        raise RuntimeError("PRIVATE_CLIENT_PATH")


class NumericCustodyR345(unittest.TestCase):
    def setUp(self):
        HostileText.calls = HostileInt.calls = HostileDecimal.calls = 0

    def reject(self, fn):
        with self.assertRaises(ValueError) as trapped:
            fn()
        self.assertNotIn("PRIVATE_CLIENT", str(trapped.exception))
        self.assertIsNone(trapped.exception.__cause__)
        self.assertEqual((HostileText.calls, HostileInt.calls, HostileDecimal.calls), (0, 0, 0))

    def test_quantity_plain_exact(self):
        self.assertEqual(checked_quantity("3.125", Decimal), Decimal("3.125"))

    def test_price_plain_subcent(self):
        self.assertEqual(checked_unit_price("0.00000001", Decimal), Decimal("0.00000001"))

    def test_price_negative_still_allowed_for_review(self):
        self.assertEqual(checked_unit_price("-10.25", Decimal), Decimal("-10.25"))

    def test_quantity_zero_allowed(self):
        self.assertEqual(checked_quantity("0", Decimal), Decimal(0))

    def test_quantity_native_decimal_input(self):
        self.assertEqual(checked_quantity(Decimal("1"), lambda v: v), Decimal(1))

    def test_price_native_integer_input(self):
        self.assertEqual(checked_unit_price(4, lambda v: Decimal(v)), Decimal(4))

    def test_quantity_upper_bound(self):
        self.assertEqual(checked_quantity("1000000000", Decimal), Decimal("1000000000"))

    def test_price_negative_lower_bound(self):
        self.assertEqual(checked_unit_price("-1000000000000", Decimal), Decimal("-1000000000000"))

    def test_trailing_zeroes_not_lost(self):
        self.assertEqual(checked_quantity("0.0000000100", Decimal), Decimal("0.0000000100"))

    def test_large_exact_integer_and_decimal(self):
        self.assertEqual(checked_unit_price("999999999999.99999999", Decimal), Decimal("999999999999.99999999"))

    def test_quantity_negative_rejected(self):
        self.reject(lambda: checked_quantity("-1", Decimal))

    def test_quantity_negative_zero_allowed(self):
        self.assertTrue(checked_quantity("-0", Decimal).is_zero())

    def test_quantity_above_maximum(self):
        self.reject(lambda: checked_quantity("1000000000.00000001", Decimal))

    def test_price_above_maximum(self):
        self.reject(lambda: checked_unit_price("1000000000000.00000001", Decimal))

    def test_price_below_minimum(self):
        self.reject(lambda: checked_unit_price("-1000000000000.00000001", Decimal))

    def test_quantity_ninth_fractional_digit(self):
        self.reject(lambda: checked_quantity("0.000000001", Decimal))

    def test_price_ninth_fractional_digit(self):
        self.reject(lambda: checked_unit_price("0.000000001", Decimal))

    def test_nonfinite_quantity_nan(self):
        self.reject(lambda: checked_quantity("NaN", Decimal))

    def test_nonfinite_price_infinity(self):
        self.reject(lambda: checked_unit_price("Infinity", Decimal))

    def test_nonfinite_price_negative_infinity(self):
        self.reject(lambda: checked_unit_price("-Infinity", Decimal))

    def test_nonfinite_quantity_snan(self):
        self.reject(lambda: checked_quantity("sNaN", Decimal))

    def test_float_input_rejected_before_parser(self):
        self.reject(lambda: checked_quantity(1.25, lambda _: self.fail("called")))

    def test_bool_input_rejected_before_parser(self):
        self.reject(lambda: checked_quantity(True, lambda _: self.fail("called")))

    def test_str_subclass_input_no_str_hook(self):
        self.reject(lambda: checked_unit_price(HostileText("1"), Decimal))

    def test_int_subclass_input_no_str_hook(self):
        self.reject(lambda: checked_quantity(HostileInt(1), Decimal))

    def test_decimal_subclass_input_no_hooks(self):
        self.reject(lambda: checked_unit_price(HostileDecimal("1"), Decimal))

    def test_decimal_subclass_callback_result_no_hooks(self):
        self.reject(lambda: checked_unit_price("1", lambda _: HostileDecimal("1")))

    def test_callback_float_result_rejected(self):
        self.reject(lambda: checked_unit_price("1.25", lambda _: 1.25))

    def test_callback_bool_result_rejected(self):
        self.reject(lambda: checked_quantity("1", lambda _: True))

    def test_callback_string_result_rejected(self):
        self.reject(lambda: checked_quantity("1", lambda _: "1"))

    def test_callback_exception_redacted(self):
        def fail(_):
            raise OSError("PRIVATE_CLIENT_PATH")
        self.reject(lambda: checked_unit_price("1", fail))

    def test_noncallable_callback_redacted(self):
        self.reject(lambda: checked_quantity("1", None))

    def test_low_precision_does_not_hide_price_limit_breach(self):
        with localcontext() as ctx:
            ctx.prec = 4
            self.reject(lambda: checked_unit_price("1000000000000.00000001", Decimal))

    def test_low_precision_does_not_hide_quantity_limit_breach(self):
        with localcontext() as ctx:
            ctx.prec = 4
            self.reject(lambda: checked_quantity("1000000000.00000001", Decimal))

    def test_caller_decimal_context_does_not_round_validation(self):
        with localcontext() as ctx:
            ctx.prec = 4
            self.assertEqual(checked_unit_price("0.00000001", Decimal), Decimal("0.00000001"))
            self.assertEqual(ctx.prec, 4)

    def test_source_object_not_mutated(self):
        source = Decimal("3.12000000")
        self.assertIs(checked_quantity(source, lambda v: v), source)

    def test_large_direct_int_rejected_before_parser(self):
        self.reject(lambda: checked_quantity(10**300, lambda _: self.fail("called")))

    def test_quantity_positive_exponent_within_bounds(self):
        self.assertEqual(checked_quantity("1E+5", Decimal), Decimal("1E+5"))

    def test_quantity_tiny_exponent_rejected_without_normalizing(self):
        self.reject(lambda: checked_quantity("1E-999999", Decimal))

    def test_price_zero_huge_negative_exponent_rejected(self):
        self.reject(lambda: checked_unit_price("0E-999999", Decimal))

    def test_zero_huge_positive_exponent_rejected(self):
        self.reject(lambda: checked_quantity("0E+999999", Decimal))

    def test_ordinary_zero_scale_remains_exact(self):
        self.assertEqual(checked_quantity("0.000000000000000", Decimal),
                         Decimal("0.000000000000000"))


if __name__ == "__main__":
    unittest.main()
