"""R322: real temp-directory offline SHA-256 witness binding, synthetic records."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.verify_restored_bundle_r320 import (
    BundleHold, ERROR, REPORT, JOURNAL, MANIFEST,
    inspect_bundle, inspect_with_external_witness,
)


_MISSING = object()


class RestoredExternalWitnessR322(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-witness-r322-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name) / "synthetic-evidence"
        self.folder.mkdir()
        self.report = b"row_id,amount\nFAKE-1,12.30\n"
        self.journal = b'{"synthetic":true}\n'
        self.make_bundle("grants", True)

    def digest(self, raw):
        return hashlib.sha256(raw).hexdigest()

    def make_bundle(self, product, journal_present):
        (self.folder / REPORT).write_bytes(self.report)
        if journal_present:
            (self.folder / JOURNAL).write_bytes(self.journal)
        else:
            (self.folder / JOURNAL).unlink(missing_ok=True)
        manifest = {
            "schema": 1, "product": product,
            "sealed_utc": "2026-11-09T10:05:00+00:00",
            "report_filename": "synthetic.csv",
            "report_sha256": self.digest(self.report),
            "journal_filename": "synthetic.jsonl" if journal_present else None,
            "journal_sha256": self.digest(self.journal) if journal_present else None,
            "journal_present": journal_present,
            "review_event_count": 1 if journal_present else 0,
        }
        (self.folder / MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")

    def check(self, *, product="grants", report=_MISSING, journal="default"):
        return inspect_with_external_witness(
            self.folder,
            product=product,
            report_sha256=self.digest(self.report) if report is _MISSING else report,
            journal_sha256=(self.digest(self.journal) if journal == "default" else journal),
        )

    def hold(self, **kwargs):
        with self.assertRaises(BundleHold) as caught:
            self.check(**kwargs)
        self.assertEqual(str(caught.exception), ERROR)
        self.assertIsNone(caught.exception.__context__)

    def test_grant_report_and_journal_witness_pass(self):
        result = self.check()
        self.assertTrue(result["external_witness_matched"])
        self.assertFalse(result["source_authenticated"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["compliance_approved"])
        self.assertTrue(result["review_required"])

    def test_procurement_report_and_journal_witness_pass(self):
        self.make_bundle("procurement", True)
        self.assertTrue(self.check(product="procurement")["external_witness_matched"])

    def test_no_journal_requires_explicit_absence(self):
        self.make_bundle("grants", False)
        self.assertTrue(self.check(journal=None)["external_witness_matched"])
        self.hold()

    def test_present_journal_refuses_absence_claim(self):
        self.hold(journal=None)

    def test_wrong_product_refuses(self):
        self.hold(product="procurement")

    def test_wrong_report_digest_refuses(self):
        self.hold(report="0" * 64)

    def test_wrong_journal_digest_refuses(self):
        self.hold(journal="0" * 64)

    def test_unknown_product_refuses(self):
        for bad in ("GrantAudit Studio Pro", "GRANTS", "ledger", "", True, None):
            with self.subTest(bad=bad):
                self.hold(product=bad)

    def test_invalid_report_witness_refuses(self):
        for bad in ("0" * 63, "0" * 65, "f" * 63 + "G", "A" * 64,
                    " " + "0" * 64, "0" * 64 + "\n", 1, True, None):
            with self.subTest(bad=bad):
                self.hold(report=bad)

    def test_invalid_journal_witness_refuses(self):
        for bad in ("0" * 63, "0" * 65, "A" * 64, "0" * 64 + "\n", False, 0):
            with self.subTest(bad=bad):
                self.hold(journal=bad)

    def test_rehashed_report_tamper_predecessor_passes_witness_holds(self):
        trusted = self.digest(self.report)
        self.report = b"row_id,amount\nFAKE-1,9999.99\n"
        self.make_bundle("grants", True)
        # The plaintext manifest is editable: consistency-only accepts a forged
        # *self-consistent* replacement. Trusted external witness detects it.
        self.assertEqual(inspect_bundle(self.folder)["report_sha256"], self.digest(self.report))
        self.hold(report=trusted)

    def test_rehashed_journal_tamper_predecessor_passes_witness_holds(self):
        trusted = self.digest(self.journal)
        self.journal = b'{"synthetic":"changed"}\n'
        self.make_bundle("grants", True)
        self.assertEqual(inspect_bundle(self.folder)["journal_sha256"], self.digest(self.journal))
        self.hold(journal=trusted)

    def test_rehashed_product_swap_refuses_witness(self):
        self.make_bundle("procurement", True)
        self.assertEqual(inspect_bundle(self.folder)["product"], "procurement")
        self.hold(product="grants")

    def test_inspector_still_holds_bad_original_manifest(self):
        (self.folder / MANIFEST).write_bytes(b'{}')
        self.hold()

    def test_no_file_bytes_changed(self):
        before = {p.name: p.read_bytes() for p in self.folder.iterdir()}
        self.check()
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.folder.iterdir()})

    def cli(self, *flags):
        script = Path(__file__).resolve().parents[1] / "scripts" / "verify_restored_bundle_r320.py"
        return subprocess.run([sys.executable, "-I", str(script), str(self.folder), *flags],
                              capture_output=True, text=True, timeout=15)

    def test_isolated_cli_full_witness_grants(self):
        result = self.cli("--expect-product", "grants", "--expect-report-sha256",
                          self.digest(self.report), "--expect-journal-sha256",
                          self.digest(self.journal))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("matches operator-supplied", result.stdout)
        self.assertIn("NOT AUTHENTICATED", result.stdout)

    def test_isolated_cli_no_journal(self):
        self.make_bundle("procurement", False)
        result = self.cli("--expect-product", "procurement", "--expect-report-sha256",
                          self.digest(self.report), "--expect-no-journal")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_isolated_cli_partial_witness_holds(self):
        for flags in (("--expect-product", "grants"),
                      ("--expect-report-sha256", self.digest(self.report)),
                      ("--expect-no-journal",),
                      ("--expect-product", "grants", "--expect-report-sha256", self.digest(self.report))):
            with self.subTest(flags=flags):
                result = self.cli(*flags)
                self.assertEqual(result.returncode, 1)
                self.assertIn("HOLD", result.stderr)
                self.assertNotIn(str(self.folder), result.stdout + result.stderr)

    def test_isolated_cli_wrong_external_digest_holds_private(self):
        result = self.cli("--expect-product", "grants", "--expect-report-sha256",
                          "0" * 64, "--expect-journal-sha256", self.digest(self.journal))
        self.assertEqual(result.returncode, 1)
        self.assertIn("HOLD", result.stderr)
        self.assertNotIn(str(self.folder), result.stdout + result.stderr)
        self.assertNotIn(self.digest(self.journal), result.stdout + result.stderr)

    def test_unanchored_cli_compatibility(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("bundle internally consistent", result.stdout)


if __name__ == "__main__":
    unittest.main()
