"""R18: a complete checksum-matched six-app candidate is still rejected if invalid."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from pe_fixture_r17 import synthetic_pe64
from release_gate import EXPECTED, GateFailure, verify


class ReleaseGateEntrypointR18(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-gate-r18-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)

    def prepare(self, bad=None):
        checksums = []
        for name in EXPECTED:
            payload = bytearray(synthetic_pe64())
            if name == bad:
                payload[168:172] = (0x3000).to_bytes(4, "little")
            content = bytes(payload)
            (self.folder / name).write_bytes(content)
            checksums.append(f"{hashlib.sha256(content).hexdigest()}  {name}")
        (self.folder / "SHA256SUMS.txt").write_text("\n".join(checksums) + "\n", encoding="ascii")

    def test_integrity_only_passes_but_never_authorizes_release(self):
        self.prepare()
        result = verify(self.folder)
        self.assertEqual(result["status"], "integrity_only")
        self.assertFalse(result["release_authorized"])
        self.assertEqual(len(result["artifacts"]), 6)

    def test_matching_checksums_do_not_legalize_bad_entrypoint(self):
        self.prepare(bad="GrantAuditStudioPro.exe")
        with self.assertRaisesRegex(GateFailure, "GrantAuditStudioPro.exe"):
            verify(self.folder)

    def test_bad_sixth_candidate_is_rejected_before_first_smoke(self):
        self.prepare(bad="ProcureGuardStudioPro.exe")
        attempted = []
        def runner(*args, **kwargs):
            attempted.append(args)
            raise AssertionError("An invalid catalog must never execute")
        with self.assertRaisesRegex(GateFailure, "ProcureGuardStudioPro.exe"):
            verify(self.folder, smoke=True, runner=runner, platform_name="nt")
        self.assertEqual(attempted, [])


if __name__ == "__main__":
    unittest.main()
