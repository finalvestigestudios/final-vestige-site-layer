"""R423: refuse unbounded or non-native CSV snapshot byte budgets.

Actual shared CSV descriptor reader; temporary synthetic data only. The guard
runs before filesystem inspection, a prerequisite for local-first privacy.
"""
from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import tempfile
import traceback
import unittest
from unittest.mock import patch

from fvs_suite import csv_snapshot as subject


class CsvSnapshotNativeBudgetR423(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r423-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.source = self.root / "PRIVATE_ACCOUNTS.csv"
        self.bytes = b"id,amount\r\nA,1.20\r\n"
        self.source.write_bytes(self.bytes)

    def assert_rejected_before_inspection(self, maximum):
        with patch.object(Path, "lstat", side_effect=AssertionError("INSPECTED_PRIVATE_FILE")) as inspect:
            with patch.object(subject.os, "open", side_effect=AssertionError("OPENED_PRIVATE_FILE")) as open_file:
                with self.assertRaisesRegex(ValueError, "^Invalid CSV input size limit$") as error:
                    subject.read_csv_snapshot(self.source, maximum)
                self.assertIsNone(error.exception.__context__)
                self.assertIsNone(error.exception.__cause__)
                inspect.assert_not_called()
                open_file.assert_not_called()

    def test_nan_fails_closed_before_file_access(self):
        self.assert_rejected_before_inspection(float("nan"))

    def test_positive_infinity_fails_closed_before_file_access(self):
        self.assert_rejected_before_inspection(float("inf"))

    def test_negative_infinity_fails_closed_before_file_access(self):
        self.assert_rejected_before_inspection(float("-inf"))

    def test_finite_float_is_not_an_integer_budget(self):
        for value in (0.0, 1.0, 1024.0, 64.0 * 1024 * 1024):
            with self.subTest(value=value):
                self.assert_rejected_before_inspection(value)

    def test_decimal_budgets_are_not_accepted(self):
        for value in (Decimal(0), Decimal("8192"), Decimal("NaN"), Decimal("Infinity")):
            with self.subTest(value=str(value)):
                self.assert_rejected_before_inspection(value)

    def test_fraction_budgets_are_not_accepted(self):
        self.assert_rejected_before_inspection(Fraction(1024, 1))

    def test_booleans_are_not_byte_budgets(self):
        self.assert_rejected_before_inspection(False)
        self.assert_rejected_before_inspection(True)

    def test_non_numeric_shapes_are_rejected(self):
        for value in (None, "1024", b"1024", [1024], {"maximum": 1024}, 1024 + 0j):
            with self.subTest(kind=type(value).__name__):
                self.assert_rejected_before_inspection(value)

    def test_int_subclass_does_not_run_python_comparison_hooks(self):
        class Hostile(int):
            def __lt__(self, other):
                raise AssertionError("PRIVATE_LT_HOOK")
            def __le__(self, other):
                raise AssertionError("PRIVATE_LE_HOOK")
            def __gt__(self, other):
                raise AssertionError("PRIVATE_GT_HOOK")
        self.assert_rejected_before_inspection(Hostile(100))

    def test_negative_native_limit_is_rejected(self):
        self.assert_rejected_before_inspection(-1)

    def test_budget_beyond_64_mib_is_rejected_before_inspection(self):
        self.assert_rejected_before_inspection(64 * 1024 * 1024 + 1)

    def test_very_large_integer_cannot_disable_memory_limit(self):
        self.assert_rejected_before_inspection(10 ** 500)

    def test_valid_zero_budget_accepts_empty_file(self):
        self.source.write_bytes(b"")
        self.assertEqual(subject.read_csv_snapshot(self.source, 0), b"")

    def test_native_exact_length_budget_preserves_source_bytes(self):
        self.assertEqual(subject.read_csv_snapshot(self.source, len(self.bytes)), self.bytes)

    def test_native_full_64_mib_budget_preserves_small_source(self):
        self.assertEqual(subject.read_csv_snapshot(self.source, 64 * 1024 * 1024), self.bytes)

    def test_one_byte_short_budget_rejects_unchanged_source(self):
        with self.assertRaisesRegex(ValueError, "file-size limit"):
            subject.read_csv_snapshot(self.source, len(self.bytes) - 1)
        self.assertEqual(self.source.read_bytes(), self.bytes)

    def test_sparse_oversize_file_fails_before_open(self):
        with self.source.open("r+b") as handle:
            handle.truncate(64 * 1024 * 1024 + 1)
        with patch.object(subject.os, "open") as opener:
            with self.assertRaisesRegex(ValueError, "file-size limit"):
                subject.read_csv_snapshot(self.source, 64 * 1024 * 1024)
            opener.assert_not_called()

    def test_rejected_budget_error_does_not_contain_private_path(self):
        try:
            subject.read_csv_snapshot(self.source, float("nan"))
        except ValueError as error:
            detail = "".join(traceback.format_exception(error))
            self.assertNotIn(str(self.source), detail)
            self.assertNotIn("PRIVATE_ACCOUNTS", detail)
        else:
            self.fail("Nonfinite limit was accepted")


if __name__ == "__main__":
    unittest.main()
