"""Pure-Python synthetic binary fixtures; never execute synthetic PE files."""
import hashlib
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

SCRIPT = Path(__file__).resolve().parents[1] / "release_gate.py"
spec = importlib.util.spec_from_file_location("fvs_r9_gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


from pe_fixture_r17 import synthetic_pe64


def fake_pe(machine=0x8664, signature=b"PE\x00\x00", opt=0x20B):
    return synthetic_pe64(machine=machine, signature=signature, opt=opt)


class ReleaseGateR9Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r9-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.install()

    def install(self):
        lines = []
        for app in gate.EXPECTED:
            data = fake_pe()
            (self.root / app).write_bytes(data)
            lines.append(f"{hashlib.sha256(data).hexdigest()}  {app}")
        (self.root / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="ascii")

    def test_integrity_report_is_never_release_approval(self):
        r = gate.verify(self.root)
        self.assertEqual(r["status"], "integrity_only")
        self.assertFalse(r["release_authorized"])
        self.assertFalse(r["premium_entitlement_verified"])
        self.assertEqual(len(r["artifacts"]), 6)

    def test_valid_mocked_windows_smoke_for_all_six(self):
        seen = []
        def runner(args, **_):
            seen.append(Path(args[0]).name)
            self.assertEqual(args[1], "--smoke-test")
            return SimpleNamespace(returncode=0)
        result = gate.verify(self.root, smoke=True, platform_name="nt", runner=runner)
        self.assertEqual(seen, list(gate.EXPECTED))
        self.assertEqual(result["status"], "windows_smoke_passed")
        self.assertFalse(result["release_authorized"])

    def test_integrity_failures_refuse_to_execute_any_binary(self):
        called = []
        def runner(*_args, **_kwargs):
            called.append(True)
            return SimpleNamespace(returncode=0)
        path = self.root / gate.EXPECTED[4]
        path.write_bytes(path.read_bytes() + b"X")
        with self.assertRaisesRegex(gate.GateFailure, "SHA256"):
            gate.verify(self.root, smoke=True, platform_name="nt", runner=runner)
        self.assertFalse(called)

    def test_malformed_checksum_entry_or_extra_binary_rejected(self):
        (self.root / "SHA256SUMS.txt").write_text("unsafe entry\n")
        with self.assertRaises(gate.GateFailure): gate.verify(self.root)
        self.install()
        (self.root / "unexpected.exe").write_bytes(fake_pe())
        with self.assertRaisesRegex(gate.GateFailure, "unexpected executables"):
            gate.verify(self.root)

    def test_wrong_architectures_and_headers_rejected(self):
        for data in (fake_pe(machine=0x14C), fake_pe(machine=0xAA64),
                     fake_pe(signature=b"FAIL"), fake_pe(opt=0x10B), b"not an executable"):
            path = self.root / gate.EXPECTED[0]
            path.write_bytes(data)
            manifest = self.root / "SHA256SUMS.txt"
            lines = manifest.read_text().splitlines()
            lines[0] = hashlib.sha256(data).hexdigest() + "  " + gate.EXPECTED[0]
            manifest.write_text("\n".join(lines) + "\n")
            with self.assertRaises(gate.GateFailure): gate.verify(self.root)
            self.install()

    def test_smoke_refuses_non_windows(self):
        with self.assertRaisesRegex(gate.GateFailure, "actual Windows"):
            gate.verify(self.root, smoke=True, platform_name="posix")

    def test_nonzero_exit_and_timeout_rejected(self):
        with self.assertRaisesRegex(gate.GateFailure, "exit code 3"):
            gate.verify(self.root, smoke=True, platform_name="nt",
                        runner=lambda *_a, **_k: SimpleNamespace(returncode=3))
        def slow(*_a, **_k): raise subprocess.TimeoutExpired("synthetic", 1)
        with self.assertRaisesRegex(gate.GateFailure, "timed out"):
            gate.verify(self.root, smoke=True, platform_name="nt", runner=slow)

    def test_no_clobber_report_and_cli_failure(self):
        p = self.root / "proof.json"
        self.assertEqual(gate.main([str(self.root), "--report", str(p)]), 0)
        self.assertTrue(p.exists())
        self.assertEqual(gate.main([str(self.root), "--report", str(p)]), 1)

    def test_missing_binary_rejected(self):
        (self.root / gate.EXPECTED[5]).unlink()
        with self.assertRaises(gate.GateFailure): gate.verify(self.root)

    def test_symlink_binary_rejected_if_supported(self):
        p = self.root / gate.EXPECTED[0]
        original = self.root / "original.bin"
        original.write_bytes(p.read_bytes())
        p.unlink()
        try: p.symlink_to(original)
        except (OSError, NotImplementedError): self.skipTest("symlink unavailable")
        with self.assertRaises(gate.GateFailure): gate.verify(self.root)

if __name__ == "__main__": unittest.main()
