"""R241: release-candidate and SHA256 manifest stream faults fail closed.

Exercises actual local file descriptors on synthetic bytes only. No EXE executes,
no premium data, external requests, or release authorization is involved.
"""
from __future__ import annotations

import errno
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from candidate_guard import CandidateGuardError, read_checksum_candidate, sha256_candidate


class FaultStream:
    """A stream proxy that injects one chosen fault without synthetic file handles."""

    def __init__(self, native, phase=None, fault=None):
        self.native = native
        self.phase = phase
        self.fault = fault
        self.close_attempted = False

    def fail(self, phase):
        if self.phase == phase:
            raise self.fault

    def __enter__(self):
        self.fail("enter")
        self.native.__enter__()
        return self

    def __exit__(self, *args):
        self.native.__exit__(*args)
        self.fail("exit")

    def fileno(self):
        self.fail("fileno")
        return self.native.fileno()

    def read(self, *args, **kwargs):
        self.fail("read")
        return self.native.read(*args, **kwargs)

    def close(self):
        self.close_attempted = True
        self.native.close()


class CandidateStreamPrivacyR241(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r241-")
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.exe = root / "private-customer-payables.exe"
        self.manifest = root / "SHA256SUMS.txt"
        self.exe.write_bytes(b"This is not an executable; local synthetic fixture only.\x00")
        self.manifest.write_bytes(b"synthetic manifest data only\n")
        self.exe_bytes = self.exe.read_bytes()
        self.manifest_bytes = self.manifest.read_bytes()
        self.native_open = os.open
        self.native_fdopen = os.fdopen
        self.opened = []
        self.proxies = []

    def tracking_open(self, *args, **kwargs):
        fd = self.native_open(*args, **kwargs)
        self.opened.append(fd)
        return fd

    def guard(self, checksum):
        return read_checksum_candidate(self.manifest) if checksum else sha256_candidate(self.exe)

    def run_fault(self, *, checksum, phase, fault, expected=CandidateGuardError):
        def fdopen(*args, **kwargs):
            wrapper = FaultStream(self.native_fdopen(*args, **kwargs), phase, fault)
            self.proxies.append(wrapper)
            return wrapper
        with patch("candidate_guard.os.open", side_effect=self.tracking_open):
            with patch("candidate_guard.os.fdopen", side_effect=fdopen):
                with self.assertRaises(expected) as result:
                    self.guard(checksum)
        self.assertEqual(len(self.opened), 1, "one actual descriptor should be opened")
        with self.assertRaises(OSError) as closed:
            os.fstat(self.opened[0])
        self.assertEqual(closed.exception.errno, errno.EBADF, "raw descriptor must be closed")
        self.assertEqual(self.exe.read_bytes(), self.exe_bytes)
        self.assertEqual(self.manifest.read_bytes(), self.manifest_bytes)
        if expected is CandidateGuardError:
            self.assertEqual(str(result.exception), "Unable to read candidate payload safely")
            self.assertIsNone(result.exception.__cause__)
            self.assertNotIn("private", str(result.exception).lower())
            self.assertNotIn(str(self.exe), str(result.exception))
            self.assertNotIn(str(self.manifest), str(result.exception))
        if phase == "enter":
            self.assertTrue(self.proxies[0].close_attempted, "failed __enter__ needs explicit close")
        return result.exception

    def test_exe_enter_oserror_closed_and_redacted(self):
        self.run_fault(checksum=False, phase="enter", fault=OSError(errno.EACCES, "private path", str(self.exe)))

    def test_manifest_enter_oserror_closed_and_redacted(self):
        self.run_fault(checksum=True, phase="enter", fault=OSError(errno.EIO, "private path", str(self.manifest)))

    def test_exe_enter_non_oserror_closed_and_redacted(self):
        self.run_fault(checksum=False, phase="enter", fault=ValueError("private report path"))

    def test_manifest_enter_non_oserror_closed_and_redacted(self):
        self.run_fault(checksum=True, phase="enter", fault=TypeError("private report path"))

    def test_exe_fileno_non_oserror_redacted(self):
        self.run_fault(checksum=False, phase="fileno", fault=TypeError("private report path"))

    def test_manifest_fileno_oserror_redacted(self):
        self.run_fault(checksum=True, phase="fileno", fault=OSError(errno.EIO, "private path", str(self.manifest)))

    def test_exe_read_oserror_redacted(self):
        self.run_fault(checksum=False, phase="read", fault=PermissionError(errno.EACCES, "private path", str(self.exe)))

    def test_manifest_read_oserror_redacted(self):
        self.run_fault(checksum=True, phase="read", fault=PermissionError(errno.EACCES, "private path", str(self.manifest)))

    def test_exe_read_non_oserror_redacted(self):
        self.run_fault(checksum=False, phase="read", fault=RuntimeError("private report path"))

    def test_manifest_read_non_oserror_redacted(self):
        self.run_fault(checksum=True, phase="read", fault=UnicodeError("private report path"))

    def test_exe_exit_oserror_redacted(self):
        self.run_fault(checksum=False, phase="exit", fault=OSError(errno.EIO, "private path", str(self.exe)))

    def test_manifest_exit_non_oserror_redacted(self):
        self.run_fault(checksum=True, phase="exit", fault=RuntimeError("private report path"))

    def test_exe_enter_interrupt_closes_then_propagates(self):
        self.run_fault(checksum=False, phase="enter", fault=KeyboardInterrupt(), expected=KeyboardInterrupt)

    def test_manifest_enter_exit_closes_then_propagates(self):
        exc = self.run_fault(checksum=True, phase="enter", fault=SystemExit(71), expected=SystemExit)
        self.assertEqual(exc.code, 71)

    def test_exe_read_interrupt_propagates(self):
        self.run_fault(checksum=False, phase="read", fault=KeyboardInterrupt(), expected=KeyboardInterrupt)

    def test_manifest_read_exit_propagates(self):
        exc = self.run_fault(checksum=True, phase="read", fault=SystemExit(72), expected=SystemExit)
        self.assertEqual(exc.code, 72)

    def test_exe_success_digest_exact(self):
        with patch("candidate_guard.os.open", side_effect=self.tracking_open):
            result = self.guard(False)
        self.assertEqual(result, hashlib.sha256(self.exe_bytes).hexdigest())
        with self.assertRaises(OSError) as closed:
            os.fstat(self.opened[0])
        self.assertEqual(closed.exception.errno, errno.EBADF)

    def test_manifest_success_bytes_exact(self):
        with patch("candidate_guard.os.open", side_effect=self.tracking_open):
            result = self.guard(True)
        self.assertEqual(result, self.manifest_bytes)
        with self.assertRaises(OSError) as closed:
            os.fstat(self.opened[0])
        self.assertEqual(closed.exception.errno, errno.EBADF)


if __name__ == "__main__":
    unittest.main()
