"""R444 Invoice Twin direct review-flag custody, pure synthetic financial evidence."""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timedelta
from decimal import Context, Decimal, Inexact, Rounded, localcontext
import traceback
import unittest

from fvs_suite.invoice_match import candidate_pairs, review_flags

PRIVATE = "PRIVATE_CLIENT_8831_DO_NOT_ECHO"


def row(n=2, *, vendor="Acme", invoice="INV-A",
        amount=Decimal("12.00"), day=0):
    return {"row": str(n), "v": "ACME", "inv": invoice.replace("-", "").replace(" ", "").upper(),
            "vendor": vendor, "invoice_number": invoice,
            "amt": amount, "dt": date(2026, 1, 1) + timedelta(days=day)}


class InvoiceReviewCustodyR444(unittest.TestCase):
    def assert_private_refusal(self, a, b=None, status="exact_invoice_key", **kwargs):
        with self.assertRaises(ValueError) as caught:
            review_flags(a, row(3) if b is None else b, status, **kwargs)
        error = caught.exception
        self.assertNotIn(PRIVATE, str(error))
        self.assertNotIn(PRIVATE, repr(error))
        self.assertNotIn(PRIVATE, "".join(traceback.format_exception(error)))
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)

    def test_exact_clean_pair_has_no_flags(self):
        self.assertEqual(review_flags(row(), row(3), "exact_invoice_key"), "")

    def test_identical_normalized_vendor_different_raw_identity_requests_review(self):
        self.assertEqual(
            review_flags(row(), row(3, vendor="Acme "), "exact_invoice_key"),
            "normalized_vendor_key_review")

    def test_invoice_identity_ascii_case_is_not_false_variance(self):
        self.assertEqual(
            review_flags(row(invoice="Invoice"), row(3, invoice="iNVOICE"),
                         "exact_invoice_key"), "")

    def test_invoice_identity_noncase_difference_requests_review(self):
        self.assertEqual(
            review_flags(row(invoice="INV-A"), row(3, invoice="INV A"),
                         "exact_invoice_key"), "normalized_invoice_key_review")

    def test_near_candidate_does_not_invent_exact_invoice_flags(self):
        self.assertEqual(
            review_flags(row(), row(3, invoice="different", amount=Decimal("18")),
                         "review_possible_duplicate"), "")

    def test_exact_variance_and_date_flags_are_independent(self):
        self.assertEqual(
            review_flags(row(), row(3, amount=Decimal("13"), day=8),
                         "exact_invoice_key"),
            "amount_variance_review;distant_dates_review")

    def test_opposite_signed_amounts_require_human_review_not_auto_fraud(self):
        self.assertEqual(
            review_flags(row(amount=Decimal("12")), row(3, amount=Decimal("-12")),
                         "exact_invoice_key"),
            "amount_variance_review;opposing_signed_amounts_review")

    def test_signed_negative_zero_is_not_a_credit(self):
        self.assertEqual(
            review_flags(row(amount=Decimal("0")), row(3, amount=Decimal("-0")),
                         "exact_invoice_key"), "")

    def test_window_boundary_is_inclusive_at_seven_days(self):
        self.assertEqual(
            review_flags(row(), row(3, day=7), "exact_invoice_key"), "")
        self.assertEqual(
            review_flags(row(), row(3, day=8), "exact_invoice_key"),
            "distant_dates_review")

    def test_dictionary_subclass_lookup_spoofing_never_runs(self):
        class Hostile(dict):
            def __getitem__(self, key):
                raise RuntimeError(PRIVATE)
            def get(self, key, default=None):
                raise RuntimeError(PRIVATE)
            def items(self):
                raise RuntimeError(PRIVATE)
            def keys(self):
                raise RuntimeError(PRIVATE)
        source = Hostile(row())
        expected = review_flags(row(), row(3, vendor="Different"), "exact_invoice_key")
        self.assertEqual(
            review_flags(source, row(3, vendor="Different"), "exact_invoice_key"),
            expected)

    def test_status_subclass_cannot_run_custom_equality(self):
        class HostileStatus(str):
            def __eq__(self, other):
                raise RuntimeError(PRIVATE)
        self.assert_private_refusal(row(), status=HostileStatus("exact_invoice_key"))

    def test_unknown_status_never_produces_misleading_empty_flag(self):
        for bad in (PRIVATE, "", "other_review", None, 1, False):
            with self.subTest(kind=type(bad).__name__):
                self.assert_private_refusal(row(), status=bad)

    def test_untrusted_window_policy_rejected_like_candidate_window(self):
        for bad in (True, False, 1.5, "7", None, -1, 366):
            with self.subTest(value=repr(bad)):
                self.assert_private_refusal(row(), window_days=bad)

    def test_review_source_must_be_real_dictionary(self):
        for bad in (None, False, {}, [], "source", object()):
            with self.subTest(kind=type(bad).__name__):
                self.assert_private_refusal(bad)

    def test_string_subclass_and_missing_raw_labels_are_rejected(self):
        class HostileText(str):
            def __str__(self):
                raise RuntimeError(PRIVATE)
        for field in ("vendor", "invoice_number"):
            for value in (None, False, HostileText(PRIVATE)):
                source = row()
                source[field] = value
                with self.subTest(field=field, kind=type(value).__name__):
                    self.assert_private_refusal(source)

    def test_non_native_mapping_keys_are_rejected(self):
        class Alias(str):
            pass
        source = row()
        source[Alias("unexpected")] = "private"
        self.assert_private_refusal(source)

    def test_only_finite_bounded_exact_decimal_money_is_accepted(self):
        class HostileMoney(Decimal):
            def __eq__(self, other):
                raise RuntimeError(PRIVATE)
        bads = (12.0, True, Decimal("NaN"), Decimal("Infinity"),
                HostileMoney("12.00"), Decimal("1000000000001"),
                Decimal("0.000000001"))
        for bad in bads:
            source = row(amount=bad)
            with self.subTest(kind=repr(type(bad))):
                self.assert_private_refusal(source)

    def test_datetime_subclasses_and_private_text_dates_rejected(self):
        for bad in (datetime(2026, 1, 1), "2026-01-01", PRIVATE, None):
            source = row()
            source["dt"] = bad
            with self.subTest(kind=type(bad).__name__):
                self.assert_private_refusal(source)

    def test_original_source_rows_are_not_edited(self):
        a, b = row(), row(3, vendor="Acmé", amount=Decimal("12.01"))
        original = deepcopy((a, b))
        self.assertIn("review", review_flags(a, b, "exact_invoice_key"))
        self.assertEqual((a, b), original)

    def test_real_candidate_evidence_integrates_with_review_flags(self):
        records = [row(4, invoice="NEW", amount=Decimal("12.00")),
                   row(3, invoice="INV-A", amount=Decimal("12.00")),
                   row(2, invoice="INV-A", amount=Decimal("12.00"))]
        candidates = candidate_pairs((record for record in records))
        self.assertEqual(
            [(a["row"], b["row"], status) for a, b, status, _ in candidates],
            [("2", "3", "exact_invoice_key"),
             ("2", "4", "review_possible_duplicate"),
             ("3", "4", "review_possible_duplicate")])
        self.assertTrue(all(review_flags(a, b, status) == ""
                            for a, b, status, _ in candidates))

    def test_hostile_decimal_context_does_not_change_exact_review(self):
        a = row(amount=Decimal("0.005"))
        b = row(3, amount=Decimal("-0.005"))
        expected = ("amount_variance_review;opposing_signed_amounts_review")
        with localcontext(Context(prec=2, Emin=-4, Emax=4)) as context:
            context.traps[Inexact] = True
            context.traps[Rounded] = True
            self.assertEqual(review_flags(a, b, "exact_invoice_key"), expected)



# R525: public review_flags direct callers must retain source-row and
# normalized-key custody, not just amounts, raw labels and calendar dates.
# Synthetic records only. This remains an already-inventoried unittest module.
class InvoiceReviewRowCustodyR525(unittest.TestCase):
    def refuse(self, left, right=None, status="exact_invoice_key"):
        if right is None:
            right = row(3)
        with self.assertRaises(ValueError) as caught:
            review_flags(left, right, status)
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(PRIVATE, str(caught.exception))
        return str(caught.exception)

    def test_same_physical_row_cannot_review_itself_exact(self):
        self.assertIn("distinct", self.refuse(row(2), row(2)))

    def test_same_physical_row_cannot_review_itself_near(self):
        self.assertIn("distinct", self.refuse(
            row(2), row(2, invoice="DIFFERENT"), "review_possible_duplicate"))

    def test_missing_source_line_fails_closed(self):
        left = row()
        del left["row"]
        self.assertIn("physical CSV row", self.refuse(left))

    def test_header_or_zero_line_not_financial_evidence(self):
        for bad in ("0", "1"):
            with self.subTest(bad=bad):
                left = row()
                left["row"] = bad
                self.assertIn("physical CSV row", self.refuse(left))

    def test_noncanonical_or_overlong_source_rows_refused(self):
        for bad in ("02", "+2", "２", "2.0", "2 ", "2\\n" + PRIVATE,
                    "9" * 5000, ""):
            with self.subTest(length=len(bad)):
                left = row()
                left["row"] = bad
                self.assertIn("physical CSV row", self.refuse(left))

    def test_source_line_must_be_native_string(self):
        class Forge(str):
            def __eq__(self, other):
                raise RuntimeError(PRIVATE)
        for bad in (2, 2.0, True, None, Forge("2")):
            with self.subTest(kind=type(bad).__name__):
                left = row()
                left["row"] = bad
                self.refuse(left)

    def test_missing_normalized_vendor_or_invoice_refused(self):
        for field in ("v", "inv"):
            left = row()
            del left[field]
            self.assertIn("normalized ASCII", self.refuse(left))

    def test_noncanonical_normalized_keys_refused(self):
        for field in ("v", "inv"):
            for bad in ("", "lowercase", "A-B", " A", "ＡＢ", PRIVATE):
                with self.subTest(field=field, kind=bad[:8]):
                    left = row()
                    left[field] = bad
                    self.assertIn("normalized ASCII", self.refuse(left))

    def test_normalized_key_subclass_callbacks_are_never_used(self):
        class Forged(str):
            def __eq__(self, other):
                raise RuntimeError(PRIVATE)
            def __str__(self):
                raise RuntimeError(PRIVATE)
        for field in ("v", "inv"):
            left = row()
            left[field] = Forged("ACME")
            self.assertIn("normalized ASCII", self.refuse(left))

    def test_right_hand_evidence_is_validated_independently(self):
        right = row(3)
        right["inv"] = "PRIVATÉ-INVALID"
        self.assertIn("normalized ASCII", self.refuse(row(), right))

    def test_hostile_dict_getters_not_consulted(self):
        class Hostile(dict):
            def get(self, *args):
                raise RuntimeError(PRIVATE)
            def items(self):
                raise RuntimeError(PRIVATE)
            def keys(self):
                raise RuntimeError(PRIVATE)
        self.assertEqual(
            review_flags(Hostile(row()), Hostile(row(3, vendor="Acme ")),
                         "exact_invoice_key"),
            "normalized_vendor_key_review")

    def test_existing_valid_exact_and_near_candidate_behavior(self):
        a, b = row(2), row(3)
        self.assertEqual(review_flags(a, b, "exact_invoice_key"), "")
        self.assertEqual(review_flags(a, row(3, amount=Decimal("13")),
                                      "exact_invoice_key"), "amount_variance_review")
        near = row(3, invoice="DIFFERENT")
        self.assertEqual(review_flags(a, near, "review_possible_duplicate"), "")

    def test_real_candidate_pair_still_has_source_evidence(self):
        records = (row(4, invoice="NEW"), row(3), row(2))
        for left, right, status, _ in candidate_pairs(iter(records)):
            self.assertNotEqual(left["row"], right["row"])
            self.assertEqual(review_flags(left, right, status), "")

    def test_rejection_does_not_mutate_the_sources(self):
        left, right = row(), row(3)
        right["row"] = left["row"]
        before = deepcopy((left, right))
        self.refuse(left, right)
        self.assertEqual((left, right), before)

    def test_source_private_bad_keys_never_reach_exception_chain(self):
        left = row()
        left["v"] = PRIVATE
        self.refuse(left)

if __name__ == "__main__":
    unittest.main()
