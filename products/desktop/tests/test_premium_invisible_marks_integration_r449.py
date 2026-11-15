"""R449 end-to-end writer/verifier mark custody; synthetic evidence only."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.manifest_guard import inventory_text
from fvs_suite.premium_manifest_completion import verify_premium_inventory


class PremiumInvisibleMarksIntegrationR449(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def _package(self, app_id):
        inputs_dir = self.root / "source"
        inputs_dir.mkdir()
        output_dir = self.root / "package"
        output_dir.mkdir()
        sources = [inputs_dir / f"input-{i}.csv" for i in range(3)]
        reports = [output_dir / f"report-{i}.csv"
                   for i in range(2 if app_id == "grants" else 1)]
        for path in sources + reports:
            path.write_bytes(b"synthetic,1.00\n")
        manifest = output_dir / "evidence-manifest.txt"
        manifest.write_text(inventory_text(sources, reports), encoding="ascii")
        return tuple(reports + [manifest])

    def test_writer_refuses_source_mark_before_any_private_hashing(self):
        with patch("fvs_suite.manifest_guard._hash_regular") as hashing:
            with self.assertRaisesRegex(ValueError, "Invalid evidence filename label"):
                inventory_text([self.root / "claim\u034f.csv"],
                               [self.root / "report.csv"])
            hashing.assert_not_called()

    def test_writer_refuses_report_selector_before_any_private_hashing(self):
        with patch("fvs_suite.manifest_guard._hash_regular") as hashing:
            with self.assertRaisesRegex(ValueError, "Invalid evidence filename label"):
                inventory_text([self.root / "claim.csv"],
                               [self.root / "report\U000e0100.csv"])
            hashing.assert_not_called()

    def test_grant_verifier_rejects_canonical_escaped_source_mark(self):
        paths = self._package("grants")
        manifest = paths[-1]
        original_reports = [path.read_bytes() for path in paths[:-1]]
        manifest.write_text(
            manifest.read_text(encoding="ascii").replace(
                "input-0.csv", r"input\u034f-0.csv", 1), encoding="ascii")
        with patch("fvs_suite.premium_manifest_completion._hash_regular") as hashing:
            with self.assertRaisesRegex(ValueError, "Invalid premium evidence label"):
                verify_premium_inventory(paths, "grants")
            hashing.assert_not_called()
        self.assertEqual(original_reports, [path.read_bytes() for path in paths[:-1]])

    def test_procurement_verifier_rejects_canonical_supplementary_selector(self):
        paths = self._package("procurement")
        manifest = paths[-1]
        original_reports = [path.read_bytes() for path in paths[:-1]]
        manifest.write_text(
            manifest.read_text(encoding="ascii").replace(
                "report-0.csv", r"report\udb40\udd00-0.csv", 1), encoding="ascii")
        with patch("fvs_suite.premium_manifest_completion._hash_regular") as hashing:
            with self.assertRaisesRegex(ValueError, "Invalid premium evidence label"):
                verify_premium_inventory(paths, "procurement")
            hashing.assert_not_called()
        self.assertEqual(original_reports, [path.read_bytes() for path in paths[:-1]])


if __name__ == "__main__":
    unittest.main()
