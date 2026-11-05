"""R210: accept only native, unambiguous audit row labels.

Synthetic financial fixtures only; all tests offline; no user data.
"""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
import tempfile
import unittest

from fvs_suite.atomic_reports import write_csv_report


class ForgedColumn(str):
    """A misleading key that compares equal to source_row under dict lookup."""
    def __hash__(self):
        return hash("source_row")
    def __eq__(self, other):
        return other == "source_row"


class ExtraSubclass(str):
    pass


class DuplicateItems(dict):
    """A mapping whose supplied items contain conflicting evidence columns."""
    def items(self):
        return list(super().items()) + [("source_row", "999")]


class RowColumnCustodyR210(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r210-")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.target = self.folder / "audit.csv"

    def publish(self, rows, convert=str):
        return write_csv_report(
            self.target, ("id", "amount", "source_row"), rows, convert
        )

    def valid(self):
        return {"id": "A", "amount": "0.10", "source_row": "2"}

    def assert_rollback(self):
        self.assertEqual(list(self.folder.iterdir()), [])

    def read_rows(self):
        with self.target.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_forged_subclass_does_not_fill_missing_provenance(self):
        row = {"id": "A", "amount": "12.00", ForgedColumn("not_a_source"): "400"}
        self.assertTrue("source_row" in row)  # Demonstrates the actual attack.
        with self.assertRaisesRegex(ValueError, "Invalid or duplicate CSV report row columns"):
            self.publish([row])
        self.assert_rollback()

    def test_forged_subclass_rejected_with_legitimate_provenance(self):
        row = self.valid()
        row[ExtraSubclass("bogus")] = "secret"
        with self.assertRaisesRegex(ValueError, "Invalid or duplicate CSV report row columns"):
            self.publish([row])
        self.assert_rollback()

    def test_bytes_extra_column_rejected(self):
        row = self.valid()
        row[b"extra"] = "secret"
        with self.assertRaises(ValueError):
            self.publish([row])
        self.assert_rollback()

    def test_integer_extra_column_rejected(self):
        row = self.valid()
        row[4] = "secret"
        with self.assertRaises(ValueError):
            self.publish([row])
        self.assert_rollback()

    def test_nonstring_object_key_rejected(self):
        row = self.valid()
        row[object()] = "secret"
        with self.assertRaises(ValueError):
            self.publish([row])
        self.assert_rollback()

    def test_duplicate_mapping_item_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid or duplicate CSV report row columns"):
            self.publish([DuplicateItems(self.valid())])
        self.assert_rollback()

    def test_duplicate_items_cannot_override_source_row(self):
        item = DuplicateItems(self.valid())
        self.assertEqual(item["source_row"], "2")
        self.assertEqual(item.items()[-1], ("source_row", "999"))
        with self.assertRaises(ValueError):
            self.publish([item])
        self.assert_rollback()

    def test_blank_native_extra_name_allowed_for_backward_compatibility(self):
        row = self.valid()
        row[""] = "ignored"
        self.publish([row])
        self.assertEqual(self.read_rows()[0]["source_row"], "2")

    def test_invalid_row_object_rejected_with_static_error(self):
        with self.assertRaisesRegex(ValueError, "Invalid CSV report row mapping"):
            self.publish([["A", "0.10", "2"]])
        self.assert_rollback()

    def test_late_forged_row_rolls_back_prior_rows(self):
        def records():
            for index in range(128):
                yield {"id": str(index), "amount": "0.01", "source_row": str(index + 2)}
            yield {"id": "A", "amount": "1", ForgedColumn("shadow"): "2000"}
        with self.assertRaises(ValueError):
            self.publish(records())
        self.assert_rollback()

    def test_existing_signed_evidence_never_overwritten(self):
        self.target.write_bytes(b"original signed report")
        with self.assertRaises(ValueError):
            self.publish([{"id": "A", "amount": "1", ForgedColumn("shadow"): "3"}])
        self.assertEqual(self.target.read_bytes(), b"original signed report")
        self.assertEqual(list(self.folder.iterdir()), [self.target])

    def test_error_message_does_not_echo_private_columns_or_values(self):
        private = "PRIVATE_CLAIM_91321"
        row = {"id": private, "amount": "12", b"secret-file-path": private,
               "source_row": "3"}
        try:
            self.publish([row])
        except ValueError as exc:
            self.assertEqual(str(exc), "Invalid or duplicate CSV report row columns")
            self.assertNotIn(private, str(exc))
        else:
            self.fail("forged financial column was accepted")
        self.assert_rollback()

    def test_mapping_proxy_with_plain_keys_is_valid(self):
        self.publish([MappingProxyType(self.valid())])
        self.assertEqual(self.read_rows(), [self.valid()])

    def test_explicit_empty_and_decimal_values_remain_valid(self):
        self.publish([{"id": "A", "amount": Decimal("0.00"), "source_row": ""}])
        self.assertEqual(self.read_rows()[0], {"id": "A", "amount": "0.00", "source_row": ""})

    def test_native_extra_field_still_sanitized_once_then_ignored(self):
        seen = []
        def sanitize(value):
            seen.append(value)
            return str(value)
        row = dict(self.valid(), extra="private-extra")
        self.publish([row], sanitize)
        self.assertEqual(seen, ["id", "amount", "source_row", "A", "0.10", "2", "private-extra"])
        self.assertEqual(self.read_rows()[0], self.valid())

    def test_same_valid_report_emits_utf8_bom(self):
        self.publish([self.valid()])
        self.assertTrue(self.target.read_bytes().startswith(bytes((0xEF, 0xBB, 0xBF))))
        self.assertEqual(self.read_rows(), [self.valid()])


if __name__ == "__main__":
    unittest.main()
