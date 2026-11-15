"""R445: private exception graph custody for both premium evidence manifests.

Synthetic files only; no client data, network calls, license, or release activity.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import traceback
import unittest
from pathlib import Path
from unittest.mock import patch

import fvs_suite.premium_manifest_completion as target

PRIVATE = "PRIVATE_GRANT_CLIENT_8821_DO_NOT_ECHO"
HEADER = "SHA-256 file inventory. Hashes do not certify accuracy or compliance.\n"


class PrivatePremiumManifestChainsR445(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def package(self, product):
        folder = self.root / product
        folder.mkdir()
        stems = ("grant-audit-exceptions", "grant-budget-check") if product == "grants" else ("procurement-three-way",)
        reports = []
        for stem in stems:
            file = folder / (stem + ".csv")
            file.write_bytes((stem + ",12.00\n").encode("ascii"))
            reports.append(file)
        manifest = folder / "evidence-manifest.txt"
        rows = [f"input-{i}.csv\t" + "a" * 64 + "\n" for i in range(3)]
        rows.extend(json.dumps(file.name)[1:-1] + "\t" + hashlib.sha256(file.read_bytes()).hexdigest() + "\n" for file in reports)
        manifest.write_text(HEADER + "".join(rows), encoding="ascii")
        return tuple(reports + [manifest])

    def assert_private(self, operation):
        with self.assertRaises(ValueError) as observed:
            operation()
        error = observed.exception
        # The traceback formatter by default suppresses from-None context;
        # explicit object inspection must also find no private underlying error.
        self.assertNotIn(PRIVATE, str(error))
        self.assertNotIn(PRIVATE, "".join(traceback.format_exception_only(type(error), error)))
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)

    def test_valid_product_packages_still_pass(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                target.verify_premium_inventory(self.package(product), product)

    def test_non_ascii_manifest_decode_private_bytes_do_not_escape(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                paths = self.package(product)
                paths[-1].write_bytes(paths[-1].read_bytes() + PRIVATE.encode() + b"\xff\n")
                self.assert_private(lambda: target.verify_premium_inventory(paths, product))

    def test_oserror_from_manifest_open_has_no_private_context(self):
        paths = self.package("grants")
        with patch.object(target, "open_inventory_stream", side_effect=OSError(PRIVATE)):
            self.assert_private(lambda: target.verify_premium_inventory(paths, "grants"))

    def test_missing_private_manifest_has_no_oserror_context(self):
        paths = self.package("procurement")
        paths[-1].unlink()
        self.assert_private(lambda: target._read_bounded_inventory(paths[-1]))

    def test_invalid_json_label_does_not_retain_source_text(self):
        paths = self.package("grants")
        content = paths[-1].read_text(encoding="ascii")
        paths[-1].write_text(content.replace("input-0.csv", PRIVATE + r"\u0QQQ"), encoding="ascii")
        self.assert_private(lambda: target.verify_premium_inventory(paths, "grants"))

    def test_directory_listing_oserror_scrubbed_before_manifest_read(self):
        paths = self.package("procurement")
        with patch.object(Path, "iterdir", side_effect=OSError(PRIVATE)):
            self.assert_private(lambda: target.verify_premium_inventory(paths, "procurement"))

    def test_report_link_inspection_oserror_scrubbed(self):
        paths = self.package("grants")
        real_lstat = Path.lstat
        def inspect(path):
            if path == paths[0]:
                raise OSError(PRIVATE)
            return real_lstat(path)
        with patch.object(Path, "lstat", autospec=True, side_effect=inspect):
            self.assert_private(lambda: target.verify_premium_inventory(paths, "grants"))

    def test_final_recheck_listing_failure_scrubbed(self):
        paths = self.package("procurement")
        original = Path.iterdir
        count = 0
        def listing(path):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError(PRIVATE)
            return original(path)
        with patch.object(Path, "iterdir", autospec=True, side_effect=listing):
            self.assert_private(lambda: target.verify_premium_inventory(paths, "procurement"))
        self.assertGreaterEqual(count, 2)

    def test_corrupt_manifest_does_not_change_report_bytes(self):
        paths = self.package("grants")
        before = tuple(path.read_bytes() for path in paths[:-1])
        paths[-1].write_bytes(paths[-1].read_bytes() + PRIVATE.encode() + b"\xfe")
        self.assert_private(lambda: target.verify_premium_inventory(paths, "grants"))
        self.assertEqual(before, tuple(path.read_bytes() for path in paths[:-1]))


if __name__ == "__main__":
    unittest.main()
