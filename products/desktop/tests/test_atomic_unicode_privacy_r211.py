"""R211: report publication rejects non-UTF-8 Unicode and redacts sanitizer failures.

All fixtures are synthetic. Tests run without network access or customer data.
"""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from fvs_suite.atomic_reports import write_csv_report


class UnicodeCustodyR211(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="fvs-r211-")
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.path = self.folder / "audit.csv"

    def publish(self, rows=None, fields=("id", "amount"), cell=str):
        return write_csv_report(
            self.path, fields, [{"id": "A", "amount": "0.10"}] if rows is None else rows, cell
        )

    def assert_no_output(self):
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_high_surrogate_in_header_fails_with_static_error(self):
        with self.assertRaisesRegex(ValueError, "Unsafe or non-text CSV report cell"):
            self.publish(fields=("id", "amount\ud800"))
        self.assert_no_output()

    def test_low_surrogate_in_header_fails_before_temp_created(self):
        with self.assertRaisesRegex(ValueError, "Unsafe or non-text CSV report cell"):
            self.publish(fields=("id", "amount\udfff"))
        self.assert_no_output()

    def test_high_surrogate_in_row_cell_fails_without_unicode_trace(self):
        with self.assertRaisesRegex(ValueError, "Unsafe or non-text CSV report cell") as e:
            self.publish([{"id": "SENSITIVE\ud800VALUE", "amount": "1"}])
        self.assertNotIn("SENSITIVE", str(e.exception))
        self.assert_no_output()

    def test_low_surrogate_in_row_cell_fails(self):
        with self.assertRaises(ValueError):
            self.publish([{"id": "A", "amount": "\udc00"}])
        self.assert_no_output()

    def test_even_ignored_extra_column_must_be_encodable(self):
        with self.assertRaises(ValueError):
            self.publish([{"id": "A", "amount": "2", "private_extra": "\udb00"}])
        self.assert_no_output()

    def test_late_surrogate_rejects_every_staged_row(self):
        def rows():
            for i in range(256):
                yield {"id": str(i), "amount": "0.01"}
            yield {"id": "TAIL\ud800", "amount": "99"}
        with self.assertRaises(ValueError):
            self.publish(rows())
        self.assert_no_output()

    def test_existing_evidence_preserved_when_invalid_utf8(self):
        original = b"previously signed, immutable evidence"
        self.path.write_bytes(original)
        with self.assertRaises(ValueError):
            self.publish([{"id": "\udfff", "amount": "1"}])
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.folder.iterdir()), [self.path])

    def test_financial_sanitizer_exception_is_static_redacted(self):
        marker = "PRIVATE_FINANCIAL_FIXTURE_49833"
        def sanitizer(value):
            if value == marker:
                raise RuntimeError("private account " + marker)
            return str(value)
        try:
            self.publish([{"id": "A", "amount": marker}], cell=sanitizer)
        except ValueError as exc:
            self.assertEqual(str(exc), "CSV report cell sanitizer failed")
            self.assertTrue(exc.__suppress_context__)
            self.assertNotIn(marker, str(exc))
        else:
            self.fail("Sanitizer exception was not redacted")
        self.assert_no_output()

    def test_header_sanitizer_exception_has_no_temp_side_effect(self):
        def sanitizer(value):
            if value == "amount":
                raise LookupError("secret metadata")
            return str(value)
        with self.assertRaisesRegex(ValueError, "CSV report cell sanitizer failed"):
            self.publish(cell=sanitizer)
        self.assert_no_output()

    def test_unicode_sanitizer_exception_redacted(self):
        def sanitizer(value):
            if value == "BAD":
                raise UnicodeEncodeError("utf-8", "BAD SECRET \ud800", 11, 12, "bad input")
            return str(value)
        with self.assertRaisesRegex(ValueError, "CSV report cell sanitizer failed"):
            self.publish([{"id": "BAD", "amount": "1"}], cell=sanitizer)
        self.assert_no_output()

    def test_success_valid_supplementary_unicode_round_trips(self):
        self.publish([{"id": "Invoice 📋🧾", "amount": "42.00"}])
        with self.path.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream)), [{"id": "Invoice 📋🧾", "amount": "42.00"}])
        self.assertEqual(self.path.read_bytes()[:3], b"\xef\xbb\xbf")

    def test_existing_multiline_csv_round_trip_unchanged(self):
        self.publish([{"id": "Row one\nRow two", "amount": Decimal("0.10")}])
        with self.path.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream)), [{"id": "Row one\nRow two", "amount": "0.10"}])

    def test_callback_called_exactly_once_for_each_header_and_cell(self):
        visited = []
        def sanitizer(value):
            visited.append(value)
            return str(value)
        self.publish([{"id": "A", "amount": "1", "ignored": "extra"}], cell=sanitizer)
        self.assertEqual(visited, ["id", "amount", "A", "1", "extra"])

    def test_normal_negative_amount_is_not_broken(self):
        self.publish([{"id": "A", "amount": "-1234.56"}])
        with self.path.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream))[0]["amount"], "-1234.56")


if __name__ == "__main__":
    unittest.main()
