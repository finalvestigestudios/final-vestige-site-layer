"""R63 Invoice Twin Scout engine/CSV integration in the full repository.

Synthetic local inputs only; no customer records or network activity.
"""
from __future__ import annotations

import csv
import hashlib
import re
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from fvs_suite import engine


class InvoiceSourceEngineR63(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="fvs-invoice-r63-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "input.csv"

    @staticmethod
    def rows(path):
        with path.open(encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))

    def run_invoice(self):
        return engine.invoice_twins(self.source, self.root)[0]

    def test_bom_and_quoted_newline_preserve_physical_source_rows(self):
        raw = (b'\xef\xbb\xbfvendor,invoice_number,amount,date,notes\r\n'
               b'ACME,A-1,10.00,2026-01-01,"first\r\nsecond"\r\n'
               b'Acme,A1,10.00,2026-01-02,ordinary\r\n')
        self.source.write_bytes(raw)
        result = self.rows(self.run_invoice())[0]
        self.assertEqual((result["row_a"], result["row_b"]), ("2", "4"))
        self.assertEqual(result["source_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertRegex(result["candidate_ref"], r"\A[0-9a-f]{64}\Z")
        self.assertEqual(result["status"], "exact_invoice_key")

    def test_repeat_run_same_bytes_stable_audit_identity(self):
        self.source.write_bytes(b"vendor,invoice_number,amount,date\nACME,X,1,2026-01-01\nACME,X,1,2026-01-02\n")
        first = self.rows(self.run_invoice())
        second = self.rows(self.run_invoice())
        self.assertEqual(first, second)
        self.assertEqual(first[0]["source_sha256"], hashlib.sha256(self.source.read_bytes()).hexdigest())

    def test_new_source_bytes_change_identity_despite_equal_parsed_records(self):
        original = b"vendor,invoice_number,amount,date\nACME,X,1,2026-01-01\nACME,X,1,2026-01-02\n"
        self.source.write_bytes(original)
        first = self.rows(self.run_invoice())[0]
        self.source.write_bytes(original.replace(b"\n", b"\r\n"))
        second = self.rows(self.run_invoice())[0]
        self.assertEqual((first["row_a"], first["row_b"], first["status"]),
                         (second["row_a"], second["row_b"], second["status"]))
        self.assertNotEqual(first["source_sha256"], second["source_sha256"])
        self.assertNotEqual(first["candidate_ref"], second["candidate_ref"])

    def test_file_changed_after_snapshot_does_not_relabel_original_result(self):
        original = b"vendor,invoice_number,amount,date\nACME,X,1,2026-01-01\nACME,X,1,2026-01-02\n"
        changed = original.replace(b"ACME,X,1,2026-01-02", b"BETA,Y,999,2026-01-02")
        self.source.write_bytes(original)
        real_table = engine.table

        def overwrite_after_verified_read(*args, **kwargs):
            parsed = real_table(*args, **kwargs)
            self.source.write_bytes(changed)
            return parsed

        with patch.object(engine, "table", side_effect=overwrite_after_verified_read):
            result = self.rows(self.run_invoice())[0]
        self.assertEqual(result["source_sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(result["amount_a"], "1.00")
        self.assertEqual(result["status"], "exact_invoice_key")
        self.assertNotEqual(result["source_sha256"], hashlib.sha256(changed).hexdigest())

    def test_original_vendor_collision_and_review_flag_remain(self):
        self.source.write_bytes(b"vendor,invoice_number,amount,date\nAcme Inc,N-9,7,2026-01-01\nACMEINC,N9,7,2026-01-02\n")
        row = self.rows(self.run_invoice())[0]
        self.assertIn("normalized_vendor_key_review", row["review_flags"])
        self.assertIn("normalized_invoice_key_review", row["review_flags"])
        self.assertEqual((row["amount_a"], row["amount_b"]), ("7.00", "7.00"))

    def test_near_candidates_get_distinct_identifiers(self):
        self.source.write_bytes(b"vendor,invoice_number,amount,date\nACME,A,1,2026-01-01\nACME,B,1,2026-01-02\nACME,C,1,2026-01-03\n")
        rows = self.rows(self.run_invoice())
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(r["status"] == "review_possible_duplicate" for r in rows))
        self.assertEqual(len({r["candidate_ref"] for r in rows}), 3)
        self.assertEqual({r["source_sha256"] for r in rows}, {hashlib.sha256(self.source.read_bytes()).hexdigest()})

    def test_no_candidate_report_still_has_evidence_columns(self):
        self.source.write_bytes(b"vendor,invoice_number,amount,date\nACME,A,1,2026-01-01\n")
        out = self.run_invoice()
        self.assertEqual(self.rows(out), [])
        with out.open(encoding="utf-8-sig", newline="") as f:
            fields = next(csv.reader(f))
        self.assertEqual(fields[-2:], ["source_sha256", "candidate_ref"])

    def test_invalid_date_aborts_without_partial_report(self):
        self.source.write_bytes(b"vendor,invoice_number,amount,date\nACME,A,1,not-a-date\n")
        with self.assertRaises(ValueError):
            self.run_invoice()
        self.assertFalse(list(self.root.glob("invoice-twins-*.csv")))

    def test_candidate_limit_aborts_without_partial_report(self):
        header = b"vendor,invoice_number,amount,date\n"
        rows = b"".join(f"ACME,INV{i},1,2026-01-01\n".encode("ascii") for i in range(450))
        self.source.write_bytes(header + rows)
        with self.assertRaisesRegex(ValueError, "Too many invoice review candidates"):
            self.run_invoice()
        self.assertFalse(list(self.root.glob("invoice-twins-*.csv")))

    def test_import_requests_digest_from_verified_descriptor_snapshot(self):
        self.source.write_bytes(b"vendor,invoice_number,amount,date\nACME,X,1,2026-01-01\nACME,X,1,2026-01-02\n")
        real_table = engine.table
        with patch.object(engine, "table", wraps=real_table) as spy:
            self.run_invoice()
        self.assertEqual(spy.call_count, 1)
        self.assertTrue(spy.call_args.kwargs.get("include_digest"))


if __name__ == "__main__":
    unittest.main()
