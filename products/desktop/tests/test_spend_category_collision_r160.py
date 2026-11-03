"""R160: protect SpendMap category identity across spreadsheet-safe CSV escaping.

All data is synthetic, generated in private temporary directories, and never
uploaded. A category review flag is not a fraud, payment, or legal decision.
"""
from __future__ import annotations

import contextlib
import csv
import hashlib
import io
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine
from fvs_suite.spend_analysis import summarize_spend
from fvs_suite.spend_evidence_verify import main, verify_membership
from fvs_suite.spend_report_envelope import COLUMNS


class SpendCategoryR160(unittest.TestCase):
    def setUp(self):
        private = tempfile.TemporaryDirectory(prefix="fvs-r160-synthetic-")
        self.addCleanup(private.cleanup)
        self.root = Path(private.name)
        self.source = self.root / "source.csv"

    @staticmethod
    def row(category="Parts", vendor="Acme", month=1, amount="10.00", note=""):
        return (vendor, amount, f"2026-{month:02d}-01", category, note)

    def write(self, rows):
        with self.source.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(("vendor", "amount", "date", "category", "note"))
            writer.writerows(rows)
        return self.source.read_bytes()

    def good(self, rows):
        source_before = self.write(rows)
        report = Path(engine.spend_map(self.source, self.root)[0])
        receipt = verify_membership(self.source, report)
        self.assertEqual(self.source.read_bytes(), source_before)
        self.assertEqual(receipt.source_sha256, hashlib.sha256(source_before).hexdigest())
        return report, receipt

    def collision(self, a, b, *, vendor_a="Acme", vendor_b="Acme", month_a=1, month_b=1):
        self.write([self.row(a, vendor=vendor_a, month=month_a),
                    self.row(b, vendor=vendor_b, month=month_b)])
        original = self.source.read_bytes()
        before_reports = tuple(self.root.glob("spend-map-*.csv"))
        with self.assertRaisesRegex(ValueError, "Ambiguous SpendMap category"):
            engine.spend_map(self.source, self.root)
        self.assertEqual(tuple(self.root.glob("spend-map-*.csv")), before_reports)
        self.assertEqual(self.source.read_bytes(), original)

    def legacy_export(self, categories):
        """Simulate an old producer that did not guard display-key collisions."""
        self.write([self.row(category) for category in categories])
        records, sha = engine.table(self.source, ("vendor", "amount", "date"),
                                    ("category",), include_digest=True)
        rows = summarize_spend(records, normalize_vendor=engine.key,
                               parse_date=engine.parse_date, parse_money=engine.money,
                               format_money=engine.dollars, source_sha256=sha)
        return Path(engine.save(self.root, "spend-map", COLUMNS, rows))

    def test_plain_category_roundtrip(self):
        _, receipt = self.good([self.row()])
        self.assertEqual(receipt.buckets_verified, 1)

    def test_single_equal_formula_roundtrip(self):
        report, _ = self.good([self.row("=A1")])
        self.assertIn("'=A1", report.read_text(encoding="utf-8-sig"))

    def test_multiple_distinct_formula_categories_roundtrip(self):
        _, receipt = self.good([self.row("=A1"), self.row("=A2"),
                                self.row("+SUM(A1:A2)")])
        self.assertEqual(receipt.buckets_verified, 3)

    def test_literal_apostrophe_category_roundtrip(self):
        _, receipt = self.good([self.row("'=A1")])
        self.assertEqual(receipt.buckets_verified, 1)

    def test_duplicate_identical_formula_category_aggregates(self):
        _, receipt = self.good([self.row("=A1", amount="50.00"),
                                self.row("=A1", amount="-12.00")])
        self.assertEqual(receipt.buckets_verified, 1)

    def test_same_display_other_vendor_allowed(self):
        _, receipt = self.good([self.row("=A1", vendor="Acme"),
                                self.row("'=A1", vendor="Beta")])
        self.assertEqual(receipt.buckets_verified, 2)

    def test_same_display_other_month_allowed(self):
        _, receipt = self.good([self.row("=A1", month=1),
                                self.row("'=A1", month=2)])
        self.assertEqual(receipt.buckets_verified, 2)

    def test_negative_numeric_and_quoted_negative_distinct(self):
        _, receipt = self.good([self.row("-10"), self.row("'-10")])
        self.assertEqual(receipt.buckets_verified, 2)

    def test_mixed_credit_totals_unchanged(self):
        report, _ = self.good([self.row("=A1", amount="125.00"),
                               self.row("=A1", amount="-25.00")])
        with report.open(encoding="utf-8-sig", newline="") as stream:
            row = next(csv.DictReader(stream))
        self.assertEqual((row["amount"], row["gross_charges"],
                          row["gross_credits"]), ("100.00", "125.00", "25.00"))

    def test_multiline_record_roundtrip(self):
        report, _ = self.good([self.row("=A1", note="line one\nline two"),
                               self.row("Parts", note="end")])
        with report.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertIn("4", ";".join(r["source_rows"] for r in rows))

    def test_normal_source_bytes_unmodified(self):
        original = self.write([self.row("=A1")])
        engine.spend_map(self.source, self.root)
        self.assertEqual(self.source.read_bytes(), original)

    def test_case_sensitive_distinct_labels_roundtrip(self):
        _, receipt = self.good([self.row("Parts"), self.row("parts")])
        self.assertEqual(receipt.buckets_verified, 2)

    def test_equal_sign_collision_rejected(self):
        self.collision("=A1", "'=A1")

    def test_plus_formula_collision_rejected(self):
        self.collision("+SUM(A1:A2)", "'+SUM(A1:A2)")

    def test_at_sign_collision_rejected(self):
        self.collision("@NOW", "'@NOW")

    def test_negative_formula_collision_rejected(self):
        self.collision("-DANGEROUS", "'-DANGEROUS")

    def test_zero_width_category_collision_rejected(self):
        self.collision("\u200bParts", "'\u200bParts")

    def test_bidi_isolate_category_collision_rejected(self):
        self.collision("\u2066Parts", "'\u2066Parts")

    def test_combining_prefix_category_collision_rejected(self):
        self.collision("\u0301Parts", "'\u0301Parts")

    def test_quoted_comma_formula_collision_rejected(self):
        self.collision("=SUM(1,2)", "'=SUM(1,2)")

    def test_normalized_vendor_alias_collision_rejected(self):
        self.collision("=A1", "'=A1", vendor_a="A.C.M.E", vendor_b="Acme")

    def test_rejection_creates_no_report(self):
        self.collision("=A1", "'=A1")
        self.assertFalse(list(self.root.glob("spend-map-*.csv")))

    def test_collision_keeps_original_source_unchanged(self):
        self.collision("=1+1", "'=1+1")
        self.assertTrue(self.source.is_file())

    def test_collision_error_does_not_echo_private_category(self):
        self.write([self.row("=PRIVATE-SYNTHETIC-124"),
                    self.row("'=PRIVATE-SYNTHETIC-124")])
        with self.assertRaises(ValueError) as captured:
            engine.spend_map(self.source, self.root)
        self.assertNotIn("PRIVATE-SYNTHETIC", str(captured.exception))
        self.assertNotIn(str(self.root), str(captured.exception))

    def test_independent_verifier_rejects_legacy_ambiguous_export(self):
        report = self.legacy_export(["=A1", "'=A1"])
        with self.assertRaisesRegex(ValueError, "Ambiguous SpendMap source category"):
            verify_membership(self.source, report)

    def test_independent_verifier_rejects_hidden_category_collision(self):
        report = self.legacy_export(["\u200bSECRET", "'\u200bSECRET"])
        with self.assertRaisesRegex(ValueError, "Ambiguous SpendMap source category"):
            verify_membership(self.source, report)

    def test_verifier_cli_redacts_ambiguous_source(self):
        report = self.legacy_export(["=CLIENT-SECRET-991", "'=CLIENT-SECRET-991"])
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = main(["--source", str(self.source), "--report", str(report)])
        self.assertEqual(status, 1)
        self.assertIn("HOLD", err.getvalue())
        self.assertNotIn("CLIENT-SECRET", out.getvalue() + err.getvalue())
        self.assertNotIn(str(self.root), out.getvalue() + err.getvalue())

    def test_verifier_accepts_noncolliding_formula_categories(self):
        report, receipt = self.good([self.row("=X1"), self.row("=X2")])
        self.assertEqual(verify_membership(self.source, report), receipt)

    def test_report_schema_still_exact_25(self):
        report, _ = self.good([self.row("=A1")])
        with report.open(encoding="utf-8-sig", newline="") as f:
            self.assertEqual(tuple(csv.reader(f).__next__()), COLUMNS)

    def test_generated_report_retains_physical_source_citations(self):
        report, _ = self.good([self.row("=A1"), self.row("Parts")])
        with report.open(encoding="utf-8-sig", newline="") as f:
            refs = [r["source_rows"] for r in csv.DictReader(f)]
        self.assertEqual(set(refs), {"2", "3"})


if __name__ == "__main__":
    unittest.main()
