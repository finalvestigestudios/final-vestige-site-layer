"""R116 path-origin tests: synthetic; Windows native known-folder smoke only."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import trusted_defender_install_r116 as roots


class TrustedDefenderInstallR116(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.data = self.base / "ProgramData"
        self.files = self.base / "Program Files"
        self.data.mkdir()
        self.files.mkdir()
        self.modern = self.data / "Microsoft" / "Windows Defender" / "Platform" / "4.18.25010.11" / "MpCmdRun.exe"
        self.legacy = self.files / "Windows Defender" / "MpCmdRun.exe"
        for exe in (self.modern, self.legacy):
            exe.parent.mkdir(parents=True)
            exe.write_bytes(b"MZ synthetic path selection, NOT signed")

    def test_modern_platform_path(self):
        self.assertEqual(roots.require_candidate(self.modern, self.data, self.files), self.modern)

    def test_legacy_path(self):
        self.assertEqual(roots.require_candidate(self.legacy, self.data, self.files), self.legacy)

    def test_bogus_programfiles_or_data_environment_cannot_redirect_roots(self):
        with patch.object(roots, "_known_folder", side_effect=[self.data, self.files]), \
             patch.dict(os.environ, {"ProgramData": str(self.base / "attacker"),
                                  "ProgramFiles": str(self.base / "attacker")}, clear=False):
            self.assertEqual(roots.native_roots(), (self.data, self.files))

    def test_non_windows_native_known_folder_is_denied(self):
        with patch.object(roots.os, "name", "posix"):
            with self.assertRaises(roots.InstallHold):
                roots._known_folder(roots.PROGRAM_DATA)

    def test_invalid_folder_guid_and_native_calls_cannot_create_nonwin_success(self):
        with patch.object(roots.os, "name", "posix"):
            with self.assertRaises(roots.InstallHold):
                roots._known_folder("not-a-guid")

    def test_identical_roots_denied(self):
        with patch.object(roots, "_known_folder", return_value=self.data):
            with self.assertRaises(roots.InstallHold):
                roots.native_roots()

    def test_missing_root_denied(self):
        with patch.object(roots, "_known_folder", side_effect=[self.data, self.base / "missing"]):
            with self.assertRaises(roots.InstallHold):
                roots.native_roots()

    def test_wrong_filename_denied(self):
        candidate = self.modern.with_name("not-defender.exe")
        candidate.write_bytes(b"MZ")
        with self.assertRaises(roots.InstallHold):
            roots.require_candidate(candidate, self.data, self.files)

    def test_wrong_install_layout_denied(self):
        candidate = self.data / "MpCmdRun.exe"
        candidate.write_bytes(b"MZ")
        with self.assertRaises(roots.InstallHold):
            roots.require_candidate(candidate, self.data, self.files)

    def test_nonversion_platform_subfolder_denied(self):
        odd = self.modern.parent.parent / "not-a-version" / "MpCmdRun.exe"
        odd.parent.mkdir()
        odd.write_bytes(b"MZ")
        with self.assertRaises(roots.InstallHold):
            roots.require_candidate(odd, self.data, self.files)

    def test_relative_scanner_denied(self):
        with self.assertRaises(roots.InstallHold):
            roots.require_candidate(Path("MpCmdRun.exe"), self.data, self.files)

    def test_non_file_and_missing_scanner_denied(self):
        self.modern.unlink()
        with self.assertRaises(roots.InstallHold):
            roots.require_candidate(self.modern, self.data, self.files)

    def test_reparse_linked_scanner_denied(self):
        target = self.base / "synthetic-target.exe"
        target.write_bytes(b"MZ")
        self.modern.unlink()
        try:
            self.modern.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        with self.assertRaises(roots.InstallHold):
            roots.require_candidate(self.modern, self.data, self.files)

    def test_reparse_parent_folder_denied(self):
        source = self.modern.parent
        other = self.base / "other-folder"
        other.mkdir()
        source.joinpath("MpCmdRun.exe").unlink()
        source.rmdir()
        try:
            source.symlink_to(other, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("directory symlink unavailable")
        (other / "MpCmdRun.exe").write_bytes(b"MZ")
        with self.assertRaises(roots.InstallHold):
            roots.require_candidate(self.modern, self.data, self.files)

    def test_nonlinked_ancestor_root_required(self):
        self.assertEqual(roots._root(self.data), self.data)
        with self.assertRaises(roots.InstallHold):
            roots._root(self.base / "missing")

    def test_native_guid_binary_order(self):
        from uuid import UUID
        value = roots._GUID.from_buffer_copy(UUID(roots.PROGRAM_DATA).bytes_le)
        self.assertEqual(value.Data1, 0x62ab5d82)
        self.assertEqual(value.Data2, 0xfdc1)
        self.assertEqual(value.Data3, 0x4dc3)
        self.assertEqual(bytes(value.Data4), bytes.fromhex("a9dd070d1d495d97"))

    @unittest.skipUnless(os.name == "nt", "Real Windows known-folder call only on Windows")
    def test_real_windows_known_folder_api_returns_two_directories(self):
        data, files = roots.native_roots()
        self.assertTrue(data.is_dir())
        self.assertTrue(files.is_dir())
        self.assertNotEqual(data, files)


if __name__ == "__main__":
    unittest.main()
