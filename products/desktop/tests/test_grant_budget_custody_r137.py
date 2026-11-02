"""R137 premium GrantAudit budget report source-custody regression suite.

Genuine synthetic local CSV inputs; no customer data, network or automatic approval.
All source rows cite physical starting lines and byte fingerprints of the
snapshots used by the corresponding audit-manifest step.
"""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from decimal import Context, localcontext
from pathlib import Path

from fvs_suite import engine
from fvs_suite.grant_allocations import reconcile_allocations


class GrantBudgetCustodyR137(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r137-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / "reports"
        self.output.mkdir()

    def source(self, filename, headers, data):
        path = self.root / filename
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(data)
        return path

    def sources(self, *, linked=False, claims=None, ledger=None, budgets=None):
        if linked:
            header = ("claim_id", "amount", "program", "ledger_reference",
                      "claim_type", "related_claim")
            if claims is None:
                claims = [("C1", "40.00", "G1", "L1", "claim", "")]
        else:
            header = ("claim_id", "amount", "program")
            if claims is None:
                claims = [("L1", "40.00", "G1")]
        if ledger is None:
            ledger = [("L1", "40.00", "G1")]
        if budgets is None:
            budgets = [("G1", "50.00")]
        return (
            self.source("claims.csv", header, claims),
            self.source("ledger.csv", ("transaction_id", "amount", "program"), ledger),
            self.source("budgets.csv", ("program", "budget"), budgets),
        )

    @staticmethod
    def read_rows(path):
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def report(self, sources, *, direct=False):
        runner = reconcile_allocations if direct else engine.grant_audit
        generated = runner(*sources, self.output)
        self.assertEqual(len(generated), 3)
        budget_file = next(path for path in generated
                           if path.name.startswith("grant-budget-check-"))
        rows = self.read_rows(budget_file)
        return rows, budget_file, generated

    def assert_digests(self, row, sources):
        for field, source in zip(
                ("claim_source_sha256", "ledger_source_sha256", "budget_source_sha256"),
                sources):
            actual = hashlib.sha256(source.read_bytes()).hexdigest()
            self.assertEqual(row[field], actual)
            self.assertEqual(len(row[field]), 64)

    def test_legacy_source_rows_and_digests(self):
        sources = self.sources()
        rows, _, _ = self.report(sources)
        self.assertEqual((rows[0]["claim_rows"], rows[0]["budget_rows"]), ("2", "2"))
        self.assert_digests(rows[0], sources)

    def test_linked_source_rows_and_digests(self):
        sources = self.sources(linked=True)
        rows, _, _ = self.report(sources)
        self.assertEqual((rows[0]["claim_rows"], rows[0]["budget_rows"]), ("2", "2"))
        self.assert_digests(rows[0], sources)

    def test_legacy_multiline_claim_physical_lines(self):
        sources = self.sources(claims=[("L\n1", "10", "G1"), ("L2", "5", "G1")],
                               ledger=[("L1", "10", "G1"), ("L2", "5", "G1")])
        rows, _, _ = self.report(sources)
        self.assertEqual(rows[0]["claim_rows"], "2;4")
        self.assertEqual(rows[0]["claimed"], "15.00")

    def test_linked_credit_claim_rows(self):
        sources = self.sources(
            linked=True,
            claims=[("C1", "50", "G1", "L1", "claim", ""),
                    ("CR1", "10", "G1", "L1", "credit", "C1")])
        rows, _, _ = self.report(sources)
        self.assertEqual(rows[0]["claim_rows"], "2;3")
        self.assertEqual(rows[0]["claimed"], "40.00")
        self.assertIn("credit_memo_review", rows[0]["status"])

    def test_multiple_budget_programs_keep_distinct_lines(self):
        sources = self.sources(
            claims=[("L1", "40", "G1"), ("L2", "30", "G2")],
            ledger=[("L1", "40", "G1"), ("L2", "30", "G2")],
            budgets=[("G1", "50"), ("G2", "60")])
        rows, _, _ = self.report(sources)
        by_program = {row["program"]: row for row in rows}
        self.assertEqual(by_program["G1"]["budget_rows"], "2")
        self.assertEqual(by_program["G2"]["budget_rows"], "3")
        self.assertEqual(by_program["G2"]["claim_rows"], "3")

    def test_missing_budget_has_no_invented_row(self):
        sources = self.sources(budgets=[("G2", "50")])
        rows, _, _ = self.report(sources)
        by_program = {row["program"]: row for row in rows}
        self.assertEqual(by_program["G1"]["budget_rows"], "")
        self.assertEqual(by_program["G1"]["claim_rows"], "2")
        self.assertIn("missing_budget", by_program["G1"]["status"])
        self.assert_digests(by_program["G1"], sources)

    def test_budget_only_program_has_no_claim_rows(self):
        sources = self.sources(budgets=[("G1", "50"), ("G2", "30")])
        rows, _, _ = self.report(sources)
        by_program = {row["program"]: row for row in rows}
        self.assertEqual(by_program["G2"]["budget_rows"], "3")
        self.assertEqual(by_program["G2"]["claim_rows"], "")
        self.assertEqual(by_program["G2"]["claimed"], "0.00")

    def test_legacy_output_is_deterministic(self):
        sources = self.sources()
        first, file_a, _ = self.report(sources)
        second, file_b, _ = self.report(sources)
        self.assertNotEqual(file_a, file_b)
        self.assertEqual(file_a.read_bytes(), file_b.read_bytes())
        self.assertEqual(first, second)

    def test_linked_output_is_deterministic(self):
        sources = self.sources(linked=True)
        _, file_a, _ = self.report(sources)
        _, file_b, _ = self.report(sources)
        self.assertNotEqual(file_a, file_b)
        self.assertEqual(file_a.read_bytes(), file_b.read_bytes())

    def test_sources_remain_byte_identical(self):
        sources = self.sources(linked=True)
        original = [item.read_bytes() for item in sources]
        self.report(sources)
        self.assertEqual([item.read_bytes() for item in sources], original)

    def test_budget_digest_matches_manifest(self):
        sources = self.sources(linked=True)
        rows, _, outputs = self.report(sources)
        manifest = next(path for path in outputs
                        if path.name.startswith("evidence-manifest-")).read_text(encoding="utf-8")
        self.assertIn(sources[2].name + "\t" + rows[0]["budget_source_sha256"], manifest)

    def test_ledger_digest_matches_manifest(self):
        sources = self.sources()
        rows, _, outputs = self.report(sources)
        manifest = next(path for path in outputs
                        if path.name.startswith("evidence-manifest-")).read_text(encoding="utf-8")
        self.assertIn(sources[1].name + "\t" + rows[0]["ledger_source_sha256"], manifest)

    def test_linked_direct_api_has_same_custody(self):
        sources = self.sources(linked=True)
        rows, _, _ = self.report(sources, direct=True)
        self.assertEqual(rows[0]["budget_rows"], "2")
        self.assert_digests(rows[0], sources)

    def test_normalization_review_survives_citations(self):
        sources = self.sources(
            claims=[("L1", "40", "G-1")],
            ledger=[("L1", "40", "G1")],
            budgets=[("G1", "50")])
        rows, _, _ = self.report(sources)
        self.assertIn("normalized_budget_program_review", rows[0]["status"])
        self.assertEqual(rows[0]["budget_rows"], "2")

    def test_low_decimal_precision_keeps_exact_total(self):
        huge = "999999999999.99"
        sources = self.sources(
            claims=[("L1", huge, "G1"), ("L2", huge, "G1")],
            ledger=[("L1", huge, "G1"), ("L2", huge, "G1")],
            budgets=[("G1", huge)])
        with localcontext(Context(prec=4)):
            rows, _, _ = self.report(sources)
        self.assertEqual(rows[0]["claimed"], "1999999999999.98")
        self.assertIn("over_budget_review", rows[0]["status"])

    def test_duplicate_budget_fails_without_any_reports(self):
        sources = self.sources(budgets=[("G1", "50"), ("G-1", "60")])
        with self.assertRaises(ValueError):
            engine.grant_audit(*sources, self.output)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_bom_claim_and_quoted_newline_preserve_lines(self):
        sources = self.sources(
            claims=[("L\n1", "10", "G1"), ("L2", "5", "G1")],
            ledger=[("L1", "10", "G1"), ("L2", "5", "G1")])
        sources[0].write_bytes(b"\xef\xbb\xbf" + sources[0].read_bytes())
        rows, _, _ = self.report(sources)
        self.assertEqual(rows[0]["claim_rows"], "2;4")
        self.assert_digests(rows[0], sources)

    def test_existing_reports_are_not_overwritten(self):
        sources = self.sources()
        _, first_file, first_paths = self.report(sources)
        old = [path.read_bytes() for path in first_paths]
        _, second_file, second_paths = self.report(sources)
        self.assertNotEqual(first_file, second_file)
        self.assertTrue(set(first_paths).isdisjoint(set(second_paths)))
        self.assertEqual([path.read_bytes() for path in first_paths], old)


if __name__ == "__main__":
    unittest.main()
