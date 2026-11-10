"""R329: an append must not silently accept a rewritten prior audit history.

All files are synthetic and local; no compliance decisions or live customer data.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from fvs_suite.journal_write_receipt import digest_pinned_prefix, require_exact_append_readback

BEFORE = b'{"audit":"prior-human-review","synthetic":true}\n'
EVENT = b'{"audit":"pending-review","synthetic":true}\n'

class PinnedPrefixR329(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix='r329-synthetic-')
        self.addCleanup(t.cleanup)
        self.path = Path(t.name) / 'PRIVATE_SYNTHETIC_LEDGER.review.jsonl'
        self.path.write_bytes(BEFORE)
        fd = os.open(self.path, os.O_RDWR | os.O_APPEND)
        self.addCleanup(os.close, fd)
        self.fd = fd

    def test_before_append_digest_matches_sha256(self):
        self.assertEqual(digest_pinned_prefix(self.fd, len(BEFORE)), hashlib.sha256(BEFORE).digest())

    def test_after_valid_append_prefix_still_matches(self):
        before = digest_pinned_prefix(self.fd, len(BEFORE))
        os.write(self.fd, EVENT)
        self.assertEqual(digest_pinned_prefix(self.fd, len(BEFORE)), before)
        require_exact_append_readback(self.fd, len(BEFORE), EVENT)

    def test_same_length_prefix_rewrite_disagrees_after_valid_append(self):
        before = digest_pinned_prefix(self.fd, len(BEFORE))
        with self.path.open('r+b') as rogue:
            rogue.write(b'X')
        os.write(self.fd, EVENT)
        require_exact_append_readback(self.fd, len(BEFORE), EVENT)
        self.assertNotEqual(digest_pinned_prefix(self.fd, len(BEFORE)), before)

    def test_empty_prefix_digest(self):
        self.path.write_bytes(b'')
        self.assertEqual(digest_pinned_prefix(self.fd, 0), hashlib.sha256(b'').digest())

    def test_truncated_prefix_rejected(self):
        with self.assertRaisesRegex(ValueError, 'changed during append'):
            digest_pinned_prefix(self.fd, len(BEFORE) + 4)

    def test_invalid_prefix_length_rejected(self):
        for value in (-1, '9', True, 1.0, None):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'length is invalid'):
                    digest_pinned_prefix(self.fd, value)

    def test_multichunk_prefix(self):
        data = b'Z' * (1024 * 1024 + 17)
        self.path.write_bytes(data)
        self.assertEqual(digest_pinned_prefix(self.fd, len(data)), hashlib.sha256(data).digest())

    def test_no_second_path_open(self):
        with mock.patch('fvs_suite.journal_write_receipt.os.open', side_effect=AssertionError('path reopen')):
            digest_pinned_prefix(self.fd, len(BEFORE))

    def test_readback_still_rejects_wrong_append(self):
        os.write(self.fd, EVENT.replace(b'pending', b'waiting'))
        with self.assertRaisesRegex(ValueError, 'appended bytes differ'):
            require_exact_append_readback(self.fd, len(BEFORE), EVENT)

    def test_prefix_snapshot_not_affected_by_mocked_readback_os_read(self):
        with mock.patch('fvs_suite.journal_write_receipt.os.read', side_effect=OSError('synthetic')):
            self.assertEqual(digest_pinned_prefix(self.fd, len(BEFORE)), hashlib.sha256(BEFORE).digest())

if __name__ == '__main__':
    unittest.main()
