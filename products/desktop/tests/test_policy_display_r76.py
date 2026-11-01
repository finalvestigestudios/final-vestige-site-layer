"""R76 Policy Delta Desk: reversible, control-safe display of text differences.

Real policy snapshots and atomic reports, synthetic local input only. A policy
text comparison is not a legal interpretation or compliance determination.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from fvs_suite import policy_diff as pd


class PolicyDisplayR76Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.before = self.folder / "before.txt"
        self.after = self.folder / "after.txt"
        self.output = self.folder / "policy-delta-r76.txt"

    def compare(self, old: bytes, new: bytes) -> str:
        self.before.write_bytes(old)
        self.after.write_bytes(new)
        def outpath(folder, stem, suffix):
            self.assertEqual((Path(folder), stem, suffix),
                             (self.folder, "policy-delta", ".txt"))
            return self.output
        self.assertEqual(pd.compare_policy_files(
            self.before, self.after, self.folder, outpath), [self.output])
        return self.output.read_bytes().decode("utf-8")

    def test_lf_only_diff_remains_standard_unified_format(self):
        report = self.compare(b"alpha\n", b"beta\n")
        self.assertIn("@@ -1 +1 @@\n-alpha\n+beta\n", report)

    def test_crlf_only_change_shows_explicit_carriage_return(self):
        report = self.compare(b"same\r\n", b"same\n")
        self.assertIn("-same\\r\n+same\n", report)
        self.assertNotIn("\r", report)

    def test_cr_only_source_line_is_delimited(self):
        report = self.compare(b"old\r", b"new\n")
        self.assertIn("-old\\r\n+new\n", report)
        self.assertNotIn("No newline at end of file", report)

    def test_cr_only_in_both_inputs_remains_unambiguous(self):
        report = self.compare(b"old\r", b"new\r")
        self.assertIn("-old\\r\n+new\\r\n", report)
        self.assertNotIn("\r", report)

    def test_old_lone_cr_to_unterminated_new_line(self):
        report = self.compare(b"old\r", b"new")
        self.assertIn("-old\\r\n+new\n\\ No newline at end of file\n", report)

    def test_unterminated_old_line_to_crlf_after(self):
        report = self.compare(b"old", b"new\r\n")
        self.assertIn("-old\n\\ No newline at end of file\n+new\\r\n", report)

    def test_crlf_context_line_is_escaped_without_moving_hunk(self):
        report = self.compare(b"context\r\nold\n", b"context\r\nnew\n")
        self.assertIn(" context\\r\n-old\n+new\n", report)
        self.assertIn("@@ -1,2 +1,2 @@", report)

    def test_literal_backslash_r_is_not_aliased_to_actual_cr(self):
        report = self.compare(b"value\\r\n", b"value\r\n")
        self.assertIn("-value\\\\r\n+value\\r\n", report)
        self.assertNotIn("\r", report)

    def test_literal_tab_marker_is_not_aliased_to_tab(self):
        report = self.compare(b"value\\t\n", b"value\t\n")
        self.assertIn("-value\\\\t\n+value\\t\n", report)
        self.assertNotIn("\t", report)

    def test_tab_indent_in_changed_source_line_is_escaped(self):
        report = self.compare(b"\told\n", b"\tnew\n")
        self.assertIn("-\\told\n+\\tnew\n", report)

    def test_tab_context_line_is_escaped(self):
        report = self.compare(b"\tcontext\nold\n", b"\tcontext\nnew\n")
        self.assertIn(" \\tcontext\n", report)
        self.assertNotIn("\t", report)

    def test_backslash_path_in_source_is_visible_and_distinct(self):
        report = self.compare(b"C:\\old\n", b"C:\\new\n")
        self.assertIn("-C:\\\\old\n+C:\\\\new\n", report)

    def test_multiple_backslashes_are_not_collapsed(self):
        report = self.compare(b"a\\\\b\n", b"a\\b\n")
        self.assertIn("-a\\\\\\\\b\n+a\\\\b\n", report)

    def test_source_sha_covers_original_crlf_and_tab_bytes(self):
        old, new = b"name\told\r\n", b"name\tnew\n"
        report = self.compare(old, new)
        self.assertIn(hashlib.sha256(old).hexdigest(), report)
        self.assertIn(hashlib.sha256(new).hexdigest(), report)
        self.assertEqual(self.before.read_bytes(), old)
        self.assertEqual(self.after.read_bytes(), new)

    def test_output_declares_display_notation(self):
        report = self.compare(b"old\r\n", b"new\n")
        self.assertIn("Diff display escapes source backslash as \\\\, tab as \\t and CR as \\r.", report)

    def test_header_filename_escape_remains_separate_from_source_encoding(self):
        # Windows treats a backslash as a directory separator; it cannot be
        # part of a filename. Exercise the real diff rendering directly there
        # without inventing an invalid on-disk Windows path.
        if os.name == "nt":
            rendered = pd._unified_diff(
                ["x\\r\\n"], ["y\\r\\n"],
                json.dumps("A\\\\r.txt", ensure_ascii=True),
                json.dumps("after.txt", ensure_ascii=True))
            self.assertIn('before "A\\\\\\\\r.txt"', rendered)
            self.assertNotIn("\\r", rendered)
        else:
            self.before = self.folder / "A\\\\r.txt"
            report = self.compare(b"x\\r\\n", b"y\\r\\n")
            self.assertIn('before "A\\\\\\\\r.txt"', report)
            self.assertNotIn("\\r", report)

    def test_hunk_headers_remain_unchanged_for_multiple_hunks(self):
        before = [f"row {i}\n" for i in range(20)]
        after = before.copy()
        after[0] = "changed first\n"
        after[19] = "changed last\n"
        report = self.compare("".join(before).encode(), "".join(after).encode())
        self.assertEqual(report.count("@@ -"), 2)
        self.assertIn("-row 0", report)
        self.assertIn("-row 19", report)

    def test_no_difference_still_uses_identical_bytes_review(self):
        report = self.compare(b"same\r\n", b"same\r\n")
        self.assertIn("Both source files have identical bytes", report)
        self.assertIn("No textual differences found.", report)
        self.assertNotIn("\r", report)

    def test_bom_only_difference_still_requests_review(self):
        report = self.compare(b"same\n", b"\xef\xbb\xbfsame\n")
        self.assertIn("Source bytes differ but decoded text is identical", report)

    def test_lf_vs_crlf_is_not_reported_as_identical_text(self):
        report = self.compare(b"same\r\n", b"same\n")
        self.assertNotIn("No textual differences found.", report)
        self.assertNotIn("Source bytes differ but decoded text is identical", report)

    def test_disallowed_control_still_rejected_without_report(self):
        self.before.write_bytes(b"safe\n")
        self.after.write_bytes(b"bad\x1b[31m\n")
        with self.assertRaisesRegex(ValueError, "control"):
            pd.compare_policy_files(self.before, self.after, self.folder,
                                    lambda *_: self.output)
        self.assertFalse(self.output.exists())

    def test_existing_report_is_not_replaced(self):
        self.output.write_text("prior evidence", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.compare(b"a\r\n", b"b\n")
        self.assertEqual(self.output.read_text(), "prior evidence")

    def test_report_has_no_partial_artifacts(self):
        self.compare(b"a\r\n", b"b\n")
        self.assertEqual(list(self.folder.glob("*.partial")), [])

    def test_large_but_bounded_synthetic_diff(self):
        old = (b"a\\b\r\n" * 1_000) + b"old\n"
        new = (b"a\\b\r\n" * 1_000) + b"new\n"
        report = self.compare(old, new)
        self.assertIn("-old", report)
        self.assertIn("+new", report)
        self.assertNotIn("\r", report)


if __name__ == "__main__":
    unittest.main()
