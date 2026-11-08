"""Real-filesystem adversarial tests of premium human-review lock ownership."""
from __future__ import annotations

import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite.review_lock import exclusive_review_lock
from synthetic_windows_fs_r104 import altered_lstat


class PremiumReviewLockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.journal = self.folder / "human-review.jsonl"
        self.lock = self.folder / "human-review.jsonl.lock"

    def _assert_synthetic_lock_drift(self, *, missing=False, field="st_ino",
                                     call_owner=True):
        """Model an observed race on Windows without deleting a held file.

        Real Windows sharing semantics may reject unlink/overwrite while the
        descriptor is live. Simulate only the path's security metadata and
        demand fail-closed ownership + no cleanup of a suspect lock.
        """
        real_lstat = os.lstat
        active = {"active": False}
        observer = altered_lstat(self.lock, active, real_lstat,
                                 missing=missing, field=field)
        with patch("fvs_suite.review_lock.os.lstat", side_effect=observer):
            with self.assertRaises(ValueError):
                with exclusive_review_lock(self.journal) as owned:
                    active["active"] = True
                    if call_owner:
                        owned()
        # This lock is real and unchanged on disk, but the custody check saw
        # a loss of identity and intentionally withheld automatic cleanup.
        self.assertTrue(self.lock.is_file())
        self.assertEqual(self.lock.read_bytes(),
                         f"pid={os.getpid()}\n".encode("ascii"))

    def test_exclusive_private_lock_and_cleanup(self):
        with exclusive_review_lock(self.journal) as owned:
            owned()
            self.assertTrue(self.lock.is_file())
            self.assertEqual(self.lock.read_bytes(), f"pid={os.getpid()}\n".encode("ascii"))
            if os.name == "posix":
                self.assertEqual(stat.S_IMODE(self.lock.stat().st_mode), 0o600)
        self.assertFalse(self.lock.exists())

    def test_normal_failure_releases_still_owned_lock(self):
        with self.assertRaisesRegex(RuntimeError, "validation"):
            with exclusive_review_lock(self.journal):
                raise RuntimeError("validation")
        self.assertFalse(self.lock.exists())

    def test_nested_writer_fails_without_unlocking_owner(self):
        with exclusive_review_lock(self.journal) as owned:
            with self.assertRaises(ValueError):
                with exclusive_review_lock(self.journal):
                    self.fail("second writer was admitted")
            owned()
            self.assertTrue(self.lock.exists())
        self.assertFalse(self.lock.exists())

    def test_preexisting_lock_is_never_replaced(self):
        self.lock.write_bytes(b"someone else's lock\n")
        with self.assertRaises(ValueError):
            with exclusive_review_lock(self.journal):
                self.fail("old lock was overwritten")
        self.assertEqual(self.lock.read_bytes(), b"someone else's lock\n")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unsupported")
    def test_preexisting_symlink_remains_untouched(self):
        private = self.folder / "private.csv"
        private.write_bytes(b"private records\n")
        try:
            self.lock.symlink_to(private)
        except OSError as exc:
            self.skipTest(f"cannot create symlink: {exc}")
        with self.assertRaises(ValueError):
            with exclusive_review_lock(self.journal):
                self.fail("symlink lock was followed")
        self.assertTrue(self.lock.is_symlink())
        self.assertEqual(private.read_bytes(), b"private records\n")

    def test_replaced_lock_blocks_confirmation_and_never_deletes_replacement(self):
        if os.name == "nt":
            self._assert_synthetic_lock_drift()
            return
        with self.assertRaises(ValueError):
            with exclusive_review_lock(self.journal) as owned:
                self.lock.unlink()
                self.lock.write_bytes(b"different writer\n")
                owned()
        self.assertEqual(self.lock.read_bytes(), b"different writer\n")

    def test_unlinked_lock_blocks_confirmation(self):
        if os.name == "nt":
            self._assert_synthetic_lock_drift(missing=True)
            return
        with self.assertRaises(ValueError):
            with exclusive_review_lock(self.journal) as owned:
                self.lock.unlink()
                owned()
        self.assertFalse(self.lock.exists())

    @unittest.skipUnless(hasattr(os, "link"), "hard links unsupported")
    def test_lock_hardlink_alias_blocks_confirmation_without_unlinking_evidence(self):
        extra = self.folder / "alias"
        try:
            with self.assertRaises(ValueError):
                with exclusive_review_lock(self.journal) as owned:
                    os.link(self.lock, extra)
                    owned()
        except OSError as exc:
            self.skipTest(f"cannot create hard link: {exc}")
        self.assertTrue(self.lock.exists())
        self.assertTrue(extra.exists())

    def test_modified_lock_blocks_confirmation_without_silent_cleanup(self):
        if os.name == "nt":
            self._assert_synthetic_lock_drift(field="st_size")
            return
        with self.assertRaises(ValueError):
            with exclusive_review_lock(self.journal) as owned:
                with self.lock.open("ab") as stream:
                    stream.write(b"tampered")
                owned()
        self.assertIn(b"tampered", self.lock.read_bytes())

    def test_missing_ownership_check_still_fails_on_exit(self):
        if os.name == "nt":
            self._assert_synthetic_lock_drift(call_owner=False)
            return
        with self.assertRaises(ValueError):
            with exclusive_review_lock(self.journal):
                self.lock.unlink()
                self.lock.write_bytes(b"replacement\n")
        self.assertEqual(self.lock.read_bytes(), b"replacement\n")

    def test_sync_failure_never_admits_writer(self):
        with patch("fvs_suite.review_lock.os.fsync", side_effect=OSError("disk failure")):
            with self.assertRaisesRegex(ValueError, "Review writer lock cannot be synced"):
                with exclusive_review_lock(self.journal):
                    self.fail("unsafe lock was accepted")
        # An indeterminate lock remains: conservative manual review.
        self.assertTrue(self.lock.exists())

    def test_subsequent_writer_works_after_clean_exit(self):
        with exclusive_review_lock(self.journal) as first:
            first()
        with exclusive_review_lock(self.journal) as second:
            second()
        self.assertFalse(self.lock.exists())

    def test_lock_does_not_write_to_or_read_journal(self):
        self.journal.write_bytes(b"existing immutable private review\n")
        with exclusive_review_lock(self.journal) as owned:
            owned()
        self.assertEqual(self.journal.read_bytes(), b"existing immutable private review\n")


if __name__ == "__main__":
    unittest.main()
