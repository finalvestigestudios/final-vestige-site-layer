"""R117 hostile synthetic byte-transfer tests; NOT native six-EXE acceptance."""
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sealed_candidate_handoff_r117 as h


class HandoffR117Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.private = self.root / "private"
        self.private.mkdir(mode=0o700)
        self.dist = self.private / "dist"
        self.dist.mkdir()
        self.evidence = self.private / "r9.json"
        self.evidence.write_bytes(b'{"r9":"synthetic, NOT tested executable evidence"}\n')
        self.pin = hashlib.sha256(self.evidence.read_bytes()).hexdigest()
        for idx, name in enumerate(h.NAMES):
            (self.dist / name).write_bytes(b"MZ-FAKE-SYNTHETIC" + bytes([idx]) * 41)
        (self.dist / "SHA256SUMS.txt").write_text("SYNTHETIC NO PE ACCEPTANCE\n")
        self.key = self.private / "key.raw"
        h.generate_key(self.key)
        self.bundle = self.private / "bundle.sealed"
        self.intake = self.private / "intake"
        self.custody = mock.patch.object(h, "_custody", return_value=None)
        self.custody.start()
        self.addCleanup(self.custody.stop)

    def test_complete_streaming_six_app_roundtrip(self):
        self.assertEqual(h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)["six_exes"], 6)
        self.assertEqual(h.unseal(self.bundle, self.key, self.pin, self.intake)["six_exes"], 6)
        for name in h.NAMES:
            self.assertEqual((self.intake / "exes" / name).read_bytes(), (self.dist / name).read_bytes())
        self.assertEqual((self.intake / "evidence" / "r9-report.json").read_bytes(), self.evidence.read_bytes())
        self.assertEqual((self.intake / "exes" / "SHA256SUMS.txt").read_bytes(), (self.dist / "SHA256SUMS.txt").read_bytes())

    def test_ciphertext_contains_no_synthetic_source(self):
        h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)
        self.assertNotIn(b"SYNTHETIC NO PE ACCEPTANCE", self.bundle.read_bytes())
        self.assertNotIn(self.evidence.read_bytes(), self.bundle.read_bytes())

    def test_published_output_does_not_overwrite(self):
        self.bundle.write_bytes(b"prior")
        with self.assertRaises(h.HandoffHold):
            h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)
        self.assertEqual(self.bundle.read_bytes(), b"prior")

    def test_unseal_does_not_overwrite(self):
        h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)
        self.intake.mkdir()
        (self.intake / "important").write_text("original")
        with self.assertRaises(h.HandoffHold):
            h.unseal(self.bundle, self.key, self.pin, self.intake)
        self.assertEqual((self.intake / "important").read_text(), "original")

    def test_reused_key_does_not_reuse_nonces(self):
        h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)
        second = self.private / "bundle2.sealed"
        h.seal(self.dist, self.evidence, self.pin, self.key, second)
        self.assertNotEqual(self.bundle.read_bytes(), second.read_bytes())

    def test_wrong_key_authentication_fails_no_intake(self):
        h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)
        wrong = self.private / "other.key"
        h.generate_key(wrong)
        with self.assertRaises(h.HandoffHold):
            h.unseal(self.bundle, wrong, self.pin, self.intake)
        self.assertFalse(self.intake.exists())

    def test_ciphertext_tamper_fails_no_intake(self):
        h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)
        data = bytearray(self.bundle.read_bytes())
        data[-40] ^= 1
        self.bundle.write_bytes(data)
        with self.assertRaises(h.HandoffHold):
            h.unseal(self.bundle, self.key, self.pin, self.intake)
        self.assertFalse(self.intake.exists())

    def test_ciphertext_truncation_fails_no_intake(self):
        h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)
        self.bundle.write_bytes(self.bundle.read_bytes()[:-10])
        with self.assertRaises(h.HandoffHold):
            h.unseal(self.bundle, self.key, self.pin, self.intake)
        self.assertFalse(self.intake.exists())

    def test_extra_byte_fails_no_intake(self):
        h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)
        with self.bundle.open("ab") as stream:
            stream.write(b"X")
        with self.assertRaises(h.HandoffHold):
            h.unseal(self.bundle, self.key, self.pin, self.intake)
        self.assertFalse(self.intake.exists())

    def test_pin_mismatch_rejected_before_decryption(self):
        h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)
        with self.assertRaises(h.HandoffHold):
            h.unseal(self.bundle, self.key, "0" * 64, self.intake)
        self.assertFalse(self.intake.exists())

    def test_upfront_r9_pin_rejects_modified_r9_evidence(self):
        self.evidence.write_bytes(b'{"tampered":"yes"}')
        with self.assertRaises(h.HandoffHold):
            h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)
        self.assertFalse(self.bundle.exists())

    def test_duplicate_json_header_fields_rejected(self):
        with self.assertRaises(h.HandoffHold):
            h._unique_json(b'{"schema":"x","schema":"y"}')

    def test_duplicate_nonce_rejected(self):
        manifest = h._manifest(h._paths(self.dist, self.evidence), self.pin)
        manifest["entries"][1]["nonce"] = manifest["entries"][0]["nonce"]
        with self.assertRaises(h.HandoffHold):
            h._check_manifest(manifest, self.pin)

    def test_injected_absolute_entry_rejected(self):
        manifest = h._manifest(h._paths(self.dist, self.evidence), self.pin)
        manifest["entries"][0]["name"] = "../../private.key"
        with self.assertRaises(h.HandoffHold):
            h._check_manifest(manifest, self.pin)

    def test_injected_duplicate_entry_rejected(self):
        manifest = h._manifest(h._paths(self.dist, self.evidence), self.pin)
        manifest["entries"][0]["name"] = manifest["entries"][1]["name"]
        with self.assertRaises(h.HandoffHold):
            h._check_manifest(manifest, self.pin)

    def test_boolean_size_rejected(self):
        manifest = h._manifest(h._paths(self.dist, self.evidence), self.pin)
        manifest["entries"][0]["size"] = True
        with self.assertRaises(h.HandoffHold):
            h._check_manifest(manifest, self.pin)

    def test_oversized_candidate_rejected_before_package(self):
        (self.dist / "LedgerDiffLite.exe").unlink()
        with (self.dist / "LedgerDiffLite.exe").open("wb") as out:
            out.truncate(h.LIMIT + 1)
        with self.assertRaises(h.HandoffHold):
            h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)
        self.assertFalse(self.bundle.exists())

    def test_symlink_input_rejected(self):
        file = self.dist / "LedgerDiffLite.exe"
        target = self.private / "original"
        file.rename(target)
        try:
            file.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        with self.assertRaises(h.HandoffHold):
            h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)

    def test_insecure_key_permissions_rejected(self):
        if os.name == "nt":
            self.skipTest("POSIX file mode test")
        self.key.chmod(0o644)
        with self.assertRaises(h.HandoffHold):
            h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)

    def test_key_symlink_rejected(self):
        alias = self.private / "alias.key"
        try:
            alias.symlink_to(self.key)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        with self.assertRaises(h.HandoffHold):
            h.seal(self.dist, self.evidence, self.pin, alias, self.bundle)

    def test_bad_key_length_rejected(self):
        self.key.write_bytes(b"not 32 bytes")
        with self.assertRaises(h.HandoffHold):
            h.seal(self.dist, self.evidence, self.pin, self.key, self.bundle)

    def test_keygen_never_clobbers(self):
        existing = self.key.read_bytes()
        with self.assertRaises(h.HandoffHold):
            h.generate_key(self.key)
        self.assertEqual(self.key.read_bytes(), existing)

    def test_public_posix_destination_parent_denied(self):
        if os.name == "nt":
            self.skipTest("POSIX directory permission test")
        exposed = self.root / "public"
        exposed.mkdir(mode=0o755)
        with self.assertRaises(h.HandoffHold):
            h.seal(self.dist, self.evidence, self.pin, self.key, exposed / "bundle")

    def test_true_release_flags_cannot_pass_manifest(self):
        manifest = h._manifest(h._paths(self.dist, self.evidence), self.pin)
        manifest["release_authorized"] = True
        with self.assertRaises(h.HandoffHold):
            h._check_manifest(manifest, self.pin)
        manifest["release_authorized"] = False
        manifest["premium_distribution_authorized"] = True
        with self.assertRaises(h.HandoffHold):
            h._check_manifest(manifest, self.pin)

    def test_missing_credential_does_not_fabricate_confirmation(self):
        self.assertEqual(h.main(["seal", "--key-file", str(self.key)]), 1)
        self.assertFalse(self.bundle.exists())


# A real six-file custody gate is exercised through existing report_attestation
# in repository CI. These isolated cases confirm that R117 itself never treats
# mere checksum-only (non-smoked) synthetic claims as transport-eligible.
class StrictCustodyR117(unittest.TestCase):
    def check(self, **claims):
        import types
        claims.setdefault("status", "windows_smoke_passed")
        claims.setdefault("windows_executables_verified", True)
        claims.setdefault("smoke_simulated", False)
        fake = types.SimpleNamespace(
            verify_report=lambda *_a, **_k: {"candidate_consistency": "PASS", "evidence_pin": "PINNED"},
            _read_verified_report=lambda *_a, **_k: (b"report", "a" * 64),
            _validate_report=lambda raw: claims)
        with mock.patch.dict(sys.modules, {"report_attestation": fake}):
            h._custody(Path("synthetic-dist"), Path("synthetic-report"), "a" * 64)

    def test_claims_for_genuine_smoke_status_accepted_by_r117_wrapper(self):
        self.check()

    def test_integrity_only_report_is_not_a_six_executable_smoke(self):
        with self.assertRaises(h.HandoffHold):
            self.check(status="integrity_only", windows_executables_verified=False)

    def test_synthetic_smoke_report_is_not_accepted(self):
        with self.assertRaises(h.HandoffHold):
            self.check(status="synthetic_smoke_only", smoke_simulated=True)

    def test_false_native_windows_provenance_is_not_accepted(self):
        with self.assertRaises(h.HandoffHold):
            self.check(windows_executables_verified=False)

    def test_attested_candidate_mismatch_is_rejected(self):
        import types
        fake = types.SimpleNamespace(
            verify_report=lambda *_a, **_k: {"candidate_consistency": "FAIL", "evidence_pin": "PINNED"},
            _read_verified_report=lambda *_a, **_k: (b"report", "a" * 64),
            _validate_report=lambda _r: {"status": "windows_smoke_passed",
                                           "windows_executables_verified": True,
                                           "smoke_simulated": False})
        with mock.patch.dict(sys.modules, {"report_attestation": fake}):
            with self.assertRaises(h.HandoffHold):
                h._custody(Path("synthetic-dist"), Path("synthetic-report"), "a" * 64)


class AtomicPublicationR117(unittest.TestCase):
    def test_no_replace_directory_preserves_existing_destination(self):
        with tempfile.TemporaryDirectory() as root:
            staged = Path(root) / "staged"
            target = Path(root) / "target"
            staged.mkdir()
            target.mkdir()
            (target / "original").write_bytes(b"DO-NOT-OVERWRITE")
            with self.assertRaises((OSError, h.HandoffHold)):
                h._promote_no_replace(staged, target)
            self.assertEqual((target / "original").read_bytes(), b"DO-NOT-OVERWRITE")
            self.assertTrue(staged.exists())

    def test_no_replace_directory_promotes_without_partial_copy(self):
        with tempfile.TemporaryDirectory() as root:
            staged = Path(root) / "staged"
            target = Path(root) / "target"
            staged.mkdir()
            (staged / "proof").write_bytes(b"COMPLETE-AND-PRIVATE")
            h._promote_no_replace(staged, target)
            self.assertFalse(staged.exists())
            self.assertEqual((target / "proof").read_bytes(), b"COMPLETE-AND-PRIVATE")



if __name__ == "__main__":
    unittest.main()
