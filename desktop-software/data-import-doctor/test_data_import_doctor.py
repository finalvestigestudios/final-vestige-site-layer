import json
import tempfile
import unittest
from pathlib import Path
from data_import_doctor import analyze, valid_type, load_schema


class DataImportDoctorTests(unittest.TestCase):
    def make(self, directory, csv_data, schema):
        root = Path(directory)
        csv_file = root / "input.csv"
        config_file = root / "config.json"
        csv_file.write_text(csv_data, encoding="utf-8")
        config_file.write_text(json.dumps(schema), encoding="utf-8")
        return csv_file, config_file

    def test_detects_duplicate_key_types_blank_and_mismatched_row(self):
        with tempfile.TemporaryDirectory() as d:
            csv_path, schema = self.make(d,
                "id,amount,date,status\nA1,12.50,2026-10-27,open\nA1,broken,2026-02-30,unknown\n,2.00,2026-01-01,open\nA4,1,2026-01-01\n",
                {"required_columns":["id","amount"],"keys":["id"],
                 "types":{"amount":"decimal","date":"date"},
                 "allowed_values":{"status":["open","closed"]}})
            result = analyze(csv_path, schema)
            found = result["issue_counts"]
            for name in ("duplicate_key", "invalid_type", "invalid_allowed_value",
                         "blank_key", "blank_required_value", "column_count_mismatch"):
                self.assertIn(name, found)
            self.assertEqual(result["row_count"], 4)
            self.assertEqual(result["status"], "ISSUES")

    def test_clean_bom_semicolon_data(self):
        with tempfile.TemporaryDirectory() as d:
            csv_path, schema = self.make(d, "\ufeffid;amount\nA;3.50\nB;4.25\n",
                                         {"keys":["id"],"types":{"amount":"decimal"}})
            result = analyze(csv_path, schema)
            self.assertEqual(result["delimiter"], ";")
            self.assertEqual(result["issue_counts"], {})
            self.assertEqual(result["row_count"], 2)

    def test_duplicate_header_case_insensitive(self):
        with tempfile.TemporaryDirectory() as d:
            csv_path, schema = self.make(d, "A,a\nx,y\n", {})
            self.assertIn("duplicate_header", analyze(csv_path, schema)["issue_counts"])

    def test_schema_rejects_unsupported_type(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "schema.json"
            p.write_text('{"types":{"amount":"float-eval"}}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_schema(p)

    def test_decimal_nan_rejected(self):
        self.assertFalse(valid_type("NaN", "decimal"))
        self.assertFalse(valid_type("Infinity", "decimal"))
        self.assertTrue(valid_type("-12.25", "decimal"))

    def test_missing_column(self):
        with tempfile.TemporaryDirectory() as d:
            csv_path, schema = self.make(d, "id\nA\n", {"required_columns":["invoice"]})
            self.assertIn("missing_required_column", analyze(csv_path, schema)["issue_counts"])


if __name__ == "__main__":
    unittest.main()
