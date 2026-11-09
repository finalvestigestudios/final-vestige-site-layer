"""R309: synthetic private restore rollback custody; no financial data or network."""
from __future__ import annotations

import errno
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import vault_restore_cleanup as rollback


class VaultRestoreRollbackR309(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fvs-r309-")
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.folder = self.parent / "fvs-evidence-restored-private"
        self.folder.mkdir(mode=0o700)
        self.owned_folder = rollback.snapshot_new_folder(self.folder)
        self.created = []

    def add_file(self, name="exception-report.csv", data=b"PRIVATE-SYNTHETIC-RECORD"):
        path = self.folder / name
        with path.open("xb") as handle:
            owned = rollback.snapshot_new_file(handle.fileno())
            self.created.append((path, owned))
            handle.write(data)
        return path

    def roll(self):
        rollback.rollback_owned_restore(self.folder, self.owned_folder, self.created)

    def test_one_owned_file_removed_and_folder_removed(self):
        path = self.add_file()
        self.roll()
        self.assertFalse(path.exists())
        self.assertFalse(self.folder.exists())

    def test_three_owned_files_removed_in_reverse_order(self):
        paths = [self.add_file(n) for n in ("exception-report.csv", "exception-report.review.jsonl", "sealed-evidence-manifest.json")]
        self.roll()
        self.assertTrue(all(not x.exists() for x in paths))
        self.assertFalse(self.folder.exists())

    def test_file_replaced_by_unrelated_regular_file_is_preserved(self):
        path = self.add_file()
        replacement = self.parent / "other-file"
        replacement.write_bytes(b"unrelated writer")
        os.replace(replacement, path)
        self.roll()
        self.assertEqual(path.read_bytes(), b"unrelated writer")
        self.assertTrue(self.folder.is_dir())

    def test_identical_bytes_but_new_inode_is_preserved(self):
        path = self.add_file(data=b"same bytes")
        replacement = self.parent / "other-file"
        replacement.write_bytes(b"same bytes")
        os.replace(replacement, path)
        self.roll()
        self.assertEqual(path.read_bytes(), b"same bytes")
        self.assertTrue(self.folder.exists())

    @unittest.skipIf(os.name == "nt", "OS symlink privileges vary on Windows")
    def test_replacement_symlink_is_preserved_and_not_followed(self):
        path = self.add_file()
        outside = self.parent / "protected.txt"
        outside.write_bytes(b"protected")
        path.unlink()
        path.symlink_to(outside)
        self.roll()
        self.assertTrue(path.is_symlink())
        self.assertEqual(outside.read_bytes(), b"protected")
        self.assertTrue(self.folder.exists())

    def test_changed_content_same_inode_is_our_file_and_removed(self):
        path = self.add_file()
        path.write_bytes(b"modified after write")
        self.roll()
        self.assertFalse(self.folder.exists())

    def test_early_missing_file_is_tolerated(self):
        path = self.add_file()
        path.unlink()
        self.roll()
        self.assertFalse(self.folder.exists())

    def test_directory_replaced_is_never_deleted(self):
        path = self.add_file()
        self.folder.rename(self.parent / "old")
        self.folder.mkdir()
        other = self.folder / path.name
        other.write_bytes(b"other occupant")
        self.roll()
        self.assertEqual(other.read_bytes(), b"other occupant")
        self.assertTrue(self.folder.exists())

    def test_directory_replaced_with_symlink_not_followed(self):
        outside = self.parent / "protected"
        outside.mkdir()
        self.add_file()
        self.folder.rename(self.parent / "old")
        try:
            self.folder.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink unavailable")
        self.roll()
        self.assertTrue(self.folder.is_symlink())
        self.assertTrue(outside.exists())

    def test_unowned_file_keeps_folder(self):
        self.add_file()
        other = self.folder / "not-ours.txt"
        other.write_bytes(b"other")
        self.roll()
        self.assertEqual(other.read_bytes(), b"other")

    def test_unlink_error_does_not_mask_original_failure(self):
        self.add_file()
        with patch.object(rollback.os, "unlink", side_effect=PermissionError(errno.EACCES, "synthetic")):
            self.roll()
        self.assertTrue(self.folder.exists())

    def test_rmdir_error_does_not_mask_original_failure(self):
        self.add_file()
        with patch.object(rollback.os, "rmdir", side_effect=PermissionError(errno.EACCES, "synthetic")):
            self.roll()
        self.assertTrue(self.folder.exists())

    def test_folder_lstat_error_does_not_delete_any_file(self):
        path = self.add_file()
        original = rollback.os.lstat
        def fail_folder(p):
            if str(p) == str(self.folder):
                raise PermissionError(errno.EACCES, "synthetic")
            return original(p)
        with patch.object(rollback.os, "lstat", side_effect=fail_folder):
            self.roll()
        self.assertTrue(path.exists())

    def test_snapshot_new_file_real_descriptor_matches_path(self):
        path = self.add_file()
        owned = self.created[0][1]
        self.assertEqual(owned.st_ino, path.stat().st_ino)
        self.assertTrue(stat.S_ISREG(owned.st_mode))

    def test_snapshot_new_file_rejects_missing_inode(self):
        class ZeroInode:
            st_mode = stat.S_IFREG | 0o600
            st_ino = 0
            st_nlink = 1
        with patch.object(rollback.os, "fstat", return_value=ZeroInode()):
            with self.assertRaisesRegex(OSError, "identity unavailable"):
                rollback.snapshot_new_file(5)

    def test_snapshot_new_file_rejects_directory(self):
        class NotFile:
            st_mode = stat.S_IFDIR | 0o700
            st_ino = 5
            st_nlink = 1
        with patch.object(rollback.os, "fstat", return_value=NotFile()):
            with self.assertRaisesRegex(OSError, "identity unavailable"):
                rollback.snapshot_new_file(5)

    def test_snapshot_new_folder_rejects_missing_inode(self):
        old = rollback.os.lstat
        class ZeroDirectory:
            st_mode = stat.S_IFDIR | 0o700
            st_ino = 0
        with patch.object(rollback.os, "lstat", return_value=ZeroDirectory()):
            with self.assertRaisesRegex(OSError, "identity unavailable"):
                rollback.snapshot_new_folder(self.folder)

    def test_snapshot_new_folder_rejects_regular_file(self):
        path = self.add_file()
        with self.assertRaisesRegex(OSError, "identity unavailable"):
            rollback.snapshot_new_folder(path)

    def test_same_inode_but_wrong_type_is_not_unlinked(self):
        path = self.add_file()
        original = rollback.os.lstat
        class WrongType:
            st_dev = self.created[0][1].st_dev
            st_ino = self.created[0][1].st_ino
            st_mode = stat.S_IFLNK | 0o777
        def altered(p):
            if str(p) == str(path):
                return WrongType()
            return original(p)
        with patch.object(rollback.os, "lstat", side_effect=altered):
            self.roll()
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
