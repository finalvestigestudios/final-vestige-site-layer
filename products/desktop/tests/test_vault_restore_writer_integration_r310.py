"""R310 full-repository integration: restore errors never leak customer paths.

These tests require cryptography and the complete fvs_suite checkout.
No real financial records, network activity, or premium distribution.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import tempfile
import traceback
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fvs_suite import evidence_vault as vault

PASS = "Synthetic-Private-Vault-Passphrase-2026"
SECRET = "PRIVATE-SYNTHETIC-CUSTOMER-FILENAME-310"


class VaultRestoreWriterIntegrationR310(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r310-integration-")
        self.addCleanup(temp.cleanup)
        self.parent = Path(temp.name)
        self.archive = self.parent / "private-archive.fvault"
        self.report = b"claim_id,amount\\nSYNTHETIC,123.45\\n".replace(b"\\n", b"\n")
        self.digest = hashlib.sha256(self.report).hexdigest()

    def sealed(self, product):
        data = {
            "schema": 1, "product": product,
            "sealed_utc": "2026-11-09T17:00:00+00:00",
            "report_filename": "synthetic.csv", "report_sha256": self.digest,
            "report_b64": base64.b64encode(self.report).decode("ascii"),
            "journal_filename": None, "journal_sha256": None,
            "journal_b64": None, "journal_present": False,
            "review_event_count": 0,
        }
        clear = json.dumps(data, sort_keys=True).encode("utf-8")
        salt, nonce = b"S" * vault.SALT_SIZE, b"N" * vault.NONCE_SIZE
        header = vault.MAGIC + salt + nonce
        cipher = AESGCM(vault._key(PASS.encode(), salt)).encrypt(nonce, clear, header)
        self.archive.write_bytes(header + cipher)
        return self.archive.read_bytes()

    def restore(self):
        with patch.object(vault, "read_cases", return_value=SimpleNamespace(report_sha256=self.digest)), \
             patch.object(vault, "read_journal", return_value=[]):
            return vault.restore_evidence(self.archive, self.parent, PASS)

    def no_restored_dirs(self):
        self.assertEqual(list(self.parent.glob("fvs-evidence-restored-*")), [])

    def check_private_error(self, error, expected):
        self.assertIsInstance(error, ValueError)
        self.assertIn(expected, str(error))
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        dump = "".join(traceback.format_exception(error))
        self.assertNotIn(SECRET, dump)
        self.assertNotIn(str(self.parent), str(error))

    def test_genuine_encrypted_restore_for_both_premium_products(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                original = self.sealed(product)
                restored = self.restore()
                self.assertEqual((restored / "exception-report.csv").read_bytes(), self.report)
                self.assertEqual(json.loads((restored / "sealed-evidence-manifest.json").read_text())["product"], product)
                self.assertEqual(self.archive.read_bytes(), original)

    def test_fsync_failure_is_private_and_rolls_back_both_products(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                original = self.sealed(product)
                with patch("fvs_suite.vault_restore_writer.os.fsync",
                           side_effect=OSError(5, SECRET, str(self.parent / SECRET))):
                    with self.assertRaises(ValueError) as captured:
                        self.restore()
                self.check_private_error(captured.exception, "write private restored evidence")
                self.no_restored_dirs()
                self.assertEqual(self.archive.read_bytes(), original)

    def test_folder_creation_failure_is_private_before_any_plaintext(self):
        self.sealed("grants")
        with patch("fvs_suite.vault_restore_writer.Path.mkdir",
                   side_effect=PermissionError(13, SECRET, str(self.parent / SECRET))):
            with self.assertRaises(ValueError) as captured:
                self.restore()
        self.check_private_error(captured.exception, "create private evidence restore folder")
        self.no_restored_dirs()

    def test_postwrite_digest_mismatch_keeps_no_restored_plaintext(self):
        self.sealed("procurement")
        with patch.object(vault, "read_cases", return_value=SimpleNamespace(report_sha256="0"*64)), \
             patch.object(vault, "read_journal", return_value=[]):
            with self.assertRaisesRegex(ValueError, "no longer matches"):
                vault.restore_evidence(self.archive, self.parent, PASS)
        self.no_restored_dirs()


if __name__ == "__main__":
    unittest.main()
