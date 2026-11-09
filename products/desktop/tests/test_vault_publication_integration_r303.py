"""R303 full-checkout integration: premium seal uses private atomic publisher.

These methods require the complete private suite, including cryptography and
the R301/R302 vault dependencies. Synthetic financial examples only.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from fvs_suite import evidence_vault as vault


class PremiumVaultPublicationIntegrationR303(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r303-integration-")
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        self.report = self.folder / "synthetic-grants-exceptions.csv"
        self.report.write_bytes(b"claim_id,amount\nC100,120.45\n")
        self.journal = self.folder / "synthetic-grants-exceptions.review.jsonl"
        self.original = self.report.read_bytes()
        self.digest = hashlib.sha256(self.original).hexdigest()
        self.passphrase = "PrivateSyntheticPassphraseForTests"

    def _seal(self):
        batch = SimpleNamespace(report_sha256=self.digest)
        with mock.patch.object(vault, "read_cases", return_value=batch), \
             mock.patch.object(vault, "read_journal", return_value=[]):
            return vault.seal_evidence(self.report, "grants", self.journal,
                                       self.folder, self.passphrase,
                                       expected_report_sha256=self.digest)

    def test_actual_sealed_ciphertext_published_and_sources_unchanged(self):
        path = self._seal()
        self.assertTrue(path.name.endswith(".fvault"))
        self.assertTrue(path.read_bytes().startswith(vault.MAGIC))
        self.assertGreater(len(path.read_bytes()), len(vault.MAGIC))
        self.assertEqual(self.report.read_bytes(), self.original)
        self.assertFalse(self.journal.exists())
        self.assertEqual(list(self.folder.glob(".fvs-vault-*.partial")), [])

    def test_fail_fsync_leaves_no_final_archive(self):
        with mock.patch("fvs_suite.vault_publish.os.fsync",
                        side_effect=OSError(5, "SYNTHETIC-PRIVATE-PATH")):
            with self.assertRaises(OSError) as caught:
                self._seal()
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)
        self.assertEqual(list(self.folder.glob("*.fvault")), [])
        self.assertEqual(list(self.folder.glob(".fvs-vault-*.partial")), [])
        self.assertEqual(self.report.read_bytes(), self.original)

    def test_final_name_is_not_visible_while_staging_fsync_runs(self):
        import os
        original_fsync = os.fsync
        observations = []
        def observe(fd):
            observations.append(list(self.folder.glob("*.fvault")))
            return original_fsync(fd)
        with mock.patch("fvs_suite.vault_publish.os.fsync", side_effect=observe):
            path = self._seal()
        self.assertEqual(observations, [[]])
        self.assertEqual(path.read_bytes()[:len(vault.MAGIC)], vault.MAGIC)


if __name__ == "__main__":
    unittest.main()
