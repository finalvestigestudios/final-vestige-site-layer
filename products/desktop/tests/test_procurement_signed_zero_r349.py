"""R349 direct-API procurement signed-zero source and parser custody.

Synthetic financial inputs. A signed zero changes the textual provenance of a
credit/return price even though Decimal(-0) == Decimal(0). No approval follows.
"""
from decimal import Decimal, Context, getcontext, localcontext
import unittest

from fvs_suite.procurement_numeric_result_r345 import checked_quantity, checked_unit_price


class SignedZeroCustodyR349(unittest.TestCase):
    def reject_without_callback(self, source):
        calls = []
        def parser(value):
            calls.append(value)
            return Decimal(0)
        with self.assertRaisesRegex(ValueError, "Procurement quantity") as error:
            checked_quantity(source, parser)
        self.assertEqual(calls, [])
        self.assertNotIn(str(source), str(error.exception))

    def reject_sign_change(self, checker, source, parsed):
        calls = []
        def parser(value):
            calls.append(value)
            return parsed
        with self.assertRaises(ValueError) as error:
            checker(source, parser)
        self.assertEqual(calls, [source])
        self.assertIsNone(error.exception.__cause__)
        self.assertNotIn(str(source), str(error.exception))

    def accept_sign(self, checker, source, parsed):
        actual = checker(source, lambda _: parsed)
        self.assertEqual(actual, parsed)
        if actual.is_zero():
            self.assertEqual(actual.is_signed(), parsed.is_signed())

    def test_negative_zero_quantity_plain_rejected_before_callback(self):
        self.reject_without_callback("-0")

    def test_negative_zero_quantity_fixed_rejected_before_callback(self):
        self.reject_without_callback("-0.00")

    def test_negative_zero_quantity_exponent_rejected_before_callback(self):
        self.reject_without_callback("-0E-8")

    def test_negative_zero_quantity_max_scale_rejected_before_callback(self):
        self.reject_without_callback("-0.00000000")

    def test_negative_zero_quantity_decimal_rejected_before_callback(self):
        self.reject_without_callback(Decimal("-0"))

    def test_negative_zero_quantity_decimal_exponent_rejected_before_callback(self):
        self.reject_without_callback(Decimal("-0E+8"))

    def test_negative_zero_quantity_plus_is_accepted(self):
        self.accept_sign(checked_quantity, "+0", Decimal(0))

    def test_positive_zero_quantity_fixed_is_accepted(self):
        self.accept_sign(checked_quantity, "0.00000000", Decimal("0.00000000"))

    def test_positive_zero_quantity_decimal_is_accepted(self):
        self.accept_sign(checked_quantity, Decimal("0E-8"), Decimal("0E-8"))

    def test_positive_zero_quantity_normalized_to_negative_is_rejected(self):
        self.reject_sign_change(checked_quantity, "0", Decimal("-0"))

    def test_positive_zero_quantity_integer_normalized_to_negative_rejected(self):
        self.reject_sign_change(checked_quantity, 0, Decimal("-0"))

    def test_positive_zero_quantity_scaled_normalized_to_negative_rejected(self):
        self.reject_sign_change(checked_quantity, "0.000", Decimal("-0.000"))

    def test_price_negative_zero_plain_to_positive_rejected(self):
        self.reject_sign_change(checked_unit_price, "-0", Decimal(0))

    def test_price_negative_zero_accounting_to_positive_rejected(self):
        self.reject_sign_change(checked_unit_price, "($0.00)", Decimal("0.00"))

    def test_price_negative_zero_prefix_currency_to_positive_rejected(self):
        self.reject_sign_change(checked_unit_price, "-$0.00", Decimal(0))

    def test_price_negative_zero_currency_prefix_to_positive_rejected(self):
        self.reject_sign_change(checked_unit_price, "$-0.00", Decimal(0))

    def test_price_negative_zero_decimal_to_positive_rejected(self):
        self.reject_sign_change(checked_unit_price, Decimal("-0"), Decimal(0))

    def test_price_positive_zero_to_negative_rejected(self):
        self.reject_sign_change(checked_unit_price, "0", Decimal("-0"))

    def test_price_positive_currency_zero_to_negative_rejected(self):
        self.reject_sign_change(checked_unit_price, "$0.00", Decimal("-0"))

    def test_price_negative_zero_accounting_sign_preserved(self):
        self.accept_sign(checked_unit_price, "($0.00)", Decimal("-0.00"))

    def test_price_negative_zero_minus_sign_preserved(self):
        self.accept_sign(checked_unit_price, "-0", Decimal("-0"))

    def test_price_negative_zero_currency_sign_preserved(self):
        self.accept_sign(checked_unit_price, "-$0.00", Decimal("-0"))

    def test_price_negative_zero_currency_minus_sign_preserved(self):
        self.accept_sign(checked_unit_price, "$-0.00", Decimal("-0"))

    def test_price_positive_zero_sign_preserved(self):
        self.accept_sign(checked_unit_price, "$0.00", Decimal("0"))

    def test_nonzero_exact_price_scale_compatible(self):
        self.accept_sign(checked_unit_price, "3.000", Decimal("3"))

    def test_nonzero_signed_credit_price_still_allowed(self):
        self.accept_sign(checked_unit_price, "-1.25", Decimal("-1.250"))

    def test_nonzero_grouped_quantity_still_allowed(self):
        self.accept_sign(checked_quantity, "1,234.50", Decimal("1234.5"))

    def test_negative_zero_private_invalid_source_redacted(self):
        secret = "-0 C:\\Private\\finance.csv"
        with self.assertRaises(ValueError) as error:
            checked_quantity(secret, Decimal)
        self.assertNotIn("Private", str(error.exception))

    def test_rejected_negative_zero_does_not_change_decimal_context(self):
        with localcontext(Context(prec=64)):
            before = getcontext().copy()
            with self.assertRaises(ValueError):
                checked_quantity("-0", lambda _: Decimal("0"))
            self.assertEqual(getcontext().prec, before.prec)
            self.assertEqual(getcontext().flags, before.flags)

    def test_valid_signed_price_zero_does_not_poison_decimal_context(self):
        with localcontext(Context(prec=64)):
            before = getcontext().copy()
            def parser(_):
                getcontext().prec = 2
                return Decimal("-0")
            result = checked_unit_price("-0", parser)
            self.assertTrue(result.is_signed() and result.is_zero())
            self.assertEqual(getcontext().prec, before.prec)
            self.assertEqual(getcontext().flags, before.flags)

    def test_nonfinite_quantity_remains_rejected(self):
        with self.assertRaises(ValueError):
            checked_quantity("NaN", Decimal)

    def test_nonfinite_price_remains_rejected(self):
        with self.assertRaises(ValueError):
            checked_unit_price("Infinity", Decimal)


if __name__ == "__main__":
    unittest.main()
