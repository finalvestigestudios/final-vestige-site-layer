"""R298 full-checkout contract: test real financial engine.table path custody.

Requires the connected repository's complete fvs_suite package. Synthetic CSV
files only; the isolated path-helper tests can also run without a checkout.
"""
from __future__ import annotations

import hashlib
import tempfile
import traceback
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import engine

SECRET = "CUSTOMER_BANK_ACCOUNT_DO_NOT_EXPOSE_R298"


class CsvPathEngineIntegrationR298(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r298-integration-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.csv_path = self.root / (SECRET + ".csv")
        self.csv_path.write_bytes(b"\xef\xbb\xbfid,amount,comment\r\nA,1.20,\"alpha\nbeta\"\r\nB,-0.02,plain\r\n")

    def assert_private(self, callback):
        with self.assertRaises(ValueError) as raised:
            callback()
        error = raised.exception
        self.assertEqual(str(error), "Select an existing CSV input")
        self.assertIsNone(error.__context__)
        self.assertIsNone(error.__cause__)
        self.assertNotIn(SECRET, "".join(traceback.format_exception(error)))

    def test_real_table_handles_permissionerror_without_private_chain(self):
        with patch.object(Path, "is_file", side_effect=PermissionError(13, SECRET, str(self.csv_path))):
            self.assert_private(lambda: engine.table(self.csv_path, ("id", "amount")))

    def test_real_table_handles_generic_oserror_without_private_chain(self):
        with patch.object(Path, "is_file", side_effect=OSError(5, SECRET, str(self.csv_path))):
            self.assert_private(lambda: engine.table(self.csv_path, ("id", "amount")))

    def test_real_table_handles_valueerror_from_preflight_privately(self):
        with patch.object(Path, "is_file", side_effect=ValueError(SECRET)):
            self.assert_private(lambda: engine.table(self.csv_path, ("id", "amount")))

    def test_real_table_handles_pathlike_oserror_privately(self):
        class BadPath:
            def __fspath__(self):
                raise OSError(5, SECRET, "/secret/" + SECRET + ".csv")
        self.assert_private(lambda: engine.table(BadPath(), ("id", "amount")))

    def test_real_table_missing_file_contract_preserved(self):
        self.assert_private(lambda: engine.table(self.root / (SECRET + "_missing.csv"), ("id", "amount")))

    def test_real_table_invalid_extension_contract_preserved(self):
        other = self.root / (SECRET + ".txt")
        other.write_bytes(b"id,amount\nA,1.20\n")
        self.assert_private(lambda: engine.table(other, ("id", "amount")))

    def test_valid_source_retains_digest_decimal_lexemes_and_physical_rows(self):
        before = self.csv_path.read_bytes()
        rows, digest, columns = engine.table(
            self.csv_path, ("id", "amount"), include_digest=True, include_columns=True)
        self.assertEqual(rows, [
            {"row": "2", "id": "A", "amount": "1.20"},
            {"row": "4", "id": "B", "amount": "-0.02"},
        ])
        self.assertEqual(columns, {"id": "id", "amount": "amount"})
        self.assertEqual(digest, hashlib.sha256(before).hexdigest())
        self.assertEqual(self.csv_path.read_bytes(), before)

    def test_valid_source_with_uppercase_extension_remains_supported(self):
        upper = self.root / "LEDGER.CSV"
        upper.write_bytes(b"id,amount\nA,9.99\n")
        self.assertEqual(engine.table(upper, ("id", "amount")),
                         [{"row": "2", "id": "A", "amount": "9.99"}])


if __name__ == "__main__":
    unittest.main()
