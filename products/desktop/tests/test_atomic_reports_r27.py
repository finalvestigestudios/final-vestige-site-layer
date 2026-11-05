"""R27 offline CSV publication regression tests (no customer data)."""
import csv
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.atomic_reports import write_csv_report


class AtomicReportsTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.output = self.root / "evidence.csv"

    def publish(self, rows, fields=("id", "amount"), cell=str):
        return write_csv_report(self.output, fields, rows, cell)

    def assert_no_partials(self):
        self.assertFalse(list(self.root.glob("*.partial")))
        self.assertFalse(list(self.root.glob(".*.partial")))

    def test_csv_roundtrip_bom_unicode_and_physical_lines(self):
        self.assertEqual(self.publish([{"id": "é\nsecond line", "amount": "2.00"}]), self.output)
        self.assertTrue(self.output.read_bytes().startswith(b"\xef\xbb\xbf"))
        with self.output.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows, [{"id": "é\nsecond line", "amount": "2.00"}])
        self.assert_no_partials()

    def test_existing_report_never_overwritten(self):
        self.output.write_bytes(b"original")
        with self.assertRaises(FileExistsError):
            self.publish([{"id": "A", "amount": "100"}])
        self.assertEqual(self.output.read_bytes(), b"original")
        self.assert_no_partials()

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_existing_output_symlink_never_replaced_or_followed(self):
        private = self.root / "private.txt"
        private.write_bytes(b"private")
        self.output.symlink_to(private)
        with self.assertRaises(FileExistsError):
            self.publish([{"id": "A", "amount": "1"}])
        self.assertEqual(private.read_bytes(), b"private")
        self.assertTrue(self.output.is_symlink())
        self.assert_no_partials()

    def test_failed_row_generator_never_publishes_incomplete_report(self):
        def data():
            yield {"id": "A", "amount": "1"}
            raise ValueError("sensitive sample value")
        with self.assertRaisesRegex(ValueError, "sensitive sample value"):
            self.publish(data())
        self.assertFalse(self.output.exists())
        self.assert_no_partials()

    def test_failed_cell_conversion_never_publishes_report(self):
        def convert(value):
            if value == "BAD":
                raise ValueError("invalid value")
            return str(value)
        with self.assertRaises(ValueError):
            self.publish([{"id": "A", "amount": "BAD"}], cell=convert)
        self.assertFalse(self.output.exists())
        self.assert_no_partials()

    def test_fsync_failure_removes_staging_file(self):
        with patch("fvs_suite.atomic_reports.os.fsync", side_effect=OSError("full disk")):
            with self.assertRaises(OSError):
                self.publish([{"id": "A", "amount": "3"}])
        self.assertFalse(self.output.exists())
        self.assert_no_partials()

    def test_publish_failure_removes_staging_file(self):
        function = "os.rename" if os.name == "nt" else "os.link"
        with patch("fvs_suite.atomic_reports." + function, side_effect=OSError("unsupported filesystem")):
            with self.assertRaises(OSError):
                self.publish([{"id": "A", "amount": "3"}])
        self.assertFalse(self.output.exists())
        self.assert_no_partials()

    def test_missing_output_folder_rejected_without_side_effects(self):
        with self.assertRaises(ValueError):
            write_csv_report(self.root / "missing" / "report.csv", ("x",), [{"x": "1"}], str)
        self.assert_no_partials()

    def test_extra_columns_ignored_and_cell_called_as_before(self):
        visited = []
        def cell(value):
            visited.append(value)
            return str(value)
        self.publish([{"id": "A", "amount": "4", "unused": "private"}], cell=cell)
        # R207: header cells are sanitized before any data cells.
        self.assertEqual(visited, ["id", "amount", "A", "4", "private"])
        with self.output.open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream)), [{"id": "A", "amount": "4"}])

    def test_can_write_large_lazy_generator(self):
        generated = 0
        def records():
            nonlocal generated
            for i in range(5000):
                generated += 1
                yield {"id": str(i), "amount": "0.01"}
        self.publish(records())
        self.assertEqual(generated, 5000)
        with self.output.open(encoding="utf-8-sig") as stream:
            self.assertEqual(sum(1 for _ in stream), 5001)
        self.assert_no_partials()

    @unittest.skipIf(os.name == "nt", "POSIX mode check")
    def test_financial_report_private_permissions_posix(self):
        self.publish([{"id": "A", "amount": "100"}])
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o600)


if __name__ == "__main__":
    unittest.main()
