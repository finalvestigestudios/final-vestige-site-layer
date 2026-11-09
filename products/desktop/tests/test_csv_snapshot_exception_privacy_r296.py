"""R296: no hidden customer paths in snapshot OS-error exception chains.

Runs on Linux and Windows against real temporary CSVs, using synthetic fault
injection at each filesystem boundary. No external services or user data.
"""
from __future__ import annotations

import errno
import os
import tempfile
import traceback
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import csv_snapshot


SENSITIVE = "CUSTOMER_LEDGER_ACCOUNT_87654321"


class SnapshotExceptionPrivacyR296(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r296-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.source = self.root / "synthetic-ledger.csv"
        self.original = b"\xef\xbb\xbfref,amount\r\nA,1.20\r\nB,-0.02\r\n"
        self.source.write_bytes(self.original)

    def read(self):
        return csv_snapshot.read_csv_snapshot(self.source, len(self.original))

    def assert_private(self, expected: str, action) -> None:
        try:
            action()
        except ValueError as error:
            self.assertEqual(str(error), expected)
            self.assertIsNone(error.__context__, "Private OS error remains reachable")
            self.assertIsNone(error.__cause__)
            self.assertNotIn(SENSITIVE, "".join(traceback.format_exception(error)))
            self.assertNotIn(str(self.source), "".join(traceback.format_exception(error)))
        else:
            self.fail("Injected error was not rejected")
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_regular_snapshot_preserves_exact_bom_and_decimals(self):
        self.assertEqual(self.read(), self.original)

    def test_file_not_found_context_is_not_exposed(self):
        with patch.object(Path, "lstat", side_effect=FileNotFoundError(errno.ENOENT, SENSITIVE, str(self.source))):
            self.assert_private("CSV input file is missing", self.read)

    def test_permission_inspection_context_is_not_exposed(self):
        with patch.object(Path, "lstat", side_effect=PermissionError(errno.EACCES, SENSITIVE, str(self.source))):
            self.assert_private("Cannot inspect CSV input", self.read)

    def test_generic_metadata_oserror_context_is_not_exposed(self):
        with patch.object(Path, "lstat", side_effect=OSError(errno.EIO, SENSITIVE, str(self.source))):
            self.assert_private("Cannot inspect CSV input", self.read)

    def test_open_permission_context_is_not_exposed(self):
        with patch("fvs_suite.csv_snapshot.os.open", side_effect=PermissionError(errno.EACCES, SENSITIVE, str(self.source))):
            self.assert_private("Cannot safely open CSV input", self.read)

    def test_open_runtime_exception_context_is_not_exposed(self):
        with patch("fvs_suite.csv_snapshot.os.open", side_effect=RuntimeError(SENSITIVE)):
            self.assert_private("Cannot safely open CSV input", self.read)

    def _test_adoption_error(self, error):
        descriptors = []
        real_open = os.open
        def tracked_open(*args, **kwargs):
            descriptor = real_open(*args, **kwargs)
            descriptors.append(descriptor)
            return descriptor
        try:
            with (patch("fvs_suite.csv_snapshot.os.open", side_effect=tracked_open),
                  patch("fvs_suite.csv_snapshot.os.fdopen", side_effect=error)):
                self.assert_private("Cannot read CSV input", self.read)
            self.assertEqual(len(descriptors), 1)
            with self.assertRaises(OSError):
                os.fstat(descriptors[0])
        finally:
            for descriptor in descriptors:
                try:
                    os.close(descriptor)
                except OSError:
                    pass

    def test_fdopen_permission_context_and_descriptor_closed(self):
        self._test_adoption_error(PermissionError(errno.EACCES, SENSITIVE, str(self.source)))

    def test_fdopen_runtime_context_and_descriptor_closed(self):
        self._test_adoption_error(RuntimeError(SENSITIVE))

    def test_fdopen_type_context_and_descriptor_closed(self):
        self._test_adoption_error(TypeError(SENSITIVE))

    def test_fdopen_other_oserror_context_and_descriptor_closed(self):
        self._test_adoption_error(OSError(errno.EIO, SENSITIVE, str(self.source)))

    def test_fstat_failure_context_not_exposed(self):
        with patch("fvs_suite.csv_snapshot.os.fstat", side_effect=OSError(errno.EBADF, SENSITIVE, str(self.source))):
            self.assert_private("Cannot read CSV input", self.read)

    def test_final_descriptor_fstat_context_not_exposed(self):
        real_fstat = os.fstat
        count = 0
        def check(fd):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError(errno.EIO, SENSITIVE, str(self.source))
            return real_fstat(fd)
        with patch("fvs_suite.csv_snapshot.os.fstat", side_effect=check):
            self.assert_private("Cannot read CSV input", self.read)
        self.assertEqual(count, 2)

    def test_stream_read_exception_context_not_exposed(self):
        real_fdopen = os.fdopen
        private_path = str(self.source)
        class FaultyStream:
            def __init__(self, wrapped):
                self.wrapped = wrapped
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return self.wrapped.__exit__(*args)
            def fileno(self):
                return self.wrapped.fileno()
            def read(self, length):
                raise OSError(errno.EIO, SENSITIVE, private_path)
        with patch("fvs_suite.csv_snapshot.os.fdopen", side_effect=lambda *a: FaultyStream(real_fdopen(*a))):
            self.assert_private("Cannot read CSV input", self.read)

    def test_close_exception_context_not_exposed(self):
        real_fdopen = os.fdopen
        private_path = str(self.source)
        class CloseFailure:
            def __init__(self, wrapped):
                self.wrapped = wrapped
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.wrapped.close()
                raise OSError(errno.EIO, SENSITIVE, private_path)
            def fileno(self):
                return self.wrapped.fileno()
            def read(self, length):
                return self.wrapped.read(length)
        with patch("fvs_suite.csv_snapshot.os.fdopen", side_effect=lambda *a: CloseFailure(real_fdopen(*a))):
            self.assert_private("Cannot read CSV input", self.read)

    def test_final_path_lstat_exception_context_not_exposed(self):
        real_lstat = Path.lstat
        count = 0
        def failure(path):
            nonlocal count
            count += 1
            if count == 2:
                raise PermissionError(errno.EACCES, SENSITIVE, str(self.source))
            return real_lstat(path)
        with patch.object(Path, "lstat", autospec=True, side_effect=failure):
            self.assert_private("Cannot inspect CSV input", self.read)
        self.assertEqual(count, 2)

    def test_original_limit_and_symlink_controls_unchanged(self):
        with self.assertRaisesRegex(ValueError, "file-size limit"):
            csv_snapshot.read_csv_snapshot(self.source, len(self.original) - 1)
        link = self.root / "symlink.csv"
        try:
            link.symlink_to(self.source)
        except (NotImplementedError, OSError):
            self.skipTest("Symlink privileges unavailable")
        with self.assertRaisesRegex(ValueError, "regular file"):
            csv_snapshot.read_csv_snapshot(link, len(self.original))
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_keyboard_interrupt_at_fdopen_propagates_without_descriptor_leak(self):
        descriptors = []
        real_open = os.open
        def tracked_open(*a, **kw):
            fd = real_open(*a, **kw)
            descriptors.append(fd)
            return fd
        try:
            with (patch("fvs_suite.csv_snapshot.os.open", side_effect=tracked_open),
                  patch("fvs_suite.csv_snapshot.os.fdopen", side_effect=KeyboardInterrupt())):
                with self.assertRaises(KeyboardInterrupt):
                    self.read()
            self.assertEqual(len(descriptors), 1)
            with self.assertRaises(OSError):
                os.fstat(descriptors[0])
        finally:
            for fd in descriptors:
                try: os.close(fd)
                except OSError: pass


    def test_systemexit_at_fdopen_preserves_interrupt_semantics(self):
        real_open = os.open
        descriptor = None
        def tracked_open(*args, **kwargs):
            nonlocal descriptor
            descriptor = real_open(*args, **kwargs)
            return descriptor
        try:
            with (patch("fvs_suite.csv_snapshot.os.open", side_effect=tracked_open),
                  patch("fvs_suite.csv_snapshot.os.fdopen", side_effect=SystemExit(73))):
                with self.assertRaises(SystemExit) as caught:
                    self.read()
            self.assertEqual(caught.exception.code, 73)
            with self.assertRaises(OSError):
                os.fstat(descriptor)
        finally:
            if descriptor is not None:
                try: os.close(descriptor)
                except OSError: pass

    def test_memoryerror_at_fdopen_not_silently_sanitized(self):
        with patch("fvs_suite.csv_snapshot.os.fdopen", side_effect=MemoryError()):
            with self.assertRaises(MemoryError):
                self.read()


if __name__ == "__main__":
    unittest.main()
