"""R302 full-checkout integration for both premium vault seal/restore inputs.

Run on a complete repository checkout: these invoke the actual evidence_vault
_read_regular entry point used by GrantAudit and ProcureGuard. Synthetic only.
"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fvs_suite import evidence_vault as vault

PRIVATE = "PRIVATE-SYNTHETIC-GRANT-REFERENCE-302"


class VaultSourceIntegrationR302Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-vault-integration-r302-")
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / (PRIVATE + ".csv")
        self.path.write_bytes(b"id,amount\nSYNTHETIC,120.45\n")

    def test_report_and_journal_are_read_from_exact_bytes(self):
        for label in ("Report", "Journal", "Encrypted archive"):
            with self.subTest(label=label):
                self.assertEqual(vault._read_regular(self.path, 4096, label), self.path.read_bytes())

    def test_report_source_lstat_diagnostic_is_private(self):
        with mock.patch.object(Path, "lstat", side_effect=PermissionError(13, PRIVATE, str(self.path))):
            with self.assertRaisesRegex(ValueError, "Cannot inspect report source") as captured:
                vault._read_regular(self.path, 4096, "Report")
        self.assertIsNone(captured.exception.__context__)
        self.assertIsNone(captured.exception.__cause__)

    def test_vault_source_read_diagnostic_is_private(self):
        with mock.patch("fvs_suite.vault_input_snapshot.os.read",
                        side_effect=OSError(5, PRIVATE, str(self.path))):
            with self.assertRaisesRegex(ValueError, "Cannot read encrypted archive source") as captured:
                vault._read_regular(self.path, 4096, "Encrypted archive")
        self.assertIsNone(captured.exception.__context__)
        self.assertIsNone(captured.exception.__cause__)

    def test_symlink_archive_never_read(self):
        link = self.path.with_suffix(".fvault")
        try:
            link.symlink_to(self.path)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks not supported")
        with self.assertRaisesRegex(ValueError, "regular file"):
            vault._read_regular(link, 4096, "Encrypted archive")

    def test_size_boundary_and_source_integrity(self):
        original = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "exceeds the size limit"):
            vault._read_regular(self.path, len(original)-1, "Report")
        self.assertEqual(self.path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
