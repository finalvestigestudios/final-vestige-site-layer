"""R88 deterministic fixed-point boundary tests for the shared price review API.

Synthetic Decimal values only; no local financial data, network, payment
approval, or interpretation of grant/procurement compliance is involved.
"""
from __future__ import annotations

import unittest
from decimal import Context, Decimal, Inexact, Rounded, ROUND_DOWN, localcontext
from random import Random

from fvs_suite.review import price_exceeds_tolerance, price_outside_tolerance


class PriceComparisonFixedPointR88(unittest.TestCase):
    def test_documented_boundary_exactly_equal_does_not_flag(self):
        self.assertFalse(price_exceeds_tolerance(
            Decimal("102.0102000000000000"), Decimal("100.01")))

    def test_sixteen_place_variance_just_above_boundary_is_reviewed(self):
        self.assertTrue(price_exceeds_tolerance(
            Decimal("102.0102000000000001"), Decimal("100.01")))

    def test_sixteen_place_variance_just_below_boundary_is_not_reviewed(self):
        self.assertFalse(price_exceeds_tolerance(
            Decimal("102.0101999999999999"), Decimal("100.01")))

    def test_rejects_witness_that_previously_silently_hid_variance(self):
        # With 64-digit arithmetic and no input scale guard the trailing 1
        # is rounded out; old implementation incorrectly returned False.
        witness = Decimal("102.0102" + "0" * 85 + "1")
        with self.assertRaisesRegex(ValueError, "suite review bounds"):
            price_exceeds_tolerance(witness, Decimal("100.01"))

    def test_seventeenth_nonzero_fractional_place_fails_closed(self):
        for which in ("actual", "expected", "absolute"):
            with self.subTest(which=which):
                values = dict(actual=Decimal("1.00"), expected=Decimal("1.00"),
                              absolute=Decimal("0.01"), fraction=Decimal("0.02"))
                values[which] = Decimal("0.00000000000000001")
                with self.assertRaises(ValueError):
                    price_outside_tolerance(**values)

    def test_ninth_fractional_place_in_direct_policy_fails_closed(self):
        with self.assertRaises(ValueError):
            price_outside_tolerance(Decimal("100"), Decimal("101"),
                                    Decimal("0.01"), Decimal("0.000000001"))

    def test_extra_trailing_zeroes_do_not_change_review_result(self):
        self.assertTrue(price_outside_tolerance(
            Decimal("102.02" + "0" * 25), Decimal("100.01"),
            Decimal("0.0100000000000000"), Decimal("0.0200000000000000")))

    def test_unbounded_coefficient_fails_closed(self):
        with self.assertRaises(ValueError):
            price_exceeds_tolerance(Decimal("1." + "0" * 80), Decimal("1"))

    def test_zero_with_extreme_exponent_is_rejected_without_rendering(self):
        for value in (Decimal("0E-99999999"), Decimal("0E+99999999")):
            with self.subTest(exponent=value.as_tuple().exponent):
                with self.assertRaises(ValueError):
                    price_exceeds_tolerance(value, Decimal("1"))

    def test_deterministic_512_case_reference_property(self):
        """Every accepted bounded comparison agrees with 128-digit arithmetic."""
        random = Random(8827)
        # 42 significant digits at 16 decimal places stay inside 1e27.
        for case in range(512):
            actual_units = random.randrange(-(10 ** 42), 10 ** 42)
            expected_units = random.randrange(-(10 ** 42), 10 ** 42)
            absolute_units = random.randrange(0, 10 ** 20)
            fraction_units = random.randrange(0, 10 ** 8 + 1)
            actual = Decimal((int(actual_units < 0), tuple(map(int, str(abs(actual_units)))), -16))
            expected = Decimal((int(expected_units < 0), tuple(map(int, str(abs(expected_units)))), -16))
            absolute = Decimal((0, tuple(map(int, str(absolute_units))), -16))
            fraction = Decimal((0, tuple(map(int, str(fraction_units))), -8))
            with localcontext(Context(prec=128)):
                wanted = (actual - expected).copy_abs() > max(
                    absolute, expected.copy_abs() * fraction)
            with self.subTest(case=case):
                with localcontext() as caller:
                    caller.prec = 2
                    caller.traps[Inexact] = True
                    caller.traps[Rounded] = True
                    found = price_outside_tolerance(actual, expected, absolute, fraction)
                    self.assertEqual(found, wanted)
                    self.assertFalse(caller.flags[Inexact])
                    self.assertFalse(caller.flags[Rounded])

    def test_max_bound_and_symmetric_negative_still_supported(self):
        limit = Decimal("1000000000000000000000000000")
        self.assertTrue(price_outside_tolerance(
            limit.copy_negate(), limit, Decimal("0.01"), Decimal("0.02")))

    def test_threshold_exact_in_aggregated_envelope(self):
        expected = Decimal("199999999999999998000.00000000000001")
        actual = Decimal("199999999999999998000.00000000000002")
        self.assertFalse(price_exceeds_tolerance(actual, expected))

    def test_invalid_direct_values_never_leak_into_error_message(self):
        for value in (Decimal("0.00000000000000001"),
                      Decimal("1." + "0" * 85), Decimal("NaN")):
            with self.subTest(type=str(value)[:10]):
                try:
                    price_exceeds_tolerance(value, Decimal("1"))
                except ValueError as exc:
                    self.assertNotIn(str(value), str(exc))
                else:
                    self.fail("Unbounded direct price was accepted")

    def test_hostile_caller_context_and_traps_remain_unchanged(self):
        with localcontext() as caller:
            caller.prec = 2
            caller.rounding = ROUND_DOWN
            caller.traps[Inexact] = True
            caller.traps[Rounded] = True
            self.assertTrue(price_exceeds_tolerance(
                Decimal("102.0102000000000001"), Decimal("100.01")))
            with self.assertRaises(ValueError):
                price_exceeds_tolerance(Decimal("1E-17"), Decimal("1"))
            self.assertEqual(caller.prec, 2)
            self.assertEqual(caller.rounding, ROUND_DOWN)
            self.assertFalse(caller.flags[Inexact])
            self.assertFalse(caller.flags[Rounded])

    def test_legacy_normal_use_is_backward_compatible(self):
        self.assertTrue(price_exceeds_tolerance(Decimal("102.02"), Decimal("100.01")))
        self.assertFalse(price_exceeds_tolerance(Decimal("102.0102"), Decimal("100.01")))
        self.assertFalse(price_exceeds_tolerance(Decimal("0.01"), Decimal("0.00")))
        self.assertTrue(price_outside_tolerance(Decimal("10"), Decimal("9"),
                                                Decimal("0.01"), Decimal("0.10")))


if __name__ == "__main__":
    unittest.main()
