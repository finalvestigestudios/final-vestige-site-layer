"""R536: reject invalid invoice review windows before opening private source CSV.

Source-only unittest coverage; no customer files, network, release, or payment
operations. These tests are committed for the normal/-OO repository gates.
"""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch

from fvs_suite import engine
from fvs_suite.invoice_match import candidate_pairs
from fvs_suite.invoice_window_policy_r536 import (
    MAX_REVIEW_WINDOW_DAYS, require_invoice_review_window,
)


class _IntegerSubclass(int):
    pass


class _DangerousValue:
    def __str__(self):
        raise AssertionError("untrusted value conversion must not run")


class _TouchSensitiveSource:
    def __iter__(self):
        raise AssertionError("private invoice iterator was touched")


class R536ExactWindowPolicy(TestCase):
    def test_r536_accepts_zero_day_review_window(self):
        self.assertEqual(require_invoice_review_window(0), 0)

    def test_r536_accepts_normal_seven_day_window(self):
        self.assertEqual(require_invoice_review_window(7), 7)

    def test_r536_accepts_maximum_365_day_window(self):
        self.assertEqual(MAX_REVIEW_WINDOW_DAYS, 365)
        self.assertEqual(require_invoice_review_window(365), 365)

    def test_r536_rejects_negative_and_out_of_range_windows(self):
        for value in (-1, -365, 366, 1_000_000):
            with self.subTest(value=value), self.assertRaises(ValueError):
                require_invoice_review_window(value)

    def test_r536_rejects_booleans_not_silent_zero_or_one(self):
        for value in (True, False):
            with self.subTest(value=value), self.assertRaises(ValueError):
                require_invoice_review_window(value)

    def test_r536_rejects_float_decimal_and_text_coercion(self):
        for value in (0.0, 7.0, Decimal("7"), "7", "365", None):
            with self.subTest(kind=type(value).__name__), self.assertRaises(ValueError):
                require_invoice_review_window(value)

    def test_r536_rejects_integer_subclass_with_overridden_methods(self):
        with self.assertRaises(ValueError):
            require_invoice_review_window(_IntegerSubclass(7))

    def test_r536_does_not_invoke_untrusted_conversion_methods(self):
        with self.assertRaisesRegex(ValueError, "integer between 0 and 365"):
            require_invoice_review_window(_DangerousValue())

    def test_r536_never_reflects_sensitive_window_text(self):
        with self.assertRaises(ValueError) as error:
            require_invoice_review_window("PRIVATE-CUSTOMER-INVOICE")
        self.assertNotIn("CUSTOMER", str(error.exception))


class R536APIBeforeSourceRead(TestCase):
    def test_r536_invalid_direct_invoice_window_skips_table_and_save(self):
        with patch.object(engine, "table", side_effect=AssertionError("read")) as table:
            with patch.object(engine, "save", side_effect=AssertionError("save")) as save:
                with self.assertRaisesRegex(ValueError, "integer between 0 and 365"):
                    engine.invoice_twins("private.csv", "never-create", window_days=True)
                table.assert_not_called()
                save.assert_not_called()

    def test_r536_out_of_range_direct_window_skips_csv_read(self):
        with patch.object(engine, "table", side_effect=AssertionError("read")) as table:
            with self.assertRaises(ValueError):
                engine.invoice_twins("private.csv", "unused", window_days=366)
            table.assert_not_called()

    def test_r536_invalid_candidate_window_does_not_iterate_source(self):
        for bad in (True, -1, 366, "7", Decimal("7")):
            with self.subTest(kind=type(bad).__name__):
                with self.assertRaisesRegex(ValueError, "integer between 0 and 365"):
                    candidate_pairs(_TouchSensitiveSource(), window_days=bad)

    def test_r536_valid_empty_candidate_inputs_keep_legacy_behavior(self):
        for good in (0, 7, 365):
            with self.subTest(days=good):
                self.assertEqual(candidate_pairs([], window_days=good), [])

    def test_r536_valid_windows_reach_existing_candidate_and_save_flow(self):
        for good in (0, 365):
            with self.subTest(days=good):
                with patch.object(engine, "table", return_value=([], "0" * 64)) as table:
                    with patch.object(engine, "candidate_pairs", return_value=[]) as pairs:
                        with patch.object(engine, "save", return_value="fake-report.csv") as save:
                            self.assertEqual(
                                engine.invoice_twins("fixture.csv", "output", window_days=good),
                                ["fake-report.csv"],
                            )
                            table.assert_called_once()
                            pairs.assert_called_once_with([], window_days=good)
                            save.assert_called_once()

    def test_r536_existing_gui_text_parser_remains_strict(self):
        self.assertEqual(engine.invoice_window_days("0"), 0)
        self.assertEqual(engine.invoice_window_days("365"), 365)
        for bad in ("0365", "366", "3.0", " 7", "-1"):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                engine.invoice_window_days(bad)


if __name__ == "__main__":
    import unittest
    unittest.main()
