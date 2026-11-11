"""R364: all-or-nothing Policy Delta look-alike navigation; synthetic only.

Untrusted direct helpers must never present a partial set of physical-line cues
after a malformed hunk. Actual diffs are derived from verified source snapshots.
"""
from __future__ import annotations

import unittest

from fvs_suite.policy_confusables import render_local_confusable_evidence as render


def hunk(line: int = 1):
    return {
        "removed_sources": [(line, "PAY A\n")],
        "added_sources": [(line, "PAY А\n")],
    }


class WholeHunkPolicyCustodyR364(unittest.TestCase):
    def test_valid_single_pair_keeps_human_review(self):
        result = render([hunk()])
        self.assertIn("before L1; after L1", result)
        self.assertIn("human review", result)

    def test_valid_two_hunks_keep_numeric_order(self):
        result = render([hunk(2), hunk(20)])
        self.assertLess(result.index("hunk 001"), result.index("hunk 002"))
        self.assertEqual(result.count("Look-alike hunk"), 2)

    def test_invalid_first_suppresses_valid_later(self):
        bad = {"removed_sources": [(0, "A")], "added_sources": [(1, "А")]}
        self.assertEqual(render([bad, hunk(2)]), "")

    def test_invalid_last_suppresses_valid_earlier(self):
        bad = {"removed_sources": [(2, "A")]}
        self.assertEqual(render([hunk(1), bad]), "")

    def test_invalid_middle_suppresses_both_sides(self):
        bad = {"removed_sources": (), "added_sources": []}
        self.assertEqual(render([hunk(1), bad, hunk(100)]), "")

    def test_not_a_dictionary_suppresses_all(self):
        self.assertEqual(render([hunk(1), object(), hunk(2)]), "")

    def test_dictionary_subclass_not_accessed(self):
        class Trap(dict):
            def get(self, *_):
                raise AssertionError("direct caller's overridden get invoked")
        self.assertEqual(render([hunk(1), Trap(hunk(2))]), "")

    def test_stored_nontext_key_not_compared(self):
        class Key:
            def __eq__(self, other):
                raise AssertionError("unsafe equality")
            def __hash__(self):
                return hash("__not_a_source_column__")
        bad = hunk(2)
        bad[Key()] = "injected"
        self.assertEqual(render([hunk(1), bad]), "")

    def test_list_subclass_never_iterated(self):
        class Trap(list):
            def __iter__(self):
                raise AssertionError("unsafe iterator")
        bad = hunk(2)
        bad["added_sources"] = Trap(bad["added_sources"])
        self.assertEqual(render([hunk(1), bad]), "")

    def test_duplicate_physical_line_in_late_hunk(self):
        bad = {"removed_sources": [(2, "A"), (2, "B")],
               "added_sources": [(2, "А")]}
        self.assertEqual(render([hunk(1), bad]), "")

    def test_later_reversed_physical_coordinate(self):
        self.assertEqual(render([hunk(10), hunk(9)]), "")

    def test_long_but_valid_hunk_does_not_suppress_short(self):
        bad_for_navigation = {
            "removed_sources": [(1, "A" * 4097)],
            "added_sources": [(1, "А" * 4097)],
        }
        value = render([bad_for_navigation, hunk(2)])
        self.assertIn("before L2; after L2", value)
        self.assertNotIn("before L1", value)

    def test_does_not_echo_private_source_when_bad_late(self):
        secret = "client-secret-112233"
        old = {"removed_sources": [(1, secret + " A\n")],
               "added_sources": [(1, secret + " А\n")]}
        self.assertEqual(render([old, {"added_sources": []}]), "")

    def test_no_mutation_of_caller_owned_records(self):
        values = [hunk(1), {"added_sources": []}]
        before = repr(values)
        self.assertEqual(render(values), "")
        self.assertEqual(repr(values), before)

    def test_empty_collection_is_silent(self):
        self.assertEqual(render([]), "")

    def test_single_invalid_hunk_remains_silent(self):
        self.assertEqual(render([{"added_sources": [(1, "А")]}]), "")


if __name__ == "__main__":
    unittest.main()
