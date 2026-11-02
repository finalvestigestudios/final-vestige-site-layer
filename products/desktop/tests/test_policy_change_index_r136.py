"""R136: genuine offline Policy Delta reports with exact physical-line change index.

Synthetic fixtures only. Index is navigation, not a legal/compliance judgment.
No network, no premium files, no destructive write to source documents.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine, policy_diff


class PolicyChangeIndexR136(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.before = self.root / "before.txt"
        self.after = self.root / "after.txt"
        self.result = self.root / "policy-change-r136.txt"

    def compare(self, old: str | bytes, new: str | bytes) -> str:
        old_bytes = old.encode("utf-8") if isinstance(old, str) else old
        new_bytes = new.encode("utf-8") if isinstance(new, str) else new
        self.before.write_bytes(old_bytes)
        self.after.write_bytes(new_bytes)

        def allocate(folder, stem, suffix):
            self.assertEqual((Path(folder), stem, suffix),
                             (self.root, "policy-delta", ".txt"))
            return self.result

        self.assertEqual(
            policy_diff.compare_policy_files(
                self.before, self.after, self.root, allocate),
            [self.result],
        )
        text = self.result.read_text(encoding="utf-8")
        self.assertEqual(self.before.read_bytes(), old_bytes)
        self.assertEqual(self.after.read_bytes(), new_bytes)
        return text

    def test_one_line_replacement_has_exact_before_after_citations(self):
        report = self.compare("old\n", "new\n")
        self.assertIn("Change index: 1 diff hunk(s); 1 removed source line(s); 1 added source line(s).", report)
        self.assertIn("Hunk 001: before L1; after L1; -1 +1; mixed removal/addition; human review.", report)
        self.assertIn("@@ -1 +1 @@\n-old\n+new\n", report)

    def test_insertion_at_start_has_no_changed_before_line(self):
        report = self.compare("original\n", "new\noriginal\n")
        self.assertIn("Hunk 001: before none; after L1; -0 +1; addition only", report)

    def test_insertion_at_end_cites_last_new_line(self):
        report = self.compare("A\nB\n", "A\nB\nC\n")
        self.assertIn("Hunk 001: before none; after L3; -0 +1; addition only", report)

    def test_deletion_at_start_has_no_changed_after_line(self):
        report = self.compare("deleted\nkept\n", "kept\n")
        self.assertIn("Hunk 001: before L1; after none; -1 +0; removal only", report)

    def test_deletion_at_end_cites_last_old_line(self):
        report = self.compare("A\nB\n", "A\n")
        self.assertIn("Hunk 001: before L2; after none; -1 +0; removal only", report)

    def test_mixed_one_for_two_preserves_independent_ranges(self):
        report = self.compare("head\nold\nfoot\n", "head\nnew 1\nnew 2\nfoot\n")
        self.assertIn("Hunk 001: before L2; after L2-L3; -1 +2; mixed removal/addition", report)

    def test_distant_edits_are_two_numbered_hunks(self):
        before = [f"Line {i}\n" for i in range(1, 41)]
        after = before.copy()
        after[0] = "Changed 1\n"
        after[-1] = "Changed 40\n"
        report = self.compare("".join(before), "".join(after))
        self.assertIn("Change index: 2 diff hunk(s); 2 removed source line(s); 2 added source line(s).", report)
        self.assertIn("Hunk 001: before L1; after L1; -1 +1", report)
        self.assertIn("Hunk 002: before L40; after L40; -1 +1", report)
        self.assertEqual(report.count("@@ -"), 2)

    def test_close_edits_group_without_inflating_change_counts(self):
        report = self.compare("keep\nold one\ncontext\nold two\nend\n",
                              "keep\nnew one\ncontext\nnew two\nend\n")
        self.assertIn("Change index: 1 diff hunk(s); 2 removed source line(s); 2 added source line(s).", report)
        self.assertIn("Hunk 001: before L2-L4; after L2-L4; -2 +2", report)
        self.assertIn("A touched range can contain unchanged lines", report)

    def test_context_lines_are_not_counted_as_changes(self):
        report = self.compare("A\nB\nC\nD\nE\n", "A\nB\nchanged\nD\nE\n")
        self.assertIn("1 removed source line(s); 1 added source line(s).", report)
        self.assertIn("Hunk 001: before L3; after L3; -1 +1", report)

    def test_completely_empty_before_source_indexes_addition(self):
        report = self.compare(b"", b"first\nsecond\n")
        self.assertIn("Hunk 001: before none; after L1-L2; -0 +2; addition only", report)

    def test_identical_bytes_produce_zero_index_and_review_note(self):
        report = self.compare("same\n", "same\n")
        self.assertIn("Change index: 0 diff hunk(s); 0 removed source line(s); 0 added source line(s).", report)
        self.assertIn("No changed source lines to index.", report)
        self.assertIn("Both source files have identical bytes", report)
        self.assertIn("No textual differences found.", report)

    def test_utf8_bom_only_difference_indexes_zero_changes(self):
        report = self.compare(b"same\n", b"\xef\xbb\xbfsame\n")
        self.assertIn("Change index: 0 diff hunk(s)", report)
        self.assertIn("Source bytes differ but decoded text is identical", report)

    def test_crlf_only_change_is_indexed_and_cr_escaped(self):
        report = self.compare(b"same\r\n", b"same\n")
        self.assertIn("Hunk 001: before L1; after L1; -1 +1", report)
        self.assertIn("-same\\r\n+same\n", report)
        self.assertNotIn("\r", report)

    def test_unterminated_last_lines_keep_index_and_eof_markers(self):
        report = self.compare(b"old", b"new")
        self.assertIn("Hunk 001: before L1; after L1; -1 +1", report)
        self.assertIn("-old\n\\ No newline at end of file\n+new\n\\ No newline at end of file", report)

    def test_unicode_hidden_difference_visible_but_citations_stable(self):
        report = self.compare("approve\u200b now\n", "approve now\n")
        self.assertIn("Hunk 001: before L1; after L1; -1 +1", report)
        self.assertIn("-approve\\u200b now\n+approve now\n", report)
        self.assertNotIn("\u200b", report)

    def test_original_source_sha_and_privacy_are_maintained(self):
        old, new = b"private-customer-OLD\n", b"private-customer-NEW\n"
        report = self.compare(old, new)
        self.assertIn(hashlib.sha256(old).hexdigest(), report)
        self.assertIn(hashlib.sha256(new).hexdigest(), report)
        self.assertNotIn(str(self.root), report)
        self.assertIn("Not legal advice or a compliance determination", report)

    def test_same_inputs_generate_byte_identical_report(self):
        first = self.compare("Original\n", "Revised\n")
        self.result.unlink()
        second = self.compare("Original\n", "Revised\n")
        self.assertEqual(first.encode("utf-8"), second.encode("utf-8"))

    def test_disallowed_control_fails_without_partial_report(self):
        self.before.write_bytes(b"Safe\n")
        self.after.write_bytes("approve\u202e deny\n".encode("utf-8"))
        with self.assertRaisesRegex(ValueError, "unsupported control"):
            policy_diff.compare_policy_files(
                self.before, self.after, self.root, lambda *_: self.result)
        self.assertFalse(self.result.exists())

    def test_existing_report_is_never_overwritten(self):
        self.result.write_text("PRIOR EVIDENCE", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.compare("old\n", "new\n")
        self.assertEqual(self.result.read_text(encoding="utf-8"), "PRIOR EVIDENCE")
        self.assertEqual(list(self.root.glob("*.partial")), [])

    def test_public_engine_entrypoint_produces_indexed_report(self):
        self.before.write_bytes(b"Policy OLD\n")
        self.after.write_bytes(b"Policy NEW\n")
        paths = engine.policy_delta(self.before, self.after, self.root)
        self.assertEqual(len(paths), 1)
        report = paths[0].read_text(encoding="utf-8")
        self.assertIn("Hunk 001: before L1; after L1; -1 +1", report)
        self.assertIn("-Policy OLD\n+Policy NEW\n", report)


if __name__ == "__main__":
    unittest.main()
