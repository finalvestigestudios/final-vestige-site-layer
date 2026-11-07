"""R258: CSV source snapshot descriptor ownership and private error hygiene.

Synthetic filesystem only; no customer data. All checks target the real CSV
snapshot implementation used by the suite, not mocks of its parsing logic.
"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import csv_snapshot as subject


class CsvDescriptorCustodyR258(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "private-financial-data.csv"
        self.original = b"id,amount\r\nA,1.25\r\nB,-0.01\r\n"
        self.source.write_bytes(self.original)

    def fault_during_adoption(self, fault, expected):
        """Exercise a genuine OS handle, close it afterward if the SUT leaks."""
        fds = []
        real_open = os.open

        def record_open(*args, **kwargs):
            handle = real_open(*args, **kwargs)
            fds.append(handle)
            return handle

        try:
            with (patch("fvs_suite.csv_snapshot.os.open", side_effect=record_open),
                  patch("fvs_suite.csv_snapshot.os.fdopen", side_effect=fault)):
                with self.assertRaises(expected) as caught:
                    subject.read_csv_snapshot(self.source, 1024)
            self.assertEqual(len(fds), 1)
            with self.assertRaises(OSError):
                os.fstat(fds[0])
            self.assertEqual(self.source.read_bytes(), self.original)
            return caught.exception
        finally:
            # A failing pre-fix regression must not itself leak a descriptor.
            for fd in fds:
                try:
                    os.close(fd)
                except OSError:
                    pass

    def test_normal_exact_bytes_preserved(self):
        self.assertEqual(subject.read_csv_snapshot(self.source, 1024), self.original)

    def test_successful_read_closes_real_descriptor(self):
        fds = []
        real_open = os.open

        def record_open(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            fds.append(fd)
            return fd

        with patch("fvs_suite.csv_snapshot.os.open", side_effect=record_open):
            self.assertEqual(subject.read_csv_snapshot(self.source, 1024), self.original)
        self.assertEqual(len(fds), 1)
        with self.assertRaises(OSError):
            os.fstat(fds[0])

    def test_fdopen_oserror_closes_handle_and_redacts(self):
        error = self.fault_during_adoption(OSError("/private/customer/ledger.csv"), ValueError)
        self.assertNotIn("customer", str(error))
        self.assertIn("Cannot read CSV input", str(error))

    def test_fdopen_permissionerror_closes_handle_and_redacts(self):
        error = self.fault_during_adoption(PermissionError("/private/customer.csv"), ValueError)
        self.assertNotIn("customer.csv", str(error))

    def test_fdopen_runtimeerror_closes_handle_and_redacts(self):
        error = self.fault_during_adoption(RuntimeError("/private/customer/ledger.csv"), ValueError)
        self.assertNotIn("customer", str(error))

    def test_fdopen_typeerror_closes_handle_and_redacts(self):
        error = self.fault_during_adoption(TypeError("/private/customer/ledger.csv"), ValueError)
        self.assertNotIn("ledger.csv", str(error))

    def test_fdopen_keyboardinterrupt_closes_handle(self):
        self.fault_during_adoption(KeyboardInterrupt(), KeyboardInterrupt)

    def test_fdopen_systemexit_closes_handle(self):
        self.fault_during_adoption(SystemExit(7), SystemExit)

    def test_fdopen_memoryerror_closes_handle(self):
        self.fault_during_adoption(MemoryError(), MemoryError)

    def test_fdopen_generatorexit_closes_handle(self):
        self.fault_during_adoption(GeneratorExit(), GeneratorExit)

    def test_unexpected_os_open_error_redacts_and_does_not_adopt(self):
        with (patch("fvs_suite.csv_snapshot.os.open", side_effect=RuntimeError("/private/customer/ledger.csv")),
              patch("fvs_suite.csv_snapshot.os.fdopen") as adopt):
            with self.assertRaises(ValueError) as caught:
                subject.read_csv_snapshot(self.source, 1024)
            adopt.assert_not_called()
        self.assertNotIn("customer", str(caught.exception))

    def test_os_open_permission_error_redacts_and_does_not_adopt(self):
        with (patch("fvs_suite.csv_snapshot.os.open", side_effect=PermissionError("/private/customer.csv")),
              patch("fvs_suite.csv_snapshot.os.fdopen") as adopt):
            with self.assertRaisesRegex(ValueError, "Cannot safely open CSV input") as caught:
                subject.read_csv_snapshot(self.source, 1024)
            adopt.assert_not_called()
        self.assertNotIn("customer.csv", str(caught.exception))

    def test_oversized_source_does_not_open_file(self):
        with patch("fvs_suite.csv_snapshot.os.open") as opener:
            with self.assertRaisesRegex(ValueError, "file-size limit"):
                subject.read_csv_snapshot(self.source, len(self.original) - 1)
            opener.assert_not_called()

    def test_symlink_fails_before_open_and_source_is_unchanged(self):
        link = self.root / "linked.csv"
        try:
            link.symlink_to(self.source)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"Symlinks unavailable: {type(exc).__name__}")
        with patch("fvs_suite.csv_snapshot.os.open") as opener:
            with self.assertRaisesRegex(ValueError, "regular file"):
                subject.read_csv_snapshot(link, 1024)
            opener.assert_not_called()
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_negative_limit_does_not_open_file(self):
        with patch("fvs_suite.csv_snapshot.os.open") as opener:
            with self.assertRaisesRegex(ValueError, "Invalid CSV input size limit"):
                subject.read_csv_snapshot(self.source, -1)
            opener.assert_not_called()


if __name__ == "__main__":
    unittest.main()
