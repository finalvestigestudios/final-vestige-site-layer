"""Fail-closed accounting reconciliation tests for high-risk ambiguity."""
import tempfile
import unittest
from pathlib import Path

from ledger_bridge import parse_money, read_ledger, reconcile, render_html


class LedgerBridgeSafetyTests(unittest.TestCase):
    def compare(self, left_rows: str, right_rows: str, tolerance: int = 3) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            left, right = root / "left.csv", root / "right.csv"
            left.write_text("date,amount,reference\n" + left_rows, encoding="utf-8")
            right.write_text("date,amount,reference\n" + right_rows, encoding="utf-8")
            return reconcile(left, right, date_tolerance=tolerance)

    def test_duplicate_exact_identity_on_both_sides_never_fifo_pairs(self):
        result = self.compare(
            "2026-01-01,50.00,REF-1\n2026-01-02,50.00,REF1\n",
            "2026-01-01,50.00,REF-1\n2026-01-02,50.00,REF1\n",
        )
        self.assertEqual(result["counts"]["matched"], 0)
        self.assertEqual(result["ambiguous_left_rows"], [2, 3])
        self.assertEqual(result["ambiguous_right_rows"], [2, 3])
        self.assertEqual(len(result["ambiguous_reference_groups"]), 1)
        self.assertEqual(result["status"], "REVIEW")

    def test_single_left_two_right_duplicate_identity_is_quarantined(self):
        result = self.compare(
            "2026-01-02,50.00,REF1\n",
            "2026-01-01,50.00,REF-1\n2026-01-02,50.00,REF1\n",
        )
        self.assertEqual(result["counts"]["matched"], 0)
        self.assertEqual(result["counts"]["unmatched_left"], 1)
        self.assertEqual(result["counts"]["unmatched_right"], 2)
        self.assertEqual(result["ambiguous_left_rows"], [2])
        self.assertEqual(result["ambiguous_right_rows"], [2, 3])

    def test_blank_amount_rejected_not_silently_zero(self):
        with self.assertRaises(ValueError):
            parse_money("")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.csv"
            path.write_text("date,amount\n2026-01-01,\n", encoding="utf-8")
            records, errors = read_ledger(path)
            self.assertEqual(records, [])
            self.assertEqual(len(errors), 1)
            self.assertIn("blank", errors[0]["message"])

    def test_both_blank_debit_credit_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.csv"
            path.write_text("date,debit,credit\n2026-01-01,,\n2026-01-02,12.00,\n", encoding="utf-8")
            records, errors = read_ledger(path)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["row"], 3)
            self.assertEqual(len(errors), 1)
            self.assertIn("blank", errors[0]["message"])

    def test_unique_amount_date_is_review_suggestion_not_confirmed(self):
        result = self.compare("2026-01-01,50.00,A\n", "2026-01-02,50.00,B\n")
        self.assertEqual(result["counts"]["matched"], 1)
        self.assertEqual(result["counts"]["suggested_matches"], 1)
        self.assertEqual(result["status"], "REVIEW")
        self.assertIn("AMOUNT_DATE_SUGGESTIONS", {w["code"] for w in result["warnings"]})

    def test_distant_exact_reference_requires_review(self):
        result = self.compare("2026-01-01,50.00,A\n", "2026-02-01,50.00,A\n")
        self.assertEqual(result["counts"]["matched"], 1)
        self.assertEqual(result["counts"]["suggested_matches"], 0)
        self.assertEqual(result["status"], "REVIEW")
        self.assertIn("EXACT_REFERENCE_DATE_GAP", {w["code"] for w in result["warnings"]})

    def test_unique_exact_reference_within_tolerance_can_reconcile(self):
        result = self.compare("2026-01-01,50.00,A\n", "2026-01-03,50.00,A\n")
        self.assertEqual(result["status"], "RECONCILED")
        self.assertEqual(result["counts"]["matched"], 1)
        self.assertFalse(result["warnings"])

    def test_two_empty_ledgers_never_claim_reconciled(self):
        result = self.compare("", "")
        self.assertEqual(result["status"], "REVIEW")
        self.assertIn("EMPTY_LEDGER", {w["code"] for w in result["warnings"]})


    def test_html_exports_show_ambiguous_duplicates_and_escape_csv(self):
        report = self.compare(
            "2026-01-01,50.00,<script>alert(1)</script>\n"
            "2026-01-02,50.00,<script>alert(1)</script>\n",
            "2026-01-01,50.00,<script>alert(1)</script>\n"
            "2026-01-02,50.00,<script>alert(1)</script>\n",
        )
        rendered = render_html(report)
        self.assertIn("Ambiguous duplicate identities", rendered)
        self.assertIn("Left CSV rows", rendered)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", rendered)
        self.assertNotIn("<script>", rendered)

    def test_html_exports_surface_suggested_match_and_warning(self):
        report = self.compare("2026-01-01,50.00,A\n", "2026-01-02,50.00,B\n")
        rendered = render_html(report)
        self.assertIn("AMOUNT_DATE_SUGGESTIONS", rendered)
        self.assertIn("UNIQUE_AMOUNT_AND_DATE", rendered)
        self.assertIn("REVIEW", rendered)
        self.assertIn("Matches and suggestions", rendered)


if __name__ == "__main__":
    unittest.main()
