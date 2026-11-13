"""R412: source-only smokes cannot trust unmeasured compiled import artifacts.

All fixtures are synthetic, local, and credential-free. These are not real
Windows executable or six financial-engine acceptance tests.
"""
from __future__ import annotations

import os
from pathlib import Path
import py_compile
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import offline_source_smoke_r408 as gate


class SourceImportArtifactR412(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "desktop"
        self.root.mkdir()
        (self.root / "fvs_suite").mkdir()
        (self.root / "launchers").mkdir()
        (self.root / "fvs_suite" / "__init__.py").write_text("# synthetic package\n", encoding="utf-8")
        (self.root / "fvs_suite" / "launcher.py").write_text(
            "import sys\n"
            "def launch(app):\n"
            "    if sys.argv[1:] != ['--smoke-test']:\n"
            "        raise SystemExit(7)\n", encoding="utf-8")
        for app, name in gate.PRODUCTS:
            (self.root / "launchers" / name).write_text(
                f"from fvs_suite.launcher import launch\nlaunch({app!r})\n",
                encoding="utf-8")
        (self.root / "offline_source_smoke_r408.py").write_bytes(Path(gate.__file__).read_bytes())

    def denied_before_spawn(self):
        with patch.object(gate.subprocess, "run") as run:
            with self.assertRaisesRegex(
                    gate.SourceGateError, "Untrusted compiled import"):
                gate.run_gate(self.root)
            run.assert_not_called()

    def test_real_precompiled_cache_is_rejected(self):
        source = self.root / "fvs_suite" / "launcher.py"
        cache = Path(py_compile.compile(str(source), doraise=True))
        self.assertTrue(cache.exists())
        self.denied_before_spawn()

    def test_nested_cache_is_rejected_without_following_imports(self):
        nested = self.root / "fvs_suite" / "nested" / "__pycache__"
        nested.mkdir(parents=True)
        (nested / "module.cpython-312.pyc").write_bytes(b"synthetic")
        self.denied_before_spawn()

    def test_uppercase_pyc_is_rejected_on_case_sensitive_hosts(self):
        (self.root / "fvs_suite" / "STALE.PYC").write_bytes(b"synthetic")
        self.denied_before_spawn()

    def test_sourceless_pyc_is_rejected(self):
        (self.root / "fvs_suite" / "orphan.pyc").write_bytes(b"synthetic")
        self.denied_before_spawn()

    def test_native_extension_artifacts_are_rejected(self):
        for name in ("native.pyd", "native.abi3.so", "module.dll"):
            with self.subTest(name=name):
                path = self.root / "fvs_suite" / name
                path.write_bytes(b"synthetic")
                try:
                    self.denied_before_spawn()
                finally:
                    path.unlink()

    def test_legacy_pyo_is_rejected(self):
        (self.root / "fvs_suite" / "legacy.pyo").write_bytes(b"synthetic")
        self.denied_before_spawn()

    def test_unmeasured_import_artifact_in_launcher_root_is_rejected(self):
        (self.root / "launchers" / "stale.pyc").write_bytes(b"synthetic")
        self.denied_before_spawn()

    def test_normal_non_executable_assets_remain_allowed(self):
        (self.root / "fvs_suite" / "example.json").write_text("{}", encoding="utf-8")
        (self.root / "fvs_suite" / "template.csv").write_text("A,B\n", encoding="utf-8")
        result = gate.run_gate(self.root)
        self.assertEqual(result["passed"], 12)
        self.assertEqual(result["required"], 12)
        self.assertFalse(result["release_authorized"])
        # -I alone ignores PYTHONDONTWRITEBYTECODE and generated caches here
        # before the R412 -B correction.
        self.assertFalse(list(self.root.rglob("*.pyc")))

    def test_all_twelve_children_use_isolated_no_bytecode_flags(self):
        with patch.object(gate.subprocess, "run", return_value=subprocess.CompletedProcess(
                args=[], returncode=0)) as run:
            result = gate.run_gate(self.root)
        self.assertEqual(result["passed"], 12)
        self.assertEqual(run.call_count, 12)
        for call in run.call_args_list:
            self.assertEqual(call.args[0][1:3], ["-I", "-B"])

    def test_artifact_injected_before_first_spawn_is_rejected(self):
        real = gate.source_digest
        calls = 0
        artifact = self.root / "fvs_suite" / "injected.pyc"
        def digest_with_injection(desktop):
            nonlocal calls
            calls += 1
            value = real(desktop)
            if calls == 1:
                artifact.write_bytes(b"synthetic")
            return value
        with patch.object(gate, "source_digest", side_effect=digest_with_injection):
            with patch.object(gate.subprocess, "run") as run:
                with self.assertRaises(gate.SourceGateError):
                    gate.run_gate(self.root)
                run.assert_not_called()

    def test_artifact_injected_by_first_child_stops_all_followups(self):
        artifact = self.root / "fvs_suite" / "injected.pyd"
        def inject(*args, **kwargs):
            artifact.write_bytes(b"synthetic")
            return subprocess.CompletedProcess(args=args[0], returncode=0)
        with patch.object(gate.subprocess, "run", side_effect=inject) as run:
            with self.assertRaises(gate.SourceGateError):
                gate.run_gate(self.root)
        self.assertEqual(run.call_count, 1)

    def test_blocked_error_does_not_include_file_contents_or_name(self):
        name = "PRIVATE_VENDOR_LEDGER_999.pyc"
        (self.root / "fvs_suite" / name).write_bytes(b"PRIVATE_CUSTOMER_DATA")
        with self.assertRaises(gate.SourceGateError) as context:
            gate.source_digest(self.root)
        self.assertNotIn("PRIVATE_", str(context.exception))
        self.assertNotIn(name, str(context.exception))


if __name__ == "__main__":
    unittest.main()
