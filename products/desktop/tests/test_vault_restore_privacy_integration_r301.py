"""R301 full-checkout integration: private fields never escape archive exceptions.

These tests require the full fvs_suite tree and cryptography dependency.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fvs_suite import evidence_vault as vault

PASSWORD = "correct horse battery staple: synthetic only"
SENSITIVE = "PRIVATE-GRANT-ACCOUNT-2026"


class VaultRestoreIntegrationR301Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-vault-r301-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.archive = self.folder / "malformed.fvault"

    def sealed(self, clear: bytes):
        salt = b"S" * vault.SALT_SIZE
        nonce = b"N" * vault.NONCE_SIZE
        prefix = vault.MAGIC + salt + nonce
        self.archive.write_bytes(prefix + AESGCM(vault._key(PASSWORD.encode(), salt)).encrypt(nonce, clear, prefix))
        return self.archive

    def check_private_failure(self, text):
        before = set(self.folder.iterdir())
        with self.assertRaisesRegex(ValueError, text) as captured:
            vault.restore_evidence(self.archive, self.folder, PASSWORD)
        self.assertIsNone(captured.exception.__cause__)
        self.assertIsNone(captured.exception.__context__)
        self.assertEqual(set(self.folder.iterdir()), before)

    def test_private_malformed_json_error_chain_is_empty(self):
        self.sealed(('{"secret":"' + SENSITIVE + '",broken}').encode())
        self.check_private_failure("invalid JSON")

    def test_private_invalid_utf8_error_chain_is_empty(self):
        self.sealed(b'{"private":"' + SENSITIVE.encode() + b'\xff"}')
        self.check_private_failure("invalid JSON")

    def test_private_invalid_base64_error_chain_is_empty(self):
        self.sealed((
            '{"schema":1,"product":"grants","sealed_utc":"2026-11-09T00:00:00+00:00",'
            '"report_filename":"synthetic.csv","report_sha256":"",'
            '"report_b64":"' + SENSITIVE + '#",'
            '"journal_filename":null,"journal_sha256":null,"journal_b64":null,'
            '"journal_present":false,"review_event_count":0}'
        ).encode())
        self.check_private_failure("Malformed encrypted evidence bytes")

    def test_wrong_password_error_chain_is_empty(self):
        self.sealed(b'{}')
        before = set(self.folder.iterdir())
        with self.assertRaisesRegex(ValueError, "Wrong passphrase") as captured:
            vault.restore_evidence(self.archive, self.folder, "a different synthetic long passphrase")
        self.assertIsNone(captured.exception.__cause__)
        self.assertIsNone(captured.exception.__context__)
        self.assertEqual(set(self.folder.iterdir()), before)


if __name__ == '__main__':
    unittest.main()
