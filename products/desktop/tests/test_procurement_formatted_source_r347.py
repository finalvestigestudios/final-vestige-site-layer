"""R347: accounting-formatted sources cannot be laundered by numeric callbacks.

All inputs are synthetic. This helper suite uses no private files or network.
"""
from decimal import Decimal, localcontext
import unittest

from fvs_suite.procurement_numeric_result_r345 import checked_quantity, checked_unit_price


class AccountingSourceCustodyR347(unittest.TestCase):
    def assert_preflight_rejects(self, function, source):
        calls = []
        def hostile_parser(_):
            calls.append(True)
            return Decimal("1")
        with self.assertRaises(ValueError) as result:
            function(source, hostile_parser)
        self.assertEqual(calls, [])
        self.assertIsNone(result.exception.__cause__)
        self.assertNotIn(str(source), str(result.exception))

    def assert_forgery_rejected(self, function, source, forged):
        calls = []
        def hostile_parser(_):
            calls.append(True)
            return Decimal(forged)
        with self.assertRaises(ValueError) as result:
            function(source, hostile_parser)
        self.assertEqual(calls, [True])
        self.assertIsNone(result.exception.__cause__)

    def test_grouped_quantity_accepted_exact(self):
        self.assertEqual(checked_quantity("1,234.500", lambda _: Decimal("1234.5")), Decimal("1234.5"))

    def test_grouped_quantity_callback_launder_rejected(self):
        self.assert_forgery_rejected(checked_quantity, "1,234.50", "123.45")

    def test_grouped_quantity_invalid_comma_rejected_before_callback(self):
        self.assert_preflight_rejects(checked_quantity, "1,23")

    def test_quantity_underscore_rejected_before_callback(self):
        self.assert_preflight_rejects(checked_quantity, "1_0")

    def test_quantity_unicode_digit_rejected_before_callback(self):
        self.assert_preflight_rejects(checked_quantity, "١٢")

    def test_quantity_scientific_exponent_still_accepted(self):
        self.assertEqual(checked_quantity("1E+5", Decimal), Decimal(100000))

    def test_quantity_scientific_forgery_rejected(self):
        self.assert_forgery_rejected(checked_quantity, "1e3", "2000")

    def test_plain_signed_number_allowed(self):
        self.assertEqual(checked_unit_price("+5.00", Decimal), Decimal("5"))

    def test_price_currency_accepted_exact(self):
        self.assertEqual(checked_unit_price("$1,234.50", lambda _: Decimal("1234.50")), Decimal("1234.5"))

    def test_price_currency_callback_forgery_rejected(self):
        self.assert_forgery_rejected(checked_unit_price, "$1,234.50", "1234.51")

    def test_price_parentheses_accepted_exact(self):
        self.assertEqual(checked_unit_price("($1,234.50)", lambda _: Decimal("-1234.50")), Decimal("-1234.5"))

    def test_price_parentheses_sign_flip_rejected(self):
        self.assert_forgery_rejected(checked_unit_price, "($1,234.50)", "1234.50")

    def test_price_negative_currency_sign_accepted(self):
        self.assertEqual(checked_unit_price("$-2.50", lambda _: Decimal("-2.50")), Decimal("-2.50"))

    def test_price_negative_currency_sign_forgery_rejected(self):
        self.assert_forgery_rejected(checked_unit_price, "-$2.50", "2.50")

    def test_price_positive_currency_sign_accepted(self):
        self.assertEqual(checked_unit_price("+$2.50", lambda _: Decimal("2.50")), Decimal("2.50"))

    def test_price_currency_malformed_grouping_preflight_rejected(self):
        self.assert_preflight_rejects(checked_unit_price, "$12,34.50")

    def test_price_double_sign_preflight_rejected(self):
        self.assert_preflight_rejects(checked_unit_price, "--$2.50")

    def test_price_mismatched_parentheses_preflight_rejected(self):
        self.assert_preflight_rejects(checked_unit_price, "($1,234.50")

    def test_price_conflicting_signs_preflight_rejected(self):
        self.assert_preflight_rejects(checked_unit_price, "(-$2.50)")

    def test_price_unicode_digit_preflight_rejected(self):
        self.assert_preflight_rejects(checked_unit_price, "$１２.50")

    def test_price_accounting_negative_zero_preserved(self):
        self.assertTrue(checked_unit_price("($0.00)", lambda _: Decimal("-0")) == Decimal("0"))

    def test_malformed_tokens_reject_private_callback_without_call(self):
        self.assert_preflight_rejects(checked_unit_price, "SECRET_PATH")

    def test_parenthetical_cents_with_context_prec_four(self):
        with localcontext() as ctx:
            ctx.prec = 4
            self.assertEqual(checked_unit_price("($1,234.12345678)", lambda _: Decimal("-1234.12345678")), Decimal("-1234.12345678"))

    def test_grouped_quantity_too_large_before_callback(self):
        self.assert_preflight_rejects(checked_quantity, "1,000,000,001")

    def test_callback_raises_private_path_and_is_redacted(self):
        def callback(_):
            raise OSError("PRIVATE_FINANCE_PATH")
        with self.assertRaises(ValueError) as result:
            checked_unit_price("$2.50", callback)
        self.assertNotIn("PRIVATE_FINANCE_PATH", str(result.exception))
        self.assertIsNone(result.exception.__cause__)


if __name__ == "__main__":
    unittest.main()
