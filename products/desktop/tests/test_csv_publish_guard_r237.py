"""R237 CSV publication privacy and descriptor custody; synthetic paths only."""
import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.csv_publish_guard import (
    adopt_csv_descriptor,
    private_csv_failure,
    require_free_destination,
)


class CSVPublicationGuardR237(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.target = self.root / "confidential-acme-payroll.csv"

    def test_missing_destination_allowed(self):
        require_free_destination(self.target)

    def test_existing_file_rejected_before_stage(self):
        self.target.write_bytes(b"original")
        with self.assertRaisesRegex(FileExistsError, "CSV report destination already exists"):
            require_free_destination(self.target)
        self.assertEqual(self.target.read_bytes(), b"original")

    def test_existing_folder_rejected_before_stage(self):
        self.target.mkdir()
        with self.assertRaises(FileExistsError):
            require_free_destination(self.target)

    @unittest.skipUnless(hasattr(os, "symlink"), "Symlinks unavailable")
    def test_dangling_symlink_rejected(self):
        self.target.symlink_to(self.root / "nonexistent-private.csv")
        with self.assertRaises(FileExistsError):
            require_free_destination(self.target)
        self.assertTrue(self.target.is_symlink())

    def test_lstat_permission_problem_not_treated_as_absence(self):
        with patch.object(Path, "lstat", side_effect=PermissionError(13, "private", str(self.target))):
            with self.assertRaises(PermissionError):
                require_free_destination(self.target)

    def test_fd_adopted_text_stream_is_utf8_bom(self):
        fd, temporary = tempfile.mkstemp(dir=self.root)
        self.addCleanup(lambda: os.path.exists(temporary) and os.unlink(temporary))
        with adopt_csv_descriptor(fd) as stream:
            stream.write("ID,amount\r\né,1.00\r\n")
            stream.flush()
            self.assertEqual(os.read(stream.fileno(), 1), b"")
        self.assertEqual(Path(temporary).read_bytes(), b"\xef\xbb\xbfID,amount\r\n\xc3\xa9,1.00\r\n")

    def test_fdopen_exception_closes_descriptor(self):
        fd, temporary = tempfile.mkstemp(dir=self.root)
        self.addCleanup(lambda: os.path.exists(temporary) and os.unlink(temporary))
        with patch("fvs_suite.csv_publish_guard.os.fdopen", side_effect=OSError(errno.EIO, "private data")):
            with self.assertRaises(OSError):
                adopt_csv_descriptor(fd)
        with self.assertRaises(OSError):
            os.fstat(fd)

    def test_fdopen_keyboard_interrupt_also_closes_descriptor(self):
        fd, temporary = tempfile.mkstemp(dir=self.root)
        self.addCleanup(lambda: os.path.exists(temporary) and os.unlink(temporary))
        with patch("fvs_suite.csv_publish_guard.os.fdopen", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                adopt_csv_descriptor(fd)
        with self.assertRaises(OSError):
            os.fstat(fd)

    def test_unexpected_close_error_does_not_mask_initial_exception(self):
        fd, temporary = tempfile.mkstemp(dir=self.root)
        self.addCleanup(lambda: os.path.exists(temporary) and os.unlink(temporary))
        real_close = os.close
        try:
            with patch("fvs_suite.csv_publish_guard.os.fdopen", side_effect=ValueError("fdopen failed")):
                with patch("fvs_suite.csv_publish_guard.os.close", side_effect=OSError(errno.EBADF, "close failed")):
                    with self.assertRaisesRegex(ValueError, "fdopen failed"):
                        adopt_csv_descriptor(fd)
        finally:
            real_close(fd)

    def assert_private_error(self, source, sanitized):
        """The new builder must never retain source paths or exception chains."""
        self.assertNotIn(str(self.target), repr(sanitized))
        self.assertNotIn("secret client", repr(sanitized))
        self.assertIsNone(sanitized.__context__)
        self.assertIsNone(sanitized.__cause__)
        self.assertIsNone(sanitized.filename)
        self.assertIsNone(sanitized.filename2)
        self.assertIsNot(sanitized, source)

    def test_collision_classification_sanitized(self):
        source = FileExistsError(errno.EEXIST, "secret client", str(self.target))
        sanitized = private_csv_failure(source)
        self.assertIsInstance(sanitized, FileExistsError)
        self.assertEqual(str(sanitized), "CSV report destination already exists")
        self.assert_private_error(source, sanitized)

    def test_permission_errno_preserved_and_redacted(self):
        source = PermissionError(errno.EACCES, "secret client", str(self.target))
        sanitized = private_csv_failure(source)
        self.assertIsInstance(sanitized, OSError)
        self.assertEqual(sanitized.errno, errno.EACCES)
        self.assertEqual(str(sanitized), "[Errno 13] CSV report publication failed")
        self.assert_private_error(source, sanitized)

    def test_disk_full_errno_preserved_and_redacted(self):
        source = OSError(errno.ENOSPC, "secret client", str(self.target))
        sanitized = private_csv_failure(source)
        self.assertEqual(sanitized.errno, errno.ENOSPC)
        self.assert_private_error(source, sanitized)

    def test_untrusted_errno_boolean_defaults_to_eio(self):
        source = OSError("secret client")
        source.errno = True
        sanitized = private_csv_failure(source)
        self.assertEqual(sanitized.errno, errno.EIO)
        self.assert_private_error(source, sanitized)

    def test_untrusted_negative_errno_defaults_to_eio(self):
        source = OSError("secret client")
        source.errno = -100
        sanitized = private_csv_failure(source)
        self.assertEqual(sanitized.errno, errno.EIO)
        self.assert_private_error(source, sanitized)

    def test_nested_private_cause_and_handler_context_not_retained(self):
        source = OSError(errno.EIO, "secret client", str(self.target))
        source.__cause__ = RuntimeError("secret client")
        try:
            raise source
        except OSError as caught:
            sanitized = private_csv_failure(caught)
        self.assertIsNone(sanitized.__cause__)
        self.assertIsNone(sanitized.__context__)
        self.assert_private_error(source, sanitized)


if __name__ == "__main__":
    unittest.main()
