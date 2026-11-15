"""R447: writer prehash and both premium reader layout integration contracts.

All files are synthetic and local. No premium data, license or release output.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.manifest_guard import inventory_text
from fvs_suite.premium_manifest_completion import verify_premium_inventory


class WindowsManifestIntegrationR447(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def bundle(self, product: str, input_count: int):
        sources = self.root / "source"
        sources.mkdir(exist_ok=True)
        package = self.root / "package"
        package.mkdir(exist_ok=True)
        inputs = []
        for index in range(input_count):
            path = sources / f"input-{index}.csv"
            path.write_bytes(b"synthetic,12.00\n")
            inputs.append(path)
        stems = (("grant-audit-exceptions", "grant-budget-check")
                 if product == "grants" else ("procurement-three-way",))
        reports = []
        for stem in stems:
            path = package / (stem + ".csv")
            path.write_bytes(b"review-needed,1\n")
            reports.append(path)
        manifest = package / "evidence-manifest.txt"
        manifest.write_text(inventory_text(inputs, reports), encoding="ascii")
        return tuple(reports + [manifest])

    def test_producer_refuses_nonportable_inputs_and_reports_before_hash_io(self):
        safe = self.root / "safe.csv"
        for unsafe in ("NUL.csv", "CON.csv", "ledger:2026.csv",
                       "report.", " ledger.csv", "LPT¹.csv"):
            with self.subTest(unsafe=unsafe), patch(
                    "fvs_suite.manifest_guard._hash_regular") as hashing:
                with self.assertRaisesRegex(ValueError, "Invalid evidence filename label"):
                    inventory_text([self.root / unsafe], [safe])
                hashing.assert_not_called()
                with self.assertRaisesRegex(ValueError, "Invalid evidence filename label"):
                    inventory_text([safe], [self.root / unsafe])
                hashing.assert_not_called()

    def test_both_premium_package_layouts_reject_unsafe_source_row_labels(self):
        for product, count in (("grants", 3), ("procurement", 3), ("procurement", 4)):
            with self.subTest(product=product, count=count):
                paths = self.bundle(product, count)
                verify_premium_inventory(paths, product)
                original = tuple(path.read_bytes() for path in paths[:-1])
                manifest = paths[-1]
                text = manifest.read_text(encoding="ascii")
                self.assertIn("input-0.csv", text)
                manifest.write_text(text.replace("input-0.csv", "CON.csv", 1),
                                    encoding="ascii")
                with self.assertRaisesRegex(ValueError, "Invalid premium evidence label"):
                    verify_premium_inventory(paths, product)
                self.assertEqual(original, tuple(path.read_bytes() for path in paths[:-1]))
                for path in paths:
                    path.unlink()
                paths[0].parent.rmdir()

    def test_report_name_alias_refusal_does_not_change_report_bytes(self):
        paths = self.bundle("grants", 3)
        reports = tuple(path.read_bytes() for path in paths[:-1])
        manifest = paths[-1]
        manifest.write_text(
            manifest.read_text(encoding="ascii").replace(
                "grant-audit-exceptions.csv", "AUX.csv", 1),
            encoding="ascii")
        with self.assertRaisesRegex(ValueError, "Invalid premium evidence label"):
            verify_premium_inventory(paths, "grants")
        self.assertEqual(reports, tuple(path.read_bytes() for path in paths[:-1]))


if __name__ == "__main__":
    unittest.main()
