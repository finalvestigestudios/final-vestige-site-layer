"""R142 Invoice Twin Scout: exact signed delta, calendar gap, and credit-review cues.

Synthetic CSV inputs only; no external data, telemetry or automated fraud finding.
"""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from decimal import Inexact, Rounded, localcontext
from pathlib import Path

from fvs_suite import engine


class InvoiceCandidateEvidenceR142(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="fvs-r142-invoices-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.input = self.root / "synthetic-invoices.csv"

    def source(self, rows):
        with self.input.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "invoice_number", "amount", "date"))
            writer.writerows(rows)
        return self.input

    def report(self, *, window_days=7):
        output = engine.invoice_twins(self.input, self.root, window_days=window_days)[0]
        with output.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
            fields = tuple(reader.fieldnames)
        return rows, fields

    @staticmethod
    def invoice(number, amount, day="2026-01-01", vendor="ACME"):
        return (vendor, number, amount, day)

    def test_exact_equal_same_day_measures_zero(self):
        self.source([self.invoice("A", "10"), self.invoice("A", "10")])
        rows, _ = self.report()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "exact_invoice_key")
        self.assertEqual((rows[0]["amount_delta_b_minus_a"], rows[0]["date_gap_days"]),
                         ("0.00", "0"))
        self.assertEqual(rows[0]["review_flags"], "")

    def test_exact_amount_increase_is_signed_b_minus_a(self):
        self.source([self.invoice("A", "10"), self.invoice("A", "11.25")])
        row = self.report()[0][0]
        self.assertEqual(row["amount_delta_b_minus_a"], "1.25")
        self.assertIn("amount_variance_review", row["review_flags"])

    def test_exact_amount_decrease_is_signed_b_minus_a(self):
        self.source([self.invoice("A", "11.25"), self.invoice("A", "10")])
        self.assertEqual(self.report()[0][0]["amount_delta_b_minus_a"], "-1.25")

    def test_positive_invoice_and_negative_credit_receive_review(self):
        self.source([self.invoice("A", "100"), self.invoice("A", "-100")])
        row = self.report()[0][0]
        self.assertEqual(row["amount_delta_b_minus_a"], "-200.00")
        self.assertIn("opposing_signed_amounts_review", row["review_flags"])
        self.assertIn("amount_variance_review", row["review_flags"])
        self.assertEqual(row["status"], "exact_invoice_key")

    def test_negative_credit_and_positive_invoice_receive_review(self):
        self.source([self.invoice("A", "-100"), self.invoice("A", "100")])
        row = self.report()[0][0]
        self.assertEqual(row["amount_delta_b_minus_a"], "200.00")
        self.assertIn("opposing_signed_amounts_review", row["review_flags"])

    def test_zero_to_negative_is_not_opposing_signed_review(self):
        self.source([self.invoice("A", "0"), self.invoice("A", "-1")])
        row = self.report()[0][0]
        self.assertEqual(row["amount_delta_b_minus_a"], "-1.00")
        self.assertNotIn("opposing_signed_amounts_review", row["review_flags"])
        self.assertIn("amount_variance_review", row["review_flags"])

    def test_negative_zero_not_reviewed_as_credit(self):
        self.source([self.invoice("A", "-0.00"), self.invoice("A", "0.00")])
        row = self.report()[0][0]
        self.assertEqual(row["amount_delta_b_minus_a"], "0.00")
        self.assertNotIn("opposing_signed_amounts_review", row["review_flags"])

    def test_equal_negative_amounts_are_not_opposing(self):
        self.source([self.invoice("A", "-50"), self.invoice("A", "-50")])
        row = self.report()[0][0]
        self.assertEqual(row["amount_delta_b_minus_a"], "0.00")
        self.assertEqual(row["review_flags"], "")

    def test_near_candidate_has_zero_delta_and_seven_day_gap(self):
        self.source([self.invoice("A", "10"), self.invoice("B", "10", "2026-01-08")])
        row = self.report()[0][0]
        self.assertEqual(row["status"], "review_possible_duplicate")
        self.assertEqual((row["amount_delta_b_minus_a"], row["date_gap_days"]), ("0.00", "7"))

    def test_near_different_amount_not_misclassified(self):
        self.source([self.invoice("A", "10"), self.invoice("B", "10.01")])
        self.assertEqual(self.report()[0], [])

    def test_near_opposing_amount_not_misclassified(self):
        self.source([self.invoice("A", "10"), self.invoice("B", "-10")])
        self.assertEqual(self.report()[0], [])

    def test_zero_day_window_preserves_same_day_measurements(self):
        self.source([self.invoice("A", "10"), self.invoice("B", "10")])
        row = self.report(window_days=0)[0][0]
        self.assertEqual((row["amount_delta_b_minus_a"], row["date_gap_days"]), ("0.00", "0"))

    def test_exact_gap_independent_of_zero_day_window(self):
        self.source([self.invoice("A", "10"), self.invoice("A", "10", "2026-06-01")])
        row = self.report(window_days=0)[0][0]
        self.assertEqual(row["date_gap_days"], "151")
        self.assertEqual(row["review_window_days"], "0")
        self.assertIn("distant_dates_review", row["review_flags"])

    def test_distant_exact_review_respects_custom_window(self):
        self.source([self.invoice("A", "10"), self.invoice("A", "10", "2026-01-11")])
        short = self.report(window_days=7)[0][0]
        long = self.report(window_days=14)[0][0]
        self.assertEqual((short["date_gap_days"], long["date_gap_days"]), ("10", "10"))
        self.assertIn("distant_dates_review", short["review_flags"])
        self.assertNotIn("distant_dates_review", long["review_flags"])

    def test_calendar_leap_day_gap(self):
        self.source([self.invoice("A", "2", "2024-02-28"),
                     self.invoice("A", "2", "2024-03-01")])
        self.assertEqual(self.report()[0][0]["date_gap_days"], "2")

    def test_source_half_cent_rounding_matches_display_delta(self):
        self.source([self.invoice("A", "0.005"), self.invoice("A", "0.015")])
        row = self.report()[0][0]
        self.assertEqual((row["amount_a"], row["amount_b"],
                          row["amount_delta_b_minus_a"]), ("0.01", "0.02", "0.01"))

    def test_maximum_amounts_retained_under_decimal_context(self):
        self.source([self.invoice("A", "1000000000000"),
                     self.invoice("A", "-1000000000000")])
        row = self.report()[0][0]
        self.assertEqual(row["amount_delta_b_minus_a"], "-2000000000000.00")
        self.assertIn("opposing_signed_amounts_review", row["review_flags"])

    def test_hostile_decimal_precision_and_traps_do_not_change_delta(self):
        self.source([self.invoice("A", "999999999999.99"),
                     self.invoice("A", "999999999999.98")])
        with localcontext() as context:
            context.prec = 2
            context.traps[Inexact] = True
            context.traps[Rounded] = True
            row = self.report()[0][0]
        self.assertEqual(row["amount_delta_b_minus_a"], "-0.01")

    def test_multiline_physical_rows_and_source_sha(self):
        self.source([self.invoice("A", "10", vendor="ACME\nSITE"),
                     self.invoice("A", "11", vendor="ACME\nSITE")])
        original = self.input.read_bytes()
        row = self.report()[0][0]
        self.assertEqual((row["row_a"], row["row_b"]), ("2", "4"))
        self.assertEqual(row["source_sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(self.input.read_bytes(), original)

    def test_report_repeats_identically_with_stable_candidate_ref(self):
        self.source([self.invoice("A", "10"), self.invoice("A", "11")])
        first = self.report()[0]
        second = self.report()[0]
        self.assertEqual(first, second)
        self.assertEqual(first[0]["candidate_ref"], second[0]["candidate_ref"])
        self.assertRegex(first[0]["candidate_ref"], r"\A[0-9a-f]{64}\Z")

    def test_formula_vendor_still_spreadsheet_escaped(self):
        self.source([self.invoice("A", "10", vendor="=SUM(A1)"),
                     self.invoice("A", "11", vendor="=SUM(A1)")])
        row = self.report()[0][0]
        self.assertEqual(row["vendor"], "'=SUM(A1)")
        self.assertEqual(row["amount_delta_b_minus_a"], "1.00")

    def test_invalid_private_date_fails_before_report(self):
        secret = "PRIVATE_DATE_SENTINEL"
        self.source([self.invoice("A", "10"), self.invoice("A", "10", secret)])
        with self.assertRaises(ValueError) as caught:
            self.report()
        self.assertNotIn(secret, str(caught.exception))
        self.assertEqual(list(self.root.glob("invoice-twins-*.csv")), [])

    def test_invalid_private_amount_fails_before_report(self):
        secret = "PRIVATE_AMOUNT_SENTINEL"
        self.source([self.invoice("A", secret), self.invoice("A", "10")])
        with self.assertRaises(ValueError) as caught:
            self.report()
        self.assertNotIn(secret, str(caught.exception))
        self.assertEqual(list(self.root.glob("invoice-twins-*.csv")), [])

    def test_rejected_window_never_writes(self):
        self.source([self.invoice("A", "10"), self.invoice("A", "10")])
        with self.assertRaises(ValueError):
            self.report(window_days=366)
        self.assertEqual(list(self.root.glob("invoice-twins-*.csv")), [])

    def test_header_schema_and_unchanged_provenance_tail(self):
        self.source([self.invoice("A", "10")])
        rows, headers = self.report()
        self.assertEqual(rows, [])
        self.assertEqual(headers[-3:], ("review_window_days", "source_sha256", "candidate_ref"))
        self.assertEqual(headers[headers.index("amount_b") + 1:
                                 headers.index("reason")],
                         ("amount_delta_b_minus_a", "date_gap_days"))

    def test_normalized_invoice_review_flag_still_present(self):
        self.source([self.invoice("A-1", "10"), self.invoice("A1", "10")])
        row = self.report()[0][0]
        self.assertIn("normalized_invoice_key_review", row["review_flags"])
        self.assertEqual(row["amount_delta_b_minus_a"], "0.00")

    def test_opposite_sign_flag_combines_with_distant_date_review(self):
        self.source([self.invoice("A", "100"), self.invoice("A", "-100", "2026-02-01")])
        row = self.report()[0][0]
        self.assertEqual(row["date_gap_days"], "31")
        self.assertIn("opposing_signed_amounts_review", row["review_flags"])
        self.assertIn("distant_dates_review", row["review_flags"])

    def test_many_exact_identifiers_anchor_stays_stable(self):
        self.source([self.invoice("A", "10"),
                     self.invoice("A", "11", "2026-01-02"),
                     self.invoice("A", "-10", "2026-01-03")])
        rows, _ = self.report()
        self.assertEqual([(r["row_a"], r["row_b"]) for r in rows],
                         [("2", "3"), ("2", "4")])
        self.assertEqual([r["amount_delta_b_minus_a"] for r in rows],
                         ["1.00", "-20.00"])


if __name__ == "__main__":
    unittest.main()
