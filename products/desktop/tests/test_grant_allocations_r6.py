"""Real CSV integration tests for explicit grant source-to-claim allocations."""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine
from fvs_suite.grant_allocations import reconcile_allocations


class GrantAllocationR6Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-grant-r6-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)

    def source(self, name, headers, rows):
        path = self.folder / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(rows)
        return str(path)

    def inputs(self, allocations, *,
               ledger_rows=(("T1", "100", "Shared"),),
               budget_rows=(("G1", "200"), ("G2", "200")),
               allocation_headers=("claim_id", "amount", "program", "ledger_reference", "claim_type", "related_claim")):
        claims = self.source("claims.csv", allocation_headers, allocations)
        ledger = self.source("ledger.csv", ("transaction_id", "amount", "program"), ledger_rows)
        budget = self.source("budgets.csv", ("program", "budget"), budget_rows)
        return claims, ledger, budget

    def reports(self, *paths):
        outputs = reconcile_allocations(*paths, str(self.folder))
        self.assertEqual(len(outputs), 3)
        self.assertTrue(all(p.is_file() for p in outputs))
        def read(path):
            with path.open(encoding="utf-8-sig", newline="") as file:
                return list(csv.DictReader(file))
        return read(outputs[0]), read(outputs[1]), outputs[2].read_text(encoding="utf-8")

    def test_split_across_programs_totals_correct_and_never_matched(self):
        paths = self.inputs([
            ("C1", "60", "G1", "T1", "claim", ""),
            ("C2", "40", "G2", "T1", "claim", ""),
        ])
        details, budgets, manifest = self.reports(*paths)
        self.assertEqual(details[0]["claim_amount"], "100.00")
        self.assertEqual(details[0]["ledger_amount"], "100.00")
        self.assertEqual(details[0]["difference"], "0.00")
        self.assertIn("split_allocation_review", details[0]["status"])
        self.assertEqual(details[0]["allocation_count"], "2")
        self.assertEqual(details[0]["allocation_program_count"], "2")
        self.assertEqual({r["program"]: r["claimed"] for r in budgets},
                         {"G1": "60.00", "G2": "40.00"})
        self.assertIn("SHA-256", manifest)

    def test_exact_single_link_remains_matched(self):
        details, _, _ = self.reports(*self.inputs([
            ("C1", "100", "G1", "T1", "claim", ""),
        ], ledger_rows=(("T1", "100", "G1"),)))
        self.assertEqual(details[0]["status"], "matched")

    def test_variance_and_partial_are_both_flagged(self):
        details, _, _ = self.reports(*self.inputs([
            ("C1", "60", "G1", "T1", "claim", ""),
        ], ledger_rows=(("T1", "100", "G1"),)))
        self.assertIn("variance", details[0]["status"])
        self.assertIn("partial_allocation_review", details[0]["status"])

    def test_credit_offsets_only_with_explicit_link_and_never_matched(self):
        details, budgets, _ = self.reports(*self.inputs([
            ("C1", "120", "G1", "T1", "claim", ""),
            ("CR1", "20", "G1", "T1", "credit", "C1"),
        ], ledger_rows=(("T1", "100", "G1"),)))
        self.assertEqual(details[0]["gross_claim_amount"], "120.00")
        self.assertEqual(details[0]["credit_amount"], "20.00")
        self.assertEqual(details[0]["net_claim_amount"], "100.00")
        self.assertIn("credit_memo_review", details[0]["status"])
        self.assertNotIn("unlinked_credit_review", details[0]["status"])
        self.assertEqual(budgets[0]["claimed"], "100.00")
        self.assertEqual(budgets[0]["gross_claimed"], "120.00")

    def test_credit_memo_unknown_reference_review(self):
        details, _, _ = self.reports(*self.inputs([
            ("C1", "100", "G1", "T1", "claim", ""),
            ("CR1", "10", "G1", "T1", "credit", "UNKNOWN"),
        ], ledger_rows=(("T1", "90", "G1"),)))
        self.assertIn("unlinked_credit_review", details[0]["status"])

    def test_cross_program_credit_requires_review(self):
        details, _, _ = self.reports(*self.inputs([
            ("C1", "100", "G1", "T1", "claim", ""),
            ("CR1", "10", "G2", "T1", "credit", "C1"),
        ], ledger_rows=(("T1", "90", "Shared"),)))
        self.assertIn("cross_program_credit_review", details[0]["status"])
        self.assertIn("split_allocation_review", details[0]["status"])

    def test_zero_amount_is_reviewed(self):
        details, _, _ = self.reports(*self.inputs([
            ("C1", "0", "G1", "T1", "claim", ""),
        ], ledger_rows=(("T1", "0", "G1"),)))
        self.assertIn("zero_claim_amount_review", details[0]["status"])

    def test_credit_memo_exceeds_parent(self):
        details, _, _ = self.reports(*self.inputs([
            ("C1", "50", "G1", "T1", "claim", ""),
            ("CR1", "60", "G1", "T1", "credit", "C1"),
        ], ledger_rows=(("T1", "-10", "G1"),)))
        self.assertIn("credit_exceeds_claim_review", details[0]["status"])
        self.assertIn("credit_exceeds_gross_review", details[0]["status"])

    def test_duplicate_claim_id_review_even_across_programs(self):
        details, _, _ = self.reports(*self.inputs([
            ("C1", "60", "G1", "T1", "claim", ""),
            ("C1", "40", "G2", "T1", "claim", ""),
        ]))
        self.assertIn("repeated_claim_id_review", details[0]["status"])

    def test_ambiguous_normalized_reference_flagged(self):
        details, _, _ = self.reports(*self.inputs([
            ("C1", "100", "G1", "T-1", "claim", ""),
        ], ledger_rows=(("T1", "100", "G1"),)))
        self.assertIn("normalized_ledger_reference_review", details[0]["status"])

    def test_missing_source_ledger_is_visible(self):
        details, _, _ = self.reports(*self.inputs([
            ("C1", "100", "G1", "MISSING", "claim", ""),
        ], ledger_rows=()))
        self.assertEqual(details[0]["status"], "missing_ledger")

    def test_missing_claim_for_unallocated_ledger(self):
        details, _, _ = self.reports(*self.inputs([], ledger_rows=(("T1", "100", "G1"),)))
        self.assertIn("missing_claim", details[0]["status"])
        self.assertEqual(details[0]["program"], "G1")

    def test_program_budget_exceeded_and_lineage(self):
        details, summaries, _ = self.reports(*self.inputs([
            ("C1", "100", "G1", "T1", "claim", ""),
        ], ledger_rows=(("T1", "100", "G1"),), budget_rows=(("G1", "80"),)))
        self.assertEqual(summaries[0]["status"], "over_budget_review")
        self.assertIn("row=2:id=C1", details[0]["claim_lineage"])

    def test_blank_ledger_reference_fails_before_export(self):
        paths = self.inputs([("C1", "100", "G1", "", "claim", "")])
        with self.assertRaisesRegex(ValueError, "Missing ledger_reference"):
            reconcile_allocations(*paths, str(self.folder))
        self.assertFalse(list(self.folder.glob("grant-audit-exceptions-*.csv")))

    def test_negative_claim_amount_fails_before_export(self):
        paths = self.inputs([("C1", "-100", "G1", "T1", "claim", "")])
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            reconcile_allocations(*paths, str(self.folder))
        self.assertFalse(list(self.folder.glob("grant-audit-exceptions-*.csv")))

    def test_unknown_claim_type_fails_before_export(self):
        paths = self.inputs([("C1", "100", "G1", "T1", "void", "")])
        with self.assertRaisesRegex(ValueError, "Unsupported claim_type"):
            reconcile_allocations(*paths, str(self.folder))
        self.assertFalse(list(self.folder.glob("grant-audit-exceptions-*.csv")))

    def test_missing_related_claim_on_credit_fails_before_export(self):
        paths = self.inputs([("CR1", "5", "G1", "T1", "credit", "")])
        with self.assertRaisesRegex(ValueError, "related_claim"):
            reconcile_allocations(*paths, str(self.folder))
        self.assertFalse(list(self.folder.glob("grant-audit-exceptions-*.csv")))

    def test_duplicate_budget_program_fails_before_export(self):
        paths = self.inputs([("C1", "100", "G1", "T1", "claim", "")],
                            ledger_rows=(("T1", "100", "G1"),),
                            budget_rows=(("G1", "100"), ("G-1", "100")))
        with self.assertRaisesRegex(ValueError, "duplicate budget"):
            reconcile_allocations(*paths, str(self.folder))
        self.assertFalse(list(self.folder.glob("grant-audit-exceptions-*.csv")))

    def test_ambiguous_aliases_fail_before_export(self):
        paths = self.inputs([("C1", "100", "G1", "T1", "claim", "")])
        bad = self.source("bad-claims.csv", ("claim_id", "amount", "program", "ledger_reference",
                                            "source_transaction_id", "claim_type", "related_claim"),
                          [("C1", "100", "G1", "T1", "T1", "claim", "")])
        with self.assertRaisesRegex(ValueError, "ambiguous 'ledger_reference'"):
            reconcile_allocations(bad, paths[1], paths[2], str(self.folder))
        self.assertFalse(list(self.folder.glob("grant-audit-exceptions-*.csv")))

    def test_formula_in_raw_id_is_neutralized_in_csv(self):
        details, _, _ = self.reports(*self.inputs([
            ('=HYPERLINK("https://evil.example")', "100", "G1", "T1", "claim", ""),
        ], ledger_rows=(("T1", "100", "G1"),)))
        self.assertTrue(details[0]["claim_ids"].startswith("'="))

    def test_missing_budget_not_misrepresented_as_within_budget(self):
        _, summaries, _ = self.reports(*self.inputs([
            ("C1", "100", "G3", "T1", "claim", ""),
        ], ledger_rows=(("T1", "100", "G3"),)))
        self.assertIn("missing_budget", {r["status"] for r in summaries})

    def test_engine_dispatch_selects_linked_mode(self):
        paths = self.inputs([("C1", "60", "G1", "T1", "claim", ""),
                             ("C2", "40", "G2", "T1", "claim", "")])
        outputs = engine.grant_audit(*paths, str(self.folder))
        with outputs[0].open(encoding="utf-8-sig", newline="") as stream:
            record = list(csv.DictReader(stream))[0]
        self.assertIn("split_allocation_review", record["status"])
        self.assertEqual(record["claim_amount"], "100.00")

    def test_legacy_credits_cannot_be_silently_counted_as_claims(self):
        paths = self.inputs([("C1", "100", "G1", "claim", "")],
                            allocation_headers=("claim_id","amount","program","claim_type","related_claim"))
        with self.assertRaisesRegex(ValueError,"requires ledger_reference"):
            engine.grant_audit(*paths, str(self.folder))
        self.assertFalse(list(self.folder.glob("grant-audit-exceptions-*.csv")))

    def test_legacy_one_to_one_mode_stays_available(self):
        paths = self.inputs([("T1", "100", "G1")],
                            ledger_rows=(("T1", "100", "G1"),),
                            budget_rows=(("G1", "150"),),
                            allocation_headers=("id", "amount", "program"))
        outputs = engine.grant_audit(*paths, str(self.folder))
        with outputs[0].open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream))[0]["status"],"matched")


if __name__ == "__main__":
    unittest.main()
