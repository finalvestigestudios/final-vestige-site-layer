"""R104: guarded Windows .exe stat-mode parity, synthetic mutation coverage.

The .exe suffix may add executable bits in Windows pathname stat but not in
opened descriptor stat. These tests never run, install or publish an EXE.
"""
from __future__ import annotations

import stat
from types import SimpleNamespace
import unittest

from scripts.toolchain_guard import _same_path_descriptor_identity


class WindowsExecutableModeR104(unittest.TestCase):
    def setUp(self):
        self.base = dict(st_dev=4, st_ino=11, st_mode=stat.S_IFREG | 0o666,
                         st_nlink=1, st_size=512, st_mtime_ns=123,
                         st_ctime_ns=321)

    def view(self, **changes):
        return SimpleNamespace(**{**self.base, **changes})

    def compare(self, descriptor_changes=None, *, windows=True, exe=True):
        return _same_path_descriptor_identity(
            self.view(),
            self.view(**(descriptor_changes or {})),
            windows=windows, executable_path=exe)

    def test_exact_identity_passes_for_executable(self):
        self.assertTrue(self.compare())

    def test_windows_exe_allows_only_executable_permission_bits(self):
        self.assertTrue(self.compare({"st_mode": self.base["st_mode"] ^ 0o111}))

    def test_non_executable_file_still_rejects_mode_drift(self):
        self.assertFalse(self.compare({"st_mode": self.base["st_mode"] ^ 0o111},
                                      exe=False))

    def test_posix_still_rejects_executable_bit_drift(self):
        self.assertFalse(self.compare({"st_mode": self.base["st_mode"] ^ 0o111},
                                      windows=False))

    def test_write_permission_change_is_never_ignored(self):
        self.assertFalse(self.compare({"st_mode": self.base["st_mode"] ^ stat.S_IWUSR}))

    def test_directory_or_symlink_type_change_never_admitted(self):
        for replacement in (stat.S_IFDIR, stat.S_IFLNK):
            with self.subTest(replacement=replacement):
                self.assertFalse(self.compare({"st_mode": replacement | 0o666}))

    def test_inode_substitution_rejected(self):
        self.assertFalse(self.compare({"st_ino": 99}))

    def test_hardlink_count_change_rejected(self):
        self.assertFalse(self.compare({"st_nlink": 2}))

    def test_file_size_drift_rejected(self):
        self.assertFalse(self.compare({"st_size": 513}))

    def test_mtime_drift_rejected(self):
        self.assertFalse(self.compare({"st_mtime_ns": 124}))

    def test_device_swap_rejected(self):
        self.assertFalse(self.compare({"st_dev": 5}))

    def test_windows_ctime_difference_still_cross_view_only(self):
        self.assertTrue(self.compare({"st_ctime_ns": 999}))
        self.assertFalse(self.compare({"st_ctime_ns": 999}, windows=False))


if __name__ == "__main__":
    unittest.main()
