"""R321 real temporary filesystem integration, synthetic evidence only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.verify_restored_bundle_r320 import (BundleHold, inspect_bundle,
                                                  JOURNAL, MANIFEST, REPORT)


class RestoredBundleJournalIntegrationR321(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-journal-r321-")
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name) / "synthetic-evidence"
        self.folder.mkdir()
        self.report = b"id,status\nSYNTHETIC,exception\n"
        (self.folder / REPORT).write_bytes(self.report)
        self.write_journal(b'{"synthetic":true}\n', 1, "grants")

    def write_journal(self, data, count, product="grants"):
        (self.folder / JOURNAL).write_bytes(data)
        meta = {"schema": 1, "product": product,
                "sealed_utc": "2026-11-09T10:05:00+00:00",
                "report_filename": "test.csv",
                "report_sha256": hashlib.sha256(self.report).hexdigest(),
                "journal_filename": "review.jsonl",
                "journal_sha256": hashlib.sha256(data).hexdigest(),
                "journal_present": True, "review_event_count": count}
        (self.folder / MANIFEST).write_text(json.dumps(meta), encoding="utf-8")

    def hold(self):
        with self.assertRaises(BundleHold) as found:
            inspect_bundle(self.folder)
        self.assertIsNone(found.exception.__context__)
        self.assertEqual(str(found.exception),
                         "Private evidence bundle failed consistency verification")

    def test_grant_one_event(self):
        result = inspect_bundle(self.folder)
        self.assertEqual(result["product"], "grants")
        self.assertFalse(result["source_authenticated"])
        self.assertFalse(result["compliance_approved"])
        self.assertTrue(result["review_required"])

    def test_procurement_multiple_events(self):
        self.write_journal(b'{"one":1}\n{"two":2}\n', 2, "procurement")
        self.assertEqual(inspect_bundle(self.folder)["members_verified"], 3)

    def test_present_empty_journal_with_zero_count(self):
        self.write_journal(b"", 0)
        self.assertEqual(inspect_bundle(self.folder)["members_verified"], 3)

    def test_rehashed_journal_wrong_count_is_hold(self):
        self.write_journal(b'{"a":1}\n{"b":2}\n', 1)
        self.hold()

    def test_rehashed_journal_missing_newline_is_hold(self):
        self.write_journal(b'{"a":1}', 1)
        self.hold()

    def test_rehashed_malformed_event_is_hold(self):
        self.write_journal(b'{"broken":}\n', 1)
        self.hold()

    def test_rehashed_duplicate_key_event_is_hold(self):
        self.write_journal(b'{"a":1,"a":2}\n', 1)
        self.hold()

    def test_rehashed_blank_event_is_hold(self):
        self.write_journal(b'{"a":1}\n\n', 2)
        self.hold()

    def test_rehashed_non_object_event_is_hold(self):
        self.write_journal(b'[]\n', 1)
        self.hold()

    def test_no_journal_unchanged(self):
        (self.folder / JOURNAL).unlink()
        p = self.folder / MANIFEST
        meta = json.loads(p.read_text())
        meta.update(journal_filename=None, journal_sha256=None,
                    journal_present=False, review_event_count=0)
        p.write_text(json.dumps(meta))
        self.assertEqual(inspect_bundle(self.folder)["members_verified"], 2)

    def test_check_remains_read_only(self):
        before = {x.name: x.read_bytes() for x in self.folder.iterdir()}
        inspect_bundle(self.folder)
        self.assertEqual(before, {x.name: x.read_bytes() for x in self.folder.iterdir()})

    def test_isolated_cli_and_private_failure(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "verify_restored_bundle_r320.py"
        command = [sys.executable, "-I", str(script), str(self.folder)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.write_journal(b'{"tampered":}\n', 1)
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(str(self.folder), result.stdout + result.stderr)
        self.assertIn("HOLD", result.stderr)


if __name__ == "__main__":
    unittest.main()
