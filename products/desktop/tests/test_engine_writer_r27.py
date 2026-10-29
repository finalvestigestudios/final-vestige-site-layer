"""R27 integration checks for the shared financial report output path."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import engine


class EngineAtomicWriterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_engine_save_keeps_spreadsheet_formula_protection(self):
        report = engine.save(self.root, "ledger-test", ("key", "amount"), [
            {"key": "=2+2", "amount": "-4.00"}])
        with report.open(encoding="utf-8-sig", newline="") as stream:
            record = next(csv.DictReader(stream))
        self.assertEqual(record["key"], "'=2+2")
        self.assertEqual(record["amount"], "-4.00")
        self.assertFalse(list(self.root.glob("*.partial")))
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_engine_save_never_overwrites_same_report_name(self):
        target = self.root / "ledger-diff-fixed.csv"
        target.write_bytes(b"existing audit evidence")
        with patch("fvs_suite.engine.outpath", return_value=target):
            with self.assertRaises(FileExistsError):
                engine.save(self.root, "ledger-diff", ("key",), [{"key": "new"}])
        self.assertEqual(target.read_bytes(), b"existing audit evidence")

    def test_engine_save_never_exposes_partial_on_bad_cell(self):
        class InvalidCell:
            def __str__(self):
                raise ValueError("synthetic invalid field")
        target = self.root / "bad.csv"
        with patch("fvs_suite.engine.outpath", return_value=target):
            with self.assertRaises(ValueError):
                engine.save(self.root, "bad", ("key",), [{"key": InvalidCell()}])
        self.assertFalse(target.exists())
        self.assertFalse(list(self.root.glob(".*.partial")))


if __name__ == "__main__":
    unittest.main()
