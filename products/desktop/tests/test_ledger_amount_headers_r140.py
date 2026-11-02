"""R140 synthetic LedgerDiff per-side amount mapping and GUI custody gates.

No customer files, network, premium access, or release approvals. Inputs are
created in isolated TemporaryDirectory and all exported flags need human review.
"""
from __future__ import annotations

import csv
import hashlib
import inspect
import tempfile
import unittest
from pathlib import Path

from fvs_suite import app, engine


class LedgerAmountHeadersR140(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory(prefix="fvs-ledger-r140-")
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.left = self.root / "left.csv"
        self.right = self.root / "right.csv"

    def write(self, left: bytes, right: bytes):
        self.left.write_bytes(left)
        self.right.write_bytes(right)

    def run_report(self, **options):
        paths = engine.ledger_diff(self.left, self.right, self.root, **options)
        self.assertEqual(len(paths), 1)
        with paths[0].open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            return list(reader), tuple(reader.fieldnames or ())

    def no_report(self):
        self.assertFalse(list(self.root.glob("ledger-diff-*.csv")))
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_default_amount_alias_is_recorded_per_side(self):
        self.write(b"id,amount\nA,12.30\n", b"id,total\nA,12.30\n")
        rows, fields = self.run_report()
        self.assertEqual(rows[0]["status"], "matched")
        self.assertEqual(rows[0]["left_amount_column"], "amount")
        self.assertEqual(rows[0]["right_amount_column"], "total")
        self.assertIn("left_amount_column", fields)
        self.assertIn("right_amount_column", fields)

    def test_independent_explicit_amount_headers(self):
        left = b"ref,Debit Value,amount\nX-1,1.25,999.00\n"
        right = b"ref,Credit Value,amount\nX-1,1.25,888.00\n"
        self.write(left, right)
        rows, _ = self.run_report(
            left_amount_column="Debit Value", right_amount_column="Credit Value")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "matched")
        self.assertEqual(rows[0]["difference"], "0.00")
        self.assertEqual(rows[0]["left_amount_column"], "Debit Value")
        self.assertEqual(rows[0]["right_amount_column"], "Credit Value")
        self.assertEqual(rows[0]["left_source_sha256"], hashlib.sha256(left).hexdigest())
        self.assertEqual(rows[0]["right_source_sha256"], hashlib.sha256(right).hexdigest())

    def test_left_only_override_preserves_right_auto(self):
        self.write(b"id,paid_value\nA,5.25\n", b"id,amount\nA,5.25\n")
        rows, _ = self.run_report(left_amount_column="paid_value")
        self.assertEqual(rows[0]["status"], "matched")
        self.assertEqual(rows[0]["right_amount_column"], "amount")

    def test_right_only_override_preserves_left_auto(self):
        self.write(b"id,total\nA,5.25\n", b"id,pay_amt\nA,5.25\n")
        rows, _ = self.run_report(right_amount_column="pay_amt")
        self.assertEqual(rows[0]["status"], "matched")
        self.assertEqual(rows[0]["left_amount_column"], "total")

    def test_override_and_match_headers_can_both_differ(self):
        self.write(b"left_ref,left_amt\nA,10.01\n",
                   b"right_ref,right_amt\nA,10.01\n")
        rows, _ = self.run_report(
            left_match_column="left_ref", right_match_column="right_ref",
            left_amount_column="left_amt", right_amount_column="right_amt")
        self.assertEqual(rows[0]["status"], "matched")
        self.assertEqual(rows[0]["left_match_column"], "left_ref")
        self.assertEqual(rows[0]["right_match_column"], "right_ref")
        self.assertEqual(rows[0]["left_amount_column"], "left_amt")
        self.assertEqual(rows[0]["right_amount_column"], "right_amt")

    def test_ambiguous_auto_amount_aliases_fail_closed(self):
        self.write(b"id,amount,total\nA,3.00,300.00\n",
                   b"id,amount\nA,3.00\n")
        with self.assertRaises(ValueError):
            self.run_report()
        self.no_report()

    def test_override_disambiguates_amount_aliases(self):
        self.write(b"id,amount,total\nA,3.00,300.00\n",
                   b"id,amount\nA,3.00\n")
        rows, _ = self.run_report(left_amount_column="amount")
        self.assertEqual(rows[0]["status"], "matched")
        self.assertEqual(rows[0]["left_amount"], "3.00")

    def test_explicit_amount_missing_fails_before_report(self):
        self.write(b"id,amount\nA,3.00\n", b"id,amount\nA,3.00\n")
        with self.assertRaises(ValueError):
            self.run_report(right_amount_column="not_present")
        self.no_report()

    def test_choosing_identity_as_amount_rejected(self):
        self.write(b"id,amount\nA,3.00\n", b"id,amount\nA,3.00\n")
        with self.assertRaisesRegex(ValueError, "distinct CSV columns"):
            self.run_report(left_amount_column="id")
        self.no_report()

    def test_choosing_amount_as_identity_rejected(self):
        self.write(b"id,amount\nA,3.00\n", b"id,amount\nA,3.00\n")
        with self.assertRaisesRegex(ValueError, "distinct CSV columns"):
            self.run_report(left_match_column="amount")
        self.no_report()

    def test_invalid_override_values_are_generic_and_private(self):
        self.write(b"id,amount\nA,3.00\n", b"id,amount\nA,3.00\n")
        secret = "private-bank-987654321"
        for invalid in ("", "A;"+secret, "x/" + secret, "\n"+secret,
                        "@" + secret, "x"*129, False, 4, None if False else []):
            with self.subTest(kind=type(invalid).__name__):
                with self.assertRaises(ValueError) as caught:
                    self.run_report(left_amount_column=invalid)
                self.assertNotIn(secret, str(caught.exception))
                self.no_report()

    def test_non_ascii_override_rejected(self):
        self.write(b"id,amount\nA,3.00\n", b"id,amount\nA,3.00\n")
        with self.assertRaises(ValueError):
            self.run_report(left_amount_column="montant_€")
        self.no_report()

    def test_case_and_space_normalization_preserves_actual_header(self):
        self.write(b"id,Total Paid\nA,6.50\n", b"id,Credits\nA,6.50\n")
        rows, _ = self.run_report(
            left_amount_column="  TOTAL PAID  ", right_amount_column=" CREDITS ")
        self.assertEqual(rows[0]["left_amount_column"], "Total Paid")
        self.assertEqual(rows[0]["right_amount_column"], "Credits")

    def test_duplicate_normalized_headers_rejected(self):
        self.write(b"id,Total Paid,total_paid\nA,1.00,1.00\n",
                   b"id,amount\nA,1.00\n")
        with self.assertRaises(ValueError):
            self.run_report(left_amount_column="Total Paid")
        self.no_report()

    def test_source_physical_line_provenance_multiline(self):
        left = b'id,Debit Value,note\r\nA,1.00,"one\r\ntwo"\r\nA,2.00,last\r\n'
        right = b"id,Credit Value\nA,3.00\n"
        self.write(left, right)
        rows, _ = self.run_report(
            left_amount_column="Debit Value", right_amount_column="Credit Value")
        self.assertEqual(rows[0]["left_rows"], "2;4")
        self.assertEqual(rows[0]["right_rows"], "2")
        self.assertEqual(rows[0]["status"], "duplicate_id_review")
        self.assertEqual(rows[0]["difference"], "0.00")

    def test_exact_negative_money_and_variance(self):
        self.write(b"id,debit\nA,-0.01\n", b"id,credit\nA,0.02\n")
        rows, _ = self.run_report(left_amount_column="debit", right_amount_column="credit")
        self.assertEqual(rows[0]["left_amount"], "-0.01")
        self.assertEqual(rows[0]["right_amount"], "0.02")
        self.assertEqual(rows[0]["difference"], "-0.03")
        self.assertEqual(rows[0]["status"], "variance")

    def test_invalid_money_still_fails_closed(self):
        self.write(b"id,debit\nA,NaN\n", b"id,credit\nA,1.00\n")
        with self.assertRaises(ValueError):
            self.run_report(left_amount_column="debit", right_amount_column="credit")
        self.no_report()

    def test_unmatched_rows_do_not_get_fabricated_citations(self):
        self.write(b"id,debit\nA,4.00\n", b"id,credit\nB,4.00\n")
        rows, _ = self.run_report(left_amount_column="debit", right_amount_column="credit")
        self.assertEqual({row["status"] for row in rows}, {"missing_left", "missing_right"})
        self.assertEqual({row["id"] for row in rows}, {"A", "B"})

    def test_identical_source_bytes_still_require_review(self):
        raw = b"id,amount\nA,10.00\n"
        self.write(raw, raw)
        rows, _ = self.run_report(left_amount_column="amount", right_amount_column="amount")
        self.assertEqual(rows[0]["input_identity_review"], "identical_source_bytes_review")

    def test_header_only_reports_have_schema_and_no_fabrication(self):
        self.write(b"id,debit\n", b"id,credit\n")
        rows, fields = self.run_report(left_amount_column="debit", right_amount_column="credit")
        self.assertEqual(rows, [])
        self.assertEqual(fields[-5:],
                         ("left_amount_column", "right_amount_column",
                          "left_source_sha256", "right_source_sha256", "input_identity_review"))

    def test_sources_unchanged_after_export(self):
        left, right = b"id,debit\nA,1.00\n", b"id,credit\nA,1.00\n"
        self.write(left, right)
        self.run_report(left_amount_column="debit", right_amount_column="credit")
        self.assertEqual(self.left.read_bytes(), left)
        self.assertEqual(self.right.read_bytes(), right)

    def test_table_original_tuple_contract_unchanged(self):
        self.write(b"id,amount\nA,1.00\n", b"id,total\nA,1.00\n")
        self.assertEqual(len(engine.table(self.left, ("id", "amount"))), 1)
        self.assertEqual(len(engine.table(self.left, ("id", "amount"), include_digest=True)), 2)
        self.assertEqual(len(engine.table(
            self.left, ("id", "amount"), include_columns=True,
            amount_column="amount")), 2)

    def test_ledger_layout_maps_all_four_optional_headers(self):
        plan = app._ledger_stacked_rows(2)
        self.assertEqual(plan["keys"], ((9, 10), (11, 12)))
        self.assertEqual(plan["amounts"], ((13, 14), (15, 16)))
        self.assertEqual(plan["output"], (17, 18, 19))
        self.assertGreater(plan["generate"], plan["amounts"][-1][1])

    def test_gui_wires_both_amount_headers_and_does_not_unlock_premium(self):
        body = inspect.getsource(app.run)
        self.assertIn("left_amount_column=ledger_amount_columns[0].get()", body)
        self.assertIn("right_amount_column=ledger_amount_columns[1].get()", body)
        self.assertEqual({key for key, value in app.APPS.items() if value[3]},
                         {"grants", "procurement"})


if __name__ == "__main__":
    unittest.main()
