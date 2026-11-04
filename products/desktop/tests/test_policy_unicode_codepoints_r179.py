"""R179: bounded, accessible Unicode codepoint cues in offline policy review.

Synthetic data only. These are navigation hints, never legal equivalence.
"""
from __future__ import annotations

import unittest
from fvs_suite.policy_canonical import (
    _canonical_codepoint_cue as cue,
    render_local_canonical_evidence as render,
)


def hunk(old, new):
    return {"removed_sources": list(old), "added_sources": list(new)}


class PolicyCodepointNavigationR179(unittest.TestCase):
    def test_composed_accent_replaced_with_combining_mark(self):
        result = render([hunk([(4, "Café\n")], [(7, "Cafe\u0301\n")])])
        self.assertIn("U+00E9 1->0", result)
        self.assertIn("U+0301 0->1", result)

    def test_reverse_accent_counts(self):
        result = render([hunk([(4, "Cafe\u0301\n")], [(7, "Café\n")])])
        self.assertIn("U+00E9 0->1", result)
        self.assertIn("U+0301 1->0", result)

    def test_hangul_counts(self):
        result = render([hunk([(1, "가\n")], [(1, "가\n")])])
        for item in ("U+1100 0->1", "U+1161 0->1", "U+AC00 1->0"):
            self.assertIn(item, result)

    def test_japanese_combining_mark_counts(self):
        result = render([hunk([(1, "が\n")], [(1, "か\u3099\n")])])
        self.assertIn("U+304B 0->1", result)
        self.assertIn("U+304C 1->0", result)
        self.assertIn("U+3099 0->1", result)

    def test_reordered_marks_explicitly_report_same_counts(self):
        result = render([hunk([(1, "e\u0301\u0323\n")], [(1, "e\u0323\u0301\n")])])
        self.assertIn("non-ASCII counts unchanged; inspect codepoint order", result)

    def test_identical_raw_lines_no_codepoint_cue(self):
        self.assertEqual(render([hunk([(1, "Café\n")], [(1, "Café\n")])]), "")

    def test_substantive_only_change_not_mislabeled(self):
        self.assertEqual(render([hunk([(1, "Limit 10\n")], [(1, "Limit 20\n")])]), "")

    def test_nfkc_only_change_not_mislabeled(self):
        self.assertEqual(render([hunk([(1, "①\n")], [(1, "1\n")])]), "")

    def test_private_source_text_not_echoed(self):
        private = "client-super-secret-01234"
        result = render([hunk([(8, private + "-Café\n")],
                              [(9, private + "-Cafe\u0301\n")])])
        self.assertNotIn(private, result)
        self.assertIn("before L8; after L9", result)

    def test_human_review_notice_retained(self):
        result = render([hunk([(1, "é\n")], [(1, "e\u0301\n")])])
        self.assertIn("NOT legal or semantic equivalence", result)
        self.assertIn("human review", result)

    def test_numeric_metadata_ignores_unchanged_ascii(self):
        self.assertEqual(cue("secret-é\n", "secret-e\u0301\n"),
                         "non-ASCII codepoint counts U+00E9 1->0, U+0301 0->1")

    def test_numeric_metadata_repeated_counts(self):
        self.assertIn("U+00E9 2->0", cue("éé", "e\u0301e\u0301"))
        self.assertIn("U+0301 0->2", cue("éé", "e\u0301e\u0301"))

    def test_supplementary_nonascii_codepoint_format(self):
        self.assertIn("U+1F600 1->0", cue("\U0001f600", ""))

    def test_only_after_has_nonascii(self):
        self.assertEqual(cue("ABC", "ABC\u0301"),
                         "non-ASCII codepoint counts U+0301 0->1")

    def test_only_before_has_nonascii(self):
        self.assertEqual(cue("ABC\u0301", "ABC"),
                         "non-ASCII codepoint counts U+0301 1->0")

    def test_twelve_distinct_changes_within_limit(self):
        old = "".join(chr(0x3100 + n) for n in range(12))
        result = cue(old, "")
        self.assertEqual(result.count("U+"), 12)
        self.assertNotIn("omitted", result)

    def test_thirteen_distinct_changes_are_truncated(self):
        old = "".join(chr(0x3100 + n) for n in range(13))
        result = cue(old, "")
        self.assertEqual(result.count("U+"), 12)
        self.assertIn("(+1 omitted)", result)

    def test_exactly_64_distinct_unicode_points_accepted(self):
        old = "".join(chr(0x4e00 + n) for n in range(64))
        self.assertNotIn("withheld", cue(old, ""))
        self.assertIn("(+52 omitted)", cue(old, ""))

    def test_65_distinct_before_fail_closed_on_detail(self):
        old = "".join(chr(0x4e00 + n) for n in range(65))
        self.assertIn("detail withheld", cue(old, ""))

    def test_65_distinct_after_fail_closed_on_detail(self):
        after = "".join(chr(0x4e00 + n) for n in range(65))
        self.assertIn("detail withheld", cue("", after))

    def test_multiple_hunks_have_independent_counts(self):
        result = render([hunk([(4, "Café\n")], [(4, "Cafe\u0301\n")]),
                         hunk([(40, "가\n")], [(41, "가\n")])])
        self.assertLess(result.index("U+00E9"), result.index("U+1100"))
        self.assertEqual(result.count("NFC-only candidate;"), 2)

    def test_omitted_hunk_has_no_extra_detail(self):
        values = [hunk([(i, f"{i}: Café\n")], [(i, f"{i}: Cafe\u0301\n")])
                  for i in range(1, 19)]
        result = render(values)
        self.assertEqual(result.count("NFC-only candidate;"), 16)
        self.assertIn("+2 additional canonical candidate pair(s) omitted", result)
        self.assertNotIn("Canonical hunk 017", result)

    def test_reordered_hunk_storage_produces_deterministic_report(self):
        items = [hunk([(9, "é\n"), (2, "Café\n")],
                      [(9, "e\u0301\n"), (2, "Cafe\u0301\n")])]
        self.assertEqual(render(items), render(items))
        self.assertLess(render(items).index("before L2"), render(items).index("before L9"))

    def test_line_endings_not_confused_with_normalization(self):
        self.assertEqual(render([hunk([(1, "Café\r\n")], [(1, "Café\n")])]), "")


if __name__ == "__main__":
    unittest.main()
