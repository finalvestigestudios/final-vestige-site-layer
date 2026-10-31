"""R82 pure-source regressions: visually blank financial reference glyphs.

All identifiers are synthetic; these do not certify a Windows executable.
"""
from __future__ import annotations

import unittest
import unicodedata
from types import SimpleNamespace

from fvs_suite.audit_display import (
    _escape_source_character, visible_review_row, visible_source_text,
)
from fvs_suite.unicode_hazards import (
    VISUALLY_BLANK_FILLERS, is_visually_blank_filler,
)


class PremiumBlankSourceDisplayR82(unittest.TestCase):
    def test_all_seven_blank_glyphs_are_enumerated(self):
        self.assertEqual(VISUALLY_BLANK_FILLERS,
                         frozenset((0x115F, 0x1160, 0x17B4, 0x17B5,
                                    0x2800, 0x3164, 0xFFA0)))

    def test_non_control_categories_reproduce_old_gap(self):
        expected = {0x115F: "Lo", 0x1160: "Lo", 0x17B4: "Mn",
                    0x17B5: "Mn", 0x2800: "So", 0x3164: "Lo", 0xFFA0: "Lo"}
        for point, category in expected.items():
            with self.subTest(point=hex(point)):
                self.assertEqual(unicodedata.category(chr(point)), category)

    def test_each_filler_is_rendered_as_explicit_ascii_escape(self):
        for point in sorted(VISUALLY_BLANK_FILLERS):
            with self.subTest(point=hex(point)):
                self.assertTrue(is_visually_blank_filler(chr(point)))
                self.assertTrue(_escape_source_character(chr(point)))
                self.assertEqual(visible_source_text("PO" + chr(point) + "7"),
                                 f"PO\\u{point:04X}7")

    def test_real_filler_and_literal_escape_are_distinct(self):
        for point in sorted(VISUALLY_BLANK_FILLERS):
            with self.subTest(point=hex(point)):
                raw_escape = f"\\u{point:04X}"
                self.assertEqual(visible_source_text(raw_escape), "\\" + raw_escape)
                self.assertEqual(visible_source_text(chr(point)), raw_escape)

    def test_mixed_hangul_braille_khmer_identifier(self):
        source = "CLM\u3164\u2800\u17b4/8"
        self.assertEqual(visible_source_text(source), r"CLM\u3164\u2800\u17B4/8")

    def test_two_premium_review_row_display_cells(self):
        case = SimpleNamespace(report_row=19, case_id="synthetic-hash",
                               source_key="PO\u115f-88", flags="needs\u2800review")
        self.assertEqual(visible_review_row(case, "pending"),
                         (19, r"PO\u115F-88", r"needs\u2800review", "pending"))
        self.assertEqual(case.source_key, "PO\u115f-88")
        self.assertEqual(case.flags, "needs\u2800review")

    def test_valid_multilingual_source_remains_readable(self):
        for source in ("José", "東京-資金", "مراجعة", "किराया", "e\u0301vidence", "王 小明"):
            with self.subTest(source=source):
                self.assertEqual(visible_source_text(source), source)

    def test_normal_ascii_space_and_printable_braille_untouched(self):
        for source in ("PO 12", "abc def", "PO\u2801-7", "HS-42"):
            with self.subTest(source=source):
                self.assertEqual(visible_source_text(source), source)
        self.assertFalse(is_visually_blank_filler(" "))
        self.assertFalse(is_visually_blank_filler("\u2801"))

    def test_existing_bidi_nbsp_control_behavior_unchanged(self):
        self.assertEqual(visible_source_text("A\u202e\u00a0\tB"),
                         r"A\u202E\u00A0\u0009B")

    def test_supplementary_selectors_behavior_unchanged(self):
        self.assertEqual(visible_source_text("A\U000E0100B"), r"A\U000E0100B")

    def test_literal_backslash_distinction_in_mixed_case(self):
        self.assertEqual(visible_source_text("A\\u2800\u2800"), r"A\\u2800\u2800")

    def test_determinism_for_repeated_review_rendering(self):
        raw = "PO\u3164\u2800\\u3164/2"
        rendered = visible_source_text(raw)
        self.assertEqual(rendered, r"PO\u3164\u2800\\u3164/2")
        self.assertTrue(all(visible_source_text(raw) == rendered for _ in range(30)))

    def test_invalid_nontext_source_has_no_raw_echo(self):
        for source in (None, 7, b"confidential", ["confidential"]):
            with self.subTest(kind=type(source).__name__):
                with self.assertRaisesRegex(TypeError, "requires text") as ctx:
                    visible_source_text(source)
                self.assertNotIn("confidential", str(ctx.exception))

    def test_emitted_escape_is_plain_ascii(self):
        display = visible_source_text("".join(chr(p) for p in sorted(VISUALLY_BLANK_FILLERS)))
        self.assertTrue(display.isascii())
        self.assertNotIn("\u2800", display)

    def test_no_files_or_network_io_required_for_rendering(self):
        self.assertEqual(visible_source_text("CASE\uFFA0"), r"CASE\uFFA0")


if __name__ == "__main__":
    unittest.main()
