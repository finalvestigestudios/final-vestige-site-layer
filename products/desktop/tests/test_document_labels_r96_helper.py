"""R96 source-document list visibility: offline source-level unit contracts."""
from __future__ import annotations

import copy
import unittest

from fvs_suite.audit_display import visible_source_label_list


class DocumentLabelListR96(unittest.TestCase):
    def test_sorted_distinct_ascii_unchanged(self):
        self.assertEqual(visible_source_label_list(["REC-2", "REC-1", "REC-1"]),
                         "REC-1; REC-2")

    def test_empty_and_spaces(self):
        self.assertEqual(visible_source_label_list(["", " ", "  A  ", "A"]), "A")

    def test_list_separator_cannot_be_forged(self):
        self.assertEqual(visible_source_label_list(["A; B", "C"]), r"A\u003B B; C")

    def test_single_semicolon(self):
        self.assertEqual(visible_source_label_list([";"]), r"\u003B")

    def test_actual_bidi_differs_from_literal_escape(self):
        actual = visible_source_label_list(["INV\u202e7"])
        literal = visible_source_label_list([r"INV\u202E7"])
        self.assertEqual(actual, r"INV\u202E7")
        self.assertEqual(literal, r"INV\\u202E7")
        self.assertNotEqual(actual, literal)

    def test_actual_tab_cr_lf_and_controls(self):
        self.assertEqual(visible_source_label_list(["I\t\r\nD"]),
                         r"I\u0009\u000D\u000AD")

    def test_non_ascii_space_not_trimmed(self):
        self.assertEqual(visible_source_label_list([" \u00a0X\u00a0 "]),
                         r"\u00A0X\u00A0")

    def test_unicode_line_separator_at_edge_not_deleted(self):
        self.assertEqual(visible_source_label_list(["A\u2028"]), r"A\u2028")

    def test_non_control_blank_filler(self):
        self.assertEqual(visible_source_label_list(["A\u2800B"]), r"A\u2800B")

    def test_supplementary_variation_selector(self):
        self.assertEqual(visible_source_label_list(["A\U000E0100"]), r"A\U000E0100")

    def test_preserve_readable_multilingual(self):
        self.assertEqual(visible_source_label_list(["東京", "José"]), "José; 東京")

    def test_literal_backslash_is_escaped(self):
        self.assertEqual(visible_source_label_list([r"A\B"]), r"A\\B")

    def test_preserve_untrusted_source_no_mutation(self):
        originals = [" A; B ", "INV\u202e", r"INV\u202E"]
        cloned = copy.deepcopy(originals)
        first = visible_source_label_list(originals)
        self.assertEqual(first, visible_source_label_list(reversed(originals)))
        self.assertEqual(originals, cloned)

    def test_generator_finite_single_pass(self):
        def source():
            for x in ("B", "A", "B"):
                yield x
        self.assertEqual(visible_source_label_list(source()), "A; B")

    def test_invalid_value_fails_closed_without_private_echo(self):
        with self.assertRaisesRegex(TypeError, "require text") as ctx:
            visible_source_label_list(["A", {"secret": "DO-NOT-ECHO"}])
        self.assertNotIn("DO-NOT-ECHO", str(ctx.exception))

    def test_empty_iterable(self):
        self.assertEqual(visible_source_label_list([]), "")

    def test_unicode_alias_distinct(self):
        self.assertEqual(visible_source_label_list(["REC-1", "REC\u200b-1"]),
                         r"REC-1; REC\u200B-1")

    def test_large_200k_deterministic(self):
        values = [f"REC-{i:06d}" for i in range(200_000)]
        result = visible_source_label_list(reversed(values))
        self.assertEqual(len(result.split("; ")), 200_000)
        self.assertTrue(result.startswith("REC-000000; REC-000001; "))
        self.assertTrue(result.endswith("; REC-199999"))


if __name__ == "__main__":
    unittest.main()
