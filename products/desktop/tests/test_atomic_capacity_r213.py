"""R213 bounded financial evidence publication; synthetic values and no network.

The shared report API must not exhaust memory on infinite header/item streams
or fill a disk with unbounded rows; a failed export must never become evidence.
"""
from __future__ import annotations

import csv
from collections import UserDict
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from fvs_suite.atomic_reports import (MAX_REPORT_COLUMNS, MAX_REPORT_ROWS,
                                      write_csv_report)


class CapacityCustodyR213(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r213-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.report = self.root / "financial-evidence.csv"

    def write(self, fields=("id", "amount"), rows=None, cell=str):
        if rows is None:
            rows = ({"id": "x", "amount": Decimal("0.10")},)
        return write_csv_report(self.report, fields, rows, cell)

    def assert_clean(self):
        self.assertFalse(self.report.exists())
        self.assertEqual(list(self.root.glob("*.partial")), [])
        self.assertEqual(list(self.root.glob(".*.partial")), [])

    def test_schema_exact_limit_is_allowed_and_values_round_trip(self):
        names = [f"col_{n}" for n in range(MAX_REPORT_COLUMNS)]
        row = {name: str(i) for i, name in enumerate(names)}
        self.write(fields=names, rows=(row,))
        with self.report.open(encoding="utf-8-sig", newline="") as f:
            read = list(csv.DictReader(f))
        self.assertEqual(len(read), 1)
        self.assertEqual(read[0], row)

    def test_schema_one_over_limit_is_rejected_before_staging(self):
        with self.assertRaisesRegex(ValueError, "CSV report column limit exceeded"):
            self.write(fields=[f"col_{n}" for n in range(MAX_REPORT_COLUMNS + 1)])
        self.assert_clean()

    def test_unbounded_header_generator_only_consumes_limit_plus_one(self):
        seen = 0
        def infinite():
            nonlocal seen
            while True:
                seen += 1
                yield f"header_{seen}"
        with self.assertRaisesRegex(ValueError, "CSV report column limit exceeded"):
            self.write(fields=infinite())
        self.assertEqual(seen, MAX_REPORT_COLUMNS + 1)
        self.assert_clean()

    def test_header_source_exception_still_redacted(self):
        secret = "SYNTHETIC_PRIVATE_FINANCIAL_TOKEN"
        def broken():
            yield "id"
            raise RuntimeError(secret)
        with self.assertRaises(ValueError) as captured:
            self.write(fields=broken())
        self.assertEqual(str(captured.exception), "CSV report columns could not be read")
        self.assertIsNone(captured.exception.__context__)
        self.assert_clean()

    def test_row_mapping_exact_limit_is_allowed_with_extras_sanitized(self):
        row = {"id": "A", "amount": Decimal("0.10")}
        row.update({f"extra_{n}": "safe" for n in range(MAX_REPORT_COLUMNS - 2)})
        seen = []
        self.write(rows=(row,), cell=lambda v: (seen.append(v), str(v))[1])
        self.assertEqual(len(seen), MAX_REPORT_COLUMNS + 2)
        with self.report.open(encoding="utf-8-sig", newline="") as f:
            self.assertEqual(list(csv.DictReader(f)), [{"id": "A", "amount": "0.10"}])

    def test_row_mapping_one_over_limit_is_rejected(self):
        row = {"id": "A", "amount": "0.10"}
        row.update({f"extra_{n}": "safe" for n in range(MAX_REPORT_COLUMNS - 1)})
        with self.assertRaisesRegex(ValueError, "CSV report row column limit exceeded"):
            self.write(rows=(row,))
        self.assert_clean()

    def test_infinite_mapping_items_is_bounded_at_limit_plus_one(self):
        class InfiniteItems(UserDict):
            def __init__(self):
                super().__init__({"id": "A", "amount": "0.10"})
                self.consumed = 0
            def items(self):
                yield "id", "A"
                yield "amount", "0.10"
                index = 0
                while True:
                    self.consumed += 1
                    yield f"extra_{index}", "safe"
                    index += 1
        record = InfiniteItems()
        with self.assertRaisesRegex(ValueError, "CSV report row column limit exceeded"):
            self.write(rows=(record,))
        self.assertEqual(record.consumed, MAX_REPORT_COLUMNS - 1)
        self.assert_clean()

    def test_rejected_late_wide_row_rolls_back_complete_report(self):
        good = {"id": "x", "amount": "1.25"}
        wide = dict(good)
        wide.update({f"extra_{n}": "safe" for n in range(MAX_REPORT_COLUMNS - 1)})
        rows = [good] * 35 + [wide]
        with self.assertRaisesRegex(ValueError, "CSV report row column limit exceeded"):
            self.write(rows=rows)
        self.assert_clean()

    def test_rejected_wide_row_preserves_existing_evidence(self):
        self.report.write_bytes(b"DO_NOT_REPLACE_OR_TRUNCATE")
        row = {"id": "x", "amount": "0.01"}
        row.update({f"extra_{n}": "safe" for n in range(MAX_REPORT_COLUMNS - 1)})
        with self.assertRaisesRegex(ValueError, "CSV report row column limit exceeded"):
            self.write(rows=(row,))
        self.assertEqual(self.report.read_bytes(), b"DO_NOT_REPLACE_OR_TRUNCATE")
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_exact_max_row_count_is_allowed(self):
        def rows():
            for i in range(MAX_REPORT_ROWS):
                yield {"id": str(i), "amount": "0.01"}
        self.write(rows=rows())
        with self.report.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(sum(1 for _ in stream), MAX_REPORT_ROWS + 1)
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_max_plus_one_rows_fail_closed_and_remove_partial(self):
        consumed = 0
        def rows():
            nonlocal consumed
            for i in range(MAX_REPORT_ROWS + 1):
                consumed += 1
                yield {"id": str(i), "amount": "0.01"}
        with self.assertRaisesRegex(ValueError, "CSV report row limit exceeded"):
            self.write(rows=rows())
        self.assertEqual(consumed, MAX_REPORT_ROWS + 1)
        self.assert_clean()

    def test_infinite_row_generator_is_bounded(self):
        consumed = 0
        def rows():
            nonlocal consumed
            while True:
                consumed += 1
                yield {"id": "same", "amount": "0.01"}
        with self.assertRaisesRegex(ValueError, "CSV report row limit exceeded"):
            self.write(rows=rows())
        self.assertEqual(consumed, MAX_REPORT_ROWS + 1)
        self.assert_clean()

    def test_over_limit_rows_never_modify_existing_report(self):
        self.report.write_bytes(b"VERIFIED_EXISTING_EVIDENCE")
        with self.assertRaisesRegex(ValueError, "CSV report row limit exceeded"):
            self.write(rows=({"id": "x", "amount": "0.01"}
                             for _ in range(MAX_REPORT_ROWS + 1)))
        self.assertEqual(self.report.read_bytes(), b"VERIFIED_EXISTING_EVIDENCE")
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_small_decimal_csv_roundtrip_and_bom_preserved(self):
        self.write()
        self.assertTrue(self.report.read_bytes().startswith(b"\xef\xbb\xbf"))
        with self.report.open(encoding="utf-8-sig", newline="") as f:
            self.assertEqual(list(csv.DictReader(f)), [{"id": "x", "amount": "0.10"}])

    def test_interrupt_from_caller_still_escapes_and_cleans(self):
        def rows():
            raise KeyboardInterrupt()
            yield {"id": "x", "amount": "0.10"}
        with self.assertRaises(KeyboardInterrupt):
            self.write(rows=rows())
        self.assert_clean()


if __name__ == "__main__":
    unittest.main()
