"""R333: no duplicated premium audit FD survives a prefix-reader setup fault.

Uses synthetic local review evidence; no real financial data, binary releases,
network operations, or automated compliance decisions.
"""
from __future__ import annotations

import errno
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from fvs_suite import journal_write_receipt as receipt

PRIOR = b'{"review":"synthetic", "decision":"needs-human-review"}\n'
NEW = b'{"review":"synthetic", "decision":"pending-human-review"}\n'


class _EntryFault:
    """An fdopen-returned stream whose context entry never transferred custody."""
    def __init__(self, fd, error):
        self.fd = fd
        self.error = error

    def __enter__(self):
        raise self.error

    def __exit__(self, *args):
        raise AssertionError("__exit__ must not run when __enter__ failed")


class _ExitFault:
    def __init__(self, stream, error):
        self.stream = stream
        self.error = error

    def __enter__(self):
        self.stream.__enter__()
        return self.stream

    def __exit__(self, *args):
        self.stream.__exit__(*args)
        raise self.error


class PrefixFdOwnershipR333(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r333-synthetic-")
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "PRIVATE_ACCOUNT_DO_NOT_DISCLOSE.review.jsonl"
        self.path.write_bytes(PRIOR)
        self.fd = os.open(self.path, os.O_RDWR | os.O_APPEND)
        self.addCleanup(os.close, self.fd)

    def assert_original_open(self):
        self.assertEqual(os.fstat(self.fd).st_size, len(self.path.read_bytes()))

    def assert_duplicate_closed(self, duplicate):
        with self.assertRaises(OSError) as error:
            os.fstat(duplicate)
        self.assertEqual(error.exception.errno, errno.EBADF)
        self.assert_original_open()

    def test_real_prefix_hash(self):
        self.assertEqual(receipt.digest_pinned_prefix(self.fd, len(PRIOR)), hashlib.sha256(PRIOR).digest())

    def test_empty_prefix_digest(self):
        self.assertEqual(receipt.digest_pinned_prefix(self.fd, 0), hashlib.sha256(b"").digest())

    def test_prefix_hash_ignores_original_fd_offset(self):
        os.lseek(self.fd, len(PRIOR), os.SEEK_SET)
        self.assertEqual(receipt.digest_pinned_prefix(self.fd, len(PRIOR)), hashlib.sha256(PRIOR).digest())

    def test_prefix_after_valid_append_stays_identical(self):
        baseline = receipt.digest_pinned_prefix(self.fd, len(PRIOR))
        os.write(self.fd, NEW)
        self.assertEqual(receipt.digest_pinned_prefix(self.fd, len(PRIOR)), baseline)
        receipt.require_exact_append_readback(self.fd, len(PRIOR), NEW)

    def test_multichunk_hash(self):
        data = b"A" * (receipt.PREFIX_CHUNK_BYTES + 37)
        self.path.write_bytes(data)
        self.assertEqual(receipt.digest_pinned_prefix(self.fd, len(data)), hashlib.sha256(data).digest())

    def test_short_prefix_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "changed during append"):
            receipt.digest_pinned_prefix(self.fd, len(PRIOR) + 5)

    def test_invalid_byte_counts_rejected_before_dup(self):
        for value in (-1, True, "1", 1.0, None):
            with self.subTest(value=repr(value)):
                with mock.patch.object(receipt.os, "dup", side_effect=AssertionError("must not duplicate")):
                    with self.assertRaisesRegex(ValueError, "length is invalid"):
                        receipt.digest_pinned_prefix(self.fd, value)

    def test_fdopen_failure_releases_duplicate(self):
        real_dup = os.dup
        handles = []
        def capture(fd):
            result = real_dup(fd)
            handles.append(result)
            return result
        with mock.patch.object(receipt.os, "dup", side_effect=capture):
            with mock.patch.object(receipt.os, "fdopen", side_effect=PermissionError(errno.EACCES, "private")):
                with self.assertRaises(PermissionError):
                    receipt.digest_pinned_prefix(self.fd, len(PRIOR))
        self.assertEqual(len(handles), 1)
        self.assert_duplicate_closed(handles[0])

    def test_enter_failure_releases_duplicate(self):
        handles = []
        def failing_fdopen(fd, *_args, **_kwargs):
            handles.append(fd)
            return _EntryFault(fd, PermissionError(errno.EACCES, "synthetic"))
        with mock.patch.object(receipt.os, "fdopen", side_effect=failing_fdopen):
            with self.assertRaises(PermissionError):
                receipt.digest_pinned_prefix(self.fd, len(PRIOR))
        self.assertEqual(len(handles), 1)
        self.assert_duplicate_closed(handles[0])

    def test_interrupt_during_enter_releases_duplicate(self):
        handles = []
        def failing_fdopen(fd, *_args, **_kwargs):
            handles.append(fd)
            return _EntryFault(fd, KeyboardInterrupt())
        with mock.patch.object(receipt.os, "fdopen", side_effect=failing_fdopen):
            with self.assertRaises(KeyboardInterrupt):
                receipt.digest_pinned_prefix(self.fd, len(PRIOR))
        self.assert_duplicate_closed(handles[0])

    def test_exit_failure_does_not_leak_descriptor(self):
        handles = []
        real_fdopen = os.fdopen
        def failing_exit(fd, *args, **kwargs):
            handles.append(fd)
            return _ExitFault(real_fdopen(fd, *args, **kwargs), OSError("synthetic"))
        with mock.patch.object(receipt.os, "fdopen", side_effect=failing_exit):
            with self.assertRaises(OSError):
                receipt.digest_pinned_prefix(self.fd, len(PRIOR))
        self.assert_duplicate_closed(handles[0])

    def test_hash_failure_does_not_leak(self):
        handles = []
        real_fdopen = os.fdopen
        def capture(fd, *args, **kwargs):
            handles.append(fd)
            return real_fdopen(fd, *args, **kwargs)
        class BadHash:
            def update(self, value):
                raise ValueError("synthetic hash failure")
        with mock.patch.object(receipt.os, "fdopen", side_effect=capture):
            with mock.patch.object(receipt.hashlib, "sha256", return_value=BadHash()):
                with self.assertRaisesRegex(ValueError, "synthetic hash failure"):
                    receipt.digest_pinned_prefix(self.fd, len(PRIOR))
        self.assert_duplicate_closed(handles[0])

    def test_dup_failure_never_closes_original(self):
        with mock.patch.object(receipt.os, "dup", side_effect=PermissionError(errno.EACCES, "synthetic")):
            with self.assertRaises(PermissionError):
                receipt.digest_pinned_prefix(self.fd, len(PRIOR))
        self.assert_original_open()

    def test_no_path_reopen(self):
        with mock.patch.object(receipt.os, "open", side_effect=AssertionError("unexpected path open")):
            self.assertEqual(receipt.digest_pinned_prefix(self.fd, len(PRIOR)), hashlib.sha256(PRIOR).digest())

    def test_bad_appended_event_still_rejected(self):
        os.write(self.fd, NEW[:-2] + b"X\n")
        with self.assertRaisesRegex(ValueError, "appended bytes differ"):
            receipt.require_exact_append_readback(self.fd, len(PRIOR), NEW)


if __name__ == "__main__":
    unittest.main()
