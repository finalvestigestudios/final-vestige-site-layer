"""R402: Policy Delta Desk displays source-exact Unicode Mc spacing marks.

Only synthetic policy sources are created. All changes remain textual review
cues, not legal interpretation or automated compliance decisions.
"""
from __future__ import annotations

import hashlib
import tempfile
import unicodedata
import unittest
from pathlib import Path

from fvs_suite import policy_diff as pd


class PolicySpacingMarkEvidenceR402(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.old = self.directory / "before.txt"
        self.new = self.directory / "after.txt"
        self.report = self.directory / "policy-evidence.txt"

    def compare(self, old: str, new: str) -> str:
        old_bytes, new_bytes = old.encode("utf-8"), new.encode("utf-8")
        self.old.write_bytes(old_bytes)
        self.new.write_bytes(new_bytes)
        result = pd.compare_policy_files(
            self.old, self.new, self.directory,
            lambda folder, stem, suffix: self.report,
        )
        self.assertEqual(result, [self.report])
        self.assertEqual(self.old.read_bytes(), old_bytes)
        self.assertEqual(self.new.read_bytes(), new_bytes)
        output = self.report.read_text(encoding="utf-8")
        self.assertIn(hashlib.sha256(old_bytes).hexdigest(), output)
        self.assertIn(hashlib.sha256(new_bytes).hexdigest(), output)
        return output

    def test_bengali_canonical_spelling_is_visible_in_real_report(self):
        composed, decomposed = "ক\u09cb", "ক\u09c7\u09be"
        self.assertEqual(unicodedata.normalize("NFC", composed),
                         unicodedata.normalize("NFC", decomposed))
        report = self.compare(composed + "\n", decomposed + "\n")
        self.assertIn("-ক\\u09cb\n+ক\\u09c7\\u09be\n", report)
        self.assertIn("NFC-normalization-equivalent", report)
        self.assertIn("before L1; after L1; NFC-only candidate", report)
        self.assertIn("Not legal advice", report)

    def test_odia_canonical_spelling_is_visible(self):
        report = self.compare("କ\u0b4b\n", "କ\u0b47\u0b3e\n")
        self.assertIn("-କ\\u0b4b\n+କ\\u0b47\\u0b3e\n", report)

    def test_tamil_canonical_spelling_is_visible(self):
        report = self.compare("க\u0bcb\n", "க\u0bc7\u0bbe\n")
        self.assertIn("-க\\u0bcb\n+க\\u0bc7\\u0bbe\n", report)

    def test_devanagari_and_myanmar_marks_in_same_line(self):
        report = self.compare("क\u093e က\u102c\n", "क က\n")
        self.assertIn("-क\\u093e က\\u102c\n+क က\n", report)

    def test_all_mc_codepoints_have_explicit_escape(self):
        marks = [chr(cp) for cp in range(0x110000)
                 if unicodedata.category(chr(cp)) == "Mc"]
        self.assertGreater(len(marks), 400)
        for mark in marks:
            with self.subTest(point=ord(mark)):
                codepoint = ord(mark)
                expected = (f"\\u{codepoint:04x}" if codepoint <= 0xFFFF
                            else f"\\U{codepoint:08x}")
                self.assertEqual(pd._visible_source_char(mark), expected)

    def test_combining_three_mark_categories_still_escaped(self):
        marks = "\u0301\u09be\u20dd"
        report = self.compare("A" + marks + "\n", "B\n")
        self.assertIn("-A\\u0301\\u09be\\u20dd\n+B\n", report)
        self.assertFalse(any(unicodedata.category(ch) in ("Mn", "Mc", "Me")
                             for ch in report))

    def test_literal_escape_is_distinct_from_real_mc(self):
        report = self.compare("A\\u09be\n", "A\u09be\n")
        self.assertIn("-A\\\\u09be\n+A\\u09be\n", report)

    def test_context_lines_keep_unicode_evidence(self):
        report = self.compare("Prefix\u09be\nold\n", "Prefix\u09be\nnew\n")
        self.assertIn(" Prefix\\u09be\n-old\n+new\n", report)

    def test_mixed_edit_keeps_physical_hunk_coordinates(self):
        report = self.compare("ক\u09cb\nLimit 10\n", "ক\u09c7\u09be\nLimit 20\n")
        self.assertIn("@@ -1,2 +1,2 @@", report)
        self.assertIn("before L1-L2; after L1-L2", report)
        self.assertIn("Limit 10", report)
        self.assertIn("Limit 20", report)
        self.assertIn("human review", report)
        self.assertNotIn("compliant", report.lower())

    def test_ascii_and_precomposed_text_remain_readable(self):
        self.assertEqual(pd._visible_source_char("é"), "é")
        report = self.compare("café 東京\n", "café 京都\n")
        self.assertIn("-café 東京\n+café 京都\n", report)

    def test_existing_report_is_not_overwritten(self):
        self.report.write_text("PRIOR EVIDENCE", encoding="utf-8")
        self.old.write_text("ক\u09cb\n", encoding="utf-8")
        self.new.write_text("ক\u09c7\u09be\n", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            pd.compare_policy_files(self.old, self.new, self.directory,
                                    lambda *_: self.report)
        self.assertEqual(self.report.read_text(encoding="utf-8"), "PRIOR EVIDENCE")
        self.assertFalse(list(self.directory.glob("*.partial")))

    def test_unsafe_bidi_source_is_rejected_without_output(self):
        self.old.write_bytes(b"safe\n")
        self.new.write_text("deny\u202e approve\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            pd.compare_policy_files(self.old, self.new, self.directory,
                                    lambda *_: self.report)
        self.assertFalse(self.report.exists())

    def test_no_change_remains_human_review(self):
        report = self.compare("क\u093e\n", "क\u093e\n")
        self.assertIn("Both source files have identical bytes", report)
        self.assertIn("No textual differences", report)
        self.assertIn("Not legal advice", report)

    def test_crlf_and_lf_without_mc_regression(self):
        report = self.compare("A\r\n", "B\n")
        self.assertIn("-A\\r\n+B\n", report)

    def test_no_empty_output_or_temp_artifacts(self):
        report = self.compare("ക\u0d3e\n", "ക\n")
        self.assertGreater(len(report), 300)
        self.assertFalse(list(self.directory.glob("*.partial")))


if __name__ == "__main__":
    unittest.main()
