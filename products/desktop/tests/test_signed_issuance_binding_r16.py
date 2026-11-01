"""R16: signed-byte receipt binding; only temporary, test-only Ed25519 keys."""
import hashlib
import os
import sqlite3
from contextlib import closing
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import license_issuer
from license_registry import IssuanceRegistry, RegistryError

NOW = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
EXPIRES = "2027-10-28T12:00:00Z"


class SignedIssuanceBindingR16(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-issuance-r16-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.database = self.root / "operator.sqlite3"
        self.registry = IssuanceRegistry(self.database)
        self.key = Ed25519PrivateKey.generate()
        self.password = b"ephemeral-test-secret"
        self.pem = self.root / "never-distribute-test-key.pem"
        self.pem.write_bytes(self.key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.BestAvailableEncryption(self.password)))
        if os.name == "posix":
            self.pem.chmod(0o600)
        self.output = self.root / "grant.fvslicense"
        self.details = dict(license_id="test-r16-grants-0001", product="grants",
                            kid="test-r16-key-0001", output=self.output)

    def reserve(self, **changes):
        details = {**self.details, **changes}
        self.registry.reserve(**details)

    def sign(self, **changes):
        d = {**self.details, **changes}
        return license_issuer.issue_entitlement(
            key_path=self.pem, password=self.password, kid=d["kid"],
            product=d["product"], license_id=d["license_id"],
            holder="Synthetic Test Entity", expires_at=EXPIRES,
            output=d["output"], now=NOW, return_digest=True,
        )

    def state(self):
        with closing(sqlite3.connect(self.database)) as db, db:
            return db.execute(
                "SELECT state, license_sha256 FROM issuance WHERE license_id=?",
                (self.details["license_id"],)).fetchone()

    def test_actual_signed_grants_content_finalizes_with_exact_receipt(self):
        self.reserve()
        path, receipt = self.sign()
        self.assertEqual(receipt, hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(receipt, self.registry.finalize(
            **self.details, expected_sha256=receipt))
        self.assertEqual(self.state(), ("issued", receipt))

    def test_actual_signed_procurement_content_finalizes_with_exact_receipt(self):
        info = {**self.details, "license_id": "test-r16-proc-0001",
                "product": "procurement",
                "output": self.root / "proc.fvslicense"}
        self.registry.reserve(**info)
        path, receipt = self.sign(**info)
        self.assertEqual(receipt, self.registry.finalize(
            **info, expected_sha256=receipt))
        self.assertTrue(path.is_file())

    def test_tampering_after_signature_verification_never_finalizes(self):
        self.reserve()
        path, receipt = self.sign()
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(RegistryError, "differs from verified signed payload"):
            self.registry.finalize(**self.details, expected_sha256=receipt)
        self.assertEqual(self.state(), ("reserved", None))

    def test_same_length_replacement_is_detected(self):
        self.reserve()
        path, receipt = self.sign()
        content = bytearray(path.read_bytes())
        content[10] ^= 1
        path.write_bytes(content)
        with self.assertRaisesRegex(RegistryError, "differs from verified"):
            self.registry.finalize(**self.details, expected_sha256=receipt)
        self.assertEqual(self.state(), ("reserved", None))

    def test_swapping_another_valid_signed_license_is_detected(self):
        self.reserve()
        path, receipt = self.sign()
        alternate = self.root / "other.fvslicense"
        other, other_receipt = self.sign(
            license_id="test-r16-grants-0002", output=alternate)
        self.assertNotEqual(other_receipt, receipt)
        path.write_bytes(other.read_bytes())
        with self.assertRaisesRegex(RegistryError, "differs from verified"):
            self.registry.finalize(**self.details, expected_sha256=receipt)
        self.assertEqual(self.state(), ("reserved", None))

    def test_signed_receipt_is_from_memory_not_an_untrusted_second_read(self):
        self.reserve()
        original_verify = license_issuer.verifier.verify_license

        def verified_then_swapped(path, product, **kwargs):
            result = original_verify(path, product, **kwargs)
            Path(path).write_bytes(b"attacker replaced the verified license")
            return result

        with patch.object(license_issuer.verifier, "verify_license",
                          side_effect=verified_then_swapped):
            path, receipt = self.sign()
        self.assertNotEqual(receipt, hashlib.sha256(path.read_bytes()).hexdigest())
        with self.assertRaisesRegex(RegistryError, "differs from verified"):
            self.registry.finalize(**self.details, expected_sha256=receipt)
        self.assertEqual(self.state(), ("reserved", None))

    def test_bad_expected_digests_fail_closed_before_db_change(self):
        self.reserve()
        self.sign()
        for invalid in (None, "", "x" * 64, "A" * 64, "0" * 63,
                        "0" * 65, b"0" * 64, 12):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                    RegistryError, "canonical lowercase hex"):
                self.registry.finalize(**self.details, expected_sha256=invalid)
        self.assertEqual(self.state(), ("reserved", None))

    def test_well_formed_but_false_digest_is_refused(self):
        self.reserve()
        path, receipt = self.sign()
        altered = ("0" if receipt[0] != "0" else "1") + receipt[1:]
        with self.assertRaisesRegex(RegistryError, "differs from verified"):
            self.registry.finalize(**self.details, expected_sha256=altered)
        self.assertEqual(self.state(), ("reserved", None))
        self.assertEqual(path.read_bytes(), self.output.read_bytes())

    def test_omitting_required_signed_receipt_is_not_allowed(self):
        self.reserve()
        self.sign()
        with self.assertRaises(TypeError):
            self.registry.finalize(**self.details)
        self.assertEqual(self.state(), ("reserved", None))

    def test_existing_r12_path_only_api_is_preserved(self):
        # The R12 public helper must still return a Path unless the trusted
        # operator CLI requests an explicit immutable signed-content receipt.
        output = license_issuer.issue_entitlement(
            key_path=self.pem, password=self.password,
            kid=self.details["kid"], product=self.details["product"],
            license_id=self.details["license_id"], holder="Test Organization",
            expires_at=EXPIRES, output=self.output, now=NOW)
        self.assertEqual(output, self.output)
        self.assertIsInstance(output, Path)

    def test_future_activation_entitlement_has_same_signed_content_receipt(self):
        self.reserve()
        issue = license_issuer.issue_entitlement(
            key_path=self.pem, password=self.password,
            kid=self.details["kid"], product=self.details["product"],
            license_id=self.details["license_id"], holder="Test Organization",
            expires_at=EXPIRES, output=self.output, now=NOW,
            not_before="2026-11-01T00:00:00Z", return_digest=True)
        self.assertEqual(issue[1], self.registry.finalize(
            **self.details, expected_sha256=issue[1]))
        self.assertEqual(self.state(), ("issued", issue[1]))


if __name__ == "__main__":
    unittest.main()
