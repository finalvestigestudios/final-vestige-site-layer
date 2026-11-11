"""R363 physical line citation reproducibility; synthetic values only."""
from __future__ import annotations

import itertools
import unittest
from unittest.mock import patch

from fvs_suite import spend_source_row_order_r363 as order
from fvs_suite.spend_source_row_order_r363 import canonical_spend_source_rows


class SourceRowOrderR363(unittest.TestCase):
    def test_empty_bucket(self):
        self.assertEqual(canonical_spend_source_rows([]), "")

    def test_one_physical_row(self):
        self.assertEqual(canonical_spend_source_rows(["2"]), "2")

    def test_lexical_sort_not_used(self):
        self.assertEqual(canonical_spend_source_rows(["10", "2", "9"]), "2;9;10")

    def test_multiple_permutations_are_identical(self):
        labels = ["27", "3", "11", "2"]
        self.assertEqual({canonical_spend_source_rows(list(x))
                          for x in itertools.permutations(labels)}, {"2;3;11;27"})

    def test_caller_order_unchanged(self):
        labels = ["100", "2", "10"]
        saved = labels[:]
        canonical_spend_source_rows(labels)
        self.assertEqual(labels, saved)

    def test_larger_numeric_coordinates(self):
        self.assertEqual(canonical_spend_source_rows(["9999999999", "2"]), "2;9999999999")

    def test_no_one_as_header_row(self):
        with self.assertRaisesRegex(ValueError, "physical row"):
            canonical_spend_source_rows(["1"])

    def test_zero_disallowed(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_rows(["0"])

    def test_leading_zero_disallowed(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_rows(["02"])

    def test_nonascii_digit_disallowed(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_rows(["٢"])

    def test_noncanonical_space_disallowed(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_rows([" 2"])

    def test_excessive_digit_count_disallowed(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_rows(["1" * 11])

    def test_duplicate_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "repeated"):
            canonical_spend_source_rows(["2", "9", "2"])

    def test_bad_container_disallowed(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_rows(("2", "3"))

    def test_str_subclass_disallowed_without_hooks(self):
        class HostileStr(str):
            def __str__(self):
                raise AssertionError("subclass hook")
        with self.assertRaises(ValueError):
            canonical_spend_source_rows([HostileStr("2")])

    def test_nontext_disallowed(self):
        with self.assertRaises(ValueError):
            canonical_spend_source_rows([2])

    def test_confidential_error_not_echoed(self):
        secret = "PRIVATE-CUSTOMER-ACCOUNT-778899"
        with self.assertRaises(ValueError) as caught:
            canonical_spend_source_rows([secret])
        self.assertNotIn(secret, str(caught.exception))

    def test_maximum_accepted_when_patched_small(self):
        with patch.object(order, "_MAX_ROWS", 3):
            self.assertEqual(canonical_spend_source_rows(["3", "2", "9"]), "2;3;9")

    def test_length_overflow_rejected_before_reading_values(self):
        class HostileStr(str):
            def __getattribute__(self, name):
                raise AssertionError("string accessed")
        with patch.object(order, "_MAX_ROWS", 1):
            with self.assertRaisesRegex(ValueError, "collection"):
                canonical_spend_source_rows([HostileStr("2"), HostileStr("3")])

    def test_separate_groups_do_not_share_state(self):
        self.assertEqual(canonical_spend_source_rows(["9", "2"]), "2;9")
        self.assertEqual(canonical_spend_source_rows(["10", "3"]), "3;10")

    def test_repeat_execution_is_identical(self):
        labels = ["17", "11", "2"]
        self.assertEqual(canonical_spend_source_rows(labels), canonical_spend_source_rows(labels))


if __name__ == "__main__":
    unittest.main()
