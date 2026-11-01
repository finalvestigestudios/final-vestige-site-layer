"""R104 regression tests for cross-platform simulated filesystem race evidence.

The tests run on Linux and Windows but never mutate customer data or publish
candidate files. The mock targets only one synthetic path and is activated
after first observation to exercise real custody gates deterministically.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from synthetic_windows_fs_r104 import STAT_FIELDS, changed_stat, altered_lstat


class WindowsSafeRaceFixtureR104(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fvs-r104-synthetic-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.target = root / "review.jsonl"
        self.neighbor = root / "other.jsonl"
        self.target.write_bytes(b'{"review":"example"}\n')
        self.neighbor.write_bytes(b"unrelated\n")

    def test_synthetic_inode_drift_preserves_every_other_security_field(self):
        original = self.target.lstat()
        changed = changed_stat(original)
        self.assertEqual(changed.st_ino, original.st_ino + 1)
        for name in STAT_FIELDS:
            if name != "st_ino":
                self.assertEqual(getattr(changed, name), getattr(original, name))

    def test_synthetic_size_drift_preserves_other_fields(self):
        original = self.target.lstat()
        changed = changed_stat(original, "st_size")
        self.assertEqual(changed.st_size, original.st_size + 1)
        for name in STAT_FIELDS:
            if name != "st_size":
                self.assertEqual(getattr(changed, name), getattr(original, name))

    def test_unknown_security_field_is_refused(self):
        with self.assertRaises(ValueError):
            changed_stat(self.target.lstat(), "private_arbitrary_field")

    def test_inactive_spoof_returns_real_stat(self):
        original_lstat = os.lstat
        state = {"active": False}
        with patch("synthetic_windows_fs_r104.os.lstat",
                   side_effect=altered_lstat(self.target, state, original_lstat)):
            self.assertEqual(os.lstat(self.target).st_ino, original_lstat(self.target).st_ino)

    def test_active_spoof_changes_target_only_and_never_file_bytes(self):
        original_lstat = os.lstat
        state = {"active": True}
        with patch("synthetic_windows_fs_r104.os.lstat",
                   side_effect=altered_lstat(self.target, state, original_lstat)):
            self.assertNotEqual(os.lstat(self.target).st_ino, original_lstat(self.target).st_ino)
            self.assertEqual(os.lstat(self.neighbor).st_ino, original_lstat(self.neighbor).st_ino)
        self.assertEqual(self.target.read_bytes(), b'{"review":"example"}\n')
        self.assertEqual(self.neighbor.read_bytes(), b"unrelated\n")

    def test_missing_path_is_observation_only(self):
        original_lstat = os.lstat
        state = {"active": True}
        with patch("synthetic_windows_fs_r104.os.lstat",
                   side_effect=altered_lstat(self.target, state, original_lstat, missing=True)):
            with self.assertRaises(FileNotFoundError):
                os.lstat(self.target)
            self.assertEqual(os.lstat(self.neighbor).st_ino, original_lstat(self.neighbor).st_ino)
        self.assertTrue(self.target.is_file())
        self.assertEqual(self.target.read_bytes(), b'{"review":"example"}\n')


if __name__ == "__main__":
    unittest.main()
