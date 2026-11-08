"""R287: premium review lock failures must not retain private OS paths.

Only local synthetic journals are used. No payment approval, real credentials,
network, or premium binary is involved.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite.review_lock import exclusive_review_lock

PRIVATE_MARKER = "client-PRIVATE-account-8724"


class ReviewLockExceptionCustodyR287(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="fvs-r287-")
        self.addCleanup(folder.cleanup)
        self.journal = Path(folder.name) / (PRIVATE_MARKER + ".jsonl")
        self.lock = Path(str(self.journal) + ".lock")

    def assert_private_safe(self, err, message):
        self.assertIs(type(err), ValueError)
        self.assertEqual(str(err), message)
        self.assertIsNone(err.__cause__, "original OS error retained as explicit cause")
        self.assertIsNone(err.__context__, "original OS error retained as implicit context")
        self.assertNotIn(PRIVATE_MARKER, str(err))

    def test_preexisting_lock_does_not_retain_path_or_write(self):
        original = b"another reviewer has custody\n"
        self.lock.write_bytes(original)
        with self.assertRaises(ValueError) as caught:
            with exclusive_review_lock(self.journal):
                self.fail("double writer admitted")
        self.assert_private_safe(caught.exception,
                                 "Review journal locked; inspect the existing lock before retrying")
        self.assertEqual(self.lock.read_bytes(), original)
        self.assertFalse(self.journal.exists())

    def test_open_denied_is_fixed_and_no_lock_created(self):
        original_open = os.open
        def denied(path, *args, **kwargs):
            if Path(path) == self.lock:
                raise PermissionError(13, "PRIVATE DENIED", str(path))
            return original_open(path, *args, **kwargs)
        with patch("fvs_suite.review_lock.os.open", side_effect=denied):
            with self.assertRaises(ValueError) as caught:
                with exclusive_review_lock(self.journal):
                    self.fail("permission-denied writer admitted")
        self.assert_private_safe(caught.exception,
                                 "Review writer lock cannot be created; inspect local permissions")
        self.assertFalse(self.lock.exists())

    def test_missing_lock_rejects_and_preserves_missing_state(self):
        if os.name == "nt":
            # A Windows-held descriptor may forbid unlinking the lock file.
            # Model a missing pathname observation without changing evidence.
            real_lstat = os.lstat
            missing = {"active": False}
            def vanished(path, *args, **kwargs):
                if Path(path) == self.lock and missing["active"]:
                    raise FileNotFoundError(2, "PRIVATE MISSING", str(path))
                return real_lstat(path, *args, **kwargs)
            with patch("fvs_suite.review_lock.os.lstat", side_effect=vanished):
                with self.assertRaises(ValueError) as caught:
                    with exclusive_review_lock(self.journal) as verify:
                        missing["active"] = True
                        verify()
            self.assertTrue(self.lock.is_file(), "unverified lock left for manual review")
        else:
            with self.assertRaises(ValueError) as caught:
                with exclusive_review_lock(self.journal) as verify:
                    self.lock.unlink()
                    verify()
            self.assertFalse(self.lock.exists())
        self.assert_private_safe(caught.exception,
                                 "Review writer lock disappeared; inspect journal before retrying")
        self.assertFalse(self.journal.exists())

    def test_lstat_denied_does_not_retain_path_or_unlink(self):
        real_lstat = os.lstat
        calls = 0
        def denied(path, *args, **kwargs):
            nonlocal calls
            if Path(path) == self.lock:
                calls += 1
                if calls >= 3:
                    raise PermissionError(13, "PRIVATE DENIED", str(path))
            return real_lstat(path, *args, **kwargs)
        with patch("fvs_suite.review_lock.os.lstat", side_effect=denied):
            with self.assertRaises(ValueError) as caught:
                with exclusive_review_lock(self.journal) as verify:
                    verify()
        self.assert_private_safe(caught.exception,
                                 "Review writer lock cannot be inspected; inspect before retrying")
        self.assertTrue(self.lock.is_file(), "indeterminate lock must remain for investigation")

    def test_unlink_denied_does_not_retain_path_or_delete(self):
        real_unlink = os.unlink
        def denied(path, *args, **kwargs):
            if Path(path) == self.lock:
                raise PermissionError(13, "PRIVATE DENIED", str(path))
            return real_unlink(path, *args, **kwargs)
        with patch("fvs_suite.review_lock.os.unlink", side_effect=denied):
            with self.assertRaises(ValueError) as caught:
                with exclusive_review_lock(self.journal) as verify:
                    verify()
        self.assert_private_safe(caught.exception,
                                 "Review writer lock cleanup failed; inspect before retrying")
        self.assertTrue(self.lock.is_file())

    def test_successful_lock_roundtrip_and_reuse(self):
        for _ in range(2):
            with exclusive_review_lock(self.journal) as verify:
                verify()
                self.assertEqual(self.lock.read_bytes(),
                                 f"pid={os.getpid()}\n".encode("ascii"))
            self.assertFalse(self.lock.exists())


if __name__ == "__main__":
    unittest.main()
