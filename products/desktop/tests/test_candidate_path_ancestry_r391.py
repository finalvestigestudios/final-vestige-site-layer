"""R391: lexical parent custody; synthetic + local filesystem regression tests.

No tests here constitute a Windows x64 EXE, Defender, or release acceptance.
"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from candidate_path_ancestry_r391 import (
    UnsafeCandidateAncestry, snapshot_candidate_parents,
)


class CandidateAncestryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.stage = self.root / "stage"
        self.stage.mkdir()
        self.candidate = self.stage / "LedgerDiff-Lite.exe"
        self.candidate.write_bytes(b"SYNTHETIC ONLY")

    def test_regular_file_parents_are_captured(self):
        snapshot = snapshot_candidate_parents(self.candidate)
        self.assertTrue(snapshot)
        self.assertEqual(snapshot[-1][0], str(self.stage))
        self.assertTrue(all(type(x) is tuple for x in snapshot))

    def test_snapshot_repeat_is_deterministic(self):
        self.assertEqual(snapshot_candidate_parents(self.candidate),
                         snapshot_candidate_parents(self.candidate))

    def test_snapshots_do_not_include_private_file_name(self):
        snapshot = snapshot_candidate_parents(self.candidate)
        self.assertFalse(any("LedgerDiff-Lite.exe" in record[0] for record in snapshot))

    def test_relative_filename_uses_current_parent(self):
        with patch("os.getcwd", return_value=str(self.stage)):
            snapshot = snapshot_candidate_parents("LedgerDiff-Lite.exe")
        self.assertEqual(snapshot[-1][0], str(self.stage))

    def test_parent_symlink_is_rejected(self):
        alias = self.root / "alias"
        try:
            alias.symlink_to(self.stage, target_is_directory=True)
        except (NotImplementedError, OSError):
            self.skipTest("native symlink creation unavailable")
        with self.assertRaises(UnsafeCandidateAncestry):
            snapshot_candidate_parents(alias / self.candidate.name)

    def test_nested_parent_symlink_is_rejected(self):
        nested = self.stage / "nested"
        nested.mkdir()
        alias = self.root / "alias"
        try:
            alias.symlink_to(self.stage, target_is_directory=True)
        except (NotImplementedError, OSError):
            self.skipTest("native symlink creation unavailable")
        with self.assertRaises(UnsafeCandidateAncestry):
            snapshot_candidate_parents(alias / "nested" / "example.exe")

    def test_root_itself_as_candidate_has_ordinary_parent(self):
        self.assertEqual(snapshot_candidate_parents(self.stage)[-1][0], str(self.root))

    def test_absolute_parent_traversal_rejected(self):
        malicious = self.stage / "nested" / ".." / self.candidate.name
        with self.assertRaises(UnsafeCandidateAncestry):
            snapshot_candidate_parents(malicious)

    def test_relative_parent_traversal_rejected(self):
        with self.assertRaises(UnsafeCandidateAncestry):
            snapshot_candidate_parents("../LedgerDiff-Lite.exe")

    def test_nonexistent_ancestor_rejected_without_path_leak(self):
        secret = self.root / "PRIVATE_COMPANY_PAYROLL_DO_NOT_EXPOSE" / "a.exe"
        with self.assertRaises(UnsafeCandidateAncestry) as cm:
            snapshot_candidate_parents(secret)
        self.assertNotIn("PRIVATE_COMPANY", str(cm.exception))
        self.assertIsNone(cm.exception.__cause__)
        self.assertIsNone(cm.exception.__context__)

    def test_parent_file_is_rejected(self):
        with self.assertRaises(UnsafeCandidateAncestry):
            snapshot_candidate_parents(self.candidate / "nested.exe")

    def test_ancestor_replacement_changes_snapshot(self):
        previous = snapshot_candidate_parents(self.candidate)
        # Rename keeps old directory inode, then create a fresh directory.
        moved = self.root / "oldstage"
        self.stage.rename(moved)
        self.stage.mkdir()
        self.candidate.write_bytes(b"SYNTHETIC ONLY")
        self.assertNotEqual(previous, snapshot_candidate_parents(self.candidate))

    def test_parent_metadata_change_changes_snapshot(self):
        previous = snapshot_candidate_parents(self.candidate)
        os.utime(self.stage, ns=(self.stage.stat().st_atime_ns,
                                  self.stage.stat().st_mtime_ns - 1_000_000_000))
        self.assertNotEqual(previous, snapshot_candidate_parents(self.candidate))

    def test_snapshot_does_not_change_candidate(self):
        original = self.candidate.read_bytes()
        snapshot_candidate_parents(self.candidate)
        self.assertEqual(original, self.candidate.read_bytes())

    def test_os_error_has_no_private_context(self):
        private = "PRIVATE_ANCESTOR_NOT_FOR_LOGS"
        with patch.object(Path, "lstat", side_effect=OSError(private)):
            with self.assertRaises(UnsafeCandidateAncestry) as cm:
                snapshot_candidate_parents(self.candidate)
        self.assertNotIn(private, str(cm.exception))
        self.assertIsNone(cm.exception.__context__)
        self.assertIsNone(cm.exception.__cause__)

    def test_forged_reparse_ancestor_is_rejected(self):
        real = self.stage.lstat()
        reparse = SimpleNamespace(st_mode=real.st_mode,
                                  st_file_attributes=0x400)
        original_lstat = Path.lstat
        def fake_lstat(path):
            return reparse if path == self.stage else original_lstat(path)
        with patch.object(Path, "lstat", fake_lstat):
            with patch("candidate_path_ancestry_r391.unsafe_windows_reparse",
                       side_effect=lambda info: bool(getattr(info, "st_file_attributes", 0) & 0x400)):
                with self.assertRaises(UnsafeCandidateAncestry):
                    snapshot_candidate_parents(self.candidate)

    def test_file_ancestor_status_fails_closed(self):
        with self.assertRaises(UnsafeCandidateAncestry):
            snapshot_candidate_parents(self.candidate / "fake_child")

    def test_untrusted_path_class_exception_redacted(self):
        class Broken:
            def __fspath__(self):
                raise OSError("PRIVATE_FILE_PATH")
        with self.assertRaises(UnsafeCandidateAncestry) as cm:
            snapshot_candidate_parents(Broken())
        self.assertIsNone(cm.exception.__context__)

    def test_windows_simulation_reparse_bit_rejected(self):
        real = self.stage.lstat()
        modified = SimpleNamespace(st_mode=real.st_mode, st_file_attributes=0x400)
        with patch.object(Path, "lstat", return_value=modified):
            with patch("candidate_path_ancestry_r391.unsafe_windows_reparse", return_value=True):
                with self.assertRaises(UnsafeCandidateAncestry):
                    snapshot_candidate_parents(self.candidate)

    def test_parent_absolute_check_never_invokes_resolve(self):
        with patch.object(Path, "resolve", side_effect=AssertionError("must not follow")):
            snapshot_candidate_parents(self.candidate)


if __name__ == "__main__":
    unittest.main()
