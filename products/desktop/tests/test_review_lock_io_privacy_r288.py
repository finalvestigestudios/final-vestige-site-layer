"""R288: descriptor IO must fail closed without leaking private financial paths.

Real temporary files plus narrowly injected OS failures; no customer data,
network, executable packaging, reviewer decision or premium access is used.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite.review_lock import exclusive_review_lock

PRIVATE = "private-customer-account-44917"


class ReviewLockDescriptorPrivacyR288(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r288-review-")
        self.addCleanup(self.temp.cleanup)
        self.journal = Path(self.temp.name) / (PRIVATE + ".jsonl")
        self.lock = Path(str(self.journal) + ".lock")

    def assert_sanitized(self, error, expected):
        self.assertIs(type(error), ValueError)
        self.assertEqual(str(error), expected)
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertNotIn(PRIVATE, str(error))

    def test_initial_descriptor_inspection_denied(self):
        with patch("fvs_suite.review_lock.os.fstat",
                   side_effect=PermissionError(13, PRIVATE, str(self.lock))):
            with self.assertRaises(ValueError) as error:
                with exclusive_review_lock(self.journal):
                    self.fail("Writer admitted without descriptor inspection")
        self.assert_sanitized(error.exception,
            "Review writer lock descriptor cannot be inspected; inspect before retrying")
        self.assertTrue(self.lock.is_file())
        self.assertFalse(self.journal.exists())

    def test_post_sync_descriptor_inspection_denied(self):
        native = os.fstat
        calls = [0]
        def later(fd):
            calls[0] += 1
            if calls[0] == 2:
                raise PermissionError(13, PRIVATE, str(self.lock))
            return native(fd)
        with patch("fvs_suite.review_lock.os.fstat", side_effect=later):
            with self.assertRaises(ValueError) as error:
                with exclusive_review_lock(self.journal):
                    self.fail("Writer admitted without durable descriptor identity")
        self.assert_sanitized(error.exception,
            "Review writer lock descriptor cannot be inspected; inspect before retrying")
        self.assertEqual(calls[0], 2)
        self.assertTrue(self.lock.is_file())

    def test_live_descriptor_failure_preserves_uncertain_lock(self):
        native = os.fstat
        calls = [0]
        def late(fd):
            calls[0] += 1
            if calls[0] == 3:
                raise PermissionError(13, PRIVATE, str(self.lock))
            return native(fd)
        with patch("fvs_suite.review_lock.os.fstat", side_effect=late):
            with self.assertRaises(ValueError) as error:
                with exclusive_review_lock(self.journal) as verify:
                    verify()
        self.assert_sanitized(error.exception,
            "Review writer lock descriptor cannot be inspected; inspect before retrying")
        self.assertTrue(self.lock.is_file(), "uncertain custody must not auto-unlink")
        self.assertFalse(self.journal.exists())

    def test_write_permission_error_is_redacted(self):
        with patch("fvs_suite.review_lock.os.write",
                   side_effect=PermissionError(13, PRIVATE, str(self.lock))):
            with self.assertRaises(ValueError) as error:
                with exclusive_review_lock(self.journal):
                    self.fail("Writer admitted after failed lock write")
        self.assert_sanitized(error.exception,
            "Review writer lock cannot be written; inspect before retrying")
        self.assertTrue(self.lock.is_file())

    def test_short_write_then_os_error_preserves_partial_lock(self):
        original = os.write
        calls = [0]
        def partial(fd, data):
            calls[0] += 1
            if calls[0] == 1:
                return original(fd, data[:1])
            raise OSError(5, PRIVATE, str(self.lock))
        with patch("fvs_suite.review_lock.os.write", side_effect=partial):
            with self.assertRaises(ValueError) as error:
                with exclusive_review_lock(self.journal):
                    self.fail("Writer admitted after truncated lock")
        self.assert_sanitized(error.exception,
            "Review writer lock cannot be written; inspect before retrying")
        self.assertEqual(self.lock.read_bytes(), b"p")
        self.assertEqual(calls[0], 2)

    def test_zero_length_write_cannot_admit_writer(self):
        with patch("fvs_suite.review_lock.os.write", return_value=0):
            with self.assertRaises(ValueError) as error:
                with exclusive_review_lock(self.journal):
                    self.fail("Writer admitted after zero write")
        self.assert_sanitized(error.exception,
            "Review writer lock cannot be written; inspect before retrying")
        self.assertTrue(self.lock.is_file())

    def test_sync_error_is_redacted_and_preserved(self):
        with patch("fvs_suite.review_lock.os.fsync",
                   side_effect=OSError(5, PRIVATE, str(self.lock))):
            with self.assertRaises(ValueError) as error:
                with exclusive_review_lock(self.journal):
                    self.fail("Writer admitted after failed fsync")
        self.assert_sanitized(error.exception,
            "Review writer lock cannot be synced; inspect before retrying")
        self.assertTrue(self.lock.is_file())

    def test_close_error_is_redacted_and_preserved(self):
        original = os.close
        failed = [False]
        def close_and_fail(fd):
            # Real closure ensures a Windows test does not leak a held FD.
            result = original(fd)
            if not failed[0]:
                failed[0] = True
                raise OSError(5, PRIVATE, str(self.lock))
            return result
        with patch("fvs_suite.review_lock.os.close", side_effect=close_and_fail):
            with self.assertRaises(ValueError) as error:
                with exclusive_review_lock(self.journal) as verify:
                    verify()
        self.assert_sanitized(error.exception,
            "Review writer lock descriptor cannot be closed; inspect before retrying")
        self.assertTrue(failed[0])
        self.assertTrue(self.lock.is_file())

    def test_successful_custody_can_repeat_after_clean_cleanup(self):
        for _ in range(3):
            with exclusive_review_lock(self.journal) as verify:
                verify()
                self.assertEqual(self.lock.read_bytes(),
                                 f"pid={os.getpid()}\n".encode("ascii"))
            self.assertFalse(self.lock.exists())


if __name__ == "__main__":
    unittest.main()
