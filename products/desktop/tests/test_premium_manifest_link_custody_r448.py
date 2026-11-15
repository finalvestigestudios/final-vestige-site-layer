"""R448: premium evidence inventories fail closed on hard-link aliases.

Synthetic local fixtures only. These tests do not authorize a release.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import manifest_guard
from fvs_suite.manifest_guard import (
    MAX_INPUT_BYTES, MAX_REPORT_BYTES, _hash_regular, inventory_text,
)
from fvs_suite.premium_link_custody import open_inventory_stream


class PremiumInventoryLinkCustodyR448(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "claim.csv"
        self.report = self.root / "report.csv"
        self.source.write_bytes(b"claim,12.34\n")
        self.report.write_bytes(b"review,required\n")
        self.original = (self.source.read_bytes(), self.report.read_bytes())

    def alias(self, path: Path, name: str) -> Path:
        other = self.root / name
        try:
            os.link(path, other)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Hard links not supported on test filesystem: {type(exc).__name__}")
        return other

    def test_existing_external_alias_refused_before_evidence_open(self):
        for filename, limit in (("source.csv", MAX_INPUT_BYTES),
                                ("report-link.csv", MAX_REPORT_BYTES)):
            with self.subTest(filename=filename):
                path = self.source if "source" in filename else self.report
                alias = self.alias(path, filename)
                try:
                    with patch("fvs_suite.manifest_guard.open_inventory_stream") as opening:
                        with self.assertRaisesRegex(ValueError, "exactly one file link"):
                            _hash_regular(path, limit)
                        opening.assert_not_called()
                finally:
                    alias.unlink()
        self.assertEqual(self.original, (self.source.read_bytes(), self.report.read_bytes()))

    def test_writer_rejects_alias_of_source_or_report(self):
        for path in (self.source, self.report):
            with self.subTest(filename=path.name):
                alias = self.alias(path, "external-alias")
                try:
                    with self.assertRaisesRegex(ValueError, "exactly one file link"):
                        inventory_text([self.source], [self.report])
                finally:
                    alias.unlink()
        self.assertEqual(self.original, (self.source.read_bytes(), self.report.read_bytes()))

    def test_alias_added_after_path_stat_detected_on_open_descriptor(self):
        alias = self.root / "late-open-alias"
        def opening(path, flags):
            stream = open_inventory_stream(path, flags)
            try:
                os.link(path, alias)
            except BaseException:
                stream.close()
                raise
            return stream

        with patch("fvs_suite.manifest_guard.open_inventory_stream", side_effect=opening):
            with self.assertRaisesRegex(ValueError, "exactly one file link"):
                _hash_regular(self.source, MAX_INPUT_BYTES)
        self.assertTrue(alias.exists())

    def test_alias_added_after_descriptor_read_detected_on_path_recheck(self):
        alias = self.root / "late-path-alias"
        original_metadata = manifest_guard._metadata
        calls = 0
        def path_metadata(path):
            nonlocal calls
            calls += 1
            if calls == 2:
                os.link(path, alias)
            return original_metadata(path)

        with patch("fvs_suite.manifest_guard._metadata", side_effect=path_metadata):
            with self.assertRaisesRegex(ValueError, "exactly one file link"):
                _hash_regular(self.source, MAX_INPUT_BYTES)
        self.assertTrue(alias.exists())
        self.assertEqual(calls, 2)

    def test_alias_added_during_later_report_hash_detected_in_final_pass(self):
        alias = self.root / "late-inventory-alias"
        original_hash = manifest_guard._hash_regular
        def hashing(path, maximum):
            outcome = original_hash(path, maximum)
            if path == self.report:
                os.link(self.source, alias)
            return outcome

        with patch("fvs_suite.manifest_guard._hash_regular", side_effect=hashing):
            with self.assertRaisesRegex(ValueError, "exactly one file link"):
                inventory_text([self.source], [self.report])
        self.assertTrue(alias.exists())

    def test_ordinary_single_link_inventory_is_exact_and_read_only(self):
        result = inventory_text([self.source], [self.report])
        self.assertIn(
            "claim.csv\t" + hashlib.sha256(self.original[0]).hexdigest() + "\n",
            result)
        self.assertIn(
            "report.csv\t" + hashlib.sha256(self.original[1]).hexdigest() + "\n",
            result)
        self.assertEqual(self.original, (self.source.read_bytes(), self.report.read_bytes()))


if __name__ == "__main__":
    unittest.main()
