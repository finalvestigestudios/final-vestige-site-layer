"""R408 offline fallback: six source launchers, two modes, no fake release pass."""
from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import offline_source_smoke_r408 as gate


class OfflineSixSourceGateR408(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "fvs_suite").mkdir()
        (self.root / "launchers").mkdir()
        (self.root / "fvs_suite" / "__init__.py").write_text("# synthetic package\n", encoding="utf-8")
        # Source import is real, but synthetic: never claim engine/Windows tests.
        (self.root / "fvs_suite" / "launcher.py").write_text(
            "import sys\n"
            "def launch(app):\n"
            "    if sys.argv[1:] != ['--smoke-test'] or app not in "
            "{'ledger','invoices','spend','policy','grants','procurement'}:\n"
            "        raise SystemExit(21)\n", encoding="utf-8")
        (self.root / "fvs_suite" / "smoke.py").write_text("# synthetic\n", encoding="utf-8")
        for app, filename in gate.PRODUCTS:
            (self.root / "launchers" / filename).write_text(
                f"from fvs_suite.launcher import launch\nlaunch({app!r})\n", encoding="utf-8")
        (self.root / "offline_source_smoke_r408.py").write_bytes(Path(gate.__file__).read_bytes())

    def test_six_synthetic_source_launchers_pass_in_two_isolated_modes(self):
        result = gate.run_gate(self.root)
        self.assertEqual(result["passed"], 12)
        self.assertEqual(result["required"], 12)
        self.assertEqual(len(result["tests"]), 6)
        self.assertFalse(result["release_authorized"])
        self.assertEqual(result["evidence"], "SOURCE_ONLY_NOT_WINDOWS_BINARY")
        self.assertEqual(result["source_sha256"], gate.source_digest(self.root))

    def test_digest_changes_with_source_even_if_name_unchanged(self):
        old = gate.source_digest(self.root)
        (self.root / "fvs_suite" / "smoke.py").write_text("# changed\n", encoding="utf-8")
        self.assertNotEqual(old, gate.source_digest(self.root))

    def test_missing_launcher_fails_closed_before_running(self):
        (self.root / "launchers" / "SpendMapLite.py").unlink()
        with self.assertRaises(gate.SourceGateError):
            gate.run_gate(self.root)

    def test_symlinked_launcher_rejected(self):
        path = self.root / "launchers" / "SpendMapLite.py"
        path.unlink()
        try:
            path.symlink_to(self.root / "fvs_suite" / "smoke.py")
        except (NotImplementedError, OSError):
            self.skipTest("Windows test runner lacks symlink privileges")
        with self.assertRaises(gate.SourceGateError):
            gate.run_gate(self.root)

    def test_synthetic_failure_redacts_entire_child_output(self):
        (self.root / "fvs_suite" / "launcher.py").write_text(
            "def launch(app):\n"
            "    raise SystemExit('PRIVATE_PAYROLL_ID_AND_PATH')\n", encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out):
            result = gate.run_gate(self.root)
        self.assertEqual(result["passed"], 0)
        self.assertNotIn("PRIVATE_PAYROLL", repr(result) + out.getvalue())
        self.assertTrue(all(p["normal"] == "fail" and p["optimized"] == "fail"
                            for p in result["tests"]))

    def test_timeout_is_failure_without_private_process_details(self):
        with patch.object(gate.subprocess, "run", side_effect=subprocess.TimeoutExpired(
                cmd="private-path", timeout=1, output=b"SECRET")) as fake:
            result = gate.run_gate(self.root)
        self.assertEqual(fake.call_count, 12)
        self.assertEqual(result["passed"], 0)
        self.assertNotIn("SECRET", repr(result))

    def test_source_changed_during_execution_invalidates_all_evidence(self):
        source = self.root / "fvs_suite" / "smoke.py"
        def changed_once(*args, **kwargs):
            source.write_text("# altered during smoke\n", encoding="utf-8")
            return subprocess.CompletedProcess(args=args[0], returncode=0)
        with patch.object(gate.subprocess, "run", side_effect=changed_once):
            with self.assertRaisesRegex(gate.SourceGateError, "changed during"):
                gate.run_gate(self.root)

    def test_no_spawning_if_source_manifest_invalid(self):
        (self.root / "launchers" / "LedgerDiffLite.py").write_bytes(b"")
        with patch.object(gate.subprocess, "run") as fake:
            with self.assertRaises(gate.SourceGateError):
                gate.run_gate(self.root)
            fake.assert_not_called()

    def test_subprocess_invocation_is_isolated_and_no_shell(self):
        with patch.object(gate.subprocess, "run", return_value=subprocess.CompletedProcess(
                args=[], returncode=0)) as fake:
            result = gate.run_gate(self.root)
        self.assertEqual(result["passed"], 12)
        for call in fake.call_args_list:
            args, kwargs = call.args[0], call.kwargs
            self.assertEqual(args[1], "-I")
            self.assertEqual(args[-1].split("/")[-1].split("\\")[-1][-3:], ".py")
            self.assertFalse(kwargs["check"])
            self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
            self.assertEqual(kwargs["stdout"], subprocess.DEVNULL)
            self.assertEqual(kwargs["stderr"], subprocess.DEVNULL)
            self.assertNotIn("shell", kwargs)


if __name__ == "__main__":
    unittest.main()
