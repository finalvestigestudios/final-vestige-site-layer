"""R134 Invoice Twin Scout configurable near-match window: real synthetic CSV integration."""
from __future__ import annotations

import csv
import hashlib
import inspect
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine, app
from scripts import native_keyboard_probe_r106 as keyboard
from scripts import native_scale_probe_r107 as scaling


class InvoiceWindowR134(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-invoice-window-r134-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.path = self.root / "synthetic-invoices.csv"

    def source(self, entries):
        with self.path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "invoice_number", "amount", "date"))
            writer.writerows(entries)
        return self.path

    def rows(self, *, window_days=7):
        output = engine.invoice_twins(self.path, self.root, window_days=window_days)[0]
        with output.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            return list(reader), tuple(reader.fieldnames)

    def test_window_parser_accepts_canonical_limits(self):
        self.assertEqual([engine.invoice_window_days(x) for x in ("0", "7", "365")],
                         [0, 7, 365])

    def test_window_parser_rejects_malformed(self):
        for bad in ("", "-1", "+1", "01", "1.0", "366", "1e2", "0x10",
                    "NaN", "Infinity", "٤", "\u200b7", "7\n", "7 "):
            with self.subTest(kind=type(bad).__name__, size=len(bad)):
                with self.assertRaises(ValueError):
                    engine.invoice_window_days(bad)

    def test_window_parser_rejects_nontext(self):
        for bad in (None, False, True, 7, 7.0, b"7", "9" * 2048):
            with self.subTest(kind=type(bad).__name__):
                with self.assertRaises(ValueError):
                    engine.invoice_window_days(bad)

    def test_zero_day_window_same_day_candidate(self):
        self.source([("ACME", "A", "1.00", "2026-01-01"),
                     ("ACME", "B", "1", "2026-01-01")])
        rows, _ = self.rows(window_days=0)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "review_possible_duplicate")
        self.assertEqual(rows[0]["review_window_days"], "0")

    def test_zero_day_window_rejects_next_day(self):
        self.source([("ACME", "A", "1", "2026-01-01"),
                     ("ACME", "B", "1", "2026-01-02")])
        rows, _ = self.rows(window_days=0)
        self.assertEqual(rows, [])

    def test_default_seven_day_window(self):
        self.source([("ACME", "A", "1", "2026-01-01"),
                     ("ACME", "B", "1", "2026-01-08"),
                     ("ACME", "C", "1", "2026-01-09")])
        rows, _ = self.rows()
        pairs = {(r["row_a"], r["row_b"]) for r in rows}
        self.assertIn(("2", "3"), pairs)
        self.assertNotIn(("2", "4"), pairs)
        self.assertTrue(all(r["review_window_days"] == "7" for r in rows))

    def test_custom_fourteen_day_window(self):
        self.source([("ACME", "A", "1", "2026-01-01"),
                     ("ACME", "B", "1", "2026-01-09")])
        first, _ = self.rows(window_days=7)
        second, _ = self.rows(window_days=14)
        self.assertEqual(first, [])
        self.assertEqual(len(second), 1)
        self.assertIn("within 14 days", second[0]["reason"])

    def test_365_day_boundary(self):
        self.source([("ACME", "A", "1", "2025-01-01"),
                     ("ACME", "B", "1", "2026-01-01"),
                     ("ACME", "C", "1", "2026-01-02")])
        rows, _ = self.rows(window_days=365)
        pairs = {frozenset((r["row_a"], r["row_b"])) for r in rows}
        self.assertIn(frozenset(("2", "3")), pairs)
        self.assertNotIn(frozenset(("2", "4")), pairs)

    def test_exact_anchor_survives_zero_window(self):
        self.source([("ACME", "X-1", "1", "2026-01-01"),
                     ("ACME", "X1", "2", "2026-12-31")])
        rows, _ = self.rows(window_days=0)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "exact_invoice_key")
        self.assertIn("amount_variance_review", rows[0]["review_flags"])

    def test_distant_dates_review_tracks_chosen_window(self):
        self.source([("ACME", "X1", "1", "2026-01-01"),
                     ("ACME", "X-1", "1", "2026-01-11")])
        short, _ = self.rows(window_days=7)
        long, _ = self.rows(window_days=14)
        self.assertIn("distant_dates_review", short[0]["review_flags"])
        self.assertNotIn("distant_dates_review", long[0]["review_flags"])

    def test_report_declares_window_even_for_exact(self):
        self.source([("ACME", "X", "1", "2026-01-01"),
                     ("ACME", "X", "1", "2026-01-03")])
        rows, fields = self.rows(window_days=0)
        self.assertEqual(rows[0]["review_window_days"], "0")
        self.assertEqual(fields[-3:], ("review_window_days", "source_sha256", "candidate_ref"))

    def test_empty_report_still_declares_header(self):
        self.source([("ACME", "X", "1", "2026-01-01")])
        rows, fields = self.rows(window_days=365)
        self.assertEqual(rows, [])
        self.assertEqual(fields[-3:], ("review_window_days", "source_sha256", "candidate_ref"))

    def test_candidate_refs_remain_stable_for_shared_pair(self):
        self.source([("ACME", "A", "1", "2026-01-01"),
                     ("ACME", "B", "1", "2026-01-01")])
        zero, _ = self.rows(window_days=0)
        seven, _ = self.rows(window_days=7)
        self.assertEqual(zero[0]["candidate_ref"], seven[0]["candidate_ref"])
        self.assertEqual(zero[0]["source_sha256"], seven[0]["source_sha256"])

    def test_invalid_engine_window_never_writes(self):
        self.source([("ACME", "A", "1", "2026-01-01"),
                     ("ACME", "B", "1", "2026-01-02")])
        for bad in (True, -1, 366, "7", 0.0):
            with self.subTest(kind=type(bad).__name__):
                with self.assertRaises(ValueError):
                    engine.invoice_twins(self.path, self.root, window_days=bad)
        self.assertEqual(list(self.root.glob("invoice-twins-*.csv")), [])

    def test_snapshot_checksum_and_original_unchanged(self):
        self.source([("ACME", "A", "1", "2026-01-01"),
                     ("ACME", "B", "1", "2026-01-02")])
        original = self.path.read_bytes()
        rows, _ = self.rows(window_days=2)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(rows[0]["source_sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(rows[0]["row_a"], "2")
        self.assertEqual(rows[0]["row_b"], "3")

    def test_invoice_gui_and_native_focus_contract(self):
        source = inspect.getsource(app.run)
        self.assertIn('elif app_id == "invoices":', source)
        self.assertIn("engine.invoice_window_days(", source)
        self.assertIn('"Near-match days (0-365)"', source)
        self.assertEqual(
            keyboard._expected_order(1, invoice_window=True),
            ("input_1", "browse_1", "invoice_window",
             "output", "browse_output", "generate"))
        self.assertEqual(scaling.FREE_INPUTS["invoices"], 1)
        self.assertIs(app.APPS["invoices"][3], False)
        self.assertIs(app.APPS["grants"][3], True)
        self.assertIs(app.APPS["procurement"][3], True)


if __name__ == "__main__":
    unittest.main()
