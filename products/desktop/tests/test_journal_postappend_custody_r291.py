"""R291: premium journal reports success only with an observed stable final path.

Actual private temporary files, no real customer data, network or license bypass.
The tests inject a noncooperating mutation precisely between the final fstat
and pathname lstat; this is not an adversarial-filesystem security guarantee.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite.csv_snapshot import _same_path_descriptor_signature
from fvs_suite.journal_io import append_verified_event


PRIVATE = "r291-private-account-89023"
FIRST = b'{"event":"reviewed-by-human"}\n'
SECOND = b'{"event":"pending-human-review"}\n'


class JournalPostAppendCustodyR291(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="r291-custody-")
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / (PRIVATE + ".jsonl")
        self.path.write_bytes(FIRST)

    def inject_at_final_path_check(self, mutation):
        """Patch only the *fourth* lstat (after final fsync + fstat)."""
        actual = os.lstat
        checks = [0]

        def injected(path, *args, **kwargs):
            if Path(path) == self.path:
                checks[0] += 1
                if checks[0] == 4:
                    mutation()
            return actual(path, *args, **kwargs)

        return patch("fvs_suite.journal_io.os.lstat", side_effect=injected), checks

    def test_concurrent_growth_after_last_fstat_fails_closed(self):
        def rogue_append():
            with self.path.open("ab") as stream:
                stream.write(b'rogue\n')
        instrument, calls = self.inject_at_final_path_check(rogue_append)
        with instrument, self.assertRaisesRegex(ValueError, "path changed during append"):
            append_verified_event(self.path, SECOND, 4096, lambda: None)
        self.assertEqual(calls[0], 4)
        self.assertEqual(self.path.read_bytes(), FIRST + SECOND + b'rogue\n')

    def test_same_size_corruption_after_last_fstat_fails_closed(self):
        def rogue_overwrite():
            with self.path.open("r+b") as stream:
                stream.write(b"X")
            # Force an unambiguous mtime difference on coarse timestamp FSs.
            original = os.stat(self.path)
            os.utime(self.path, ns=(original.st_atime_ns, original.st_mtime_ns - 4_000_000_000))
        instrument, calls = self.inject_at_final_path_check(rogue_overwrite)
        with instrument, self.assertRaisesRegex(ValueError, "path changed during append"):
            append_verified_event(self.path, SECOND, 4096, lambda: None)
        self.assertEqual(calls[0], 4)
        self.assertEqual(self.path.read_bytes(), b"X" + FIRST[1:] + SECOND)

    def test_postwrite_path_permission_error_sanitized_and_evidence_retained(self):
        def blocked():
            raise PermissionError(13, PRIVATE, str(self.path))
        instrument, calls = self.inject_at_final_path_check(blocked)
        with instrument, self.assertRaises(ValueError) as raised:
            append_verified_event(self.path, SECOND, 4096, lambda: None)
        error = raised.exception
        self.assertEqual(str(error), "Review journal I/O failed; inspect journal before retrying")
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertEqual(calls[0], 4)
        self.assertEqual(self.path.read_bytes(), FIRST + SECOND)

    def test_postwrite_disappearance_is_sanitized_and_existing_data_retained(self):
        def missing():
            # Raised by injected code before os.lstat, no unlink side effect.
            raise FileNotFoundError(2, PRIVATE, str(self.path))
        instrument, calls = self.inject_at_final_path_check(missing)
        with instrument, self.assertRaises(ValueError) as raised:
            append_verified_event(self.path, SECOND, 4096, lambda: None)
        error = raised.exception
        self.assertEqual(str(error), "Review journal path changed during access")
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertEqual(calls[0], 4)
        self.assertEqual(self.path.read_bytes(), FIRST + SECOND)

    def test_windows_ctime_view_disparity_does_not_fake_a_path_change(self):
        native_lstat = os.lstat
        checks = [0]
        def altered_ctime(path, *args, **kwargs):
            result = native_lstat(path, *args, **kwargs)
            if Path(path) == self.path:
                checks[0] += 1
                if checks[0] == 4:
                    class WindowsStatView:
                        def __getattr__(self, item):
                            if item == "st_ctime_ns":
                                return result.st_ctime_ns + 99
                            return getattr(result, item)
                    return WindowsStatView()
            return result
        def windows_signature(path_view, fd_view):
            return _same_path_descriptor_signature(path_view, fd_view, windows=True)
        with patch("fvs_suite.journal_io.os.lstat", side_effect=altered_ctime):
            with patch("fvs_suite.journal_io._same_path_descriptor_signature", side_effect=windows_signature):
                append_verified_event(self.path, SECOND, 4096, lambda: None)
        self.assertEqual(checks[0], 4)
        self.assertEqual(self.path.read_bytes(), FIRST + SECOND)

    def test_normal_existing_append_is_byte_exact(self):
        append_verified_event(self.path, SECOND, 4096,
                              lambda: self.assertEqual(self.path.read_bytes(), FIRST))
        self.assertEqual(self.path.read_bytes(), FIRST + SECOND)

    def test_normal_new_journal_is_byte_exact(self):
        self.path.unlink()
        append_verified_event(self.path, SECOND, 4096, lambda: None)
        self.assertEqual(self.path.read_bytes(), SECOND)

    def test_invalid_event_does_not_modify_journal(self):
        with self.assertRaisesRegex(ValueError, "One newline-terminated"):
            append_verified_event(self.path, b"bad\nline\n", 4096, lambda: None)
        self.assertEqual(self.path.read_bytes(), FIRST)


if __name__ == "__main__":
    unittest.main()
