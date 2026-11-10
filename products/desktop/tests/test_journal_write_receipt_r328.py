"""R328: premium audit append requires readback of the actual written event.

Local synthetic evidence only. Fault injection models a successful same-length
but wrong-content write, not a claim of spontaneous file corruption in normal use.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from fvs_suite.journal_write_receipt import require_exact_append_readback
from fvs_suite import journal_io

FIRST = b'{"decision":"needs_evidence","synthetic":true}\n'
SECOND = b'{"decision":"manual_review","synthetic":true}\n'
PRIVATE = "PRIVATE_BANK_ACCOUNT_428133.review.jsonl"
LIMIT = 4096


class JournalWriteReceiptR328(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r328-synthetic-")
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / PRIVATE
        self.path.write_bytes(FIRST)

    def _write(self, event: bytes = SECOND):
        descriptor = os.open(self.path, os.O_RDWR | os.O_APPEND)
        self.addCleanup(os.close, descriptor)
        before = os.fstat(descriptor)
        os.write(descriptor, event)
        os.fsync(descriptor)
        return descriptor, before.st_size

    def test_helper_existing_journal_exact_readback(self):
        fd, offset = self._write()
        require_exact_append_readback(fd, offset, SECOND)
        self.assertEqual(self.path.read_bytes(), FIRST + SECOND)

    def test_helper_empty_journal_exact_readback(self):
        self.path.write_bytes(b"")
        fd, offset = self._write()
        self.assertEqual(offset, 0)
        require_exact_append_readback(fd, offset, SECOND)

    def test_helper_rejects_same_length_wrong_content(self):
        bad = SECOND.replace(b"manual", b"formal")
        self.assertEqual(len(bad), len(SECOND))
        fd, offset = self._write(bad)
        with self.assertRaisesRegex(ValueError, "appended bytes differ"):
            require_exact_append_readback(fd, offset, SECOND)

    def test_helper_rejects_short_content(self):
        fd, offset = self._write(SECOND[:-1])
        with self.assertRaisesRegex(ValueError, "appended bytes differ"):
            require_exact_append_readback(fd, offset, SECOND)

    def test_helper_rejects_extra_content(self):
        fd, offset = self._write(SECOND + b"x")
        with self.assertRaisesRegex(ValueError, "appended bytes differ"):
            require_exact_append_readback(fd, offset, SECOND)

    def test_helper_rejects_injected_short_read(self):
        fd, offset = self._write()
        with mock.patch("fvs_suite.journal_write_receipt.os.read", return_value=SECOND[:3]):
            with self.assertRaisesRegex(ValueError, "appended bytes differ"):
                require_exact_append_readback(fd, offset, SECOND)

    def test_helper_rejects_false_seek_offset(self):
        fd, offset = self._write()
        with mock.patch("fvs_suite.journal_write_receipt.os.lseek", return_value=offset + 1):
            with self.assertRaisesRegex(ValueError, "could not be positioned"):
                require_exact_append_readback(fd, offset, SECOND)

    def test_helper_rejects_invalid_location_or_payload(self):
        fd, offset = self._write()
        for invalid_offset, invalid_event in ((-1, SECOND), ("0", SECOND), (offset, b""), (offset, "not bytes")):
            with self.subTest(offset=invalid_offset, event=invalid_event):
                with self.assertRaisesRegex(ValueError, "witness is invalid"):
                    require_exact_append_readback(fd, invalid_offset, invalid_event)

    def test_integration_existing_journal_appends_exact_bytes(self):
        calls = []
        journal_io.append_verified_event(self.path, SECOND, LIMIT, lambda: calls.append(True))
        self.assertEqual(calls, [True])
        self.assertEqual(self.path.read_bytes(), FIRST + SECOND)

    def test_integration_new_journal_appends_exact_bytes(self):
        self.path.unlink()
        journal_io.append_verified_event(self.path, SECOND, LIMIT, lambda: None)
        self.assertEqual(self.path.read_bytes(), SECOND)

    def test_integration_rejects_corrupt_same_length_write_and_preserves_evidence(self):
        native_write = os.write
        corrupt = SECOND.replace(b"manual", b"formal")
        self.assertEqual(len(SECOND), len(corrupt))
        def tamper(fd, payload):
            return native_write(fd, corrupt if payload == SECOND else payload)
        with mock.patch.object(journal_io.os, "write", side_effect=tamper):
            with self.assertRaisesRegex(ValueError, "appended bytes differ") as caught:
                journal_io.append_verified_event(self.path, SECOND, LIMIT, lambda: None)
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertIsNone(caught.exception.__context__)
        self.assertEqual(self.path.read_bytes(), FIRST + corrupt)

    def test_integration_rejects_short_read_even_when_file_size_matches(self):
        native_read = os.read
        def truncate(fd, count):
            return native_read(fd, count)[:3]
        with mock.patch("fvs_suite.journal_write_receipt.os.read", side_effect=truncate):
            with self.assertRaisesRegex(ValueError, "appended bytes differ"):
                journal_io.append_verified_event(self.path, SECOND, LIMIT, lambda: None)
        self.assertEqual(self.path.read_bytes(), FIRST + SECOND)

    def test_integration_readback_oserror_is_path_redacted(self):
        with mock.patch("fvs_suite.journal_write_receipt.os.read", side_effect=PermissionError(13, PRIVATE, str(self.path))):
            with self.assertRaises(ValueError) as caught:
                journal_io.append_verified_event(self.path, SECOND, LIMIT, lambda: None)
        self.assertEqual(str(caught.exception), "Review journal I/O failed; inspect journal before retrying")
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(self.path.read_bytes(), FIRST + SECOND)

    def test_integration_callback_failure_does_not_append(self):
        with self.assertRaises(ValueError):
            journal_io.append_verified_event(self.path, SECOND, LIMIT,
                                             lambda: (_ for _ in ()).throw(ValueError("HOLD")))
        self.assertEqual(self.path.read_bytes(), FIRST)


if __name__ == "__main__":
    unittest.main()
