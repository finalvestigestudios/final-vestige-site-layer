"""R102: cross-API Windows ctime parity without weakening local-first source custody.

All fixtures synthetic; no finance data, no entitlement decisions, no release.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import hashlib
import tempfile
import unittest

from fvs_suite import csv_snapshot
import candidate_guard


MODULES = (csv_snapshot, candidate_guard)


def fake_stat(**changes):
    data = dict(st_dev=1, st_ino=101, st_size=6,
                st_mtime_ns=1234567, st_ctime_ns=9876543)
    data.update(changes)
    return SimpleNamespace(**data)


class WindowsDescriptorCtimeParityR102(unittest.TestCase):
    """Exercise both independently protected descriptor-reading paths."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="fvs-r102-synthetic-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_identical_views_accepted_on_both_platforms(self):
        for module in MODULES:
            with self.subTest(module=module.__name__):
                self.assertTrue(module._same_path_descriptor_signature(
                    fake_stat(), fake_stat(), windows=False))
                self.assertTrue(module._same_path_descriptor_signature(
                    fake_stat(), fake_stat(), windows=True))

    def test_windows_creation_time_difference_only_is_accepted(self):
        for module in MODULES:
            with self.subTest(module=module.__name__):
                self.assertTrue(module._same_path_descriptor_signature(
                    fake_stat(st_ctime_ns=100),
                    fake_stat(st_ctime_ns=200), windows=True))

    def test_linux_creation_time_difference_still_rejected(self):
        for module in MODULES:
            with self.subTest(module=module.__name__):
                self.assertFalse(module._same_path_descriptor_signature(
                    fake_stat(st_ctime_ns=100),
                    fake_stat(st_ctime_ns=200), windows=False))

    def test_windows_inode_substitution_rejected(self):
        for module in MODULES:
            with self.subTest(module=module.__name__):
                self.assertFalse(module._same_path_descriptor_signature(
                    fake_stat(), fake_stat(st_ino=102), windows=True))

    def test_windows_device_substitution_rejected(self):
        for module in MODULES:
            with self.subTest(module=module.__name__):
                self.assertFalse(module._same_path_descriptor_signature(
                    fake_stat(), fake_stat(st_dev=2), windows=True))

    def test_windows_size_change_rejected(self):
        for module in MODULES:
            with self.subTest(module=module.__name__):
                self.assertFalse(module._same_path_descriptor_signature(
                    fake_stat(), fake_stat(st_size=7), windows=True))

    def test_windows_mtime_change_rejected(self):
        for module in MODULES:
            with self.subTest(module=module.__name__):
                self.assertFalse(module._same_path_descriptor_signature(
                    fake_stat(), fake_stat(st_mtime_ns=222), windows=True))

    def test_windows_two_simultaneous_changes_rejected(self):
        for module in MODULES:
            with self.subTest(module=module.__name__):
                self.assertFalse(module._same_path_descriptor_signature(
                    fake_stat(), fake_stat(st_ctime_ns=200, st_ino=102),
                    windows=True))

    def test_same_view_creation_time_change_remains_detectable(self):
        # Code compares complete path-to-path and fd-to-fd signatures.
        for module in MODULES:
            with self.subTest(module=module.__name__):
                self.assertNotEqual(module._signature(fake_stat(st_ctime_ns=1)),
                                    module._signature(fake_stat(st_ctime_ns=2)))

    def test_same_view_mtime_change_remains_detectable(self):
        for module in MODULES:
            with self.subTest(module=module.__name__):
                self.assertNotEqual(module._signature(fake_stat(st_mtime_ns=1)),
                                    module._signature(fake_stat(st_mtime_ns=2)))

    def test_real_csv_descriptor_snapshot(self):
        source = self.root / "records.csv"
        data = b"id,amount\nA,10\n"
        source.write_bytes(data)
        self.assertEqual(csv_snapshot.read_csv_snapshot(source, maximum=128), data)
        self.assertEqual(source.read_bytes(), data)

    def test_real_candidate_descriptor_sha_and_checksum(self):
        candidate = self.root / "LedgerDiffLite.exe"
        payload = b"MZ" + b"x" * 32
        candidate.write_bytes(payload)
        self.assertEqual(candidate_guard.sha256_candidate(candidate),
                         hashlib.sha256(payload).hexdigest())
        checksum = self.root / "SHA256SUMS.txt"
        checksum.write_bytes(b"abc\n")
        self.assertEqual(candidate_guard.read_checksum_candidate(checksum), b"abc\n")

    def test_csv_late_path_ctime_mutation_still_rejected(self):
        source = self.root / "records.csv"
        source.write_bytes(b"id,amount\nA,10\n")
        original = csv_snapshot._metadata
        calls = 0
        def simulate_path_change(path):
            nonlocal calls
            calls += 1
            info = original(path)
            if calls == 2:
                return fake_stat(st_dev=info.st_dev, st_ino=info.st_ino,
                    st_size=info.st_size, st_mtime_ns=info.st_mtime_ns,
                    st_ctime_ns=info.st_ctime_ns + 1, st_mode=info.st_mode)
            return info
        with patch.object(csv_snapshot, "_metadata", side_effect=simulate_path_change):
            with self.assertRaisesRegex(ValueError, "path changed"):
                csv_snapshot.read_csv_snapshot(source, maximum=128)
        self.assertEqual(calls, 2)

    def test_candidate_late_path_ctime_mutation_still_rejected(self):
        source = self.root / "LedgerDiffLite.exe"
        source.write_bytes(b"MZsynthetic")
        original = candidate_guard._ordinary
        calls = 0
        def simulate_path_change(path, maximum):
            nonlocal calls
            calls += 1
            info = original(path, maximum)
            if calls == 2:
                return fake_stat(st_dev=info.st_dev, st_ino=info.st_ino,
                    st_size=info.st_size, st_mtime_ns=info.st_mtime_ns,
                    st_ctime_ns=info.st_ctime_ns + 1, st_mode=info.st_mode,
                    st_nlink=info.st_nlink)
            return info
        with patch.object(candidate_guard, "_ordinary", side_effect=simulate_path_change):
            with self.assertRaisesRegex(candidate_guard.CandidateGuardError, "path changed"):
                candidate_guard.sha256_candidate(source)
        self.assertEqual(calls, 2)

    def test_csv_maximum_still_enforced(self):
        source = self.root / "too_large.csv"
        source.write_bytes(b"id,amount\nA,10\n")
        with self.assertRaisesRegex(ValueError, "file-size limit"):
            csv_snapshot.read_csv_snapshot(source, maximum=2)

    def test_candidate_hardlink_still_rejected(self):
        import os
        source = self.root / "LedgerDiffLite.exe"
        alias = self.root / "InvoiceTwinScout.exe"
        source.write_bytes(b"MZsynthetic")
        try:
            os.link(source, alias)
        except OSError:
            self.skipTest("hardlinks unsupported")
        with self.assertRaises(candidate_guard.CandidateGuardError):
            candidate_guard.sha256_candidate(source)


if __name__ == "__main__":
    unittest.main()
