import tempfile
import unittest
from pathlib import Path
from reimbursement_auditor import audit, amount_value, attached_path, html_report


class ReimbursementAuditorTests(unittest.TestCase):
    def test_flag_mismatches_duplicate_claim_missing_attachment(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            attachments = root / "attachments"
            attachments.mkdir()
            (attachments / "invoice-001.pdf").write_bytes(b"pdf")
            claims = root / "claims.csv"
            claims.write_text("vendor,invoice,amount\nVendor A,INV-001,100.00\n"
                              "Vendor A,INV-001,25.00\nVendor B,INV-002,50.00\n", encoding="utf-8")
            index = root / "index.csv"
            index.write_text("vendor,invoice,amount,file\n"
                             "Vendor A,INV-001,110.00,invoice-001.pdf\n"
                             "Vendor B,INV-002,50.00,missing.pdf\n", encoding="utf-8")
            result = audit(claims, index, attachments)
            codes = {r["code"] for r in result["findings"]}
            self.assertIn("DUPLICATE_CLAIM_REFERENCE", codes)
            self.assertIn("AMOUNT_MISMATCH", codes)
            self.assertIn("ATTACHMENT_MISSING", codes)
            self.assertEqual(result["claims"], 3)
            self.assertIn("does not inspect PDFs", result["disclaimer"])

    def test_safe_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for unsafe in ("/etc/passwd", "../secret", "C:/Windows/foo", "one\\two"):
                with self.assertRaises(ValueError):
                    attached_path(root, unsafe)

    def test_valid_no_exceptions(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "invoice.pdf").write_bytes(b"%PDF")
            claims = root / "claims.csv"
            claims.write_text("vendor,invoice,amount\nAcme,INV-002,52.50\n", encoding="utf-8")
            evidence = root / "evidence.csv"
            evidence.write_text("vendor,invoice,amount,file\nAcme,INV002,52.50,invoice.pdf\n", encoding="utf-8")
            result = audit(claims, evidence, root)
            self.assertEqual(result["finding_count"], 0)
            self.assertEqual(result["status"], "NO_FILE_OR_INDEX_EXCEPTIONS")

    def test_reject_nonfinite_amount(self):
        with self.assertRaises(ValueError):
            amount_value("NaN")

    def test_html_escape(self):
        report = {"findings":[{"priority":"HIGH","code":"TEST","claim_rows":[2],
                               "reason":"<script>"}], "disclaimer":"Manual",
                  "claims":1,"finding_count":1}
        self.assertNotIn("<script>", html_report(report))
        self.assertIn("&lt;script&gt;", html_report(report))


if __name__ == "__main__":
    unittest.main()
