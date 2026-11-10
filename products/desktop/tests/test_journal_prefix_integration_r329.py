"""R329: full premium journal append entrypoint custody with synthetic local files."""
from __future__ import annotations
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from fvs_suite import journal_io

BEFORE = b'{"audit":"prior-human-review","synthetic":true}\n'
EVENT = b'{"audit":"pending-review","synthetic":true}\n'
PRIVATE = 'PRIVATE_BANK_IDENTIFIER_572 REVIEW.jsonl'

class PrefixIntegrationR329(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix='r329-app-')
        self.addCleanup(t.cleanup)
        self.path = Path(t.name) / PRIVATE
        self.path.write_bytes(BEFORE)

    def append(self):
        journal_io.append_verified_event(self.path, EVENT, 4096, lambda: self.assertEqual(self.path.read_bytes(), BEFORE))

    def test_healthy_existing_journal(self):
        self.append()
        self.assertEqual(self.path.read_bytes(), BEFORE + EVENT)

    def test_healthy_new_journal(self):
        self.path.unlink()
        journal_io.append_verified_event(self.path, EVENT, 4096, lambda: None)
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_rejects_historical_rewrite_during_correct_append(self):
        original_write = os.write
        def rogue_write(fd, data):
            with self.path.open('r+b') as rogue:
                rogue.write(b'X')
            return original_write(fd, data)
        with mock.patch.object(journal_io.os, 'write', side_effect=rogue_write):
            with self.assertRaisesRegex(ValueError, 'previous events changed during append') as caught:
                self.append()
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(self.path.read_bytes(), b'X' + BEFORE[1:] + EVENT)

    def test_bad_prefix_read_error_is_private_path_redacted(self):
        with mock.patch.object(journal_io, 'digest_pinned_prefix', side_effect=PermissionError(13, PRIVATE, str(self.path))):
            with self.assertRaises(ValueError) as caught:
                self.append()
        self.assertEqual(str(caught.exception), 'Review journal I/O failed; inspect journal before retrying')
        self.assertIsNone(caught.exception.__context__)
        self.assertEqual(self.path.read_bytes(), BEFORE)

    def test_detects_prefix_changes_during_prewrite_snapshot(self):
        native = journal_io.digest_pinned_prefix
        def rogue(fd, length):
            out = native(fd, length)
            with self.path.open('r+b') as f:
                f.write(b'X')
            return out
        with mock.patch.object(journal_io, 'digest_pinned_prefix', side_effect=rogue):
            with self.assertRaisesRegex(ValueError, 'changed while binding prior events'):
                self.append()
        self.assertEqual(self.path.read_bytes(), b'X' + BEFORE[1:])

    def test_does_not_auto_approve_compliance(self):
        seen = []
        journal_io.append_verified_event(self.path, EVENT, 4096, lambda: seen.append('verified-only'))
        self.assertEqual(seen, ['verified-only'])
        self.assertEqual(self.path.read_bytes(), BEFORE + EVENT)

if __name__ == '__main__':
    unittest.main()
