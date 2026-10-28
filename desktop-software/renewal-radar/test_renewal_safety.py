import sqlite3
import tempfile
import unittest
from pathlib import Path

from renewal_safety import import_csv_atomic, write_new_file


def db():
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE renewal (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                 'title TEXT NOT NULL, category TEXT NOT NULL DEFAULT "", '
                 'due TEXT NOT NULL, cadence TEXT NOT NULL DEFAULT "none", '
                 'remind_days INTEGER NOT NULL DEFAULT 30, notes TEXT NOT NULL DEFAULT "")')
    return conn


class SafetyTests(unittest.TestCase):
    def test_valid_import_then_repeat_rejected_no_duplicates(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'test.csv'
            csv.write_text('title,due,cadence,remind_days\nLicense,2027-05-04,yearly,0\n', encoding='utf-8')
            conn = db()
            self.assertEqual(import_csv_atomic(conn, csv)['inserted'], 1)
            repeat = import_csv_atomic(conn, csv)
            self.assertEqual(repeat['inserted'], 0)
            self.assertEqual(len(repeat['problems']), 1)
            self.assertEqual(conn.execute('SELECT count(*) FROM renewal').fetchone()[0], 1)
            self.assertEqual(conn.execute('SELECT remind_days FROM renewal').fetchone()[0], 0)

    def test_bad_row_aborts_entire_file(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'test.csv'
            csv.write_text('title,due\nGood,2027-05-04\nBroken,2027-02-30\n', encoding='utf-8')
            conn = db()
            result = import_csv_atomic(conn, csv)
            self.assertEqual(result['inserted'], 0)
            self.assertEqual(result['problems'][0]['row'], 3)
            self.assertEqual(conn.execute('SELECT count(*) FROM renewal').fetchone()[0], 0)

    def test_duplicate_file_row_aborts_entire_file(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'test.csv'
            csv.write_text('title,due\nA,2027-05-04\na,2027-05-04\n', encoding='utf-8')
            result = import_csv_atomic(db(), csv)
            self.assertEqual(result['inserted'], 0)
            self.assertEqual(result['problems'][0]['row'], 3)

    def test_csv_multiline_problem_references_physical_start_line(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'test.csv'
            csv.write_text('title,due,notes\n"First\nline",2027-05-04,hello\nBroken,not-a-date,hello\n', encoding='utf-8')
            result = import_csv_atomic(db(), csv)
            self.assertEqual(result['inserted'], 0)
            self.assertEqual(result['problems'][0]['row'], 4)

    def test_duplicate_header_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'test.csv'
            csv.write_text('title,title,due\nA,A,2027-05-04\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                import_csv_atomic(db(), csv)

    def test_unknown_column_rejected_without_silent_loss(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'test.csv'
            csv.write_text('title,due,social_security_number\nA,2027-05-04,123\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                import_csv_atomic(db(), csv)

    def test_extra_cells_not_discarded(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'test.csv'
            csv.write_text('title,due\nA,2027-05-04,EXTRA\n', encoding='utf-8')
            result = import_csv_atomic(db(), csv)
            self.assertEqual(result['inserted'], 0)
            self.assertEqual(result['problems'][0]['row'], 2)

    def test_failed_sql_insert_rolls_back_batch(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'test.csv'
            csv.write_text('title,due\nA,2027-05-04\nB,2027-05-05\n', encoding='utf-8')
            conn = db()
            conn.execute("CREATE TRIGGER deny_b BEFORE INSERT ON renewal WHEN NEW.title='B' BEGIN SELECT RAISE(ABORT,'denied'); END;")
            with self.assertRaises(sqlite3.IntegrityError):
                import_csv_atomic(conn, csv)
            self.assertEqual(conn.execute('SELECT count(*) FROM renewal').fetchone()[0], 0)

    def test_existing_export_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'calendar.ics'
            out.write_bytes(b'original')
            with self.assertRaises(FileExistsError):
                write_new_file(out, b'replacement')
            self.assertEqual(out.read_bytes(), b'original')

    def test_new_export_writes_full_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'calendar.ics'
            data = b'BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n'
            write_new_file(out, data)
            self.assertEqual(out.read_bytes(), data)

    def test_csv_file_size_guard(self):
        with tempfile.TemporaryDirectory() as d:
            csv = Path(d) / 'test.csv'
            with csv.open('wb') as f:
                f.truncate(8 * 1024 * 1024 + 1)
            with self.assertRaises(ValueError):
                import_csv_atomic(db(), csv)


if __name__ == '__main__':
    unittest.main()
