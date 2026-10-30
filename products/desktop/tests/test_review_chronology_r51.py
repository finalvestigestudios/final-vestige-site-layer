"""R51 deterministic journal chronology checks, no customer data or network."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from fvs_suite.review_chronology import (
    check_new_review_clock, check_record_order, parse_review_utc,
)


class JournalChronologyTests(unittest.TestCase):
    def test_current_python_utc_format_accepted(self):
        instant = parse_review_utc("2026-10-30T03:05:01+00:00")
        self.assertEqual(instant, datetime(2026, 10, 30, 3, 5, 1, tzinfo=timezone.utc))

    def test_zulu_suffix_accepted(self):
        self.assertEqual(parse_review_utc("2026-01-01T00:00:00Z").tzinfo, timezone.utc)

    def test_same_second_is_valid(self):
        previous = parse_review_utc("2026-10-30T03:05:01+00:00")
        self.assertEqual(check_record_order(previous, "2026-10-30T03:05:01+00:00"), previous)

    def test_increasing_timestamps_valid(self):
        previous = parse_review_utc("2026-10-30T03:05:01+00:00")
        self.assertGreater(check_record_order(previous, "2026-10-30T03:05:02Z"), previous)

    def test_first_event_valid(self):
        self.assertEqual(check_record_order(None, "2026-10-30T03:05:01Z"),
                         parse_review_utc("2026-10-30T03:05:01Z"))

    def test_retroactive_timestamp_rejected(self):
        previous = parse_review_utc("2026-10-30T03:05:02Z")
        with self.assertRaisesRegex(ValueError, "chronological"):
            check_record_order(previous, "2026-10-30T03:05:01Z")

    def test_microsecond_rollback_is_rejected(self):
        previous = parse_review_utc("2026-10-30T03:05:02.500000Z")
        with self.assertRaises(ValueError):
            check_record_order(previous, "2026-10-30T03:05:02Z")

    def test_utc_zero_offset_canonicalizes(self):
        self.assertEqual(parse_review_utc("2026-10-30T03:05:01-00:00"),
                         parse_review_utc("2026-10-30T03:05:01+00:00"))

    def test_reject_non_utc_offset(self):
        with self.assertRaises(ValueError):
            parse_review_utc("2026-10-30T01:05:01-02:00")

    def test_reject_naive(self):
        with self.assertRaises(ValueError):
            parse_review_utc("2026-10-30T03:05:01")

    def test_reject_empty(self):
        with self.assertRaises(ValueError):
            parse_review_utc("")

    def test_reject_non_string_and_nonfinite(self):
        for raw in (None, 4, float("nan"), float("inf"), True, [], {}, b"2026-10-30T03:05:01Z"):
            with self.subTest(raw=type(raw).__name__), self.assertRaises(ValueError):
                parse_review_utc(raw)

    def test_reject_whitespace(self):
        for raw in (" 2026-10-30T03:05:01Z", "2026-10-30T03:05:01Z\n"):
            with self.subTest(), self.assertRaises(ValueError):
                parse_review_utc(raw)

    def test_reject_oversized_timestamp_without_echoing(self):
        sensitive = "customer-secret-" * 200
        with self.assertRaises(ValueError) as caught:
            parse_review_utc(sensitive)
        self.assertNotIn("customer-secret", str(caught.exception))

    def test_reject_invalid_previous_timestamp(self):
        for previous in ("2026-10-30", datetime(2026, 10, 30), None):
            if previous is None:
                continue
            with self.subTest(previous=type(previous).__name__), self.assertRaises(ValueError):
                check_record_order(previous, "2026-10-30T03:05:01Z")

    def test_new_review_equal_timestamp_allowed(self):
        clock = datetime(2026, 10, 30, 3, 5, 1, tzinfo=timezone.utc)
        self.assertIsNone(check_new_review_clock("2026-10-30T03:05:01Z", clock))

    def test_new_review_later_clock_allowed(self):
        clock = datetime(2026, 10, 30, 3, 5, 2, tzinfo=timezone.utc)
        self.assertIsNone(check_new_review_clock("2026-10-30T03:05:01Z", clock))

    def test_new_review_without_history_allowed(self):
        clock = datetime(2026, 10, 30, 3, 5, 2, tzinfo=timezone.utc)
        self.assertIsNone(check_new_review_clock(None, clock))

    def test_new_review_backdated_clock_rejected(self):
        clock = datetime(2026, 10, 30, 3, 5, 1, tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError, "predates"):
            check_new_review_clock("2026-10-30T03:05:02Z", clock)

    def test_new_review_aware_non_utc_clock_rejected(self):
        clock = datetime(2026, 10, 29, 23, 5, tzinfo=timezone(timedelta(hours=-4)))
        with self.assertRaisesRegex(ValueError, "UTC"):
            check_new_review_clock(None, clock)

    def test_new_review_naive_clock_rejected(self):
        with self.assertRaises(ValueError):
            check_new_review_clock(None, datetime(2026, 10, 30, 3, 5))

    def test_no_source_rows_or_private_fields_in_error(self):
        with self.assertRaises(ValueError) as caught:
            check_record_order(parse_review_utc("2026-10-30T03:05:02Z"),
                               "2026-10-30T03:05:01Z")
        self.assertNotIn("2026-10-30T03:05:01", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
