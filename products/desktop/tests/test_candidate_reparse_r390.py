"""R390: source-owned Windows non-symlink reparse protections, simulated on Linux.

Native Windows/Defender testing is still required; no test here proves a binary
safe to launch or authorizes distribution.
"""
from __future__ import annotations

import hashlib
import os
import stat
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import candidate_guard
from candidate_guard import CandidateGuardError
from candidate_reparse_r390 import unsafe_windows_reparse


class _IntSubclass(int):
    def __and__(self, other):
        raise AssertionError("untrusted bitwise hook executed")


class _AttributeTrap:
    def __init__(self):
        self.lookups = 0

    @property
    def st_file_attributes(self):
        self.lookups += 1
        raise OSError("PRIVATE_CLIENT_PATH_DO_NOT_DISCLOSE")


class WindowsReparseFlagTests(unittest.TestCase):
    def test_plain_windows_file(self):
        self.assertFalse(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=0), on_windows=True))

    def test_windows_archive_flag(self):
        self.assertFalse(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=0x20), on_windows=True))

    def test_windows_readonly_flag(self):
        self.assertFalse(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=0x1), on_windows=True))

    def test_windows_hidden_system_flags(self):
        self.assertFalse(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=0x6), on_windows=True))

    def test_windows_reparse_flag_alone(self):
        self.assertTrue(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=0x400), on_windows=True))

    def test_windows_reparse_with_archive(self):
        self.assertTrue(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=0x420), on_windows=True))

    def test_windows_reparse_with_directory(self):
        self.assertTrue(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=0x410), on_windows=True))

    def test_windows_reparse_with_other_flags(self):
        self.assertTrue(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=0x24400), on_windows=True))

    def test_missing_windows_attributes(self):
        self.assertTrue(unsafe_windows_reparse(SimpleNamespace(), on_windows=True))

    def test_none_windows_attributes(self):
        self.assertTrue(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=None), on_windows=True))

    def test_boolean_windows_attributes(self):
        self.assertTrue(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=False), on_windows=True))

    def test_string_windows_attributes(self):
        self.assertTrue(unsafe_windows_reparse(SimpleNamespace(st_file_attributes="0"), on_windows=True))

    def test_int_subclass_does_not_execute_bitwise_hook(self):
        self.assertTrue(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=_IntSubclass(0)), on_windows=True))

    def test_float_windows_attributes(self):
        self.assertTrue(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=0.0), on_windows=True))

    def test_faulting_attribute_is_redacted_and_rejected(self):
        trap = _AttributeTrap()
        self.assertTrue(unsafe_windows_reparse(trap, on_windows=True))
        self.assertEqual(trap.lookups, 1)

    def test_posix_does_not_query_malicious_attribute(self):
        trap = _AttributeTrap()
        self.assertFalse(unsafe_windows_reparse(trap, on_windows=False))
        self.assertEqual(trap.lookups, 0)

    def test_missing_posix_attributes_not_a_windows_flag(self):
        self.assertFalse(unsafe_windows_reparse(SimpleNamespace(), on_windows=False))

    def test_invalid_platform_type_fails_closed(self):
        self.assertTrue(unsafe_windows_reparse(SimpleNamespace(st_file_attributes=0), on_windows="nt"))

    def test_actual_os_policy_preserves_native_posix(self):
        if os.name == "nt":
            self.skipTest("POSIX-only platform observation")
        with tempfile.NamedTemporaryFile() as stream:
            self.assertFalse(unsafe_windows_reparse(os.stat(stream.name)))


class ReleaseCandidateIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.candidate = self.root / "LedgerDiff-Lite.exe"
        self.candidate.write_bytes(b"SAFE SYNTHETIC FIXTURE - NOT A WINDOWS EXE")

    def test_real_file_sha256_still_works(self):
        expected = hashlib.sha256(self.candidate.read_bytes()).hexdigest()
        self.assertEqual(candidate_guard.sha256_candidate(self.candidate), expected)

    def test_ordinary_path_reparse_rejected_before_file_open(self):
        with patch.object(candidate_guard, "unsafe_windows_reparse", return_value=True):
            with patch.object(candidate_guard.os, "open", side_effect=AssertionError("opened")):
                with self.assertRaisesRegex(CandidateGuardError, "reparse"):
                    candidate_guard.sha256_candidate(self.candidate)

    def test_descriptor_reparse_rejected_before_payload_read(self):
        with patch.object(candidate_guard, "unsafe_windows_reparse", side_effect=[False, True]):
            with patch.object(candidate_guard, "_read_chunks", side_effect=AssertionError("read")):
                with self.assertRaisesRegex(CandidateGuardError, "reparse"):
                    candidate_guard.sha256_candidate(self.candidate)

    def test_changed_descriptor_to_reparse_during_read(self):
        with patch.object(candidate_guard, "unsafe_windows_reparse", side_effect=[False, False, True]):
            with self.assertRaisesRegex(CandidateGuardError, "reparse"):
                candidate_guard.sha256_candidate(self.candidate)

    def test_final_path_reparse_rejected(self):
        with patch.object(candidate_guard, "unsafe_windows_reparse", side_effect=[False, False, False, True]):
            with self.assertRaisesRegex(CandidateGuardError, "reparse"):
                candidate_guard.sha256_candidate(self.candidate)

    def test_staging_directory_reparse_rejected_before_children(self):
        with patch.object(candidate_guard, "unsafe_windows_reparse", return_value=True):
            with self.assertRaisesRegex(CandidateGuardError, "reparse"):
                candidate_guard.check_candidate_directory(self.root, ("LedgerDiff-Lite.exe",))

    def test_forged_windows_path_attributes_are_checked(self):
        original = unsafe_windows_reparse
        with patch.object(candidate_guard, "unsafe_windows_reparse", side_effect=lambda info: original(info, on_windows=True)):
            native = self.candidate.lstat()
            fake = SimpleNamespace(st_mode=native.st_mode, st_nlink=native.st_nlink,
                                   st_size=native.st_size, st_file_attributes=0x400)
            with patch.object(Path, "lstat", return_value=fake):
                with self.assertRaisesRegex(CandidateGuardError, "reparse"):
                    candidate_guard.sha256_candidate(self.candidate)

    def test_no_candidate_mutation_on_reparse_rejection(self):
        before = self.candidate.read_bytes()
        with patch.object(candidate_guard, "unsafe_windows_reparse", return_value=True):
            with self.assertRaises(CandidateGuardError):
                candidate_guard.sha256_candidate(self.candidate)
        self.assertEqual(self.candidate.read_bytes(), before)

    def test_native_regular_staging_directory_still_passes(self):
        (self.root / "SHA256SUMS.txt").write_text("synthetic checksum placeholder\n", encoding="ascii")
        self.assertIsNone(candidate_guard.check_candidate_directory(self.root, ("LedgerDiff-Lite.exe",)))


if __name__ == "__main__":
    unittest.main()
