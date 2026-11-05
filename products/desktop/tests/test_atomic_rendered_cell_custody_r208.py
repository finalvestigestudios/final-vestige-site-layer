"""R208: fail-closed six-app CSV output for malformed sanitizer results.

All inputs are synthetic. Nothing reads or writes customer information.
"""
from __future__ import annotations

import csv
from decimal import Decimal
import tempfile
import unittest
from pathlib import Path

from fvs_suite.atomic_reports import write_csv_report


def safe(value):
    text = str(value)
    return "'" + text if text.startswith(("=", "+", "@")) else text


class RenderedCellCustodyR208(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fv-r208-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.report = self.root / "audit.csv"

    def write(self, rows, headers=("id", "amount"), sanitizer=safe):
        return write_csv_report(self.report, headers, rows, sanitizer)

    def assert_no_artifacts(self):
        self.assertEqual(list(self.root.iterdir()), [])

    def test_plain_sanitized_headers_and_values_round_trip(self):
        self.write([{"id": "=HYPERLINK(1)", "amount": Decimal("-1.20")}], headers=("id", "amount"))
        with self.report.open(encoding="utf-8-sig", newline="") as f:
            self.assertEqual(list(csv.reader(f)), [["id", "amount"], ["'=HYPERLINK(1)", "-1.20"]])

    def test_every_nontext_value_result_rejected(self):
        for invalid in (None, b"x", 7, 7.0, Decimal("1.00"), False):
            with self.subTest(type=type(invalid).__name__):
                with self.assertRaisesRegex(ValueError, "CSV report cell"):
                    self.write([{"id": "one"}], sanitizer=lambda x: str(x) if x in ("id", "amount") else invalid)
                self.assert_no_artifacts()

    def test_string_subclass_result_rejected(self):
        class UntrustedText(str):
            def __str__(self):
                raise AssertionError("must not invoke suspicious __str__")
        with self.assertRaisesRegex(ValueError, "CSV report cell"):
            self.write([{"id": "one"}], sanitizer=lambda x: str(x) if x in ("id", "amount") else UntrustedText("one"))
        self.assert_no_artifacts()

    def test_nul_in_rendered_row_rejected(self):
        with self.assertRaisesRegex(ValueError, "CSV report cell"):
            self.write([{"id": "one", "amount": "3\x00hidden"}])
        self.assert_no_artifacts()

    def test_nul_in_ignored_extra_column_rejected(self):
        with self.assertRaisesRegex(ValueError, "CSV report cell"):
            self.write([{"id": "one", "unused": "3\x00hidden"}])
        self.assert_no_artifacts()

    def test_nontext_ignored_column_rejected_too(self):
        with self.assertRaisesRegex(ValueError, "CSV report cell"):
            self.write([{"id": "one", "unused": object()}], sanitizer=lambda x: str(x) if x in ("id", "amount", "one") else None)
        self.assert_no_artifacts()

    def test_bare_formula_in_value_rejected_if_callback_fails_to_escape(self):
        with self.assertRaisesRegex(ValueError, "CSV report cell"):
            self.write([{"id": "=1+1"}], sanitizer=str)
        self.assert_no_artifacts()

    def test_bare_plus_formula_in_value_rejected(self):
        with self.assertRaisesRegex(ValueError, "CSV report cell"):
            self.write([{"id": "+1+1"}], sanitizer=str)
        self.assert_no_artifacts()

    def test_bare_at_formula_in_value_rejected(self):
        with self.assertRaisesRegex(ValueError, "CSV report cell"):
            self.write([{"id": "@SUM(1)"}], sanitizer=str)
        self.assert_no_artifacts()

    def test_bare_formula_in_header_rejected_before_staging(self):
        with self.assertRaisesRegex(ValueError, "CSV report cell"):
            self.write([], headers=("=1+1",), sanitizer=str)
        self.assert_no_artifacts()

    def test_bare_plus_header_rejected_before_staging(self):
        with self.assertRaises(ValueError):
            self.write([], headers=("+1+1",), sanitizer=str)
        self.assert_no_artifacts()

    def test_bare_at_header_rejected_before_staging(self):
        with self.assertRaises(ValueError):
            self.write([], headers=("@SUM(1)",), sanitizer=str)
        self.assert_no_artifacts()

    def test_header_nonstring_rejected_before_staging(self):
        with self.assertRaises(ValueError):
            self.write([], sanitizer=lambda x: None)
        self.assert_no_artifacts()

    def test_header_nul_rejected_before_staging(self):
        with self.assertRaises(ValueError):
            self.write([], headers=("bad\x00label",), sanitizer=str)
        self.assert_no_artifacts()

    def test_multiline_value_remains_legal(self):
        self.write([{"id": "line 1\nline 2", "amount": "2.00"}])
        with self.report.open(encoding="utf-8-sig", newline="") as f:
            self.assertEqual(list(csv.DictReader(f)), [{"id": "line 1\nline 2", "amount": "2.00"}])

    def test_original_report_preserved_on_bad_rendered_cell(self):
        self.report.write_bytes(b"previous signed evidence")
        with self.assertRaises(ValueError):
            self.write([{"id": "x\x00y"}])
        self.assertEqual(self.report.read_bytes(), b"previous signed evidence")
        self.assertEqual(list(self.root.iterdir()), [self.report])

    def test_partial_rows_rollback_after_late_bad_render(self):
        def rows():
            yield {"id": "first", "amount": "1"}
            yield {"id": "second", "amount": None}
        def convert(value):
            return None if value is None else safe(value)
        with self.assertRaises(ValueError):
            self.write(rows(), sanitizer=convert)
        self.assert_no_artifacts()

    def test_extra_column_still_sanitized_once_and_ignored(self):
        calls = []
        def convert(value):
            calls.append(value)
            return safe(value)
        self.write([{"id": "ok", "amount": "0", "extra": "=UNUSED"}], sanitizer=convert)
        self.assertEqual(calls, ["id", "amount", "ok", "0", "=UNUSED"])
        with self.report.open(encoding="utf-8-sig", newline="") as f:
            self.assertEqual(list(csv.reader(f)), [["id", "amount"], ["ok", "0"]])


if __name__ == "__main__":
    unittest.main()
