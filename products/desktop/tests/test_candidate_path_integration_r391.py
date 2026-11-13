"""R391 integration with the exact shared six-app candidate custody reader.

All payloads are synthetic bytes, never Windows executables or customer data.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import candidate_guard
from candidate_guard import CandidateGuardError


class CandidateGuardAncestryIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.stage = self.root / "stage"
        self.stage.mkdir()
        self.exe = self.stage / "LedgerDiff-Lite.exe"
        self.exe.write_bytes(b"synthetic Windows x64 file name, NOT executable")
        self.sumfile = self.stage / "SHA256SUMS.txt"
        self.sumfile.write_bytes(b"synthetic checksum file")

    def _alias(self):
        alias = self.root / "alias"
        try:
            alias.symlink_to(self.stage, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("local filesystem symlinks unavailable")
        return alias

    def test_normal_candidate_sha256_unchanged(self):
        self.assertEqual(candidate_guard.sha256_candidate(self.exe),
                         hashlib.sha256(self.exe.read_bytes()).hexdigest())

    def test_normal_checksum_reader_unchanged(self):
        self.assertEqual(candidate_guard.read_checksum_candidate(self.sumfile),
                         self.sumfile.read_bytes())

    def test_normal_seven_file_membership_helper_remains_compatible(self):
        self.assertIsNone(candidate_guard.check_candidate_directory(
            self.stage, (self.exe.name,)))

    def test_sha256_rejects_symlink_parent_with_regular_final_file(self):
        alias = self._alias()
        with self.assertRaisesRegex(CandidateGuardError, "parent directory"):
            candidate_guard.sha256_candidate(alias / self.exe.name)

    def test_checksum_reader_rejects_symlink_parent(self):
        alias = self._alias()
        with self.assertRaises(CandidateGuardError):
            candidate_guard.read_checksum_candidate(alias / self.sumfile.name)

    def test_directory_check_rejects_symlink_parent(self):
        alias = self._alias()
        with self.assertRaises(CandidateGuardError):
            candidate_guard.check_candidate_directory(alias, (self.exe.name,))

    def test_directory_under_symlinked_ancestor_rejected(self):
        nested = self.stage / "nested"
        nested.mkdir()
        (nested / self.exe.name).write_bytes(self.exe.read_bytes())
        (nested / self.sumfile.name).write_bytes(self.sumfile.read_bytes())
        alias = self._alias()
        # The final directory is ordinary; an intermediate parent is a link.
        with self.assertRaises(CandidateGuardError):
            candidate_guard.check_candidate_directory(alias / "nested", (self.exe.name,))

    def test_child_of_symlinked_parent_does_not_open_bytes(self):
        alias = self._alias()
        with patch.object(candidate_guard.os, "open", side_effect=AssertionError("unsafe open")):
            with self.assertRaises(CandidateGuardError):
                candidate_guard.sha256_candidate(alias / self.exe.name)

    def test_lexical_parent_traversal_rejected_in_candidate_hash(self):
        with self.assertRaises(CandidateGuardError):
            candidate_guard.sha256_candidate(self.stage / "unused" / ".." / self.exe.name)

    def test_privacy_exception_chain_not_retained(self):
        with patch.object(Path, "lstat", side_effect=OSError("PRIVATE_CUSTOMER_EXPORT_PATH")):
            with self.assertRaises(CandidateGuardError) as cm:
                candidate_guard.sha256_candidate(self.exe)
        self.assertNotIn("PRIVATE_CUSTOMER", str(cm.exception))
        self.assertIsNone(cm.exception.__cause__)
        self.assertIsNone(cm.exception.__context__)

    def test_in_flight_directory_swapped_to_symlink_is_rejected(self):
        original = candidate_guard._read_chunks
        moved = self.root / "moved"
        def swap(stream):
            self.stage.rename(moved)
            try:
                self.stage.symlink_to(moved, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("local filesystem symlinks unavailable")
            yield from original(stream)
        with patch.object(candidate_guard, "_read_chunks", swap):
            with self.assertRaises(CandidateGuardError):
                candidate_guard.sha256_candidate(self.exe)

    def test_parent_replaced_after_listing_fails_directory_verification(self):
        original = candidate_guard._ordinary
        count = 0
        def mutate(path, maximum):
            nonlocal count
            value = original(path, maximum)
            count += 1
            if count == 2:
                moved = self.root / "moved"
                self.stage.rename(moved)
                self.stage.mkdir()
                self.exe.write_bytes(b"synthetic Windows x64 file name, NOT executable")
                self.sumfile.write_bytes(b"synthetic checksum file")
            return value
        with patch.object(candidate_guard, "_ordinary", mutate):
            with self.assertRaisesRegex(CandidateGuardError, "changed"):
                candidate_guard.check_candidate_directory(self.stage, (self.exe.name,))

    def test_rejection_never_deletes_original_candidate(self):
        original = self.exe.read_bytes()
        alias = self._alias()
        with self.assertRaises(CandidateGuardError):
            candidate_guard.sha256_candidate(alias / self.exe.name)
        self.assertEqual(self.exe.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
