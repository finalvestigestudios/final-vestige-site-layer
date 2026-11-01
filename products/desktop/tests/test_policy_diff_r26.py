"""Policy Delta Desk R26: real helper I/O, provenance and fail-closed intake."""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import policy_diff as pd


class PolicyDiffR26Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.old = self.root / "before.txt"
        self.new = self.root / "after.txt"
        self.output = self.root / "policy-delta-r26.txt"

    def write(self, old=b"Rule A\n", new=b"Rule B\n"):
        self.old.write_bytes(old)
        self.new.write_bytes(new)

    def allocator(self, folder, stem, suffix):
        self.assertEqual((Path(folder), stem, suffix), (self.root, "policy-delta", ".txt"))
        return self.output

    def run_diff(self):
        return pd.compare_policy_files(self.old, self.new, self.root, self.allocator)

    def no_output_after_error(self, needle):
        with self.assertRaisesRegex(ValueError, needle):
            self.run_diff()
        self.assertFalse(self.output.exists())

    def test_actual_diff_has_verifiable_raw_sha256_and_source_rows(self):
        self.write()
        self.assertEqual(self.run_diff(), [self.output])
        report = self.output.read_text(encoding="utf-8")
        self.assertIn("-Rule A", report)
        self.assertIn("+Rule B", report)
        self.assertIn("@@ -1 +1 @@", report)
        self.assertIn(hashlib.sha256(b"Rule A\n").hexdigest(), report)
        self.assertIn(hashlib.sha256(b"Rule B\n").hexdigest(), report)
        self.assertIn("lines: 1", report)
        self.assertEqual(self.old.read_bytes(), b"Rule A\n")

    def test_identical_inputs_produce_deterministic_no_change_report(self):
        self.write(b"same\n", b"same\n")
        self.run_diff()
        self.assertIn("No textual differences found.", self.output.read_text())

    def test_utf8_bom_and_unicode_are_supported_and_hashed_exactly(self):
        before = b"\xef\xbb\xbf" + "Café\n".encode("utf-8")
        self.write(before, "Café\n".encode("utf-8"))
        self.run_diff()
        report = self.output.read_text()
        self.assertIn(hashlib.sha256(before).hexdigest(), report)
        self.assertIn("No textual differences found.", report)

    def test_unterminated_final_line_separated_with_explicit_marker(self):
        self.write(b"before", b"after")
        self.run_diff()
        report = self.output.read_text()
        self.assertIn("-before\n\\ No newline at end of file\n+after\n\\ No newline at end of file", report)

    def test_newline_only_change_is_visible(self):
        self.write(b"same\n", b"same")
        self.run_diff()
        report = self.output.read_text()
        self.assertIn("-same\n", report)
        self.assertIn("+same\n\\ No newline at end of file", report)

    def test_reject_nul_in_old_without_artifacts(self):
        self.write(b"Rule\x00 hidden\n", b"good\n")
        self.no_output_after_error("NUL")

    def test_reject_nul_in_new_without_artifacts(self):
        self.write(b"good\n", b"New\x00 hidden\n")
        self.no_output_after_error("NUL")

    def test_invalid_utf8_fails_without_artifacts_and_without_echo(self):
        self.write(b"good\n", b"private\xffvalue\n")
        with self.assertRaisesRegex(ValueError, "valid UTF-8") as caught:
            self.run_diff()
        self.assertNotIn("private", str(caught.exception))
        self.assertFalse(self.output.exists())

    def test_oversized_sparse_input_is_rejected_before_read(self):
        self.write()
        with self.new.open("wb") as stream:
            stream.truncate(pd.MAX_POLICY_BYTES + 1)
        self.no_output_after_error("10 MiB")

    def test_exact_byte_limit_allowed_and_one_over_rejected(self):
        with patch.object(pd, "MAX_POLICY_BYTES", 9):
            self.write(b"123456789", b"123456789")
            self.run_diff()
            self.assertIn("No textual differences", self.output.read_text())
            self.output.unlink()
            self.new.write_bytes(b"1234567890")
            self.no_output_after_error("10 MiB")

    def test_physical_line_limit_rejects_many_short_lines(self):
        with patch.object(pd, "MAX_POLICY_LINES", 2):
            self.write(b"one\ntwo\nthree\n", b"fine\n")
            self.no_output_after_error("50,000")

    def test_reject_terminal_escape_and_bidi_controls(self):
        for unsafe in (b"\x1b[31m", "\u202esneaky".encode(), b"one\x0btwo"):
            with self.subTest(unsafe=unsafe):
                self.write(b"safe\n", unsafe)
                self.no_output_after_error("control")

    def test_reject_embedded_bom_without_artifacts(self):
        self.write(b"safe\n", "a\ufeffb\n".encode("utf-8"))
        self.no_output_after_error("control")

    def test_filename_with_newline_cannot_forge_diff_header(self):
        self.write()
        # Windows forbids LF in filenames. A bidi-control filename is legal
        # and still verifies that source typography cannot forge a header.
        name = "before\u202e+forged.txt" if os.name == "nt" else "before\n+forged.txt"
        self.old.rename(self.root / name)
        self.old = self.root / name
        self.run_diff()
        report = self.output.read_text()
        if os.name == "nt":
            self.assertIn('"before\\u202e+forged.txt"', report)
            self.assertNotIn("\u202e", report)
        else:
            self.assertIn('"before\\n+forged.txt"', report)
            self.assertNotIn("\n+forged.txt", report)

    def test_unsupported_extension_or_missing_input_rejected(self):
        self.write()
        self.new = self.new.rename(self.root / "after.pdf")
        self.no_output_after_error("supports existing TXT")
        self.new = self.root / "missing.txt"
        self.no_output_after_error("supports existing TXT")

    def test_existing_report_is_not_overwritten(self):
        self.write()
        self.output.write_text("existing", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.run_diff()
        self.assertEqual(self.output.read_text(), "existing")

    def test_markdown_and_csv_inputs_supported(self):
        self.old = self.root / "old.md"
        self.new = self.root / "new.csv"
        self.write(b"# Change\n", b"header\n")
        self.run_diff()
        self.assertIn("-# Change", self.output.read_text())


if __name__ == "__main__":
    unittest.main()
