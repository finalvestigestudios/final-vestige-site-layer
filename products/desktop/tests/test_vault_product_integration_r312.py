"""R312 complete-checkout AES-GCM tests. Require cryptography and fvs_suite.

These cannot be certified by the isolated helper tests: the hosted source
and Windows jobs must execute them before QD approval.
"""
from __future__ import annotations

import base64
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fvs_suite import evidence_vault as vault

_PASSWORD = "Synthetic-Premium-Binding-2026"


class ProductScopeIntegrationR312(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r312-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.archive = self.root / "synthetic.fvault"
        self.report = b"case_id,amount\\nSYNTHETIC,15.25\\n".replace(b"\\n", b"\n")
        self.digest = hashlib.sha256(self.report).hexdigest()

    def seal_fixture(self, product):
        payload = {
            "schema": 1, "product": product,
            "sealed_utc": "2026-11-09T00:00:00+00:00",
            "report_filename": "synthetic.csv", "report_sha256": self.digest,
            "report_b64": base64.b64encode(self.report).decode("ascii"),
            "journal_filename": None, "journal_sha256": None,
            "journal_b64": None, "journal_present": False,
            "review_event_count": 0,
        }
        salt, nonce = b"S" * vault.SALT_SIZE, b"N" * vault.NONCE_SIZE
        header = vault.MAGIC + salt + nonce
        clear = json.dumps(payload, sort_keys=True).encode("utf-8")
        cipher = AESGCM(vault._key(_PASSWORD.encode(), salt)).encrypt(nonce, clear, header)
        self.archive.write_bytes(header + cipher)
        return self.archive.read_bytes()

    def restore(self, scope):
        with patch.object(vault, "read_cases", return_value=SimpleNamespace(report_sha256=self.digest)), \
             patch.object(vault, "read_journal", return_value=[]):
            return vault.restore_evidence(self.archive, self.root, _PASSWORD,
                                          expected_product=scope)

    def test_mismatched_archives_fail_before_plaintext_for_both_products(self):
        for archive_product, scope in (("grants", "procurement"), ("procurement", "grants")):
            with self.subTest(archive=archive_product):
                original = self.seal_fixture(archive_product)
                with self.assertRaisesRegex(ValueError, "does not match"):
                    self.restore(scope)
                self.assertEqual(list(self.root.glob("fvs-evidence-restored-*")), [])
                self.assertEqual(self.archive.read_bytes(), original)

    def test_matched_archives_restore_for_both_products(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                original = self.seal_fixture(product)
                restored = self.restore(product)
                self.assertEqual((restored / "exception-report.csv").read_bytes(), self.report)
                self.assertEqual(self.archive.read_bytes(), original)

    def test_invalid_scope_rejected_without_plaintext(self):
        self.seal_fixture("grants")
        with self.assertRaisesRegex(ValueError, "Invalid premium review product scope"):
            self.restore("LedgerDiff Lite")
        self.assertEqual(list(self.root.glob("fvs-evidence-restored-*")), [])


if __name__ == "__main__":
    unittest.main()
