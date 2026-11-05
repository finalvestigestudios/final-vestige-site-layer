"""R204: deterministic Policy Delta link-control witness, never a silent skip.

Native symlink rejection is exercised where the OS permits it. When Windows
denies link creation, a metadata-only stand-in still tests the production
reader's fail-closed lstat guard. A simulated pass is NOT native Windows
security qualification; separate physical acceptance remains mandatory.
"""
from __future__ import annotations

import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import test_policy_real_file_matrix_r197 as r197


class PolicySymlinkWitnessR204(unittest.TestCase):
    def _run_with_blocked_symlinks(self, failure):
        case = r197.PolicyRealFileMatrixR197(
            "test_source_symlink_cannot_be_published")
        observed = unittest.TestResult()
        with patch.object(Path, "symlink_to", side_effect=failure):
            case.run(observed)
        self.assertEqual(observed.skipped, [])
        self.assertEqual(observed.errors, [])
        self.assertEqual(observed.failures, [])
        self.assertEqual(observed.testsRun, 1)
        self.assertTrue(observed.wasSuccessful())
        self.assertIs(case._native_link_verified, False)

    def test_symlink_privilege_denied_uses_guard_without_skip(self):
        self._run_with_blocked_symlinks(
            PermissionError("synthetic access denied"))

    def test_symlink_unimplemented_uses_guard_without_skip(self):
        self._run_with_blocked_symlinks(
            NotImplementedError("synthetic absent"))

    def test_link_witness_marks_only_selected_path(self):
        with tempfile.TemporaryDirectory() as location:
            first = Path(location) / "first.txt"
            second = Path(location) / "second.txt"
            first.write_text("a", encoding="utf-8")
            second.write_text("b", encoding="utf-8")
            source_lstat = Path.lstat
            marked = r197._linked_metadata_witness_r204(
                first, source_lstat, first)
            other = r197._linked_metadata_witness_r204(
                second, source_lstat, first)
            self.assertTrue(stat.S_ISLNK(marked.st_mode))
            self.assertTrue(stat.S_ISREG(other.st_mode))
            self.assertEqual(second.lstat().st_ino, other.st_ino)

    def test_native_policy_link_rejection_or_documented_fallback(self):
        case = r197.PolicyRealFileMatrixR197(
            "test_source_symlink_cannot_be_published")
        observed = unittest.TestResult()
        case.run(observed)
        self.assertTrue(observed.wasSuccessful())
        self.assertFalse(observed.skipped)
        self.assertEqual(observed.testsRun, 1)
        self.assertIn(case._native_link_verified, (True, False))


if __name__ == "__main__":
    unittest.main()
