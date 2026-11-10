"""R332: reconcile historical R47/R290 rollback assertions with R331 custody.

Synthetic local evidence only. This exercises the real journal I/O entrypoint;
no auto-approval, remote calls, premium artifacts, or personal data.
"""
from __future__ import annotations

import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite.journal_io import append_verified_event, read_regular_bytes

EVENT = b'{"review":"human-only","synthetic":true}\n'
PRIOR = b'{"review":"prior","synthetic":true}\n'
PRIVATE = "PRIVATE_SYNTHETIC_FINANCIAL_DATA_R332.jsonl"
APPEND_ERROR = "Review journal I/O failed; inspect journal before retrying"


class FailedJournalCustodyR332(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="r332-private-review-")
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / PRIVATE

    def append(self, verify=lambda: None):
        append_verified_event(self.path, EVENT, 4096, verify)

    def test_failed_new_verification_retains_empty_journal(self):
        with self.assertRaisesRegex(ValueError, "source changed"):
            self.append(lambda: (_ for _ in ()).throw(ValueError("source changed")))
        self.assertTrue(self.path.is_file())
        self.assertEqual(self.path.read_bytes(), b"")

    def test_callback_oserror_redacted_and_keeps_empty_file(self):
        def deny():
            raise PermissionError(13, PRIVATE, str(self.path))
        with self.assertRaises(ValueError) as caught:
            self.append(deny)
        self.assertEqual(str(caught.exception), APPEND_ERROR)
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(self.path.read_bytes(), b"")

    def test_failed_new_verification_never_invokes_unlink(self):
        with patch("fvs_suite.journal_io.os.unlink", side_effect=AssertionError("unsafe deletion")) as unlink:
            with self.assertRaisesRegex(ValueError, "hold"):
                self.append(lambda: (_ for _ in ()).throw(ValueError("hold")))
        unlink.assert_not_called()
        self.assertEqual(self.path.read_bytes(), b"")

    def test_explicit_retry_from_preserved_empty_file_appends_once(self):
        with self.assertRaises(ValueError):
            self.append(lambda: (_ for _ in ()).throw(ValueError("hold")))
        self.assertEqual(read_regular_bytes(self.path, 4096, "Review journal"), b"")
        self.append()
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_previous_journal_not_deleted_when_callback_rejects(self):
        self.path.write_bytes(PRIOR)
        with self.assertRaisesRegex(ValueError, "hold"):
            self.append(lambda: (_ for _ in ()).throw(ValueError("hold")))
        self.assertEqual(self.path.read_bytes(), PRIOR)

    def test_preopen_invalid_data_creates_nothing(self):
        with self.assertRaisesRegex(ValueError, "newline-terminated"):
            append_verified_event(self.path, b"not-json\x00\n", 4096, lambda: None)
        self.assertFalse(self.path.exists())

    def test_new_open_permission_denial_creates_nothing(self):
        with patch("fvs_suite.journal_io.os.open", side_effect=PermissionError(13, PRIVATE, str(self.path))):
            with self.assertRaises(ValueError) as caught:
                self.append()
        self.assertEqual(str(caught.exception), APPEND_ERROR)
        self.assertFalse(self.path.exists())

    def test_fsync_denial_preserves_ambiguous_written_event(self):
        with patch("fvs_suite.journal_io.os.fsync", side_effect=OSError("synthetic fsync denial")):
            with self.assertRaises(ValueError) as caught:
                self.append()
        self.assertEqual(str(caught.exception), APPEND_ERROR)
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_successful_existing_append_preserves_prior_history(self):
        self.path.write_bytes(PRIOR)
        self.append()
        self.assertEqual(self.path.read_bytes(), PRIOR + EVENT)

    def test_new_journal_creation_is_private_on_posix(self):
        self.append()
        self.assertEqual(self.path.read_bytes(), EVENT)
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)


if __name__ == "__main__":
    unittest.main()
