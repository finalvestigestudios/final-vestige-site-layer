"""R78: real local-file integration checks for review-visible Unicode spaces.

All inputs are synthetic. This test does not claim native Windows EXE coverage.
"""
from __future__ import annotations

import hashlib
import tempfile
import unicodedata
import unittest
from pathlib import Path

from fvs_suite import policy_diff


class PolicySpacingReviewR78(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.before = self.folder / "original.txt"
        self.after = self.folder / "revised.txt"
        self.output = self.folder / "diff.txt"

    def compare(self, old: str, new: str) -> str:
        before_bytes = old.encode("utf-8")
        after_bytes = new.encode("utf-8")
        self.before.write_bytes(before_bytes)
        self.after.write_bytes(after_bytes)
        artifacts = policy_diff.compare_policy_files(
            self.before, self.after, self.folder,
            lambda folder, stem, suffix: self.output,
        )
        self.assertEqual(artifacts, [self.output])
        self.assertEqual(self.before.read_bytes(), before_bytes)
        self.assertEqual(self.after.read_bytes(), after_bytes)
        text = self.output.read_text(encoding="utf-8")
        self.assertIn(hashlib.sha256(before_bytes).hexdigest(), text)
        self.assertIn(hashlib.sha256(after_bytes).hexdigest(), text)
        return text

    def test_nobreak_space_different_from_ascii_space(self):
        report = self.compare("Approve\u00a0payment\n", "Approve payment\n")
        self.assertIn("-Approve\\u00a0payment\n+Approve payment\n", report)
        self.assertNotIn("\u00a0", report)

    def test_narrow_nobreak_space(self):
        report = self.compare("per\u202fdiem\n", "per diem\n")
        self.assertIn("-per\\u202fdiem\n+per diem\n", report)

    def test_figure_space(self):
        report = self.compare("Total\u2007120\n", "Total 120\n")
        self.assertIn("-Total\\u2007120\n+Total 120\n", report)

    def test_thin_space(self):
        report = self.compare("Amount\u2009100\n", "Amount 100\n")
        self.assertIn("-Amount\\u2009100\n+Amount 100\n", report)

    def test_ideographic_space(self):
        report = self.compare("承認\u3000必要\n", "承認 必要\n")
        self.assertIn("-承認\\u3000必要\n+承認 必要\n", report)

    def test_ogham_space_mark(self):
        report = self.compare("A\u1680B\n", "A B\n")
        self.assertIn("-A\\u1680B\n+A B\n", report)

    def test_en_quad_and_em_quad(self):
        report = self.compare("A\u2000B\n", "A\u2001B\n")
        self.assertIn("-A\\u2000B\n+A\\u2001B\n", report)

    def test_all_non_ascii_unicode_zs_are_visible(self):
        spaces = [chr(point) for point in range(0x110000)
                  if unicodedata.category(chr(point)) == "Zs" and point != 0x20]
        self.assertGreaterEqual(len(spaces), 15)
        report = self.compare("Approve" + "".join(spaces) + "now\n",
                              "Approve now\n")
        for character in spaces:
            with self.subTest(codepoint=hex(ord(character))):
                self.assertIn(f"\\u{ord(character):04x}", report)
                self.assertNotIn(character, report)

    def test_source_literal_escape_is_unambiguously_distinct(self):
        report = self.compare("Flag\\u00a0\n", "Flag\u00a0\n")
        self.assertIn("-Flag\\\\u00a0\n+Flag\\u00a0\n", report)

    def test_report_context_line_shows_special_space(self):
        report = self.compare("Context\u00a0clause\nOld\n", "Context\u00a0clause\nNew\n")
        self.assertIn(" Context\\u00a0clause\n-Old\n+New\n", report)

    def test_multiple_spaces_and_ascii_spaces_are_distinct(self):
        report = self.compare("Approve \u00a0 now\n", "Approve   now\n")
        self.assertIn("-Approve \\u00a0 now\n+Approve   now\n", report)

    def test_regular_space_remains_readable(self):
        report = self.compare("Reviewed  yesterday\n", "Reviewed yesterday\n")
        self.assertIn("-Reviewed  yesterday\n+Reviewed yesterday\n", report)
        self.assertNotIn("\\u0020", report)

    def test_existing_cr_tab_backslash_protections_remain(self):
        report = self.compare("A\t\\u00a0\r\n", "A\t\u00a0\n")
        self.assertIn("-A\\t\\\\u00a0\\r\n+A\\t\\u00a0\n", report)
        self.assertNotIn("\r", report)
        self.assertNotIn("\t", report)

    def test_unicode_in_both_added_and_removed_lines(self):
        report = self.compare("Clause\u00a0A\n", "Clause\u202fB\n")
        self.assertIn("-Clause\\u00a0A\n+Clause\\u202fB\n", report)

    def test_hunk_coordinates_and_header_labels_remain_intact(self):
        report = self.compare("A\u00a0B\n", "A B\n")
        self.assertIn('--- before "original.txt"\n', report)
        self.assertIn('+++ after "revised.txt"\n', report)
        self.assertIn("@@ -1 +1 @@\n", report)

    def test_preserved_multilingual_letters(self):
        report = self.compare("café 東京\u3000済\n", "café 東京 済\n")
        self.assertIn("-café 東京\\u3000済\n+café 東京 済\n", report)

    def test_identical_sources_still_require_human_review(self):
        report = self.compare("Same\u00a0text\n", "Same\u00a0text\n")
        self.assertIn("Both source files have identical bytes", report)
        self.assertIn("No textual differences found.", report)
        self.assertIn("Not legal advice", report)

    def test_preexisting_report_is_immutable(self):
        self.output.write_text("PREVIOUS SIGNED EVIDENCE", encoding="utf-8")
        self.before.write_text("A\u00a0B\n", encoding="utf-8")
        self.after.write_text("A B\n", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            policy_diff.compare_policy_files(
                self.before, self.after, self.folder,
                lambda folder, stem, suffix: self.output,
            )
        self.assertEqual(self.output.read_text(encoding="utf-8"), "PREVIOUS SIGNED EVIDENCE")
        self.assertFalse(list(self.folder.glob("*.partial")))

    def test_unsafe_bidi_override_does_not_publish(self):
        self.before.write_text("fine\n", encoding="utf-8")
        self.after.write_text("approve\u202e deny\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unsupported control"):
            policy_diff.compare_policy_files(
                self.before, self.after, self.folder,
                lambda folder, stem, suffix: self.output,
            )
        self.assertFalse(self.output.exists())

    def test_invalid_utf8_does_not_publish(self):
        self.before.write_bytes(b"A\n")
        self.after.write_bytes(b"A\xff\n")
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            policy_diff.compare_policy_files(
                self.before, self.after, self.folder,
                lambda folder, stem, suffix: self.output,
            )
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
