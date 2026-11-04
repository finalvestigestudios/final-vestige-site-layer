"""R184: historical R180 source-order contract and R183 global custody.

Only synthetic source lines; no file, network, or compliance processing.
The real Policy Delta diff produces monotonically increasing physical rows.
"""
from __future__ import annotations

import unittest

from fvs_suite.policy_confusables import render_local_confusable_evidence as render


def hunk(old=(), new=()):
    return {"removed_sources": list(old), "added_sources": list(new)}


class PolicySourceOrderContractR184(unittest.TestCase):
    def test_ordered_pairs_have_deterministic_physical_order(self):
        data = [hunk([(2, "B\n"), (9, "A\n")], [(2, "Β\n"), (9, "А\n")])]
        result = render(data)
        self.assertLess(result.index("before L2"), result.index("before L9"))
        self.assertEqual(result, render(data))

    def test_reversed_before_rows_with_match_fail_closed(self):
        self.assertEqual(render([hunk([(9, "A\n"), (2, "B\n")],
                                      [(2, "Β\n"), (9, "А\n")])]), "")

    def test_reversed_after_rows_with_match_fail_closed(self):
        self.assertEqual(render([hunk([(2, "B\n"), (9, "A\n")],
                                      [(9, "А\n"), (2, "Β\n")])]), "")

    def test_three_valid_pairs_sorted_on_source_coordinates(self):
        body = render([hunk([(2, "B\n"), (5, "P\n"), (9, "A\n")],
                            [(2, "Β\n"), (6, "Р\n"), (10, "А\n")])])
        self.assertEqual(body.count("Look-alike hunk"), 3)
        self.assertLess(body.index("before L2"), body.index("before L5"))
        self.assertLess(body.index("before L5"), body.index("before L9"))

    def test_two_disjoint_hunks_are_ordered(self):
        body = render([hunk([(2, "B\n")], [(8, "Β\n")]),
                       hunk([(13, "P\n")], [(15, "Р\n")])])
        self.assertLess(body.index("hunk 001"), body.index("hunk 002"))

    def test_reusing_before_coordinate_in_later_hunk_rejected(self):
        self.assertEqual(render([hunk([(2, "B\n")], [(3, "Β\n")]),
                                 hunk([(2, "P\n")], [(8, "Р\n")])]), "")

    def test_reusing_after_coordinate_in_later_hunk_rejected(self):
        self.assertEqual(render([hunk([(2, "B\n")], [(3, "Β\n")]),
                                 hunk([(8, "P\n")], [(3, "Р\n")])]), "")

    def test_backward_moving_before_hunk_rejected(self):
        self.assertEqual(render([hunk([(8, "B\n")], [(2, "Β\n")]),
                                 hunk([(7, "P\n")], [(10, "Р\n")])]), "")

    def test_backward_moving_after_hunk_rejected(self):
        self.assertEqual(render([hunk([(2, "B\n")], [(8, "Β\n")]),
                                 hunk([(10, "P\n")], [(7, "Р\n")])]), "")

    def test_before_only_intermediate_hunk_retains_checkpoint(self):
        self.assertEqual(render([hunk([(2, "B\n")], [(3, "Β\n")]),
                                 hunk([(9, "plain\n")], []),
                                 hunk([(8, "P\n")], [(12, "Р\n")])]), "")

    def test_after_only_intermediate_hunk_retains_checkpoint(self):
        self.assertEqual(render([hunk([(2, "B\n")], [(3, "Β\n")]),
                                 hunk([], [(9, "plain\n")]),
                                 hunk([(12, "P\n")], [(8, "Р\n")])]), "")

    def test_long_unmatched_before_row_still_blocks_reuse(self):
        self.assertEqual(render([hunk([(2, "B\n"), (11, "x" * 4097)], [(3, "Β\n")]),
                                 hunk([(11, "P\n")], [(15, "Р\n")])]), "")

    def test_long_unmatched_after_row_still_blocks_reuse(self):
        self.assertEqual(render([hunk([(2, "B\n")], [(3, "Β\n"), (11, "x" * 4097)]),
                                 hunk([(15, "P\n")], [(11, "Р\n")])]), "")

    def test_valid_gaps_between_rows_do_not_create_fake_citations(self):
        body = render([hunk([(1, "B\n"), (40, "A\n")],
                            [(3, "Β\n"), (50, "А\n")])])
        self.assertIn("before L1; after L3", body)
        self.assertIn("before L40; after L50", body)
        self.assertNotIn("before L2;", body)

    def test_ambiguous_skeleton_suppressed_without_guessing(self):
        self.assertEqual(render([hunk([(1, "A\n"), (2, "А\n")],
                                 [(3, "Α\n")])]), "")

    def test_oversize_lines_skipped_but_short_candidate_remains(self):
        body = render([hunk([(1, "X" * 4097), (3, "A\n")],
                            [(1, "X" * 4097), (3, "А\n")])])
        self.assertIn("before L3; after L3", body)
        self.assertNotIn("before L1;", body)

    def test_untrusted_row_tuple_subclass_rejected_without_iteration(self):
        class Trap(tuple):
            def __iter__(self):
                raise AssertionError("injected iteration")
        self.assertEqual(render([hunk([Trap((1, "A\n"))], [(1, "А\n")])]), "")

    def test_untrusted_hunk_dict_subclass_rejected_without_get(self):
        class Trap(dict):
            def get(self, *_):
                raise AssertionError("injected lookup")
        self.assertEqual(render([Trap(hunk([(1, "A\n")], [(1, "А\n")]))]), "")

    def test_sensitive_line_text_never_repeated_in_navigation(self):
        secret = "private-finance-file-2026"
        body = render([hunk([(1, secret + " A\n")],
                            [(1, secret + " А\n")])])
        self.assertNotIn(secret, body)
        self.assertIn("human review", body)
        self.assertIn("CYRILLIC CAPITAL LETTER A", body)

    def test_50000_line_limit_valid_and_overflow_fails(self):
        self.assertIn("L50000", render([hunk([(50_000, "A\n")],
                                            [(50_000, "А\n")])]))
        self.assertEqual(render([hunk([(50_001, "A\n")],
                                      [(50_001, "А\n")])]), "")


if __name__ == "__main__":
    unittest.main()
