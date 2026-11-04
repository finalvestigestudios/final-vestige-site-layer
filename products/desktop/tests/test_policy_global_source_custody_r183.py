"""R183: source-line identities must be unique and increasing across hunks.

Synthetic in-memory policy data only; no customer documents, network, or writes.
"""
from __future__ import annotations

import unittest

from fvs_suite.policy_confusables import render_local_confusable_evidence as render


def hunk(old=((1, "PAY A\n"),), new=((1, "PAY А\n"),)):
    return {"removed_sources": list(old), "added_sources": list(new)}


class PolicyGlobalSourceCustodyR183(unittest.TestCase):
    def test_valid_single_hunk(self):
        self.assertIn("before L1; after L1", render([hunk()]))

    def test_valid_disjoint_hunks(self):
        result = render([hunk(), hunk([(11, "CAP A\n")], [(12, "CAP А\n")])])
        self.assertIn("hunk 001: before L1; after L1", result)
        self.assertIn("hunk 002: before L11; after L12", result)

    def test_same_line_before_after_is_allowed(self):
        self.assertIn("before L8; after L8", render([hunk([(8, "PAY A\n")], [(8, "PAY А\n")])]))

    def test_reused_before_line_in_separate_hunks_fails_closed(self):
        self.assertEqual(render([hunk(), hunk([(1, "CAP A\n")], [(20, "CAP А\n")])]), "")

    def test_reused_after_line_in_separate_hunks_fails_closed(self):
        self.assertEqual(render([hunk(), hunk([(20, "CAP A\n")], [(1, "CAP А\n")])]), "")

    def test_reused_identical_rows_in_separate_hunks_fails_closed(self):
        self.assertEqual(render([hunk(), hunk()]), "")

    def test_before_coordinates_descend_between_hunks_fails_closed(self):
        self.assertEqual(render([hunk([(10, "PAY A\n")], [(1, "PAY А\n")]), hunk([(9, "CAP A\n")], [(12, "CAP А\n")])]), "")

    def test_after_coordinates_descend_between_hunks_fails_closed(self):
        self.assertEqual(render([hunk([(1, "PAY A\n")], [(10, "PAY А\n")]), hunk([(12, "CAP A\n")], [(9, "CAP А\n")])]), "")

    def test_before_rows_descend_inside_hunk_suppressed(self):
        self.assertEqual(render([hunk([(8, "other\n"), (4, "PAY A\n")], [(5, "PAY А\n")])]), "")

    def test_after_rows_descend_inside_hunk_suppressed(self):
        self.assertEqual(render([hunk([(4, "PAY A\n")], [(8, "other\n"), (5, "PAY А\n")])]), "")

    def test_long_before_row_does_not_hide_reused_line(self):
        old = hunk([(1, "A" * 4097), (9, "PAY A\n")], [(2, "PAY А\n")])
        new = hunk([(9, "CAP A\n")], [(15, "CAP А\n")])
        self.assertEqual(render([old, new]), "")

    def test_long_after_row_does_not_hide_reused_line(self):
        old = hunk([(1, "PAY A\n")], [(2, "А" * 4097), (9, "PAY А\n")])
        new = hunk([(15, "CAP A\n")], [(9, "CAP А\n")])
        self.assertEqual(render([old, new]), "")

    def test_long_before_row_out_of_order_inside_hunk_suppressed(self):
        self.assertEqual(render([hunk([(9, "A" * 4097), (2, "PAY A\n")], [(2, "PAY А\n")])]), "")

    def test_long_after_row_out_of_order_inside_hunk_suppressed(self):
        self.assertEqual(render([hunk([(2, "PAY A\n")], [(9, "А" * 4097), (2, "PAY А\n")])]), "")

    def test_long_valid_row_does_not_hide_short_pair(self):
        result = render([hunk([(1, "A" * 4097), (2, "PAY A\n")], [(1, "А" * 4097), (2, "PAY А\n")])])
        self.assertIn("before L2; after L2", result)
        self.assertNotIn("before L1", result)

    def test_empty_hunk_between_valid_disjoint_hunks(self):
        result = render([hunk(), hunk([], []), hunk([(3, "CAP A\n")], [(4, "CAP А\n")])])
        self.assertIn("hunk 003: before L3; after L4", result)

    def test_empty_side_does_not_erase_prior_before_checkpoint(self):
        self.assertEqual(render([hunk(), hunk([], [(2, "unmatched\n")]), hunk([(1, "CAP A\n")], [(3, "CAP А\n")])]), "")

    def test_empty_side_does_not_erase_prior_after_checkpoint(self):
        self.assertEqual(render([hunk(), hunk([(2, "unmatched\n")], []), hunk([(3, "CAP A\n")], [(1, "CAP А\n")])]), "")

    def test_locally_invalid_hunk_keeps_separate_valid_hunk(self):
        invalid = hunk([(0, "PAY A\n")], [(1, "PAY А\n")])
        self.assertIn("hunk 002: before L1; after L1", render([invalid, hunk()]))

    def test_locally_invalid_hunk_does_not_disable_global_gate(self):
        invalid = hunk([(0, "bad\n")], [(15, "bad\n")])
        self.assertEqual(render([hunk(), invalid, hunk()]), "")

    def test_unmatched_rows_still_enforce_cross_hunk_order(self):
        previous = hunk([(1, "PAY A\n"), (99, "unmatched\n")], [(1, "PAY А\n")])
        next_one = hunk([(5, "CAP A\n")], [(5, "CAP А\n")])
        self.assertEqual(render([previous, next_one]), "")

    def test_lower_upper_boundary_lines_accepted(self):
        result = render([hunk([(1, "PAY A\n")], [(1, "PAY А\n")]), hunk([(50000, "CAP A\n")], [(50000, "CAP А\n")])])
        self.assertIn("before L50000; after L50000", result)

    def test_excess_hunk_collection_is_rejected(self):
        self.assertEqual(render([hunk([], [])] * 50001), "")

    def test_existing_16_pair_bound_preserved(self):
        hunks = [hunk([(i, f"{i} A\n")], [(i, f"{i} А\n")]) for i in range(1, 19)]
        result = render(hunks)
        self.assertEqual(result.count("Look-alike hunk"), 16)
        self.assertIn("+2 additional look-alike pair(s) omitted", result)

    def test_output_is_stable_and_privacy_preserving(self):
        source = [hunk([(1, "secret-client PAY A\n")], [(1, "secret-client PAY А\n")])]
        before = repr(source)
        result = render(source)
        self.assertEqual(result, render(source))
        self.assertEqual(repr(source), before)
        self.assertIn("human review", result)
        self.assertNotIn("secret-client", result)
        self.assertIn("CYRILLIC CAPITAL LETTER A", result)


if __name__ == "__main__":
    unittest.main()
