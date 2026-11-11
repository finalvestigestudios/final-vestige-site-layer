"""R348: preserve zero sign in ProcureGuard source and callback custody.

Only synthetic values. A zero quantity with a minus sign is not valid CSV
quantity grammar, and an accounting negative-zero unit price retains its
sign as evidence even when its numerical value compares equal to +0.
"""
from decimal import Decimal, localcontext
import unittest

from fvs_suite.procurement_numeric_result_r345 import checked_quantity, checked_unit_price


class SignedZeroCustodyR348(unittest.TestCase):
    def rejected_pre_callback(self, function, source):
        calls = []
        def callback(_):
            calls.append(True)
            return Decimal("0")
        with self.assertRaises(ValueError) as caught:
            function(source, callback)
        self.assertEqual(calls, [], "invalid source reached custom parser")
        self.assertIsNone(caught.exception.__cause__)
        self.assertNotIn(str(source), str(caught.exception))

    def rejected_post_callback(self, function, source, value):
        calls = []
        def callback(_):
            calls.append(True)
            return Decimal(value)
        with self.assertRaises(ValueError) as caught:
            function(source, callback)
        self.assertEqual(calls, [True])
        self.assertIsNone(caught.exception.__cause__)

    def exact(self, function, source, parsed, *, signed):
        actual = function(source, lambda _: Decimal(parsed))
        self.assertEqual(actual, Decimal(0))
        self.assertEqual(actual.is_signed(), signed)

    # A minus sign on a quantity is an invalid physical source token, even
    # when it has numeric value zero (engine.qty rejects signed-zero strings).
    def test_negative_zero_quantity_string(self):
        self.rejected_pre_callback(checked_quantity, "-0")

    def test_negative_zero_quantity_fractional_string(self):
        self.rejected_pre_callback(checked_quantity, "-0.000")

    def test_negative_zero_quantity_dot_prefix(self):
        self.rejected_pre_callback(checked_quantity, "-.0")

    def test_negative_zero_quantity_scientific(self):
        self.rejected_pre_callback(checked_quantity, "-0E+3")

    def test_negative_zero_quantity_scientific_fraction(self):
        self.rejected_pre_callback(checked_quantity, "-0.0e-3")

    def test_negative_zero_quantity_native_decimal(self):
        self.rejected_pre_callback(checked_quantity, Decimal("-0"))

    def test_negative_zero_quantity_native_decimal_scaled(self):
        self.rejected_pre_callback(checked_quantity, Decimal("-0.00000000"))

    def test_negative_integer_quantity_still_rejected(self):
        self.rejected_pre_callback(checked_quantity, -1)

    # Numeric Decimal equality is not a sufficient representation check for
    # zero: a callback can silently reverse its sign without changing totals.
    def test_positive_quantity_callback_negative_zero_rejected(self):
        self.rejected_post_callback(checked_quantity, "0", "-0")

    def test_positive_fractional_quantity_callback_negative_zero_rejected(self):
        self.rejected_post_callback(checked_quantity, "0.000", "-0.00")

    def test_native_quantity_callback_negative_zero_rejected(self):
        self.rejected_post_callback(checked_quantity, Decimal(0), "-0")

    def test_grouped_quantity_zero_callback_negative_zero_rejected(self):
        self.rejected_post_callback(checked_quantity, "0,000", "-0")

    def test_positive_quantity_zero_still_accepted(self):
        self.exact(checked_quantity, "0", "0", signed=False)

    def test_positive_quantity_fractional_zero_still_accepted(self):
        self.exact(checked_quantity, "0.00000000", "0", signed=False)

    def test_native_quantity_zero_still_accepted(self):
        self.exact(checked_quantity, Decimal("0.0"), "0", signed=False)

    def test_grouped_quantity_zero_still_accepted(self):
        self.exact(checked_quantity, "0,000", "0", signed=False)

    def test_nonzero_quantity_callback_not_affected(self):
        self.assertEqual(checked_quantity("1,234.50", lambda _: Decimal("1234.500")), Decimal("1234.5"))

    def test_negative_accounting_price_zero_retains_sign(self):
        self.exact(checked_unit_price, "($0.00)", "-0", signed=True)

    def test_negative_currency_price_zero_retains_sign(self):
        self.exact(checked_unit_price, "$-0.00", "-0", signed=True)

    def test_negative_plain_price_zero_retains_sign(self):
        self.exact(checked_unit_price, "-0", "-0", signed=True)

    def test_native_negative_price_zero_retains_sign(self):
        self.exact(checked_unit_price, Decimal("-0.0"), "-0", signed=True)

    def test_negative_accounting_price_sign_flip_rejected(self):
        self.rejected_post_callback(checked_unit_price, "($0.00)", "0")

    def test_negative_currency_price_sign_flip_rejected(self):
        self.rejected_post_callback(checked_unit_price, "$-0.00", "0")

    def test_native_negative_price_sign_flip_rejected(self):
        self.rejected_post_callback(checked_unit_price, Decimal("-0"), "0")

    def test_positive_price_sign_flip_rejected(self):
        self.rejected_post_callback(checked_unit_price, "$0.00", "-0")

    def test_native_positive_price_sign_flip_rejected(self):
        self.rejected_post_callback(checked_unit_price, Decimal("0"), "-0")

    def test_positive_price_zero_still_accepted(self):
        self.exact(checked_unit_price, "$+0.00", "0", signed=False)

    def test_context_low_precision_does_not_erode_zero_sign(self):
        with localcontext() as context:
            context.prec = 2
            self.exact(checked_unit_price, "($0.00000000)", "-0", signed=True)
            self.rejected_post_callback(checked_unit_price, "($0.00000000)", "0")
            self.assertEqual(context.prec, 2)

    def test_private_callback_exception_message_not_reflected(self):
        def secret(_):
            raise OSError("PRIVATE_CUSTOMER_PATH")
        with self.assertRaises(ValueError) as caught:
            checked_unit_price("($0.00)", secret)
        self.assertIsNone(caught.exception.__cause__)
        self.assertNotIn("PRIVATE_CUSTOMER_PATH", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
