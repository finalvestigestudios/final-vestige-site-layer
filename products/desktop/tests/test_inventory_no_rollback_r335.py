"""R335: failed six-app checksum publication is preserved, never pathname-unlinked.

Synthetic local bytes only; no real executables, premium files, distribution,
malware claims, financial records or compliance decisions.
"""
from __future__ import annotations

import errno
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_inventory as inv


class NoAutomaticManifestRollbackR335(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r335-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "dist"
        self.root.mkdir()
        self.data = {}
        for i, name in enumerate(inv.EXPECTED):
            blob = b"MZ-SYNTHETIC-NOT-EXE-" + bytes([i + 1]) * (20 + i)
            (self.root / name).write_bytes(blob)
            self.data[name] = blob
        self.target = self.root / inv.MANIFEST

    def canonical(self):
        return b"".join(hashlib.sha256(self.data[name]).hexdigest().encode("ascii")
                        + b"  " + name.encode("ascii") + b"\n"
                        for name in inv.EXPECTED)

    def assert_no_staging_or_source_edits(self):
        self.assertEqual([p for p in self.root.iterdir()
                          if p.name.startswith(".fvs-inventory-")], [])
        for name, data in self.data.items():
            self.assertEqual((self.root / name).read_bytes(), data)

    def test_postpublication_guard_rejection_preserves_exact_evidence(self):
        with patch.object(inv, "check_candidate_directory",
                          side_effect=inv.CandidateGuardError("private path")):
            with self.assertRaises(inv.InventoryBuildError) as caught:
                inv.build_inventory(self.root)
        self.assertEqual(self.target.read_bytes(), self.canonical())
        self.assertNotIn(str(self.root), str(caught.exception))
        self.assert_no_staging_or_source_edits()

    def test_postlink_error_after_actual_hardlink_keeps_evidence(self):
        real_link = os.link
        def linked_then_raises(stage, output):
            real_link(stage, output)
            raise OSError(errno.EIO, "secret private path", str(self.root))
        with patch("build_inventory.os.link", side_effect=linked_then_raises):
            with self.assertRaises(inv.InventoryBuildError) as caught:
                inv.build_inventory(self.root)
        self.assertEqual(self.target.read_bytes(), self.canonical())
        self.assertNotIn(str(self.root), str(caught.exception))
        self.assert_no_staging_or_source_edits()

    def test_postlink_keyboard_interrupt_keeps_evidence(self):
        real_link = os.link
        def linked_then_interrupt(stage, output):
            real_link(stage, output)
            raise KeyboardInterrupt()
        with patch("build_inventory.os.link", side_effect=linked_then_interrupt):
            with self.assertRaises(KeyboardInterrupt):
                inv.build_inventory(self.root)
        self.assertEqual(self.target.read_bytes(), self.canonical())
        self.assert_no_staging_or_source_edits()

    def test_postlink_system_exit_keeps_evidence(self):
        real_link = os.link
        def linked_then_exit(stage, output):
            real_link(stage, output)
            raise SystemExit(71)
        with patch("build_inventory.os.link", side_effect=linked_then_exit):
            with self.assertRaises(SystemExit) as caught:
                inv.build_inventory(self.root)
        self.assertEqual(caught.exception.code, 71)
        self.assertEqual(self.target.read_bytes(), self.canonical())
        self.assert_no_staging_or_source_edits()

    def test_postlink_lstat_error_leaves_evidence_without_retry_unlink(self):
        real_lstat = Path.lstat
        attempts = []
        def lstat(path, *args, **kwargs):
            if path == self.target:
                attempts.append(1)
                raise PermissionError(errno.EACCES, "private path", str(self.root))
            return real_lstat(path, *args, **kwargs)
        with patch.object(Path, "lstat", autospec=True, side_effect=lstat):
            with self.assertRaises(inv.InventoryBuildError):
                inv.build_inventory(self.root)
        self.assertEqual(len(attempts), 1)
        self.assertEqual(self.target.read_bytes(), self.canonical())
        self.assert_no_staging_or_source_edits()

    def test_no_postpublication_target_unlink_is_attempted(self):
        real_unlink = Path.unlink
        calls = []
        def guarded_unlink(path, *args, **kwargs):
            if path == self.target:
                calls.append(1)
                raise AssertionError("unsafe check-then-unlink of published pathname")
            return real_unlink(path, *args, **kwargs)
        with patch.object(inv, "check_candidate_directory",
                          side_effect=inv.CandidateGuardError("reject")):
            with patch.object(Path, "unlink", autospec=True, side_effect=guarded_unlink):
                with self.assertRaises(inv.InventoryBuildError):
                    inv.build_inventory(self.root)
        self.assertEqual(calls, [])
        self.assertEqual(self.target.read_bytes(), self.canonical())
        self.assert_no_staging_or_source_edits()

    def test_foreign_regular_replacement_is_not_deleted(self):
        real_link = os.link
        marker = b"independent financial-evidence marker"
        def link_then_swap(stage, output):
            real_link(stage, output)
            os.unlink(output)
            Path(output).write_bytes(marker)
        with patch("build_inventory.os.link", side_effect=link_then_swap):
            with self.assertRaises(inv.InventoryBuildError):
                inv.build_inventory(self.root)
        self.assertEqual(self.target.read_bytes(), marker)
        self.assert_no_staging_or_source_edits()

    def test_foreign_symlink_replacement_is_not_deleted(self):
        real_link = os.link
        external = self.root.parent / "external.txt"
        external.write_text("untouched", encoding="utf-8")
        def link_then_symlink(stage, output):
            real_link(stage, output)
            os.unlink(output)
            os.symlink(external, output)
        with patch("build_inventory.os.link", side_effect=link_then_symlink):
            with self.assertRaises(inv.InventoryBuildError):
                inv.build_inventory(self.root)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(external.read_text(encoding="utf-8"), "untouched")
        self.assert_no_staging_or_source_edits()

    def test_prelink_error_has_no_published_inventory(self):
        with patch("build_inventory.os.link",
                   side_effect=PermissionError(errno.EACCES, "private path")):
            with self.assertRaises(inv.InventoryBuildError):
                inv.build_inventory(self.root)
        self.assertFalse(self.target.exists())
        self.assert_no_staging_or_source_edits()

    def test_explicit_review_cleanup_required_before_retry(self):
        with patch.object(inv, "check_candidate_directory",
                          side_effect=inv.CandidateGuardError("review hold")):
            with self.assertRaises(inv.InventoryBuildError):
                inv.build_inventory(self.root)
        evidence = self.target.read_bytes()
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(self.root)
        self.assertEqual(self.target.read_bytes(), evidence)
        # An operator has to review and explicitly retire failed evidence.
        self.target.unlink()
        self.assertEqual(inv.build_inventory(self.root), inv.MANIFEST)
        self.assertEqual(self.target.read_bytes(), evidence)
        self.assert_no_staging_or_source_edits()


if __name__ == "__main__":
    unittest.main()
