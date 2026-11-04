"""R182: fail-closed source-coordinate custody for Policy Delta review cues.

All input records are synthetic; never touches real policy or financial files.
"""
from __future__ import annotations

import unittest

from fvs_suite.policy_confusables import (
    _changes, render_local_confusable_evidence as render,
)


def hunk(old=((1, "PAY A\n"),), new=((2, "PAY А\n"),)):
    return {"removed_sources": list(old), "added_sources": list(new)}


class PolicyConfusableSourceCustodyR182(unittest.TestCase):
    def test_valid_before_after_source_coordinates(self):
        self.assertIn("before L1; after L2", render([hunk()]))

    def test_two_hunks_remain_distinct(self):
        result = render([hunk(), hunk([(7, "PAY A\n")], [(8, "PAY А\n")])])
        self.assertIn("hunk 001: before L1; after L2", result)
        self.assertIn("hunk 002: before L7; after L8", result)

    def test_no_hunks(self):
        self.assertEqual(render([]), "")

    def test_non_list_hunk_collection_fails_closed(self):
        self.assertEqual(render(iter([hunk()])), "")

    def test_list_subclass_is_not_iterated(self):
        class Trap(list):
            def __iter__(self):
                raise AssertionError("unsafe list iterator")
        self.assertEqual(render(Trap([hunk()])), "")

    def test_non_dict_hunk_fails_closed(self):
        self.assertEqual(render([object()]), "")

    def test_dict_subclass_not_accessed(self):
        class Trap(dict):
            def get(self, *_):
                raise AssertionError("unsafe mapping access")
        self.assertEqual(render([Trap(hunk())]), "")

    def test_missing_removed_sources(self):
        self.assertEqual(render([{"added_sources": [(2, "PAY А\n")]}]), "")

    def test_missing_added_sources(self):
        self.assertEqual(render([{"removed_sources": [(1, "PAY A\n")]}]), "")

    def test_tuple_rows_rejected(self):
        value = hunk()
        value["removed_sources"] = tuple(value["removed_sources"])
        self.assertEqual(render([value]), "")

    def test_list_subclass_rows_not_iterated(self):
        class Trap(list):
            def __iter__(self):
                raise AssertionError("unsafe row iteration")
        value = hunk()
        value["removed_sources"] = Trap(value["removed_sources"])
        self.assertEqual(render([value]), "")

    def test_list_row_rejected(self):
        self.assertEqual(render([hunk(old=[[1, "PAY A\n"]])]), "")

    def test_tuple_subclass_row_not_unpacked(self):
        class Trap(tuple):
            def __iter__(self):
                raise AssertionError("unsafe tuple iterator")
        self.assertEqual(render([hunk(old=[Trap((1, "PAY A\n"))])]), "")

    def test_zero_length_row_rejected(self):
        self.assertEqual(render([hunk(old=[()])]), "")

    def test_triple_row_rejected(self):
        self.assertEqual(render([hunk(old=[(1, "PAY A\n", "forged")])]), "")

    def test_zero_source_line_rejected(self):
        self.assertEqual(render([hunk(old=[(0, "PAY A\n")])]), "")

    def test_negative_source_line_rejected(self):
        self.assertEqual(render([hunk(old=[(-1, "PAY A\n")])]), "")

    def test_over_limit_before_line_rejected(self):
        self.assertEqual(render([hunk(old=[(50_001, "PAY A\n")])]), "")

    def test_over_limit_after_line_rejected(self):
        self.assertEqual(render([hunk(new=[(50_001, "PAY А\n")])]), "")

    def test_exact_limit_permitted(self):
        result = render([hunk(old=[(50_000, "PAY A\n")], new=[(50_000, "PAY А\n")])])
        self.assertIn("before L50000; after L50000", result)

    def test_boolean_source_line_rejected(self):
        self.assertEqual(render([hunk(old=[(True, "PAY A\n")])]), "")

    def test_integer_subclass_not_executed(self):
        class Trap(int):
            def __hash__(self):
                raise AssertionError("unsafe hash")
        self.assertEqual(render([hunk(old=[(Trap(1), "PAY A\n")])]), "")

    def test_float_source_line_rejected(self):
        self.assertEqual(render([hunk(old=[(1.0, "PAY A\n")])]), "")

    def test_string_source_line_rejected(self):
        self.assertEqual(render([hunk(old=[("1", "PAY A\n")])]), "")

    def test_duplicate_before_line_rejected(self):
        value = hunk(old=[(1, "PAY A\n"), (1, "FEE A\n")])
        self.assertEqual(render([value]), "")

    def test_duplicate_after_line_rejected(self):
        value = hunk(new=[(2, "PAY А\n"), (2, "FEE А\n")])
        self.assertEqual(render([value]), "")

    def test_invalid_before_suppresses_otherwise_valid_candidate(self):
        value = hunk(old=[(1, "PAY A\n"), (1, "unrelated\n")])
        self.assertEqual(render([value]), "")

    def test_invalid_after_suppresses_otherwise_valid_candidate(self):
        value = hunk(new=[(2, "PAY А\n"), (2, "unrelated\n")])
        self.assertEqual(render([value]), "")

    def test_text_subclass_rejected_without_iteration(self):
        class Trap(str):
            def __iter__(self):
                raise AssertionError("unsafe text iterator")
        self.assertEqual(render([hunk(old=[(1, Trap("PAY A\n"))])]), "")

    def test_object_text_rejected(self):
        class Trap:
            def __str__(self):
                raise AssertionError("unsafe string cast")
        self.assertEqual(render([hunk(old=[(1, Trap())])]), "")

    def test_long_line_skipped_without_suppressing_short_candidate(self):
        value = hunk(old=[(1, "A" * 4097), (3, "PAY A\n")],
                     new=[(2, "А" * 4097), (4, "PAY А\n")])
        result = render([value])
        self.assertIn("before L3; after L4", result)
        self.assertNotIn("before L1", result)

    def test_invalid_hunk_does_not_suppress_independent_valid_hunk(self):
        result = render([hunk(old=[(0, "PAY A\n")]), hunk()])
        self.assertIn("hunk 002: before L1; after L2", result)
        self.assertNotIn("hunk 001", result)

    def test_source_rows_unchanged(self):
        value = hunk()
        original = repr(value)
        render([value])
        self.assertEqual(repr(value), original)

    def test_private_source_content_not_repeated(self):
        result = render([hunk(old=[(1, "secret-client PAY A\n")],
                              new=[(2, "secret-client PAY А\n")])])
        self.assertNotIn("secret-client", result)
        self.assertIn("human review", result)

    def test_numeric_and_spoken_cues_preserved(self):
        result = render([hunk()])
        self.assertIn("U+0041->U+0410", result)
        self.assertIn("LATIN CAPITAL LETTER A -> CYRILLIC CAPITAL LETTER A", result)

    def test_legacy_ambiguous_skeletons_still_suppressed(self):
        value = hunk(old=[(1, "PAY A\n"), (2, "PAY А\n")],
                     new=[(3, "PAY Α\n")])
        self.assertEqual(render([value]), "")

    def test_legacy_bounded_pair_count(self):
        values = [hunk([(i, f"{i} A\n")], [(i, f"{i} А\n")]) for i in range(1, 19)]
        result = render(values)
        self.assertEqual(result.count("Look-alike hunk"), 16)
        self.assertIn("+2 additional look-alike pair(s) omitted", result)

    def test_legacy_bounded_codepoint_count(self):
        value = _changes("A" * 10, "А" * 10)
        self.assertEqual(value.count("column"), 8)
        self.assertIn("(+2 substitution(s) omitted)", value)


if __name__ == "__main__":
    unittest.main()
