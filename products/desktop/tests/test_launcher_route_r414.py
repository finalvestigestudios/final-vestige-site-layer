"""R414: source-smoke success must mean six correctly routed launcher entries.

Synthetic launchers only; no claim of Windows binaries or premium release.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import offline_source_smoke_r408 as gate


class OfflineLauncherRouteR414(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.desktop = Path(self.workspace.name) / "desktop"
        self.desktop.mkdir()
        (self.desktop / "fvs_suite").mkdir()
        (self.desktop / "launchers").mkdir()
        (self.desktop / "fvs_suite" / "__init__.py").write_text("# synthetic\n", encoding="utf-8")
        (self.desktop / "fvs_suite" / "launcher.py").write_text(
            "import sys\n"
            "def launch(app):\n"
            "    if sys.argv[1:] != ['--smoke-test']:\n"
            "        raise SystemExit(7)\n", encoding="utf-8")
        (self.desktop / "offline_source_smoke_r408.py").write_bytes(Path(gate.__file__).read_bytes())
        for app, name in gate.PRODUCTS:
            self.write(name, f"from fvs_suite.launcher import launch\nlaunch({app!r})\n")

    def write(self, name: str, content: str) -> None:
        (self.desktop / "launchers" / name).write_text(content, encoding="utf-8")

    def assert_rejected_without_spawn(self, name: str, source: str) -> None:
        self.write(name, source)
        with patch.object(gate.subprocess, "run") as run:
            with self.assertRaisesRegex(gate.SourceGateError, "Unsafe desktop launcher route") as error:
                gate.run_gate(self.desktop)
            run.assert_not_called()
        self.assertNotIn(source, str(error.exception))

    def test_all_six_synthetic_launchers_really_run_both_python_modes(self):
        outcome = gate.run_gate(self.desktop)
        self.assertEqual(outcome["passed"], 12)
        self.assertEqual(outcome["required"], 12)
        self.assertEqual([entry["app"] for entry in outcome["tests"]],
                         [app for app, _ in gate.PRODUCTS])
        self.assertFalse(outcome["release_authorized"])

    def test_genuine_main_guard_entrypoint_shape_remains_valid(self):
        for app, name in gate.PRODUCTS:
            self.write(name, f'"""{name} offline entry point."""\n'
                             'from fvs_suite.launcher import launch\n'
                             f'if __name__ == "__main__":\n    launch({app!r})\n')
        self.assertEqual(gate.run_gate(self.desktop)["passed"], 12)

    def test_noop_launcher_cannot_claim_twelve_successes(self):
        self.assert_rejected_without_spawn("LedgerDiffLite.py", "# no-op that exits successfully\n")

    def test_other_valid_product_cannot_impersonate_ledger(self):
        self.assert_rejected_without_spawn("LedgerDiffLite.py",
            "from fvs_suite.launcher import launch\nlaunch('grants')\n")

    def test_premium_app_cannot_be_routed_to_free_app(self):
        self.assert_rejected_without_spawn("GrantAuditStudioPro.py",
            "from fvs_suite.launcher import launch\nlaunch('ledger')\n")

    def test_dynamic_app_identity_is_not_attested(self):
        self.assert_rejected_without_spawn("InvoiceTwinScout.py",
            "from fvs_suite.launcher import launch\nlaunch('invo' + 'ices')\n")

    def test_local_fake_launch_function_is_not_attested(self):
        self.assert_rejected_without_spawn("SpendMapLite.py",
            "def launch(app):\n    return None\nlaunch('spend')\n")

    def test_accidental_second_smoke_or_extra_side_effect_is_rejected(self):
        self.assert_rejected_without_spawn("PolicyDeltaDesk.py",
            "from fvs_suite.launcher import launch\nlaunch('policy')\nlaunch('policy')\n")

    def test_disabled_main_guard_cannot_be_attested(self):
        self.assert_rejected_without_spawn("ProcureGuardStudioPro.py",
            "from fvs_suite.launcher import launch\nif False:\n    launch('procurement')\n")

    def test_reversed_main_guard_is_rejected(self):
        self.assert_rejected_without_spawn("LedgerDiffLite.py",
            "from fvs_suite.launcher import launch\nif __name__ != '__main__':\n    launch('ledger')\n")

    def test_import_alias_is_not_silently_accepted(self):
        self.assert_rejected_without_spawn("LedgerDiffLite.py",
            "from fvs_suite.launcher import launch as run\nrun('ledger')\n")

    def test_import_only_does_not_count_as_smoke(self):
        self.assert_rejected_without_spawn("LedgerDiffLite.py",
            "from fvs_suite.launcher import launch\n")

    def test_private_source_value_not_reflected_in_rejection(self):
        confidential = "SENSITIVE_VENDOR_NAME_948201"
        self.assert_rejected_without_spawn("PolicyDeltaDesk.py",
            f"from fvs_suite.launcher import launch\nlaunch({confidential!r})\n")

    def test_syntax_error_rejected_before_subprocess(self):
        self.assert_rejected_without_spawn("LedgerDiffLite.py",
            "from fvs_suite.launcher import launch\nlaunch(\n")

    def test_consistent_receipt_still_reports_devnull_child_streams(self):
        with patch.object(gate.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as calls:
            receipt = gate.run_gate(self.desktop)
        self.assertEqual(receipt["passed"], 12)
        self.assertEqual(calls.call_count, 12)
        for invocation in calls.call_args_list:
            self.assertEqual(invocation.kwargs["stdout"], subprocess.DEVNULL)
            self.assertEqual(invocation.kwargs["stderr"], subprocess.DEVNULL)
            self.assertNotIn("shell", invocation.kwargs)


if __name__ == "__main__":
    unittest.main()
