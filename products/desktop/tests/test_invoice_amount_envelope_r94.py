"""R94: bounded exact-Decimal input for Invoice Twin Scout direct APIs.

Direct candidate discovery is not a substitute for a descriptor-verified CSV
snapshot. All matches are review candidates, never automated payment approval.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Context, Decimal, Inexact, Rounded, localcontext
import random
import unittest

from fvs_suite.invoice_match import candidate_pairs


def row(line=2, *, amount="10.00", invoice="A"):
    return {
        "row": str(line), "v": "ACME", "inv": invoice,
        "dt": date(2026, 1, 1), "amt": Decimal(amount),
        "vendor": "ACME", "invoice_number": invoice,
    }


class InvoiceAmountEnvelopeR94(unittest.TestCase):
    def test_positive_ledger_import_bound_is_accepted(self):
        self.assertEqual(len(candidate_pairs([row(2, amount="1000000000000.00"),
                                              row(3, amount="1000000000000.00", invoice="B")])), 1)

    def test_negative_import_bound_is_accepted(self):
        self.assertEqual(len(candidate_pairs([row(2, amount="-1000000000000.00"),
                                              row(3, amount="-1000000000000.00", invoice="B")])), 1)

    def test_over_maximum_positive_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "permitted range"):
            candidate_pairs([row(amount="1000000000000.01")])

    def test_over_maximum_negative_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "permitted range"):
            candidate_pairs([row(amount="-1000000000000.01")])

    def test_scientific_overflow_exponent_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "permitted range"):
            candidate_pairs([row(amount="1E+999999")])

    def test_scientific_underflow_exponent_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "permitted range"):
            candidate_pairs([row(amount="1E-999999")])

    def test_zero_with_absurd_exponent_is_not_canonical(self):
        with self.assertRaisesRegex(ValueError, "permitted range"):
            candidate_pairs([row(amount="0E-999999")])

    def test_more_than_eight_significant_fractional_places_rejected(self):
        with self.assertRaisesRegex(ValueError, "precision"):
            candidate_pairs([row(amount="0.000000001")])

    def test_more_than_eight_places_negative_rejected(self):
        with self.assertRaisesRegex(ValueError, "precision"):
            candidate_pairs([row(amount="-12.123456789")])

    def test_trailing_zeroes_do_not_add_significant_precision(self):
        self.assertEqual(len(candidate_pairs([row(2, amount="1.123456780000"),
                                              row(3, amount="1.12345678", invoice="B")])), 1)

    def test_exact_half_cent_from_existing_r67_contract_remains_allowed(self):
        self.assertEqual(len(candidate_pairs([row(2, amount="0.005"),
                                              row(3, amount="0.005", invoice="B")])), 1)

    def test_eighth_fractional_place_preserved(self):
        self.assertEqual(len(candidate_pairs([row(2, amount="0.00000001"),
                                              row(3, amount="0.00000001", invoice="B")])), 1)

    def test_excessive_coefficient_even_for_zero_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "permitted range"):
            candidate_pairs([row(amount="0." + "0" * 1000)])

    def test_zero_and_negative_zero_are_equal(self):
        self.assertEqual(len(candidate_pairs([row(2, amount="0"),
                                              row(3, amount="-0.00", invoice="B")])), 1)

    def test_no_partial_candidates_if_late_amount_invalid(self):
        with self.assertRaisesRegex(ValueError, "precision"):
            candidate_pairs([row(2), row(3, invoice="B"),
                             row(4, amount="0.000000001", invoice="C")])

    def test_rejection_does_not_leak_source_amount(self):
        private_amount = "999999999999999999999999999999999999999999999999"
        with self.assertRaises(ValueError) as caught:
            candidate_pairs([row(amount=private_amount)])
        self.assertNotIn(private_amount, str(caught.exception))

    def test_hostile_decimal_context_preserves_bounds_and_match_order(self):
        records = [row(5, amount="1000000000000", invoice="B"),
                   row(2, amount="1000000000000.00", invoice="A")]
        expected = [(a["row"], b["row"], kind) for a, b, kind, _ in candidate_pairs(records)]
        with localcontext(Context(prec=2, Emax=4, Emin=-4)) as ctx:
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            got = [(a["row"], b["row"], kind) for a, b, kind, _ in candidate_pairs(records)]
            self.assertEqual(got, expected)
            with self.assertRaisesRegex(ValueError, "permitted range"):
                candidate_pairs([row(amount="1000000000000.01")])
        self.assertEqual(expected, [("2", "5", "review_possible_duplicate")])

    def test_input_objects_untouched_after_rejection(self):
        records = [row(2), row(3, amount="1E-999999")]
        before = deepcopy(records)
        with self.assertRaises(ValueError):
            candidate_pairs(records)
        self.assertEqual(records, before)

    def test_permutation_stability_for_valid_boundary_values(self):
        records = [row(5, amount="0.005", invoice="C"),
                   row(2, amount="0.005", invoice="A"),
                   row(3, amount="0.005", invoice="B")]
        def keyseq(items):
            return [(a["row"], b["row"], kind) for a, b, kind, _ in candidate_pairs(items)]
        expected = keyseq(records)
        for seed in range(12):
            shuffled = records.copy()
            random.Random(seed).shuffle(shuffled)
            self.assertEqual(keyseq(shuffled), expected)


if __name__ == "__main__":
    unittest.main()
