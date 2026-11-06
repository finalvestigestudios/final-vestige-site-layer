"""R237 end-to-end CSV writer privacy assertions (synthetic finance only).

This module is mandatory in both hosted OS workflows but cannot be claimed
locally executed without the inherited full repository dependencies.
"""
import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.atomic_reports import write_csv_report


class CSVPublicationIntegrationR237(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.target = self.root / "confidential-acme-payroll.csv"
        self.rows = [{"id": "A", "amount": "42.10"}]

    def publish(self):
        return write_csv_report(self.target, ("id", "amount"), self.rows, str)

    def assert_no_staging(self):
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_success_keeps_byte_exact_financial_csv_and_private_staging(self):
        self.assertEqual(self.publish(), self.target)
        self.assertEqual(self.target.read_bytes(), b"\xef\xbb\xbfid,amount\r\nA,42.10\r\n")
        self.assert_no_staging()

    def test_existing_file_fails_before_mkstemp_and_preserves_original(self):
        self.target.write_bytes(b"ORIGINAL")
        with patch("fvs_suite.atomic_reports.tempfile.mkstemp", side_effect=AssertionError("created stage")):
            with self.assertRaises(FileExistsError) as caught:
                self.publish()
        self.assertEqual(str(caught.exception), "CSV report destination already exists")
        self.assertEqual(self.target.read_bytes(), b"ORIGINAL")
        self.assert_no_staging()

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support unavailable")
    def test_dangling_symlink_fails_before_mkstemp(self):
        try:
            self.target.symlink_to(self.root / "unavailable-private.csv")
        except OSError:
            self.skipTest("symlink privilege unavailable")
        with patch("fvs_suite.atomic_reports.tempfile.mkstemp", side_effect=AssertionError("created stage")):
            with self.assertRaises(FileExistsError):
                self.publish()
        self.assertTrue(self.target.is_symlink())
        self.assert_no_staging()

    def test_fdopen_failure_leaks_neither_descriptor_nor_customer_path(self):
        captured = []
        def fail(fd, *args, **kwargs):
            captured.append(fd)
            raise PermissionError(errno.EACCES, "sensitive message", str(self.target))
        with patch("fvs_suite.csv_publish_guard.os.fdopen", side_effect=fail):
            with self.assertRaises(OSError) as caught:
                self.publish()
        self.assertEqual(caught.exception.errno, errno.EACCES)
        self.assertNotIn(str(self.target), str(caught.exception))
        self.assertIsNone(caught.exception.filename)
        self.assertEqual(len(captured), 1)
        with self.assertRaises(OSError):
            os.fstat(captured[0])
        self.assertFalse(self.target.exists())
        self.assert_no_staging()

    def test_fsync_failure_redacts_os_filename_and_removes_partial(self):
        with patch("fvs_suite.atomic_reports.os.fsync", side_effect=OSError(errno.ENOSPC, "sensitive", str(self.target))):
            with self.assertRaises(OSError) as caught:
                self.publish()
        self.assertEqual(caught.exception.errno, errno.ENOSPC)
        self.assertNotIn(str(self.target), str(caught.exception))
        self.assertFalse(self.target.exists())
        self.assert_no_staging()

    def test_mkstemp_failure_redacts_os_filename_without_new_report(self):
        with patch("fvs_suite.atomic_reports.tempfile.mkstemp", side_effect=OSError(errno.EACCES, "sensitive", str(self.target))):
            with self.assertRaises(OSError) as caught:
                self.publish()
        self.assertEqual(caught.exception.errno, errno.EACCES)
        self.assertNotIn(str(self.target), str(caught.exception))
        self.assertFalse(self.target.exists())
        self.assert_no_staging()

    def test_late_collision_does_not_overwrite_racer_or_leak_name(self):
        operation = "os.rename" if os.name == "nt" else "os.link"
        def collide(*args, **kwargs):
            self.target.write_bytes(b"RACER")
            raise FileExistsError(errno.EEXIST, "private data", str(self.target))
        with patch("fvs_suite.atomic_reports." + operation, side_effect=collide):
            with self.assertRaises(FileExistsError) as caught:
                self.publish()
        self.assertEqual(str(caught.exception), "CSV report destination already exists")
        self.assertEqual(self.target.read_bytes(), b"RACER")
        self.assert_no_staging()


if __name__ == "__main__":
    unittest.main()
