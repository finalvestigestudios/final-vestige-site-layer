"""R167: Invoice Twin snapshot must read actual dict storage, not overridden mapping views.

Synthetic in-memory rows only. These subclasses expose one value through mapping
protocol hooks and a different value in their underlying dict storage.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import unittest

from fvs_suite.invoice_match import candidate_pairs, review_flags


def source(**changes):
    row = {"row": "2", "v": "ACME", "inv": "INV1",
           "amt": Decimal("12.00"), "dt": date(2026, 1, 1),
           "vendor": "Acme", "invoice_number": "INV1"}
    row.update(changes)
    return row


class ForgedMappingViews(dict):
    """Dict subclass whose keys/getitem/items/iter/get lie about stored data."""

    def __init__(self, stored, advertised=None):
        super().__init__(stored)
        self.advertised = source() if advertised is None else dict(advertised)
        self.hook_calls = []

    def keys(self):
        self.hook_calls.append("keys")
        return self.advertised.keys()

    def __iter__(self):
        self.hook_calls.append("iter")
        return iter(self.advertised)

    def __getitem__(self, key):
        self.hook_calls.append("getitem")
        return self.advertised[key]

    def get(self, key, default=None):
        self.hook_calls.append("get")
        return self.advertised.get(key, default)

    def items(self):
        self.hook_calls.append("items")
        return self.advertised.items()


class ForbiddenMappingHooks(dict):
    """None of these subclass methods should execute during snapshotting."""

    def keys(self):
        raise AssertionError("untrusted keys() was called")

    def __iter__(self):
        raise AssertionError("untrusted __iter__ was called")

    def __getitem__(self, key):
        raise AssertionError("untrusted __getitem__ was called")

    def get(self, key, default=None):
        raise AssertionError("untrusted get() was called")

    def items(self):
        raise AssertionError("untrusted items() was called")


class InvoiceStoredItemsCustodyR167(unittest.TestCase):
    def reject_stored(self, message, **bad):
        held = source(**bad)
        forged = ForgedMappingViews(held)
        with self.assertRaisesRegex(ValueError, message):
            candidate_pairs([forged])
        self.assertEqual(forged.hook_calls, [])

    def test_reject_stored_invalid_row(self):
        self.reject_stored("canonical physical CSV row", row="SECRET ROW")

    def test_reject_stored_header_row(self):
        self.reject_stored("canonical physical CSV row", row="1")

    def test_reject_stored_unicode_row(self):
        self.reject_stored("canonical physical CSV row", row="２")

    def test_reject_stored_row_with_leading_zero(self):
        self.reject_stored("canonical physical CSV row", row="02")

    def test_reject_stored_duplicate_rows(self):
        second = ForgedMappingViews(source(row="2", inv="INV2"),
                                    source(row="3", inv="INV2"))
        with self.assertRaisesRegex(ValueError, "Duplicate invoice physical CSV row"):
            candidate_pairs([source(), second])
        self.assertEqual(second.hook_calls, [])

    def test_reject_stored_date_string(self):
        self.reject_stored("parsed calendar date", dt="2026-01-01")

    def test_reject_stored_datetime(self):
        self.reject_stored("parsed calendar date", dt=datetime(2026, 1, 1))

    def test_reject_stored_float_money(self):
        self.reject_stored("finite exact Decimal", amt=12.0)

    def test_reject_stored_nan_money(self):
        self.reject_stored("finite exact Decimal", amt=Decimal("NaN"))

    def test_reject_stored_over_limit_money(self):
        self.reject_stored("permitted range", amt=Decimal("1000000000001"))

    def test_reject_stored_scale_overflow(self):
        self.reject_stored("permitted precision", amt=Decimal("0.123456789"))

    def test_reject_stored_vendor_lowercase(self):
        self.reject_stored("normalized ASCII", v="acme")

    def test_reject_stored_vendor_unicode(self):
        self.reject_stored("normalized ASCII", v="ACMÉ")

    def test_reject_stored_invoice_empty(self):
        self.reject_stored("normalized ASCII", inv="")

    def test_reject_stored_missing_key(self):
        held = source()
        del held["v"]
        forged = ForgedMappingViews(held)
        with self.assertRaisesRegex(ValueError, "normalized ASCII"):
            candidate_pairs([forged])
        self.assertEqual(forged.hook_calls, [])

    def test_valid_stored_data_ignores_bad_forged_views(self):
        forged = ForgedMappingViews(source(), source(row="bad", v="bad", amt="bad"))
        self.assertEqual(candidate_pairs([forged]), [])
        self.assertEqual(forged.hook_calls, [])

    def test_stored_exact_group_anchor(self):
        earlier = ForgedMappingViews(source(), source(row="99", inv="DIFFERENT"))
        later = ForgedMappingViews(source(row="3"), source(row="98", inv="ANOTHER"))
        matches = candidate_pairs([later, earlier])
        self.assertEqual([(a["row"], b["row"], status) for a, b, status, _ in matches],
                         [("2", "3", "exact_invoice_key")])
        self.assertEqual(earlier.hook_calls + later.hook_calls, [])

    def test_stored_near_match_not_forged_exact(self):
        earlier = source()
        later = ForgedMappingViews(source(row="3", inv="INV2"),
                                   source(row="3", inv="INV1"))
        matches = candidate_pairs([earlier, later])
        self.assertEqual([match[2] for match in matches],
                         ["review_possible_duplicate"])
        self.assertEqual(later.hook_calls, [])

    def test_stored_amount_groups_not_forged(self):
        later = ForgedMappingViews(source(row="3", inv="INV2", amt=Decimal("13.00")),
                                   source(row="3", inv="INV2"))
        self.assertEqual(candidate_pairs([source(), later]), [])
        self.assertEqual(later.hook_calls, [])

    def test_forged_row_order_cannot_swap_anchor(self):
        earlier = ForgedMappingViews(source(row="2"), source(row="900"))
        later = ForgedMappingViews(source(row="3"), source(row="3"))
        matches = candidate_pairs([later, earlier])
        self.assertEqual([(a["row"], b["row"]) for a, b, _, _ in matches],
                         [("2", "3")])

    def test_stored_amount_sign_review(self):
        earlier = source()
        later = ForgedMappingViews(source(row="3", amt=Decimal("-12.00")),
                                   source(row="3", amt=Decimal("12.00")))
        matches = candidate_pairs([earlier, later])
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0][2], "exact_invoice_key")
        self.assertIn("opposing_signed_amounts_review",
                      review_flags(*matches[0][:3]))

    def test_snapshot_owned_after_source_changed(self):
        held = ForgedMappingViews(source())
        matches = candidate_pairs([held, source(row="3")])
        held["row"] = "999"
        held["amt"] = Decimal("0")
        self.assertEqual(matches[0][0]["row"], "2")
        self.assertEqual(matches[0][0]["amt"], Decimal("12.00"))
        self.assertIsNot(matches[0][0], held)

    def test_failure_has_no_private_values(self):
        private = "CUSTOMER-PRIVATE-IDENTIFIER-00013"
        held = ForgedMappingViews(source(v=private))
        with self.assertRaises(ValueError) as caught:
            candidate_pairs([held])
        self.assertNotIn(private, str(caught.exception))
        self.assertEqual(held.hook_calls, [])

    def test_validate_before_generating_candidates(self):
        def rows():
            yield source()
            yield source(row="3", inv="INV2")
            yield ForgedMappingViews(source(row="wrong", inv="INV3"),
                                     source(row="4", inv="INV3"))
        with self.assertRaisesRegex(ValueError, "canonical physical CSV row"):
            candidate_pairs(rows())

    def test_plain_dict_still_works(self):
        matches = candidate_pairs([source(), source(row="3")])
        self.assertEqual([(a["row"], b["row"], status) for a, b, status, _ in matches],
                         [("2", "3", "exact_invoice_key")])

    def test_no_original_view_method_called(self):
        row = ForbiddenMappingHooks(source())
        self.assertEqual(candidate_pairs([row]), [])


if __name__ == "__main__":
    unittest.main()
