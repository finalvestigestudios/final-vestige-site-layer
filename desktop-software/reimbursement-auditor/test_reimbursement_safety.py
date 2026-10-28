"""Fail-closed integration tests for reimbursement decision-support reports."""
import json
import tempfile
import unittest
from pathlib import Path

from reimbursement_auditor import audit, csv_items, html_report
from packet_integrity import write_report


class ReimbursementSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.attachments = self.root / "evidence"
        self.attachments.mkdir()
        (self.attachments / "receipt.pdf").write_bytes(b"%PDF-1.4 fictional")
        self.claims = self.root / "claims.csv"
        self.support = self.root / "support.csv"
        self.claims.write_text(
            "vendor,invoice,amount\nAcme,INV-001,100.00\n",
            encoding="utf-8",
        )
        self.support.write_text(
            "vendor,invoice,amount,file\nAcme,INV-001,100.00,receipt.pdf\n",
            encoding="utf-8",
        )

    def test_valid_report_tracks_file_fingerprints(self):
        result = audit(self.claims, self.support, self.attachments)
        self.assertEqual(result["status"], "NO_FILE_OR_INDEX_EXCEPTIONS")
        self.assertEqual(len(result["snapshot"]["sources"]["claims"]["sha256"]), 64)
        self.assertEqual(len(result["snapshot"]["attachments"]["files"]), 1)

    def test_empty_packet_cannot_pass(self):
        self.claims.write_text("vendor,invoice,amount\n", encoding="utf-8")
        self.support.write_text("vendor,invoice,amount,file\n", encoding="utf-8")
        result = audit(self.claims, self.support, self.attachments)
        codes = {item["code"] for item in result["findings"]}
        self.assertTrue({"EMPTY_CLAIMS", "EMPTY_SUPPORT_INDEX"} <= codes)
        self.assertEqual(result["status"], "INCOMPLETE")

    def test_ambiguous_alias_headers_rejected(self):
        self.claims.write_text(
            "vendor,invoice,invoice number,amount\nAcme,A,A,100.00\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "multiple columns map to invoice"):
            audit(self.claims, self.support, self.attachments)

    def test_repeated_header_rejected(self):
        self.claims.write_text(
            "vendor,invoice,amount,amount\nAcme,A,100.00,100.00\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "repeated CSV headers"):
            audit(self.claims, self.support, self.attachments)

    def test_duplicate_support_reference_flagged(self):
        (self.attachments / "second.pdf").write_bytes(b"%PDF-1.4 second")
        self.support.write_text(
            "vendor,invoice,amount,file\nAcme,INV-001,60.00,receipt.pdf\n"
            "Acme,INV-001,40.00,second.pdf\n",
            encoding="utf-8",
        )
        result = audit(self.claims, self.support, self.attachments)
        self.assertIn("DUPLICATE_SUPPORT_REFERENCE",
                      {item["code"] for item in result["findings"]})
        self.assertEqual(result["status"], "REVIEW")

    def test_extra_file_flagged(self):
        (self.attachments / "extra.pdf").write_bytes(b"%PDF-1.4 extra")
        result = audit(self.claims, self.support, self.attachments)
        self.assertIn("UNINDEXED_ATTACHMENT",
                      {item["code"] for item in result["findings"]})

    def test_invalid_support_row_is_incomplete(self):
        self.support.write_text(
            "vendor,invoice,amount,file\nAcme,INV-001,notmoney,receipt.pdf\n",
            encoding="utf-8",
        )
        result = audit(self.claims, self.support, self.attachments)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("INVALID_SUPPORT_ROW",
                      {item["code"] for item in result["findings"]})

    def test_multiline_csv_records_keep_source_line(self):
        self.claims.write_text(
            'vendor,invoice,amount\n"Acme\nIndustries",INV-001,100.00\n',
            encoding="utf-8",
        )
        self.support.write_text(
            'vendor,invoice,amount,file\n"Acme\nIndustries",INV-001,100.00,receipt.pdf\n',
            encoding="utf-8",
        )
        records, errors = csv_items(self.claims, False)
        self.assertEqual(errors, [])
        self.assertEqual(records[0]["row"], 2)
        self.assertEqual(audit(self.claims, self.support, self.attachments)["finding_count"], 0)

    def test_changes_after_audit_block_report_export(self):
        result = audit(self.claims, self.support, self.attachments)
        (self.attachments / "receipt.pdf").write_bytes(b"tampered")
        destination = self.root / "report.json"
        with self.assertRaisesRegex(ValueError, "changed since analysis"):
            write_report(destination, json.dumps(result), self.claims,
                         self.support, self.attachments, result["snapshot"])
        self.assertFalse(destination.exists())

    def test_report_export_exclusive(self):
        result = audit(self.claims, self.support, self.attachments)
        destination = self.root / "report.html"
        write_report(destination, html_report(result), self.claims, self.support,
                     self.attachments, result["snapshot"])
        with self.assertRaises(FileExistsError):
            write_report(destination, "overwritten", self.claims, self.support,
                         self.attachments, result["snapshot"])


if __name__ == "__main__":
    unittest.main()
