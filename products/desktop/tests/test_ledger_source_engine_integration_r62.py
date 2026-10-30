"""R62 full-checkout LedgerDiff CSV reader/writer integration; synthetic only."""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import engine


class LedgerSourceEngineR62(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-ledger-r62-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.left = self.root / "left.csv"
        self.right = self.root / "right.csv"

    @staticmethod
    def report(path):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def run_diff(self):
        return self.report(engine.ledger_diff(self.left, self.right, self.root)[0])

    def test_bom_multiline_and_source_physical_rows_bind_bytes(self):
        left = (b'\xef\xbb\xbfid,amount,note\r\n'
                b'X,0.10,"first\r\nsecond"\r\n'
                b'X,0.20,ok\r\n')
        right = b'id,amount,note\nX,0.30,right\n'
        self.left.write_bytes(left)
        self.right.write_bytes(right)
        result = self.run_diff()[0]
        self.assertEqual(result["status"], "duplicate_id_review")
        self.assertEqual(result["left_amount"], "0.30")
        self.assertEqual(result["right_amount"], "0.30")
        self.assertEqual(result["left_rows"], "2;4")
        self.assertEqual(result["right_rows"], "2")
        self.assertEqual(result["left_source_sha256"], hashlib.sha256(left).hexdigest())
        self.assertEqual(result["right_source_sha256"], hashlib.sha256(right).hexdigest())
        self.assertEqual(result["input_identity_review"], "")

    def test_same_file_selected_twice_requires_review(self):
        raw = b"id,amount\nT1,10\n"
        self.left.write_bytes(raw)
        result = self.report(engine.ledger_diff(self.left, self.left, self.root)[0])[0]
        self.assertEqual(result["status"], "matched")
        self.assertEqual(result["input_identity_review"], "identical_source_bytes_review")
        self.assertEqual(result["left_source_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result["right_source_sha256"], hashlib.sha256(raw).hexdigest())

    def test_distinct_paths_containing_same_bytes_require_review(self):
        raw = b"id,amount\nT1,10\n"
        self.left.write_bytes(raw)
        self.right.write_bytes(raw)
        self.assertEqual(self.run_diff()[0]["input_identity_review"],
                         "identical_source_bytes_review")

    def test_different_raw_bytes_with_same_rows_not_flagged(self):
        self.left.write_bytes(b"id,amount\nT1,10\n")
        self.right.write_bytes(b"id,amount\r\nT1,10\r\n")
        result = self.run_diff()[0]
        self.assertEqual(result["status"], "matched")
        self.assertEqual(result["input_identity_review"], "")
        self.assertNotEqual(result["left_source_sha256"], result["right_source_sha256"])

    def test_post_snapshot_file_change_does_not_rewrite_evidence(self):
        original = b"id,amount\nT1,1.00\n"
        swapped = b"id,amount\nT1,99.00\n"
        self.left.write_bytes(original)
        self.right.write_bytes(b"id,amount\nT1,1.00\n")
        original_table = engine.table

        def change_source_after_verified_read(*args, **kwargs):
            parsed = original_table(*args, **kwargs)
            if Path(args[0]) == self.left:
                self.left.write_bytes(swapped)
            return parsed

        with patch.object(engine, "table", side_effect=change_source_after_verified_read):
            result = self.run_diff()[0]
        self.assertEqual(result["status"], "matched")
        self.assertEqual(result["left_amount"], "1.00")
        self.assertEqual(result["left_source_sha256"], hashlib.sha256(original).hexdigest())
        self.assertNotEqual(result["left_source_sha256"], hashlib.sha256(swapped).hexdigest())

    def test_missing_left_still_cites_both_sources(self):
        left = b"id,amount\n"
        right = b"id,amount\nT1,5\n"
        self.left.write_bytes(left)
        self.right.write_bytes(right)
        result = self.run_diff()[0]
        self.assertEqual(result["status"], "missing_left")
        self.assertEqual(result["left_rows"], "")
        self.assertEqual(result["right_rows"], "2")
        self.assertEqual(result["left_source_sha256"], hashlib.sha256(left).hexdigest())
        self.assertEqual(result["right_source_sha256"], hashlib.sha256(right).hexdigest())

    def test_header_only_pair_has_no_fabricated_evidence_row(self):
        self.left.write_bytes(b"id,amount\n")
        self.right.write_bytes(b"id,amount\n")
        output = engine.ledger_diff(self.left, self.right, self.root)[0]
        self.assertEqual(self.report(output), [])
        with output.open(encoding="utf-8-sig", newline="") as stream:
            columns = next(csv.reader(stream))
        self.assertEqual(columns[-3:], ["left_source_sha256", "right_source_sha256",
                                        "input_identity_review"])

    def test_changed_left_source_content_preserves_right_identity(self):
        raw = b"id,amount\nT1,10\n"
        self.left.write_bytes(raw)
        self.right.write_bytes(b"id,amount\nT1,11\n")
        report1 = self.run_diff()[0]
        self.left.write_bytes(raw.replace(b"\n", b"\r\n"))
        report2 = self.run_diff()[0]
        self.assertEqual(report1["status"], report2["status"])
        self.assertEqual(report1["difference"], report2["difference"])
        self.assertNotEqual(report1["left_source_sha256"], report2["left_source_sha256"])
        self.assertEqual(report1["right_source_sha256"], report2["right_source_sha256"])

    def test_invalid_input_creates_no_partial_report(self):
        self.left.write_bytes(b"id,amount\nT1,NaN\n")
        self.right.write_bytes(b"id,amount\nT1,10\n")
        with self.assertRaises(ValueError):
            engine.ledger_diff(self.left, self.right, self.root)
        self.assertFalse(list(self.root.glob("ledger-diff-*.csv")))


if __name__ == "__main__":
    unittest.main()
