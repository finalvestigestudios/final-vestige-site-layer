"""R72 repository-level privacy regression: real parser/engines, synthetic files."""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine

PRIVATE = "CLIENT_462_PRIVATE_PAYROLL_DO_NOT_LOG"


class CsvImportErrorPrivacyIntegrationR72(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-import-error-r72-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.secret = self.root / (PRIVATE + ".csv")

    def write(self, path, headings, records):
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headings)
            writer.writerows(records)
        return path

    def error_is_private(self, function, phrase):
        with self.assertRaises(ValueError) as raised:
            function()
        message = str(raised.exception)
        self.assertIn(phrase, message)
        self.assertNotIn(PRIVATE, message)
        self.assertNotIn(str(self.root), message)
        self.assertLess(len(message), 200)

    def test_invalid_extension_and_missing_csv_do_not_echo_file_name(self):
        bad = self.root / (PRIVATE + ".txt")
        bad.write_text("id,amount\nA,1\n", encoding="utf-8")
        self.error_is_private(lambda: engine.table(bad, ("id", "amount")), "existing CSV input")
        self.error_is_private(lambda: engine.table(self.secret, ("id", "amount")), "existing CSV input")

    def test_missing_headers_and_bad_utf8_header(self):
        self.secret.write_bytes(b"")
        self.error_is_private(lambda: engine.table(self.secret, ("id", "amount")), "Missing headers")
        self.secret.write_bytes(b"id,am\xffount\nA,1\n")
        self.error_is_private(lambda: engine.table(self.secret, ("id", "amount")), "invalid CSV header")

    def test_duplicate_and_nul_headers(self):
        self.write(self.secret, ("id", "amount", "Amount"), (("A", "10", "20"),))
        self.error_is_private(lambda: engine.table(self.secret, ("id", "amount")), "duplicate normalized CSV header")
        self.write(self.secret, ("id", "amount\x00bad"), (("A", "10"),))
        self.error_is_private(lambda: engine.table(self.secret, ("id", "amount")), "header contains a NUL")

    def test_missing_and_ambiguous_columns(self):
        self.write(self.secret, ("id", "vendor"), (("A", "V"),))
        self.error_is_private(lambda: engine.table(self.secret, ("id", "amount")), "missing 'amount' column")
        self.write(self.secret, ("id", "amount", "paid"), (("A", "10", "10"),))
        self.error_is_private(lambda: engine.table(self.secret, ("id", "amount")), "ambiguous 'amount' aliases")

    def test_malformed_short_row_and_null_cell(self):
        self.write(self.secret, ("id", "amount", "note"), (("A", "10"),))
        self.error_is_private(lambda: engine.table(self.secret, ("id", "amount")),
                              "malformed CSV record at physical line 2")
        self.write(self.secret, ("id", "amount", "note"), (("A", "10", "private\x00data"),))
        self.error_is_private(lambda: engine.table(self.secret, ("id", "amount")),
                              "NUL character at physical line 2")

    def test_unterminated_quote_does_not_echo_csv_name(self):
        self.secret.write_text('id,amount\nA,"123', encoding="utf-8")
        self.error_is_private(lambda: engine.table(self.secret, ("id", "amount")),
                              "invalid CSV near physical line")

    def test_bad_ledger_id_preserves_physical_row_not_name(self):
        self.write(self.secret, ("id", "amount"), (("---", "10"),))
        right = self.write(self.root / "right.csv", ("id", "amount"), (("A", "10"),))
        before = self.secret.read_bytes()
        self.error_is_private(lambda: engine.ledger_diff(self.secret, right, self.root),
                              "Blank transaction ID at physical CSV row 2")
        self.assertEqual(before, self.secret.read_bytes())
        self.assertFalse(list(self.root.glob("ledger-diff-*.csv")))

    def test_invoice_and_spend_file_errors_do_not_echo_private_name(self):
        self.write(self.secret, ("id", "amount"), (("A", "10"),))
        self.error_is_private(lambda: engine.invoice_twins(self.secret, self.root), "missing 'vendor' column")
        self.error_is_private(lambda: engine.spend_map(self.secret, self.root), "missing 'vendor' column")
        self.assertFalse(list(self.root.glob("invoice-twins-*.csv")))
        self.assertFalse(list(self.root.glob("spend-map-*.csv")))

    def test_grant_and_procurement_file_errors_do_not_echo_private_name(self):
        self.write(self.secret, ("id", "amount"), (("A", "10"),))
        unused1 = self.write(self.root / "second.csv", ("id", "amount"), (("A", "10"),))
        unused2 = self.write(self.root / "third.csv", ("id", "amount"), (("A", "10"),))
        self.error_is_private(lambda: engine.grant_audit(self.secret, unused1, unused2, self.root),
                              "missing 'program' column")
        self.error_is_private(lambda: engine.procure_guard(self.secret, unused1, unused2, self.root),
                              "missing 'po_number' column")
        self.assertFalse(list(self.root.glob("evidence-manifest-*.txt")))

    def test_valid_inputs_preserve_bytes_reconciliation_and_sha256(self):
        left = self.write(self.secret, ("id", "amount", "notes"),
                          (("INV-3", "0.10", "a\nsecond"), ("B", "0.20", "text")))
        right = self.write(self.root / "right.csv", ("id", "amount"),
                           (("INV3", "0.10"), ("B", "0.19")))
        original = left.read_bytes()
        output = engine.ledger_diff(left, right, self.root)[0]
        with output.open(encoding="utf-8-sig", newline="") as stream:
            rows = {r["id"]: r for r in csv.DictReader(stream)}
        self.assertEqual(rows["INV3"]["status"], "normalized_id_review")
        self.assertEqual(rows["INV3"]["left_rows"], "2")
        self.assertEqual(rows["B"]["left_rows"], "4")
        self.assertEqual(rows["B"]["difference"], "0.01")
        self.assertEqual(rows["B"]["left_source_sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(left.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
