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
            review_flags(row(), row(3, invoice="different", amount=Decimal("12")),
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


# R526: public direct review must authenticate its candidate status against the
# same normalized evidence predicates used by candidate_pairs. Pure synthetic
# records; no customer data or external services are used.
class InvoiceReviewCandidatePolicyR526(unittest.TestCase):
    def refuse(self, left, right, status="exact_invoice_key", window_days=7):
        with self.assertRaises(ValueError) as caught:
            review_flags(left, right, status, window_days=window_days)
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)
        self.assertNotIn(PRIVATE, str(caught.exception))
        return str(caught.exception)

    def test_exact_same_normalized_identity_allows_amount_date_variance(self):
        self.assertEqual(
            review_flags(row(), row(3, amount=Decimal("13"), day=30),
                         "exact_invoice_key"),
            "amount_variance_review;distant_dates_review")

    def test_exact_rejects_different_normalized_vendor(self):
        other = row(3)
        other["v"] = "OTHER"
        self.assertIn("vendor key", self.refuse(row(), other))

    def test_exact_rejects_different_normalized_invoice(self):
        self.assertIn("invoice key", self.refuse(
            row(), row(3, invoice="OTHER")))

    def test_near_accepts_exact_seven_day_limit(self):
        self.assertEqual(
            review_flags(row(), row(3, invoice="OTHER", day=7),
                         "review_possible_duplicate"), "")

    def test_near_requires_distinct_normalized_invoice(self):
        self.assertIn("near candidate", self.refuse(
            row(), row(3), "review_possible_duplicate"))

    def test_near_requires_same_normalized_vendor(self):
        other = row(3, invoice="OTHER")
        other["v"] = "OTHER"
        self.assertIn("vendor key", self.refuse(
            row(), other, "review_possible_duplicate"))

    def test_near_requires_same_exact_amount(self):
        self.assertIn("near candidate", self.refuse(
            row(), row(3, invoice="OTHER", amount=Decimal("12.01")),
            "review_possible_duplicate"))

    def test_near_rejects_eight_day_gap(self):
        self.assertIn("near candidate", self.refuse(
            row(), row(3, invoice="OTHER", day=8),
            "review_possible_duplicate"))

    def test_near_window_zero_accepts_same_day(self):
        self.assertEqual(
            review_flags(row(), row(3, invoice="OTHER"),
                         "review_possible_duplicate", window_days=0), "")

    def test_near_window_zero_rejects_next_day(self):
        self.refuse(
            row(), row(3, invoice="OTHER", day=1),
            "review_possible_duplicate", window_days=0)

    def test_near_reverse_chronological_order_is_valid(self):
        self.assertEqual(
            review_flags(row(3, invoice="OTHER", day=7), row(),
                         "review_possible_duplicate"), "")

    def test_near_rejects_opposing_charge_and_credit(self):
        self.refuse(
            row(), row(3, invoice="OTHER", amount=Decimal("-12")),
            "review_possible_duplicate")

    def test_near_equal_decimal_value_different_scale_is_valid(self):
        self.assertEqual(
            review_flags(row(), row(3, invoice="OTHER",
                                    amount=Decimal("12.000")),
                         "review_possible_duplicate"), "")

    def test_policy_guard_does_not_mutate_source_rows(self):
        a, b = row(), row(3, invoice="OTHER", day=7)
        original = deepcopy((a, b))
        self.assertEqual(review_flags(a, b, "review_possible_duplicate"), "")
        self.assertEqual((a, b), original)


# R527: no supposedly clean direct invoice review from contradictory source
# labels/normalized keys; bounded raw label processing. Synthetic only.
class InvoiceCleanReviewIdentityR527(unittest.TestCase):
    def refuse(self, left, right, status="exact_invoice_key"):
        with self.assertRaises(ValueError) as caught:
            review_flags(left, right, status)
        error = caught.exception
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertNotIn(PRIVATE, str(error))
        self.assertNotIn(PRIVATE, "".join(traceback.format_exception(error)))
        return str(error)

    def test_valid_exact_pair_remains_clean(self):
        self.assertEqual(review_flags(row(), row(3), "exact_invoice_key"), "")

    def test_valid_near_pair_remains_clean(self):
        self.assertEqual(review_flags(row(), row(3, invoice="OTHER"),
                                      "review_possible_duplicate"), "")

    def test_both_raw_vendor_labels_contradict_matching_keys(self):
        a, b = row(), row(3)
        a["v"] = b["v"] = "OTHER"
        self.assertIn("contradict", self.refuse(a, b))

    def test_both_raw_invoice_labels_contradict_matching_keys(self):
        a, b = row(), row(3)
        a["inv"] = b["inv"] = "OTHER"
        self.assertIn("contradict", self.refuse(a, b))

    def test_one_side_raw_vendor_label_contradicts_accepted_key(self):
        a, b = row(), row(3)
        b["vendor"] = "NotAcme"
        # Preserve the collision review and explicitly flag source/key conflict.
        self.assertEqual(review_flags(a, b, "exact_invoice_key"),
                         "normalized_vendor_key_review;source_identity_key_mismatch_review")
        b["vendor"] = a["vendor"]
        b["v"] = a["v"] = "SPOOF"
        self.refuse(a, b)

    def test_near_status_rejects_forged_different_keys_for_same_raw_invoice(self):
        a, b = row(), row(3)
        b["inv"] = "NOTINVOICE"
        self.assertIn("contradict", self.refuse(
            a, b, "review_possible_duplicate"))

    def test_near_status_rejects_forged_matching_vendor_key(self):
        a, b = row(), row(3, invoice="DIFFERENT")
        a["v"] = b["v"] = "FAKE"
        self.refuse(a, b, "review_possible_duplicate")

    def test_raw_punctuation_normalization_remains_valid(self):
        a, b = row(invoice="INV---A"), row(3, invoice="INV A")
        self.assertEqual(review_flags(a, b, "exact_invoice_key"),
                         "normalized_invoice_key_review")

    def test_unicode_uppercase_expansion_preserves_clean_evidence(self):
        a, b = row(invoice="Straße"), row(3, invoice="STRASSE")
        self.assertEqual(review_flags(a, b, "exact_invoice_key"),
                         "normalized_invoice_key_review")

    def test_ascii_case_variants_remain_clean(self):
        self.assertEqual(review_flags(row(invoice="Invoice"),
                                      row(3, invoice="iNVOICE"),
                                      "exact_invoice_key"), "")

    def test_empty_raw_vendor_cannot_support_clean_matching_key(self):
        a, b = row(), row(3)
        a["vendor"] = b["vendor"] = ""
        self.refuse(a, b)

    def test_empty_raw_invoice_cannot_support_clean_matching_key(self):
        a, b = row(), row(3)
        a["invoice_number"] = b["invoice_number"] = ""
        self.refuse(a, b)

    def test_vendor_label_limit_applies_even_if_collision_would_be_flagged(self):
        from unittest.mock import patch
        a, b = row(), row(3, vendor="ABCDEFGHI")
        with patch("fvs_suite.invoice_match.MAX_SOURCE_IDENTITY_CHARS", 8):
            self.assertIn("length limit", self.refuse(a, b))

    def test_invoice_label_limit_applies_to_near_review(self):
        from unittest.mock import patch
        a, b = row(), row(3, invoice="LONGINVOICE123")
        with patch("fvs_suite.invoice_match.MAX_SOURCE_IDENTITY_CHARS", 8):
            self.assertIn("length limit", self.refuse(
                a, b, "review_possible_duplicate"))

    def test_at_test_ceiling_valid_labels_still_work(self):
        from unittest.mock import patch
        a, b = row(invoice="INV-1234"), row(3, invoice="INV-1234")
        with patch("fvs_suite.invoice_match.MAX_SOURCE_IDENTITY_CHARS", 8):
            self.assertEqual(review_flags(a, b, "exact_invoice_key"), "")

    def test_private_raw_label_not_exposed_by_error_or_traceback(self):
        a, b = row(), row(3)
        a["invoice_number"] = b["invoice_number"] = PRIVATE
        self.refuse(a, b)

    def test_rejected_and_accepted_source_mappings_remain_unmodified(self):
        a, b = row(), row(3)
        before = deepcopy((a, b))
        self.assertEqual(review_flags(a, b, "exact_invoice_key"), "")
        self.assertEqual((a, b), before)
        a["v"] = b["v"] = "FAKE"
        before = deepcopy((a, b))
        self.refuse(a, b)
        self.assertEqual((a, b), before)



# R528: direct review source/key contradictions must remain visible even
# when another independent ambiguity already produces a human-review flag.
# Standalone synthetic evidence only; no files, network or premium artifacts.
class InvoiceFlaggedSourceIdentityR528(unittest.TestCase):
    MISMATCH = "source_identity_key_mismatch_review"

    def test_forged_left_vendor_stays_visible_after_collision(self):
        a = row()
        a["vendor"] = "OtherVendor"
        self.assertEqual(
            review_flags(a, row(3), "exact_invoice_key"),
            "normalized_vendor_key_review;" + self.MISMATCH)

    def test_forged_right_vendor_stays_visible_after_collision(self):
        b = row(3)
        b["vendor"] = "OtherVendor"
        self.assertEqual(
            review_flags(row(), b, "exact_invoice_key"),
            "normalized_vendor_key_review;" + self.MISMATCH)

    def test_forged_left_invoice_stays_visible_after_collision(self):
        a = row()
        a["invoice_number"] = "OTHER"
        self.assertEqual(
            review_flags(a, row(3), "exact_invoice_key"),
            "normalized_invoice_key_review;" + self.MISMATCH)

    def test_forged_right_invoice_stays_visible_after_collision(self):
        b = row(3)
        b["invoice_number"] = "OTHER"
        self.assertEqual(
            review_flags(row(), b, "exact_invoice_key"),
            "normalized_invoice_key_review;" + self.MISMATCH)

    def test_four_contradictions_make_only_one_explicit_mismatch_flag(self):
        a, b = row(), row(3)
        a["vendor"] = b["vendor"] = "WrongVendor"
        a["invoice_number"] = "OTHER"
        b["invoice_number"] = "DIFFERENT"
        flags = review_flags(a, b, "exact_invoice_key").split(";")
        self.assertIn(self.MISMATCH, flags)
        self.assertEqual(flags.count(self.MISMATCH), 1)
        self.assertEqual(flags[-1], self.MISMATCH)

    def test_variance_and_date_flags_are_retained(self):
        b = row(3, vendor="OtherVendor", amount=Decimal("14.00"), day=12)
        self.assertEqual(
            review_flags(row(), b, "exact_invoice_key"),
            "normalized_vendor_key_review;amount_variance_review;"
            "distant_dates_review;" + self.MISMATCH)

    def test_sign_review_is_retained_with_source_mismatch(self):
        b = row(3, invoice="OTHER", amount=Decimal("-12.00"))
        # Exact invoice number identity is also required for this status.
        b["inv"] = "INVA"
        self.assertEqual(
            review_flags(row(), b, "exact_invoice_key"),
            "normalized_invoice_key_review;amount_variance_review;"
            "opposing_signed_amounts_review;" + self.MISMATCH)

    def test_near_vendor_collision_and_forged_invoice_label(self):
        b = row(3, vendor="Acme ", invoice="OTHER")
        b["invoice_number"] = "FORGED"
        self.assertEqual(
            review_flags(row(), b, "review_possible_duplicate"),
            "normalized_vendor_key_review;" + self.MISMATCH)

    def test_near_genuine_pair_remains_clean(self):
        self.assertEqual(
            review_flags(row(), row(3, invoice="OTHER"),
                         "review_possible_duplicate"), "")

    def test_clean_vendor_key_spoof_still_fails_closed(self):
        a, b = row(), row(3)
        a["v"] = b["v"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "contradict") as caught:
            review_flags(a, b, "exact_invoice_key")
        self.assertIsNone(caught.exception.__context__)

    def test_clean_invoice_key_spoof_still_fails_closed(self):
        a, b = row(), row(3)
        a["inv"] = b["inv"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "contradict") as caught:
            review_flags(a, b, "exact_invoice_key")
        self.assertIsNone(caught.exception.__context__)

    def test_valid_raw_vendor_punctuation_only_remains_review(self):
        self.assertEqual(
            review_flags(row(), row(3, vendor="Acme-"), "exact_invoice_key"),
            "normalized_vendor_key_review")

    def test_valid_raw_invoice_punctuation_only_remains_review(self):
        self.assertEqual(
            review_flags(row(invoice="INV-A"), row(3, invoice="INV A"),
                         "exact_invoice_key"), "normalized_invoice_key_review")

    def test_unicode_uppercase_expansion_remains_a_normal_collision(self):
        self.assertEqual(
            review_flags(row(invoice="Straße"), row(3, invoice="STRASSE"),
                         "exact_invoice_key"), "normalized_invoice_key_review")

    def test_private_forged_label_is_not_written_to_review_flags(self):
        b = row(3)
        b["vendor"] = PRIVATE
        flags = review_flags(row(), b, "exact_invoice_key")
        self.assertEqual(
            flags, "normalized_vendor_key_review;" + self.MISMATCH)
        self.assertNotIn(PRIVATE, flags)

    def test_source_dicts_not_mutated_even_for_forged_flagged_pair(self):
        a, b = row(), row(3, vendor="OtherVendor")
        before = deepcopy((a, b))
        self.assertIn(self.MISMATCH, review_flags(a, b, "exact_invoice_key"))
        self.assertEqual((a, b), before)


if __name__ == "__main__":
    unittest.main()
