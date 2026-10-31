"""R37 integration: six-app gate rejects stray material before/during smoke.

Synthetic PE fixtures never execute; mocked runner exercises call ordering.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from pe_fixture_r17 import synthetic_pe64
from release_gate import EXPECTED, GateFailure, verify


class CandidateGateIntegrationR37Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r37-gate-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.synthetic = synthetic_pe64()
        digest = hashlib.sha256(self.synthetic).hexdigest()
        for name in EXPECTED:
            (self.root / name).write_bytes(self.synthetic)
        (self.root / "SHA256SUMS.txt").write_text(
            "".join(f"{digest}  {name}\n" for name in EXPECTED), encoding="ascii",
        )

    def test_normal_all_six_integrity_only(self):
        evidence = verify(self.root)
        self.assertEqual(len(evidence["artifacts"]), 6)
        self.assertFalse(evidence["release_authorized"])

    def test_extra_manifest_alternative_rejected_before_smoke(self):
        (self.root / "SHA256SUMS.old").write_text("old")
        called = []
        with self.assertRaisesRegex(GateFailure, "unapproved"):
            verify(self.root, smoke=True, platform_name="nt",
                   runner=lambda *_a, **_k: called.append(True))
        self.assertFalse(called)

    def test_private_premium_material_rejected_before_smoke(self):
        (self.root / "premium-issuer-secret.json").write_text("not for release")
        with self.assertRaises(GateFailure) as caught:
            verify(self.root)
        self.assertNotIn("issuer-secret", str(caught.exception))

    def test_mid_smoke_stray_payload_rejected_after_first_execution(self):
        seen = []
        def runner(args, **_kw):
            seen.append(Path(args[0]).name)
            (self.root / "new-autostart.ps1").write_text("not approved")
            return SimpleNamespace(returncode=0)
        with self.assertRaisesRegex(GateFailure, "unapproved"):
            verify(self.root, smoke=True, platform_name="nt", runner=runner)
        self.assertEqual(seen, [EXPECTED[0]])

    def test_hardlink_binary_alternative_rejected_before_smoke(self):
        dst = self.root / EXPECTED[1]
        dst.unlink()
        try:
            dst.hardlink_to(self.root / EXPECTED[0])
        except OSError:
            self.skipTest("Hardlinks unsupported")
        seen = []
        with self.assertRaisesRegex(GateFailure, "ordinary"):
            verify(self.root, smoke=True, platform_name="nt",
                   runner=lambda *_a, **_k: seen.append(1))
        self.assertFalse(seen)

    def test_malicious_extra_directory_rejected(self):
        (self.root / "companion").mkdir()
        with self.assertRaisesRegex(GateFailure, "unapproved"):
            verify(self.root)

    def test_clean_mocked_windows_smoke_still_never_authorizes_release(self):
        seen = []
        def runner(args, **_kw):
            seen.append(Path(args[0]).name)
            return SimpleNamespace(returncode=0)
        result = verify(self.root, smoke=True, platform_name="nt", runner=runner)
        self.assertEqual(seen, list(EXPECTED))
        self.assertEqual(result["status"], "synthetic_smoke_only")
        self.assertFalse(result["windows_executables_verified"])
        self.assertTrue(result["smoke_simulated"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["premium_entitlement_verified"])


if __name__ == "__main__":
    unittest.main()
