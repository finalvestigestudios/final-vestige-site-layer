"""R214 bounded final CSV bytes and cells; synthetic, offline audit evidence."""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite import atomic_reports as reports


class ByteBudgetCustodyR214(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r214-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.target = self.root / "evidence.csv"

    def write(self, rows=None, fields=("id", "amount"), cell=str):
        if rows is None:
            rows = [{"id": "A", "amount": Decimal("0.10")}]
        return reports.write_csv_report(self.target, fields, rows, cell)

    def budget(self, byte_count):
        return patch.object(reports, "MAX_REPORT_BYTES", byte_count, create=True)

    def cell_limit(self, char_count):
        return patch.object(reports, "MAX_REPORT_CELL_CHARS", char_count, create=True)

    def assert_clean(self):
        self.assertFalse(self.target.exists())
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_exact_ascii_budget_accepts_report_including_bom(self):
        expected = b"\xef\xbb\xbfid,amount\r\nA,0.10\r\n"
        with self.budget(len(expected)):
            self.write()
        self.assertEqual(self.target.read_bytes(), expected)

    def test_one_byte_below_full_encoded_budget_rolls_back(self):
        expected = b"\xef\xbb\xbfid,amount\r\nA,0.10\r\n"
        with self.budget(len(expected) - 1):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.write()
        self.assert_clean()

    def test_budget_failure_does_not_replace_existing_evidence(self):
        self.target.write_bytes(b"PREVIOUS_SIGNED_AUDIT_EVIDENCE")
        with self.budget(12):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.write()
        self.assertEqual(self.target.read_bytes(), b"PREVIOUS_SIGNED_AUDIT_EVIDENCE")
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_budget_accounts_for_quoted_comma_and_embedded_newline(self):
        rows = [{"id": 'alpha,"quoted"\nbeta', "amount": "0.10"}]
        self.write(rows=rows)
        output = self.target.read_bytes()
        self.target.unlink()
        raw_without_quoting = '\ufeffid,amount\r\nalpha,"quoted"\nbeta,0.10\r\n'.encode("utf-8")
        self.assertGreater(len(output), len(raw_without_quoting))
        with self.budget(len(raw_without_quoting)):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.write(rows=rows)
        self.assert_clean()

    def test_multibyte_utf8_bytes_not_python_character_count(self):
        rows = [{"id": "📚" * 7, "amount": "0.10"}]
        self.write(rows=rows)
        actual = self.target.read_bytes()
        self.target.unlink()
        self.assertGreater(len(actual), len(actual.decode("utf-8-sig")) + 3)
        with self.budget(len(actual) - 1):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.write(rows=rows)
        self.assert_clean()

    def test_zero_row_header_still_counts_bom_and_crlf(self):
        expected = b"\xef\xbb\xbfid,amount\r\n"
        with self.budget(len(expected)):
            self.write(rows=[])
        self.assertEqual(self.target.read_bytes(), expected)
        self.target.unlink()
        with self.budget(len(expected) - 1):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.write(rows=[])
        self.assert_clean()

    def test_late_budget_failure_does_not_publish_partial(self):
        rows = ({"id": str(i), "amount": "1.00"} for i in range(60))
        with self.budget(128):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.write(rows=rows)
        self.assert_clean()

    def test_oversized_first_record_does_not_consume_remaining_rows(self):
        visited = []
        def rows():
            for i in range(100):
                visited.append(i)
                yield {"id": "x" * 30, "amount": "0.01"}
        with self.budget(35):
            with self.assertRaisesRegex(ValueError, "CSV report byte limit exceeded"):
                self.write(rows=rows())
        self.assertEqual(visited, [0])
        self.assert_clean()

    def test_cell_at_exact_character_limit_allowed(self):
        with self.cell_limit(12):
            self.write(rows=[{"id": "x" * 12, "amount": "0.10"}])
        with self.target.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream))[0]["id"], "x" * 12)

    def test_cell_over_character_limit_rejected_with_no_staging_left(self):
        with self.cell_limit(12):
            with self.assertRaisesRegex(ValueError, "CSV report cell size limit exceeded"):
                self.write(rows=[{"id": "x" * 13, "amount": "0.10"}])
        self.assert_clean()

    def test_overlong_header_rejected_before_creating_staging_file(self):
        with self.cell_limit(12):
            with self.assertRaisesRegex(ValueError, "CSV report cell size limit exceeded"):
                self.write(fields=("id", "long_header_label"))
        self.assert_clean()

    def test_ignored_extra_field_cannot_bypass_cell_limit(self):
        with self.cell_limit(12):
            with self.assertRaisesRegex(ValueError, "CSV report cell size limit exceeded"):
                self.write(rows=[{"id": "A", "amount": "0.10", "extra": "S" * 13}])
        self.assert_clean()

    def test_late_overlong_cell_preserves_prior_evidence(self):
        self.target.write_bytes(b"VERIFIED_EVIDENCE")
        rows = [{"id": "x", "amount": "0.10"}] * 8 + [{"id": "S" * 13, "amount": "0.10"}]
        with self.cell_limit(12):
            with self.assertRaisesRegex(ValueError, "CSV report cell size limit exceeded"):
                self.write(rows=rows)
        self.assertEqual(self.target.read_bytes(), b"VERIFIED_EVIDENCE")
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_discarded_extra_cells_do_not_consume_output_budget(self):
        seen = []
        row = {"id": "A", "amount": "0.10", "unused": "ignored"}
        expected = b"\xef\xbb\xbfid,amount\r\nA,0.10\r\n"
        def sanitizer(value):
            seen.append(value)
            return str(value)
        with self.budget(len(expected)):
            self.write(rows=[row], cell=sanitizer)
        self.assertEqual(self.target.read_bytes(), expected)
        self.assertEqual(seen.count("ignored"), 1)

    def test_size_rejections_never_include_private_source_content(self):
        private = "SYNTHETIC_ACCOUNT_NUMBER_123"
        with self.cell_limit(8):
            try:
                self.write(rows=[{"id": private, "amount": "0.10"}])
            except ValueError as error:
                self.assertEqual(str(error), "CSV report cell size limit exceeded")
                self.assertIsNone(error.__context__)
                self.assertIsNone(error.__cause__)
                self.assertNotIn(private, repr(error))
            else:
                self.fail("oversized field did not fail closed")
        self.assert_clean()

    def test_default_decimal_and_local_utf8_bom_round_trip(self):
        self.write()
        self.assertTrue(self.target.read_bytes().startswith(b"\xef\xbb\xbf"))
        with self.target.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream)), [{"id": "A", "amount": "0.10"}])

    def test_default_budgets_remain_positive_and_reasonably_bounded(self):
        self.assertGreater(reports.MAX_REPORT_BYTES, 1024 * 1024)
        self.assertLessEqual(reports.MAX_REPORT_BYTES, 256 * 1024 * 1024)
        self.assertGreater(reports.MAX_REPORT_CELL_CHARS, 4096)
        self.assertLessEqual(reports.MAX_REPORT_CELL_CHARS, 1_048_576)


if __name__ == "__main__":
    unittest.main()
