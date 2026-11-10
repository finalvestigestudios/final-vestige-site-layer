"""R330 local, synthetic fault tests for owned read-descriptor lifetime."""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from fvs_suite.journal_fd_read import read_bounded_duplicate

SYNTHETIC = b'{"review":"synthetic-human-check"}\n'


class JournalDuplicateR330(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="r330-synthetic-")
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "PRIVATE_DEMO_LEDGER.jsonl"
        self.path.write_bytes(SYNTHETIC)
        self.original = os.open(self.path, os.O_RDONLY)
        self.addCleanup(os.close, self.original)

    def _assert_closed(self, fd):
        with self.assertRaises(OSError):
            os.fstat(fd)
        self.assertEqual(os.fstat(self.original).st_size, len(SYNTHETIC))

    def test_normal_exact_read(self):
        self.assertEqual(read_bounded_duplicate(self.original, len(SYNTHETIC)), SYNTHETIC)

    def test_bounded_read_keeps_overflow_witness(self):
        self.assertEqual(read_bounded_duplicate(self.original, 5), SYNTHETIC[:6])

    def test_zero_limit_reads_one_byte(self):
        self.assertEqual(read_bounded_duplicate(self.original, 0), SYNTHETIC[:1])

    def test_invalid_limit_does_not_duplicate(self):
        with mock.patch("fvs_suite.journal_fd_read.os.dup", side_effect=AssertionError("dup executed")):
            for value in (-1, True, 1.5, "5", None):
                with self.subTest(value=value), self.assertRaisesRegex(ValueError, "limit is invalid"):
                    read_bounded_duplicate(self.original, value)

    def test_fdopen_oserror_closes_duplicate_and_retains_original(self):
        actual_dup = os.dup
        duplicates = []
        def capture(fd):
            value = actual_dup(fd)
            duplicates.append(value)
            return value
        with mock.patch("fvs_suite.journal_fd_read.os.dup", side_effect=capture):
            with mock.patch("fvs_suite.journal_fd_read.os.fdopen", side_effect=PermissionError("PRIVATE_DEMO_LEDGER")):
                with self.assertRaises(PermissionError):
                    read_bounded_duplicate(self.original, 4096)
        self.assertEqual(len(duplicates), 1)
        self._assert_closed(duplicates[0])

    def test_fdopen_runtimeerror_closes_duplicate(self):
        actual_dup = os.dup
        duplicates = []
        with mock.patch("fvs_suite.journal_fd_read.os.dup", side_effect=lambda fd: duplicates.append(actual_dup(fd)) or duplicates[-1]):
            with mock.patch("fvs_suite.journal_fd_read.os.fdopen", side_effect=RuntimeError("synthetic")):
                with self.assertRaisesRegex(RuntimeError, "synthetic"):
                    read_bounded_duplicate(self.original, 4096)
        self._assert_closed(duplicates[0])

    def test_fdopen_entry_failure_closes_duplicate(self):
        actual_dup = os.dup
        duplicates = []
        class BrokenEntry:
            def __enter__(self):
                raise OSError("enter refused")
            def __exit__(self, *args):
                raise AssertionError("not entered")
        with mock.patch("fvs_suite.journal_fd_read.os.dup", side_effect=lambda fd: duplicates.append(actual_dup(fd)) or duplicates[-1]):
            with mock.patch("fvs_suite.journal_fd_read.os.fdopen", return_value=BrokenEntry()):
                with self.assertRaisesRegex(OSError, "enter refused"):
                    read_bounded_duplicate(self.original, 4096)
        self._assert_closed(duplicates[0])

    def test_os_dup_failure_keeps_original_open(self):
        with mock.patch("fvs_suite.journal_fd_read.os.dup", side_effect=OSError("dup refused")):
            with self.assertRaisesRegex(OSError, "dup refused"):
                read_bounded_duplicate(self.original, 4096)
        self.assertEqual(os.fstat(self.original).st_size, len(SYNTHETIC))

    def test_read_exception_closes_duplicate(self):
        actual_dup = os.dup
        duplicates = []
        class BrokenRead:
            def __init__(self, fd):
                self.fd = fd
            def __enter__(self):
                return self
            def __exit__(self, *_):
                os.close(self.fd)
            def read(self, n):
                raise PermissionError("PRIVATE_DEMO_LEDGER")
        with mock.patch("fvs_suite.journal_fd_read.os.dup", side_effect=lambda fd: duplicates.append(actual_dup(fd)) or duplicates[-1]):
            with mock.patch("fvs_suite.journal_fd_read.os.fdopen", side_effect=lambda fd, mode: BrokenRead(fd)):
                with self.assertRaises(PermissionError):
                    read_bounded_duplicate(self.original, 4096)
        self._assert_closed(duplicates[0])

    def test_read_does_not_open_path_again(self):
        with mock.patch("fvs_suite.journal_fd_read.os.open", side_effect=AssertionError("path reopened")):
            self.assertEqual(read_bounded_duplicate(self.original, 4096), SYNTHETIC)

    def test_large_synthetic_limit_preserves_complete_record(self):
        self.assertEqual(read_bounded_duplicate(self.original, 1024 * 1024), SYNTHETIC)


if __name__ == "__main__":
    unittest.main()
