"""R506: real-descriptor SHA256 receipt regression; synthetic bytes only."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from pe_digest_custody_r493 import PEDigestCustodyError, verify_pe_digest_stream

DATA = b'MZ-inert-synthetic-' * 300
HASH = hashlib.sha256(DATA).hexdigest()


class Fault:
    def __init__(self, stream, mode):
        self.stream, self.mode, self.reads = stream, mode, 0

    def fileno(self):
        return self.stream.fileno()

    def seek(self, value):
        result = self.stream.seek(value)
        if self.mode == 'bad-seek':
            return value + 1
        if self.mode == 'none-seek':
            return None
        if self.mode == 'bool-seek':
            return True
        if self.mode == 'private-seek':
            raise OSError('/private/claims.csv')
        return result

    def read(self, size):
        self.reads += 1
        if self.mode == 'private-read':
            raise OSError('/private/claims.csv')
        if self.mode == 'overread':
            return self.stream.read(size + 1)
        if self.mode == 'detached':
            old = self.stream.tell()
            data = self.stream.read(size)
            self.stream.seek(old)
            return data
        if self.mode == 'mutable':
            return bytearray(self.stream.read(size))
        if self.mode == 'early-eof':
            return b''
        return self.stream.read(size)

    def tell(self):
        if self.mode == 'private-tell':
            raise OSError('/private/claims.csv')
        if self.mode == 'wrong-tell':
            return self.stream.tell() + 1
        if self.mode == 'none-tell':
            return None
        if self.mode == 'bool-tell':
            return True
        if self.mode == 'late-tell' and self.reads >= 2:
            return self.stream.tell() - 1
        return self.stream.tell()


class DigestReceiptsR506(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'inert.bin'
        self.path.write_bytes(DATA)

    def reject(self, stream, *, maximum=8192, digest=HASH):
        caught = None
        try:
            verify_pe_digest_stream(stream, os.fstat(stream.fileno()), digest, maximum=maximum)
        except PEDigestCustodyError as exc:
            caught = exc
        self.assertIsNotNone(caught)
        self.assertEqual(str(caught), 'PE digest custody unavailable')
        self.assertIsNone(caught.__cause__)
        self.assertIsNone(caught.__context__)

    def test_real_descriptor_unbuffered(self):
        with self.path.open('rb', buffering=0) as stream:
            verify_pe_digest_stream(stream, os.fstat(stream.fileno()), HASH, maximum=8192)

    def test_buffered_stream_from_nonzero_offset(self):
        with self.path.open('rb') as stream:
            stream.seek(3)
            verify_pe_digest_stream(stream, os.fstat(stream.fileno()), HASH, maximum=8192)

    def test_reject_non_native_and_wrong_seek_receipts_before_read(self):
        for mode in ('bad-seek', 'none-seek', 'bool-seek'):
            with self.subTest(mode=mode), self.path.open('rb', buffering=0) as stream:
                bad = Fault(stream, mode)
                self.reject(bad)
                self.assertEqual(bad.reads, 0)

    def test_reject_disconnected_read_progress(self):
        with self.path.open('rb', buffering=0) as stream:
            self.reject(Fault(stream, 'detached'))

    def test_reject_postread_tell_receipts(self):
        for mode in ('wrong-tell', 'none-tell', 'bool-tell'):
            with self.subTest(mode=mode), self.path.open('rb', buffering=0) as stream:
                self.reject(Fault(stream, mode))

    def test_reject_oversized_read_receipt(self):
        large = b'z' * (1_048_576 + 37)
        self.path.write_bytes(large)
        with self.path.open('rb', buffering=0) as stream:
            self.reject(Fault(stream, 'overread'), maximum=len(large))

    def test_reject_early_eof(self):
        with self.path.open('rb', buffering=0) as stream:
            self.reject(Fault(stream, 'early-eof'))

    def test_reject_mutable_read_receipt(self):
        with self.path.open('rb', buffering=0) as stream:
            self.reject(Fault(stream, 'mutable'))

    def test_private_stream_errors_are_fixed_unchained(self):
        for mode in ('private-seek', 'private-read', 'private-tell'):
            with self.subTest(mode=mode), self.path.open('rb', buffering=0) as stream:
                self.reject(Fault(stream, mode))

    def test_multichunk_real_stream_passes(self):
        large = b'z' * (1_048_576 + 37)
        self.path.write_bytes(large)
        with self.path.open('rb', buffering=0) as stream:
            verify_pe_digest_stream(stream, os.fstat(stream.fileno()),
                                    hashlib.sha256(large).hexdigest(), maximum=len(large))

    def test_multichunk_wrong_second_position_rejected(self):
        large = b'z' * (1_048_576 + 37)
        self.path.write_bytes(large)
        with self.path.open('rb', buffering=0) as stream:
            self.reject(Fault(stream, 'late-tell'), maximum=len(large))

    def test_changed_digest_still_fails(self):
        with self.path.open('rb', buffering=0) as stream:
            self.reject(stream, digest='0' * 64)


if __name__ == '__main__':
    unittest.main()
