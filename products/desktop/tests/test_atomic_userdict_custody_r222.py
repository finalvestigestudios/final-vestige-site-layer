"""R222 end-to-end CSV evidence custody tests (must run on full checkout)."""
from __future__ import annotations

import csv
import tempfile
import unittest
from collections import UserDict
from decimal import Decimal
from pathlib import Path

from fvs_suite.atomic_reports import write_csv_report
from fvs_suite.csv_native_cell import native_report_text
from fvs_suite.csv_userdict_custody import UserDictCustodyError


class FabricatedUserDict(UserDict):
    def __init__(self, stored, virtual):
        super().__init__(stored)
        self.virtual = tuple(virtual)

    def items(self):
        return iter(self.virtual)


class WriterUserDictCustodyR222(unittest.TestCase):
    fields = ("id", "amount", "source_row")

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fv-r222-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.target = self.root / "report.csv"
        self.stored = {"id": "ORIGINAL", "amount": Decimal("0.0100"), "source_row": "12"}

    def publish(self, records):
        return write_csv_report(self.target, self.fields, records, native_report_text)

    def rows(self):
        with self.target.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def assert_rollback(self):
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.glob(".*.partial")), [])

    def test_forged_userdict_identifier_blocked(self):
        forged = (("id", "APPROVED"), ("amount", Decimal("0.0100")), ("source_row", "12"))
        with self.assertRaises(UserDictCustodyError):
            self.publish([FabricatedUserDict(self.stored, forged)])
        self.assert_rollback()

    def test_forged_userdict_amount_blocked(self):
        forged = (("id", "ORIGINAL"), ("amount", Decimal("999.00")), ("source_row", "12"))
        with self.assertRaises(UserDictCustodyError):
            self.publish([FabricatedUserDict(self.stored, forged)])
        self.assert_rollback()

    def test_forged_userdict_cannot_hide_extra_formula(self):
        stored = {**self.stored, "ignored": "=SUM(A1)"}
        with self.assertRaises(UserDictCustodyError):
            self.publish([FabricatedUserDict(stored, tuple(self.stored.items()))])
        self.assert_rollback()

    def test_forged_userdict_cannot_hide_missing_source(self):
        stored = {"id": "ORIGINAL", "amount": Decimal("0.0100")}
        with self.assertRaises(UserDictCustodyError):
            self.publish([FabricatedUserDict(stored, tuple(self.stored.items()))])
        self.assert_rollback()

    def test_native_userdict_preserves_decimal_scale(self):
        self.publish([UserDict(self.stored)])
        self.assertEqual(self.rows()[0], {"id": "ORIGINAL", "amount": "0.0100", "source_row": "12"})
        self.assertTrue(self.target.read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_failed_late_row_cannot_publish_earlier_rows(self):
        bad = FabricatedUserDict(self.stored, (("id", "FAKE"), *tuple(self.stored.items())[1:]))
        with self.assertRaises(UserDictCustodyError):
            self.publish([self.stored for _ in range(10)] + [bad])
        self.assert_rollback()

    def test_preexisting_report_never_overwritten(self):
        self.target.write_bytes(b"EXISTING_AUDIT_REPORT")
        bad = FabricatedUserDict(self.stored, (("id", "FAKE"), *tuple(self.stored.items())[1:]))
        with self.assertRaises(UserDictCustodyError):
            self.publish([bad])
        self.assertEqual(self.target.read_bytes(), b"EXISTING_AUDIT_REPORT")
        self.assertEqual(list(self.root.glob(".*.partial")), [])


if __name__ == "__main__":
    unittest.main()
