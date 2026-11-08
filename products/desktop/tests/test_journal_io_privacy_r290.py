"""R290: offline premium journal I/O failures never disclose evidence paths.

Only synthetic local files and injected failures; no payment decision, customer
records, licensed artifacts, network calls, or publication.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite.journal_io import append_verified_event, read_regular_bytes

PRIVATE = "synthetic-customer-account-69117"
READ_ERROR = "Review evidence cannot be read; inspect local input permissions"
APPEND_ERROR = "Review journal I/O failed; inspect journal before retrying"


class JournalIOMetadataPrivacyR290(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="r290-journal-")
        self.addCleanup(directory.cleanup)
        self.source = Path(directory.name) / (PRIVATE + ".jsonl")
        self.data = b'{"decision":"human-review"}\n'

    def assert_private_failure(self, error, message):
        self.assertIs(type(error), ValueError)
        self.assertEqual(str(error), message)
        self.assertIsNone(error.__cause__, "raw OSError retained as __cause__")
        self.assertIsNone(error.__context__, "raw OSError retained as __context__")
        self.assertNotIn(PRIVATE, repr(error))

    def test_missing_read_is_sanitized(self):
        with self.assertRaises(ValueError) as raised:
            read_regular_bytes(self.source, 1024, "Review journal")
        self.assert_private_failure(raised.exception, READ_ERROR)

    def test_initial_read_lstat_permission_denial_is_sanitized(self):
        self.source.write_bytes(self.data)
        with patch("fvs_suite.journal_io.os.lstat", side_effect=PermissionError(13, PRIVATE, str(self.source))):
            with self.assertRaises(ValueError) as raised:
                read_regular_bytes(self.source, 1024, "Review journal")
        self.assert_private_failure(raised.exception, READ_ERROR)
        self.assertEqual(self.source.read_bytes(), self.data)

    def test_read_open_permission_denial_is_sanitized(self):
        self.source.write_bytes(self.data)
        with patch("fvs_suite.journal_io.os.open", side_effect=PermissionError(13, PRIVATE, str(self.source))):
            with self.assertRaises(ValueError) as raised:
                read_regular_bytes(self.source, 1024, "Review journal")
        self.assert_private_failure(raised.exception, READ_ERROR)

    def test_read_fstat_failure_closes_descriptor_and_sanitizes(self):
        self.source.write_bytes(self.data)
        real_close = os.close
        closed = []
        def checked_close(fd):
            closed.append(fd)
            return real_close(fd)
        with patch("fvs_suite.journal_io.os.fstat", side_effect=PermissionError(13, PRIVATE, str(self.source))):
            with patch("fvs_suite.journal_io.os.close", side_effect=checked_close):
                with self.assertRaises(ValueError) as raised:
                    read_regular_bytes(self.source, 1024, "Review journal")
        self.assert_private_failure(raised.exception, READ_ERROR)
        self.assertEqual(len(closed), 1)

    def test_path_disappearance_after_descriptor_open_has_no_exception_chain(self):
        self.source.write_bytes(self.data)
        native_lstat = os.lstat
        calls = [0]
        def vanish(path):
            calls[0] += 1
            if calls[0] == 2:
                raise FileNotFoundError(2, PRIVATE, str(self.source))
            return native_lstat(path)
        with patch("fvs_suite.journal_io.os.lstat", side_effect=vanish):
            with self.assertRaises(ValueError) as raised:
                read_regular_bytes(self.source, 1024, "Review journal")
        self.assert_private_failure(raised.exception, "Review journal path changed during access")
        self.assertEqual(calls[0], 2)
        self.assertEqual(self.source.read_bytes(), self.data)

    def test_new_journal_open_error_is_sanitized(self):
        with patch("fvs_suite.journal_io.os.open", side_effect=PermissionError(13, PRIVATE, str(self.source))):
            with self.assertRaises(ValueError) as raised:
                append_verified_event(self.source, self.data, 1024, lambda: None)
        self.assert_private_failure(raised.exception, APPEND_ERROR)
        self.assertFalse(self.source.exists())

    def test_new_journal_creation_lstat_failure_is_sanitized(self):
        with patch("fvs_suite.journal_io.os.lstat", side_effect=PermissionError(13, PRIVATE, str(self.source))):
            with self.assertRaises(ValueError) as raised:
                append_verified_event(self.source, self.data, 1024, lambda: None)
        self.assert_private_failure(raised.exception, APPEND_ERROR)

    def test_verified_callback_oserror_is_sanitized_and_empty_file_removed(self):
        def fail_verification():
            raise PermissionError(13, PRIVATE, str(self.source))
        with self.assertRaises(ValueError) as raised:
            append_verified_event(self.source, self.data, 1024, fail_verification)
        self.assert_private_failure(raised.exception, APPEND_ERROR)
        self.assertFalse(self.source.exists(), "unchanged empty new file may be cleaned")

    def test_append_fsync_error_is_sanitized_and_write_not_rolled_back(self):
        self.source.write_bytes(self.data)
        with patch("fvs_suite.journal_io.os.fsync", side_effect=PermissionError(13, PRIVATE, str(self.source))):
            with self.assertRaises(ValueError) as raised:
                append_verified_event(self.source, self.data, 1024, lambda: None)
        self.assert_private_failure(raised.exception, APPEND_ERROR)
        self.assertEqual(self.source.read_bytes(), self.data + self.data)

    def test_partial_append_error_is_sanitized_and_retains_indeterminate_journal(self):
        self.source.write_bytes(self.data)
        native_write = os.write
        calls = [0]
        def partial(fd, data):
            calls[0] += 1
            if calls[0] == 1:
                return native_write(fd, data[:1])
            raise PermissionError(13, PRIVATE, str(self.source))
        with patch("fvs_suite.journal_io.os.write", side_effect=partial):
            with self.assertRaises(ValueError) as raised:
                append_verified_event(self.source, self.data, 1024, lambda: None)
        self.assert_private_failure(raised.exception, APPEND_ERROR)
        self.assertEqual(calls[0], 2)
        self.assertEqual(self.source.read_bytes(), self.data + b"{")

    def test_changed_empty_new_journal_is_retained_for_manual_review(self):
        native_lstat = os.lstat
        altered = [False]
        def changed(path):
            record = native_lstat(path)
            if altered[0]:
                # Same inode / zero size; different pathname ctime.
                # This previously passed the cleanup's inode/size-only check.
                class Drift:
                    def __getattr__(self, key):
                        if key == "st_ctime_ns":
                            return record.st_ctime_ns + 1
                        return getattr(record, key)
                return Drift()
            return record
        def reject():
            altered[0] = True
            raise ValueError("source changed; human revalidation required")
        with patch("fvs_suite.journal_io.os.lstat", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "human revalidation required"):
                append_verified_event(self.source, self.data, 1024, reject)
        self.assertTrue(self.source.exists(), "changed empty journal must not be removed")
        self.assertEqual(self.source.read_bytes(), b"")

    def test_normal_read_and_append_remain_byte_exact(self):
        self.source.write_bytes(self.data)
        self.assertEqual(read_regular_bytes(self.source, 1024, "Review journal"), self.data)
        append_verified_event(self.source, self.data, 1024, lambda: self.assertEqual(self.source.read_bytes(), self.data))
        self.assertEqual(self.source.read_bytes(), self.data + self.data)


if __name__ == "__main__":
    unittest.main()
