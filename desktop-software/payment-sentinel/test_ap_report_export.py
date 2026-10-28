import csv
import io
import tempfile
import unittest
from pathlib import Path

from ap_report_export import REPORT_COLUMNS, excel_safe, render_csv, save_report


class ReportExportTests(unittest.TestCase):
    @staticmethod
    def report(reason="Possible duplicate"):
        return {"source_sha256": "a" * 64, "status": "REVIEW", "records_reviewed": 2,
                "rows_excluded": 0, "flags": [{"severity": "HIGH", "rule": "DUPLICATE",
                "rows": [2, 3], "reason": reason, "status": "REVIEW"}]}

    def test_filterable_csv_roundtrip(self):
        values = list(csv.DictReader(io.StringIO(render_csv(self.report()))))
        self.assertEqual(len(values), 1)
        self.assertEqual(list(values[0]), list(REPORT_COLUMNS))
        self.assertEqual(values[0]["source_csv_lines"], "2;3")
        self.assertEqual(values[0]["source_sha256"], "a" * 64)

    def test_formula_injection_neutralized(self):
        for dangerous in ("=HYPERLINK(\"evil\")", "+SUM(1)", "-CMD", "@SUM(1)",
                          " \t=SUM(1)", "\t=1", "\n=1"):
            with self.subTest(value=dangerous):
                cell = excel_safe(dangerous)
                self.assertTrue(cell.startswith("'"))
                row = list(csv.DictReader(io.StringIO(render_csv(self.report(dangerous)))))[0]
                self.assertTrue(row["reason"].startswith("'"))

    def test_zero_flags_still_exports_review_status(self):
        result = self.report()
        result["flags"] = []
        result["status"] = "INCOMPLETE"
        rows = list(csv.DictReader(io.StringIO(render_csv(result))))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["review_status"], "INCOMPLETE")
        self.assertEqual(rows[0]["reason"], "No exception flags")

    def test_no_source_file_overwrite_and_existing_output_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "pay.csv"
            source.write_text("payment data", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source CSV"):
                save_report(source, source, self.report(), lambda r: "<html/>")
            self.assertEqual(source.read_text(), "payment data")
            destination = Path(temporary) / "report.csv"
            save_report(destination, source, self.report(), lambda r: "<html/>")
            before = destination.read_bytes()
            with self.assertRaises(FileExistsError):
                save_report(destination, source, self.report(), lambda r: "<html/>")
            self.assertEqual(destination.read_bytes(), before)

    def test_report_formats_and_bad_suffix(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = folder / "pay.csv"
            source.write_text("sample", encoding="utf-8")
            for suffix in (".html", ".json", ".csv"):
                target = folder / ("review" + suffix)
                save_report(target, source, self.report(), lambda r: "<html>safe</html>")
                self.assertTrue(target.is_file())
                self.assertGreater(target.stat().st_size, 10)
            with self.assertRaisesRegex(ValueError, "Choose"):
                save_report(folder / "review.exe", source, self.report(), lambda r: "<html/>")


if __name__ == "__main__":
    unittest.main()
