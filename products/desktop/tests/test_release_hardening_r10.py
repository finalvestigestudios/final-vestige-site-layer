"""R10: synthetic integrity mutations + optimization-safe executable self-checks.

Mocked PE files in these tests are NOT executable or signed Windows binaries.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
GATE_SCRIPT = ROOT / "release_gate.py"
spec = importlib.util.spec_from_file_location("fvs_r10_gate", GATE_SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


from pe_fixture_r17 import synthetic_pe64


class ArtifactDriftRegression(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r10-integrity-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.data = synthetic_pe64()
        digest = hashlib.sha256(self.data).hexdigest()
        for filename in gate.EXPECTED:
            (self.root / filename).write_bytes(self.data)
        (self.root / "SHA256SUMS.txt").write_text(
            "".join(f"{digest}  {name}\n" for name in gate.EXPECTED), encoding="ascii")

    def test_clean_mock_smoke_all_six_with_bounded_output(self):
        seen = []
        def runner(args, **kwargs):
            seen.append(Path(args[0]).name)
            self.assertEqual(kwargs["stdout"], subprocess.DEVNULL)
            self.assertEqual(kwargs["stderr"], subprocess.DEVNULL)
            self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
            return SimpleNamespace(returncode=0)
        evidence = gate.verify(self.root, smoke=True, platform_name="nt", runner=runner)
        self.assertEqual(seen, list(gate.EXPECTED))
        self.assertEqual(evidence["status"], "synthetic_smoke_only")
        self.assertFalse(evidence["windows_executables_verified"])
        self.assertTrue(evidence["smoke_simulated"])
        self.assertFalse(evidence["release_authorized"])
        self.assertTrue(all(r["smoke"] == "simulated" for r in evidence["artifacts"]))

    def test_self_modifying_binary_rejected_after_zero_exit(self):
        def runner(args, **kwargs):
            Path(args[0]).write_bytes(self.data + b"SWAPPED")
            return SimpleNamespace(returncode=0)
        with self.assertRaisesRegex(gate.GateFailure, "executable changed"):
            gate.verify(self.root, smoke=True, platform_name="nt", runner=runner)

    def test_other_executable_modified_before_next_launch(self):
        calls = []
        def runner(args, **kwargs):
            calls.append(Path(args[0]).name)
            (self.root / gate.EXPECTED[1]).write_bytes(self.data + b"ALTERED")
            return SimpleNamespace(returncode=0)
        with self.assertRaisesRegex(gate.GateFailure, "executable changed"):
            gate.verify(self.root, smoke=True, platform_name="nt", runner=runner)
        self.assertEqual(calls, [gate.EXPECTED[0]])

    def test_checksum_manifest_modified_during_smoke_rejected(self):
        def runner(args, **kwargs):
            inventory = self.root / "SHA256SUMS.txt"
            inventory.write_text(inventory.read_text(encoding="ascii") + "\n", encoding="ascii")
            return SimpleNamespace(returncode=0)
        with self.assertRaisesRegex(gate.GateFailure, "inventory changed"):
            gate.verify(self.root, smoke=True, platform_name="nt", runner=runner)

    def test_binary_replaced_with_symlink_during_smoke_rejected(self):
        target = self.root / "ordinary.bin"
        target.write_bytes(self.data)
        def runner(args, **kwargs):
            exe = Path(args[0])
            exe.unlink()
            try:
                exe.symlink_to(target)
            except (NotImplementedError, OSError):
                self.skipTest("symlink creation not available")
            return SimpleNamespace(returncode=0)
        with self.assertRaisesRegex(gate.GateFailure, "ordinary file"):
            gate.verify(self.root, smoke=True, platform_name="nt", runner=runner)

    def test_non_smoke_verification_never_implies_release(self):
        evidence = gate.verify(self.root)
        self.assertEqual(evidence["status"], "integrity_only")
        self.assertFalse(evidence["codesigning_verified"])
        self.assertFalse(evidence["malware_scan_verified"])
        self.assertFalse(evidence["premium_entitlement_verified"])


class OptimizedSmokeRegression(unittest.TestCase):
    def test_all_smoke_checks_survive_python_O(self):
        """Extract the exact _check function; run bytecode with optimize=2."""
        source = (ROOT / "fvs_suite" / "smoke.py").read_text(encoding="utf-8")
        module = ast.parse(source)
        self.assertFalse(any(isinstance(n, ast.Assert) for n in ast.walk(module)),
                         "Python -O could disable an assert-based packaged EXE check")
        functions = [n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == "_check"]
        self.assertEqual(len(functions), 1)
        isolated = ast.Module(body=functions, type_ignores=[])
        isolated = ast.fix_missing_locations(isolated)
        namespace = {}
        exec(compile(isolated, "smoke.py", "exec", optimize=2), namespace)
        namespace["_check"](True, "good")
        with self.assertRaisesRegex(RuntimeError, "smoke invariant deliberately failed"):
            namespace["_check"](False, "smoke invariant deliberately failed")

    def test_all_six_real_python_engine_smokes(self):
        """Full engine-level integration; no packaged Windows EXEs are invoked here."""
        from fvs_suite.smoke import run_smoke
        for product in ("ledger", "invoices", "spend", "policy", "grants", "procurement"):
            with self.subTest(product=product):
                outputs = run_smoke(product)
                self.assertTrue(outputs)


if __name__ == "__main__":
    unittest.main()
