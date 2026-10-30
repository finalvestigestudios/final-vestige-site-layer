"""R61 full-checkout integration; real CSV importer/writer, synthetic inputs."""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import engine


class SpendSourceDigestEngineR61(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-spend-r61-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "spend.csv"

    @staticmethod
    def read_report(path):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_real_csv_snapshot_digest_in_each_row(self):
        raw = (b'\xef\xbb\xbfvendor,amount,date,category,note\r\n'
               b'A-CME,0.10,2026-01-01,Parts,"multi\r\nline"\r\n'
               b'ACME,0.20,2026-02-01,Parts,regular\r\n')
        self.source.write_bytes(raw)
        report = self.read_report(engine.spend_map(self.source, self.root)[0])
        self.assertEqual(len(report), 2)
        self.assertEqual({r["source_sha256"] for r in report},
                         {hashlib.sha256(raw).hexdigest()})
        self.assertEqual([r["source_rows"] for r in report], ["2", "4"])
        self.assertTrue(all("normalized_vendor_collision_review" in r["flag"]
                            for r in report))

    def test_identical_parsed_records_different_bytes_bind_different_source(self):
        text = "vendor,amount,date\nACME,1.00,2026-01-01\n"
        self.source.write_bytes(text.encode("utf-8"))
        report_a = self.read_report(engine.spend_map(self.source, self.root)[0])[0]
        self.source.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
        report_b = self.read_report(engine.spend_map(self.source, self.root)[0])[0]
        self.assertEqual(report_a["amount"], report_b["amount"])
        self.assertNotEqual(report_a["source_sha256"], report_b["source_sha256"])

    def test_post_snapshot_path_swap_cannot_rewrite_source_identity(self):
        original = b"vendor,amount,date\nACME,1.00,2026-01-01\n"
        swapped = b"vendor,amount,date\nACME,99.00,2026-01-01\n"
        self.source.write_bytes(original)
        original_table = engine.table

        def swap_after_snapshot(*args, **kwargs):
            frozen = original_table(*args, **kwargs)
            self.source.write_bytes(swapped)
            return frozen

        with patch.object(engine, "table", side_effect=swap_after_snapshot):
            report = self.read_report(engine.spend_map(self.source, self.root)[0])[0]
        self.assertEqual(report["amount"], "1.00")
        self.assertEqual(report["source_sha256"], hashlib.sha256(original).hexdigest())
        self.assertNotEqual(report["source_sha256"], hashlib.sha256(swapped).hexdigest())

    def test_explicit_csv_header_and_digest_are_stable(self):
        self.source.write_text("vendor,amount,date\nACME,1,2026-01-01\n", encoding="utf-8")
        output = engine.spend_map(self.source, self.root)[0]
        with output.open(encoding="utf-8-sig", newline="") as f:
            header = next(csv.reader(f))
        self.assertEqual(header[-1], "source_sha256")
        self.assertEqual(header.count("source_sha256"), 1)

    def test_bad_source_creates_no_spend_csv(self):
        self.source.write_text("vendor,amount,date\nACME,NaN,2026-01-01\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            engine.spend_map(self.source, self.root)
        self.assertFalse(list(self.root.glob("spend-map-*.csv")))


if __name__ == "__main__":
    unittest.main()
