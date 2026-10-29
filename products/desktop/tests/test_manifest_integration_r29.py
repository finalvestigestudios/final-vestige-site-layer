"""R29 integration contracts for the real GrantAudit manifest entry point.

Synthetic data only. Full-checkout CI and native Windows runs remain required.
"""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import engine


class ManifestIntegrationR29Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.claims = self.root / "claims.csv"
        self.ledger = self.root / "ledger.csv"
        self.claims.write_bytes(b"id,amount\nA,0.01\n")
        self.ledger.write_bytes(b"id,amount\nA,0.01\n")

    def assert_no_manifest(self):
        self.assertEqual(list(self.root.glob("evidence-manifest-*.txt")), [])
        self.assertEqual(list(self.root.glob(".*.partial")), [])

    def test_engine_manifest_preserves_legacy_ascii_records(self):
        path = engine.manifest(self.root, [self.claims], [self.ledger])
        rows = path.read_text(encoding="utf-8").splitlines()
        expected = [(source.name, hashlib.sha256(source.read_bytes()).hexdigest())
                    for source in (self.claims, self.ledger)]
        self.assertEqual([tuple(line.split("\t")) for line in rows[1:]], expected)

    def test_engine_rejects_two_same_named_sources_without_publication(self):
        other = self.root / "second"
        other.mkdir()
        duplicate = other / "claims.csv"
        duplicate.write_bytes(b"different private claim")
        with self.assertRaisesRegex(ValueError, "Ambiguous evidence names"):
            engine.manifest(self.root, [self.claims, duplicate], [self.ledger])
        self.assert_no_manifest()

    def test_engine_rejects_oversized_source_without_publication(self):
        oversized = self.root / "oversized.csv"
        with oversized.open("wb") as handle:
            handle.truncate(64 * 1024 * 1024 + 1)
        with self.assertRaisesRegex(ValueError, "file-size limit"):
            engine.manifest(self.root, [oversized], [self.ledger])
        self.assert_no_manifest()

    @unittest.skipIf(os.name == "nt", "Symlink privileges vary on Windows")
    def test_engine_rejects_symlinked_source_without_publication(self):
        linked = self.root / "linked.csv"
        linked.symlink_to(self.claims)
        with self.assertRaisesRegex(ValueError, "regular file"):
            engine.manifest(self.root, [linked], [self.ledger])
        self.assert_no_manifest()

    def test_existing_manifest_preserved_after_verified_source(self):
        destination = self.root / "existing-manifest.txt"
        destination.write_bytes(b"trusted prior manifest")
        with patch("fvs_suite.engine.outpath", return_value=destination):
            with self.assertRaises(FileExistsError):
                engine.manifest(self.root, [self.claims], [self.ledger])
        self.assertEqual(destination.read_bytes(), b"trusted prior manifest")
        self.assertEqual(list(self.root.glob(".*.partial")), [])


if __name__ == "__main__":
    unittest.main()
