"""R168: Invoice Twin must not trust subclassed source keys or money operands.

All evidence is synthetic, local, and review-only. This tests the direct
candidate API that callers may invoke without descriptor-checked CSV input.
"""
from __future__ import annotations

from datetime import date
from decimal import Context, Decimal, Inexact, Rounded, localcontext
import unittest

from fvs_suite.invoice_match import candidate_pairs


def source(row="2", *, v="ACME", inv="INV1", amt=None):
    return {
        "row": row, "v": v, "inv": inv,
        "amt": Decimal("12.00") if amt is None else amt,
        "dt": date(2026, 1, 1),
        "vendor": "Acme original", "invoice_number": "INV1",
    }


class PlainStrSubclass(str):
    pass


class IdentityAlias(str):
    """An apparent different source identifier that compares as ACME/INV1."""

    def __new__(cls, text, claimed):
        obj = super().__new__(cls, text)
        obj.claimed = claimed
        return obj

    def __hash__(self):
        return hash(self.claimed)

    def __eq__(self, other):
        return str(other) == self.claimed


class LyingDecimal(Decimal):
    """Can override comparison, hash and classification despite being Decimal."""

    def __hash__(self):
        return hash(Decimal("12.00"))

    def __eq__(self, other):
        return True

    def is_finite(self):
        return True


class HiddenAmount(Decimal):
    def as_tuple(self):
        raise AssertionError("Subclass hook was called while validating money")


class ForbiddenDictHooks(dict):
    def keys(self):
        raise AssertionError("untrusted keys override was called")

    def items(self):
        raise AssertionError("untrusted items override was called")

    def get(self, key, default=None):
        raise AssertionError("untrusted get override was called")

    def __getitem__(self, key):
        raise AssertionError("untrusted getitem override was called")

    def __iter__(self):
        raise AssertionError("untrusted iter override was called")


class InvoiceExactPrimitivesR168(unittest.TestCase):
    def reject(self, record, phrase):
        with self.assertRaisesRegex(ValueError, phrase):
            candidate_pairs([record])

    def test_reject_vendor_equality_alias(self):
        self.reject(source(v=IdentityAlias("BETA", "ACME")), "normalized ASCII")

    def test_reject_invoice_equality_alias(self):
        self.reject(source(inv=IdentityAlias("INV2", "INV1")), "normalized ASCII")

    def test_reject_vendor_plain_subclass(self):
        self.reject(source(v=PlainStrSubclass("ACME")), "normalized ASCII")

    def test_reject_invoice_plain_subclass(self):
        self.reject(source(inv=PlainStrSubclass("INV1")), "normalized ASCII")

    def test_reject_row_plain_subclass(self):
        self.reject(source(row=PlainStrSubclass("2")), "canonical physical CSV row")

    def test_reject_row_equality_alias(self):
        self.reject(source(row=IdentityAlias("3", "2")), "canonical physical CSV row")

    def test_reject_decimal_plain_subclass(self):
        self.reject(source(amt=type("OrdinaryDecimalSubclass", (Decimal,), {})("12.00")),
                    "finite exact Decimal")

    def test_reject_decimal_lying_comparison(self):
        self.reject(source(amt=LyingDecimal("12.00")), "finite exact Decimal")

    def test_reject_decimal_lying_hash(self):
        self.reject(source(amt=LyingDecimal("13.00")), "finite exact Decimal")

    def test_reject_decimal_classification_hook(self):
        self.reject(source(amt=LyingDecimal("NaN")), "finite exact Decimal")

    def test_reject_decimal_tuple_hook(self):
        self.reject(source(amt=HiddenAmount("12.00")), "finite exact Decimal")

    def test_reject_extra_subclass_field_name(self):
        record = source()
        record[PlainStrSubclass("unexpected")] = "private"
        self.reject(record, "field names must be plain text")

    def test_reject_row_field_name_subclass(self):
        record = source()
        del record["row"]
        record[PlainStrSubclass("row")] = "2"
        self.reject(record, "field names must be plain text")

    def test_reject_alias_field_name_hash(self):
        record = source()
        del record["row"]
        record[IdentityAlias("SHADOW", "row")] = "2"
        self.reject(record, "field names must be plain text")

    def test_reject_vendor_field_name_subclass(self):
        record = source()
        del record["v"]
        record[PlainStrSubclass("v")] = "ACME"
        self.reject(record, "field names must be plain text")

    def test_reject_amount_field_name_subclass(self):
        record = source()
        del record["amt"]
        record[PlainStrSubclass("amt")] = Decimal("12.00")
        self.reject(record, "field names must be plain text")

    def test_no_subclassed_dict_hooks_executed(self):
        rows = [ForbiddenDictHooks(source()),
                ForbiddenDictHooks(source(row="3"))]
        pairs = candidate_pairs(rows)
        self.assertEqual([(a["row"], b["row"]) for a, b, _, _ in pairs],
                         [("2", "3")])

    def test_rejection_does_not_mutate_input(self):
        item = source(v=PlainStrSubclass("ACME"))
        original_keys = tuple(item.keys())
        original_value = item["v"]
        self.reject(item, "normalized ASCII")
        self.assertEqual(tuple(item.keys()), original_keys)
        self.assertIs(item["v"], original_value)

    def test_late_bad_vendor_fails_without_partial_result(self):
        def stream():
            yield source()
            yield source(row="3", inv="INV2")
            yield source(row="4", v=IdentityAlias("BETA", "ACME"))
        with self.assertRaisesRegex(ValueError, "normalized ASCII"):
            candidate_pairs(stream())

    def test_late_bad_money_fails_without_partial_result(self):
        def stream():
            yield source()
            yield source(row="3", inv="INV2")
            yield source(row="4", amt=LyingDecimal("13"))
        with self.assertRaisesRegex(ValueError, "finite exact Decimal"):
            candidate_pairs(stream())

    def test_private_alias_not_reflected_in_error(self):
        secret = "PRIVATE-CUSTOMER-ACCOUNT-111"
        with self.assertRaises(ValueError) as caught:
            candidate_pairs([source(v=IdentityAlias(secret, "ACME"))])
        self.assertNotIn(secret, str(caught.exception))

    def test_private_field_name_not_reflected_in_error(self):
        secret = "PRIVATE-CUSTOMER-FIELD-222"
        item = source()
        item[PlainStrSubclass(secret)] = "secret value"
        with self.assertRaises(ValueError) as caught:
            candidate_pairs([item])
        self.assertNotIn(secret, str(caught.exception))

    def test_plain_exact_group_is_preserved(self):
        pairs = candidate_pairs([source(row="3"), source(row="2")])
        self.assertEqual([(a["row"], b["row"], status) for a, b, status, _ in pairs],
                         [("2", "3", "exact_invoice_key")])

    def test_plain_near_group_is_preserved(self):
        pairs = candidate_pairs([source(row="2"), source(row="3", inv="INV2")])
        self.assertEqual([(a["row"], b["row"], status) for a, b, status, _ in pairs],
                         [("2", "3", "review_possible_duplicate")])

    def test_exact_subcent_decimal_and_hostile_context(self):
        rows = [source(amt=Decimal("0.00000001")),
                source(row="3", inv="INV2", amt=Decimal("0.00000001"))]
        with localcontext(Context(prec=2, Emax=4, Emin=-4)) as ctx:
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            pairs = candidate_pairs(rows)
        self.assertEqual([(a["amt"], b["amt"]) for a, b, *_ in pairs],
                         [(Decimal("0.00000001"), Decimal("0.00000001"))])

    def test_owned_snapshots_still_survive_original_mutation(self):
        a, b = source(), source(row="3", inv="INV2")
        pair = candidate_pairs([a, b])[0]
        a["row"] = "500"
        b["amt"] = Decimal("0")
        self.assertEqual((pair[0]["row"], pair[1]["amt"]),
                         ("2", Decimal("12.00")))


if __name__ == "__main__":
    unittest.main()
