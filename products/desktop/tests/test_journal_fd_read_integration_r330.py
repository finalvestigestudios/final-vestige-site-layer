"""R330: public premium journal read must retain privacy and close a failed duplicated fd.

Full-repository test; executes in Windows and Ubuntu source discovery when CI runs.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from fvs_suite.journal_io import read_regular_bytes

PRIVATE = "PRIVATE_SYNTHETIC_CLIENT_ACCOUNT_330"
EVIDENCE = b'{"review":"manual","synthetic":true}\n'
DENIAL = "Review evidence cannot be read; inspect local input permissions"


class JournalDuplicateIntegrationR330(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="r330-public-read-")
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / (PRIVATE + ".jsonl")
        self.path.write_bytes(EVIDENCE)

    def test_normal_read_remains_identical(self):
        self.assertEqual(read_regular_bytes(self.path, 4096, "Review journal"), EVIDENCE)

    def test_fdopen_denial_is_redacted_and_duplicate_closed(self):
        native_dup = os.dup
        copies = []
        def tracked(fd):
            duplicated = native_dup(fd)
            copies.append(duplicated)
            return duplicated
        with mock.patch("fvs_suite.journal_fd_read.os.dup", side_effect=tracked):
            with mock.patch("fvs_suite.journal_fd_read.os.fdopen",
                            side_effect=PermissionError(13, PRIVATE, str(self.path))):
                with self.assertRaises(ValueError) as caught:
                    read_regular_bytes(self.path, 4096, "Review journal")
        self.assertEqual(str(caught.exception), DENIAL)
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(PRIVATE, repr(caught.exception))
        self.assertEqual(len(copies), 1)
        with self.assertRaises(OSError):
            os.fstat(copies[0])
        self.assertEqual(self.path.read_bytes(), EVIDENCE)

    def test_overlimit_read_still_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "allowed size"):
            read_regular_bytes(self.path, 4, "Review journal")
        self.assertEqual(self.path.read_bytes(), EVIDENCE)


if __name__ == "__main__":
    unittest.main()
