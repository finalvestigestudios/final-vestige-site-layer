"""R365 budget boundary tests: synthetic-only Policy Delta review data."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from fvs_suite import policy_confusable_budget_r365 as budget


def hunk(before="A", after="А", line=1):
    return {"removed_sources": [(line, before)], "added_sources": [(line, after)]}


class ConfusableBudgetR365(unittest.TestCase):
    def test_standard_short_citation_input_passes(self):
        self.assertTrue(budget.within_confusable_budget([hunk()]))

    def test_empty_collection_allowed_for_silent_renderer(self):
        self.assertTrue(budget.within_confusable_budget([]))

    def test_exact_text_budget_is_inclusive(self):
        with patch.object(budget, "MAX_TEXT_CODEPOINTS", 2):
            self.assertTrue(budget.within_confusable_budget([hunk()]))

    def test_one_codepoint_over_text_budget_fails(self):
        with patch.object(budget, "MAX_TEXT_CODEPOINTS", 1):
            self.assertFalse(budget.within_confusable_budget([hunk()]))

    def test_text_budget_spans_many_hunks(self):
        with patch.object(budget, "MAX_TEXT_CODEPOINTS", 3):
            self.assertFalse(budget.within_confusable_budget([hunk(), hunk(line=2)]))

    def test_text_budget_counts_long_uncitable_lines(self):
        with patch.object(budget, "MAX_TEXT_CODEPOINTS", 4096):
            self.assertFalse(budget.within_confusable_budget([hunk("X" * 4097, "")]))

    def test_unicode_codepoints_counted_without_normalizing(self):
        with patch.object(budget, "MAX_TEXT_CODEPOINTS", 2):
            self.assertTrue(budget.within_confusable_budget([hunk("😀", "А")]))
            self.assertFalse(budget.within_confusable_budget([hunk("😀😀", "А")]))

    def test_exact_row_budget_is_inclusive(self):
        with patch.object(budget, "MAX_SOURCE_ROWS", 2):
            self.assertTrue(budget.within_confusable_budget([hunk()]))

    def test_row_budget_spans_both_sides_and_hunks(self):
        with patch.object(budget, "MAX_SOURCE_ROWS", 3):
            self.assertFalse(budget.within_confusable_budget([hunk(), hunk(line=2)]))

    def test_list_length_preflight_avoids_iterating_rows(self):
        class Trap(list):
            def __iter__(self):
                raise AssertionError("untrusted iterator executed")
        sample = hunk()
        sample["added_sources"] = Trap([(1, "А")])
        self.assertFalse(budget.within_confusable_budget([sample]))

    def test_custom_hunk_dict_not_accessed(self):
        class Trap(dict):
            def get(self, _):
                raise AssertionError("untrusted .get executed")
        self.assertFalse(budget.within_confusable_budget([Trap(hunk())]))

    def test_custom_source_tuple_not_accessed(self):
        class Trap(tuple):
            def __getitem__(self, _):
                raise AssertionError("untrusted tuple indexed")
        sample = hunk()
        sample["added_sources"] = [Trap((1, "А"))]
        self.assertFalse(budget.within_confusable_budget([sample]))

    def test_rejects_non_string_source(self):
        sample = hunk()
        sample["removed_sources"] = [(1, b"secret")]
        self.assertFalse(budget.within_confusable_budget([sample]))

    def test_rejects_bool_line_identity(self):
        sample = hunk()
        sample["removed_sources"] = [(True, "A")]
        self.assertFalse(budget.within_confusable_budget([sample]))

    def test_invalid_late_hunk_cannot_be_ignored(self):
        self.assertFalse(budget.within_confusable_budget([hunk(), {"removed_sources": []}]))

    def test_invalid_top_container(self):
        self.assertFalse(budget.within_confusable_budget((hunk(),)))

    def test_hunk_budget(self):
        with patch.object(budget, "MAX_HUNKS", 1):
            self.assertFalse(budget.within_confusable_budget([hunk(), hunk(line=2)]))

    def test_does_not_mutate_source_records(self):
        rows = [hunk()]
        before = repr(rows)
        self.assertTrue(budget.within_confusable_budget(rows))
        self.assertEqual(before, repr(rows))

    def test_private_values_not_in_return(self):
        result = budget.within_confusable_budget([hunk("client-private-data", "А")])
        self.assertIs(type(result), bool)

    def test_stored_custom_key_is_rejected_without_key_equality(self):
        class Key:
            def __hash__(self):
                return 123
            def __eq__(self, _):
                raise AssertionError("untrusted equality executed")
        sample = hunk()
        sample[Key()] = "injected"
        self.assertFalse(budget.within_confusable_budget([sample]))


if __name__ == "__main__":
    unittest.main()
