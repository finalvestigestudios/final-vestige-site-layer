"""R310: privacy of expected restore I/O errors and identity-bound rollback."""
from __future__ import annotations

import errno
import os
import stat
import tempfile
import traceback
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import vault_restore_writer as writer
from fvs_suite import vault_restore_cleanup as cleanup

PRIVATE = "PRIVATE-GRANT-CUSTOMER-ACCOUNT-2026"


class RestoreWriterR310(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r310-")
        self.addCleanup(temp.cleanup)
        self.parent = Path(temp.name)
        self.folder = self.parent / "restored"
        self.created = []

    def assert_private(self, error):
        self.assertIsNone(error.__context__)
        self.assertIsNone(error.__cause__)
        self.assertNotIn(PRIVATE, repr(error))
        self.assertNotIn(PRIVATE, "".join(traceback.format_exception(error)))
        self.assertNotIn(str(self.parent), repr(error))

    def test_create_private_directory_and_capture_actual_identity(self):
        owned = writer.make_private_restore_folder(self.folder)
        self.assertTrue(self.folder.is_dir())
        self.assertEqual(owned.st_dev, self.folder.stat().st_dev)
        self.assertEqual(owned.st_ino, self.folder.stat().st_ino)
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(self.folder.stat().st_mode), 0o700)

    def test_exclusive_member_write_tracks_identity_and_accurate_bytes(self):
        owned = writer.make_private_restore_folder(self.folder)
        path = self.folder / "exception-report.csv"
        writer.write_private_restore_member(path, b"id,amount\nSYNTHETIC,12.30\n", self.created)
        self.assertEqual(path.read_bytes(), b"id,amount\nSYNTHETIC,12.30\n")
        self.assertEqual(self.created[0][1].st_ino, path.stat().st_ino)
        cleanup.rollback_owned_restore(self.folder, owned, self.created)
        self.assertFalse(self.folder.exists())

    def test_directory_already_exists_does_not_write_or_modify(self):
        self.folder.mkdir()
        keeper = self.folder / "another-writers-file"
        keeper.write_bytes(b"keep")
        with self.assertRaisesRegex(ValueError, "create private") as err:
            writer.make_private_restore_folder(self.folder)
        self.assert_private(err.exception)
        self.assertEqual(keeper.read_bytes(), b"keep")

    def test_directory_creation_error_is_private(self):
        with patch.object(Path, "mkdir", side_effect=PermissionError(errno.EACCES, PRIVATE, str(self.folder))):
            with self.assertRaisesRegex(ValueError, "create private") as err:
                writer.make_private_restore_folder(self.folder)
        self.assert_private(err.exception)

    def test_folder_identity_error_is_private(self):
        with patch.object(writer, "snapshot_new_folder", side_effect=OSError(errno.EIO, PRIVATE, str(self.folder))):
            with self.assertRaisesRegex(ValueError, "verify private") as err:
                writer.make_private_restore_folder(self.folder)
        self.assert_private(err.exception)

    def test_directory_symlink_not_followed(self):
        outsider = self.parent / "outside"
        outsider.mkdir()
        try:
            self.folder.symlink_to(outsider, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink privilege unavailable")
        with self.assertRaisesRegex(ValueError, "create private") as err:
            writer.make_private_restore_folder(self.folder)
        self.assert_private(err.exception)
        self.assertTrue(self.folder.is_symlink())

    def test_write_existing_file_does_not_overwrite_or_claim(self):
        writer.make_private_restore_folder(self.folder)
        path = self.folder / "exception-report.csv"
        path.write_bytes(b"another writer")
        with self.assertRaisesRegex(ValueError, "write private") as err:
            writer.write_private_restore_member(path, b"SECRET", self.created)
        self.assert_private(err.exception)
        self.assertEqual(path.read_bytes(), b"another writer")
        self.assertEqual(self.created, [])

    def test_open_error_does_not_expose_private_path_or_chain(self):
        writer.make_private_restore_folder(self.folder)
        path = self.folder / "exception-report.csv"
        with patch.object(Path, "open", side_effect=PermissionError(errno.EACCES, PRIVATE, str(path))):
            with self.assertRaisesRegex(ValueError, "write private") as err:
                writer.write_private_restore_member(path, b"SYNTHETIC", self.created)
        self.assert_private(err.exception)
        self.assertEqual(self.created, [])

    def test_fsync_error_is_private_and_rollback_removes_created_file(self):
        owned = writer.make_private_restore_folder(self.folder)
        path = self.folder / "exception-report.csv"
        with patch.object(writer.os, "fsync", side_effect=OSError(errno.EIO, PRIVATE, str(path))):
            with self.assertRaisesRegex(ValueError, "write private") as err:
                writer.write_private_restore_member(path, b"PRIVATE-SYNTHETIC", self.created)
        self.assert_private(err.exception)
        self.assertEqual(len(self.created), 1)
        cleanup.rollback_owned_restore(self.folder, owned, self.created)
        self.assertFalse(self.folder.exists())

    def test_fsync_error_replacement_file_survives_rollback(self):
        owned = writer.make_private_restore_folder(self.folder)
        path = self.folder / "exception-report.csv"
        with patch.object(writer.os, "fsync", side_effect=OSError(errno.EIO, PRIVATE)):
            with self.assertRaises(ValueError):
                writer.write_private_restore_member(path, b"PRIVATE-SYNTHETIC", self.created)
        replacement = self.parent / "other"
        replacement.write_bytes(b"unrelated")
        os.replace(replacement, path)
        cleanup.rollback_owned_restore(self.folder, owned, self.created)
        self.assertEqual(path.read_bytes(), b"unrelated")

    def test_interrupt_propagates_and_caller_can_rollback(self):
        owned = writer.make_private_restore_folder(self.folder)
        path = self.folder / "exception-report.csv"
        with patch.object(writer.os, "fsync", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                writer.write_private_restore_member(path, b"PRIVATE-SYNTHETIC", self.created)
        cleanup.rollback_owned_restore(self.folder, owned, self.created)
        self.assertFalse(self.folder.exists())

    def test_unavailable_descriptor_identity_writes_no_payload(self):
        writer.make_private_restore_folder(self.folder)
        path = self.folder / "exception-report.csv"
        with patch.object(writer, "snapshot_new_file", side_effect=OSError(errno.EIO, PRIVATE, str(path))):
            with self.assertRaisesRegex(ValueError, "write private") as err:
                writer.write_private_restore_member(path, b"PRIVATE-SYNTHETIC", self.created)
        self.assert_private(err.exception)
        self.assertEqual(path.read_bytes(), b"")
        self.assertEqual(self.created, [])

    def test_multiple_members_are_all_tracked_for_rollback(self):
        owned = writer.make_private_restore_folder(self.folder)
        for name in ("exception-report.csv", "exception-report.review.jsonl", "sealed-evidence-manifest.json"):
            writer.write_private_restore_member(self.folder / name, b"SYNTHETIC", self.created)
        self.assertEqual(len(self.created), 3)
        cleanup.rollback_owned_restore(self.folder, owned, self.created)
        self.assertFalse(self.folder.exists())


if __name__ == "__main__":
    unittest.main()
