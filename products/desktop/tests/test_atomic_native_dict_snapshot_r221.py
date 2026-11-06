"""R221: preserve native dict storage in locally published audit CSV reports.

Synthetic financial fixtures only. No accounts, telemetry, premium assets,
customer records, legal conclusions or automated payment approvals.
"""
from __future__ import annotations

import csv
import tempfile
import unittest
from collections import UserDict
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType

from fvs_suite.atomic_reports import write_csv_report
from fvs_suite.csv_native_cell import native_report_text


class ShadowedDict(dict):
    """A dict subclass with genuine stored values and a deceptive items view."""

    def __init__(self, original, fabricated=()):
        super().__init__(original)
        self._fabricated = fabricated
        self.calls = 0

    def items(self):
        self.calls += 1
        return iter(self._fabricated)


class PoisonedDict(dict):
    calls = 0

    def items(self):
        self.calls += 1
        raise RuntimeError("SYNTHETIC_PRIVATE_CLIENT_1291")

    def keys(self):
        self.calls += 1
        raise RuntimeError("SYNTHETIC_PRIVATE_CLIENT_1291")

    def __getitem__(self, key):
        self.calls += 1
        raise RuntimeError("SYNTHETIC_PRIVATE_CLIENT_1291")


class NativeDictSnapshotR221(unittest.TestCase):
    fields = ("id", "amount", "source_row")

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r221-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.output = self.root / "financial-evidence.csv"

    def write(self, rows, *, sanitizer=native_report_text, fields=None, output=None):
        return write_csv_report(output or self.output, fields or self.fields, rows, sanitizer)

    def read(self, path=None):
        with (path or self.output).open(encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))

    def assert_no_partial(self):
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_reproduced_forged_transaction_identifier_cannot_publish(self):
        stored = {"id": "ORIGINAL-ROW-42", "amount": Decimal("0.10"), "source_row": "42"}
        forged = (("id", "FRAUDULENT-APPROVED-ID"), ("amount", "999999.99"), ("source_row", "42"))
        row = ShadowedDict(stored, forged)
        self.write([row])
        self.assertEqual(self.read(), [{"id": "ORIGINAL-ROW-42", "amount": "0.10", "source_row": "42"}])
        self.assertEqual(row.calls, 0)
        self.assert_no_partial()

    def test_shadowed_items_cannot_change_money(self):
        row = ShadowedDict({"id": "R1", "amount": Decimal("12.3400"), "source_row": "7"},
                           (("id", "R1"), ("amount", "0.00"), ("source_row", "7")))
        self.write([row])
        self.assertEqual(self.read()[0]["amount"], "12.3400")
        self.assertEqual(row.calls, 0)

    def test_shadowed_items_cannot_hide_missing_audit_reference(self):
        row = ShadowedDict({"id": "R1", "amount": "0.10"},
                           (("id", "R1"), ("amount", "0.10"), ("source_row", "FAKE")))
        with self.assertRaisesRegex(ValueError, "Incomplete CSV report row schema"):
            self.write([row])
        self.assertFalse(self.output.exists())
        self.assert_no_partial()

    def test_shadowed_items_cannot_hide_unchecked_formula_extra(self):
        row = ShadowedDict({"id": "R1", "amount": "1.00", "source_row": "2",
                            "hidden": "=HYPERLINK(A1)"},
                           (("id", "R1"), ("amount", "1.00"), ("source_row", "2")))
        with self.assertRaisesRegex(ValueError, "Unsafe or non-text CSV report cell"):
            self.write([row])
        self.assertFalse(self.output.exists())
        self.assert_no_partial()

    def test_shadowed_items_cannot_hide_non_native_extra_cell(self):
        row = ShadowedDict({"id": "R1", "amount": "1.00", "source_row": "2",
                            "hidden": object()},
                           (("id", "R1"), ("amount", "1.00"), ("source_row", "2")))
        with self.assertRaisesRegex(ValueError, "CSV report cell sanitizer failed") as ctx:
            self.write([row])
        self.assertIsNone(ctx.exception.__context__)
        self.assert_no_partial()

    def test_shadowed_items_cannot_hide_overwide_underlying_record(self):
        source = {"id": "R1", "amount": "1.00", "source_row": "2"}
        source.update({f"extra_{i}": "x" for i in range(255)})
        row = ShadowedDict(source, (("id", "R1"), ("amount", "1.00"), ("source_row", "2")))
        with self.assertRaisesRegex(ValueError, "row column limit exceeded"):
            self.write([row])
        self.assert_no_partial()

    def test_shadowed_items_cannot_reorder_stored_data(self):
        row = ShadowedDict({"id": "R1", "amount": "0.10", "source_row": "2"},
                           (("amount", "0.10"), ("id", "R1"), ("source_row", "2")))
        seen = []
        def sanitizer(value):
            seen.append(value)
            return native_report_text(value)
        self.write([row], sanitizer=sanitizer)
        self.assertEqual(seen, [*self.fields, "R1", "0.10", "2"])
        self.assertEqual(row.calls, 0)

    def test_poisoned_items_and_getitem_are_never_invoked(self):
        row = PoisonedDict({"id": "R1", "amount": Decimal("-1.20"), "source_row": "2"})
        self.write([row])
        self.assertEqual(row.calls, 0)
        self.assertEqual(self.read()[0]["amount"], "-1.20")
        self.assert_no_partial()

    def test_shadowed_late_record_cannot_corrupt_earlier_rows(self):
        valid = {"id": "FIRST", "amount": "0.10", "source_row": "2"}
        evil = ShadowedDict({"id": "SECOND", "amount": "0.10", "source_row": "3",
                             "extra": "=SUM(A1)"},
                            (("id", "SECOND"), ("amount", "0.10"), ("source_row", "3")))
        with self.assertRaises(ValueError):
            self.write([valid] * 25 + [evil])
        self.assertFalse(self.output.exists())
        self.assert_no_partial()

    def test_preexisting_evidence_never_overwritten_after_forgery(self):
        prior = b"IMMUTABLE-LOCAL-AUDIT-EVIDENCE"
        self.output.write_bytes(prior)
        row = ShadowedDict({"id": "ACTUAL", "amount": "1.00", "source_row": "2"},
                           (("id", "FORGED"), ("amount", "1.00"), ("source_row", "2")))
        with self.assertRaises(FileExistsError):
            self.write([row])
        self.assertEqual(self.output.read_bytes(), prior)
        self.assert_no_partial()

    def test_native_dict_subclass_emits_same_bytes_as_exact_dict(self):
        record = {"id": "ROW-01", "amount": Decimal("0.0100"), "source_row": "2"}
        disguised = ShadowedDict(record, (("id", "FAKE"),))
        a = self.root / "a.csv"
        b = self.root / "b.csv"
        self.write([record], output=a)
        self.write([disguised], output=b)
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertTrue(a.read_bytes().startswith(b"\xef\xbb\xbf"))
        self.assertEqual(disguised.calls, 0)

    def test_native_dict_subclass_keeps_negative_decimal_and_leading_zeros(self):
        row = ShadowedDict({"id": "0007", "amount": Decimal("-0.0100"), "source_row": "0002"}, ())
        self.write([row])
        self.assertEqual(self.read()[0], {"id": "0007", "amount": "-0.0100", "source_row": "0002"})

    def test_ordinary_dict_extra_values_are_still_processed(self):
        seen = []
        row = {"id": "R1", "amount": Decimal("1.00"), "source_row": "2", "note": "safe"}
        self.write([row], sanitizer=lambda value: seen.append(value) or native_report_text(value))
        self.assertEqual(seen, [*self.fields, "R1", Decimal("1.00"), "2", "safe"])
        self.assertEqual(self.read()[0]["amount"], "1.00")

    def test_custom_userdict_remains_supported(self):
        self.write([UserDict({"id": "U1", "amount": Decimal("0.10"), "source_row": "2"})])
        self.assertEqual(self.read()[0]["amount"], "0.10")

    def test_mapping_proxy_remains_supported(self):
        self.write([MappingProxyType({"id": "P1", "amount": Decimal("0.10"), "source_row": "2"})])
        self.assertEqual(self.read()[0]["id"], "P1")

    def test_plain_dict_supports_unicode_without_formula(self):
        self.write([{"id": "Café", "amount": "0.10", "source_row": "8"}])
        self.assertEqual(self.read()[0]["id"], "Café")

    def test_dict_subclass_cannot_skip_ignored_large_unsafe_cell(self):
        row = ShadowedDict({"id": "R", "amount": "0.10", "source_row": "2",
                            "unused": "A" * 1_048_577}, ())
        with self.assertRaisesRegex(ValueError, "cell sanitizer failed"):
            self.write([row])
        self.assert_no_partial()

    def test_dict_subclass_skips_no_honest_extra_fields(self):
        row = ShadowedDict({"id": "R", "amount": "0.10", "source_row": "2",
                            "note": "preserved only in validation"}, ())
        seen = []
        self.write([row], sanitizer=lambda value: seen.append(value) or native_report_text(value))
        self.assertIn("preserved only in validation", seen)
        self.assertEqual(len(self.read()[0]), 3)

    def test_report_can_be_reproduced_in_separate_folders(self):
        row = ShadowedDict({"id": "R", "amount": Decimal("-0.0200"), "source_row": "4"}, ())
        a = self.root / "one.csv"
        b = self.root / "two.csv"
        self.write([row], output=a)
        self.write([row], output=b)
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assert_no_partial()

    def test_no_automatic_decision_is_issued_by_writer(self):
        row = ShadowedDict({"id": "REVIEW-ONLY", "amount": Decimal("0.10"), "source_row": "3"}, ())
        self.write([row])
        self.assertEqual(set(self.read()[0]), set(self.fields))
        self.assertNotIn("approved", self.output.read_text(encoding="utf-8-sig").lower())


if __name__ == "__main__":
    unittest.main()
