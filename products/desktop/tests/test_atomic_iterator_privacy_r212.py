"""R212: private iterable/callback exceptions cannot escape CSV evidence custody.

No network or customer data. Synthetic strings deliberately resemble sensitive
financial records to prove both the visible error and hidden exception context
are sanitized while atomic publication is preserved.
"""
from __future__ import annotations

import csv
from collections import UserDict
from decimal import Decimal
from pathlib import Path
import tempfile
import traceback
import unittest

from fvs_suite.atomic_reports import write_csv_report


SECRET = "PRIVATE_ACCOUNT_990011_AMT_4199"


class IteratorPrivacyR212(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r212-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.out = self.folder / "evidence.csv"

    def publish(self, rows=None, fields=("id", "amount"), cell=str):
        if rows is None:
            rows = [{"id": "a", "amount": Decimal("0.10")}]
        return write_csv_report(self.out, fields, rows, cell)

    def protected_error(self, expected, callback):
        try:
            callback()
        except ValueError as exc:
            self.assertEqual(str(exc), expected)
            self.assertIsNone(exc.__context__)
            self.assertIsNone(exc.__cause__)
            self.assertNotIn(SECRET, "".join(traceback.format_exception(exc)))
        else:
            self.fail("Expected private input failure")
        self.assertFalse(list(self.folder.glob("*.partial")))
        self.assertFalse(list(self.folder.glob(".*.partial")))

    def test_header_sanitizer_hidden_context_cannot_leak(self):
        def converter(value):
            if value == "amount":
                raise RuntimeError(SECRET)
            return str(value)
        self.protected_error("CSV report cell sanitizer failed", lambda: self.publish(cell=converter))
        self.assertFalse(self.out.exists())

    def test_row_sanitizer_hidden_context_cannot_leak(self):
        def converter(value):
            if value == SECRET:
                raise LookupError(SECRET)
            return str(value)
        self.protected_error("CSV report cell sanitizer failed",
                             lambda: self.publish([{"id": "a", "amount": SECRET}], cell=converter))
        self.assertFalse(self.out.exists())

    def test_late_sanitizer_failure_does_not_replace_evidence(self):
        self.out.write_bytes(b"PREVIOUS_VERIFIED_EVIDENCE")
        def converter(value):
            if value == SECRET:
                raise ValueError(SECRET)
            return str(value)
        rows = [{"id": str(n), "amount": "1.00"} for n in range(90)]
        rows.append({"id": "tail", "amount": SECRET})
        self.protected_error("CSV report cell sanitizer failed", lambda: self.publish(rows, cell=converter))
        self.assertEqual(self.out.read_bytes(), b"PREVIOUS_VERIFIED_EVIDENCE")

    def test_fields_generator_error_redacted_without_staging(self):
        def fields():
            yield "id"
            raise RuntimeError(SECRET)
        self.protected_error("CSV report columns could not be read", lambda: self.publish(fields=fields()))
        self.assertFalse(self.out.exists())

    def test_fields_iter_method_error_redacted(self):
        class BadFields:
            def __iter__(self):
                raise OSError(SECRET)
        self.protected_error("CSV report columns could not be read", lambda: self.publish(fields=BadFields()))
        self.assertFalse(self.out.exists())

    def test_row_iter_method_error_redacted(self):
        class BadRows:
            def __iter__(self):
                raise RuntimeError(SECRET)
        self.protected_error("CSV report rows could not be read", lambda: self.publish(BadRows()))
        self.assertFalse(self.out.exists())

    def test_row_generator_error_redacted_after_many_rows(self):
        def rows():
            for n in range(80):
                yield {"id": str(n), "amount": "1.25"}
            raise RuntimeError(SECRET)
        self.protected_error("CSV report rows could not be read", lambda: self.publish(rows()))
        self.assertFalse(self.out.exists())

    def test_late_row_generator_error_preserves_existing_evidence(self):
        self.out.write_bytes(b"PREVIOUS_VERIFIED_EVIDENCE")
        def rows():
            yield {"id": "a", "amount": "1.25"}
            raise ValueError(SECRET)
        self.protected_error("CSV report rows could not be read", lambda: self.publish(rows()))
        self.assertEqual(self.out.read_bytes(), b"PREVIOUS_VERIFIED_EVIDENCE")

    def test_row_items_method_error_redacted(self):
        class BadMapping(UserDict):
            def items(self):
                raise RuntimeError(SECRET)
        self.protected_error("CSV report row columns could not be read",
                             lambda: self.publish([BadMapping(id="x", amount="1.00")]))
        self.assertFalse(self.out.exists())

    def test_row_items_iterator_error_redacted(self):
        class BadMapping(UserDict):
            def items(self):
                yield "id", "a"
                raise OSError(SECRET)
        self.protected_error("CSV report row columns could not be read",
                             lambda: self.publish([BadMapping(id="a", amount="1.00")]))
        self.assertFalse(self.out.exists())

    def test_non_mapping_is_still_rejected_without_private_repr(self):
        class NotARow:
            def __repr__(self):
                raise RuntimeError(SECRET)
        self.protected_error("Invalid CSV report row mapping", lambda: self.publish([NotARow()]))
        self.assertFalse(self.out.exists())

    def test_fields_valid_generator_and_decimal_amount_roundtrip(self):
        self.publish(fields=(name for name in ("id", "amount")))
        with self.out.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream)), [{"id": "a", "amount": "0.10"}])

    def test_rows_valid_generator_is_consumed_once(self):
        invoked = 0
        def rows():
            nonlocal invoked
            for n in range(35):
                invoked += 1
                yield {"id": str(n), "amount": str(n) + ".00"}
        self.publish(rows())
        self.assertEqual(invoked, 35)
        with self.out.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(len(list(csv.DictReader(stream))), 35)

    def test_empty_rows_still_publish_header_only(self):
        self.publish(iter(()))
        with self.out.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.reader(stream)), [["id", "amount"]])

    def test_keyboard_interrupt_not_swallowed(self):
        def rows():
            raise KeyboardInterrupt()
            yield {"id": "a", "amount": "1.00"}
        with self.assertRaises(KeyboardInterrupt):
            self.publish(rows())
        self.assertFalse(self.out.exists())
        self.assertFalse(list(self.folder.glob(".*.partial")))

    def test_system_exit_from_sanitizer_not_swallowed(self):
        def converter(value):
            raise SystemExit(42)
        with self.assertRaises(SystemExit) as exc:
            self.publish(cell=converter)
        self.assertEqual(exc.exception.code, 42)
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()
