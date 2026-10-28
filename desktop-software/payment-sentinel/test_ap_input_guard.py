import tempfile
import unittest
from pathlib import Path

from ap_input_guard import (
    MAX_SOURCE_BYTES,
    normalize_search_key,
    resolve_headers,
    source_fingerprint,
)

ALIASES = {
    "amount": {"amount", "payment amount", "paid amount"},
    "vendor": {"vendor", "supplier", "payee"},
    "date": {"date", "payment date"},
}


class APInputGuardTests(unittest.TestCase):
    def test_unicode_vendor_key_keeps_non_ascii_characters(self):
        self.assertEqual(normalize_search_key("MÜLLER & SÖHNE"), "müllersöhne")
        self.assertEqual(normalize_search_key("株式会社"), "株式会社")
        self.assertEqual(normalize_search_key("ＡＢＣ-１２"), "abc12")

    def test_ambiguous_amount_columns_rejected(self):
        with self.assertRaisesRegex(ValueError, "Ambiguous amount"):
            resolve_headers(["Vendor", "Amount", "Payment Amount", "Date"], ALIASES,
                            {"vendor", "amount", "date"})

    def test_duplicate_casefold_headers_rejected(self):
        with self.assertRaisesRegex(ValueError, "Repeated CSV column"):
            resolve_headers(["Vendor", " vendor ", "Amount", "Date"], ALIASES,
                            {"vendor", "amount", "date"})

    def test_blank_and_missing_headers_rejected(self):
        with self.assertRaisesRegex(ValueError, "blank"):
            resolve_headers(["Vendor", "", "Amount", "Date"], ALIASES,
                            {"vendor", "amount", "date"})
        with self.assertRaisesRegex(ValueError, "Missing required"):
            resolve_headers(["Vendor", "Amount"], ALIASES, {"vendor", "amount", "date"})

    def test_unambiguous_alias_mapping(self):
        self.assertEqual(resolve_headers([" Supplier ", "Paid Amount", "Payment Date"],
                                         ALIASES, {"vendor", "amount", "date"}),
                         {"vendor": " Supplier ", "amount": "Paid Amount", "date": "Payment Date"})

    def test_source_fingerprint_and_change(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "pay.csv"
            path.write_bytes(b"vendor,amount\\nA,10\\n")
            first = source_fingerprint(path)
            self.assertEqual(first["bytes"], len(path.read_bytes()))
            self.assertEqual(len(first["sha256"]), 64)
            self.assertEqual(first, source_fingerprint(path))
            path.write_bytes(b"vendor,amount\\nB,12\\n")
            self.assertNotEqual(first["sha256"], source_fingerprint(path)["sha256"])

    def test_directory_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "file"):
                source_fingerprint(Path(temporary))


if __name__ == "__main__":
    unittest.main()
