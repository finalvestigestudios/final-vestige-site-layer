"""R148: LedgerDiff must not conceal gross transaction movement behind equal nets.

All test ledgers are synthetic and private, all outcomes require human review.
Source custody, Decimal cents, explicit header mappings, and premium gates
remain governed by the existing suite. No real financial input is used.
"""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from decimal import Inexact, Rounded, localcontext
from pathlib import Path

from fvs_suite import engine


class LedgerGrossFlowR148(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="fvs-ledger-flow-r148-")
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.left = self.root / "synthetic-left.csv"
        self.right = self.root / "synthetic-right.csv"

    def sources(self, left, right, *, header="id,amount\n"):
        a = (header + "".join(f"{key},{amount}\n" for key, amount in left)).encode("utf-8")
        b = (header + "".join(f"{key},{amount}\n" for key, amount in right)).encode("utf-8")
        self.left.write_bytes(a)
        self.right.write_bytes(b)
        return a, b

    def report(self, **options):
        path, = engine.ledger_diff(self.left, self.right, self.root, **options)
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            return list(reader), tuple(reader.fieldnames or ())

    def one(self, **options):
        rows, _ = self.report(**options)
        self.assertEqual(len(rows), 1)
        return rows[0]

    def no_report(self):
        self.assertFalse(list(self.root.glob("ledger-diff-*.csv")))
        self.assertFalse(list(self.root.glob(".*.partial")))

    @staticmethod
    def flows(item):
        return tuple(item[field] for field in (
            "left_gross_charges", "left_gross_credits",
            "right_gross_charges", "right_gross_credits"))

    def test_simple_identical_charge_remains_matched(self):
        self.sources([("A", "10.25")], [("A", "10.25")])
        item = self.one()
        self.assertEqual(item["status"], "matched")
        self.assertEqual(self.flows(item), ("10.25", "0.00", "10.25", "0.00"))

    def test_simple_identical_credit_remains_matched(self):
        self.sources([("A", "-10.25")], [("A", "-10.25")])
        item = self.one()
        self.assertEqual(item["status"], "matched")
        self.assertEqual(self.flows(item), ("0.00", "10.25", "0.00", "10.25"))

    def test_hidden_left_offset_is_explicit_review_not_matched(self):
        self.sources([("A", "150.00"), ("A", "-140.00")], [("A", "10.00")])
        item = self.one()
        self.assertEqual(item["difference"], "0.00")
        self.assertEqual(item["status"],
                         "duplicate_id_review;gross_flow_mismatch_review")
        self.assertEqual(self.flows(item),
                         ("150.00", "140.00", "10.00", "0.00"))

    def test_hidden_right_offset_is_explicit_review(self):
        self.sources([("A", "10")], [("A", "150"), ("A", "-140")])
        item = self.one()
        self.assertEqual(item["status"],
                         "duplicate_id_review;gross_flow_mismatch_review")
        self.assertEqual(self.flows(item), ("10.00", "0.00", "150.00", "140.00"))

    def test_zero_net_cancellation_cannot_appear_matched(self):
        self.sources([("A", "500"), ("A", "-500")], [("A", "0")])
        item = self.one()
        self.assertEqual(item["left_amount"], "0.00")
        self.assertEqual(item["right_amount"], "0.00")
        self.assertIn("gross_flow_mismatch_review", item["status"])
        self.assertEqual(self.flows(item), ("500.00", "500.00", "0.00", "0.00"))

    def test_equal_net_both_sides_different_gross(self):
        self.sources([("A", "100"), ("A", "-20")],
                     [("A", "200"), ("A", "-120")])
        item = self.one()
        self.assertEqual(item["difference"], "0.00")
        self.assertIn("gross_flow_mismatch_review", item["status"])
        self.assertEqual(self.flows(item), ("100.00", "20.00", "200.00", "120.00"))

    def test_equal_gross_reordered_transactions_do_not_flag(self):
        self.sources([("A", "75"), ("A", "-25")],
                     [("A", "-25"), ("A", "75")])
        item = self.one()
        self.assertEqual(item["status"], "duplicate_id_review")
        self.assertEqual(self.flows(item), ("75.00", "25.00", "75.00", "25.00"))

    def test_same_positive_gross_different_row_counts_does_not_flag(self):
        self.sources([("A", "15"), ("A", "35")], [("A", "50")])
        item = self.one()
        self.assertEqual(item["status"], "duplicate_id_review")
        self.assertEqual(self.flows(item), ("50.00", "0.00", "50.00", "0.00"))

    def test_missing_left_is_not_misclassified_as_gross_mismatch(self):
        self.sources([], [("A", "20")])
        item = self.one()
        self.assertEqual(item["status"], "missing_left")
        self.assertEqual(self.flows(item), ("0.00", "0.00", "20.00", "0.00"))

    def test_missing_right_is_not_misclassified_as_gross_mismatch(self):
        self.sources([("A", "-20")], [])
        item = self.one()
        self.assertEqual(item["status"], "missing_right")
        self.assertEqual(self.flows(item), ("0.00", "20.00", "0.00", "0.00"))

    def test_unequal_net_preserves_variance_without_duplicate_gross_flag(self):
        self.sources([("A", "10")], [("A", "11")])
        item = self.one()
        self.assertEqual(item["status"], "variance")
        self.assertEqual(item["difference"], "-1.00")

    def test_unequal_net_duplicates_preserve_existing_flags(self):
        self.sources([("A", "100"), ("A", "-20")], [("A", "81")])
        item = self.one()
        self.assertEqual(item["status"], "duplicate_id_review;variance")
        self.assertEqual(self.flows(item), ("100.00", "20.00", "81.00", "0.00"))

    def test_negative_zero_is_not_credit_movement(self):
        self.sources([("A", "-0.00")], [("A", "0.00")])
        item = self.one()
        self.assertEqual(item["status"], "matched")
        self.assertEqual(self.flows(item), ("0.00", "0.00", "0.00", "0.00"))

    def test_zero_plus_charge_does_not_change_gross(self):
        self.sources([("A", "0"), ("A", "12")], [("A", "12")])
        item = self.one()
        self.assertEqual(item["status"], "duplicate_id_review")
        self.assertEqual(self.flows(item), ("12.00", "0.00", "12.00", "0.00"))

    def test_cent_precision_is_exact_across_credits(self):
        self.sources([("A", "0.01"), ("A", "0.02"), ("A", "-0.01")],
                     [("A", "0.02")])
        item = self.one()
        self.assertEqual(item["difference"], "0.00")
        self.assertEqual(self.flows(item), ("0.03", "0.01", "0.02", "0.00"))
        self.assertIn("gross_flow_mismatch_review", item["status"])

    def test_one_trillion_boundary_keeps_decimal_cents(self):
        self.sources([("A", "1000000000000.00"), ("A", "-999999999999.99")],
                     [("A", "0.01")])
        item = self.one()
        self.assertEqual(item["left_amount"], "0.01")
        self.assertEqual(self.flows(item),
                         ("1000000000000.00", "999999999999.99", "0.01", "0.00"))

    def test_low_precision_and_rounding_traps_do_not_corrupt_gross(self):
        self.sources([("A", "1000000000000.00"), ("A", "-999999999999.99")],
                     [("A", "0.01")])
        with localcontext() as context:
            context.prec = 2
            context.traps[Inexact] = True
            context.traps[Rounded] = True
            item = self.one()
            self.assertEqual(context.prec, 2)
        self.assertEqual(item["difference"], "0.00")
        self.assertEqual(item["left_gross_credits"], "999999999999.99")

    def test_multiline_source_physical_rows_preserved(self):
        left = b'id,amount,note\r\nA,100,"first\r\nsecond"\r\nA,-90,last\r\n'
        right = b"id,amount\nA,10\n"
        self.left.write_bytes(left)
        self.right.write_bytes(right)
        item = self.one()
        self.assertEqual(item["left_rows"], "2;4")
        self.assertEqual(item["right_rows"], "2")
        self.assertIn("gross_flow_mismatch_review", item["status"])

    def test_original_source_sha256_and_files_preserved(self):
        left, right = self.sources([("A", "20"), ("A", "-10")],
                                   [("A", "10")])
        item = self.one()
        self.assertEqual(item["left_source_sha256"], hashlib.sha256(left).hexdigest())
        self.assertEqual(item["right_source_sha256"], hashlib.sha256(right).hexdigest())
        self.assertEqual(self.left.read_bytes(), left)
        self.assertEqual(self.right.read_bytes(), right)

    def test_repeat_reports_have_deterministic_content(self):
        self.sources([("A", "150"), ("A", "-90")], [("A", "60")])
        first_rows, first_fields = self.report()
        second_rows, second_fields = self.report()
        self.assertEqual(first_rows, second_rows)
        self.assertEqual(first_fields, second_fields)

    def test_header_only_inputs_publish_unfabricated_schema(self):
        self.sources([], [])
        rows, fields = self.report()
        self.assertEqual(rows, [])
        self.assertEqual(fields[9:13], (
            "left_gross_charges", "left_gross_credits",
            "right_gross_charges", "right_gross_credits"))
        self.assertEqual(fields[-5:], (
            "left_amount_column", "right_amount_column",
            "left_source_sha256", "right_source_sha256", "input_identity_review"))

    def test_cross_keys_do_not_share_gross_flows(self):
        self.sources([("A", "100"), ("A", "-70"), ("B", "2")],
                     [("A", "30"), ("B", "2")])
        rows, _ = self.report()
        by_id = {row["id"]: row for row in rows}
        self.assertIn("gross_flow_mismatch_review", by_id["A"]["status"])
        self.assertEqual(by_id["B"]["status"], "matched")
        self.assertEqual(self.flows(by_id["B"]), ("2.00", "0.00", "2.00", "0.00"))

    def test_explicit_amount_mapping_retains_gross_evidence(self):
        self.left.write_bytes(b"id,Debit Value\nA,100\nA,-90\n")
        self.right.write_bytes(b"id,Credit Value\nA,10\n")
        item = self.one(left_amount_column="Debit Value",
                        right_amount_column="Credit Value")
        self.assertEqual(item["left_amount_column"], "Debit Value")
        self.assertEqual(item["right_amount_column"], "Credit Value")
        self.assertEqual(item["left_gross_credits"], "90.00")
        self.assertIn("gross_flow_mismatch_review", item["status"])

    def test_invalid_money_fails_before_any_report_publication(self):
        self.sources([("A", "10"), ("A", "NaN")], [("A", "10")])
        with self.assertRaises(ValueError):
            engine.ledger_diff(self.left, self.right, self.root)
        self.no_report()

    def test_rejected_private_money_not_reflected_in_error(self):
        secret = "PRIVATE-BANK-ACCOUNT-987654321"
        self.sources([("A", secret)], [("A", "10")])
        with self.assertRaises(ValueError) as caught:
            engine.ledger_diff(self.left, self.right, self.root)
        self.assertNotIn(secret, str(caught.exception))
        self.no_report()

    def test_normalized_identity_collision_still_requires_review(self):
        self.sources([("A-B", "25"), ("AB", "-5")], [("AB", "20")])
        item = self.one()
        self.assertIn("normalized_id_review", item["status"])
        self.assertIn("gross_flow_mismatch_review", item["status"])
        self.assertEqual(item["input_identity_review"], "")

    def test_output_source_identical_hash_flag_unchanged(self):
        self.sources([("A", "10")], [("A", "10")])
        self.right.write_bytes(self.left.read_bytes())
        item = self.one()
        self.assertEqual(item["input_identity_review"], "identical_source_bytes_review")

    def test_formula_like_transaction_identity_stays_escaped(self):
        self.sources([("=A", "5")], [("=A", "5")])
        item = self.one()
        self.assertEqual(item["left_ids"], "'=A")
        self.assertEqual(item["status"], "matched")


if __name__ == "__main__":
    unittest.main()
