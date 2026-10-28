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
            self.assertEqual(result["inserted"], 0)
            self.assertEqual(len(result["problems"]), 1)
            self.assertEqual(len(entries(conn)), 0)

    def test_export_never_overwrites_existing_calendar(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            conn = open_store(root / "db.sqlite")
            add_entry(conn, "License", "2027-01-01")
            calendar = root / "existing.ics"
            calendar.write_bytes(b"KEEP-MY-DATA")
            with self.assertRaises(FileExistsError):
                export_ics(conn, calendar)
            self.assertEqual(calendar.read_bytes(), b"KEEP-MY-DATA")
            # The database itself is also protected from accidental selection.
            with self.assertRaises(FileExistsError):
                export_ics(conn, root / "db.sqlite")
            self.assertEqual(len(entries(conn)), 1)
            conn.close()

    def test_ical_escaping(self):
        row = {"id": 1, "title": "Test; comma, newline\n", "category": "", "notes": "",
               "due": "2026-12-31", "cadence": "none", "remind_days": 5}
        output = render_ical([row])
        self.assertIn(r"SUMMARY:Test\; comma\, newline\n", output)
        self.assertIn("\r\n", output)

    def test_calendar_folds_long_unicode_titles_and_notes(self):
        row = {"id": 3, "title": "Résumé " + "🗓️" * 80, "category": "",
               "notes": "Long notes " + "é" * 500, "due": "2027-04-15",
               "cadence": "none", "remind_days": 14}
        output = render_ical([row])
        lines = [line for line in output.split("\r\n") if line]
        self.assertTrue(all(len(line.encode("utf-8")) <= 75 for line in lines))
        logical = []
        for line in lines:
            if line.startswith(" "):
                logical[-1] += line[1:]
            else:
                logical.append(line)
        self.assertIn("SUMMARY:Résumé " + "🗓️" * 80, logical)
        self.assertIn("END:VCALENDAR", logical)

    def test_latest_possible_date_does_not_overflow(self):
        row = {"id": 10, "title": "Very distant", "category": "",
               "notes": "", "due": "9999-12-31", "cadence": "none", "remind_days": 0}
        result = render_ical([row])
        self.assertIn("DTSTART;VALUE=DATE:99991231", result)
        self.assertNotIn("DTEND;VALUE=DATE:", result)



if __name__ == "__main__":
    unittest.main()
