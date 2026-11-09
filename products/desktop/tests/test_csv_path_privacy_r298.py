"""R298 isolated CSV pathname privacy controls; synthetic paths and files only."""
from __future__ import annotations

import os
import tempfile
import traceback
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.csv_path_privacy import checked_csv_path

SECRET = "FINANCIAL_CLIENT_DO_NOT_EXPOSE_842397"
MESSAGE = "Select an existing CSV input"


class CsvPathPrivacyR298(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r298-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / (SECRET + ".csv")
        self.source.write_bytes(b"id,amount\nA,1.20\n")

    def assert_private_rejection(self, callback):
        try:
            callback()
        except ValueError as error:
            self.assertEqual(str(error), MESSAGE)
            self.assertIsNone(error.__cause__)
            self.assertIsNone(error.__context__)
            self.assertNotIn(SECRET, "".join(traceback.format_exception(error)))
            self.assertNotIn(str(self.root), "".join(traceback.format_exception(error)))
        else:
            self.fail("Expected a fail-closed ValueError")

    def test_existing_regular_csv_retains_exact_path(self):
        self.assertEqual(checked_csv_path(self.source), self.source)

    def test_regular_csv_keeps_original_content_unchanged(self):
        before = self.source.read_bytes()
        checked_csv_path(self.source)
        self.assertEqual(self.source.read_bytes(), before)

    def test_uppercase_csv_suffix_remains_accepted(self):
        upper = self.root / "EXPORT.CSV"
        upper.write_bytes(b"id,amount\nA,1.00\n")
        self.assertEqual(checked_csv_path(upper), upper)

    def test_str_path_remains_accepted(self):
        self.assertEqual(checked_csv_path(str(self.source)), self.source)

    def test_valid_pathlike_remains_accepted(self):
        class Valid:
            def __fspath__(self):
                return os.fspath(self.source)
        v = Valid()
        v.source = self.source
        self.assertEqual(checked_csv_path(v), self.source)

    def test_missing_csv_rejected_privately(self):
        self.assert_private_rejection(lambda: checked_csv_path(self.root / (SECRET + "-missing.csv")))

    def test_non_csv_extension_rejected_privately(self):
        other = self.root / (SECRET + ".txt")
        other.write_bytes(b"x")
        self.assert_private_rejection(lambda: checked_csv_path(other))

    def test_directory_ending_csv_rejected_privately(self):
        folder = self.root / (SECRET + "_dir.csv")
        folder.mkdir()
        self.assert_private_rejection(lambda: checked_csv_path(folder))

    def test_invalid_extension_never_inspects_file(self):
        with patch.object(Path, "is_file", side_effect=AssertionError("unexpected filesystem check")) as inspect:
            self.assert_private_rejection(lambda: checked_csv_path(self.root / (SECRET + ".txt")))
        inspect.assert_not_called()

    def test_is_file_called_once_on_valid_csv(self):
        with patch.object(Path, "is_file", wraps=None, return_value=True) as inspect:
            self.assertEqual(checked_csv_path(self.source), self.source)
        inspect.assert_called_once()

    def test_permission_error_with_private_filename_never_chained(self):
        with patch.object(Path, "is_file", side_effect=PermissionError(13, SECRET, str(self.source))):
            self.assert_private_rejection(lambda: checked_csv_path(self.source))

    def test_missing_file_error_with_private_filename_never_chained(self):
        with patch.object(Path, "is_file", side_effect=FileNotFoundError(2, SECRET, str(self.source))):
            self.assert_private_rejection(lambda: checked_csv_path(self.source))

    def test_generic_oserror_with_private_filename_never_chained(self):
        with patch.object(Path, "is_file", side_effect=OSError(5, SECRET, str(self.source))):
            self.assert_private_rejection(lambda: checked_csv_path(self.source))

    def test_value_error_from_preflight_never_chained(self):
        with patch.object(Path, "is_file", side_effect=ValueError(SECRET)):
            self.assert_private_rejection(lambda: checked_csv_path(self.source))

    def test_unicode_error_from_preflight_never_chained(self):
        with patch.object(Path, "is_file", side_effect=UnicodeError(SECRET)):
            self.assert_private_rejection(lambda: checked_csv_path(self.source))

    def test_type_error_from_preflight_never_chained(self):
        with patch.object(Path, "is_file", side_effect=TypeError(SECRET)):
            self.assert_private_rejection(lambda: checked_csv_path(self.source))

    def test_pathlike_oserror_never_chained(self):
        class BadPath:
            def __fspath__(self):
                raise OSError(5, SECRET, "/private/" + SECRET + ".csv")
        self.assert_private_rejection(lambda: checked_csv_path(BadPath()))

    def test_pathlike_value_error_never_chained(self):
        class BadPath:
            def __fspath__(self):
                raise ValueError(SECRET)
        self.assert_private_rejection(lambda: checked_csv_path(BadPath()))

    def test_pathlike_type_error_never_chained(self):
        class BadPath:
            def __fspath__(self):
                raise TypeError(SECRET)
        self.assert_private_rejection(lambda: checked_csv_path(BadPath()))

    def test_invalid_input_type_is_private(self):
        self.assert_private_rejection(lambda: checked_csv_path(123))

    def test_malformed_nul_path_is_private(self):
        self.assert_private_rejection(lambda: checked_csv_path(str(self.root) + "/" + SECRET + "\x00.csv"))

    def test_keyboard_interrupt_not_swallowed(self):
        with patch.object(Path, "is_file", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                checked_csv_path(self.source)

    def test_system_exit_not_swallowed(self):
        with patch.object(Path, "is_file", side_effect=SystemExit(9)):
            with self.assertRaises(SystemExit) as raised:
                checked_csv_path(self.source)
            self.assertEqual(raised.exception.code, 9)

    def test_memory_error_not_swallowed(self):
        with patch.object(Path, "is_file", side_effect=MemoryError):
            with self.assertRaises(MemoryError):
                checked_csv_path(self.source)


if __name__ == "__main__":
    unittest.main()
