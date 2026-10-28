import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from renewal_radar import (
    add_entry, delete_entry, entries, export_ics, import_csv, next_occurrence,
    open_store, parse_due, render_ical,
)


class RenewalRadarTests(unittest.TestCase):
    def test_create_list_delete_and_export(self):
        with tempfile.TemporaryDirectory() as d:
            conn = open_store(Path(d) / "data.sqlite")
            ident = add_entry(conn, "Annual certificate", "2026-11-12", "Business", "yearly", 21)
            rows = entries(conn, date(2026, 10, 27))
            self.assertEqual(rows[0]["days_remaining"], 16)
            self.assertEqual(rows[0]["title"], "Annual certificate")
            ics = Path(d) / "calendar.ics"
            self.assertEqual(export_ics(conn, ics), 1)
            text = ics.read_text(encoding="utf-8")
            self.assertIn("BEGIN:VALARM", text)
            self.assertIn("TRIGGER:-P21D", text)
            self.assertIn("RRULE:FREQ=YEARLY", text)
            self.assertTrue(delete_entry(conn, ident))
            self.assertEqual(entries(conn), [])
            conn.close()

    def test_recurrence_skips_impossible_months(self):
        self.assertEqual(
            next_occurrence(date(2026, 1, 31), "monthly", date(2026, 2, 1)),
            date(2026, 3, 31),
        )
        self.assertEqual(
            next_occurrence(date(2024, 2, 29), "yearly", date(2025, 1, 1)),
            date(2028, 2, 29),
        )

    def test_validation_rejects_bad_dates_and_negative_reminder(self):
        with tempfile.TemporaryDirectory() as d:
            conn = open_store(Path(d) / "db.sqlite")
            with self.assertRaises(ValueError):
                add_entry(conn, "Bad", "2026-02-30")
            with self.assertRaises(ValueError):
                add_entry(conn, "Bad", "2026-11-30", remind_days=-4)

    def test_csv_bulk_import_reports_bad_rows(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            conn = open_store(root / "db.sqlite")
            csv = root / "import.csv"
            csv.write_text("title,due,cadence,remind_days\nLicense,2027-05-04,yearly,30\nBad,wrong,none,15\n",
                           encoding="utf-8")
            result = import_csv(conn, csv)
            self.assertEqual(result["inserted"], 1)
            self.assertEqual(len(result["problems"]), 1)
            self.assertEqual(len(entries(conn)), 1)

    def test_ical_escaping(self):
        row = {"id": 1, "title": "Test; comma, newline\n", "category": "", "notes": "",
               "due": "2026-12-31", "cadence": "none", "remind_days": 5}
        output = render_ical([row])
        self.assertIn(r"SUMMARY:Test\; comma\, newline\n", output)
        self.assertIn("\r\n", output)


if __name__ == "__main__":
    unittest.main()
