"""R239: no leaked candidate descriptors on fdopen failure; synthetic offline files only.

Does not sign, execute or approve an executable; tests both six-app hashes and
SHA256SUMS.txt read through the exact candidate guard module.
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


class CandidateDescriptorCustodyR239(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="fvs-r239-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.file = self.root / "confidential-ledger-client.exe"
        self.file.write_bytes(b"synthetic non-executable contents")
        self.manifest = self.root / "SHA256SUMS.txt"
        self.manifest.write_bytes(b"fake checksum inventory, no real binary")
        self.native_open = os.open
        self.opened = []

    def tracking_open(self, *args, **kwargs):
        fd = self.native_open(*args, **kwargs)
        self.opened.append(fd)
        return fd

    def assert_closed(self):
        self.assertEqual(len(self.opened), 1)
        with self.assertRaises(OSError) as caught:
            os.fstat(self.opened[0])
        self.assertEqual(caught.exception.errno, errno.EBADF)

    def guarded(self, checksum: bool):
        return (read_checksum_candidate(self.manifest) if checksum
                else sha256_candidate(self.file))

    def induce_fdopen_error(self, checksum, failure):
        target = str(self.manifest if checksum else self.file)
        with patch("candidate_guard.os.open", side_effect=self.tracking_open):
            with patch("candidate_guard.os.fdopen", side_effect=failure):
                with self.assertRaises(CandidateGuardError) as raised:
                    self.guarded(checksum)
        self.assertEqual(str(raised.exception), "Unable to read candidate payload safely")
        self.assertNotIn(target, str(raised.exception))
        self.assertNotIn("private", str(raised.exception).lower())
        self.assert_closed()
        self.assertIsNone(raised.exception.__cause__)

    def test_exe_fdopen_permission_error(self):
        self.induce_fdopen_error(False, PermissionError(errno.EACCES, "private secret", str(self.file)))

    def test_inventory_fdopen_permission_error(self):
        self.induce_fdopen_error(True, PermissionError(errno.EACCES, "private secret", str(self.manifest)))

    def test_exe_fdopen_too_many_handles(self):
        self.induce_fdopen_error(False, OSError(errno.EMFILE, "client name", str(self.file)))

    def test_inventory_fdopen_too_many_handles(self):
        self.induce_fdopen_error(True, OSError(errno.EMFILE, "client name", str(self.manifest)))

    def test_exe_fdopen_value_error(self):
        self.induce_fdopen_error(False, ValueError("private invoice file"))

    def test_inventory_fdopen_value_error(self):
        self.induce_fdopen_error(True, ValueError("private invoice file"))

    def test_exe_fdopen_type_error(self):
        self.induce_fdopen_error(False, TypeError("private invoice file"))

    def test_inventory_fdopen_type_error(self):
        self.induce_fdopen_error(True, TypeError("private invoice file"))

    def test_exe_fdopen_unicode_error(self):
        self.induce_fdopen_error(False, UnicodeError("private invoice file"))

    def test_inventory_fdopen_unicode_error(self):
        self.induce_fdopen_error(True, UnicodeError("private invoice file"))

    def test_exe_keyboard_interrupt_closes(self):
        self.interrupt(False, KeyboardInterrupt())

    def test_inventory_keyboard_interrupt_closes(self):
        self.interrupt(True, KeyboardInterrupt())

    def test_exe_system_exit_closes(self):
        self.interrupt(False, SystemExit(7))

    def test_inventory_system_exit_closes(self):
        self.interrupt(True, SystemExit(7))

    def interrupt(self, checksum, failure):
        with patch("candidate_guard.os.open", side_effect=self.tracking_open):
            with patch("candidate_guard.os.fdopen", side_effect=failure):
                with self.assertRaises(type(failure)):
                    self.guarded(checksum)
        self.assert_closed()

    def test_exe_normal_digest_byte_exact(self):
        with patch("candidate_guard.os.open", side_effect=self.tracking_open):
            digest = self.guarded(False)
        self.assertEqual(digest, hashlib.sha256(self.file.read_bytes()).hexdigest())
        self.assert_closed()

    def test_inventory_normal_bytes_exact(self):
        with patch("candidate_guard.os.open", side_effect=self.tracking_open):
            raw = self.guarded(True)
        self.assertEqual(raw, self.manifest.read_bytes())
        self.assert_closed()

    def test_exe_open_error_hides_client_path(self):
        with patch("candidate_guard.os.open", side_effect=OSError(errno.EACCES, "secret", str(self.file))):
            with self.assertRaises(CandidateGuardError) as caught:
                self.guarded(False)
        self.assertEqual(str(caught.exception), "Unable to open candidate payload safely")
        self.assertEqual(self.opened, [])

    def test_inventory_open_error_hides_client_path(self):
        with patch("candidate_guard.os.open", side_effect=OSError(errno.EACCES, "secret", str(self.manifest))):
            with self.assertRaises(CandidateGuardError) as caught:
                self.guarded(True)
        self.assertEqual(str(caught.exception), "Unable to open candidate payload safely")
        self.assertEqual(self.opened, [])

    def test_exe_inner_fstat_error_closes(self):
        with patch("candidate_guard.os.open", side_effect=self.tracking_open):
            with patch("candidate_guard.os.fstat", side_effect=OSError(errno.EIO, "private client", str(self.file))):
                with self.assertRaisesRegex(CandidateGuardError, "Unable to read candidate"):
                    self.guarded(False)
        self.assert_closed()

    def test_inventory_inner_fstat_error_closes(self):
        with patch("candidate_guard.os.open", side_effect=self.tracking_open):
            with patch("candidate_guard.os.fstat", side_effect=OSError(errno.EIO, "private client", str(self.manifest))):
                with self.assertRaisesRegex(CandidateGuardError, "Unable to read candidate"):
                    self.guarded(True)
        self.assert_closed()


if __name__ == "__main__":
    unittest.main()
