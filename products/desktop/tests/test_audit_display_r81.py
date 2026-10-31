"""R81: unambiguous source reference display for both premium products.

Pure offline tests; does not imply a Windows binary or release-gate pass.
"""
from __future__ import annotations

import unittest
import unicodedata
from types import SimpleNamespace

from fvs_suite.audit_display import (
    _escape_source_character, visible_review_row, visible_source_text,
)


class AuditSourceDisplayR81(unittest.TestCase):
    def test_ascii_and_whitespace_compatibility(self):
        for value in ("", "GRANT-2026 / 4", "variance_review", "  PO-102 / 1  ",
                      "a+b=c", "line 002", "human review pending"):
            with self.subTest(value=value):
                self.assertEqual(visible_source_text(value), value)

    def test_multilingual_letters_and_combining_accents(self):
        for value in ("José", "東京-資金", "مراجعة", "किराया", "e\u0301vidence", "€100.00"):
            with self.subTest(value=value):
                self.assertEqual(visible_source_text(value), value)

    def test_literal_escape_distinct_from_control(self):
        self.assertEqual(visible_source_text(r"ID\u202E"), r"ID\\u202E")
        self.assertEqual(visible_source_text("ID\u202e"), r"ID\u202E")
        self.assertNotEqual(visible_source_text(r"ID\u202E"), visible_source_text("ID\u202e"))

    def test_mixed_backslash_tab_carriage_return_newline(self):
        self.assertEqual(visible_source_text("X\\\tY\r\n"), r"X\\\u0009Y\u000D\u000A")

    def test_every_ascii_and_c1_control_escaped(self):
        for cp in (*range(0x20), 0x7F, *range(0x80, 0xA0)):
            with self.subTest(cp=cp):
                self.assertEqual(visible_source_text(chr(cp)), f"\\u{cp:04X}")

    def test_c1_escaped_readable_unicode_retained(self):
        self.assertEqual(visible_source_text("PO-\u0085-2"), r"PO-\u0085-2")
        self.assertEqual(visible_source_text("PO-乙-2"), "PO-乙-2")

    def test_bidi_controls_and_zero_width_escaped(self):
        for cp in (0x061C, 0x200B, 0x200C, 0x200D, 0x202A, 0x202E,
                   0x2060, 0x2066, 0x2069, 0xFEFF):
            with self.subTest(cp=hex(cp)):
                self.assertEqual(visible_source_text("ref" + chr(cp) + "id"),
                                 f"ref\\u{cp:04X}id")

    def test_line_and_paragraph_separators_escaped(self):
        self.assertEqual(visible_source_text("A\u2028B\u2029C"), r"A\u2028B\u2029C")

    def test_non_ascii_spacing_escaped(self):
        for cp in (0x00A0, 0x1680, 0x2007, 0x2009, 0x202F, 0x205F, 0x3000):
            with self.subTest(cp=hex(cp)):
                self.assertEqual(visible_source_text("A" + chr(cp) + "B"), f"A\\u{cp:04X}B")
        self.assertEqual(visible_source_text("A B"), "A B")

    def test_bmp_variation_selectors_and_grapheme_joiner(self):
        for cp in (0x034F, 0x180B, 0x180E, 0x180F, 0xFE00, 0xFE0F):
            with self.subTest(cp=hex(cp)):
                self.assertEqual(visible_source_text(chr(cp)), f"\\u{cp:04X}")

    def test_supplementary_variation_selectors(self):
        for cp in (0xE0100, 0xE010F, 0xE01EF):
            with self.subTest(cp=hex(cp)):
                self.assertEqual(visible_source_text(chr(cp)), f"\\U{cp:08X}")

    def test_surrogates_private_use_unassigned(self):
        for cp in (0xD800, 0xDFFF, 0xE000, 0xF8FF, 0x0378):
            with self.subTest(cp=hex(cp)):
                self.assertEqual(visible_source_text(chr(cp)), f"\\u{cp:04X}")

    def test_formula_prefix_retained_for_csv_guard(self):
        self.assertEqual(visible_source_text("=SUM(A1:A2)"), "=SUM(A1:A2)")
        self.assertEqual(visible_source_text("\u200B=SUM(A1:A2)"),
                         r"\u200B=SUM(A1:A2)")

    def test_determinism(self):
        value = "ß\u202E\\\u00A0A\U000E0100\t"
        first = visible_source_text(value)
        for _ in range(10):
            self.assertEqual(visible_source_text(value), first)
        self.assertEqual(first, r"ß\u202E\\\u00A0A\U000E0100\u0009")

    def test_nontext_rejected_no_private_echo(self):
        for value in (None, 7, b"sensitive", ["sensitive"]):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaisesRegex(TypeError, "requires text") as problem:
                    visible_source_text(value)
                self.assertNotIn("sensitive", str(problem.exception))

    def test_hidden_codepoint_predicate(self):
        for cp in (0, 9, 10, 13, 0x1F, 0x7F, 0x85, 0xAD, 0x200B, 0x3000, 0xE0100):
            with self.subTest(cp=hex(cp)):
                self.assertTrue(_escape_source_character(chr(cp)))
        self.assertFalse(_escape_source_character(" "))
        self.assertFalse(_escape_source_character("é"))

    def test_no_nonprinting_raw_codepoints_in_sample(self):
        source = "".join(chr(i) for i in range(0x2100))
        rendered = visible_source_text(source)
        for char in rendered:
            self.assertNotIn(unicodedata.category(char),
                             {"Cc", "Cf", "Cs", "Co", "Cn", "Zl", "Zp"})

    def test_review_queue_cell_rendering_without_source_mutation(self):
        case = SimpleNamespace(case_id="hash-bound", report_row=12,
                               source_key="PO\u202e-1", flags="review\u200b_needed")
        self.assertEqual(visible_review_row(case, "pending"),
                         (12, r"PO\u202E-1", r"review\u200B_needed", "pending"))
        self.assertEqual(case.case_id, "hash-bound")
        self.assertEqual(case.source_key, "PO\u202e-1")
        self.assertEqual(case.flags, "review\u200b_needed")

    def test_review_state_labels_unchanged(self):
        case = SimpleNamespace(report_row=5, source_key="CLM-2", flags="variance")
        for state in ("pending", "reviewed", "escalated", "needs_evidence"):
            with self.subTest(state=state):
                self.assertEqual(visible_review_row(case, state),
                                 (5, "CLM-2", "variance", state))

    def test_raw_source_remains_unchanged(self):
        source = "Private\u202E\\Ref"
        original = source.encode("utf-8")
        self.assertNotEqual(visible_source_text(source), source)
        self.assertEqual(source.encode("utf-8"), original)


if __name__ == "__main__":
    unittest.main()
