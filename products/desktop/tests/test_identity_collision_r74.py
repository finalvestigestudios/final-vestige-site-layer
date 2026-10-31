"""R74 conservative Unicode identity-review regression suite (synthetic only)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
import unittest

from fvs_suite.review import (
    ascii_case_identity, normalized_collision, reconciliation_status,
    labels_for_report, price_exceeds_tolerance,
)
from fvs_suite.invoice_match import review_flags, candidate_pairs


def invoice(vendor: str, number: str, row: str, *, amount: str = "10.00") -> dict:
    # Source spellings deliberately differ but the lossy engine key is identical.
    return {"vendor": vendor, "invoice_number": number, "v": "SS", "inv": "SS",
            "amt": Decimal(amount), "dt": date(2026, 10, 30), "row": row}


class AsciiSourceIdentityR74(unittest.TestCase):
    def test_ascii_case_variants_share_review_identity(self):
        self.assertEqual(ascii_case_identity("AcMe-INV1"), "acme-inv1")
        self.assertEqual(ascii_case_identity("A-1"), ascii_case_identity("a-1"))

    def test_unicode_long_s_is_not_silently_folded_to_ascii_s(self):
        self.assertNotEqual(ascii_case_identity("ſ1"), ascii_case_identity("S1"))
        self.assertEqual("ſ1".casefold(), "S1".casefold())

    def test_sharp_s_is_not_silently_folded_to_ss(self):
        self.assertNotEqual(ascii_case_identity("Straße"), ascii_case_identity("STRASSE"))
        self.assertEqual("Straße".casefold(), "STRASSE".casefold())

    def test_case_expansion_ligature_is_not_ascii_identity(self):
        self.assertNotEqual(ascii_case_identity("ﬀ"), ascii_case_identity("FF"))
        self.assertEqual("ﬀ".casefold(), "FF".casefold())

    def test_unicode_source_labels_retained(self):
        self.assertEqual(ascii_case_identity("ſßﬀ"), "ſßﬀ")

    def test_invalid_direct_source_identity_never_stringified(self):
        class Sensitive:
            def __str__(self):
                raise AssertionError("must not stringify")
        for value in (None, 0, False, b"TEST", Sensitive()):
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaisesRegex(ValueError, "must be text"):
                    ascii_case_identity(value)

    def test_empty_and_non_ascii_identity_are_deterministic(self):
        self.assertEqual(ascii_case_identity(""), "")
        self.assertEqual(ascii_case_identity("İ-I"), "İ-i")

    def test_ascii_case_only_does_not_trigger_collision(self):
        self.assertFalse(normalized_collision([{"id": "LedgerA"}, {"id": "LEDGERa"}], "id"))

    def test_punctuation_collision_still_flagged(self):
        self.assertTrue(normalized_collision([{"id": "A-1"}, {"id": "A1"}], "id"))

    def test_long_s_collision_is_now_reviewed(self):
        self.assertTrue(normalized_collision([{"id": "ſ1"}, {"id": "S1"}], "id"))

    def test_sharp_s_collision_is_now_reviewed(self):
        self.assertTrue(normalized_collision([{"program": "ß1"}, {"program": "SS1"}], "program"))

    def test_ligature_collision_is_now_reviewed(self):
        self.assertTrue(normalized_collision([{"po_number": "ﬀ1"}, {"po_number": "FF1"}], "po_number"))

    def test_reconciliation_equal_decimals_still_require_unicode_review(self):
        status = reconciliation_status([{"id": "ſ1"}], [{"id": "S1"}],
                                       Decimal("0.30"), Decimal("0.30"),
                                       missing_left="missing_left", missing_right="missing_right")
        self.assertEqual(status, "normalized_id_review")

    def test_review_and_monetary_variance_are_both_preserved(self):
        status = reconciliation_status([{"id": "ſ1"}], [{"id": "S1"}],
                                       Decimal("0.31"), Decimal("0.30"),
                                       missing_left="missing_left", missing_right="missing_right")
        self.assertEqual(status, "normalized_id_review;variance")

    def test_same_exact_identifier_remains_matched(self):
        result = reconciliation_status([{"id": "S1"}], [{"id": "S1"}],
                                       Decimal("10.00"), Decimal("10.00"),
                                       missing_left="left", missing_right="right")
        self.assertEqual(result, "matched")

    def test_original_unicode_labels_remain_auditable(self):
        labels = labels_for_report([{"id": "ß1"}, {"id": "SS1"}], "id")
        self.assertIn("ß1", labels)
        self.assertIn("SS1", labels)

    def test_decimal_price_policy_is_unchanged(self):
        self.assertFalse(price_exceeds_tolerance(Decimal("10.01"), Decimal("10.00")))
        self.assertTrue(price_exceeds_tolerance(Decimal("10.22"), Decimal("10.00")))

    def test_invoice_vendor_unicode_identity_is_flagged(self):
        a, b = invoice("ß", "X", "2"), invoice("SS", "X", "3")
        self.assertEqual(review_flags(a, b, "exact_invoice_key"), "normalized_vendor_key_review")

    def test_invoice_number_unicode_identity_is_flagged(self):
        a, b = invoice("ACME", "ſ1", "2"), invoice("ACME", "S1", "3")
        self.assertEqual(review_flags(a, b, "exact_invoice_key"), "normalized_invoice_key_review")

    def test_invoice_both_identity_flags_survive(self):
        a, b = invoice("ß", "ﬀ", "2"), invoice("SS", "FF", "3")
        self.assertEqual(review_flags(a, b, "exact_invoice_key"),
                         "normalized_vendor_key_review;normalized_invoice_key_review")

    def test_invoice_ascii_only_case_remains_unflagged(self):
        a, b = invoice("AcMe", "Inv1", "2"), invoice("ACME", "INV1", "3")
        self.assertEqual(review_flags(a, b, "exact_invoice_key"), "")

    def test_invoice_near_review_vendor_ambiguity_still_visible(self):
        a, b = invoice("ß", "X", "2"), invoice("SS", "Y", "3")
        self.assertEqual(review_flags(a, b, "review_possible_duplicate"),
                         "normalized_vendor_key_review")

    def test_invoice_existing_variance_flag_unchanged(self):
        a, b = invoice("ACME", "INV1", "2"), invoice("ACME", "INV1", "3", amount="11.00")
        self.assertEqual(review_flags(a, b, "exact_invoice_key"), "amount_variance_review")

    def test_invoice_valid_candidate_selection_remains_deterministic(self):
        a, b = invoice("ß", "ﬀ", "2"), invoice("SS", "FF", "3")
        items = candidate_pairs([a, b])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][2], "exact_invoice_key")
        self.assertEqual((items[0][0]["row"], items[0][1]["row"]), ("2", "3"))
        self.assertEqual(review_flags(*items[0][:3]),
                         "normalized_vendor_key_review;normalized_invoice_key_review")


if __name__ == "__main__":
    unittest.main()
