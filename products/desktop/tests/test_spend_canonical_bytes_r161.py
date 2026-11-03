"""R161 synthetic local-first native SpendMap byte-identity regressions."""
import contextlib
import csv
import hashlib
import io
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine
from fvs_suite.spend_evidence_verify import main, verify_membership
from fvs_suite.spend_report_envelope import COLUMNS, NativeSpendCsvDigest


class SpendNativeBytesR161(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r161-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "source.csv"

    @staticmethod
    def row(vendor="Acme", amount="10.00", month=1, category="Parts", note=""):
        return (vendor, amount, f"2026-{month:02d}-01", category, note)

    def build(self, rows=None):
        if rows is None:
            rows = [self.row()]
        with self.source.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(("vendor", "amount", "date", "category", "note"))
            w.writerows(rows)
        self.original = self.source.read_bytes()
        self.report = Path(engine.spend_map(self.source, self.root)[0])
        raw = self.report.read_bytes()
        receipt = verify_membership(self.source, self.report)
        self.assertEqual(receipt.report_sha256, hashlib.sha256(raw).hexdigest())
        self.assertEqual(self.source.read_bytes(), self.original)
        return raw

    def hold(self, tampered):
        self.report.write_bytes(tampered)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(self.report.read_bytes(), tampered)

    def test_native_single_bucket(self):
        self.assertTrue(self.build().startswith(b"\xef\xbb\xbfvendor_key,"))

    def test_native_multi_vendor_month_sort(self):
        self.build([self.row("Zulu", month=3), self.row("Acme", month=1),
                    self.row("Acme", month=2)])

    def test_native_quoted_comma_category(self):
        self.build([self.row(category='R&D, "special"')])

    def test_native_formula_category(self):
        self.build([self.row(category="=SUM(1,2)")])

    def test_native_invisible_prefix_category(self):
        self.build([self.row(category="\u200bServices")])

    def test_native_unicode_values(self):
        self.build([self.row(vendor="München", category="Résumé")])

    def test_native_credit_offsets(self):
        self.build([self.row(amount="140.00"), self.row(amount="-139.99")])

    def test_native_multiline_source(self):
        self.build([self.row(note="a\nb"), self.row(month=2)])

    def test_streaming_canonical_digest_matches_report(self):
        raw = self.build()
        with self.report.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        native = NativeSpendCsvDigest()
        for row in rows:
            native.add_row(row)
        self.assertEqual(native.byte_length, len(raw))
        self.assertTrue(native.matches(raw))

    def test_streaming_digest_rejects_wrong_length(self):
        raw = self.build()
        native = NativeSpendCsvDigest()
        self.assertFalse(native.matches(raw))

    def test_trailing_blank_record_rejected(self):
        raw = self.build()
        self.hold(raw + b"\r\n")

    def test_multiple_trailing_blank_records_rejected(self):
        raw = self.build()
        self.hold(raw + b"\r\n\r\n")

    def test_blank_record_after_header_rejected(self):
        raw = self.build()
        self.hold(raw.replace(b"\r\n", b"\r\n\r\n", 1))

    def test_blank_record_between_data_rejected(self):
        raw = self.build([self.row(month=1), self.row(month=2)])
        pos = raw.find(b"\r\n", raw.find(b"\r\n") + 2)
        self.assertGreater(pos, 0)
        self.hold(raw[:pos + 2] + b"\r\n" + raw[pos + 2:])

    def test_all_lf_records_rejected(self):
        raw = self.build()
        self.hold(raw.replace(b"\r\n", b"\n"))

    def test_all_cr_records_rejected(self):
        raw = self.build()
        self.hold(raw.replace(b"\r\n", b"\r"))

    def test_mixed_first_lf_record_rejected(self):
        raw = self.build()
        self.hold(raw.replace(b"\r\n", b"\n", 1))

    def test_mixed_last_lf_record_rejected(self):
        raw = self.build()
        self.hold(raw[:-2] + b"\n")

    def test_missing_final_crlf_rejected(self):
        raw = self.build()
        self.assertTrue(raw.endswith(b"\r\n"))
        self.hold(raw[:-2])

    def test_missing_bom_rejected(self):
        raw = self.build()
        self.hold(raw[3:])

    def test_duplicate_bom_rejected(self):
        raw = self.build()
        self.hold(b"\xef\xbb\xbf" + raw)

    def test_quote_all_fields_rejected(self):
        self.build()
        with self.report.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        f = io.StringIO(newline="")
        writer = csv.DictWriter(f, fieldnames=COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
        self.hold(f.getvalue().encode("utf-8-sig"))

    def test_extra_quote_around_first_header_rejected(self):
        raw = self.build()
        self.hold(raw.replace(b"vendor_key,", b'"vendor_key",', 1))

    def test_extra_quote_around_vendor_cell_rejected(self):
        raw = self.build()
        self.assertIn(b"ACME,", raw)
        self.hold(raw.replace(b"ACME,", b'"ACME",', 1))

    def test_cli_error_redacts_source_content(self):
        raw = self.build([self.row(vendor="PRIVATESYNTHETIC")])
        self.report.write_bytes(raw + b"\r\n")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            result = main(["--source", str(self.source), "--report", str(self.report)])
        self.assertEqual(result, 1)
        self.assertIn("HOLD", err.getvalue())
        self.assertNotIn("PRIVATESYNTHETIC", out.getvalue()+err.getvalue())
        self.assertNotIn(str(self.root), out.getvalue()+err.getvalue())

    def test_rejected_report_never_edits_source(self):
        raw = self.build()
        self.hold(raw + b"\r\n")
        self.assertEqual(self.source.read_bytes(), self.original)


if __name__ == "__main__":
    unittest.main()
