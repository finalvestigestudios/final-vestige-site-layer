"""R180: deterministic, private-source-free look-alike navigation tests."""
from __future__ import annotations

import unittest
from fvs_suite.policy_confusables import _changes, render_local_confusable_evidence as render


def hunk(old=(), new=()):
    return {"removed_sources": list(old), "added_sources": list(new)}


class PolicyConfusableR180(unittest.TestCase):
    def test_latin_to_cyrillic_a(self):
        value = render([hunk([(2, "PAYMENT\n")], [(3, "PАYMENT\n")])])
        self.assertIn("before L2; after L3", value)
        self.assertIn("column 2 U+0041->U+0410", value)
        self.assertNotIn("omitted", value)

    def test_cyrillic_to_latin_a(self):
        self.assertIn("U+0410->U+0041", render([hunk([(1, "А\n")], [(1, "A\n")])]))

    def test_greek_omicron_to_latin_o(self):
        self.assertIn("U+03BF->U+006F", render([hunk([(1, "ο\n")], [(1, "o\n")])]))

    def test_latin_o_to_cyrillic_o(self):
        self.assertIn("U+006F->U+043E", render([hunk([(1, "o\n")], [(1, "о\n")])]))

    def test_cyrillic_to_greek_same_shape(self):
        self.assertIn("U+041E->U+039F", render([hunk([(1, "О\n")], [(1, "Ο\n")])]))

    def test_two_substitutions_in_one_line(self):
        result = render([hunk([(1, "COST\n")], [(1, "CОSТ\n")])])
        self.assertIn("column 2 U+004F->U+041E", result)
        self.assertIn("column 4 U+0054->U+0422", result)

    def test_substantive_change_not_paired(self):
        self.assertEqual(render([hunk([(1, "Cost 10\n")], [(1, "Cоst 20\n")])]), "")

    def test_changed_case_not_paired(self):
        self.assertEqual(render([hunk([(1, "A\n")], [(1, "а\n")])]), "")

    def test_canonical_accent_not_paired(self):
        self.assertEqual(render([hunk([(1, "é\n")], [(1, "e\u0301\n")])]), "")

    def test_nfkc_fullwidth_not_paired(self):
        self.assertEqual(render([hunk([(1, "Ａ\n")], [(1, "A\n")])]), "")

    def test_unchanged_text_not_paired(self):
        self.assertEqual(render([hunk([(1, "А\n")], [(1, "А\n")])]), "")

    def test_no_cross_hunk_paired(self):
        self.assertEqual(render([hunk([(1, "A\n")]), hunk(new=[(2, "А\n")])]), "")

    def test_duplicate_old_suppressed(self):
        self.assertEqual(render([hunk([(1, "A\n"), (2, "А\n")], [(1, "Α\n")])]), "")

    def test_duplicate_new_suppressed(self):
        self.assertEqual(render([hunk([(1, "A\n")], [(1, "А\n"), (2, "Α\n")])]), "")

    def test_only_added_or_removed(self):
        self.assertEqual(render([hunk(new=[(1, "А\n")])]), "")
        self.assertEqual(render([hunk([(1, "A\n")])]), "")

    def test_private_source_not_duplicated(self):
        secret = "confidential-client-098765"
        result = render([hunk([(1, secret + " A\n")],
                              [(2, secret + " А\n")])])
        self.assertNotIn(secret, result)
        self.assertIn("before L1; after L2", result)

    def test_caveat_and_human_review(self):
        result = render([hunk([(1, "A\n")], [(1, "А\n")])])
        self.assertIn("NOT a comprehensive", result)
        self.assertIn("human review", result)

    def test_deterministic_sorted_physical_lines(self):
        value = hunk([(2, "B\n"), (9, "A\n")], [(2, "Β\n"), (9, "А\n")])
        result = render([value])
        self.assertEqual(result, render([value]))
        self.assertLess(result.index("before L2"), result.index("before L9"))

    def test_two_hunks_kept_separate(self):
        result = render([hunk([(1, "A\n")], [(1, "А\n")]),
                         hunk([(20, "P\n")], [(22, "Р\n")])])
        self.assertLess(result.index("hunk 001"), result.index("hunk 002"))

    def test_max_sixteen_pairs(self):
        values = [hunk([(i, f"{i} A\n")], [(i, f"{i} А\n")]) for i in range(1, 19)]
        result = render(values)
        self.assertEqual(result.count("Look-alike hunk"), 16)
        self.assertIn("+2 additional look-alike pair(s) omitted", result)
        self.assertNotIn("hunk 017", result)

    def test_max_eight_codepoint_changes(self):
        cue = _changes("A" * 10, "А" * 10)
        self.assertEqual(cue.count("column"), 8)
        self.assertIn("(+2 substitution(s) omitted)", cue)

    def test_long_line_not_explored(self):
        self.assertEqual(render([hunk([(1, "A" * 4097)], [(1, "А" * 4097)])]), "")

    def test_short_line_limit_exact(self):
        self.assertIn("Look-alike hunk", render([
            hunk([(1, "A" * 4096)], [(1, "А" + "A" * 4095)])]))

    def test_invalid_line_number_skipped(self):
        self.assertEqual(render([hunk([(0, "A\n")], [(1, "А\n")])]), "")
        self.assertEqual(render([hunk([(True, "A\n")], [(1, "А\n")])]), "")

    def test_str_subclass_not_executed(self):
        class Forged(str):
            def __iter__(self):
                raise AssertionError("must not run")
        self.assertEqual(render([hunk([(1, Forged("A\n"))], [(1, "А\n")])]), "")

    def test_regular_cyrillic_language_no_flag(self):
        self.assertEqual(render([hunk([(1, "Договор\n")], [(1, "Контракт\n")])]), "")

    def test_no_hunks(self):
        self.assertEqual(render([]), "")


if __name__ == "__main__":
    unittest.main()
