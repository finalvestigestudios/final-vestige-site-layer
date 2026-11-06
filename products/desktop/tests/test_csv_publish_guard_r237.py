"""R237 CSV publication privacy and descriptor custody; synthetic paths only."""
import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.csv_publish_guard import (
    adopt_csv_descriptor,
    raise_private_csv_failure,
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

    def test_collision_classification_sanitized(self):
        error = FileExistsError(errno.EEXIST, "secret client", str(self.target))
        with self.assertRaises(FileExistsError) as caught:
            raise_private_csv_failure(error)
        self.assertEqual(str(caught.exception), "CSV report destination already exists")
        self.assertNotIn(str(self.target), str(caught.exception))
        self.assertIsNone(caught.exception.filename)

    def test_permission_errno_preserved_and_redacted(self):
        error = PermissionError(errno.EACCES, "full payroll data", str(self.target))
        with self.assertRaises(OSError) as caught:
            raise_private_csv_failure(error)
        self.assertEqual(caught.exception.errno, errno.EACCES)
        self.assertEqual(str(caught.exception), "[Errno 13] CSV report publication failed")
        self.assertIsNone(caught.exception.filename)

    def test_disk_full_errno_preserved_and_redacted(self):
        with self.assertRaises(OSError) as caught:
            raise_private_csv_failure(OSError(errno.ENOSPC, "client path", str(self.target)))
        self.assertEqual(caught.exception.errno, errno.ENOSPC)
        self.assertNotIn(str(self.target), str(caught.exception))

    def test_untrusted_errno_boolean_defaults_to_eio(self):
        bad = OSError("secret")
        bad.errno = True
        with self.assertRaises(OSError) as caught:
            raise_private_csv_failure(bad)
        self.assertEqual(caught.exception.errno, errno.EIO)

    def test_untrusted_negative_errno_defaults_to_eio(self):
        bad = OSError("secret")
        bad.errno = -100
        with self.assertRaises(OSError) as caught:
            raise_private_csv_failure(bad)
        self.assertEqual(caught.exception.errno, errno.EIO)


if __name__ == "__main__":
    unittest.main()
