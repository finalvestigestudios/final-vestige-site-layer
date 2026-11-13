"""R410: offline financial source smokes must not inherit user or CI secrets."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import offline_source_smoke_r408 as gate


class OfflineSourceEnvironmentR410(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "desktop"
        self.root.mkdir()
        (self.root / "fvs_suite").mkdir()
        (self.root / "launchers").mkdir()
        (self.root / "fvs_suite" / "__init__.py").write_text("# synthetic\n", encoding="utf-8")
        (self.root / "fvs_suite" / "launcher.py").write_text(
            "import os,sys\n"
            "def launch(app):\n"
            "    if sys.argv[1:] != ['--smoke-test'] or app not in "
            "{'ledger','invoices','spend','policy','grants','procurement'}:\n"
            "        raise SystemExit(20)\n"
            "    if os.environ.get('FVS_PRIVATE_TEST_TOKEN') or os.environ.get('GITHUB_TOKEN'):\n"
            "        raise SystemExit(21)\n", encoding="utf-8")
        for app, filename in gate.PRODUCTS:
            (self.root / "launchers" / filename).write_text(
                f"from fvs_suite.launcher import launch\nlaunch({app!r})\n", encoding="utf-8")
        (self.root / "offline_source_smoke_r408.py").write_bytes(Path(gate.__file__).read_bytes())

    def test_environment_default_denies_sensitive_and_injection_variables(self):
        inherited = {
            "GITHUB_TOKEN": "INTERNAL_PRIVATE_TOKEN", "FVS_PRIVATE_TEST_TOKEN": "SECRET",
            "AWS_SECRET_ACCESS_KEY": "SECRET", "OPENAI_API_KEY": "SECRET",
            "HTTPS_PROXY": "proxy-with-credentials", "PYTHONPATH": "/untrusted",
            "PYTHONHOME": "/untrusted", "PYTHONINSPECT": "1", "LD_PRELOAD": "/untrusted.so",
            "BASH_ENV": "/private", "PATH": "/usr/bin",
            "TMPDIR": "/tmp", "SystemRoot": r"C:\Windows",
        }
        with patch.dict(os.environ, inherited, clear=True):
            actual = gate._child_environment()
        self.assertEqual(actual, {
            "PATH": "/usr/bin", "TMPDIR": "/tmp",
            "SystemRoot": r"C:\Windows", "PYTHONDONTWRITEBYTECODE": "1",
        })
        self.assertNotIn("INTERNAL_PRIVATE_TOKEN", repr(actual))
        self.assertNotIn("proxy-with-credentials", repr(actual))

    def test_preserves_windows_runtime_keys_without_leaking_user_identity(self):
        inherited = {"systemroot": r"C:\Windows", "windir": r"C:\Windows",
                     "TEMP": r"C:\Temp", "TMP": r"C:\Temp", "PATHEXT": ".EXE",
                     "USERPROFILE": r"C:\Users\Private", "APPDATA": r"C:\Users\Private\AppData"}
        with patch.dict(os.environ, inherited, clear=True):
            child = gate._child_environment()
        self.assertEqual(set(child), {
            "systemroot", "windir", "TEMP", "TMP", "PATHEXT", "PYTHONDONTWRITEBYTECODE"})
        self.assertNotIn("Private", repr(child))

    def test_forces_no_bytecode_even_if_parent_disables_it(self):
        with patch.dict(os.environ, {"PYTHONDONTWRITEBYTECODE": "0"}, clear=True):
            self.assertEqual(gate._child_environment(), {"PYTHONDONTWRITEBYTECODE": "1"})

    def test_never_mutates_parent_environment(self):
        with patch.dict(os.environ, {"FVS_PRIVATE_TEST_TOKEN": "S", "PATH": "abc"}, clear=True):
            original = dict(os.environ)
            gate._child_environment()
            self.assertEqual(dict(os.environ), original)

    def test_all_twelve_children_receive_only_allowlisted_environment(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "SECRET", "PATH": "/bin",
                                      "FVS_PRIVATE_TEST_TOKEN": "SECRET"}, clear=True):
            with patch.object(gate.subprocess, "run", return_value=subprocess.CompletedProcess(
                    args=[], returncode=0)) as fake:
                result = gate.run_gate(self.root)
        self.assertEqual(result["passed"], 12)
        self.assertEqual(fake.call_count, 12)
        self.assertEqual(len(result["tests"]), 6)
        self.assertFalse(result["release_authorized"])
        for call in fake.call_args_list:
            self.assertEqual(call.kwargs["env"], {
                "PATH": "/bin", "PYTHONDONTWRITEBYTECODE": "1"})
            self.assertEqual(call.kwargs["stdin"], subprocess.DEVNULL)
            self.assertEqual(call.kwargs["stdout"], subprocess.DEVNULL)
            self.assertEqual(call.kwargs["stderr"], subprocess.DEVNULL)

    def test_real_twelve_processes_cannot_read_private_parent_tokens(self):
        with patch.dict(os.environ, {"FVS_PRIVATE_TEST_TOKEN": "SECRET",
                                      "GITHUB_TOKEN": "SECRET"}):
            result = gate.run_gate(self.root)
        self.assertEqual(result["passed"], result["required"])
        self.assertEqual(result["required"], 12)
        self.assertFalse(result["release_authorized"])

    def test_all_twelve_children_fail_when_synthetic_sources_do(self):
        (self.root / "fvs_suite" / "launcher.py").write_text(
            "def launch(app):\n    raise SystemExit('DO_NOT_PRINT_SECRET')\n", encoding="utf-8")
        with patch.dict(os.environ, {"GITHUB_TOKEN": "SECRET"}):
            result = gate.run_gate(self.root)
        self.assertEqual(result["passed"], 0)
        self.assertEqual(result["required"], 12)
        self.assertNotIn("DO_NOT_PRINT_SECRET", repr(result))

    def test_source_digest_still_deterministic_under_different_parent_secrets(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "A"}):
            first = gate.run_gate(self.root)
        with patch.dict(os.environ, {"GITHUB_TOKEN": "B"}):
            second = gate.run_gate(self.root)
        self.assertEqual(first, second)
        self.assertEqual(first["passed"], 12)

    def test_child_environment_has_bounded_explicit_keyset(self):
        self.assertEqual(gate._CHILD_RUNTIME_ENV, frozenset({
            "PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR"}))


if __name__ == "__main__":
    unittest.main()
