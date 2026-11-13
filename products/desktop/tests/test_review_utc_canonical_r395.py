"""R395 chronology evidence: bounded UTC lexical custody and no lossy timestamps.

Synthetic metadata only; no customer files, network, payment or automation.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from fvs_suite.review_chronology import (
    parse_review_utc, check_record_order, check_new_review_clock,
)

BASE = "2026-11-13T05:01:02"


class CanonicalPremiumReviewUTC(unittest.TestCase):
    def assert_private_rejection(self, raw):
        with self.assertRaises(ValueError) as result:
            parse_review_utc(raw)
        self.assertEqual(str(result.exception), "Review journal has an invalid UTC timestamp")
        self.assertIsNone(result.exception.__cause__)
        self.assertIsNone(result.exception.__context__)

    def test_persisted_writer_seconds(self):
        self.assertEqual(parse_review_utc(BASE + "+00:00"),
                         datetime(2026, 11, 13, 5, 1, 2, tzinfo=timezone.utc))

    def test_historical_zulu_seconds(self):
        self.assertEqual(parse_review_utc(BASE + "Z"), parse_review_utc(BASE + "+00:00"))

    def test_historical_negative_zero_offset(self):
        self.assertEqual(parse_review_utc(BASE + "-00:00"), parse_review_utc(BASE + "+00:00"))

    def test_supported_fraction_widths(self):
        for n in range(1, 7):
            for zone in ("Z", "+00:00", "-00:00"):
                with self.subTest(n=n, zone=zone):
                    observed = parse_review_utc(BASE + "." + "7" * n + zone)
                    self.assertEqual(observed.microsecond, int("7" * n) * 10 ** (6 - n))

    def test_no_silent_fraction_truncation(self):
        for n in (7, 8, 9, 12):
            with self.subTest(n=n):
                self.assert_private_rejection(BASE + "." + "0" * 6 + "1" * (n - 6) + "Z")

    def test_no_ambiguous_separator(self):
        for sep in ("X", " ", "_", "\u200b", "\u2028"):
            with self.subTest(sep=repr(sep)):
                self.assert_private_rejection(BASE.replace("T", sep) + "Z")

    def test_no_week_or_ordinal_or_compact_date(self):
        for value in ("2026-W46-5T05:01:02Z", "20261113T050102Z",
                      "2026-317T05:01:02Z", "2026-11-13T050102Z"):
            with self.subTest(value=value):
                self.assert_private_rejection(value)

    def test_no_short_time_or_time_precision(self):
        for value in ("2026-11-13T05:01Z", "2026-11-13T05Z",
                      "2026-11-13T05:01:02.Z", "2026-11-13T05:01:02,5Z"):
            with self.subTest(value=value):
                self.assert_private_rejection(value)

    def test_reject_noncanonical_timezone_spellings(self):
        for zone in ("+0000", "-0000", "+00", "+00:00:00", "+00:00:00.0", "z", "GMT"):
            with self.subTest(zone=zone):
                self.assert_private_rejection(BASE + zone)

    def test_reject_real_nonzero_utc_offsets(self):
        for zone in ("+01:00", "-12:00", "+00:01"):
            with self.subTest(zone=zone):
                self.assert_private_rejection(BASE + zone)

    def test_reject_calendar_invalid(self):
        for value in ("2026-02-30T05:01:02Z", "2026-13-13T05:01:02Z",
                      "2026-11-13T25:01:02Z", "2026-11-13T05:61:02Z",
                      "2026-11-13T05:01:60Z"):
            with self.subTest(value=value):
                self.assert_private_rejection(value)

    def test_reject_untrusted_types_before_coercion(self):
        class PrivateStr:
            def __str__(self):
                raise RuntimeError("PRIVATE-CUSTOMER-IDENTIFIER")
        for value in (None, [], {}, b"2026-11-13T05:01:02Z", PrivateStr(), True, 3.14):
            with self.subTest(value=type(value).__name__):
                self.assert_private_rejection(value)

    def test_reject_hidden_prefix_and_whitespace(self):
        for value in (" " + BASE + "Z", BASE + "Z\n", "\ufeff" + BASE + "Z",
                      BASE + "Z\u200b", "\t" + BASE + "Z"):
            with self.subTest(value=repr(value)):
                self.assert_private_rejection(value)

    def test_reject_unicode_digit_forgery(self):
        self.assert_private_rejection(BASE.replace("2", "\u0662") + "Z")

    def test_reject_oversized_private_timestamp(self):
        self.assert_private_rejection(BASE + "PRIV-CLAIM-" * 20)

    def test_equal_seconds_not_misclassified(self):
        a = parse_review_utc(BASE + "+00:00")
        self.assertEqual(check_record_order(a, BASE + "Z"), a)

    def test_second_precision_rollback(self):
        a = parse_review_utc(BASE + ".000001Z")
        with self.assertRaisesRegex(ValueError, "chronological"):
            check_record_order(a, BASE + "Z")

    def test_distinct_microsecond_order(self):
        a = parse_review_utc(BASE + ".000001Z")
        b = check_record_order(a, BASE + ".000002Z")
        self.assertEqual(b.microsecond, 2)

    def test_future_clock_rollback_is_not_auto_repaired(self):
        now = datetime(2026, 11, 13, 5, 1, 2, tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError, "predates"):
            check_new_review_clock(BASE + ".000001Z", now)

    def test_new_local_clock_preserves_whole_second_review(self):
        now = datetime(2026, 11, 13, 5, 1, 2, tzinfo=timezone.utc)
        self.assertIsNone(check_new_review_clock(BASE + "Z", now))

    def test_empty_history_and_utc_clock_accepted(self):
        self.assertIsNone(check_new_review_clock(None, datetime(2026, 11, 13,
                                                       5, 1, 2, tzinfo=timezone.utc)))

    def test_non_utc_clock_fails_closed(self):
        now = datetime(2026, 11, 13, 1, 1, 2, tzinfo=timezone(timedelta(hours=-4)))
        with self.assertRaisesRegex(ValueError, "UTC"):
            check_new_review_clock(None, now)

    def test_noncanonical_history_blocks_new_append(self):
        now = datetime(2026, 11, 13, 5, 1, 3, tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            check_new_review_clock("2026-11-13X05:01:02Z", now)

    def test_invalid_previous_timestamp_type_rejected(self):
        with self.assertRaisesRegex(ValueError, "previous"):
            check_record_order("not-a-datetime", BASE + "Z")


if __name__ == "__main__":
    unittest.main()
