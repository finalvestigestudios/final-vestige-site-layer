"""R174 SpendMap direct API provenance: native stored rows and primitive values.

Only synthetic values are used. Tests never open a network connection or export data.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal, Inexact, Rounded, localcontext
import unittest

from fvs_suite.spend_input import validated_spend_rows

PRIVATE = "PRIVATE CUSTOMER SECRET"


def record(number="2", *, vendor="ACME", amount="10.25", category="Parts"):
    return {"row": number, "vendor": vendor, "date": "2026-01-02",
            "amount": amount, "category": category}


def parsed(records, *, vendor=None, money=None):
    return list(validated_spend_rows(
        records, normalize_vendor=vendor or (lambda value: value.upper()),
        parse_date=date.fromisoformat, parse_money=money or Decimal))


class ForgedDict(dict):
    """Pretends to contain other financial values through Python hooks."""
    def get(self, field, fallback=None):
        if field == "row":
            return "99"
        if field == "amount":
            return "0.00"
        if field == "vendor":
            return "FORGED"
        if field == "category":
            return "Forged"
        return super().get(field, fallback)

    def __getitem__(self, field):
        raise AssertionError("untrusted __getitem__ hook executed")

    def keys(self):
        raise AssertionError("untrusted keys hook executed")

    def items(self):
        raise AssertionError("untrusted items hook executed")

    def __iter__(self):
        raise AssertionError("untrusted iteration hook executed")


class LyingString(str):
    def __str__(self):
        raise AssertionError("untrusted string conversion executed")

    def __hash__(self):
        raise AssertionError("untrusted string hash executed")

    def __eq__(self, other):
        raise AssertionError("untrusted string equality executed")


class LyingDecimal(Decimal):
    def is_finite(self):
        raise AssertionError("untrusted Decimal predicate executed")

    def copy_abs(self):
        raise AssertionError("untrusted Decimal magnitude executed")


class LyingList(list):
    def __iter__(self):
        raise AssertionError("untrusted list iteration executed")

    def __len__(self):
        raise AssertionError("untrusted list length executed")


class HostileKey:
    def __hash__(self):
        return 12

    def __str__(self):
        raise AssertionError("untrusted key conversion executed")


class SpendNativeCustodyR174(unittest.TestCase):
    def reject(self, rows, fragment, **kwargs):
        with self.assertRaises(ValueError) as caught:
            parsed(rows, **kwargs)
        self.assertIn(fragment, str(caught.exception))
        self.assertNotIn(PRIVATE, str(caught.exception))
        return str(caught.exception)

    def test_plain_rows_preserve_exact_cents_and_month(self):
        result = parsed([record(), record("3", amount="-2.30")])
        self.assertEqual([part[-1] for part in result],
                         [Decimal("10.25"), Decimal("-2.30")])
        self.assertEqual([part[2] for part in result], ["2026-01"] * 2)

    def test_original_plain_records_are_unmodified(self):
        original = [record()]
        expected = [dict(original[0])]
        parsed(original)
        self.assertEqual(original, expected)

    def test_result_owns_independent_dictionary(self):
        original = record()
        snapshot = parsed([original])[0][0]
        self.assertIsNot(snapshot, original)
        original["amount"] = "9999.99"
        self.assertEqual(snapshot["amount"], "10.25")

    def test_spoofed_get_cannot_replace_physical_row(self):
        result = parsed([ForgedDict(record())])
        self.assertEqual(result[0][0]["row"], "2")

    def test_spoofed_get_cannot_replace_amount(self):
        result = parsed([ForgedDict(record())])
        self.assertEqual(result[0][-1], Decimal("10.25"))
        self.assertEqual(result[0][0]["amount"], "10.25")

    def test_spoofed_get_cannot_replace_vendor(self):
        result = parsed([ForgedDict(record())])
        self.assertEqual(result[0][1], "ACME")

    def test_spoofed_get_cannot_replace_category(self):
        result = parsed([ForgedDict(record())])
        self.assertEqual(result[0][3], "Parts")

    def test_spoofed_keys_items_getitem_and_iter_never_called(self):
        self.assertEqual(parsed([ForgedDict(record())])[0][0], record())

    def test_callback_mutation_cannot_change_current_row_provenance(self):
        source = record()
        def change_original(value):
            source.update(row="999", amount="0.00", category="Forged", vendor=PRIVATE)
            return value
        result = parsed([source], vendor=change_original)
        self.assertEqual((result[0][0]["row"], result[0][0]["amount"], result[0][3]),
                         ("2", "10.25", "Parts"))
        self.assertEqual(result[0][-1], Decimal("10.25"))

    def test_no_original_record_mapped_source_changed_by_copy(self):
        original = ForgedDict(record())
        parsed([original])
        self.assertEqual(dict.items(original).__len__(), 5)
        self.assertEqual(dict.__getitem__(original, "row"), "2")

    def test_list_subclass_cannot_override_iteration(self):
        self.reject(LyingList([record()]), "must be a list")

    def test_list_subclass_cannot_override_length(self):
        self.reject(LyingList([record()]), "must be a list")

    def test_custom_nonstring_key_rejected_before_display(self):
        item = record()
        item[HostileKey()] = PRIVATE
        self.reject([item], "field names must be plain text")

    def test_string_subclass_key_rejected_before_hashing(self):
        item = record()
        # Hash while constructing, then reject without calling the hook again.
        # dict.__setitem__ would invoke hash; insert through an innocuous
        # subclass whose own hash is still built-in.
        class Key(str):
            __hash__ = str.__hash__
            def __str__(self):
                raise AssertionError("untrusted key string hook executed")
        item[Key(PRIVATE)] = "value"
        self.reject([item], "field names must be plain text")

    def test_source_row_string_subclass_rejected_without_hooks(self):
        self.reject([record(LyingString(PRIVATE))], "canonical physical CSV row")

    def test_source_vendor_string_subclass_rejected_without_hooks(self):
        self.reject([record(vendor=LyingString(PRIVATE))], "vendor must be imported text")

    def test_source_amount_string_subclass_rejected_without_hooks(self):
        self.reject([record(amount=LyingString(PRIVATE))], "amount must be imported text")

    def test_source_date_string_subclass_rejected_without_hooks(self):
        row = record()
        row["date"] = LyingString(PRIVATE)
        self.reject([row], "date must be imported text")

    def test_source_category_string_subclass_rejected_without_hooks(self):
        self.reject([record(category=LyingString(PRIVATE))], "category must be imported text")

    def test_vendor_normalizer_subclass_rejected_before_equality_hash(self):
        self.reject([record()], "Invalid normalized vendor key",
                    vendor=lambda _: LyingString(PRIVATE))

    def test_money_parser_decimal_subclass_rejected_before_arithmetic(self):
        self.reject([record()], "finite exact Decimal",
                    money=lambda _: LyingDecimal("9999.99"))

    def test_float_parser_not_accepted_as_money(self):
        self.reject([record()], "finite exact Decimal", money=lambda _: 1.5)

    def test_normal_plain_negative_credit_stays_exact(self):
        self.assertEqual(parsed([record(amount="-0.10")])[0][-1], Decimal("-0.10"))

    def test_missing_category_still_uncategorized(self):
        value = record()
        del value["category"]
        self.assertEqual(parsed([value])[0][3], "Uncategorized")

    def test_callback_receives_stored_not_forged_values(self):
        calls = []
        def amount_parser(raw):
            calls.append(raw)
            return Decimal(raw)
        parsed([ForgedDict(record())], money=amount_parser)
        self.assertEqual(calls, ["10.25"])

    def test_duplicate_rows_still_rejected(self):
        self.reject([record(), ForgedDict(record())], "Duplicate spend physical CSV row")

    def test_caller_decimal_traps_stay_unchanged(self):
        with localcontext() as ctx:
            ctx.prec = 4
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            self.assertEqual(parsed([record(amount="999999999999.99")])[0][-1],
                             Decimal("999999999999.99"))
            self.assertEqual(ctx.prec, 4)


if __name__ == "__main__":
    unittest.main()
