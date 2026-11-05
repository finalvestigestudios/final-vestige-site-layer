"""R197 real-file Policy Delta acceptance matrix (synthetic fixtures only).

Exercises the production file reader, atomic report publication, and source
citation pipeline. No network, financial records, or automated legal decisions.
Run from repo root with PYTHONPATH=products/desktop.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import policy_diff


class PolicyRealFileMatrixR197(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="fv-policy-real-r197-")
        self.addCleanup(directory.cleanup)
        self.folder = Path(directory.name)
        self.old = self.folder / "old.txt"
        self.new = self.folder / "new.txt"
        self.report = self.folder / "review.txt"

    def compare(self, before: bytes, after: bytes, *, old_ext="txt", new_ext="txt") -> str:
        self.old = self.folder / f"old.{old_ext}"
        self.new = self.folder / f"new.{new_ext}"
        self.old.write_bytes(before)
        self.new.write_bytes(after)
        original_old, original_new = self.old.read_bytes(), self.new.read_bytes()
        result = policy_diff.compare_policy_files(
            self.old, self.new, self.folder, lambda *_: self.report)
        self.assertEqual(result, [self.report])
        text = self.report.read_text(encoding="utf-8")
        self.assertIn(hashlib.sha256(before).hexdigest(), text)
        self.assertIn(hashlib.sha256(after).hexdigest(), text)
        self.assertEqual(self.old.read_bytes(), original_old)
        self.assertEqual(self.new.read_bytes(), original_new)
        self.assertFalse(any(self.folder.glob("*.partial")))
        self.assertFalse(any(self.folder.glob(".*.partial")))
        return text

    def rejected(self, before: bytes, after: bytes, *, expression: str) -> None:
        self.old.write_bytes(before)
        self.new.write_bytes(after)
        with self.assertRaisesRegex(ValueError, expression) as caught:
            policy_diff.compare_policy_files(
                self.old, self.new, self.folder, lambda *_: self.report)
        self.assertNotIn("private-tenant-82917", str(caught.exception))
        self.assertFalse(self.report.exists())
        self.assertFalse(any(self.folder.glob(".*.partial")))

    def test_changed_original_sha_and_exact_line_index(self):
        body = self.compare(b"Header\nAmount 10\n", b"Header\nAmount 20\n")
        self.assertIn("Hunk 001: before L2; after L2; -1 +1", body)
        self.assertIn("-Amount 10", body)
        self.assertIn("+Amount 20", body)
        self.assertIn("Not legal advice", body)

    def test_mixed_md_csv_extensions_are_source_cited(self):
        body = self.compare(b"# Heading\nvalue,old\n", b"# Heading\nvalue,new\n",
                            old_ext="md", new_ext="csv")
        self.assertIn('--- before "old.md"', body)
        self.assertIn('+++ after "new.csv"', body)
        self.assertIn("before L2; after L2", body)

    def test_bom_only_change_preserves_two_raw_hashes(self):
        body = self.compare(b"Policy\n", b"\xef\xbb\xbfPolicy\n")
        self.assertIn("Source bytes differ but decoded text is identical", body)
        self.assertIn("No textual differences found.", body)

    def test_crlf_to_lf_exact_bytes_not_silently_normalized(self):
        body = self.compare(b"Clause A\r\n", b"Clause A\n")
        self.assertIn("\\r", body)
        self.assertIn("Hunk 001: before L1; after L1", body)

    def test_unterminated_last_line_is_distinct(self):
        body = self.compare(b"same\n", b"same")
        self.assertIn("\\ No newline at end of file", body)
        self.assertIn("Hunk 001: before L1; after L1", body)

    def test_two_distant_hunks_have_real_file_coordinates(self):
        before = ("A\n" + "unchanged\n" * 10 + "B\n").encode()
        after = ("А\n" + "unchanged\n" * 10 + "Β\n").encode()
        body = self.compare(before, after)
        self.assertIn("Look-alike hunk 001: before L1; after L1", body)
        self.assertIn("Look-alike hunk 002: before L12; after L12", body)
        self.assertLess(body.index("before L1; after L1"), body.index("before L12; after L12"))

    def test_mixed_revision_preserves_confusable_and_substantive_hunks(self):
        body = self.compare("PAYMENT\nOwner Old\n".encode(),
                            "PАYMENT\nOwner New\n".encode())
        self.assertIn("Look-alike hunk 001: before L1; after L1", body)
        self.assertIn("CYRILLIC CAPITAL LETTER A", body)
        self.assertIn("+Owner New", body)
        self.assertIn("human review", body)

    def test_ambiguous_lookalikes_stay_unpaired(self):
        body = self.compare(b"PAY\nPAY\n", "PАY\nPАY\n".encode())
        self.assertNotIn("Look-alike hunk", body)
        self.assertIn("Hunk 001", body)

    def test_canonical_accent_change_cited_and_escaped(self):
        body = self.compare("Cafe\u0301\n".encode(), "Café\n".encode())
        self.assertIn("Canonical hunk 001: before L1; after L1", body)
        self.assertIn("\\u0301", body)
        self.assertIn("NFC-only", body)

    def test_nfkc_compatibility_is_not_declared_legal_equivalence(self):
        body = self.compare("Grant ①\n".encode(), b"Grant 1\n")
        self.assertIn("NFKC-compatibility-equivalent ONLY", body)
        self.assertIn("NOT legal or semantic", body)
        self.assertIn("before L1; after L1", body)

    def test_false_positive_ordinary_edit_has_no_unicode_review_marker(self):
        body = self.compare(b"Limit 12\n", b"Limit 13\n")
        self.assertNotIn("Look-alike hunk", body)
        self.assertNotIn("NFKC-only candidate", body)
        self.assertNotIn("Canonical hunk", body)

    def test_reject_bad_utf8_without_echo_or_report(self):
        self.rejected(b"safe\n", b"private-tenant-82917\xff\n", expression="valid UTF-8")

    def test_reject_bidi_and_escape_without_report(self):
        for payload in ("private-tenant-82917\u202e\n".encode(),
                        b"private-tenant-82917\x1b[31m\n"):
            with self.subTest(payload=payload):
                self.rejected(b"safe\n", payload, expression="control")

    def test_reject_nul_and_embedded_bom(self):
        for payload, expression in ((b"private-tenant-82917\x00\n", "NUL"),
                                    ("private-tenant-82917\ufeff\n".encode(), "control")):
            with self.subTest(expression=expression):
                self.rejected(b"safe\n", payload, expression=expression)

    def test_limit_second_input_fails_without_partial_artifact(self):
        with patch.object(policy_diff, "MAX_POLICY_BYTES", 16):
            self.rejected(b"valid\n", b"private-tenant-82917" * 2,
                          expression="10 MiB")

    def test_exact_line_limit_allowed(self):
        with patch.object(policy_diff, "MAX_POLICY_LINES", 3):
            body = self.compare(b"one\ntwo\nthree\n", b"one\ntwo\nchanged\n")
        self.assertIn("Hunk 001: before L3; after L3", body)

    def test_line_overflow_rejected_without_report(self):
        with patch.object(policy_diff, "MAX_POLICY_LINES", 3):
            self.rejected(b"one\ntwo\nthree\nfour\n", b"short\n",
                          expression="50,000")

    def test_source_symlink_cannot_be_published(self):
        target = self.folder / "real.txt"
        target.write_bytes(b"private-tenant-82917\n")
        self.new.write_bytes(b"safe\n")
        try:
            self.old.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest("symlinks unavailable: " + type(exc).__name__)
        with self.assertRaisesRegex(ValueError, "stable regular file"):
            policy_diff.compare_policy_files(
                self.old, self.new, self.folder, lambda *_: self.report)
        self.assertFalse(self.report.exists())
        self.assertEqual(target.read_bytes(), b"private-tenant-82917\n")

    def test_atomic_publish_exception_leaves_no_half_report(self):
        import os
        from fvs_suite import atomic_text
        self.old.write_bytes(b"original\n")
        self.new.write_bytes(b"revised\n")
        publish_primitive = "rename" if os.name == "nt" else "link"
        with patch.object(atomic_text.os, publish_primitive,
                          side_effect=OSError("synthetic filesystem failure")):
            with self.assertRaises(OSError):
                policy_diff.compare_policy_files(
                    self.old, self.new, self.folder, lambda *_: self.report)
        self.assertFalse(self.report.exists())
        self.assertFalse(any(self.folder.glob(".*.partial")))
        self.assertEqual(self.old.read_bytes(), b"original\n")
        self.assertEqual(self.new.read_bytes(), b"revised\n")

    def test_literal_backslash_cannot_impersonate_invisible_escape(self):
        body = self.compare(b"item \\u200b\n", "item \u200b\n".encode())
        self.assertIn("-item \\\\u200b", body)
        self.assertIn("+item \\u200b", body)

    def test_existing_report_is_never_overwritten(self):
        self.old.write_bytes(b"a\n")
        self.new.write_bytes(b"b\n")
        self.report.write_bytes(b"operator-signed historical evidence\n")
        with self.assertRaises(FileExistsError):
            policy_diff.compare_policy_files(
                self.old, self.new, self.folder, lambda *_: self.report)
        self.assertEqual(self.report.read_bytes(), b"operator-signed historical evidence\n")
        self.assertFalse(any(self.folder.glob(".*.partial")))


if __name__ == "__main__":
    unittest.main()
