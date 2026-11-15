"""R453: bound CSV serialization before csv.writer allocates its entire row.

All samples are synthetic. Test both exact on-disk byte limits and that the
preflight refuses an impossible row BEFORE calling the low-level writer.
"""
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import atomic_reports
from fvs_suite.atomic_reports import _BudgetedCSVTextSink, write_csv_report


class CSVSerializationPreflightR453(unittest.TestCase):
    def setUp(self):
        root = tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        self.root = Path(root.name)
        self.target = self.root / "synthetic-finance.csv"

    def publish(self, rows, fields=("id", "amount")):
        return write_csv_report(self.target, fields, rows, str)

    def assert_no_publication(self):
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.glob(".fvs-csv-*.partial")), [])

    def watch_writes(self):
        calls = []
        original = _BudgetedCSVTextSink.write

        def monitor(sink, value):
            calls.append(value)
            return original(sink, value)

        return calls, patch.object(_BudgetedCSVTextSink, "write", monitor)

    def test_preflight_is_utf8_lower_bound_and_does_not_debit_budget(self):
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 9):
            sink = _BudgetedCSVTextSink(io.StringIO())
        sink.preflight(("€", "é"))  # 3+2 encoded bytes, 6 bytes available after BOM.
        sink.preflight(("€", "é"))
        with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
            sink.preflight(("€", "é", "A€"))
        self.assertEqual(sink._remaining, 6)

    def test_oversized_header_never_reaches_serialization(self):
        calls, spy = self.watch_writes()
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 16), spy:
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.publish([], fields=("very_long_financial_header",))
        self.assertEqual(calls, [])
        self.assert_no_publication()

    def test_oversized_row_never_reaches_serialization(self):
        calls, spy = self.watch_writes()
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 24), spy:
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.publish([{"id": "A", "amount": "1" * 20}])
        self.assertEqual(calls, ["id,amount\r\n"])
        self.assert_no_publication()

    def test_second_row_uses_remaining_not_initial_budget(self):
        calls, spy = self.watch_writes()
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 27), spy:
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.publish([
                    {"id": "A", "amount": "1.00"},
                    {"id": "B", "amount": "1" * 8},
                ])
        self.assertEqual(calls, ["id,amount\r\n", "A,1.00\r\n"])
        self.assert_no_publication()

    def test_multibyte_utf8_rejected_before_writerow(self):
        calls, spy = self.watch_writes()
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 29), spy:
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.publish([{"id": "é" * 8, "amount": "1"}])
        self.assertEqual(calls, ["id,amount\r\n"])
        self.assert_no_publication()

    def test_exact_serialized_byte_boundary_preserves_output(self):
        expected = b"\xef\xbb\xbfid,amount\r\nA,42.10\r\n"
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", len(expected)):
            self.assertEqual(self.publish([{"id": "A", "amount": "42.10"}]), self.target)
        self.assertEqual(self.target.read_bytes(), expected)
        self.assertEqual(list(self.root.glob(".fvs-csv-*.partial")), [])

    def test_one_byte_below_exact_file_limit_fails_closed(self):
        expected = b"\xef\xbb\xbfid,amount\r\nA,42.10\r\n"
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", len(expected) - 1):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.publish([{"id": "A", "amount": "42.10"}])
        self.assert_no_publication()

    def test_quoted_csv_expansion_still_requires_exact_sink_check(self):
        calls, spy = self.watch_writes()
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 36), spy:
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.publish([{"id": "A", "amount": '"' * 20}])
        # Raw value fits; the exact writer expands escaping and the sink rejects.
        self.assertEqual(len(calls), 2)
        self.assert_no_publication()

    def test_ignored_extra_column_still_needs_formula_sanitization(self):
        with self.assertRaisesRegex(ValueError, "Unsafe or non-text"):
            self.publish([{"id": "A", "amount": "5.00", "extra": "=1+1"}])
        self.assert_no_publication()

    def test_negative_decimal_amount_is_unmodified(self):
        expected = b"\xef\xbb\xbfid,amount\r\nA,-42.10\r\n"
        self.publish([{"id": "A", "amount": "-42.10"}])
        self.assertEqual(self.target.read_bytes(), expected)

    def test_existing_report_remains_untouched(self):
        self.target.write_bytes(b"ORIGINAL EVIDENCE")
        with self.assertRaises(FileExistsError):
            self.publish([{"id": "A", "amount": "10.00"}])
        self.assertEqual(self.target.read_bytes(), b"ORIGINAL EVIDENCE")
        self.assertEqual(list(self.root.glob(".fvs-csv-*.partial")), [])


if __name__ == "__main__":
    unittest.main()
