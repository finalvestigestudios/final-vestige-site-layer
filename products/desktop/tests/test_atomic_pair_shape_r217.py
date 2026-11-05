"""R217: CSV mapping items must be native two-element pairs before unpacking.

Synthetic finance fixtures only. No network, external records or premium files.
"""
from __future__ import annotations

import csv
from collections import UserDict
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
import tempfile
import traceback
import unittest

from fvs_suite.atomic_reports import write_csv_report


SECRET = "PRIVATE_LEDGER_82490_AMOUNT_3999"
ERROR = "Invalid or duplicate CSV report row columns"


class PairMapping(UserDict):
    def __init__(self, items):
        super().__init__({"id": "SOURCE-ID", "amount": "0.10", "source_row": "2"})
        self.supplied_items = items

    def items(self):
        return iter(self.supplied_items)


class HijackedTuple(tuple):
    def __iter__(self):
        return iter(("id", "FORGED-TRANSACTION"))


class ExplodingTuple(tuple):
    def __iter__(self):
        raise RuntimeError(SECRET)


class ExplodingObject:
    def __iter__(self):
        raise RuntimeError(SECRET)

    def __len__(self):
        raise RuntimeError(SECRET)

    def __repr__(self):
        raise RuntimeError(SECRET)


class PairShapeCustodyR217(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r217-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.target = self.root / "audit-evidence.csv"
        self.fields = ("id", "amount", "source_row")

    def valid(self):
        return {"id": "SOURCE-ID", "amount": Decimal("0.10"), "source_row": "2"}

    def write(self, rows, sanitizer=str):
        return write_csv_report(self.target, self.fields, rows, sanitizer)

    def assert_private_rejection(self, rows, expected=ERROR):
        try:
            self.write(rows)
        except ValueError as exc:
            self.assertEqual(str(exc), expected)
            self.assertIsNone(exc.__context__)
            self.assertIsNone(exc.__cause__)
            self.assertNotIn(SECRET, "".join(traceback.format_exception(exc)))
        else:
            self.fail("Untrusted mapping pair escaped structural validation")
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.glob(".*.partial")), [])

    def test_singleton_tuple_cannot_drop_evidence_column(self):
        self.assert_private_rejection([PairMapping([("id", "A"), ("amount",), ("source_row", "2")])])

    def test_three_element_tuple_cannot_replace_amount(self):
        self.assert_private_rejection([PairMapping([("id", "A"), ("amount", "0.10", SECRET), ("source_row", "2")])])

    def test_empty_tuple_is_rejected(self):
        self.assert_private_rejection([PairMapping([(), ("amount", "0.10"), ("source_row", "2")])])

    def test_list_pairs_rejected_instead_of_invoking_custom_list_iteration(self):
        self.assert_private_rejection([PairMapping([["id", "A"], ("amount", "0.10"), ("source_row", "2")])])

    def test_string_pair_not_interpreted_as_two_column_characters(self):
        self.assert_private_rejection([PairMapping(["id", ("amount", "0.10"), ("source_row", "2")])])

    def test_none_item_is_rejected_without_untrusted_unpack(self):
        self.assert_private_rejection([PairMapping([None, ("amount", "0.10"), ("source_row", "2")])])

    def test_tuple_subclass_cannot_forge_source_id_by_overriding_iteration(self):
        self.assert_private_rejection([PairMapping([HijackedTuple(("id", "SOURCE-ID")), ("amount", "0.10"), ("source_row", "2")])])

    def test_tuple_subclass_exception_has_no_private_context(self):
        self.assert_private_rejection([PairMapping([ExplodingTuple(("id", "SOURCE-ID")), ("amount", "0.10"), ("source_row", "2")])])

    def test_custom_pair_exception_never_executed(self):
        self.assert_private_rejection([PairMapping([ExplodingObject(), ("amount", "0.10"), ("source_row", "2")])])

    def test_generator_pair_rejected_without_consuming_private_data(self):
        consumed = []
        def inner():
            consumed.append("opened")
            yield "id"
            yield SECRET
        self.assert_private_rejection([PairMapping([inner(), ("amount", "0.10"), ("source_row", "2")])])
        self.assertEqual(consumed, [])

    def test_failure_after_valid_rows_rolls_back_atomic_publication(self):
        rows = [self.valid() for _ in range(60)]
        rows.append(PairMapping([("id", "A"), ("amount", SECRET, "extra"), ("source_row", "63")]))
        self.assert_private_rejection(rows)

    def test_existing_evidence_is_not_replaced_on_malformed_late_pair(self):
        self.target.write_bytes(b"SIGNED_EVIDENCE_MUST_REMAIN")
        with self.assertRaisesRegex(ValueError, ERROR):
            self.write([self.valid(), PairMapping([("id", "A"), ("amount",)])])
        self.assertEqual(self.target.read_bytes(), b"SIGNED_EVIDENCE_MUST_REMAIN")
        self.assertEqual(list(self.root.glob(".*.partial")), [])

    def test_invalid_pair_never_calls_value_sanitizer(self):
        seen = []
        def safe(value):
            seen.append(value)
            return str(value)
        with self.assertRaisesRegex(ValueError, ERROR):
            self.write([PairMapping([("id", SECRET), ["amount", SECRET], ("source_row", "2")])], safe)
        self.assertEqual(seen, list(self.fields))
        self.assertFalse(self.target.exists())

    def test_native_mapping_proxy_remains_supported_with_decimal(self):
        self.write([MappingProxyType(self.valid())])
        with self.target.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream)),
                             [{"id": "SOURCE-ID", "amount": "0.10", "source_row": "2"}])

    def test_userdict_standard_items_remains_supported(self):
        self.write([UserDict(self.valid())])
        with self.target.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream))[0]["amount"], "0.10")

    def test_normal_extra_column_still_sanitized_once(self):
        seen = []
        def safe(value):
            seen.append(value)
            return str(value)
        source = dict(self.valid())
        source["unused"] = "secondary"
        self.write([source], safe)
        self.assertEqual(seen, [*self.fields, "SOURCE-ID", Decimal("0.10"), "2", "secondary"])
        with self.target.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream))[0]["amount"], "0.10")

    def test_deterministic_csv_bytes_and_exact_decimal(self):
        self.write([self.valid()])
        original = self.target.read_bytes()
        self.assertTrue(original.startswith(bytes((0xEF, 0xBB, 0xBF))))
        second = self.root / "audit-two.csv"
        write_csv_report(second, self.fields, [self.valid()], str)
        self.assertEqual(second.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
