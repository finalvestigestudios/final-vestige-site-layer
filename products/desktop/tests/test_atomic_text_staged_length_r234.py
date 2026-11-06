"""R234: never publish partial/expanded UTF-8 policy or grant evidence.

Synthetic-only local fixtures; covers real local file descriptors with fault-
injected file-like wrappers, not a Windows executable acceptance claim.
"""
import errno
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fvs_suite.atomic_text import publish_text


_ACTUAL = object()


class _WriteShim:
    """Intercept one real staged fd to simulate legal/hostile write outcomes."""

    def __init__(self, real_stream, accepted=None, reported=_ACTUAL, extra=b""):
        self._stream = real_stream
        self.accepted = accepted
        self.reported = reported
        self.extra = extra

    def write(self, payload):
        accepted = payload if self.accepted is None else payload[:self.accepted]
        self._stream.write(accepted)
        if self.extra:
            self._stream.write(self.extra)
        return len(accepted) if self.reported is _ACTUAL else self.reported

    def flush(self):
        return self._stream.flush()

    def fileno(self):
        return self._stream.fileno()

    def __enter__(self):
        self._stream.__enter__()
        return self

    def __exit__(self, *args):
        return self._stream.__exit__(*args)


class TextStageLengthR234(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.secret = 'CONFIDENTIAL-CLIENT-5541'
        self.target = self.root / (self.secret + '-manifest.txt')
        self.content = 'claim\t€100.01\r\nref\tΔ\n'
        self.payload = self.content.encode('utf-8')

    def check_clean(self):
        self.assertFalse(self.target.exists())
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(list(self.root.glob('.*.partial')), [])

    def check_private_error(self, error):
        self.assertIsInstance(error, OSError)
        self.assertEqual(error.errno, errno.EIO)
        self.assertEqual(str(error), f'[Errno {errno.EIO}] Text report publication failed')
        self.assertNotIn(self.secret, str(error))
        self.assertNotIn(str(self.root), str(error))
        self.assertIsNone(error.filename)
        self.check_clean()

    def attempt(self, *, accepted=None, reported=_ACTUAL, extra=b''):
        fdopen = os.fdopen
        called = []
        def wrapper(*args, **kwargs):
            called.append(True)
            return _WriteShim(fdopen(*args, **kwargs), accepted, reported, extra)
        with patch('fvs_suite.atomic_text.os.fdopen', side_effect=wrapper):
            with self.assertRaises(OSError) as failure:
                publish_text(self.target, self.content)
        self.assertEqual(len(called), 1)
        self.check_private_error(failure.exception)

    def test_short_one_byte_writes_fail_closed(self):
        self.attempt(accepted=1)

    def test_short_half_writes_fail_closed(self):
        self.attempt(accepted=len(self.payload)//2)

    def test_zero_byte_write_fails_closed(self):
        self.attempt(accepted=0)

    def test_none_write_result_fails_closed(self):
        self.attempt(accepted=2, reported=None)

    def test_arbitrary_write_object_result_fails_closed(self):
        self.attempt(accepted=2, reported=object())

    def test_boolean_true_result_fails_closed(self):
        self.attempt(accepted=2, reported=True)

    def test_boolean_false_result_fails_closed(self):
        self.attempt(accepted=2, reported=False)

    def test_negative_write_result_fails_closed(self):
        self.attempt(accepted=2, reported=-1)

    def test_oversized_write_result_fails_closed(self):
        self.attempt(accepted=2, reported=len(self.payload)+100)

    def test_int_subclass_write_result_fails_closed(self):
        class ForgedInt(int):
            pass
        self.attempt(accepted=2, reported=ForgedInt(len(self.payload)))

    def test_lying_full_write_return_does_not_publish_truncated_report(self):
        self.attempt(accepted=3, reported=len(self.payload))

    def test_extra_staged_bytes_are_not_silently_published(self):
        self.attempt(extra=b'FORGED TAIL', reported=len(self.payload))

    def test_staging_fstat_error_is_private_and_no_publish(self):
        with patch('fvs_suite.atomic_text.os.fstat', side_effect=OSError(errno.EIO, self.secret, str(self.target))):
            with self.assertRaises(OSError) as failure:
                publish_text(self.target, self.content)
        self.check_private_error(failure.exception)

    def test_staging_fstat_short_size_fails_closed(self):
        with patch('fvs_suite.atomic_text.os.fstat', return_value=SimpleNamespace(st_size=len(self.payload)-1)):
            with self.assertRaises(OSError) as failure:
                publish_text(self.target, self.content)
        self.check_private_error(failure.exception)

    def test_staging_fstat_extended_size_fails_closed(self):
        with patch('fvs_suite.atomic_text.os.fstat', return_value=SimpleNamespace(st_size=len(self.payload)+1)):
            with self.assertRaises(OSError) as failure:
                publish_text(self.target, self.content)
        self.check_private_error(failure.exception)

    def test_good_unicode_bytes_and_line_endings_round_trip(self):
        self.assertEqual(publish_text(self.target, self.content), self.target)
        self.assertEqual(self.target.read_bytes(), self.payload)
        self.assertEqual(list(self.root.glob('.*.partial')), [])

    def test_empty_document_is_valid_and_exact(self):
        self.assertEqual(publish_text(self.target, ''), self.target)
        self.assertEqual(self.target.read_bytes(), b'')
        self.assertEqual(list(self.root.glob('.*.partial')), [])

    def test_existing_evidence_is_never_replaced(self):
        self.target.write_bytes(b'previous notarized evidence')
        with self.assertRaisesRegex(FileExistsError, '^Text report destination already exists$'):
            publish_text(self.target, self.content)
        self.assertEqual(self.target.read_bytes(), b'previous notarized evidence')
        self.assertEqual(list(self.root.glob('.*.partial')), [])

    def test_short_write_never_fsyncs_or_publishes(self):
        original_fdopen = os.fdopen
        with patch('fvs_suite.atomic_text.os.fdopen', side_effect=lambda *a, **kw: _WriteShim(original_fdopen(*a, **kw), accepted=1)):
            with patch('fvs_suite.atomic_text.os.fsync', side_effect=AssertionError('unexpected fsync')):
                with self.assertRaises(OSError) as failure:
                    publish_text(self.target, self.content)
        self.check_private_error(failure.exception)

    def test_valid_stage_invokes_fstat_and_fsync_before_publishing(self):
        real_fstat, real_fsync = os.fstat, os.fsync
        order = []
        def st(fd):
            order.append('fstat')
            return real_fstat(fd)
        def sync(fd):
            order.append('fsync')
            return real_fsync(fd)
        with patch('fvs_suite.atomic_text.os.fstat', side_effect=st):
            with patch('fvs_suite.atomic_text.os.fsync', side_effect=sync):
                publish_text(self.target, self.content)
        self.assertEqual(order, ['fstat','fsync'])
        self.assertEqual(self.target.read_bytes(), self.payload)


if __name__ == '__main__':
    unittest.main()
