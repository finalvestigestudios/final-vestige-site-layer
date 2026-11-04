"""R181: deterministic spoken names for bounded cross-script review evidence."""
from __future__ import annotations

import unittest
from fvs_suite.policy_confusables import _changes, render_local_confusable_evidence


def cue(before, after):
    return render_local_confusable_evidence([{
        "removed_sources": [(1, before)], "added_sources": [(2, after)]
    }])


class PolicyCharacterNamesR181(unittest.TestCase):
    def test_latin_capital_to_cyrillic_capital(self):
        self.assertIn("[LATIN CAPITAL LETTER A -> CYRILLIC CAPITAL LETTER A]", cue("A\n", "А\n"))

    def test_cyrillic_to_latin(self):
        self.assertIn("[CYRILLIC CAPITAL LETTER A -> LATIN CAPITAL LETTER A]", cue("А\n", "A\n"))

    def test_greek_to_latin(self):
        self.assertIn("[GREEK SMALL LETTER OMICRON -> LATIN SMALL LETTER O]", cue("ο\n", "o\n"))

    def test_cyrillic_to_greek(self):
        self.assertIn("[CYRILLIC CAPITAL LETTER O -> GREEK CAPITAL LETTER OMICRON]", cue("О\n", "Ο\n"))

    def test_latin_to_greek(self):
        self.assertIn("[LATIN CAPITAL LETTER B -> GREEK CAPITAL LETTER BETA]", cue("B\n", "Β\n"))

    def test_lowercase_reverse(self):
        self.assertIn("[CYRILLIC SMALL LETTER O -> LATIN SMALL LETTER O]", cue("о\n", "o\n"))

    def test_two_characters_independent_names(self):
        result = cue("COST\n", "CОSТ\n")
        self.assertIn("[LATIN CAPITAL LETTER O -> CYRILLIC CAPITAL LETTER O]", result)
        self.assertIn("[LATIN CAPITAL LETTER T -> CYRILLIC CAPITAL LETTER TE]", result)
        self.assertEqual(result.count("[LATIN CAPITAL LETTER"), 2)

    def test_preserve_machine_numeric_citations(self):
        result = cue("PAID\n", "PАID\n")
        self.assertIn("before L1; after L2; column 2 U+0041->U+0410", result)

    def test_no_source_text_repeated(self):
        result = cue("secret-supplier-account A\n", "secret-supplier-account А\n")
        self.assertNotIn("secret-supplier-account", result)
        self.assertIn("LATIN CAPITAL LETTER", result)

    def test_no_name_when_no_change(self):
        self.assertEqual(cue("A\n", "A\n"), "")

    def test_no_name_when_substantive_change(self):
        self.assertEqual(cue("Amount A\n", "Amount Б\n"), "")

    def test_not_canonical_unicode_folding(self):
        self.assertEqual(cue("é\n", "e\u0301\n"), "")

    def test_not_fullwidth_compatibility_folding(self):
        self.assertEqual(cue("Ａ\n", "A\n"), "")

    def test_direct_function_rejects_non_native_text(self):
        class Trap(str):
            def __iter__(self):
                raise AssertionError("untrusted iterator")
        self.assertEqual(_changes(Trap("A"), "А"), "")

    def test_exact_eight_names_shown(self):
        result = _changes("A" * 8, "А" * 8)
        self.assertEqual(result.count("[LATIN CAPITAL LETTER A"), 8)
        self.assertNotIn("omitted", result)

    def test_nine_names_bounded(self):
        result = _changes("A" * 9, "А" * 9)
        self.assertEqual(result.count("[LATIN CAPITAL LETTER A"), 8)
        self.assertIn("(+1 substitution(s) omitted)", result)

    def test_eighteen_pairs_limit(self):
        hunks = [{"removed_sources": [(i, f"{i} A\n")],
                  "added_sources": [(i, f"{i} А\n")]} for i in range(1, 19)]
        result = render_local_confusable_evidence(hunks)
        self.assertEqual(result.count("[LATIN CAPITAL LETTER A"), 16)
        self.assertIn("+2 additional look-alike pair(s) omitted", result)

    def test_private_unicode_source_does_not_appear(self):
        before = "SENSITIVE CLIENT 独自 A\n"
        after = "SENSITIVE CLIENT 独自 А\n"
        result = cue(before, after)
        self.assertNotIn("SENSITIVE CLIENT", result)
        self.assertNotIn("独自", result)

    def test_readable_caution_retained(self):
        result = cue("A\n", "А\n")
        self.assertIn("NOT a comprehensive", result)
        self.assertIn("human review", result)

    def test_zero_hunks(self):
        self.assertEqual(render_local_confusable_evidence([]), "")

    def test_unsupported_cyrillic_unpaired(self):
        self.assertEqual(cue("А\n", "Б\n"), "")

    def test_output_repeatability(self):
        self.assertEqual(cue("PAY\n", "PАY\n"), cue("PAY\n", "PАY\n"))

    def test_limit_long_source_lines(self):
        self.assertEqual(cue("A" * 4097, "А" + "A" * 4096), "")

    def test_no_duplicate_ambiguous_pair(self):
        h = {"removed_sources": [(1, "A\n"), (2, "А\n")],
             "added_sources": [(3, "Α\n")]}
        self.assertEqual(render_local_confusable_evidence([h]), "")

    def test_names_are_ascii_only(self):
        result = cue("A\n", "А\n")
        name = result.split("[", 1)[1].split("]", 1)[0]
        self.assertTrue(name.isascii())


if __name__ == "__main__":
    unittest.main()
