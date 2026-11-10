"""R320 real local filesystem tests for the read-only premium bundle inspector."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.verify_restored_bundle_r320 import (BundleHold, JOURNAL, MANIFEST,
                                                REPORT, inspect_bundle, main)


class RestoredBundleInspectionR320(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix="fvs-inspect-r320-")
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.folder = self.root / "fvs-evidence-restored-synthetic"
        self.folder.mkdir()
        self.report = b"case_id,amount\nSYNTHETIC,2.31\n"
        self.journal = b'{"synthetic":true}\n'
        self._make("grants", False)

    def _make(self, product, with_journal):
        (self.folder / REPORT).write_bytes(self.report)
        if with_journal:
            (self.folder / JOURNAL).write_bytes(self.journal)
        else:
            (self.folder / JOURNAL).unlink(missing_ok=True)
        meta = {"schema": 1, "product": product,
                "sealed_utc": "2026-11-09T10:05:00+00:00",
                "report_filename": "synthetic.csv",
                "report_sha256": hashlib.sha256(self.report).hexdigest(),
                "journal_filename": "review.jsonl" if with_journal else None,
                "journal_sha256": hashlib.sha256(self.journal).hexdigest() if with_journal else None,
                "journal_present": with_journal,
                "review_event_count": 1 if with_journal else 0}
        (self.folder / MANIFEST).write_text(json.dumps(meta), encoding="utf-8")

    def _mutate_meta(self, field, value):
        p = self.folder / MANIFEST
        meta = json.loads(p.read_text())
        meta[field] = value
        p.write_text(json.dumps(meta))

    def _hold(self):
        with self.assertRaises(BundleHold) as ctx:
            inspect_bundle(self.folder)
        self.assertEqual(str(ctx.exception), "Private evidence bundle failed consistency verification")
        self.assertIsNone(ctx.exception.__context__)

    def test_grant_no_journal_real_bytes(self):
        result = inspect_bundle(self.folder)
        self.assertEqual(result["product"], "grants")
        self.assertEqual(result["members_verified"], 2)
        self.assertFalse(result["source_authenticated"])
        self.assertFalse(result["compliance_approved"])
        self.assertTrue(result["review_required"])

    def test_procurement_with_journal(self):
        self._make("procurement", True)
        result = inspect_bundle(self.folder)
        self.assertEqual(result["members_verified"], 3)
        self.assertEqual(result["journal_sha256"], hashlib.sha256(self.journal).hexdigest())

    def test_no_files_modified(self):
        self._make("grants", True)
        before = {x.name: x.read_bytes() for x in self.folder.iterdir()}
        inspect_bundle(self.folder)
        self.assertEqual(before, {x.name: x.read_bytes() for x in self.folder.iterdir()})

    def test_modified_report_rejected(self):
        (self.folder / REPORT).write_bytes(b"altered report")
        self._hold()

    def test_modified_journal_rejected(self):
        self._make("procurement", True)
        (self.folder / JOURNAL).write_bytes(b"altered journal")
        self._hold()

    def test_unexpected_extra_file_rejected(self):
        (self.folder / "private-other.csv").write_text("secret")
        self._hold()

    def test_unexpected_journal_without_manifest_flag_rejected(self):
        (self.folder / JOURNAL).write_bytes(b"hidden unregistered")
        self._hold()

    def test_missing_report_rejected(self):
        (self.folder / REPORT).unlink()
        self._hold()

    def test_symlink_file_rejected(self):
        (self.folder / REPORT).unlink()
        (self.folder / REPORT).symlink_to(self.root / "outside.csv")
        self._hold()

    def test_symlink_folder_rejected(self):
        link = self.root / "link"
        link.symlink_to(self.folder, target_is_directory=True)
        with self.assertRaises(BundleHold):
            inspect_bundle(link)

    def test_hardlinked_report_rejected(self):
        os.link(self.folder / REPORT, self.root / "hardlink.csv")
        self._hold()

    def test_forged_manifest_changed_digest_rejected(self):
        self._mutate_meta("report_sha256", "0" * 64)
        self._hold()

    def test_cross_product_or_unknown_product_rejected(self):
        self._mutate_meta("product", "LedgerDiffLite")
        self._hold()

    def test_not_a_manifest_v1_rejected(self):
        self._mutate_meta("schema", True)
        self._hold()

    def test_journal_count_bool_rejected(self):
        self._mutate_meta("review_event_count", False)
        self._hold()

    def test_duplicate_json_key_rejected(self):
        p = self.folder / MANIFEST
        p.write_bytes(p.read_bytes().replace(b'"schema": 1', b'"schema": 1, "schema": 1'))
        self._hold()

    def test_nonfinite_json_token_rejected(self):
        p = self.folder / MANIFEST
        p.write_bytes(p.read_bytes().replace(b'"schema": 1', b'"schema": NaN'))
        self._hold()

    def test_traversal_report_filename_rejected(self):
        self._mutate_meta("report_filename", "../secret.csv")
        self._hold()

    def test_report_bytes_after_first_pass_mutated_fails(self):
        import scripts.verify_restored_bundle_r320 as module
        original = module._read_member
        calls = [0]
        def mutate(*args, **kw):
            result = original(*args, **kw)
            if args[2] == REPORT:
                calls[0] += 1
                if calls[0] == 1:
                    (self.folder / REPORT).write_bytes(b"tampered afterwards")
            return result
        with patch.object(module, "_read_member", side_effect=mutate):
            self._hold()

    def test_private_path_hidden_from_exception_context(self):
        import scripts.verify_restored_bundle_r320 as module
        secret = str(self.folder / "TOP-SECRET-CUSTOMER-2026")
        with patch.object(module.os, "listdir", side_effect=OSError(secret)):
            with self.assertRaises(BundleHold) as caught:
                inspect_bundle(self.folder)
        self.assertNotIn(secret, str(caught.exception))
        self.assertIsNone(caught.exception.__context__)

    def test_bad_timestamp_rejected(self):
        self._mutate_meta("sealed_utc", "2026-11-09")
        self._hold()

    def test_cli_success_and_failure_no_private_paths(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "verify_restored_bundle_r320.py"
        cmd = [sys.executable, "-I", str(script), str(self.folder)]
        good = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        self.assertEqual(good.returncode, 0)
        self.assertIn("NOT AUTHENTICATED", good.stdout)
        (self.folder / REPORT).write_bytes(b"tampered")
        bad = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        self.assertEqual(bad.returncode, 1)
        self.assertNotIn(str(self.folder), bad.stderr + bad.stdout)


if __name__ == "__main__":
    unittest.main()
