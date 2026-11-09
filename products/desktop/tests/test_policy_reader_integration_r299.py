"""R299 integration regressions for Policy Delta's private source boundary.

Runs only in the complete desktop checkout; never uses real customer data.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import policy_diff as pd
from fvs_suite import csv_snapshot

SECRET = "confidential-policy-source-90831"


class PolicyReaderPrivacyR299(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.source = self.root / "before.txt"
        self.source.write_bytes(b"Policy One\r\n")

    def assert_clean_error(self, action, expected):
        with self.assertRaises(ValueError) as caught:
            action()
        error = caught.exception
        self.assertIn(expected, str(error))
        self.assertNotIn(SECRET, str(error))
        self.assertIsNone(error.__context__)
        self.assertIsNone(error.__cause__)

    def test_real_snapshot_retains_physical_lines_sha_and_basename(self):
        lines, digest, label = pd._read_policy(self.source)
        self.assertEqual(lines, ["Policy One\r\n"])
        self.assertEqual(digest, hashlib.sha256(b"Policy One\r\n").hexdigest())
        self.assertEqual(label, '"before.txt"')

    def test_valid_bom_is_accepted_with_byte_exact_hash(self):
        raw = b"\xef\xbb\xbfPolicy One\n"
        self.source.write_bytes(raw)
        lines, digest, name = pd._read_policy(self.source)
        self.assertEqual(lines, ["Policy One\n"])
        self.assertEqual(digest, hashlib.sha256(raw).hexdigest())

    def test_real_invalid_utf8_has_no_hidden_exception_chain(self):
        self.source.write_bytes(SECRET.encode() + b"\xff")
        self.assert_clean_error(lambda: pd._read_policy(self.source), "UTF-8")

    def test_real_limit_retains_policy_specific_message_and_no_context(self):
        with patch.object(pd, "MAX_POLICY_BYTES", 3):
            self.assert_clean_error(lambda: pd._read_policy(self.source), "10 MiB")

    def test_path_probe_permission_failure_never_leaks_customer_path(self):
        private = PermissionError(13, SECRET, SECRET)
        with patch.object(Path, "is_file", side_effect=private):
            self.assert_clean_error(lambda: pd._read_policy(self.source), "supports existing")

    def test_snapshot_permission_failure_never_leaks_customer_path(self):
        private = PermissionError(13, SECRET, SECRET)
        with patch.object(csv_snapshot, "read_csv_snapshot", side_effect=private):
            self.assert_clean_error(lambda: pd._read_policy(self.source), "stable regular file")

    def test_snapshot_private_valueerror_does_not_get_oversize_label(self):
        with patch.object(csv_snapshot, "read_csv_snapshot",
                          side_effect=ValueError(SECRET + " exceeds data.txt")):
            self.assert_clean_error(lambda: pd._read_policy(self.source), "stable regular file")

    def test_unsupported_suffix_does_not_create_any_report(self):
        self.source.rename(self.root / "before.pdf")
        self.assert_clean_error(lambda: pd._read_policy(self.root / "before.pdf"), "supports existing")
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["before.pdf"])

    def test_compare_policy_files_bad_second_input_is_non_destructive(self):
        other = self.root / "after.txt"
        other.write_bytes(SECRET.encode() + b"\xff")
        out = self.root / "should-not-exist.txt"
        self.assert_clean_error(
            lambda: pd.compare_policy_files(self.source, other, self.root,
                 lambda folder, stem, ext: out),
            "UTF-8")
        self.assertFalse(out.exists())
        self.assertEqual(self.source.read_bytes(), b"Policy One\r\n")
        self.assertEqual(other.read_bytes(), SECRET.encode() + b"\xff")


if __name__ == "__main__":
    unittest.main()
