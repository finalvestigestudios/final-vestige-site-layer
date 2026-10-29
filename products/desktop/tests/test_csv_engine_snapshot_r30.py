"""R30 integration contracts for the real financial CSV engine (synthetic only).

The isolated snapshot-helper tests are independently runnable; these tests
require the complete connected repository checkout and remain a CI release gate.
"""
import csv
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import engine
from fvs_suite.csv_snapshot import read_csv_snapshot


class FinancialCsvSnapshotIntegrationR30(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, headers, data):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(data)
        return path

    def sources(self, *, linked=False):
        if linked:
            claim_columns = ("claim_id", "amount", "program", "ledger_reference")
            claim_rows = [("C1", "10.00", "G1", "T1")]
            ledger_rows = [("T1", "10.00", "G1")]
        else:
            claim_columns = ("claim_id", "amount", "program")
            claim_rows = [("T1", "10.00", "G1")]
            ledger_rows = [("T1", "10.00", "G1")]
        return (
            self.write("claims.csv", claim_columns, claim_rows),
            self.write("ledger.csv", ("transaction_id", "amount", "program"), ledger_rows),
            self.write("budgets.csv", ("program", "budget"), [("G1", "100.00")]),
        )

    def test_snapshot_csv_header_mapping_and_row_provenance(self):
        claims, _, _ = self.sources(linked=True)
        rows, headers = engine.table(
            claims, ("id", "amount", "program"),
            ("ledger_reference", "claim_type"), include_headers=True)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "C1")
        self.assertEqual(rows[0]["ledger_reference"], "T1")
        self.assertEqual(rows[0]["row"], "2")
        self.assertEqual(headers, {"claim_id", "amount", "program", "ledger_reference"})

    def test_table_preserves_multiline_physical_source_line(self):
        source = self.write(
            "multiline.csv", ("transaction_id", "amount", "note"),
            [("A", "1", "first\nsecond"), ("B", "2", "last")])
        records = engine.table(source, ("id", "amount"))
        self.assertEqual([r["row"] for r in records], ["2", "4"])

    def test_engine_uses_one_snapshot_for_each_csv_parse(self):
        source = self.write("records.csv", ("id", "amount"), [("T1", "1")])
        with patch("fvs_suite.csv_snapshot.read_csv_snapshot", wraps=read_csv_snapshot) as snapshot:
            rows = engine.table(source, ("id", "amount"))
        self.assertEqual(len(rows), 1)
        snapshot.assert_called_once_with(source, engine.MAX_IMPORT_BYTES)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlinked_financial_input_rejected_before_report(self):
        source = self.write("original.csv", ("id", "amount"), [("T1", "1")])
        linked = self.root / "linked.csv"
        try:
            linked.symlink_to(source)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        second = self.write("other.csv", ("id", "amount"), [("T1", "1")])
        with self.assertRaisesRegex(ValueError, "regular file"):
            engine.ledger_diff(linked, second, self.root)
        self.assertEqual(list(self.root.glob("ledger-diff-*.csv")), [])

    def test_grant_linked_mode_survives_single_header_snapshot(self):
        paths = self.sources(linked=True)
        reports = engine.grant_audit(*paths, self.root)
        self.assertEqual(len(reports), 3)
        self.assertTrue(all(path.is_file() for path in reports))
        with reports[0].open(encoding="utf-8-sig", newline="") as stream:
            data = list(csv.DictReader(stream))
        self.assertIn("ledger_reference_labels", data[0])
        self.assertIn("T1", data[0]["ledger_reference_labels"])

    def test_grant_legacy_mode_survives_single_header_snapshot(self):
        paths = self.sources(linked=False)
        reports = engine.grant_audit(*paths, self.root)
        self.assertEqual(len(reports), 3)
        self.assertTrue(all(path.is_file() for path in reports))
        with reports[0].open(encoding="utf-8-sig", newline="") as stream:
            data = list(csv.DictReader(stream))
        self.assertEqual(data[0]["claim_amount"], "10.00")

    def test_grant_never_reopens_claim_csv_header_after_validation(self):
        paths = self.sources(linked=False)
        original_open = Path.open
        def forbid_claim_reopen(path, *args, **kwargs):
            if Path(path) == paths[0]:
                raise AssertionError("Grant claim CSV was reopened after snapshot")
            return original_open(path, *args, **kwargs)
        with patch.object(Path, "open", forbid_claim_reopen):
            reports = engine.grant_audit(*paths, self.root)
        self.assertEqual(len(reports), 3)


if __name__ == "__main__":
    unittest.main()
