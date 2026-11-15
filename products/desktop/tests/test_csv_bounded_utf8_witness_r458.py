"""R458: bounded UTF-8 allocations while counting and attesting local CSVs.

Synthetic-only evidence; no network, telemetry, licenses, or production files.
The complete-source tests exercise the shared six-utility CSV publisher.
"""
from __future__ import annotations

import csv
import hashlib
import io
import os
import random
import tempfile
import tracemalloc
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from fvs_suite import atomic_reports
from fvs_suite.atomic_reports import (
    _BudgetedCSVTextSink,
    _utf8_chunks,
    write_csv_report,
)
from fvs_suite.engine import safe_cell


class BoundedUTF8WitnessR458(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r458-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.target = self.root / "local-evidence.csv"

    def assert_unpublished(self):
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.glob(".fvs-csv-*.partial")), [])

    def test_seeded_native_utf8_byte_parity(self):
        randomizer = random.Random(458)
        fragments = ("", "A", " ", "é", "€", "😀", "𐀀", "\t",
                     '"', ",", "\r", "\n", "e\u0301")
        for case in range(3000):
            value = "".join(randomizer.choice(fragments)
                            for _ in range(randomizer.randrange(0, 100)))
            with self.subTest(case=case):
                expected = value.encode("utf-8")
                self.assertEqual(sum(map(len, _utf8_chunks(value))),
                                 len(expected))
                excel = len(expected) + value.count('"')
                if any(mark in value for mark in ('"', ",", "\r", "\n")):
                    excel += 2
                self.assertEqual(_BudgetedCSVTextSink._excel_field_bytes(value),
                                 excel)

    def test_utf8_chunk_size_is_bounded_at_astral_limit(self):
        huge = "😀" * 1_048_576
        total = 0
        maximum = 0
        for chunk in _utf8_chunks(huge):
            self.assertEqual(type(chunk), bytes)
            maximum = max(maximum, len(chunk))
            total += len(chunk)
        self.assertEqual(total, 4 * len(huge))
        self.assertLessEqual(maximum, 4 * atomic_reports._UTF8_CHUNK_CHARACTERS)

    def test_multibyte_straddling_character_slice_boundary(self):
        for char in ("A", "é", "€", "😀", "e\u0301", '"'):
            for size in (16383, 16384, 16385, 40000):
                with self.subTest(char=repr(char), size=size):
                    value = char * size
                    self.assertEqual(
                        sum(len(piece) for piece in _utf8_chunks(value)),
                        len(value.encode("utf-8")))

    def test_empty_input_has_zero_cost_and_no_witness_change(self):
        sink = _BudgetedCSVTextSink(io.StringIO())
        self.assertEqual(list(_utf8_chunks("")), [])
        self.assertEqual(sink.write(""), 0)
        self.assertEqual(sink._witness._size, 3)
        self.assertEqual(sink._remaining, atomic_reports.MAX_REPORT_BYTES - 3)

    def test_witness_matches_sha256_of_full_utf8_stream(self):
        payload = "€😀,\r\n" * 50_000
        with tempfile.TemporaryFile(mode="w+", encoding="utf-8-sig",
                                    newline="") as stream:
            sink = _BudgetedCSVTextSink(stream)
            self.assertEqual(sink.write(payload), len(payload))
            sink.write(",-42.1000\r\n")
            stream.flush()
            sink.verify(stream.fileno())
            expected = b"\xef\xbb\xbf" + (payload + ",-42.1000\r\n").encode("utf-8")
            self.assertEqual(sink._witness._size, len(expected))
            self.assertEqual(sink._witness._digest.hexdigest(),
                             hashlib.sha256(expected).hexdigest())

    def test_direct_sink_budget_rejection_happens_before_writing(self):
        class CountWrites:
            def __init__(self):
                self.calls = 0

            def write(self, text):
                self.calls += 1
                return len(text)

        stream = CountWrites()
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", 103):
            sink = _BudgetedCSVTextSink(stream)
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                sink.write("😀" * 26)
            self.assertEqual(stream.calls, 0)
            self.assertEqual(sink._witness._size, 3)
            self.assertEqual(sink._remaining, 100)

    def test_short_character_write_is_never_attested(self):
        class ShortWrite:
            def write(self, text):
                return len(text) - 1

        sink = _BudgetedCSVTextSink(ShortWrite())
        with self.assertRaises(OSError):
            sink.write("SYNTHETIC FINANCIAL EVIDENCE")
        self.assertEqual(sink._witness._size, 3)
        self.assertEqual(sink._remaining, atomic_reports.MAX_REPORT_BYTES - 3)

    def test_standard_csv_writer_serialization_parity(self):
        randomizer = random.Random(45801)
        fragments = ("", "simple", "é", "😀", ",", '"', "\n", "\r", "-42.10")
        for case in range(400):
            values = tuple(
                "".join(randomizer.choice(fragments)
                        for _ in range(randomizer.randrange(0, 6)))
                for _ in range(randomizer.randrange(1, 9)))
            expected = io.StringIO(newline="")
            csv.writer(expected).writerow(values)
            observed = io.StringIO(newline="")
            sink = _BudgetedCSVTextSink(observed)
            sink.preflight(values)
            csv.writer(sink).writerow(values)
            with self.subTest(case=case):
                self.assertEqual(observed.getvalue(), expected.getvalue())
                expected_bytes = b"\xef\xbb\xbf" + expected.getvalue().encode("utf-8")
                self.assertEqual(sink._witness._size, len(expected_bytes))
                self.assertEqual(sink._witness._digest.digest(),
                                 hashlib.sha256(expected_bytes).digest())

    def test_large_field_counting_does_not_materialize_full_utf8_copy(self):
        huge = "😀" * 300_000
        tracemalloc.start()
        try:
            cost = _BudgetedCSVTextSink._excel_field_bytes(huge)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual(cost, 1_200_000)
        # The old full value.encode("utf-8") allocated 1.2 MB in this path.
        # This bound allows platform overhead but not a full encoded duplicate.
        self.assertLess(peak, 500_000)

    def test_full_publisher_preserves_utf8_bom_money_and_provenance(self):
        fields = ("row_ref", "amount")
        rows = [{"row_ref": "é😀", "amount": Decimal("-42.1000")}]
        output = write_csv_report(self.target, fields, rows, safe_cell)
        self.assertEqual(output, self.target)
        self.assertEqual(self.target.read_bytes(),
                         b"\xef\xbb\xbfrow_ref,amount\r\n"
                         + "é😀,-42.1000\r\n".encode("utf-8"))
        self.assertEqual(list(self.root.glob(".fvs-csv-*.partial")), [])

    def test_one_byte_short_rolls_back_without_partial_report(self):
        fields = ("id", "amount")
        values = ("é😀", '€,"42.10"')
        expected = io.StringIO(newline="")
        csv.writer(expected).writerow(fields)
        csv.writer(expected).writerow(values)
        expected_len = 3 + len(expected.getvalue().encode("utf-8"))
        with patch.object(atomic_reports, "MAX_REPORT_BYTES", expected_len - 1):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                write_csv_report(self.target, fields, [dict(zip(fields, values))],
                                 safe_cell)
        self.assert_unpublished()

    def test_existing_financial_report_never_replaced(self):
        self.target.write_bytes(b"PREEXISTING REVIEWED AUDIT")
        with self.assertRaises(FileExistsError):
            write_csv_report(self.target, ("id", "amount"),
                             [{"id": "A", "amount": Decimal("0.10")}], safe_cell)
        self.assertEqual(self.target.read_bytes(), b"PREEXISTING REVIEWED AUDIT")
        self.assertEqual(list(self.root.glob(".fvs-csv-*.partial")), [])

    def test_unsanitized_spreadsheet_formula_remains_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsafe or non-text"):
            write_csv_report(self.target, ("id", "amount"),
                             [{"id": "=HYPERLINK(1)", "amount": "42.10"}], str)
        self.assert_unpublished()


if __name__ == "__main__":
    unittest.main()
