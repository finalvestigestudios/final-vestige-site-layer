"""R366: bounded, hash-seed-independent Policy Delta review output.

All inputs synthetic. These cues do not constitute compliance or legal advice.
"""
from __future__ import annotations

import random
import unittest
from unittest.mock import patch

from fvs_suite.policy_confusables import (
    _retain_earliest_pair,
    render_local_confusable_evidence as render,
)


def hunk(line=1, count=1):
    return {
        "removed_sources": [(line + i, f"Term {i:03d} A\n") for i in range(count)],
        "added_sources": [(line + i, f"Term {i:03d} А\n") for i in range(count)],
    }


class BoundedCitationsR366(unittest.TestCase):
    def test_one_pair_still_renders(self):
        report = render([hunk()])
        self.assertIn("before L1; after L1", report)
        self.assertIn("human review", report)

    def test_dense_single_hunk_keeps_earliest_sixteen(self):
        report = render([hunk(count=100)])
        self.assertEqual(report.count("Look-alike hunk"), 16)
        self.assertIn("before L1; after L1", report)
        self.assertIn("before L16; after L16", report)
        self.assertNotIn("before L17;", report)
        self.assertIn("+84 additional look-alike pair(s) omitted", report)

    def test_hunk_order_and_omission_count(self):
        report = render([hunk(i) for i in range(1, 21)])
        self.assertEqual(report.count("Look-alike hunk"), 16)
        self.assertIn("Look-alike hunk 016", report)
        self.assertNotIn("Look-alike hunk 017", report)
        self.assertIn("+4 additional look-alike pair(s) omitted", report)

    def test_multi_hunk_and_multi_row_citation_order(self):
        report = render([hunk(1, 10), hunk(21, 10)])
        before_10 = report.index("before L10;")
        before_21 = report.index("before L21;")
        self.assertLess(before_10, before_21)
        self.assertNotIn("before L27;", report)
        self.assertIn("+4 additional look-alike pair(s) omitted", report)

    def test_invalid_late_hunk_fails_whole_report(self):
        self.assertEqual(render([hunk(count=100),
                                 {"removed_sources": [(1, "X")]}]), "")

    def test_ambiguous_skeleton_not_counted_as_omitted(self):
        ambiguous = {"removed_sources": [(1, "A"), (2, "А")],
                     "added_sources": [(1, "Α")]}
        report = render([ambiguous, hunk(4)])
        self.assertEqual(report.count("Look-alike hunk"), 1)
        self.assertNotIn("additional look-alike", report)

    def test_source_and_private_labels_not_mutated_or_echoed(self):
        private = [{"removed_sources": [(1, "customer-507 A")],
                    "added_sources": [(1, "customer-507 А")]}]
        before = repr(private)
        report = render(private)
        self.assertNotIn("customer-507", report)
        self.assertEqual(repr(private), before)

    def test_selector_drops_late_high_coordinates(self):
        shown = []
        for line in range(1, 5001):
            _retain_earliest_pair(shown, (1, line, line, "cue"), 16)
            self.assertLessEqual(len(shown), 16)
        self.assertEqual([v[1] for v in shown], list(range(1, 17)))

    def test_selector_retains_earliest_even_in_reverse_order(self):
        shown = []
        for line in range(5000, 0, -1):
            _retain_earliest_pair(shown, (1, line, line, "cue"), 16)
            self.assertLessEqual(len(shown), 16)
        self.assertEqual([v[1] for v in shown], list(range(1, 17)))

    def test_selector_equals_full_sort_on_shuffled_matches(self):
        all_candidates = [(i // 70 + 1, i + 1, i + 2, "safe") for i in range(300)]
        random.Random(366).shuffle(all_candidates)
        retained = []
        for candidate in all_candidates:
            _retain_earliest_pair(retained, candidate, 16)
        self.assertEqual(retained, sorted(all_candidates)[:16])

    def test_selector_handles_zero_and_negative_limit(self):
        for limit in (0, -5):
            held = []
            _retain_earliest_pair(held, (1, 1, 1, "cue"), limit)
            self.assertEqual(held, [])

    def test_selector_obeys_one_pair_limit(self):
        held = []
        for coord in (10, 4, 20, 2):
            _retain_earliest_pair(held, (1, coord, coord, "cue"), 1)
            self.assertLessEqual(len(held), 1)
        self.assertEqual(held, [(1, 2, 2, "cue")])

    def test_renderer_with_small_limit_keeps_correct_earliest(self):
        with patch("fvs_suite.policy_confusables._MAX_PAIRS", 2):
            report = render([hunk(count=8)])
        self.assertIn("before L1;", report)
        self.assertIn("before L2;", report)
        self.assertNotIn("before L3;", report)
        self.assertIn("+6 additional look-alike pair(s) omitted", report)

    def test_zero_limit_still_warns_without_leaking_source(self):
        with patch("fvs_suite.policy_confusables._MAX_PAIRS", 0):
            report = render([hunk(count=2)])
        self.assertNotIn("before L", report)
        self.assertIn("+2 additional look-alike pair(s) omitted", report)

    def test_renderer_deterministic_across_repeated_calls(self):
        values = [hunk(count=90)]
        reference = render(values)
        for _ in range(10):
            self.assertEqual(render(values), reference)


if __name__ == "__main__":
    unittest.main()
