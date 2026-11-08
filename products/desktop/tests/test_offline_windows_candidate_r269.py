"""R269 regression plan for private, never-uploaded Windows candidates."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "offline_windows_candidate_r269.py"
spec = importlib.util.spec_from_file_location("r269_candidate", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

from test_offline_windows_candidate_r270 import source_receipt  # synthetic receipt fixture


class CandidatePlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.space = Path(self.temp.name) / "private"
        self.space.mkdir()
        self.run = Path(self.temp.name) / "session"
        self.run.mkdir()
        self.calls = []
        # R270 requires a retained source-suite receipt before any packaging.
        (self.run / "source-suite-evidence.json").write_text(
            json.dumps(source_receipt()), encoding="utf-8")

    def runner(self, argv, cwd, timeout):
        self.calls.append((argv, cwd, timeout))
        if "report_attestation.py" in argv[2]:
            self.assertTrue("--expected-report-sha256" in argv)
        if "release_gate.py" in argv[2]:
            report = Path(argv[-1])
            report.write_text('{"synthetic":"not a real release report"}', encoding="ascii")
        return 0

    def test_exact_six_unique_apps_in_order(self):
        self.assertEqual(module.APPS, (
            "LedgerDiffLite", "InvoiceTwinScout", "SpendMapLite", "PolicyDeltaDesk",
            "GrantAuditStudioPro", "ProcureGuardStudioPro"))
        self.assertEqual(len(set(module.APPS)), 6)

    def test_full_command_plan_never_uploads_or_publishes(self):
        module._execute_plan(self.root, self.run, "python.exe", self.runner)
        commands = [x[0] for x in self.calls]
        self.assertEqual(len(commands), 3 + 6 * 5 + 7, 40)
        self.assertIn("offline_source_gate.py", commands[0][2])
        self.assertEqual(commands[1][3], "capture")
        self.assertEqual(commands[2][3], "capture")
        builds = [command for command in commands if "PyInstaller" in command]
        self.assertEqual(len(builds), 6)
        self.assertEqual([c[c.index("--name") + 1] for c in builds], list(module.APPS))
        self.assertTrue(all("--onefile" in c and "--windowed" in c and
                            "--clean" in c and "--noconfirm" in c for c in builds))
        self.assertEqual(len([c for c in commands if "release_gate.py" in c[2]]), 1)
        self.assertEqual(len([c for c in commands if "report_attestation.py" in c[2]]), 1)
        self.assertTrue(all("curl" not in " ".join(c).lower() and
                            "upload" not in " ".join(c).lower() for c in commands))
        self.assertTrue(all(cwd == self.root for _, cwd, _ in self.calls))

    def test_every_build_has_before_and_after_custody(self):
        module._execute_plan(self.root, self.run, "python.exe", self.runner)
        commands = [x[0] for x in self.calls]
        for index, cmd in enumerate(commands):
            if "PyInstaller" not in cmd:
                continue
            self.assertIn("toolchain_guard.py", commands[index-2][2])
            self.assertIn("build_input_guard.py", commands[index-1][2])
            self.assertIn("build_input_guard.py", commands[index+1][2])
            self.assertIn("toolchain_guard.py", commands[index+2][2])
        self.assertIn("toolchain_guard.py", commands[-1][2])

    def test_source_failure_short_circuits_before_packaging(self):
        def fail_first(argv, cwd, timeout):
            self.calls.append(argv)
            return 1
        with self.assertRaises(module.CandidateBuildRejected):
            module._execute_plan(self.root, self.run, "python.exe", fail_first)
        self.assertEqual(len(self.calls), 1)

    def test_any_exe_failure_prevents_inventory_or_report(self):
        def reject_second_app(argv, cwd, timeout):
            self.calls.append(argv)
            return 1 if "InvoiceTwinScout" in argv else 0
        with self.assertRaises(module.CandidateBuildRejected):
            module._execute_plan(self.root, self.run, "python.exe", reject_second_app)
        self.assertFalse(any("release_gate.py" in " ".join(c) for c in self.calls))
        self.assertFalse(any("build_inventory.py" in " ".join(c) for c in self.calls))

    def test_missing_report_rejects_even_if_fake_runner_claims_success(self):
        with self.assertRaises(module.CandidateBuildRejected):
            module._execute_plan(self.root, self.run, "python.exe", lambda a, b, c: 0)

    def test_existing_workspace_outside_repo_allowed(self):
        self.assertEqual(module._workspace(self.root, self.space), self.space)

    def test_checkout_workspace_forbidden(self):
        with self.assertRaises(module.CandidateBuildRejected):
            module._workspace(self.root, self.root)

    def test_workspace_child_of_checkout_forbidden(self):
        folder = self.root / "artifacts"
        folder.mkdir()
        with self.assertRaises(module.CandidateBuildRejected):
            module._workspace(self.root, folder)

    def test_workspace_parent_of_checkout_forbidden(self):
        with self.assertRaises(module.CandidateBuildRejected):
            module._workspace(self.root, self.root.parent)

    def test_workspace_symlink_forbidden(self):
        link = self.space / "link"
        try:
            link.symlink_to(self.run, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unavailable")
        with self.assertRaises(module.CandidateBuildRejected):
            module._workspace(self.root, link)

    def test_workspace_nonexistent_forbidden(self):
        with self.assertRaises(module.CandidateBuildRejected):
            module._workspace(self.root, self.space / "nonexistent")

    def test_windows_gate_rejects_current_nonwindows_os(self):
        with mock.patch.object(module, "_windows_x64", return_value=False):
            with self.assertRaises(module.CandidateBuildRejected):
                module.build_candidate(self.space)

    def test_failed_build_erases_new_private_run(self):
        with mock.patch.object(module, "_windows_x64", return_value=True), \
             mock.patch.object(module, "ROOT", self.root), \
             mock.patch.object(module, "_execute_plan", side_effect=module.CandidateBuildRejected("private path")):
            with self.assertRaises(module.CandidateBuildRejected) as cm:
                module.build_candidate(self.space)
        self.assertEqual(str(cm.exception), module.ERROR)
        self.assertEqual(list(self.space.iterdir()), [])

    def test_success_retains_private_candidate_folder(self):
        with mock.patch.object(module, "_windows_x64", return_value=True), \
             mock.patch.object(module, "ROOT", self.root), \
             mock.patch.object(module, "_execute_plan"):
            module.build_candidate(self.space)
        self.assertEqual(len(list(self.space.iterdir())), 1)
        self.assertTrue(list(self.space.iterdir())[0].name.startswith("fvs-r269-private-"))

    def test_cli_error_does_not_reveal_exception(self):
        with mock.patch.object(module, "build_candidate", side_effect=module.CandidateBuildRejected("private")), \
             mock.patch("sys.stderr") as output:
            self.assertEqual(module.main(["--workspace", str(self.space)]), 1)
        self.assertEqual(output.write.call_args_list[0].args[0], module.ERROR)

    def test_real_subprocess_wrapper_masks_path_and_output(self):
        with mock.patch.object(module.subprocess, "run", side_effect=OSError("customer-path")):
            self.assertEqual(module._run_child(["missing"], self.root, 5), 1)

    def test_no_shell_or_terminal_output_in_real_child(self):
        with mock.patch.object(module.subprocess, "run") as call:
            call.return_value.returncode = 0
            self.assertEqual(module._run_child(["python"], self.root, 5), 0)
        kwargs = call.call_args.kwargs
        self.assertIs(kwargs["shell"], False)
        self.assertEqual(kwargs["stdout"], module.subprocess.DEVNULL)
        self.assertEqual(kwargs["stderr"], module.subprocess.DEVNULL)
        self.assertEqual(kwargs["stdin"], module.subprocess.DEVNULL)
        self.assertEqual(kwargs["env"]["PIP_NO_INDEX"], "1")


if __name__ == "__main__":
    unittest.main()
