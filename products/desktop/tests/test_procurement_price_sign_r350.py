"""R350 exact sign-bit reviewer flags; synthetic prices only."""
from __future__ import annotations

from decimal import Context, Decimal, getcontext, localcontext
import unittest

from fvs_suite.procurement_price_sign_r350 import negative_price_review_required


class HostileDecimal(Decimal):
    def is_signed(self):
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")


class HostileObject:
    def __lt__(self, _):
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")

    def is_signed(self):
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")


class NegativePriceReviewR350(unittest.TestCase):
    def expect(self, text: str, expected: bool):
        source = Decimal(text)
        original_tuple = source.as_tuple()
        self.assertIs(negative_price_review_required(source), expected)
        self.assertEqual(source.as_tuple(), original_tuple)

    def reject(self, source):
        with self.assertRaises(ValueError) as error:
            negative_price_review_required(source)
        self.assertEqual(str(error.exception),
                         "Procurement price review requires a finite native Decimal")
        self.assertIsNone(error.exception.__cause__)

    def test_negative_integer(self):
        self.expect("-1", True)

    def test_negative_fractional_subcent(self):
        self.expect("-0.00000001", True)

    def test_negative_large_price(self):
        self.expect("-1000000000000", True)

    def test_negative_zero_integer(self):
        self.expect("-0", True)

    def test_negative_zero_cents(self):
        self.expect("-0.00", True)

    def test_negative_zero_eight_places(self):
        self.expect("-0E-8", True)

    def test_negative_zero_positive_exponent(self):
        self.expect("-0E+6", True)

    def test_positive_zero_integer(self):
        self.expect("0", False)

    def test_positive_zero_cents(self):
        self.expect("0.00", False)

    def test_positive_zero_exponent(self):
        self.expect("0E-8", False)

    def test_positive_one(self):
        self.expect("1", False)

    def test_positive_subcent(self):
        self.expect("0.00000001", False)

    def test_positive_maximum(self):
        self.expect("1000000000000", False)

    def test_integer_rejected(self):
        self.reject(-1)

    def test_float_rejected(self):
        self.reject(-0.0)

    def test_string_rejected(self):
        self.reject("-0")

    def test_bool_rejected(self):
        self.reject(True)

    def test_none_rejected(self):
        self.reject(None)

    def test_decimal_subclass_not_interpreted(self):
        self.reject(HostileDecimal("-0"))

    def test_hostile_object_not_interpreted(self):
        self.reject(HostileObject())

    def test_nan_rejected(self):
        self.reject(Decimal("NaN"))

    def test_snan_rejected_without_triggering_traps(self):
        self.reject(Decimal("sNaN"))

    def test_positive_infinity_rejected(self):
        self.reject(Decimal("Infinity"))

    def test_negative_infinity_rejected(self):
        self.reject(Decimal("-Infinity"))

    def test_caller_context_and_flags_unchanged(self):
        with localcontext(Context(prec=4)):
            prior = getcontext().copy()
            self.assertTrue(negative_price_review_required(Decimal("-0.00000000")))
            self.assertFalse(negative_price_review_required(Decimal("0.00000000")))
            self.assertEqual(getcontext().prec, prior.prec)
            self.assertEqual(getcontext().flags, prior.flags)

    def test_repeated_calls_are_deterministic(self):
        price = Decimal("-0.00")
        self.assertEqual([negative_price_review_required(price) for _ in range(20)], [True] * 20)


if __name__ == "__main__":
    unittest.main()
