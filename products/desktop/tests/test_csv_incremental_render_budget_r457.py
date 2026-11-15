"""R457: bound financial CSV row allocation during sanitization.

All values and paths in this suite are synthetic. The source test runs against
the actual atomic writer, including its no-overwrite and byte-witness gates.
"""
from __future__ import annotations

import csv
import io
import random
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from fvs_suite import atomic_reports
from fvs_suite.atomic_reports import _BudgetedCSVTextSink, write_csv_report
from fvs_suite.engine import safe_cell


def _csv_bytes(values):
    buffer = io.StringIO(newline="")
    csv.writer(buffer).writerow(values)
    return buffer.getvalue().encode("utf-8")


class IncrementalRenderBudgetR457(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.target = self.root / "synthetic-audit.csv"

    def _publish(self, rows, fields=("id", "amount"), cell=safe_cell):
        return write_csv_report(self.target, fields, rows, cell)

    def _assert_unpublished(self):
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.glob(".fvs-csv-*.partial")), [])

    def test_seeded_native_excel_parity_for_incremental_budget(self):
        rng = random.Random(457)
        fragments = ("", "a", "b", " ", "\t", "\r", "\n", ",", '"',
                     "é", "€", "😀", 'a"b', "x,y")
        samples = [("",), ("", ""), (",",), ('"',), ("é", "😀")]
        for columns in (1, 2, 3, 9, 32, 64):
            for _ in range(100):
                samples.append(tuple(
                    "".join(rng.choice(fragments) for _ in range(rng.randrange(0, 7)))
                    for _ in range(columns)
                ))
        for i, values in enumerate(samples):
            exact = len(_csv_bytes(values))
            order = list(values)
            rng.shuffle(order)  # Mapping.items() order need not match header order
            with self.subTest(case=i, columns=len(values)):
                with patch.object(atomic_reports, "MAX_REPORT_BYTES", exact + 3):
                    sink = _BudgetedCSVTextSink(io.StringIO())
                    subtotal = 0
                    for value in order:
                        subtotal = sink.preflight_add(value, subtotal, len(values))
                    sink.preflight(values)
                    self.assertEqual(sink._remaining, exact)
                with patch.object(atomic_reports, "MAX_REPORT_BYTES", exact + 2):
                    sink = _BudgetedCSVTextSink(io.StringIO())
                    subtotal = 0
                    with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                        for value in order:
                            subtotal = sink.preflight_add(value, subtotal, len(values))

    def test_preflight_append_does_not_debit_stream(self):
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 40):
            sink = _BudgetedCSVTextSink(io.StringIO())
            first = sink.preflight_add("é", 0, 2)
            sink.preflight_add('a"b', first, 2)
            self.assertEqual(sink._remaining, 37)
            sink.preflight(("é", 'a"b'))
            self.assertEqual(sink._remaining, 37)

    def test_single_empty_column_quote_edge(self):
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 7):
            sink = _BudgetedCSVTextSink(io.StringIO())
            self.assertEqual(sink.preflight_add("", 0, 1), 2)
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 6):
            sink = _BudgetedCSVTextSink(io.StringIO())
            with self.assertRaises(ValueError):
                sink.preflight_add("", 0, 1)

    def test_rejects_zero_column_incremental_gate(self):
        sink = _BudgetedCSVTextSink(io.StringIO())
        with self.assertRaisesRegex(ValueError, "Invalid CSV report column count"):
            sink.preflight_add("A", 0, 0)

    def test_first_oversized_emitted_cell_stops_later_sanitization(self):
        seen = []
        def checked(value):
            seen.append(value)
            return safe_cell(value)
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 100):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self._publish([{"id": "A" * 1000, "amount": "LATER"}], cell=checked)
        self.assertEqual(seen, ["id", "amount", "A" * 1000])
        self._assert_unpublished()

    def test_reordered_mapping_stops_before_later_schema_field(self):
        seen = []
        def checked(value):
            seen.append(value)
            return safe_cell(value)
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 100):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self._publish([{"amount": "A" * 1000, "id": "LATER"}], cell=checked)
        self.assertEqual(seen, ["id", "amount", "A" * 1000])
        self._assert_unpublished()

    def test_many_escaped_cells_abort_before_building_full_256_column_row(self):
        fields = tuple(f"column_{i:03d}" for i in range(256))
        row = {name: "=SUM(" + "9" * 8000 + ")" for name in fields}
        rendered = []
        def checked(value):
            rendered.append(value)
            return safe_cell(value)
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 33000):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self._publish([row], fields=fields, cell=checked)
        # 256 headers are expected, but fewer than six 8-KiB row values should
        # be escaped before the incremental gate refuses further allocation.
        self.assertLess(len(rendered) - len(fields), 6)
        self._assert_unpublished()

    def test_valid_ignored_extra_column_is_still_sanitized(self):
        seen = []
        def checked(value):
            seen.append(value)
            return safe_cell(value)
        self._publish([{"id": "A", "amount": "-42.10", "ignored": "=SECRET"}], cell=checked)
        self.assertIn("=SECRET", seen)
        self.assertEqual(self.target.read_bytes(), b"\xef\xbb\xbfid,amount\r\nA,-42.10\r\n")

    def test_unsafe_ignored_extra_column_still_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unsafe or non-text"):
            self._publish([{"id": "A", "amount": "-42.10", "ignored": "=A1"}], cell=str)
        self._assert_unpublished()

    def test_exact_multibyte_quote_boundary_still_publishes(self):
        fields = ("id", "amount")
        values = ("😀", '€,"42.10"')
        expected = b"\xef\xbb\xbf" + _csv_bytes(fields) + _csv_bytes(values)
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", len(expected)):
            self.assertEqual(self._publish([dict(zip(fields, values))]), self.target)
        self.assertEqual(self.target.read_bytes(), expected)
        self.assertEqual(list(self.root.glob(".fvs-csv-*.partial")), [])

    def test_one_byte_short_fails_without_partial_publication(self):
        fields = ("id", "amount")
        values = ("😀", '€,"42.10"')
        expected = b"\xef\xbb\xbf" + _csv_bytes(fields) + _csv_bytes(values)
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", len(expected) - 1):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self._publish([dict(zip(fields, values))])
        self._assert_unpublished()

    def test_decimal_money_text_and_human_review_boundary(self):
        self._publish([{"id": "REVIEW", "amount": Decimal("-42.1000")}])
        self.assertEqual(self.target.read_bytes(),
                         b"\xef\xbb\xbfid,amount\r\nREVIEW,-42.1000\r\n")

    def test_existing_financial_evidence_is_never_overwritten(self):
        self.target.write_bytes(b"EXISTING PRIVATE AUDIT")
        with self.assertRaises(FileExistsError):
            self._publish([{"id": "A", "amount": Decimal("42.10")}])
        self.assertEqual(self.target.read_bytes(), b"EXISTING PRIVATE AUDIT")
        self.assertEqual(list(self.root.glob(".fvs-csv-*.partial")), [])


if __name__ == "__main__":
    unittest.main()
