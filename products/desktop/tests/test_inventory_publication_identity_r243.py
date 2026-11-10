"""R243: post-link manifest inode custody and non-destructive failed-build evidence.

Synthetic non-executable bytes only. Exercises real temporary files and links,
never builds, executes or distributes a Windows binary.
"""
from __future__ import annotations

import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_inventory as inv


class ManifestPublicationIdentityR243(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r243-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "dist"
        self.root.mkdir()
        self.originals = {}
        for index, name in enumerate(inv.EXPECTED):
            data = b"MZ-not-executable-" + bytes([index + 1]) * (31 + index)
            self.originals[name] = data
            (self.root / name).write_bytes(data)
        self.target = self.root / inv.MANIFEST

    def assert_sources_unchanged(self):
        for name, data in self.originals.items():
            self.assertEqual((self.root / name).read_bytes(), data)
        self.assertFalse(any(p.name.startswith(".fvs-inventory-")
                             for p in self.root.iterdir()))

    def fail_first_postlink_lstat(self, exc):
        """Inject exactly one fault AFTER the exclusive link becomes visible."""
        real_lstat = Path.lstat
        seen = []

        def wrapped(path, *args, **kwargs):
            if path == self.target and os.path.lexists(path):
                seen.append(str(path))
                if len(seen) == 1:
                    raise exc
            return real_lstat(path, *args, **kwargs)

        with patch.object(Path, "lstat", autospec=True, side_effect=wrapped):
            with self.assertRaises(inv.InventoryBuildError) as caught:
                inv.build_inventory(self.root)
        self.assertEqual(len(seen), 1, "no pathname-based rollback lstat")
        self.assertNotIn(str(self.root), str(caught.exception))
        self.assertNotIn("secret", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(self.target.is_file(), "preserve failed-build evidence")
        self.assert_sources_unchanged()

    def test_postlink_lstat_permission_error_rolls_back_only_own_manifest(self):
        self.fail_first_postlink_lstat(
            PermissionError(errno.EACCES, "secret customer folder", str(self.root)))

    def test_postlink_lstat_missing_error_rolls_back_only_own_manifest(self):
        self.fail_first_postlink_lstat(
            FileNotFoundError(errno.ENOENT, "secret customer folder", str(self.root)))

    def test_postlink_lstat_generic_io_failure_rolls_back(self):
        self.fail_first_postlink_lstat(OSError(errno.EIO, "secret customer folder", str(self.root)))

    def test_postlink_lstat_keyboard_interrupt_rolls_back_and_propagates(self):
        real_lstat = Path.lstat
        faults = []

        def wrapped(path, *args, **kwargs):
            if path == self.target and os.path.lexists(path):
                faults.append(1)
                if len(faults) == 1:
                    raise KeyboardInterrupt()
            return real_lstat(path, *args, **kwargs)

        with patch.object(Path, "lstat", autospec=True, side_effect=wrapped):
            with self.assertRaises(KeyboardInterrupt):
                inv.build_inventory(self.root)
        self.assertEqual(len(faults), 1)
        self.assertTrue(self.target.is_file())
        self.assert_sources_unchanged()

    def test_postlink_lstat_system_exit_rolls_back_and_propagates(self):
        real_lstat = Path.lstat
        faults = []

        def wrapped(path, *args, **kwargs):
            if path == self.target and os.path.lexists(path):
                faults.append(1)
                if len(faults) == 1:
                    raise SystemExit(51)
            return real_lstat(path, *args, **kwargs)

        with patch.object(Path, "lstat", autospec=True, side_effect=wrapped):
            with self.assertRaises(SystemExit) as caught:
                inv.build_inventory(self.root)
        self.assertEqual(caught.exception.code, 51)
        self.assertEqual(len(faults), 1)
        self.assertTrue(self.target.is_file())
        self.assert_sources_unchanged()

    def perform_link_swap(self, *, corrupt):
        """Model another writer replacing the new link before post-link lstat."""
        original_link = os.link
        replacement = b""

        def link_then_swap(stage, target, *args, **kwargs):
            nonlocal replacement
            original_link(stage, target, *args, **kwargs)
            content = Path(target).read_bytes()
            replacement = b"X" * len(content) if corrupt else content
            os.unlink(target)
            Path(target).write_bytes(replacement)  # distinct inode, third-party file

        with patch("build_inventory.os.link", side_effect=link_then_swap):
            with self.assertRaises(inv.InventoryBuildError) as caught:
                inv.build_inventory(self.root)
        self.assertNotIn(str(self.root), str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertEqual(self.target.read_bytes(), replacement,
                         "rollback deleted a file replacing our own link")
        self.assert_sources_unchanged()

    def test_same_bytes_different_inode_cannot_be_accepted(self):
        self.perform_link_swap(corrupt=False)

    def test_corrupted_replacement_cannot_be_deleted_by_rollback(self):
        self.perform_link_swap(corrupt=True)

    def test_symlink_replacement_is_not_removed(self):
        original_link = os.link
        secret = self.root.parent / "not-an-output.txt"
        secret.write_text("external evidence", encoding="utf-8")

        def swap_to_symlink(stage, target, *args, **kwargs):
            original_link(stage, target, *args, **kwargs)
            os.unlink(target)
            os.symlink(secret, target)

        with patch("build_inventory.os.link", side_effect=swap_to_symlink):
            with self.assertRaises(inv.InventoryBuildError):
                inv.build_inventory(self.root)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(secret.read_text(encoding="utf-8"), "external evidence")
        self.assert_sources_unchanged()

    def test_genuine_link_failure_keeps_root_pristine(self):
        with patch("build_inventory.os.link", side_effect=OSError(errno.EACCES, "private folder")):
            with self.assertRaises(inv.InventoryBuildError):
                inv.build_inventory(self.root)
        self.assertFalse(self.target.exists())
        self.assert_sources_unchanged()

    def test_postpublish_guard_failure_retains_manifest_for_review(self):
        with patch("build_inventory.check_candidate_directory",
                   side_effect=inv.CandidateGuardError("failed release gate")):
            with self.assertRaises(inv.InventoryBuildError):
                inv.build_inventory(self.root)
        self.assertTrue(self.target.is_file())
        self.assert_sources_unchanged()

    def test_originals_remain_untouched_on_success(self):
        self.assertEqual(inv.build_inventory(self.root), inv.MANIFEST)
        self.assertTrue(self.target.is_file())
        self.assert_sources_unchanged()

    def test_existing_manifest_cannot_be_overwritten(self):
        self.target.write_text("owner's evidence", encoding="utf-8")
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(self.root)
        self.assertEqual(self.target.read_text(encoding="utf-8"), "owner's evidence")
        self.assert_sources_unchanged()


if __name__ == "__main__":
    unittest.main()
