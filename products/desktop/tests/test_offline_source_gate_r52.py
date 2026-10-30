"""R52: fail-closed offline tests and exact synthetic source provenance."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

DESKTOP = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fvs_offline_source_gate_r52", DESKTOP / "scripts" / "offline_source_gate.py"
)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class OfflineSourceGateR52Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r52-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.desktop = self.root / "products" / "desktop"
        self.package = self.desktop / "fvs_suite"
        self.tests = self.desktop / "tests"
        self.launchers = self.desktop / "launchers"
        for directory in (self.package, self.tests, self.launchers):
            directory.mkdir(parents=True)
        self.engine = self.package / "engine.py"
        self.engine.write_text("# deterministic synthetic engine\n", encoding="utf-8")
        self.test_source = self.tests / "test_synthetic.py"
        self.test_source.write_text("# deterministic synthetic test\n", encoding="utf-8")
        for name, _ in gate.source_gate.APPS:
            (self.launchers / f"{name}.py").write_text("# synthetic launcher\n")
        self.test_passes = []
        self.smoke_calls = []

    def pass_tests(self, optimized):
        self.test_passes.append(optimized)

    def smoke(self, app):
        self.smoke_calls.append(app)
        return [Path("synthetic-only.csv")]

    def verify(self, tests=None, smoke=None):
        return gate.verify_source_suite(
            self.root, tests or self.pass_tests, smoke or self.smoke, commit="synthetic",
        )

    def test_complete_evidence_requires_two_full_passes_and_six_smokes(self):
        report = self.verify()
        self.assertEqual(self.test_passes, [False, True])
        self.assertEqual(self.smoke_calls, [app for _, app in gate.source_gate.APPS])
        self.assertEqual(report["normal_unittest"], "PASS")
        self.assertEqual(report["optimized_unittest"], "PASS")
        self.assertTrue(report["source_smoke"]["all_six_passed"])
        self.assertEqual(len(report["test_inventory"]), 1)
        self.assertEqual(set(report["test_inventory"][0]), {"path", "sha256"})
        for field in ("released", "qd_approved", "windows_executables_verified",
                      "premium_download_authorized"):
            self.assertIs(report[field], False)
        self.assertNotIn(str(self.root), str(report))

    def test_normal_suite_failure_prevents_smoke_and_second_pass(self):
        def fail_first(optimized):
            self.test_passes.append(optimized)
            raise RuntimeError("synthetic test failure")
        with self.assertRaisesRegex(RuntimeError, "synthetic test failure"):
            self.verify(tests=fail_first)
        self.assertEqual(self.test_passes, [False])
        self.assertEqual(self.smoke_calls, [])

    def test_optimized_failure_prevents_source_smokes(self):
        def fail_second(optimized):
            self.test_passes.append(optimized)
            if optimized:
                raise RuntimeError("optimized suite failure")
        with self.assertRaisesRegex(RuntimeError, "optimized suite failure"):
            self.verify(tests=fail_second)
        self.assertEqual(self.test_passes, [False, True])
        self.assertEqual(self.smoke_calls, [])

    def test_source_rewrite_during_tests_withholds_evidence(self):
        def modify(optimized):
            self.engine.write_text("# tampered source\n")
        with self.assertRaisesRegex(RuntimeError, "changed"):
            self.verify(tests=modify)
        self.assertFalse(self.smoke_calls)

    def test_test_file_rewrite_during_tests_withholds_evidence(self):
        def modify(optimized):
            self.test_source.write_text("# tampered test\n")
        with self.assertRaisesRegex(RuntimeError, "changed"):
            self.verify(tests=modify)
        self.assertFalse(self.smoke_calls)

    def test_new_test_injected_after_first_pass_withholds_evidence(self):
        def inject(optimized):
            if not optimized:
                (self.tests / "test_injected.py").write_text("# new test\n")
        with self.assertRaisesRegex(RuntimeError, "changed"):
            self.verify(tests=inject)

    def test_test_deleted_after_optimized_pass_withholds_evidence(self):
        def delete(optimized):
            if optimized:
                self.test_source.unlink()
        with self.assertRaises((RuntimeError, ValueError)):
            self.verify(tests=delete)
        self.assertFalse(self.smoke_calls)

    def test_same_bytes_replaced_test_inode_withholds_evidence(self):
        def swap(optimized):
            if not optimized:
                payload = self.test_source.read_bytes()
                self.test_source.unlink()
                self.test_source.write_bytes(payload)
        with self.assertRaisesRegex(RuntimeError, "changed"):
            self.verify(tests=swap)

    def test_test_metadata_modified_withholds_evidence(self):
        def touch(optimized):
            info = self.test_source.stat()
            os.utime(self.test_source, ns=(info.st_atime_ns, info.st_mtime_ns + 10_000_000))
        with self.assertRaisesRegex(RuntimeError, "changed"):
            self.verify(tests=touch)

    def test_source_modified_during_last_smoke_withholds_evidence(self):
        def modify(app):
            if app == "procurement":
                self.engine.write_text("# changed in last smoke\n")
            return self.smoke(app)
        with self.assertRaisesRegex(RuntimeError, "sources changed"):
            self.verify(smoke=modify)

    def test_test_changed_during_smoke_withholds_evidence(self):
        def modify(app):
            if app == "policy":
                self.test_source.write_text("# modified after tests\n")
            return self.smoke(app)
        with self.assertRaisesRegex(RuntimeError, "changed"):
            self.verify(smoke=modify)

    def test_missing_test_is_rejected_before_running_anything(self):
        self.test_source.unlink()
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            self.verify()
        self.assertFalse(self.test_passes)
        self.assertFalse(self.smoke_calls)

    def test_unexpected_seventh_launcher_is_rejected(self):
        (self.launchers / "Unauthorized.py").write_text("# extra\n")
        with self.assertRaises(ValueError):
            self.verify()
        self.assertFalse(self.test_passes)

    def test_symlinked_test_file_is_rejected(self):
        target = self.tests / "test_injected.py"
        try:
            target.symlink_to(self.test_source)
        except (OSError, NotImplementedError):
            self.skipTest("filesystem does not support symlinks")
        with self.assertRaises(ValueError):
            self.verify()

    def test_child_tests_run_isolated_and_without_output_capture(self):
        with patch.object(gate.subprocess, "run") as proc:
            proc.return_value.returncode = 0
            gate._child_suite(self.root, False, timeout=61)
            normal = proc.call_args
            self.assertEqual(normal.args[0][1:3], ["-m", "unittest"])
            self.assertEqual(normal.kwargs["cwd"], self.root)
            self.assertEqual(normal.kwargs["stderr"], subprocess.DEVNULL)
            self.assertEqual(normal.kwargs["stdout"], subprocess.DEVNULL)
            self.assertEqual(normal.kwargs["env"]["PYTHONPATH"], str(self.desktop))
            gate._child_suite(self.root, True, timeout=61)
            self.assertEqual(proc.call_args.args[0][1:4], ["-OO", "-m", "unittest"])

    def test_child_nonzero_and_timeout_fail_closed(self):
        with patch.object(gate.subprocess, "run") as proc:
            proc.return_value.returncode = 5
            with self.assertRaisesRegex(RuntimeError, "normal regression suite failed"):
                gate._child_suite(self.root, False, timeout=61)
            proc.side_effect = subprocess.TimeoutExpired(["python"], timeout=61)
            with self.assertRaisesRegex(RuntimeError, "timed out"):
                gate._child_suite(self.root, True, timeout=61)


if __name__ == "__main__":
    unittest.main()
