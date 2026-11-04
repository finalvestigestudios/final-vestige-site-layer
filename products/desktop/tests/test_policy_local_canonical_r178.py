"""R178: source-line-cited, bounded NFC-only Policy Delta navigation.

All values are synthetic; no advice or compliance determination is produced.
"""
from __future__ import annotations

import unittest

from fvs_suite.policy_canonical import render_local_canonical_evidence as render


def hunk(old=(), new=()):
    return {"removed_sources": list(old), "added_sources": list(new)}


class PolicyLocalCanonicalR178(unittest.TestCase):
    def test_composed_decomposed(self):
        self.assertIn("before L2; after L3; NFC-only candidate",
                      render([hunk([(2, "Café\n")], [(3, "Cafe\u0301\n")])]))

    def test_decomposed_composed(self):
        self.assertIn("before L9; after L7; NFC-only candidate",
                      render([hunk([(9, "Cafe\u0301\n")], [(7, "Café\n")])]))

    def test_reordered_combining_marks(self):
        self.assertIn("NFC-only candidate", render([
            hunk([(1, "e\u0301\u0323\n")], [(1, "e\u0323\u0301\n")])]))

    def test_hiragana_decomposition(self):
        self.assertIn("NFC-only candidate", render([
            hunk([(1, "が\n")], [(1, "か\u3099\n")])]))

    def test_korean_hangul_composition(self):
        self.assertIn("NFC-only candidate", render([
            hunk([(1, "가\n")], [(1, "가\n")])]))

    def test_true_policy_edit_not_paired(self):
        self.assertEqual(render([hunk([(1, "Limit 10\n")], [(1, "Limit 20\n")])]), "")

    def test_nfkc_only_fullwidth_not_paired(self):
        self.assertEqual(render([hunk([(1, "Ａ\n")], [(1, "A\n")])]), "")

    def test_nfkc_only_ligature_not_paired(self):
        self.assertEqual(render([hunk([(1, "oﬃce\n")], [(1, "office\n")])]), "")

    def test_same_text_not_paired(self):
        self.assertEqual(render([hunk([(1, "same\n")], [(2, "same\n")])]), "")

    def test_only_added_not_paired(self):
        self.assertEqual(render([hunk([], [(1, "Cafe\u0301\n")])]), "")

    def test_only_removed_not_paired(self):
        self.assertEqual(render([hunk([(1, "Café\n")], [])]), "")

    def test_nothing_changed(self):
        self.assertEqual(render([]), "")

    def test_duplicate_old_normalized_text_suppresses_pair(self):
        self.assertEqual(render([hunk([(1, "Café\n"), (2, "Cafe\u0301\n")],
                                      [(1, "Café\n")])]), "")

    def test_duplicate_new_normalized_text_suppresses_pair(self):
        self.assertEqual(render([hunk([(1, "Café\n")],
                                      [(1, "Cafe\u0301\n"), (2, "Café\n")])]), "")

    def test_duplicates_in_both_sides_suppressed(self):
        self.assertEqual(render([hunk([(1, "Café\n"), (2, "Café\n")],
                                      [(1, "Cafe\u0301\n"), (2, "Cafe\u0301\n")])]), "")

    def test_no_cross_hunk_pairing(self):
        self.assertEqual(render([hunk([(1, "Café\n")]),
                                 hunk(new=[(90, "Cafe\u0301\n")])]), "")

    def test_multiple_hunks_numbered_and_sorted(self):
        result = render([hunk([(15, "Café\n")], [(20, "Cafe\u0301\n")]),
                         hunk([(30, "が\n")], [(31, "か\u3099\n")])])
        self.assertLess(result.index("hunk 001"), result.index("hunk 002"))

    def test_two_pairs_in_one_hunk_physical_order(self):
        result = render([hunk([(11, "Café\n"), (3, "が\n")],
                              [(11, "Cafe\u0301\n"), (3, "か\u3099\n")])])
        self.assertLess(result.index("before L3"), result.index("before L11"))

    def test_mixed_substantive_change_retains_one_canonical_pair(self):
        result = render([hunk([(1, "Café\n"), (2, "Owner A\n")],
                              [(1, "Cafe\u0301\n"), (2, "Owner B\n")])])
        self.assertEqual(result.count("NFC-only candidate"), 1)

    def test_eof_difference_not_aliased_to_canonical_edit(self):
        self.assertEqual(render([hunk([(1, "Café\n")], [(1, "Café")])]), "")

    def test_crlf_difference_not_aliased_to_canonical_edit(self):
        self.assertEqual(render([hunk([(1, "Café\r\n")], [(1, "Café\n")])]), "")

    def test_sixteen_bounded_pairs(self):
        values = [hunk([(i, f"{i} Café\n")], [(i, f"{i} Cafe\u0301\n")])
                  for i in range(1, 17)]
        result = render(values)
        self.assertEqual(result.count("NFC-only candidate;"), 16)
        self.assertNotIn("omitted", result.split("Canonical hunk")[-1])

    def test_seventeen_bounded_with_explicit_omission(self):
        values = [hunk([(i, f"{i} Café\n")], [(i, f"{i} Cafe\u0301\n")])
                  for i in range(1, 18)]
        result = render(values)
        self.assertEqual(result.count("NFC-only candidate;"), 16)
        self.assertIn("+1 additional canonical candidate pair(s) omitted", result)
        self.assertNotIn("hunk 017", result)

    def test_deterministic_multiple_candidates(self):
        values = [hunk([(5, "é\n"), (1, "Café\n")],
                       [(5, "e\u0301\n"), (1, "Cafe\u0301\n")])]
        self.assertEqual(render(values), render(values))

    def test_original_private_text_not_echoed(self):
        result = render([hunk([(7, "private-secret-Café\n")],
                              [(7, "private-secret-Cafe\u0301\n")])])
        self.assertNotIn("private-secret", result)
        self.assertIn("before L7; after L7", result)

    def test_human_review_caveat_present(self):
        result = render([hunk([(1, "é\n")], [(1, "e\u0301\n")])])
        self.assertIn("NOT legal or semantic equivalence", result)
        self.assertIn("human review", result)

    def test_existing_unrelated_keys_ignored(self):
        value = hunk([(1, "é\n")], [(1, "e\u0301\n")])
        value["deleted"] = 999
        self.assertIn("NFC-only candidate", render([value]))

    def test_distinct_glyph_not_canonical_equivalence(self):
        self.assertEqual(render([hunk([(1, "A\n")], [(1, "А\n")])]), "")


if __name__ == "__main__":
    unittest.main()
