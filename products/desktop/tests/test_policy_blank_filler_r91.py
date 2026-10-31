"""R91: policy-diff visible custody for non-control Unicode blank fillers.

Synthetic local TXT/MD/CSV fixtures only. Real policy_diff, csv_snapshot,
atomic_text, and unicode_hazards source modules are exercised end-to-end.
No legal/compliance approval or Windows executable behavior is asserted.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import policy_diff as pd
from fvs_suite.unicode_hazards import VISUALLY_BLANK_FILLERS


class PolicyBlankFillerR91(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.before = self.folder / "original.txt"
        self.after = self.folder / "revised.txt"
        self.output = self.folder / "diff.txt"

    def compare(self, old: str | bytes, new: str | bytes) -> str:
        old_bytes = old.encode("utf-8") if isinstance(old, str) else old
        new_bytes = new.encode("utf-8") if isinstance(new, str) else new
        self.before.write_bytes(old_bytes)
        self.after.write_bytes(new_bytes)

        def output_path(folder, stem, suffix):
            self.assertEqual((Path(folder), stem, suffix),
                             (self.folder, "policy-delta", ".txt"))
            return self.output

        self.assertEqual(pd.compare_policy_files(
            self.before, self.after, self.folder, output_path), [self.output])
        report = self.output.read_bytes().decode("utf-8")
        self.assertEqual(self.before.read_bytes(), old_bytes)
        self.assertEqual(self.after.read_bytes(), new_bytes)
        self.assertIn(hashlib.sha256(old_bytes).hexdigest(), report)
        self.assertIn(hashlib.sha256(new_bytes).hexdigest(), report)
        return report

    def test_all_seven_filler_codepoints_render_explicitly(self):
        self.assertEqual(len(VISUALLY_BLANK_FILLERS), 7)
        for point in sorted(VISUALLY_BLANK_FILLERS):
            with self.subTest(codepoint=f"U+{point:04X}"):
                self.assertEqual(pd._visible_source_char(chr(point)),
                                 f"\\u{point:04x}")

    def test_blank_filler_cannot_be_mistaken_for_normal_space(self):
        report = self.compare("Approve\u2800payment\n", "Approve payment\n")
        self.assertIn("-Approve\\u2800payment\n+Approve payment\n", report)
        self.assertNotIn("\u2800", report)

    def test_hangul_filler_cannot_be_mistaken_for_missing_character(self):
        report = self.compare("Clause\u115fX\n", "ClauseX\n")
        self.assertIn("-Clause\\u115fX\n+ClauseX\n", report)
        self.assertNotIn("\u115f", report)

    def test_all_seven_filler_glyphs_escape_in_real_report(self):
        raw = "Clause" + "".join(chr(point) for point in sorted(VISUALLY_BLANK_FILLERS))
        report = self.compare(raw + "\n", "Clause\n")
        for point in VISUALLY_BLANK_FILLERS:
            with self.subTest(codepoint=point):
                self.assertIn(f"\\u{point:04x}", report)
                self.assertNotIn(chr(point), report)

    def test_actual_filler_differs_from_literal_escape_text(self):
        report = self.compare("A\\u2800B\n", "A\u2800B\n")
        self.assertIn("-A\\\\u2800B\n+A\\u2800B\n", report)
        self.assertNotIn("\u2800", report)

    def test_each_source_line_type_is_escaped(self):
        report = self.compare("Context\u3164\nOld\u2800\n", "Context\u3164\nNew\u115f\n")
        self.assertIn(" Context\\u3164\n-Old\\u2800\n+New\\u115f\n", report)

    def test_diff_hunk_line_numbers_are_unchanged(self):
        old = [f"Row {i}\n" for i in range(40)]
        new = old.copy()
        old[0] = "First\u17b4\n"
        new[0] = "First\n"
        old[-1] = "Last\u17b5\n"
        new[-1] = "Last\n"
        report = self.compare("".join(old), "".join(new))
        self.assertEqual(report.count("@@ -"), 2)
        self.assertIn('--- before "original.txt"\n', report)
        self.assertIn('+++ after "revised.txt"\n', report)

    def test_unterminated_source_line_keeps_missing_newline_marker(self):
        report = self.compare("Old\u2800", "New\n")
        self.assertIn("-Old\\u2800\n\\ No newline at end of file\n+New\n", report)

    def test_all_markdown_csv_txt_extensions_are_supported(self):
        for suffix in (".txt", ".md", ".csv"):
            with self.subTest(ext=suffix):
                self.before = self.folder / ("original" + suffix)
                self.after = self.folder / ("revised" + suffix)
                self.output = self.folder / ("diff" + suffix + ".txt")
                report = self.compare("Key\u2800changed\n", "Key changed\n")
                self.assertIn("-Key\\u2800changed\n+Key changed\n", report)

    def test_source_bytes_and_hashes_unchanged(self):
        report = self.compare("α\u1160β\n", "αβ\n")
        self.assertIn("-α\\u1160β\n+αβ\n", report)
        self.assertIn("SHA-256 fingerprints cover the exact source bytes", report)

    def test_normal_multilingual_text_not_escaped(self):
        report = self.compare("café 東京\n", "café 京都\n")
        self.assertIn("-café 東京\n+café 京都\n", report)

    def test_ordinary_space_keeps_source_appearance(self):
        report = self.compare("A  B\n", "A B\n")
        self.assertIn("-A  B\n+A B\n", report)
        self.assertNotIn("\\u0020", report)

    def test_CR_tab_backslash_preserve_prior_escaping_contract(self):
        report = self.compare("A\t\\u2800\r\n", "A\t\u2800\n")
        self.assertIn("-A\\t\\\\u2800\\r\n+A\\t\\u2800\n", report)
        self.assertNotIn("\r", report)
        self.assertNotIn("\t", report)

    def test_report_describes_the_new_display_convention(self):
        report = self.compare("A\u2800\n", "A\n")
        self.assertIn("Unicode blank filler", report)
        self.assertIn("Not legal advice or a compliance determination", report)

    def test_identical_source_files_remain_human_review(self):
        report = self.compare("Unchanged\u2800\n", "Unchanged\u2800\n")
        self.assertIn("Both source files have identical bytes", report)
        self.assertIn("No textual differences found", report)

    def test_bom_only_change_keeps_review_signal(self):
        report = self.compare(b"Identical\n", b"\xef\xbb\xbfIdentical\n")
        self.assertIn("Source bytes differ but decoded text is identical", report)

    def test_control_code_rejected_without_a_report(self):
        self.before.write_bytes(b"Safe\n")
        self.after.write_bytes(b"Unsafe\x1b[31m\n")
        with self.assertRaisesRegex(ValueError, "unsupported control"):
            pd.compare_policy_files(self.before, self.after, self.folder,
                                    lambda *_: self.output)
        self.assertFalse(self.output.exists())

    def test_invalid_utf8_rejected_without_a_report(self):
        self.before.write_bytes(b"Safe\n")
        self.after.write_bytes(b"Unsafe\xff\n")
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            pd.compare_policy_files(self.before, self.after, self.folder,
                                    lambda *_: self.output)
        self.assertFalse(self.output.exists())

    def test_preexisting_report_not_overwritten(self):
        self.output.write_text("PRIOR EVIDENCE", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.compare("Old\u2800\n", "New\n")
        self.assertEqual(self.output.read_text(encoding="utf-8"), "PRIOR EVIDENCE")
        self.assertFalse(list(self.folder.glob("*.partial")))

    def test_success_cleans_up_staged_partial_files(self):
        self.compare("Old\u2800\n", "New\n")
        self.assertFalse(list(self.folder.glob("*.partial")))

    def test_many_unchanged_context_lines_keep_filler_visible(self):
        report = self.compare("Context\u2800\n" * 1200 + "old\n",
                              "Context\u2800\n" * 1200 + "new\n")
        self.assertIn(" Context\\u2800\n-old\n+new\n", report)
        self.assertNotIn("\u2800", report)

    def test_reports_are_byte_deterministic_for_same_sources(self):
        first = self.compare("Old\u2800\n", "New\n")
        self.output.unlink()
        second = self.compare("Old\u2800\n", "New\n")
        self.assertEqual(first.encode("utf-8"), second.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
