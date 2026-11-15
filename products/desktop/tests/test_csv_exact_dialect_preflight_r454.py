"""R454: exact csv.excel byte-cost preflight before CPython row allocation.

Only synthetic data are used. Compare the predictive budget against the real
csv.writer dialect on a reproducible corpus, then prove allocation order and
no partial final publication through the production report API.
"""
from __future__ import annotations

import csv
import io
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import atomic_reports
from fvs_suite.atomic_reports import _BudgetedCSVTextSink, write_csv_report


def _serialized(values: tuple[str, ...]) -> bytes:
    stream = io.StringIO(newline="")
    csv.writer(stream).writerow(values)
    return stream.getvalue().encode("utf-8")


class CSVExactDialectPreflightR454(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.target = self.root / "private-test.csv"

    def publish(self, rows, fields=("id", "amount")):
        return write_csv_report(self.target, fields, rows, str)

    def assert_unpublished(self):
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.glob(".fvs-csv-*.partial")), [])

    def tracked_writes(self):
        writes = []
        original = _BudgetedCSVTextSink.write

        def tracked(sink, text):
            writes.append(text)
            return original(sink, text)

        return writes, patch.object(_BudgetedCSVTextSink, "write", tracked)

    def test_cpython_excel_dialect_cost_parity_on_deterministic_corpus(self):
        rng = random.Random(454)
        fragments = ("", " ", "\t", "\v", "simple", "é", "😀", ",",
                     "a,b", 'a"b', "a\nb", "a\rb", '"', '"""', "a\r\nb")
        rows = [("",), ("", ""), ("é", "😀", '"a,b"\r\n'),
                ('"\""',), ("abc",), ("a,b",), ("\n",)]
        for size in (1, 2, 3, 7, 20, 64):
            for _ in range(75):
                rows.append(tuple(
                    "".join(rng.choice(fragments) for _ in range(rng.randrange(1, 5)))
                    for _ in range(size)
                ))
        for index, values in enumerate(rows):
            encoded_bytes = len(_serialized(values))
            with self.subTest(index=index, values=len(values)):
                with patch.object(atomic_reports, "MAX_REPORT_BYTES", encoded_bytes + 3):
                    sink = _BudgetedCSVTextSink(io.StringIO())
                    sink.preflight(iter(values))
                    self.assertEqual(sink._remaining, encoded_bytes)
                with patch.object(atomic_reports, "MAX_REPORT_BYTES", encoded_bytes + 2):
                    sink = _BudgetedCSVTextSink(io.StringIO())
                    with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                        sink.preflight(iter(values))

    def test_only_empty_field_requires_extra_quotes(self):
        self.assertEqual(_serialized(("",)), b'""\r\n')
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 7):
            _BudgetedCSVTextSink(io.StringIO()).preflight(("",))
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 6):
            with self.assertRaises(ValueError):
                _BudgetedCSVTextSink(io.StringIO()).preflight(("",))

    def test_two_empty_fields_do_not_trigger_singleton_special_case(self):
        self.assertEqual(_serialized(("", "")), b",\r\n")
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 6):
            _BudgetedCSVTextSink(io.StringIO()).preflight(("", ""))

    def test_preflight_never_debits_accepted_budget(self):
        row = ('é"', "item,1", "one\nline")
        exact = len(_serialized(row))
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", exact + 3):
            sink = _BudgetedCSVTextSink(io.StringIO())
            sink.preflight(row)
            sink.preflight(row)
            self.assertEqual(sink._remaining, exact)

    def test_quote_doubling_rejects_before_native_writer_allocates(self):
        writes, spy = self.tracked_writes()
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 100), spy:
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.publish([{"id": "A", "amount": '"' * 4000}])
        self.assertEqual(writes, ["id,amount\r\n"])
        self.assert_unpublished()

    def test_quoted_header_rejects_before_serialization(self):
        writes, spy = self.tracked_writes()
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 9), spy:
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.publish([], fields=("a,b",))
        self.assertEqual(writes, [])
        self.assert_unpublished()

    def test_comma_and_newline_enclosures_reject_before_serialization(self):
        for amount in ("a,b", "a\nb", "a\rb", "a\r\nb"):
            with self.subTest(amount=repr(amount)):
                writes, spy = self.tracked_writes()
                with patch.object(atomic_reports, "MAX_REPORT_BYTES", 21), spy:
                    with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                        self.publish([{"id": "A", "amount": amount}])
                self.assertEqual(writes, ["id,amount\r\n"])
                self.assert_unpublished()

    def test_exact_multibyte_quoted_invoice_csv_still_succeeds(self):
        fields = ("id", "amount")
        values = ("😀", '€,"42.10"')
        expected = b"\xef\xbb\xbf" + _serialized(fields) + _serialized(values)
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", len(expected)):
            self.assertEqual(self.publish([dict(zip(fields, values))]), self.target)
        self.assertEqual(self.target.read_bytes(), expected)

    def test_one_byte_below_quote_expanded_boundary_fails_closed(self):
        fields = ("id", "amount")
        values = ("A", '€,"42.10"')
        expected = b"\xef\xbb\xbf" + _serialized(fields) + _serialized(values)
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", len(expected) - 1):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.publish([dict(zip(fields, values))])
        self.assert_unpublished()

    def test_remaining_budget_accounts_for_quotes_on_second_row(self):
        writes, spy = self.tracked_writes()
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 28), spy:
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.publish([{"id": "A", "amount": "1.00"},
                              {"id": "B", "amount": '""""'}])
        self.assertEqual(writes, ["id,amount\r\n", "A,1.00\r\n"])
        self.assert_unpublished()

    def test_unselected_extra_still_rejects_unsafe_formula(self):
        with self.assertRaisesRegex(ValueError, "Unsafe or non-text"):
            self.publish([{"id": "A", "amount": "1.00", "ignored": "=HYPERLINK(1)"}])
        self.assert_unpublished()

    def test_existing_destination_never_overwritten(self):
        self.target.write_bytes(b"EXISTING AUDIT EVIDENCE")
        with self.assertRaises(FileExistsError):
            self.publish([{"id": "A", "amount": "42.10"}])
        self.assertEqual(self.target.read_bytes(), b"EXISTING AUDIT EVIDENCE")


if __name__ == "__main__":
    unittest.main()
