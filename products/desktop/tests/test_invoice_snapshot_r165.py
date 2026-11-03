"""R165 direct Invoice Twin Scout input-ownership regression: synthetic records only.

A caller can legally yield the same mutable dict for consecutive source rows.
Candidate calculations must retain validated snapshots, not dangling aliases.
No finance data, external services, approvals or premium artifacts are used.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from decimal import Context, Decimal, Inexact, Rounded, localcontext
import hashlib
import unittest

from fvs_suite.invoice_match import candidate_pairs, review_flags
from fvs_suite.invoice_provenance import attach_invoice_provenance


def row(line=2, *, inv="A", vendor="ACME", amount="1.00", day=0, label=None):
    return {
        "row": str(line), "v": vendor, "inv": inv, "amt": Decimal(amount),
        "dt": date(2026, 1, 1) + timedelta(days=day),
        "vendor": label if label is not None else vendor,
        "invoice_number": inv,
    }


def reused(specifications, **kwargs):
    """One physical mutable mapping, deliberately recycled at every yield."""
    shared = row()
    def stream():
        for line, vendor, inv, amount, day, label in specifications:
            shared.clear()
            shared.update(row(line, vendor=vendor, inv=inv, amount=amount,
                              day=day, label=label))
            yield shared
    return candidate_pairs(stream(), **kwargs)


def signatures(pairs):
    return [(a["row"], b["row"], status, reason) for a, b, status, reason in pairs]


class InvoiceSnapshotR165(unittest.TestCase):
    def test_recycled_generator_two_near_rows(self):
        pairs = reused([(2, "ACME", "A", "1.00", 0, None),
                        (3, "ACME", "B", "1.00", 1, None)])
        self.assertEqual([(a["row"], b["row"], s) for a, b, s, _ in pairs],
                         [("2", "3", "review_possible_duplicate")])

    def test_recycled_generator_three_near_rows(self):
        specs = [(n, "ACME", inv, "2.00", 0, None)
                 for n, inv in ((2, "A"), (3, "B"), (4, "C"))]
        self.assertEqual([(a["row"], b["row"]) for a, b, _, _ in reused(specs)],
                         [("2", "3"), ("2", "4"), ("3", "4")])

    def test_recycled_generator_exact_invoice_anchor(self):
        pairs = reused([(4, "ACME", "SAME", "3", 2, None),
                        (2, "ACME", "SAME", "4", 0, None),
                        (3, "ACME", "SAME", "5", 1, None)])
        self.assertEqual([(a["row"], b["row"], s) for a, b, s, _ in pairs],
                         [("2", "3", "exact_invoice_key"),
                          ("2", "4", "exact_invoice_key")])

    def test_recycled_generator_keeps_vendors_separate(self):
        self.assertEqual(reused([
            (2, "ACME", "X", "1", 0, None),
            (3, "BETA", "X", "1", 0, None),
        ]), [])

    def test_recycled_generator_keeps_amounts_separate(self):
        self.assertEqual(reused([
            (2, "ACME", "A", "1.00", 0, None),
            (3, "ACME", "B", "2.00", 0, None),
        ]), [])

    def test_recycled_generator_retains_precise_decimals(self):
        pairs = reused([(2, "ACME", "A", "0.00000001", 0, None),
                        (3, "ACME", "B", "0.00000001", 0, None)])
        self.assertEqual(pairs[0][0]["amt"], Decimal("0.00000001"))
        self.assertEqual(pairs[0][1]["amt"], Decimal("0.00000001"))

    def test_recycled_generator_preserves_distinct_original_labels(self):
        pairs = reused([(2, "ACME", "X", "1", 0, "Acme Corporation"),
                        (3, "ACME", "X", "1", 0, "ACME Corp.")])
        a, b, status, _ = pairs[0]
        self.assertEqual((a["vendor"], b["vendor"]),
                         ("Acme Corporation", "ACME Corp."))
        self.assertIn("normalized_vendor_key_review", review_flags(a, b, status))

    def test_distinct_result_mappings_after_reused_generator(self):
        pairs = reused([(2, "ACME", "A", "1", 0, None),
                        (3, "ACME", "B", "1", 0, None)])
        self.assertIsNot(pairs[0][0], pairs[0][1])

    def test_result_records_do_not_alias_original_list(self):
        a, b = row(2, inv="A"), row(3, inv="B")
        results = candidate_pairs([a, b])
        self.assertIsNot(results[0][0], a)
        self.assertIsNot(results[0][1], b)

    def test_mutating_input_after_candidates_does_not_change_evidence(self):
        a, b = row(2, inv="A"), row(3, inv="B")
        results = candidate_pairs([a, b])
        original = signatures(results)
        a.update({"row": "999", "inv": "CORRUPT", "amt": Decimal("999")})
        b.update({"row": "998", "inv": "CORRUPT"})
        self.assertEqual(signatures(results), original)
        self.assertEqual((results[0][0]["amt"], results[0][1]["row"]),
                         (Decimal("1.00"), "3"))

    def test_original_labels_stable_after_input_mutation(self):
        a = row(2, inv="A", label="Original vendor A")
        b = row(3, inv="B", label="Original vendor B")
        results = candidate_pairs([a, b])
        a["vendor"] = "Redacted or replaced"
        b["invoice_number"] = "Changed after lookup"
        self.assertEqual((results[0][0]["vendor"], results[0][1]["invoice_number"]),
                         ("Original vendor A", "B"))

    def test_provenance_candidate_ref_binds_original_source_lines(self):
        a, b = row(2, inv="A"), row(3, inv="B")
        pairs = candidate_pairs([a, b])
        digest = hashlib.sha256(b"synthetic original invoice CSV").hexdigest()
        def evidence():
            return attach_invoice_provenance([
                {"row_a": x["row"], "row_b": y["row"], "status": kind}
                for x, y, kind, _ in pairs
            ], source_sha256=digest)
        before = evidence()
        a["row"], b["row"] = "400", "500"
        self.assertEqual(evidence(), before)
        self.assertEqual((before[0]["row_a"], before[0]["row_b"]), ("2", "3"))

    def test_recycled_input_matches_independent_dict_records(self):
        specs = [(2, "ACME", "A", "1", 4, None),
                 (3, "ACME", "B", "1", 0, None),
                 (4, "ACME", "A", "2", 10, None),
                 (5, "BETA", "A", "1", 0, None)]
        independent = [row(n, vendor=v, inv=i, amount=amt, day=day, label=label)
                       for n, v, i, amt, day, label in specs]
        self.assertEqual(signatures(reused(specs)), signatures(candidate_pairs(independent)))

    def test_out_of_order_recycled_source_is_numeric(self):
        result = reused([(30, "ACME", "X", "5", 0, None),
                         (2, "ACME", "X", "5", 0, None),
                         (10, "ACME", "X", "5", 0, None)])
        self.assertEqual([(a["row"], b["row"]) for a, b, _, _ in result],
                         [("2", "10"), ("2", "30")])

    def test_bad_later_row_blocks_all_results(self):
        def stream():
            yield row(2, inv="A")
            yield row(3, inv="B", amount="1").__class__(
                row="INVALID", v="ACME", inv="B", amt=Decimal("1"),
                dt=date(2026, 1, 1), vendor="ACME", invoice_number="B")
        with self.assertRaisesRegex(ValueError, "physical CSV row"):
            candidate_pairs(stream())

    def test_recycled_duplicate_physical_line_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate invoice physical CSV row"):
            reused([(2, "ACME", "A", "1", 0, None),
                    (2, "ACME", "B", "1", 1, None)])

    def test_recycled_generator_fails_closed_at_candidate_cap(self):
        specs = [(n, "ACME", key, "1.00", 0, None)
                 for n, key in ((2, "A"), (3, "B"), (4, "C"))]
        with self.assertRaisesRegex(ValueError, "no incomplete report was saved"):
            reused(specs, max_candidates=2)

    def test_list_inputs_remain_unchanged_by_snapshot(self):
        rows = [row(8, inv="C"), row(2, inv="A"), row(3, inv="B")]
        before = deepcopy(rows)
        candidate_pairs(rows)
        self.assertEqual(rows, before)

    def test_hostile_decimal_context_preserves_source_snapshot(self):
        rows = [row(2, inv="A", amount="0.00000001"),
                row(3, inv="B", amount="0.00000001")]
        expected = signatures(candidate_pairs(rows))
        with localcontext(Context(prec=2, Emax=4, Emin=-4)) as ctx:
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            self.assertEqual(signatures(candidate_pairs(rows)), expected)

    def test_empty_recycled_generator_has_no_candidates(self):
        self.assertEqual(reused([]), [])


if __name__ == "__main__":
    unittest.main()
