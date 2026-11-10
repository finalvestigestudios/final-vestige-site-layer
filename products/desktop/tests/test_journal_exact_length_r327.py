"""R327: a successful premium journal read must return ALL observed bytes.

Synthetic private-looking test names only. Fault injection models a shortened
regular-file read with unchanged fstat and pathname metadata, not a claim that
an ordinary local disk will produce this condition without external faults.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from fvs_suite import journal_io

EVENT = b'{"synthetic_review":true,"decision":"needs_evidence"}\n'
PRIVATE = "PRIVATE_LEDGER_ACCOUNT_789123.review.jsonl"
KIND = "Review journal"


class ShortReadStream:
    def __init__(self, source, response):
        self.source, self.response = source, response

    def __enter__(self):
        self.source.__enter__()
        return self

    def __exit__(self, *exc):
        return self.source.__exit__(*exc)

    def read(self, count):
        self.source.read(count)
        return self.response


class PremiumJournalExactLengthR327(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r327-synthetic-")
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / PRIVATE
        self.path.write_bytes(EVENT)

    def _override_read(self, response):
        original = os.fdopen
        def substitute(descriptor, mode, *args, **kwargs):
            return ShortReadStream(original(descriptor, mode, *args, **kwargs), response)
        return mock.patch.object(journal_io.os, "fdopen", side_effect=substitute)

    def _hold(self, response):
        with self._override_read(response):
            with self.assertRaises(ValueError) as context:
                journal_io.read_regular_bytes(self.path, len(EVENT) + 16, KIND)
        self.assertIn("changed during read", str(context.exception))
        self.assertNotIn(PRIVATE, str(context.exception))
        self.assertIsNone(context.exception.__context__)
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_normal_full_read_exact(self):
        self.assertEqual(journal_io.read_regular_bytes(self.path, len(EVENT), KIND), EVENT)

    def test_exact_metadata_length_even_with_generous_bound(self):
        self.assertEqual(journal_io.read_regular_bytes(self.path, 4096, KIND), EVENT)

    def test_empty_regular_file_allowed(self):
        self.path.write_bytes(b"")
        self.assertEqual(journal_io.read_regular_bytes(self.path, 4096, KIND), b"")

    def test_exact_one_byte_file_allowed(self):
        self.path.write_bytes(b"x")
        self.assertEqual(journal_io.read_regular_bytes(self.path, 1, KIND), b"x")

    def test_bounds_over_size_rejected_without_modification(self):
        with self.assertRaises(ValueError):
            journal_io.read_regular_bytes(self.path, len(EVENT) - 1, KIND)
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_zero_byte_short_read_rejected_despite_unchanged_metadata(self):
        self._hold(b"")

    def test_one_byte_short_read_rejected_despite_unchanged_metadata(self):
        self._hold(EVENT[:1])

    def test_half_length_short_read_rejected_despite_unchanged_metadata(self):
        self._hold(EVENT[:len(EVENT)//2])

    def test_one_byte_missing_at_end_rejected_despite_unchanged_metadata(self):
        self._hold(EVENT[:-1])

    def test_spurious_extra_bytes_rejected_even_under_maximum(self):
        self._hold(EVENT + b"X")

    def test_consistent_injected_full_length_is_accepted_not_claimed_authenticated(self):
        with self._override_read(EVENT):
            self.assertEqual(journal_io.read_regular_bytes(self.path, 4096, KIND), EVENT)

    def test_append_existing_journal_keeps_full_bytes_and_callback(self):
        checked = []
        journal_io.append_verified_event(self.path, EVENT, 4096, lambda: checked.append(True))
        self.assertEqual(checked, [True])
        self.assertEqual(self.path.read_bytes(), EVENT + EVENT)

    def test_file_permission_error_is_private_path_free(self):
        original = os.fdopen
        def denied(descriptor, mode, *args, **kwargs):
            stream = original(descriptor, mode, *args, **kwargs)
            class Denied:
                def __enter__(self):
                    return self
                def __exit__(self, *exc):
                    stream.close()
                def read(self, count):
                    raise PermissionError(13, PRIVATE, str(self_path))
            return Denied()
        self_path = self.path
        with mock.patch.object(journal_io.os, "fdopen", side_effect=denied):
            with self.assertRaises(ValueError) as caught:
                journal_io.read_regular_bytes(self.path, 4096, KIND)
        self.assertEqual(str(caught.exception),
                         "Review evidence cannot be read; inspect local input permissions")
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertIsNone(caught.exception.__context__)


if __name__ == "__main__":
    unittest.main()
