"""R326: premium review I/O must not hang if a checked path becomes a FIFO.

All evidence here is synthetic. POSIX race cases execute in killable children;
Windows checks real ordinary-file behavior without claiming POSIX FIFO safety.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from fvs_suite import journal_io

EVENT = b'{"synthetic":true}\n'

_CHILD = r'''
import os, sys
from pathlib import Path
from fvs_suite import journal_io
path, operation = Path(sys.argv[1]), sys.argv[2]
original_open = os.open
swapped = False
verified = False

def race_open(target, flags, *args, **kwargs):
    global swapped
    if not swapped and Path(target) == path:
        swapped = True
        os.unlink(target)
        os.mkfifo(target)
    return original_open(target, flags, *args, **kwargs)

def verify():
    global verified
    verified = True

journal_io.os.open = race_open
try:
    if operation == 'read':
        journal_io.read_regular_bytes(path, 4096, 'Review journal')
    else:
        journal_io.append_verified_event(path, b'{"synthetic":true}\n', 4096, verify)
except ValueError as exc:
    if (swapped and not verified and str(path) not in str(exc)
            and 'PRIVATE_LEDGER' not in str(exc) and exc.__context__ is None):
        print('HOLD')
        raise SystemExit(0)
    raise SystemExit(3)
raise SystemExit(4)
'''


class PremiumJournalFifoOpenR326(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r326-synthetic-")
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "PRIVATE_LEDGER.journal.jsonl"
        self.path.write_bytes(EVENT)

    def test_read_regular_file_unchanged(self):
        self.assertEqual(journal_io.read_regular_bytes(self.path, 4096, 'Review journal'), EVENT)
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_append_existing_regular_file(self):
        seen = []
        journal_io.append_verified_event(self.path, EVENT, 4096, lambda: seen.append(True))
        self.assertEqual(seen, [True])
        self.assertEqual(self.path.read_bytes(), EVENT * 2)

    def test_append_new_regular_file(self):
        self.path.unlink()
        journal_io.append_verified_event(self.path, EVENT, 4096, lambda: None)
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_failed_verification_does_not_append(self):
        def refuse():
            raise ValueError('Synthetic verification denied')
        with self.assertRaises(ValueError):
            journal_io.append_verified_event(self.path, EVENT, 4096, refuse)
        self.assertEqual(self.path.read_bytes(), EVENT)

    def test_flags_preserve_read_write_and_no_follow(self):
        for base in (os.O_RDONLY, os.O_WRONLY | os.O_APPEND, os.O_WRONLY | os.O_CREAT | os.O_EXCL):
            with self.subTest(base=base):
                flags = journal_io._flags(base)
                self.assertEqual(flags & base, base)
                if hasattr(os, 'O_NONBLOCK'):
                    self.assertNotEqual(flags & os.O_NONBLOCK, 0)
                if hasattr(os, 'O_NOFOLLOW'):
                    self.assertNotEqual(flags & os.O_NOFOLLOW, 0)

    def test_actual_read_open_is_nonblocking(self):
        original_open = os.open
        observed = []
        def witness(path, flags, *a, **kw):
            observed.append(flags)
            return original_open(path, flags, *a, **kw)
        with mock.patch.object(journal_io.os, 'open', side_effect=witness):
            self.assertEqual(journal_io.read_regular_bytes(self.path, 4096, 'Review journal'), EVENT)
        self.assertEqual(len(observed), 1)
        if hasattr(os, 'O_NONBLOCK'):
            self.assertTrue(observed[0] & os.O_NONBLOCK)

    def test_actual_append_open_is_nonblocking(self):
        original_open = os.open
        observed = []
        def witness(path, flags, *a, **kw):
            observed.append(flags)
            return original_open(path, flags, *a, **kw)
        with mock.patch.object(journal_io.os, 'open', side_effect=witness):
            journal_io.append_verified_event(self.path, EVENT, 4096, lambda: None)
        self.assertEqual(len(observed), 1)
        if hasattr(os, 'O_NONBLOCK'):
            self.assertTrue(observed[0] & os.O_NONBLOCK)
        self.assertEqual(self.path.read_bytes(), EVENT * 2)

    def test_read_rejects_preexisting_fifo(self):
        if not hasattr(os, 'mkfifo'):
            self.skipTest('POSIX FIFO needed')
        self.path.unlink()
        os.mkfifo(self.path)
        with self.assertRaises(ValueError):
            journal_io.read_regular_bytes(self.path, 4096, 'Review journal')

    def test_append_rejects_preexisting_fifo(self):
        if not hasattr(os, 'mkfifo'):
            self.skipTest('POSIX FIFO needed')
        self.path.unlink()
        os.mkfifo(self.path)
        with self.assertRaises(ValueError):
            journal_io.append_verified_event(self.path, EVENT, 4096, lambda: None)

    def _raced_fifo_held(self, operation):
        if not (hasattr(os, 'mkfifo') and hasattr(os, 'O_NONBLOCK')):
            self.skipTest('POSIX O_NONBLOCK and mkfifo required')
        outcome = subprocess.run(
            [sys.executable, '-c', _CHILD, str(self.path), operation],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=4,
            env={**os.environ, 'PYTHONPATH': str(Path(__file__).resolve().parents[1])},
        )
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        self.assertEqual(outcome.stdout.strip(), 'HOLD')
        self.assertNotIn(str(self.path), outcome.stdout + outcome.stderr)

    def test_read_lstat_to_open_fifo_swap_held_without_hang(self):
        self._raced_fifo_held('read')

    def test_append_lstat_to_open_fifo_swap_held_without_hang(self):
        self._raced_fifo_held('append')


if __name__ == '__main__':
    unittest.main()
