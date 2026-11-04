"""R191: SpendMap median direct API rejects forged or unbounded monetary values.

All inputs are synthetic. No network, real client data, files or report publication.
"""
from __future__ import annotations

from decimal import Context, Decimal, Inexact, Rounded, ROUND_DOWN, localcontext
from fractions import Fraction
from itertools import permutations
from statistics import median
import unittest

from fvs_suite.spend_median import RunningDecimalMedian


PRIVATE = "CUSTOMER SECRET ACCOUNT 123"


class HookedDecimal(Decimal):
    def is_finite(self):
        raise AssertionError("untrusted subclass method was executed")

    def __le__(self, other):
        raise AssertionError("untrusted subclass ordering was executed")

    def copy_negate(self):
        raise AssertionError("untrusted subclass heap-key method was executed")


class HookedString:
    def __str__(self):
        raise AssertionError("untrusted string conversion was executed")

    def __repr__(self):
        raise AssertionError("untrusted repr was executed")


class SpendMedianEnvelopeR191(unittest.TestCase):
    def setUp(self):
        self.history = RunningDecimalMedian()
        self.history.add(Decimal("9.25"))
        self.history.add(Decimal("10.75"))

    def assert_rejected_unchanged(self, value, fragment="Monthly total"):
        original = (len(self.history), self.history.median())
        with self.assertRaises(ValueError) as caught:
            self.history.add(value)
        self.assertIn(fragment, str(caught.exception))
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual((len(self.history), self.history.median()), original)

    def test_reject_subclass_before_is_finite_hook(self):
        self.assert_rejected_unchanged(HookedDecimal("1.00"), "finite native Decimal")

    def test_reject_subclass_before_ordering_hook(self):
        class ComparisonTrap(Decimal):
            def __le__(self, other):
                raise AssertionError("untrusted ordering method")
        self.assert_rejected_unchanged(ComparisonTrap("9.25"))

    def test_reject_subclass_before_copy_negate_hook(self):
        class NegateTrap(Decimal):
            def copy_negate(self):
                raise AssertionError("untrusted copy_negate method")
        self.assert_rejected_unchanged(NegateTrap("-1"))

    def test_reject_subclass_with_oversized_private_value_without_repr(self):
        self.assert_rejected_unchanged(HookedDecimal("1e1000"))

    def test_reject_untrusted_nondecimal_without_hooks(self):
        self.assert_rejected_unchanged(HookedString())

    def test_reject_integer(self):
        self.assert_rejected_unchanged(10)

    def test_reject_bool(self):
        self.assert_rejected_unchanged(True)

    def test_reject_float(self):
        self.assert_rejected_unchanged(10.25)

    def test_reject_fraction(self):
        self.assert_rejected_unchanged(Fraction(1, 2))

    def test_reject_none(self):
        self.assert_rejected_unchanged(None)

    def test_reject_nan_and_infinities(self):
        for raw in ("NaN", "-NaN", "Infinity", "-Infinity", "sNaN"):
            with self.subTest(raw=raw):
                self.assert_rejected_unchanged(Decimal(raw))

    def test_reject_exponent_beyond_positive_bound(self):
        self.assert_rejected_unchanged(Decimal("1e81"), "bounded Decimal envelope")

    def test_reject_exponent_beyond_negative_bound(self):
        self.assert_rejected_unchanged(Decimal("1e-81"), "bounded Decimal envelope")

    def test_reject_zero_with_pathological_exponent(self):
        self.assert_rejected_unchanged(Decimal("0e-9999999"), "bounded Decimal envelope")

    def test_reject_oversized_coefficient(self):
        self.assert_rejected_unchanged(Decimal("9" * 81), "bounded Decimal envelope")

    def test_allow_eighty_digit_coefficient(self):
        self.history.add(Decimal("9" * 80))
        self.assertEqual(len(self.history), 3)
        self.assertEqual(self.history.median(), Decimal("10.75"))

    def test_allow_bounded_positive_exponent(self):
        self.history.add(Decimal("1e80"))
        self.assertEqual(self.history.median(), Decimal("10.75"))

    def test_allow_bounded_negative_exponent(self):
        self.history.add(Decimal("1e-80"))
        self.assertEqual(self.history.median(), Decimal("9.25"))

    def test_preserve_large_exact_half_cent_under_hostile_context(self):
        self.history = RunningDecimalMedian()
        with localcontext() as ctx:
            ctx.prec = 3
            ctx.Emax = 6
            ctx.rounding = ROUND_DOWN
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            self.history.add(Decimal("123456789012.01"))
            self.history.add(Decimal("123456789012.02"))
            self.assertEqual(self.history.median(), Decimal("123456789012.015"))
            self.assertEqual((ctx.prec, ctx.Emax, ctx.rounding), (3, 6, ROUND_DOWN))

    def test_preserve_historical_seventy_digit_exact_midpoint(self):
        self.history = RunningDecimalMedian()
        a = Decimal("9" * 70 + ".01")
        b = Decimal("9" * 70 + ".02")
        self.history.add(a)
        self.history.add(b)
        self.assertEqual(self.history.median(), Decimal("9" * 70 + ".015"))

    def test_median_with_opposite_large_exponents_exact(self):
        self.history = RunningDecimalMedian()
        a = Decimal("1e80")
        b = Decimal("1e-80")
        self.history.add(a)
        self.history.add(b)
        with localcontext(Context(prec=200)):
            expected = (a + b) / 2
        self.assertEqual(self.history.median(), expected)

    def test_repeat_determinism_after_rejected_record(self):
        self.assert_rejected_unchanged(HookedDecimal("0.01"))
        self.history.add(Decimal("11.25"))
        self.assertEqual(self.history.median(), Decimal("10.75"))

    def test_one_value_negative_zero_and_mixed_signs(self):
        self.history = RunningDecimalMedian()
        self.history.add(Decimal("-0.00"))
        self.assertEqual(self.history.median(), Decimal("0.00"))
        self.history.add(Decimal("-10.00"))
        self.history.add(Decimal("10.00"))
        self.assertEqual(self.history.median(), Decimal("-0.00"))

    def test_bound_preserves_order_independent_median(self):
        vals = [Decimal("-1.01"), Decimal("0.00"), Decimal("100.99"), Decimal("2.03")]
        results = []
        for permutation in permutations(vals):
            history = RunningDecimalMedian()
            for value in permutation:
                history.add(value)
            results.append(history.median())
        self.assertEqual(results, [median(vals)] * len(results))

    def test_many_values_reference_median(self):
        history = RunningDecimalMedian()
        vals = [Decimal(n * 7919 % 10007 - 5000) / 100 for n in range(3000)]
        for value in vals:
            history.add(value)
        self.assertEqual(history.median(), median(vals))


if __name__ == "__main__":
    unittest.main()
