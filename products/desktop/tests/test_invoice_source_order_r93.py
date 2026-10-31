"""R93 reproducible source-row ordering for direct Invoice Twin candidate APIs.

Source positions, not incoming iterable order, govern candidate orientation and
report sequence. Synthetic records only; this test never approves an invoice.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from decimal import Context, Decimal, Inexact, Rounded, localcontext
import hashlib
import random
import unittest

from fvs_suite.invoice_match import MAX_CANDIDATES, candidate_pairs


def record(row: int, *, inv: str = "A", vendor: str = "ACME", amount: str = "1.00",
           day: int = 0) -> dict:
    return {
        "row": str(row), "v": vendor, "inv": inv, "amt": Decimal(amount),
        "dt": date(2026, 1, 1) + timedelta(days=day),
        "vendor": vendor, "invoice_number": inv,
    }


def refs(records, **kwargs):
    return [(a["row"], b["row"], status) for a, b, status, _ in
            candidate_pairs(records, **kwargs)]


class InvoiceSourceOrderR93(unittest.TestCase):
    def test_exact_anchor_is_earliest_physical_line(self):
        rows = [record(4), record(2), record(3)]
        self.assertEqual(refs(rows), [
            ("2", "3", "exact_invoice_key"),
            ("2", "4", "exact_invoice_key"),
        ])

    def test_multiple_exact_groups_sorted_by_first_physical_line(self):
        rows = [record(9, inv="B", amount="9"), record(10, inv="B", amount="9"),
                record(2, inv="A", amount="2"), record(3, inv="A", amount="2")]
        self.assertEqual(refs(rows), [("2", "3", "exact_invoice_key"),
                                      ("9", "10", "exact_invoice_key")])

    def test_numeric_physical_line_order_not_string_lexical_order(self):
        self.assertEqual(refs([record(10), record(9)]),
                         [("9", "10", "exact_invoice_key")])

    def test_near_groups_sorted_by_first_source_line(self):
        rows = [record(8, inv="D", amount="9"), record(7, inv="C", amount="9"),
                record(3, inv="B", amount="2"), record(2, inv="A", amount="2")]
        self.assertEqual(refs(rows), [("2", "3", "review_possible_duplicate"),
                                      ("7", "8", "review_possible_duplicate")])

    def test_reordered_input_has_identical_full_candidate_stream(self):
        rows = [record(2, inv="Z", amount="10", day=4),
                record(4, inv="Z", amount="12", day=5),
                record(6, inv="B", amount="10", day=1),
                record(8, inv="C", amount="10", day=3),
                record(12, inv="B", amount="10", day=6),
                record(17, inv="M", vendor="BETA", amount="10", day=4),
                record(18, inv="N", vendor="BETA", amount="10", day=1)]
        canonical = [(a["row"], b["row"], status, reason)
                     for a, b, status, reason in candidate_pairs(rows)]
        for seed in range(30):
            shuffled = rows.copy()
            random.Random(seed).shuffle(shuffled)
            observed = [(a["row"], b["row"], status, reason)
                        for a, b, status, reason in candidate_pairs(shuffled)]
            self.assertEqual(observed, canonical, msg=f"shuffle seed {seed}")

    def test_generator_and_list_yield_identical_review_stream(self):
        rows = [record(8), record(2), record(4)]
        self.assertEqual(refs((r for r in rows)), refs(rows))
        self.assertEqual(refs(rows), refs(list(reversed(rows))))

    def test_date_sort_still_governs_near_pair_orientation(self):
        rows = [record(2, inv="A", day=5), record(4, inv="B", day=1)]
        self.assertEqual(refs(rows), [("4", "2", "review_possible_duplicate")])

    def test_quoted_newline_source_gap_preserved(self):
        self.assertEqual(refs([record(4), record(2)]),
                         [("2", "4", "exact_invoice_key")])

    def test_equal_decimal_representations_share_near_group(self):
        rows = [record(4, inv="B", amount="1.0"),
                record(2, inv="A", amount="1.00")]
        self.assertEqual(refs(rows), [("2", "4", "review_possible_duplicate")])

    def test_hostile_decimal_context_does_not_change_candidate_order(self):
        rows = [record(5, inv="B", amount="0.00000001"),
                record(2, inv="A", amount="0.00000001")]
        expected = refs(rows)
        with localcontext(Context(prec=2, Emax=4, Emin=-4)) as ctx:
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            self.assertEqual(refs(rows), expected)
        self.assertEqual(expected, [("2", "5", "review_possible_duplicate")])

    def test_inputs_are_not_modified_by_order_normalization(self):
        rows = [record(8), record(2), record(4)]
        old = deepcopy(rows)
        candidate_pairs(rows)
        self.assertEqual(rows, old)

    def test_candidate_cap_still_fails_closed(self):
        rows = [record(8, inv="C"), record(2, inv="A"), record(4, inv="B")]
        with self.assertRaisesRegex(ValueError, "no incomplete report was saved"):
            candidate_pairs(rows, max_candidates=2)
        with self.assertRaisesRegex(ValueError, "safety maximum"):
            candidate_pairs([], max_candidates=MAX_CANDIDATES + 1)

    def test_duplicate_source_line_still_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate invoice physical CSV row"):
            candidate_pairs([record(4), record(2), record(4, inv="Z")])

    def test_bounds_still_apply_before_any_results(self):
        with self.assertRaisesRegex(ValueError, "Too many invoice source records"):
            import fvs_suite.invoice_match as target
            old = target.MAX_RECORDS
            target.MAX_RECORDS = 2
            try:
                candidate_pairs([record(5), record(4), record(2)])
            finally:
                target.MAX_RECORDS = old

    def test_large_reverse_source_does_not_emit_false_pairs(self):
        # 25,000 independent groups exercise sorting and bounded-memory behavior.
        rows = [record(i + 2, inv=f"INV{i}", amount=str(i + 1))
                for i in reversed(range(25_000))]
        self.assertEqual(candidate_pairs(rows), [])


if __name__ == "__main__":
    unittest.main()
