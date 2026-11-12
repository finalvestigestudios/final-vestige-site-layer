"""R374: candidate integrity-check failures must not retain private causes.

Only inert local bytes and temporary directories are used. Never run an EXE,
change an input file, publish a candidate, or exercise customer financial data.
"""
from __future__ import annotations

import errno
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import candidate_guard
from candidate_guard import CandidateGuardError, check_candidate_directory, read_checksum_candidate, sha256_candidate


EXES = (
    "LedgerDiffLite.exe", "InvoiceTwinScout.exe", "SpendMapLite.exe",
    "PolicyDeltaDesk.exe", "GrantAuditStudioPro.exe", "ProcureGuardStudioPro.exe",
)


class FaultStream:
    """Forward actual disk operations, injecting a synthetic private exception."""
    def __init__(self, native, phase, fault):
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


class CandidateExceptionChainsR374(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="fv-r374-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.originals = {}
        for index, name in enumerate(EXES, 1):
            payload = (b"inert test bytes" + bytes([index])) * 30
            (self.root / name).write_bytes(payload)
            self.originals[name] = payload
        self.manifest = self.root / "SHA256SUMS.txt"
        self.manifest.write_bytes(b"a" * 64 + b"  LedgerDiffLite.exe\n")
        self.originals[self.manifest.name] = self.manifest.read_bytes()
        self.exe = self.root / EXES[0]
        self.open = os.open
        self.fdopen = os.fdopen
        self.descriptors = []
        self.proxies = []

    def private_error(self, cls=OSError):
        if issubclass(cls, OSError):
            return cls(errno.EACCES, "PRIVATE_CLIENT_LEDGER_PATH", str(self.exe))
        return cls("PRIVATE_CLIENT_LEDGER_PATH")

    def assert_public(self, exception, expected=None):
        self.assertIs(type(exception), CandidateGuardError)
        self.assertIsNone(exception.__context__, "raw exception must not be retained in __context__")
        self.assertIsNone(exception.__cause__, "raw exception must not be retained in __cause__")
        self.assertNotIn("PRIVATE_CLIENT_LEDGER_PATH", str(exception))
        self.assertNotIn(str(self.root), str(exception))
        if expected is not None:
            self.assertEqual(str(exception), expected)

    def assert_unchanged(self):
        for name, content in self.originals.items():
            self.assertEqual((self.root / name).read_bytes(), content)

    def track_open(self, *args, **kwargs):
        fd = self.open(*args, **kwargs)
        self.descriptors.append(fd)
        return fd

    def assert_closed(self):
        self.assertEqual(len(self.descriptors), 1)
        with self.assertRaises(OSError) as e:
            os.fstat(self.descriptors[0])
        self.assertEqual(e.exception.errno, errno.EBADF)

    def smoke_fault(self, phase, fault, *, manifest=False, expected=CandidateGuardError):
        target = self.manifest if manifest else self.exe
        def fake_fdopen(*args, **kwargs):
            proxy = FaultStream(self.fdopen(*args, **kwargs), phase, fault)
            self.proxies.append(proxy)
            return proxy
        with patch.object(candidate_guard.os, "open", side_effect=self.track_open), patch.object(
                candidate_guard.os, "fdopen", side_effect=fake_fdopen):
            with self.assertRaises(expected) as e:
                if manifest:
                    read_checksum_candidate(target)
                else:
                    sha256_candidate(target)
        self.assert_closed()
        self.assert_unchanged()
        if expected is CandidateGuardError:
            self.assert_public(e.exception, "Unable to read candidate payload safely")
        if phase == "enter":
            self.assertTrue(self.proxies[0].close_attempted)
        return e.exception

    def test_missing_path_clean_chain(self):
        with self.assertRaises(CandidateGuardError) as e:
            sha256_candidate(self.root / "missing-private-file.exe")
        self.assert_public(e.exception, "Missing or inaccessible candidate payload")

    def test_lstat_oserror_clean_chain(self):
        with patch.object(Path, "lstat", side_effect=self.private_error()):
            with self.assertRaises(CandidateGuardError) as e:
                sha256_candidate(self.exe)
        self.assert_public(e.exception, "Missing or inaccessible candidate payload")

    def test_directory_lstat_oserror_clean_chain(self):
        with patch.object(Path, "lstat", side_effect=self.private_error()):
            with self.assertRaises(CandidateGuardError) as e:
                check_candidate_directory(self.root, EXES)
        self.assert_public(e.exception, "Cannot inspect candidate directory")

    def test_directory_iteration_oserror_clean_chain(self):
        with patch.object(Path, "iterdir", side_effect=self.private_error()):
            with self.assertRaises(CandidateGuardError) as e:
                check_candidate_directory(self.root, EXES)
        self.assert_public(e.exception, "Cannot inspect candidate directory")

    def test_open_oserror_clean_chain(self):
        with patch.object(candidate_guard.os, "open", side_effect=self.private_error()):
            with self.assertRaises(CandidateGuardError) as e:
                sha256_candidate(self.exe)
        self.assert_public(e.exception, "Unable to open candidate payload safely")

    def test_fdopen_oserror_clean_chain_and_closed(self):
        with patch.object(candidate_guard.os, "open", side_effect=self.track_open), patch.object(
                candidate_guard.os, "fdopen", side_effect=self.private_error()):
            with self.assertRaises(CandidateGuardError) as e:
                sha256_candidate(self.exe)
        self.assert_public(e.exception, "Unable to read candidate payload safely")
        self.assert_closed()

    def test_fdopen_valueerror_clean_chain_and_closed(self):
        with patch.object(candidate_guard.os, "open", side_effect=self.track_open), patch.object(
                candidate_guard.os, "fdopen", side_effect=self.private_error(ValueError)):
            with self.assertRaises(CandidateGuardError) as e:
                read_checksum_candidate(self.manifest)
        self.assert_public(e.exception, "Unable to read candidate payload safely")
        self.assert_closed()

    def test_fdopen_interrupt_closes_and_propagates(self):
        with patch.object(candidate_guard.os, "open", side_effect=self.track_open), patch.object(
                candidate_guard.os, "fdopen", side_effect=KeyboardInterrupt()):
            with self.assertRaises(KeyboardInterrupt):
                sha256_candidate(self.exe)
        self.assert_closed()

    def test_stream_enter_oserror_clean_chain(self):
        self.smoke_fault("enter", self.private_error())

    def test_stream_enter_typeerror_clean_chain(self):
        self.smoke_fault("enter", self.private_error(TypeError), manifest=True)

    def test_stream_fileno_oserror_clean_chain(self):
        self.smoke_fault("fileno", self.private_error(), manifest=True)

    def test_stream_read_oserror_clean_chain(self):
        self.smoke_fault("read", self.private_error())

    def test_stream_read_valueerror_clean_chain(self):
        self.smoke_fault("read", self.private_error(ValueError), manifest=True)

    def test_stream_exit_oserror_clean_chain(self):
        self.smoke_fault("exit", self.private_error())

    def test_stream_exit_runtimeerror_clean_chain(self):
        self.smoke_fault("exit", self.private_error(RuntimeError), manifest=True)

    def test_stream_interrupt_propagates_and_closes(self):
        self.smoke_fault("read", KeyboardInterrupt(), expected=KeyboardInterrupt)

    def test_hash_failure_clean_chain(self):
        with patch.object(candidate_guard.hashlib, "sha256", side_effect=self.private_error(ValueError)):
            with self.assertRaises(CandidateGuardError) as e:
                sha256_candidate(self.exe)
        self.assert_public(e.exception, "Unable to read candidate payload safely")

    def test_fstat_failure_clean_chain(self):
        with patch.object(candidate_guard.os, "fstat", side_effect=self.private_error()):
            with self.assertRaises(CandidateGuardError) as e:
                sha256_candidate(self.exe)
        self.assert_public(e.exception, "Unable to read candidate payload safely")

    def test_six_executable_hashes_unchanged(self):
        for name in EXES:
            with self.subTest(name=name):
                self.assertEqual(sha256_candidate(self.root / name), hashlib.sha256(self.originals[name]).hexdigest())

    def test_manifest_bytes_unchanged(self):
        self.assertEqual(read_checksum_candidate(self.manifest), self.originals[self.manifest.name])

    def test_seven_file_directory_still_accepted(self):
        check_candidate_directory(self.root, EXES)

    def test_unapproved_file_still_rejected(self):
        (self.root / "private-premium-key.txt").write_bytes(b"synthetic")
        with self.assertRaises(CandidateGuardError) as e:
            check_candidate_directory(self.root, EXES)
        self.assert_public(e.exception, "Candidate directory has missing or unapproved payloads")

    def test_oversize_still_rejected(self):
        with self.assertRaises(CandidateGuardError) as e:
            sha256_candidate(self.exe, maximum=3)
        self.assert_public(e.exception, "Candidate payload exceeds the safety limit")


if __name__ == "__main__":
    unittest.main()
