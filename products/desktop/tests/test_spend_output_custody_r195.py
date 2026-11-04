"""R195 SpendMap direct-API evidence is read-only native source text.

Synthetic source only. Output immutability is not a file authenticity claim;
source SHA-256 must still come from descriptor-verified bytes. No approvals.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal, Inexact, Rounded, localcontext
from types import MappingProxyType
import unittest

from fvs_suite.spend_input import validated_spend_rows

PRIVATE = "PRIVATE-ACCOUNT-9911\n=IMPORTDATA('secret')"


def row(number="2", **extra):
    result = {"row": number, "vendor": "ALPHA", "date": "2026-03-02",
              "amount": "12.34", "category": "Supplies"}
    result.update(extra)
    return result


def iterate(rows, *, normal=str.upper, day=date.fromisoformat, money=Decimal):
    return validated_spend_rows(rows, normalize_vendor=normal,
                                parse_date=day, parse_money=money)


class HostileDict(dict):
    def __getitem__(self, key):
        raise AssertionError("hostile lookup")
    def get(self, key, default=None):
        raise AssertionError("hostile get")
    def keys(self):
        raise AssertionError("hostile keys")
    def items(self):
        raise AssertionError("hostile items")
    def __iter__(self):
        raise AssertionError("hostile iterator")


class HostileStr(str):
    def __str__(self):
        raise AssertionError("hostile __str__")
    def __repr__(self):
        raise AssertionError("hostile __repr__")
    def __format__(self, fmt):
        raise AssertionError("hostile format")


class HostileObject:
    def __str__(self):
        raise AssertionError("hostile __str__")
    def __repr__(self):
        raise AssertionError("hostile __repr__")
    def __hash__(self):
        raise AssertionError("hostile __hash__")
    def __eq__(self, value):
        raise AssertionError("hostile comparison")


class SpendOutputCustodyR195(unittest.TestCase):
    def reject_without_callbacks(self, records):
        called = []
        it = iterate(records, normal=lambda value: called.append(value) or value)
        with self.assertRaises(ValueError) as caught:
            next(it)
        self.assertIn("source column values must be plain text", str(caught.exception))
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(called, [])
        with self.assertRaises(StopIteration):
            next(it)

    def test_readonly_mapping_type(self):
        result = list(iterate([row()]))[0][0]
        self.assertIs(type(result), MappingProxyType)
        self.assertEqual(result["row"], "2")

    def test_cannot_rewrite_physical_row(self):
        saved = list(iterate([row()]))[0][0]
        with self.assertRaises(TypeError):
            saved["row"] = "9999"
        self.assertEqual(saved["row"], "2")

    def test_cannot_rewrite_original_vendor(self):
        saved = list(iterate([row()]))[0][0]
        with self.assertRaises(TypeError):
            saved["vendor"] = "FORGED"
        self.assertEqual(saved["vendor"], "ALPHA")

    def test_cannot_rewrite_original_amount(self):
        saved = list(iterate([row()]))[0][0]
        with self.assertRaises(TypeError):
            saved["amount"] = "900000000000.00"
        self.assertEqual(saved["amount"], "12.34")

    def test_cannot_rewrite_original_date(self):
        saved = list(iterate([row()]))[0][0]
        with self.assertRaises(TypeError):
            saved["date"] = "2050-01-01"
        self.assertEqual(saved["date"], "2026-03-02")

    def test_cannot_remove_original_field(self):
        saved = list(iterate([row()]))[0][0]
        with self.assertRaises(TypeError):
            del saved["row"]
        self.assertEqual(saved["row"], "2")

    def test_cannot_add_source_column(self):
        saved = list(iterate([row()]))[0][0]
        with self.assertRaises(TypeError):
            saved["approval"] = "APPROVED"
        self.assertNotIn("approval", saved)

    def test_mutating_mapping_methods_not_exposed(self):
        saved = list(iterate([row()]))[0][0]
        for name in ("clear", "update", "pop", "popitem", "setdefault", "__setitem__"):
            with self.subTest(name=name):
                self.assertFalse(hasattr(saved, name))

    def test_mapping_read_protocol_and_dict_copy(self):
        saved = list(iterate([row()]))[0][0]
        self.assertEqual(saved.get("category"), "Supplies")
        self.assertEqual(tuple(saved), tuple(row()))
        self.assertEqual(dict(saved), row())
        self.assertEqual(len(saved), 5)

    def test_empty_records_do_not_call_parser(self):
        called = []
        self.assertEqual(list(iterate([], normal=lambda s: called.append(s))), [])
        self.assertEqual(called, [])

    def test_multiple_rows_are_independently_immutable(self):
        items = [row("8"), row("3", vendor="BETA"), row("20", amount="-0.02")]
        saved = list(iterate(items))
        self.assertEqual([result[0]["row"] for result in saved], ["8", "3", "20"])
        for result in saved:
            with self.assertRaises(TypeError):
                result[0]["row"] = "123"
        self.assertEqual([result[0]["row"] for result in saved], ["8", "3", "20"])
        self.assertEqual(saved[2][-1], Decimal("-0.02"))

    def test_record_remains_readonly_after_later_iteration(self):
        it = iterate([row("2"), row("3")])
        first = next(it)[0]
        self.assertEqual(next(it)[0]["row"], "3")
        with self.assertRaises(TypeError):
            first["row"] = "3"

    def test_original_mutation_after_first_yield_does_not_forge_source(self):
        inputs = [row(), row("3", vendor="BETA", amount="20.00")]
        it = iterate(inputs)
        first = next(it)
        inputs[0]["row"] = "500"
        inputs[1]["amount"] = "-999999.99"
        second = next(it)
        self.assertEqual(first[0]["row"], "2")
        self.assertEqual(second[0]["amount"], "20.00")
        self.assertEqual(second[-1], Decimal("20.00"))

    def test_native_extra_column_retained_as_readonly_text(self):
        saved = list(iterate([row(note="Review manually; not approved")]))[0][0]
        self.assertEqual(saved["note"], "Review manually; not approved")
        with self.assertRaises(TypeError):
            saved["note"] = "Approved"

    def test_native_extra_column_private_text_not_in_error(self):
        saved = list(iterate([row(note=PRIVATE)]))[0][0]
        self.assertEqual(saved["note"], PRIVATE)

    def test_unused_extra_list_fails_before_parsers(self):
        self.reject_without_callbacks([row(), row("3", metadata=[PRIVATE])])

    def test_unused_extra_dict_fails_before_parsers(self):
        self.reject_without_callbacks([row(), row("3", metadata={"secret": PRIVATE})])

    def test_unused_extra_custom_object_fails_without_hooks(self):
        self.reject_without_callbacks([row(), row("3", metadata=HostileObject())])

    def test_unused_extra_str_subclass_fails_without_hooks(self):
        self.reject_without_callbacks([row(), row("3", metadata=HostileStr(PRIVATE))])

    def test_unused_extra_decimal_fails(self):
        self.reject_without_callbacks([row(), row("3", metadata=Decimal("1.00"))])

    def test_unused_extra_bytes_fails(self):
        self.reject_without_callbacks([row(), row("3", metadata=PRIVATE.encode("utf8"))])

    def test_unused_extra_boolean_fails(self):
        self.reject_without_callbacks([row(), row("3", metadata=False)])

    def test_unused_extra_none_fails(self):
        self.reject_without_callbacks([row(), row("3", metadata=None)])

    def test_extra_nontext_on_first_row_fails_before_any_parser(self):
        self.reject_without_callbacks([row(extra=HostileObject()), row("3")])

    def test_native_dict_subclass_overrides_not_called(self):
        saved = list(iterate([HostileDict(row()), HostileDict(row("3"))]))
        self.assertEqual([r[0]["row"] for r in saved], ["2", "3"])
        self.assertTrue(all(type(r[0]) is MappingProxyType for r in saved))

    def test_required_field_diagnostics_unchanged(self):
        item = row("3", amount=12.34)
        with self.assertRaisesRegex(ValueError, "Spend amount must be imported text at physical row 3"):
            list(iterate([row(), item]))

    def test_semantic_late_error_yields_no_rows(self):
        it = iterate([row(), row("3", amount="0.001")])
        with self.assertRaisesRegex(ValueError, "cent precision"):
            next(it)
        with self.assertRaises(StopIteration):
            next(it)

    def test_low_precision_decimal_context_does_not_affect_source(self):
        with localcontext() as ctx:
            ctx.prec = 3
            ctx.traps[Inexact] = ctx.traps[Rounded] = True
            saved = list(iterate([row()]))
        self.assertEqual(saved[0][-1], Decimal("12.34"))
        self.assertEqual(saved[0][0]["amount"], "12.34")

    def test_no_original_mutation(self):
        originals = [row("2", note="A"), row("4", note="B")]
        baseline = [dict(x) for x in originals]
        list(iterate(originals))
        self.assertEqual(originals, baseline)


if __name__ == "__main__":
    unittest.main()
