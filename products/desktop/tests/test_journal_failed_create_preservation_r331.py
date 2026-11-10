"""R331: prevent rollback deletion of a newly-created premium review journal.

Only synthetic local data. All tests use the real common journal append entrypoint.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from fvs_suite import journal_io

EVENT = b'{"action":"human-review","synthetic":true}\n'
PRIOR = b'{"action":"prior-review","synthetic":true}\n'
PRIVATE = "PRIVATE_SYNTHETIC_BANK_REFERENCE_R331.jsonl"


class NewJournalPreservationR331(unittest.TestCase):
    def setUp(self):
        sandbox = tempfile.TemporaryDirectory(prefix="r331-audit-local-")
        self.addCleanup(sandbox.cleanup)
        self.path = Path(sandbox.name) / PRIVATE

    def append(self, verify=lambda: None):
        return journal_io.append_verified_event(self.path, EVENT, 4096, verify)

    def test_new_success_writes_exact_event(self):
        self.append()
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_existing_success_preserves_history_and_adds_event(self):
        self.path.write_bytes(PRIOR)
        self.append()
        self.assertEqual(self.path.read_bytes(), PRIOR + EVENT)

    def test_new_verify_rejection_keeps_empty_evidence(self):
        def reject():
            raise ValueError("human-review-was-denied")
        with self.assertRaisesRegex(ValueError, "human-review-was-denied"):
            self.append(reject)
        self.assertTrue(self.path.exists())
        self.assertEqual(self.path.read_bytes(), b"")

    def test_new_oserror_during_validation_keeps_empty_and_redacts(self):
        def denied():
            raise PermissionError(13, PRIVATE, str(self.path))
        with self.assertRaises(ValueError) as caught:
            self.append(denied)
        self.assertEqual(str(caught.exception), "Review journal I/O failed; inspect journal before retrying")
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(self.path.read_bytes(), b"")

    def test_new_prefix_witness_failure_preserves_empty_evidence(self):
        with mock.patch.object(journal_io, "digest_pinned_prefix", side_effect=ValueError("prefix unavailable")):
            with self.assertRaisesRegex(ValueError, "prefix unavailable"):
                self.append()
        self.assertEqual(self.path.read_bytes(), b"")

    def test_new_prewrite_oserror_keeps_empty_and_redacts(self):
        with mock.patch.object(journal_io.os, "write", side_effect=PermissionError(13, PRIVATE, str(self.path))):
            with self.assertRaises(ValueError) as caught:
                self.append()
        self.assertEqual(str(caught.exception), "Review journal I/O failed; inspect journal before retrying")
        self.assertIsNone(caught.exception.__context__)
        self.assertEqual(self.path.read_bytes(), b"")

    def test_new_zero_length_write_does_not_erase_evidence(self):
        with mock.patch.object(journal_io.os, "write", return_value=0):
            with self.assertRaises(ValueError):
                self.append()
        self.assertEqual(self.path.read_bytes(), b"")

    def test_new_late_fsync_failure_retains_attempted_event(self):
        with mock.patch.object(journal_io.os, "fsync", side_effect=OSError("synthetic fsync denied")):
            with self.assertRaises(ValueError) as caught:
                self.append()
        self.assertEqual(str(caught.exception), "Review journal I/O failed; inspect journal before retrying")
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_rollback_never_unlinks_verified_new_empty_path(self):
        with mock.patch.object(journal_io.os, "unlink", side_effect=AssertionError("UNSAFE rollback unlink")) as deletion:
            with self.assertRaisesRegex(ValueError, "review intentionally rejected"):
                self.append(lambda: (_ for _ in ()).throw(ValueError("review intentionally rejected")))
        deletion.assert_not_called()
        self.assertEqual(self.path.read_bytes(), b"")

    def test_rollback_never_enters_attackable_check_then_unlink_window(self):
        native_unlink = os.unlink
        removed = []
        def replace_and_delete(path, *args, **kwargs):
            # Simulates rival process replacing a path after the prior lstat.
            Path(path).write_bytes(b"RIVAL_PRIVATE_FINANCIAL_DOCUMENT")
            removed.append(str(path))
            native_unlink(path, *args, **kwargs)
        with mock.patch.object(journal_io.os, "unlink", side_effect=replace_and_delete):
            with self.assertRaisesRegex(ValueError, "review denied"):
                self.append(lambda: (_ for _ in ()).throw(ValueError("review denied")))
        self.assertEqual(removed, [])
        self.assertEqual(self.path.read_bytes(), b"")

    def test_explicit_retry_after_failed_creation_appends_without_deletion(self):
        with self.assertRaisesRegex(ValueError, "manual hold"):
            self.append(lambda: (_ for _ in ()).throw(ValueError("manual hold")))
        self.assertEqual(self.path.read_bytes(), b"")
        # A human reviewer can inspect the empty attempt and explicitly retry.
        self.append()
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_existing_verify_rejection_never_modifies_previous_records(self):
        self.path.write_bytes(PRIOR)
        with self.assertRaisesRegex(ValueError, "review denied"):
            self.append(lambda: (_ for _ in ()).throw(ValueError("review denied")))
        self.assertEqual(self.path.read_bytes(), PRIOR)

    def test_invalid_event_does_not_create_file(self):
        with self.assertRaisesRegex(ValueError, "newline-terminated"):
            journal_io.append_verified_event(self.path, b'bad\x00event\n', 4096, lambda: None)
        self.assertFalse(self.path.exists())

    def test_over_limit_event_does_not_create_file(self):
        with self.assertRaisesRegex(ValueError, "size limit"):
            journal_io.append_verified_event(self.path, EVENT, len(EVENT) - 1, lambda: None)
        self.assertFalse(self.path.exists())

    def test_validation_callback_called_once_before_healthy_append(self):
        checked = []
        self.append(lambda: checked.append(not self.path.read_bytes()))
        self.assertEqual(checked, [True])
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_readback_failure_retains_ambiguous_written_evidence(self):
        with mock.patch.object(journal_io, "require_exact_append_readback", side_effect=ValueError("readback mismatch")):
            with self.assertRaisesRegex(ValueError, "readback mismatch"):
                self.append()
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_existing_oversize_journal_fails_without_modification(self):
        self.path.write_bytes(PRIOR)
        with self.assertRaisesRegex(ValueError, "size limit"):
            journal_io.append_verified_event(self.path, EVENT, len(PRIOR) + len(EVENT) - 1, lambda: None)
        self.assertEqual(self.path.read_bytes(), PRIOR)


if __name__ == "__main__":
    unittest.main()
