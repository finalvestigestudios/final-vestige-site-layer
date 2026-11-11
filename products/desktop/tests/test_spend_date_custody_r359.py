"""R359 independent original-date custody, synthetic dates only."""
from __future__ import annotations

from datetime import date, datetime, timedelta
import unittest

from fvs_suite.spend_date_custody_r359 import (
    canonical_spend_source_date, spend_date_parser_preserves_source,
)


class SpendDateCustodyR359(unittest.TestCase):
    def test_iso_date(self):
        self.assertEqual(canonical_spend_source_date("2026-11-01"), date(2026, 11, 1))

    def test_iso_single_digits(self):
        self.assertEqual(canonical_spend_source_date("2026-2-3"), date(2026, 2, 3))

    def test_us_long_date(self):
        self.assertEqual(canonical_spend_source_date("11/01/2026"), date(2026, 11, 1))

    def test_us_short_date(self):
        self.assertEqual(canonical_spend_source_date("11/01/26"), date(2026, 11, 1))

    def test_supported_whitespace(self):
        self.assertEqual(canonical_spend_source_date(" 2026-11-01 \t"), date(2026, 11, 1))

    def test_calendar_leap_day(self):
        self.assertEqual(canonical_spend_source_date("2024-02-29"), date(2024, 2, 29))

    def test_invalid_leap_day_rejected(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_date("2026-02-29")

    def test_invalid_forged_date_rejected(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_date("2026-11-32")

    def test_unsupported_locale_rejected(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_date("01.11.2026")

    def test_formula_date_rejected(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_date("=DATE(2026,11,1)")

    def test_overlong_rejected(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_date("2" * 33)

    def test_source_subclass_not_invoked(self):
        class HostileStr(str):
            def strip(self, *args):
                raise AssertionError("unsafe source callback invoked")
        with self.assertRaises(ValueError):
            canonical_spend_source_date(HostileStr("2026-11-01"))

    def test_arbitrary_source_object_not_invoked(self):
        class Hostile:
            def __str__(self):
                raise AssertionError("unsafe source conversion invoked")
        with self.assertRaises(ValueError):
            canonical_spend_source_date(Hostile())

    def test_rewrite_to_different_month_rejected(self):
        self.assertFalse(spend_date_parser_preserves_source(
            date(2026, 11, 1), date(2026, 12, 1)))

    def test_rewrite_to_different_day_rejected(self):
        self.assertFalse(spend_date_parser_preserves_source(
            date(2026, 11, 1), date(2026, 11, 2)))

    def test_equal_day_from_alternate_format_accepted(self):
        self.assertTrue(spend_date_parser_preserves_source(
            canonical_spend_source_date("11/01/26"), date(2026, 11, 1)))

    def test_datetime_is_not_native_date(self):
        self.assertFalse(spend_date_parser_preserves_source(
            date(2026, 11, 1), datetime(2026, 11, 1)))

    def test_date_subclass_rejected(self):
        class HostileDate(date):
            def __eq__(self, other):
                raise AssertionError("unsafe date comparison invoked")
        self.assertFalse(spend_date_parser_preserves_source(
            date(2026, 11, 1), HostileDate(2026, 11, 1)))

    def test_non_date_callback_output_rejected(self):
        for value in ("2026-11-01", 20261101, None, object()):
            with self.subTest(value_type=type(value).__name__):
                self.assertFalse(spend_date_parser_preserves_source(date(2026, 11, 1), value))

    def test_invalid_error_contains_no_source(self):
        secret = "PRIVATE-INVOICE-1234"
        with self.assertRaises(ValueError) as error:
            canonical_spend_source_date(secret)
        self.assertNotIn(secret, str(error.exception))

    def test_determinism_from_source(self):
        for source in ("2026-01-01", " 2026-01-01 ", "01/01/2026", "1/1/26"):
            with self.subTest(source=source):
                self.assertEqual(canonical_spend_source_date(source), date(2026, 1, 1))


if __name__ == "__main__":
    unittest.main()
