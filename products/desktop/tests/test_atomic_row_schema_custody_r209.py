"""R209: financial CSV exports cannot silently omit evidence columns.

Synthetic offline fixtures only; no customer data, accounts, or network.
"""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from fvs_suite.atomic_reports import write_csv_report


class CompleteRowCustodyR209(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fv-r209-")
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        self.target = self.folder / "audit.csv"

    def publish(self, rows, fields=("id", "amount", "source_row"), cell=str):
        return write_csv_report(self.target, fields, rows, cell)

    def assert_no_partial(self):
        self.assertEqual(list(self.folder.iterdir()), [])

    def read_rows(self):
        with self.target.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_missing_last_source_reference_refuses_report(self):
        with self.assertRaisesRegex(ValueError, "Incomplete CSV report row schema"):
            self.publish([{"id": "a", "amount": "3.00"}])
        self.assert_no_partial()

    def test_missing_first_identity_refuses_report(self):
        with self.assertRaisesRegex(ValueError, "Incomplete CSV report row schema"):
            self.publish([{"amount": "3.00", "source_row": "5"}])
        self.assert_no_partial()

    def test_missing_middle_amount_refuses_report(self):
        with self.assertRaisesRegex(ValueError, "Incomplete CSV report row schema"):
            self.publish([{"id": "a", "source_row": "5"}])
        self.assert_no_partial()

    def test_empty_row_refuses_report(self):
        with self.assertRaisesRegex(ValueError, "Incomplete CSV report row schema"):
            self.publish([{}])
        self.assert_no_partial()

    def test_late_missing_provenance_rolls_back_all_rows(self):
        def rows():
            for n in range(64):
                yield {"id": str(n), "amount": "1.20", "source_row": str(n + 2)}
            yield {"id": "late", "amount": "0.01"}
        with self.assertRaisesRegex(ValueError, "Incomplete CSV report row schema"):
            self.publish(rows())
        self.assert_no_partial()

    def test_prior_evidence_survives_missing_column(self):
        self.target.write_bytes(b"original signed evidence")
        with self.assertRaisesRegex(ValueError, "Incomplete CSV report row schema"):
            self.publish([{"id": "a", "amount": "1"}])
        self.assertEqual(self.target.read_bytes(), b"original signed evidence")
        self.assertEqual(list(self.folder.iterdir()), [self.target])

    def test_explicit_blank_value_is_allowed_and_distinct_from_absence(self):
        self.publish([{"id": "a", "amount": "", "source_row": ""}])
        self.assertEqual(self.read_rows(), [{"id": "a", "amount": "", "source_row": ""}])

    def test_explicit_zero_and_decimal_are_preserved(self):
        self.publish([{"id": "z", "amount": Decimal("0.00"), "source_row": "9"}])
        self.assertEqual(self.read_rows(), [{"id": "z", "amount": "0.00", "source_row": "9"}])

    def test_unknown_extra_columns_still_sanitized_once_then_ignored(self):
        called = []
        def convert(value):
            called.append(value)
            return str(value)
        self.publish([{"id": "a", "amount": "1", "source_row": "5", "unused": "private"}], cell=convert)
        self.assertEqual(called, ["id", "amount", "source_row", "a", "1", "5", "private"])
        self.assertEqual(self.read_rows(), [{"id": "a", "amount": "1", "source_row": "5"}])

    def test_similar_but_not_identical_header_does_not_fill_missing_key(self):
        with self.assertRaisesRegex(ValueError, "Incomplete CSV report row schema"):
            self.publish([{"id": "a", "amount": "1", "Source_Row": "5"}])
        self.assert_no_partial()

    def test_missing_error_does_not_echo_private_value_or_column_name(self):
        secret = "PRIVATE_SYNTHETIC_CLAIM_4319"
        try:
            self.publish([{"id": secret, "amount": "2.00"}])
        except ValueError as exc:
            self.assertNotIn(secret, str(exc))
            self.assertNotIn("source_row", str(exc))
        else:
            self.fail("missing provenance was silently published")
        self.assert_no_partial()

    def test_complete_generator_writes_all_rows_with_bom(self):
        self.publish(({"id": str(n), "amount": "2", "source_row": str(n + 1)} for n in range(12)))
        self.assertTrue(self.target.read_bytes().startswith(b"\xef\xbb\xbf"))
        self.assertEqual(len(self.read_rows()), 12)

    def test_single_field_report_also_refuses_missing_value(self):
        with self.assertRaisesRegex(ValueError, "Incomplete CSV report row schema"):
            self.publish([{}], fields=("source_row",))
        self.assert_no_partial()


if __name__ == "__main__":
    unittest.main()
