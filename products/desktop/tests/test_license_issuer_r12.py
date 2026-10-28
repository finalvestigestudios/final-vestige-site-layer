"""R12: real offline issuance + actual R11 verifier interoperability.

All private keys are ephemeral test fixtures and never enter GitHub artifacts.
"""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

import license_issuer as issuer
from fvs_suite import offline_entitlement as verifier

NOW = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
EXPIRES = "2027-10-28T12:00:00Z"


class IssuerR12Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.key = ed25519.Ed25519PrivateKey.generate()
        self.password = b"ephemeral test passphrase"
        self.key_file = self.root / "operator-only.pem"
        self.write_key(self.key, encrypted=True)
        self.target = self.root / "synthetic.fvslicense"
        self.options = dict(key_path=self.key_file, password=self.password,
                            kid="release-operator-01", product="grants",
                            license_id="synthetic-license-001", holder="Test Org",
                            expires_at=EXPIRES, output=self.target, now=NOW)

    def write_key(self, key, *, encrypted):
        protection = (serialization.BestAvailableEncryption(self.password)
                      if encrypted else serialization.NoEncryption())
        self.key_file.write_bytes(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=protection))
        self.key_file.chmod(0o600)

    def issue(self, **updates):
        return issuer.issue_entitlement(**{**self.options, **updates})

    def check(self, path=None, product="grants", now=NOW, public_key=None):
        public_key = public_key or self.key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw)
        return verifier.verify_license(path or self.target, product,
                                       trusted_keys={self.options["kid"]: public_key}, now=now)

    def test_grants_roundtrip_against_actual_r11_verifier(self):
        result = self.issue()
        self.assertEqual(result, self.target)
        self.assertEqual(self.check().license_id, self.options["license_id"])
        self.assertEqual(json.loads(result.read_text())["schema"], verifier.SCHEMA)
        self.assertEqual(result.read_bytes()[-1:], b"\n")

    def test_procurement_roundtrip_and_cross_product_denial(self):
        self.issue(product="procurement")
        self.assertEqual(self.check(product="procurement").product, "procurement")
        with self.assertRaises(verifier.EntitlementError):
            self.check(product="grants")

    def test_signed_fields_cannot_be_changed(self):
        self.issue()
        obj = json.loads(self.target.read_text())
        obj["holder"] = "Another Business"
        self.target.write_text(json.dumps(obj), encoding="utf-8")
        with self.assertRaisesRegex(verifier.EntitlementError, "signature"):
            self.check()

    def test_no_private_key_or_password_in_license(self):
        self.issue()
        data = self.target.read_bytes()
        self.assertNotIn(b"PRIVATE KEY", data)
        self.assertNotIn(self.password, data)
        self.assertFalse(verifier.TRUSTED_PUBLIC_KEYS)

    def test_future_activation_accepted_only_after_not_before(self):
        activation = "2026-11-01T00:00:00Z"
        self.issue(not_before=activation)
        with self.assertRaises(verifier.EntitlementError):
            self.check(now=NOW)
        self.assertEqual(self.check(now=datetime(2026, 11, 1, tzinfo=timezone.utc)).product,
                         "grants")

    def test_noncanonical_timestamps_are_rejected_before_write(self):
        for stamp in ("2027-10-28", "2027-10-28T12:00:00+00:00", "2026-02-30T00:00:00Z"):
            with self.subTest(stamp=stamp):
                with self.assertRaises(issuer.IssuanceError):
                    self.issue(expires_at=stamp)
                self.assertFalse(self.target.exists())

    def test_invalid_validity_windows_and_backdated_activation(self):
        for changes in (
            {"expires_at": "2026-10-28T12:00:00Z"},
            {"expires_at": "2040-10-28T12:00:00Z"},
            {"not_before": "2026-10-27T12:00:00Z"},
            {"not_before": "2027-11-01T00:00:00Z"},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(issuer.IssuanceError):
                    self.issue(**changes)
                self.assertFalse(self.target.exists())

    def test_invalid_naive_issuance_clock_is_rejected(self):
        with self.assertRaisesRegex(issuer.IssuanceError, "timezone aware"):
            self.issue(now=datetime(2026, 10, 28, 12, 0))
        self.assertFalse(self.target.exists())

    def test_invalid_product_and_identifiers_are_rejected(self):
        for changes in (
            {"product": "ledger"}, {"kid": "?bad?"},
            {"license_id": "short"[:2]}, {"holder": ""},
            {"holder": " Alice "}, {"holder": "Bad\nName"},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(issuer.IssuanceError):
                    self.issue(**changes)
                self.assertFalse(self.target.exists())

    def test_unicode_holder_roundtrip(self):
        self.issue(holder="Société de recherche")
        self.assertEqual(self.check().holder, "Société de recherche")

    def test_wrong_password_and_missing_password_fail_without_output(self):
        for password in (b"wrong", b"", "plaintext"):
            with self.subTest(password_type=type(password)):
                with self.assertRaises(issuer.IssuanceError):
                    self.issue(password=password)
                self.assertFalse(self.target.exists())

    def test_unencrypted_private_key_is_never_accepted(self):
        self.write_key(self.key, encrypted=False)
        with self.assertRaisesRegex(issuer.IssuanceError, "encrypted PKCS#8"):
            self.issue()
        self.assertFalse(self.target.exists())

    def test_encrypted_rsa_pem_is_not_an_ed25519_authority(self):
        other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.write_key(other, encrypted=True)
        with self.assertRaisesRegex(issuer.IssuanceError, "Ed25519"):
            self.issue()
        self.assertFalse(self.target.exists())

    def test_unbounded_and_missing_key_files_fail_closed(self):
        self.key_file.write_bytes(b"X" * (issuer.MAX_KEY_BYTES + 1))
        self.key_file.chmod(0o600)
        with self.assertRaises(issuer.IssuanceError):
            self.issue()
        with self.assertRaises(issuer.IssuanceError):
            self.issue(key_path=self.root / "absent.pem")
        self.assertFalse(self.target.exists())

    def test_key_inside_git_repository_is_rejected(self):
        repo = self.root / "repo"
        (repo / ".git").mkdir(parents=True)
        inside = repo / "signing-key.pem"
        inside.write_bytes(self.key_file.read_bytes())
        inside.chmod(0o600)
        with self.assertRaisesRegex(issuer.IssuanceError, "outside Git"):
            self.issue(key_path=inside)
        self.assertFalse(self.target.exists())

    def test_symlink_key_is_rejected(self):
        alias = self.root / "alias.pem"
        try:
            alias.symlink_to(self.key_file)
        except (NotImplementedError, OSError):
            self.skipTest("Symlinks unavailable")
        with self.assertRaisesRegex(issuer.IssuanceError, "symlink"):
            self.issue(key_path=alias)
        self.assertFalse(self.target.exists())

    def test_output_collision_never_overwrites(self):
        self.target.write_bytes(b"existing customer data")
        with self.assertRaisesRegex(issuer.IssuanceError, "already exists"):
            self.issue()
        self.assertEqual(self.target.read_bytes(), b"existing customer data")

    def test_symlink_output_collision_never_overwrites_target(self):
        valuable = self.root / "valuable.txt"
        valuable.write_bytes(b"DO NOT DELETE")
        try:
            self.target.symlink_to(valuable)
        except (NotImplementedError, OSError):
            self.skipTest("Symlinks unavailable")
        with self.assertRaisesRegex(issuer.IssuanceError, "already exists"):
            self.issue()
        self.assertEqual(valuable.read_bytes(), b"DO NOT DELETE")

    def test_bad_output_extension_and_parent_do_not_create_files(self):
        for path in (self.root / "wrong.json", self.root / "missing" / "license.fvslicense"):
            with self.subTest(path=path):
                with self.assertRaisesRegex(issuer.IssuanceError, "Output"):
                    self.issue(output=path)
                self.assertFalse(path.exists())

    @unittest.skipUnless(os.name == "posix", "POSIX file modes only")
    def test_private_key_must_be_owner_only(self):
        self.key_file.chmod(0o644)
        with self.assertRaisesRegex(issuer.IssuanceError, "owner-only"):
            self.issue()
        self.assertFalse(self.target.exists())

    @unittest.skipUnless(os.name == "posix", "POSIX file modes only")
    def test_created_entitlement_is_owner_only(self):
        self.issue()
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o600)

    def test_cli_refuses_noninteractive_passphrase_injection(self):
        arguments = ["--key", str(self.key_file), "--kid", self.options["kid"],
                     "--product", "grants", "--license-id", "synthetic-license-001",
                     "--holder", "Test Org", "--expires-at", EXPIRES,
                     "--output", str(self.target), "--confirm-issue"]
        with patch.object(issuer.sys.stdin, "isatty", return_value=False), \
             patch.object(issuer.getpass, "getpass") as secret, \
             redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                issuer.main(arguments)
        self.assertEqual(caught.exception.code, 2)
        secret.assert_not_called()
        self.assertFalse(self.target.exists())

    def test_cli_requires_explicit_issuance_acknowledgement(self):
        with patch.object(issuer.getpass, "getpass") as secret, redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                issuer.main(["--key", str(self.key_file), "--kid", "release-operator-01",
                             "--product", "grants", "--license-id", "synthetic-license-001",
                             "--holder", "Test Org", "--expires-at", EXPIRES,
                             "--output", str(self.target)])
        self.assertEqual(caught.exception.code, 2)
        secret.assert_not_called()
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
