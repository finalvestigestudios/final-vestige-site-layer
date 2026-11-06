"""R233 strict, deterministic private text publication error safety tests."""
import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.atomic_text import publish_text


class AtomicTextIOPrivacyR233(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.secret = 'CLIENT-SECRET-39107'
        self.target = self.root / f'{self.secret}-grant-report.txt'

    def assert_no_parts(self):
        self.assertEqual(list(self.root.glob('.*.partial')), [])

    def assert_redacted(self, err, *, collision=False, expected_errno=None):
        self.assertNotIn(self.secret, str(err))
        self.assertNotIn(str(self.root), str(err))
        self.assertNotIn('private token', str(err))
        self.assertEqual(str(err), 'Text report destination already exists' if collision else
                         ('[Errno %d] Text report publication failed' % expected_errno))
        self.assertIsNone(getattr(err, 'filename', None))
        self.assertIsNone(getattr(err, 'filename2', None))

    def test_real_existing_destination_uses_generic_collision(self):
        self.target.write_bytes(b'original')
        with self.assertRaises(FileExistsError) as failure:
            publish_text(self.target, 'new')
        self.assert_redacted(failure.exception, collision=True)
        self.assertEqual(self.target.read_bytes(), b'original')
        self.assert_no_parts()

    def test_unexpected_lstat_permission_error_is_redacted_before_staging(self):
        def deny(*_args, **_kwargs):
            raise PermissionError(errno.EACCES, 'private token '+self.secret, str(self.target))
        with patch('fvs_suite.atomic_text.Path.lstat', side_effect=deny):
            with patch('fvs_suite.atomic_text.tempfile.mkstemp', side_effect=AssertionError('staged')):
                with self.assertRaises(PermissionError) as failure:
                    publish_text(self.target, 'private token')
        self.assert_redacted(failure.exception, expected_errno=errno.EACCES)
        self.assertFalse(self.target.exists())

    def test_mkstemp_oserror_redacted_and_not_staged(self):
        with patch('fvs_suite.atomic_text.tempfile.mkstemp', side_effect=OSError(errno.ENOSPC, 'private token', str(self.root))):
            with self.assertRaises(OSError) as failure:
                publish_text(self.target, 'data')
        self.assert_redacted(failure.exception, expected_errno=errno.ENOSPC)
        self.assertFalse(self.target.exists())
        self.assert_no_parts()

    def test_fdopen_permission_error_closes_and_redacts(self):
        real_create = tempfile.mkstemp
        native_fds = []
        def create(*args, **kwargs):
            fd, path = real_create(*args, **kwargs)
            native_fds.append(fd)
            return fd, path
        with patch('fvs_suite.atomic_text.tempfile.mkstemp', side_effect=create):
            with patch('fvs_suite.atomic_text.os.fdopen', side_effect=PermissionError(errno.EACCES, 'private token', str(self.target))):
                with self.assertRaises(PermissionError) as failure:
                    publish_text(self.target, 'data')
        self.assert_redacted(failure.exception, expected_errno=errno.EACCES)
        self.assertEqual(len(native_fds), 1)
        with self.assertRaises(OSError):
            os.fstat(native_fds[0])
        self.assert_no_parts()

    def test_fsync_path_leak_is_redacted_and_partial_deleted(self):
        with patch('fvs_suite.atomic_text.os.fsync', side_effect=OSError(errno.EIO, 'private token', str(self.target))):
            with self.assertRaises(OSError) as failure:
                publish_text(self.target, 'data')
        self.assert_redacted(failure.exception, expected_errno=errno.EIO)
        self.assertFalse(self.target.exists())
        self.assert_no_parts()

    def test_publication_permission_error_redacted(self):
        symbol = 'os.rename' if os.name == 'nt' else 'os.link'
        with patch('fvs_suite.atomic_text.'+symbol, side_effect=PermissionError(errno.EACCES, 'private token', str(self.target))):
            with self.assertRaises(PermissionError) as failure:
                publish_text(self.target, 'data')
        self.assert_redacted(failure.exception, expected_errno=errno.EACCES)
        self.assertFalse(self.target.exists())
        self.assert_no_parts()

    def test_publication_late_collision_redacted(self):
        symbol = 'os.rename' if os.name == 'nt' else 'os.link'
        with patch('fvs_suite.atomic_text.'+symbol, side_effect=FileExistsError(errno.EEXIST, 'private token', str(self.target))):
            with self.assertRaises(FileExistsError) as failure:
                publish_text(self.target, 'data')
        self.assert_redacted(failure.exception, collision=True)
        self.assertFalse(self.target.exists())
        self.assert_no_parts()

    def test_unknown_errno_uses_generic_io_error_without_leaking_text(self):
        with patch('fvs_suite.atomic_text.os.fsync', side_effect=OSError('private token '+self.secret)):
            with self.assertRaises(OSError) as failure:
                publish_text(self.target, 'data')
        self.assert_redacted(failure.exception, expected_errno=errno.EIO)
        self.assertEqual(failure.exception.errno, errno.EIO)
        self.assert_no_parts()

    def test_publication_io_error_keeps_native_errno_for_callers(self):
        symbol = 'os.rename' if os.name == 'nt' else 'os.link'
        with patch('fvs_suite.atomic_text.'+symbol, side_effect=OSError(errno.ENOSPC, 'private token', str(self.target))):
            with self.assertRaises(OSError) as failure:
                publish_text(self.target, 'data')
        self.assert_redacted(failure.exception, expected_errno=errno.ENOSPC)
        self.assertEqual(failure.exception.errno, errno.ENOSPC)
        self.assert_no_parts()

    def test_existing_dangling_symlink_is_not_followed(self):
        try:
            self.target.symlink_to(self.root / 'absent.txt')
        except (OSError, NotImplementedError):
            self.skipTest('symlinks unavailable on this host')
        with self.assertRaises(FileExistsError) as failure:
            publish_text(self.target, 'data')
        self.assert_redacted(failure.exception, collision=True)
        self.assertTrue(self.target.is_symlink())
        self.assert_no_parts()

    def test_oserror_traceback_suppresses_original_sensitive_exception(self):
        import traceback
        with patch('fvs_suite.atomic_text.os.fsync', side_effect=OSError(errno.EIO, 'private token '+self.secret, str(self.target))):
            try:
                publish_text(self.target, 'data')
            except OSError as exc:
                rendered = ''.join(traceback.format_exception(exc))
                self.assertNotIn(self.secret, rendered)
                self.assertNotIn('private token', rendered)
                self.assertTrue(exc.__suppress_context__)
            else:
                self.fail('expected failure')
        self.assert_no_parts()

    def test_success_byte_identity_and_private_filename(self):
        content = 'before\r\nafter €\n'
        self.assertEqual(publish_text(self.target, content), self.target)
        self.assertEqual(self.target.read_bytes(), content.encode('utf-8'))
        self.assert_no_parts()



if __name__ == '__main__':
    unittest.main()
