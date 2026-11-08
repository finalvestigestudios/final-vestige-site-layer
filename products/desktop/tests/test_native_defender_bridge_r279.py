"""R279: private candidate acceptance requires a native Defender scan.

Synthetic plan tests below are NOT Windows build, AV or malware clearance.
The real subprocess test invokes the Defender CLI's --help import path only.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_offline_windows_candidate_r270 import source_receipt

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
RUNNER = SCRIPTS / "offline_windows_candidate_r269.py"
DEFENDER = SCRIPTS / "defender_candidate_scan_r111.py"
spec = importlib.util.spec_from_file_location("r279_private_runner", RUNNER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class NativeDefenderBridgeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "checkout"
        self.root.mkdir()
        self.session = Path(temporary.name) / "private"
        self.session.mkdir()
        (self.session / "source-suite-evidence.json").write_text(
            json.dumps(source_receipt()), encoding="utf-8")
        self.r9_bytes = b'{"synthetic":"not Windows evidence"}'
        self.defender_bytes = b'{"synthetic":"not AV evidence"}'
        self.calls = []

    def fake(self, argv, cwd, timeout):
        self.calls.append((list(argv), cwd, timeout))
        if "release_gate.py" in argv[2]:
            Path(argv[-1]).write_bytes(self.r9_bytes)
        elif "defender_candidate_scan_r111.py" in argv[2]:
            Path(argv[-1]).write_bytes(self.defender_bytes)
        return 0

    def test_mandatory_defender_follows_six_builds_and_attestation(self):
        module._execute_plan(self.root, self.session, "python.exe", self.fake)
        commands = [call[0] for call in self.calls]
        self.assertEqual(len(commands), 43)
        self.assertEqual(sum("PyInstaller" in command for command in commands), 6)
        scans = [i for i, cmd in enumerate(commands)
                 if "defender_candidate_scan_r111.py" in cmd[2]]
        attests = [i for i, cmd in enumerate(commands)
                   if "report_attestation.py" in cmd[2]]
        self.assertEqual(len(scans), 1)
        self.assertEqual(len(attests), 1)
        self.assertLess(attests[0], scans[0])
        self.assertEqual(self.calls[scans[0]][2], 3600)

    def test_scan_receives_exact_r9_pin_and_private_report_target(self):
        module._execute_plan(self.root, self.session, "python.exe", self.fake)
        command = next(call[0] for call in self.calls
                       if "defender_candidate_scan_r111.py" in call[0][2])
        self.assertEqual(command[:2], ["python.exe", "-I"])
        self.assertEqual(command[2],
                         str(self.root / "products/desktop/scripts/defender_candidate_scan_r111.py"))
        self.assertEqual(command[3], str(self.session / "dist"))
        self.assertEqual(command[4], str(self.session / "offline-candidate-evidence.json"))
        self.assertEqual(command[command.index("--expected-r9-sha256") + 1],
                         hashlib.sha256(self.r9_bytes).hexdigest())
        self.assertEqual(command[-2], "--report")
        self.assertEqual(Path(command[-1]),
                         self.session / "defender-candidate-evidence.json")

    def test_nonzero_av_exit_blocks_private_success(self):
        def fail_scan(argv, cwd, timeout):
            result = self.fake(argv, cwd, timeout)
            return 2 if "defender_candidate_scan_r111.py" in argv[2] else result
        with self.assertRaises(module.CandidateBuildRejected):
            module._execute_plan(self.root, self.session, "python.exe", fail_scan)

    def test_zero_exit_without_av_receipt_is_rejected(self):
        def missing_receipt(argv, cwd, timeout):
            result = self.fake(argv, cwd, timeout)
            if "defender_candidate_scan_r111.py" in argv[2]:
                (self.session / "defender-candidate-evidence.json").unlink()
            return result
        with self.assertRaises(module.CandidateBuildRejected):
            module._execute_plan(self.root, self.session, "python.exe", missing_receipt)

    def test_changed_av_receipt_after_scanning_is_rejected(self):
        saw_scan = False
        def mutate(argv, cwd, timeout):
            nonlocal saw_scan
            result = self.fake(argv, cwd, timeout)
            if "defender_candidate_scan_r111.py" in argv[2]:
                saw_scan = True
            elif saw_scan and "toolchain_guard.py" in argv[2]:
                (self.session / "defender-candidate-evidence.json").write_bytes(
                    b'{"synthetic":"altered after scan"}')
            return result
        with self.assertRaises(module.CandidateBuildRejected):
            module._execute_plan(self.root, self.session, "python.exe", mutate)

    def test_removed_av_receipt_after_scanning_is_rejected(self):
        saw_scan = False
        def remove(argv, cwd, timeout):
            nonlocal saw_scan
            result = self.fake(argv, cwd, timeout)
            if "defender_candidate_scan_r111.py" in argv[2]:
                saw_scan = True
            elif saw_scan and "build_input_guard.py" in argv[2]:
                (self.session / "defender-candidate-evidence.json").unlink()
            return result
        with self.assertRaises(module.CandidateBuildRejected):
            module._execute_plan(self.root, self.session, "python.exe", remove)

    def test_no_distribution_or_malware_certification_claim(self):
        self.assertIn("no distribution", module.SUCCESS)
        self.assertIn("no release authorized", module.ERROR)
        self.assertIn("no-remediation", module.SUCCESS.lower())

    def test_defender_help_cli_loads_under_python_isolation(self):
        # Real Linux/Windows Python process, but NO AV scan or exe execution.
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run(
                [sys.executable, "-I", str(DEFENDER), "--help"], cwd=cwd,
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, shell=False, timeout=30, check=False,
                env={"PATH": os.environ.get("PATH", ""), "PYTHONNOUSERSITE": "1"})
        self.assertEqual(result.returncode, 0, "Defender -I CLI imports must work")


if __name__ == "__main__":
    unittest.main()
