"""R289: premium review locks retain uncertain evidence on exceptional exits.

No customer files, decisions, licensing service, network or Windows EXE used.
Failures are injected into a real descriptor's final ownership inspection.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite.review_lock import exclusive_review_lock

PRIVATE = "synthetic-private-ledger-77003"


class ReviewLockExceptionalExitR289(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="r289-review-")
        self.addCleanup(self.tmp.cleanup)
        self.journal = Path(self.tmp.name) / (PRIVATE + ".jsonl")
        self.lock = Path(str(self.journal) + ".lock")

    def _descriptor_failure(self, at_call, *, mode="oserror"):
        original = os.fstat
        calls = [0]

        def injected(fd):
            calls[0] += 1
            if calls[0] == at_call:
                if mode == "oserror":
                    raise PermissionError(13, PRIVATE, str(self.lock))
                original_info = original(fd)
                class Changed:
                    def __getattr__(self, name):
                        if name == "st_size":
                            return original_info.st_size + 1
                        return getattr(original_info, name)
                return Changed()
            return original(fd)
        return calls, injected

    def test_runtime_failure_preserves_uncertain_descriptor_lock(self):
        calls, injected = self._descriptor_failure(3)
        with patch("fvs_suite.review_lock.os.fstat", side_effect=injected):
            with self.assertRaisesRegex(RuntimeError, "synthetic validation"):
                with exclusive_review_lock(self.journal):
                    raise RuntimeError("synthetic validation")
        self.assertEqual(calls[0], 3)
        self.assertTrue(self.lock.is_file())
        self.assertFalse(self.journal.exists())

    def test_keyboard_interrupt_preserves_uncertain_lock(self):
        calls, injected = self._descriptor_failure(3)
        with patch("fvs_suite.review_lock.os.fstat", side_effect=injected):
            with self.assertRaises(KeyboardInterrupt):
                with exclusive_review_lock(self.journal):
                    raise KeyboardInterrupt()
        self.assertEqual(calls[0], 3)
        self.assertTrue(self.lock.is_file())

    def test_system_exit_preserves_uncertain_lock(self):
        calls, injected = self._descriptor_failure(3)
        with patch("fvs_suite.review_lock.os.fstat", side_effect=injected):
            with self.assertRaises(SystemExit):
                with exclusive_review_lock(self.journal):
                    raise SystemExit(2)
        self.assertEqual(calls[0], 3)
        self.assertTrue(self.lock.is_file())

    def test_descriptor_metadata_drift_on_callback_failure_keeps_lock(self):
        calls, injected = self._descriptor_failure(3, mode="drift")
        with patch("fvs_suite.review_lock.os.fstat", side_effect=injected):
            with self.assertRaisesRegex(RuntimeError, "synthetic validation"):
                with exclusive_review_lock(self.journal):
                    raise RuntimeError("synthetic validation")
        self.assertEqual(calls[0], 3)
        self.assertTrue(self.lock.is_file())

    def test_late_drift_after_successful_post_yield_check_is_rejected(self):
        calls, injected = self._descriptor_failure(4, mode="drift")
        with patch("fvs_suite.review_lock.os.fstat", side_effect=injected):
            with self.assertRaisesRegex(ValueError, "Review writer lock descriptor changed"):
                with exclusive_review_lock(self.journal):
                    pass
        self.assertEqual(calls[0], 4)
        self.assertTrue(self.lock.is_file())

    def test_uncertain_lock_blocks_subsequent_writer(self):
        calls, injected = self._descriptor_failure(3)
        with patch("fvs_suite.review_lock.os.fstat", side_effect=injected):
            with self.assertRaises(RuntimeError):
                with exclusive_review_lock(self.journal):
                    raise RuntimeError("synthetic failure")
        self.assertEqual(calls[0], 3)
        with self.assertRaisesRegex(ValueError, "journal locked"):
            with exclusive_review_lock(self.journal):
                self.fail("Second writer entered after uncertain ownership")
        self.assertTrue(self.lock.is_file())

    def test_ordinary_callback_failure_cleans_still_owned_lock(self):
        with self.assertRaisesRegex(RuntimeError, "synthetic validation"):
            with exclusive_review_lock(self.journal):
                raise RuntimeError("synthetic validation")
        self.assertFalse(self.lock.exists())

    def test_success_still_releases_lock(self):
        with exclusive_review_lock(self.journal) as owned:
            owned()
        self.assertFalse(self.lock.exists())


if __name__ == "__main__":
    unittest.main()
