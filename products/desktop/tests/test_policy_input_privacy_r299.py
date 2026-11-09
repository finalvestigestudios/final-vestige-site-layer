"""R299: real-path + injected-fault regression for Policy Delta's private intake."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.policy_input_privacy import (
    checked_policy_path, read_policy_snapshot, decode_policy_utf8,
)

ALLOWED = frozenset((".txt", ".md", ".csv"))
SECRET = "secret-contract-client-90831"


class BrokenPath:
    def __init__(self, exc):
        self.exc = exc
    def __fspath__(self):
        raise self.exc


class PolicyPrivateIntakeR299(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.source = self.dir / "before.txt"
        self.source.write_bytes(b"Policy A\n")

    def sanitized(self, operation, phrase):
        with self.assertRaises(ValueError) as seen:
            operation()
        e = seen.exception
        self.assertIn(phrase, str(e))
        self.assertNotIn(SECRET, str(e))
        self.assertIsNone(e.__cause__)
        self.assertIsNone(e.__context__)
        return e

    def test_real_txt_candidate_and_content_unchanged(self):
        self.assertEqual(checked_policy_path(self.source, ALLOWED), self.source)
        self.assertEqual(self.source.read_bytes(), b"Policy A\n")

    def test_supported_uppercase_extension(self):
        upper = self.source.rename(self.dir / "BEFORE.TXT")
        self.assertEqual(checked_policy_path(upper, ALLOWED), upper)

    def test_real_markdown_and_csv_candidates(self):
        for ext in (".md", ".csv"):
            p = self.dir / ("before" + ext)
            p.write_bytes(b"Policy B\n")
            self.assertEqual(checked_policy_path(p, ALLOWED), p)

    def test_missing_file_has_stable_diagnostic(self):
        self.sanitized(lambda: checked_policy_path(self.dir / "missing.txt", ALLOWED), "supports existing")

    def test_directory_is_not_file(self):
        self.sanitized(lambda: checked_policy_path(self.dir, ALLOWED), "supports existing")

    def test_unsupported_suffix_is_rejected(self):
        self.sanitized(lambda: checked_policy_path(self.source.with_suffix(".pdf"), ALLOWED), "supports existing")

    def test_invalid_pathlike_expected_exceptions_are_sanitized(self):
        for exc in (OSError(13, SECRET, SECRET), PermissionError(13, SECRET, SECRET),
                    ValueError(SECRET), TypeError(SECRET)):
            with self.subTest(exc=type(exc).__name__):
                self.sanitized(lambda: checked_policy_path(BrokenPath(exc), ALLOWED), "supports existing")

    def test_probe_filesystem_errors_leave_no_hidden_chain(self):
        for exception in (PermissionError(13, SECRET, SECRET), OSError(5, SECRET, SECRET)):
            with self.subTest(exception=type(exception).__name__):
                with patch.object(Path, "is_file", side_effect=exception):
                    self.sanitized(lambda: checked_policy_path(self.source, ALLOWED), "supports existing")

    def test_interrupts_and_memory_failures_are_not_swallowed_by_path(self):
        for exc in (KeyboardInterrupt(), SystemExit(), MemoryError()):
            with self.subTest(exc=type(exc).__name__):
                with self.assertRaises(type(exc)):
                    checked_policy_path(BrokenPath(exc), ALLOWED)

    def test_valid_snapshot_preserves_exact_bytes_and_arguments(self):
        observed = []
        def reader(path, limit):
            observed.append((path, limit))
            return b"\xef\xbb\xbfHello\n"
        self.assertEqual(read_policy_snapshot(self.source, 87, reader), b"\xef\xbb\xbfHello\n")
        self.assertEqual(observed, [(self.source, 87)])

    def test_known_oversize_sentinel_gets_policy_specific_limit(self):
        def reader(path, limit):
            raise ValueError("CSV input exceeds 64 MiB file-size limit")
        self.sanitized(lambda: read_policy_snapshot(self.source, 50, reader), "10 MiB")

    def test_private_valueerror_does_not_leak(self):
        def reader(path, limit):
            raise ValueError(SECRET)
        self.sanitized(lambda: read_policy_snapshot(self.source, 50, reader), "stable regular file")

    def test_private_valueerror_with_exceeds_is_not_misclassified(self):
        def reader(path, limit):
            raise ValueError(f"{SECRET}/exceeds.txt")
        e = self.sanitized(lambda: read_policy_snapshot(self.source, 50, reader), "stable regular file")
        self.assertNotIn("10 MiB", str(e))

    def test_private_oserror_with_filename_does_not_leak(self):
        for exception in (PermissionError(13, SECRET, SECRET), OSError(5, SECRET, SECRET)):
            def reader(path, limit):
                raise exception
            with self.subTest(exception=type(exception).__name__):
                self.sanitized(lambda: read_policy_snapshot(self.source, 50, reader), "stable regular file")

    def test_other_size_message_is_not_misclassified(self):
        def reader(path, limit):
            raise ValueError("CSV input exceeds 64 MiB file-size limit " + SECRET)
        self.sanitized(lambda: read_policy_snapshot(self.source, 50, reader), "stable regular file")

    def test_snapshot_interrupts_and_memory_errors_propagate(self):
        for fault in (KeyboardInterrupt(), SystemExit(), MemoryError()):
            with self.subTest(fault=type(fault).__name__):
                def reader(path, limit):
                    raise fault
                with self.assertRaises(type(fault)):
                    read_policy_snapshot(self.source, 50, reader)

    def test_decode_valid_utf8_bom_preserves_newlines(self):
        self.assertEqual(decode_policy_utf8(b"\xef\xbb\xbfPolicy\r\n"), "Policy\r\n")

    def test_decode_empty_source(self):
        self.assertEqual(decode_policy_utf8(b""), "")

    def test_decode_invalid_utf8_does_not_retain_sensitive_object(self):
        self.sanitized(lambda: decode_policy_utf8(SECRET.encode() + b"\xff"), "valid UTF-8")

    def test_decode_invalid_bom_source_does_not_retain_sensitive_object(self):
        self.sanitized(lambda: decode_policy_utf8(b"\xef\xbb\xbf" + SECRET.encode() + b"\xff"), "valid UTF-8")

    def test_input_types_not_silently_coerced_into_compliance_decisions(self):
        self.sanitized(lambda: checked_policy_path(object(), ALLOWED), "supports existing")


if __name__ == "__main__":
    unittest.main()
