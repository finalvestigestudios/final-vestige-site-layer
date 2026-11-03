"""R172: premium finance event classification must use native stored source values.

Only synthetic records. These tests intentionally exercise direct Python API
callers with adversarial dict subclasses; ordinary CSV intake remains unchanged.
"""
from __future__ import annotations

from collections import UserDict
from decimal import Decimal
import unittest

from fvs_suite.grant_input import claim_kind
from fvs_suite.procurement_input import event_kind


class ForgedGet(dict):
    """Report the opposite movement via get(), while retaining real storage."""

    def get(self, key, default=None):
        if key == "event_type":
            return "invoice" if dict.get(self, key) == "credit" else "receipt"
        if key == "claim_type":
            return "claim"
        return dict.get(self, key, default)


class HostileView(dict):
    """The legacy dict(row) / row.items() approaches could see fake values."""

    def get(self, key, default=None):
        return "invoice" if key == "event_type" else "claim"

    def keys(self):
        return ("event_type", "claim_type", "row")

    def items(self):
        return (("event_type", "invoice"), ("claim_type", "claim"), ("row", "2"))

    def __iter__(self):
        return iter(("event_type", "claim_type", "row"))

    def __getitem__(self, key):
        if key in ("event_type", "claim_type"):
            return "invoice" if key == "event_type" else "claim"
        return dict.__getitem__(self, key)


class HostileText(str):
    def __str__(self):
        raise AssertionError("Private text __str__ was invoked")

    def strip(self, *args, **kwargs):
        return "invoice"

    def casefold(self):
        return "claim"


class HostileField(str):
    def __hash__(self):
        return hash("unrelated-field")

    def __eq__(self, other):
        return False


class HostileObject:
    def __str__(self):
        raise AssertionError("Private object string conversion executed")

    def __eq__(self, other):
        raise AssertionError("Private object equality executed")


class PremiumEventNativeCustodyR172(unittest.TestCase):
    def test_procurement_stored_credit_overrides_fake_invoice_get(self):
        self.assertEqual(event_kind(ForgedGet(event_type="credit", row="2"), source="invoice"), "credit")

    def test_procurement_stored_return_overrides_fake_receipt_get(self):
        self.assertEqual(event_kind(ForgedGet(event_type="return", row="3"), source="receipt"), "return")

    def test_grant_stored_credit_overrides_fake_claim_get(self):
        self.assertEqual(claim_kind(ForgedGet(claim_type="credit", row="2")), "credit")

    def test_procurement_hostile_views_do_not_change_credit(self):
        row = HostileView(event_type="credit", row="2")
        self.assertEqual(event_kind(row, source="invoice"), "credit")

    def test_procurement_hostile_views_do_not_change_return(self):
        row = HostileView(event_type="return", row="2")
        self.assertEqual(event_kind(row, source="receipt"), "return")

    def test_grant_hostile_views_do_not_change_credit(self):
        self.assertEqual(claim_kind(HostileView(claim_type="credit", row="2")), "credit")

    def test_native_data_is_not_mutated(self):
        row = ForgedGet(event_type="credit", claim_type="credit", row="2")
        before = dict(dict.items(row))
        self.assertEqual(event_kind(row, source="invoice"), "credit")
        self.assertEqual(claim_kind(row), "credit")
        self.assertEqual(dict(dict.items(row)), before)

    def test_procurement_rejects_non_dict_mapping_before_get(self):
        with self.assertRaisesRegex(ValueError, "dictionary"):
            event_kind(UserDict(event_type="credit"), source="invoice")

    def test_grant_rejects_non_dict_mapping_before_get(self):
        with self.assertRaisesRegex(ValueError, "dictionary"):
            claim_kind(UserDict(claim_type="credit"))

    def test_procurement_rejects_forged_field_key(self):
        row = {"event_type": "credit", HostileField("event_type"): "invoice"}
        with self.assertRaisesRegex(ValueError, "field names"):
            event_kind(row, source="invoice")

    def test_grant_rejects_forged_field_key(self):
        row = {"claim_type": "credit", HostileField("claim_type"): "claim"}
        with self.assertRaisesRegex(ValueError, "field names"):
            claim_kind(row)

    def test_procurement_rejects_hostile_type_value_without_hooks(self):
        with self.assertRaisesRegex(ValueError, "plain text"):
            event_kind({"event_type": HostileObject()}, source="invoice")

    def test_grant_rejects_hostile_type_value_without_hooks(self):
        with self.assertRaisesRegex(ValueError, "plain text"):
            claim_kind({"claim_type": HostileObject()})

    def test_procurement_rejects_str_subclass_without_hooks(self):
        with self.assertRaisesRegex(ValueError, "plain text"):
            event_kind({"event_type": HostileText("credit")}, source="invoice")

    def test_grant_rejects_str_subclass_without_hooks(self):
        with self.assertRaisesRegex(ValueError, "plain text"):
            claim_kind({"claim_type": HostileText("credit")})

    def test_procurement_rejects_numeric_and_boolean_types(self):
        for raw in (0, 1, False, True, Decimal("1.0"), [], {}):
            with self.subTest(type=type(raw).__name__):
                with self.assertRaisesRegex(ValueError, "plain text"):
                    event_kind({"event_type": raw}, source="receipt")

    def test_grant_rejects_numeric_and_boolean_types(self):
        for raw in (0, 1, False, True, Decimal("1.0"), [], {}):
            with self.subTest(type=type(raw).__name__):
                with self.assertRaisesRegex(ValueError, "plain text"):
                    claim_kind({"claim_type": raw})

    def test_both_preserve_missing_blank_none_legacy_defaults(self):
        for raw in (None, ""):
            self.assertEqual(event_kind({"event_type": raw}, source="invoice"), "invoice")
            self.assertEqual(event_kind({"event_type": raw}, source="receipt"), "receipt")
            self.assertEqual(claim_kind({"claim_type": raw}), "claim")
        self.assertEqual(event_kind({}, source="invoice"), "invoice")
        self.assertEqual(claim_kind({}), "claim")

    def test_both_preserve_casefold_and_whitespace(self):
        self.assertEqual(event_kind({"event_type": " CrEdIt\t"}, source="invoice"), "credit")
        self.assertEqual(event_kind({"event_type": "\tReTuRn "}, source="receipt"), "return")
        self.assertEqual(claim_kind({"claim_type": "  CrEdIt\t"}), "credit")

    def test_whitespace_only_remains_invalid(self):
        for family, call in (
            ("ProcureGuard", lambda: event_kind({"event_type": " \t", "row": "2"}, source="invoice")),
            ("GrantAudit", lambda: claim_kind({"claim_type": " \t", "row": "2"})),
        ):
            with self.subTest(family=family):
                with self.assertRaises(ValueError):
                    call()

    def test_source_stream_failure_precedes_untrusted_mapping_access(self):
        with self.assertRaisesRegex(ValueError, "Unsupported procurement event stream"):
            event_kind(UserDict(event_type="invoice"), source="unknown")

    def test_procurement_untrusted_citation_is_sanitized(self):
        for bad in ("0", "1", "02", "٢", "2\nsecret", HostileText("42")):
            with self.subTest(type=type(bad).__name__):
                with self.assertRaises(ValueError) as caught:
                    event_kind({"event_type": "secret private vendor", "row": bad}, source="invoice")
                self.assertEqual(str(caught.exception),
                                 "Unsupported invoice event_type at input physical row ?")

    def test_grant_untrusted_citation_is_sanitized(self):
        for bad in ("0", "1", "02", "٢", "2\nsecret", HostileText("42")):
            with self.subTest(type=type(bad).__name__):
                with self.assertRaises(ValueError) as caught:
                    claim_kind({"claim_type": "secret private beneficiary", "row": bad})
                self.assertEqual(str(caught.exception),
                                 "Unsupported claim_type at claim CSV physical row ?; use claim or credit")

    def test_canonical_physical_citation_still_visible(self):
        with self.assertRaisesRegex(ValueError, "physical row 42"):
            event_kind({"event_type": "unknown", "row": "42"}, source="receipt")
        with self.assertRaisesRegex(ValueError, "physical row 42"):
            claim_kind({"claim_type": "unknown", "row": "42"})

    def test_actual_procurement_credit_affects_review_totals(self):
        from fvs_suite.procurement import PricePolicy, review_line
        def item(qty, *, event="", doc=""):
            return {"quantity": qty, "unit_price": "10", "event_type": event,
                    "document_id": doc, "row": "2"}
        original = item("2", doc="INV1")
        reversal = ForgedGet(item("1", event="credit", doc="CM1"),
                             related_document="INV1")
        report, flags = review_line(
            [item("2")], [original, reversal], [item("2", doc="REC1")],
            quantity=lambda raw: Decimal(raw), unit_cost=lambda raw: Decimal(raw),
            identifier=lambda raw: str(raw).upper(), policy=PricePolicy())
        self.assertEqual(report["gross_invoice_total_exact"], "20")
        self.assertEqual(report["credit_value_exact"], "10")
        self.assertEqual(report["invoice_total_exact"], "10")
        self.assertIn("credit_memo_review", flags)

    def test_actual_grant_credit_stored_in_linked_allocation(self):
        from fvs_suite import engine
        from fvs_suite.grant_allocations import _parse_claims
        row = ForgedGet(id="CR1", program="G1", ledger_reference="T1",
                        amount="10", claim_type="credit", related_claim="C1", row="2")
        by_ref, _, _ = _parse_claims([row], engine)
        self.assertEqual(by_ref["T1"][0]["_kind"], "credit")
        self.assertEqual(by_ref["T1"][0]["_amount"], Decimal("10"))

    def test_private_unknown_event_values_never_escape(self):
        for call in (
            lambda: event_kind({"event_type": "ACME salary secret", "row": "3"}, source="invoice"),
            lambda: claim_kind({"claim_type": "ACME salary secret", "row": "3"}),
        ):
            with self.assertRaises(ValueError) as caught:
                call()
            self.assertNotIn("ACME", str(caught.exception))
            self.assertNotIn("salary", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
