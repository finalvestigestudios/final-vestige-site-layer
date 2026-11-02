"""R131 synthetic integration tests: configurable per-side LedgerDiff CSV match keys.

No customer data, network, license issuance or production output is used.
Each generated report is a local-only review artifact, never an approval.
"""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine


class LedgerCustomMatchR131(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory(prefix="fvs-ledger-r131-")
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.left = self.root / "ledger-left.csv"
        self.right = self.root / "ledger-right.csv"

    def load(self, **options):
        reports = engine.ledger_diff(self.left, self.right, self.root, **options)
        self.assertEqual(len(reports), 1)
        with reports[0].open("r", newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            return list(reader), reader.fieldnames

    def no_report(self):
        self.assertFalse(list(self.root.glob("ledger-diff-*.csv")))

    def test_default_aliases_remain_compatible_and_cited(self):
        self.left.write_bytes(b"transaction_id,amount\nA,1.20\n")
        self.right.write_bytes(b"id,amount\nA,1.20\n")
        records, _ = self.load()
        self.assertEqual(records[0]["status"], "matched")
        self.assertEqual(records[0]["left_match_column"], "transaction_id")
        self.assertEqual(records[0]["right_match_column"], "id")
        self.assertEqual(records[0]["left_amount"], "1.20")

    def test_distinct_explicit_left_and_right_match_headers(self):
        left = b"Payment Reference,amount,id\nX-1,12.30,WRONG\n"
        right = b"pay_ref,amount,id\nX-1,12.30,OTHER\n"
        self.left.write_bytes(left)
        self.right.write_bytes(right)
        records, _ = self.load(left_match_column="Payment Reference",
                               right_match_column="pay_ref")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["status"], "matched")
        self.assertEqual(records[0]["id"], "X1")
        self.assertEqual(records[0]["left_ids"], "X-1")
        self.assertEqual(records[0]["right_ids"], "X-1")
        self.assertEqual(records[0]["left_match_column"], "Payment Reference")
        self.assertEqual(records[0]["right_match_column"], "pay_ref")
        self.assertEqual(records[0]["left_source_sha256"], hashlib.sha256(left).hexdigest())
        self.assertEqual(records[0]["right_source_sha256"], hashlib.sha256(right).hexdigest())

    def test_override_disambiguates_two_auto_id_aliases(self):
        raw = b"id,transaction_id,amount\nA,B,1.00\n"
        self.left.write_bytes(raw)
        self.right.write_bytes(raw)
        with self.assertRaises(ValueError):
            engine.ledger_diff(self.left, self.right, self.root)
        self.no_report()
        rows, _ = self.load(left_match_column="id", right_match_column="id")
        self.assertEqual(rows[0]["status"], "matched")
        self.assertEqual(rows[0]["id"], "A")

    def test_case_and_space_normalize_to_exact_imported_header(self):
        self.left.write_bytes(b"Payment Reference,amount\nX,1.00\n")
        self.right.write_bytes(b"pay_ref,amount\nX,1.00\n")
        rows, _ = self.load(left_match_column="  PAYMENT REFERENCE  ",
                            right_match_column="PAY_REF")
        self.assertEqual(rows[0]["status"], "matched")
        self.assertEqual(rows[0]["left_match_column"], "Payment Reference")

    def test_only_one_side_explicit_uses_other_auto_id_alias(self):
        self.left.write_bytes(b"document_key,amount\nT5,1.00\n")
        self.right.write_bytes(b"reference,amount\nT5,1.00\n")
        rows, _ = self.load(left_match_column="document_key")
        self.assertEqual(rows[0]["status"], "matched")
        self.assertEqual(rows[0]["right_match_column"], "reference")

    def test_unmatched_selected_keys_never_claim_match(self):
        self.left.write_bytes(b"external_ref,amount,id\nA,8.00,SAME\n")
        self.right.write_bytes(b"external_ref,amount,id\nB,8.00,SAME\n")
        rows, _ = self.load(left_match_column="external_ref",
                            right_match_column="external_ref")
        self.assertEqual({r["status"] for r in rows},
                         {"missing_left", "missing_right"})
        self.assertEqual({r["id"] for r in rows}, {"A", "B"})

    def test_missing_explicit_header_fails_before_save(self):
        self.left.write_bytes(b"id,amount\nA,1.00\n")
        self.right.write_bytes(b"id,amount\nA,1.00\n")
        with self.assertRaises(ValueError):
            engine.ledger_diff(self.left, self.right, self.root,
                               left_match_column="not_present")
        self.no_report()

    def test_amount_cannot_be_reused_as_identity(self):
        self.left.write_bytes(b"id,amount\nA,1.00\n")
        self.right.write_bytes(b"id,amount\nA,1.00\n")
        with self.assertRaisesRegex(ValueError, "distinct CSV columns"):
            engine.ledger_diff(self.left, self.right, self.root,
                               left_match_column="amount")
        self.no_report()

    def test_dangerous_or_private_header_name_is_never_echoed(self):
        self.left.write_bytes(b"id,amount\nA,1.00\n")
        self.right.write_bytes(b"id,amount\nA,1.00\n")
        marker = "bank=987654321"
        for invalid in ("", "\n" + marker, "ID\x00" + marker, "id;"+marker,
                        "id/"+marker, "æ_reference", "=" + marker,
                        "x" * 129, 9, False):
            with self.subTest(length=len(str(invalid))):
                with self.assertRaises(ValueError) as caught:
                    engine.ledger_diff(self.left, self.right, self.root,
                                       left_match_column=invalid)
                self.assertNotIn(marker, str(caught.exception))
                self.no_report()

    def test_duplicate_normalized_headers_remain_rejected(self):
        self.left.write_bytes(b"Payment Ref,payment_ref,amount\nA,B,1.00\n")
        self.right.write_bytes(b"id,amount\nA,1.00\n")
        with self.assertRaises(ValueError):
            engine.ledger_diff(self.left, self.right, self.root,
                               left_match_column="payment_ref")
        self.no_report()

    def test_physical_line_citations_survive_quoted_multiline(self):
        self.left.write_bytes(
            b'local_ref,amount,note\r\nA,1.00,"first\r\nsecond"\r\nA,2.00,ok\r\n')
        self.right.write_bytes(b"remote_ref,amount\nA,3.00\n")
        records, _ = self.load(left_match_column="local_ref",
                               right_match_column="remote_ref")
        self.assertEqual(records[0]["left_rows"], "2;4")
        self.assertEqual(records[0]["right_rows"], "2")
        self.assertEqual(records[0]["status"], "duplicate_id_review")
        self.assertEqual(records[0]["difference"], "0.00")

    def test_header_only_report_exposes_mapping_schema_without_fabricated_rows(self):
        self.left.write_bytes(b"local_ref,amount\n")
        self.right.write_bytes(b"remote_ref,amount\n")
        records, fields = self.load(left_match_column="local_ref",
                                    right_match_column="remote_ref")
        self.assertEqual(records, [])
        self.assertIn("left_match_column", fields)
        self.assertIn("right_match_column", fields)
        self.assertEqual(fields[-3:], ["left_source_sha256",
                                       "right_source_sha256", "input_identity_review"])

    def test_invalid_money_and_missing_keys_still_fail_closed(self):
        self.left.write_bytes(b"local_ref,amount\nA,NaN\n")
        self.right.write_bytes(b"remote_ref,amount\nA,1.00\n")
        with self.assertRaises(ValueError):
            engine.ledger_diff(self.left, self.right, self.root,
                               left_match_column="local_ref",
                               right_match_column="remote_ref")
        self.no_report()
        self.left.write_bytes(b"local_ref,amount\n,1.00\n")
        with self.assertRaises(ValueError):
            engine.ledger_diff(self.left, self.right, self.root,
                               left_match_column="local_ref",
                               right_match_column="remote_ref")
        self.no_report()

    def test_original_inputs_are_never_modified(self):
        left = b"local_ref,amount\nA,1.00\n"
        right = b"remote_ref,amount\nA,1.00\n"
        self.left.write_bytes(left)
        self.right.write_bytes(right)
        self.load(left_match_column="local_ref", right_match_column="remote_ref")
        self.assertEqual(self.left.read_bytes(), left)
        self.assertEqual(self.right.read_bytes(), right)

    def test_existing_table_tuple_shapes_stay_compatible(self):
        self.left.write_bytes(b"id,amount\nA,1.00\n")
        rows = engine.table(self.left, ("id", "amount"))
        self.assertEqual(len(rows), 1)
        rows_digest = engine.table(self.left, ("id", "amount"), include_digest=True)
        self.assertEqual(len(rows_digest), 2)
        rows_fields_digest = engine.table(
            self.left, ("id", "amount"), include_headers=True, include_digest=True)
        self.assertEqual(len(rows_fields_digest), 3)
        self.assertEqual(rows_fields_digest[1], {"id", "amount"})


if __name__ == "__main__":
    unittest.main()
