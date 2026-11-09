"""R300: committed atomic publisher must never retain confidential error chains.

Synthetic names and fault injection only. No customer files, GUI or network.
"""
from __future__ import annotations

import errno
import os
import tempfile
import traceback
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.atomic_text import publish_text

SECRET = "PRIVATE-CLIENT-ACCOUNT-80193"


class AtomicTextContextPrivacyR300(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r300-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.target = self.root / (SECRET + "-policy-evidence.txt")

    def clean(self, action, expected_type=OSError, *, code=None, fragment=None):
        with self.assertRaises(expected_type) as observed:
            action()
        error = observed.exception
        self.assertIsNone(error.__context__, "original private error retained in __context__")
        self.assertIsNone(error.__cause__, "original private error retained in __cause__")
        self.assertTrue(error.__suppress_context__)
        self.assertNotIn(SECRET, repr(error))
        self.assertNotIn(SECRET, "".join(traceback.format_exception(error)))
        self.assertNotIn(str(self.root), repr(error))
        self.assertIsNone(getattr(error, "filename", None))
        self.assertIsNone(getattr(error, "filename2", None))
        if code is not None:
            self.assertEqual(error.errno, code)
        if fragment is not None:
            self.assertIn(fragment, str(error))
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.glob(".fvs-text-*.partial")), [])
        return error

    def test_lstat_permission_has_no_private_hidden_chain(self):
        with patch("fvs_suite.atomic_text.Path.lstat",
                   side_effect=PermissionError(errno.EACCES, SECRET, str(self.target))):
            self.clean(lambda: publish_text(self.target, "Evidence"), PermissionError,
                       code=errno.EACCES)

    def test_mkstemp_oserror_has_no_hidden_chain(self):
        with patch("fvs_suite.atomic_text.tempfile.mkstemp",
                   side_effect=OSError(errno.ENOSPC, SECRET, str(self.target))):
            self.clean(lambda: publish_text(self.target, "Evidence"), OSError,
                       code=errno.ENOSPC)

    def test_mkstemp_non_oserror_has_no_hidden_chain(self):
        with patch("fvs_suite.atomic_text.tempfile.mkstemp",
                   side_effect=RuntimeError(SECRET)):
            self.clean(lambda: publish_text(self.target, "Evidence"), ValueError,
                       fragment="staging could not be created")

    def test_fdopen_oserror_has_no_hidden_chain_or_leaked_descriptor(self):
        captured = []
        native = tempfile.mkstemp
        def create(*a, **kw):
            fd, name = native(*a, **kw)
            captured.append(fd)
            return fd, name
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=create), patch(
                "fvs_suite.atomic_text.os.fdopen",
                side_effect=PermissionError(errno.EACCES, SECRET, str(self.target))):
            self.clean(lambda: publish_text(self.target, "Evidence"), PermissionError,
                       code=errno.EACCES)
        self.assertEqual(len(captured), 1)
        with self.assertRaises(OSError):
            os.fstat(captured[0])

    def test_fdopen_non_oserror_has_no_hidden_chain_or_staging(self):
        with patch("fvs_suite.atomic_text.os.fdopen", side_effect=RuntimeError(SECRET)):
            self.clean(lambda: publish_text(self.target, "Evidence"), ValueError,
                       fragment="staging could not be opened")

    def test_fsync_oserror_has_no_hidden_chain(self):
        with patch("fvs_suite.atomic_text.os.fsync",
                   side_effect=OSError(errno.EIO, SECRET, str(self.target))):
            self.clean(lambda: publish_text(self.target, "Evidence"), OSError,
                       code=errno.EIO)

    def test_fsync_oserror_with_nested_private_cause_discarded(self):
        error = OSError(errno.EIO, SECRET, str(self.target))
        try:
            raise ValueError(SECRET)
        except ValueError as cause:
            error.__cause__ = cause
        with patch("fvs_suite.atomic_text.os.fsync", side_effect=error):
            self.clean(lambda: publish_text(self.target, "Evidence"), OSError,
                       code=errno.EIO)

    def test_publication_permission_has_no_private_hidden_chain(self):
        name = "os.rename" if os.name == "nt" else "os.link"
        with patch("fvs_suite.atomic_text." + name,
                   side_effect=PermissionError(errno.EACCES, SECRET, str(self.target))):
            self.clean(lambda: publish_text(self.target, "Evidence"), PermissionError,
                       code=errno.EACCES)

    def test_late_collision_has_no_private_hidden_chain(self):
        name = "os.rename" if os.name == "nt" else "os.link"
        with patch("fvs_suite.atomic_text." + name,
                   side_effect=FileExistsError(errno.EEXIST, SECRET, str(self.target))):
            self.clean(lambda: publish_text(self.target, "Evidence"), FileExistsError,
                       fragment="destination already exists")

    def test_real_existing_file_remains_unchanged_without_private_hidden_chain(self):
        self.target.write_bytes(b"OLD\n")
        try:
            with self.assertRaises(FileExistsError) as caught:
                publish_text(self.target, "NEW\n")
            error = caught.exception
            self.assertIsNone(error.__context__)
            self.assertIsNone(error.__cause__)
            self.assertEqual(str(error), "Text report destination already exists")
            self.assertEqual(self.target.read_bytes(), b"OLD\n")
            self.assertEqual(list(self.root.glob(".fvs-text-*.partial")), [])
        finally:
            self.target.unlink()

    def test_unknown_errno_default_is_eio_without_private_hidden_chain(self):
        with patch("fvs_suite.atomic_text.os.fsync", side_effect=OSError(SECRET)):
            self.clean(lambda: publish_text(self.target, "Evidence"), OSError, code=errno.EIO)

    def test_real_utf8_crlf_and_unicode_are_byte_exact(self):
        raw = "Version 1\r\nCafé \u20ac\n"
        result = publish_text(self.target, raw)
        self.assertEqual(result, self.target)
        self.assertEqual(self.target.read_bytes(), raw.encode("utf-8"))
        self.assertEqual(list(self.root.glob(".fvs-text-*.partial")), [])

    def test_invalid_nul_is_rejected_before_staging(self):
        with self.assertRaisesRegex(ValueError, "Invalid text report content"):
            publish_text(self.target, "a\x00b")
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.glob(".fvs-text-*.partial")), [])

    def test_interrupt_fd_adoption_is_preserved_and_file_removed(self):
        with patch("fvs_suite.atomic_text.os.fdopen", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                publish_text(self.target, "Evidence")
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.glob(".fvs-text-*.partial")), [])

    def test_memory_error_during_staging_is_not_swallowed(self):
        with patch("fvs_suite.atomic_text.tempfile.mkstemp", side_effect=MemoryError):
            with self.assertRaises(MemoryError):
                publish_text(self.target, "Evidence")
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
