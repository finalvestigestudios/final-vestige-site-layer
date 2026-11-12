"""R365 real-renderer integration regressions; synthetic policy source only."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from fvs_suite import policy_confusable_budget_r365 as budget
from fvs_suite.policy_confusables import render_local_confusable_evidence as render


def hunk(n=1, before="PAY A\n", after="PAY А\n"):
    return {"removed_sources": [(n, before)], "added_sources": [(n, after)]}


class ConfusableBudgetRendererR365(unittest.TestCase):
    def test_normal_pair_remains_visible(self):
        report = render([hunk()])
        self.assertIn("before L1; after L1", report)
        self.assertIn("human review", report)

    def test_exact_character_budget_still_renders(self):
        with patch.object(budget, "MAX_TEXT_CODEPOINTS", 12):
            self.assertIn("before L1", render([hunk()]))

    def test_one_char_over_budget_suppresses_all(self):
        with patch.object(budget, "MAX_TEXT_CODEPOINTS", 11):
            self.assertEqual(render([hunk()]), "")

    def test_second_hunk_over_budget_removes_earlier_cue(self):
        with patch.object(budget, "MAX_TEXT_CODEPOINTS", 18):
            self.assertEqual(render([hunk(1), hunk(2)]), "")

    def test_aggregate_row_cap_suppresses_all(self):
        with patch.object(budget, "MAX_SOURCE_ROWS", 3):
            self.assertEqual(render([hunk(1), hunk(2)]), "")

    def test_aggregate_hunk_cap_suppresses_all(self):
        with patch.object(budget, "MAX_HUNKS", 1):
            self.assertEqual(render([hunk(1), hunk(2)]), "")

    def test_boundary_overlong_line_still_consumes_budget(self):
        huge = hunk(1, "X" * 4097, "А" * 4097)
        with patch.object(budget, "MAX_TEXT_CODEPOINTS", 8200):
            self.assertEqual(render([huge, hunk(2)]), "")

    def test_navigational_rejection_does_not_mutate_inputs(self):
        values = [hunk(1), hunk(2)]
        original = repr(values)
        with patch.object(budget, "MAX_TEXT_CODEPOINTS", 2):
            self.assertEqual(render(values), "")
        self.assertEqual(repr(values), original)

    def test_local_validation_retains_strict_hunk_contract(self):
        invalid = {"removed_sources": [(1, "A")], "added_sources": ((1, "А"),)}
        self.assertEqual(render([hunk(1), invalid]), "")


if __name__ == "__main__":
    unittest.main()
