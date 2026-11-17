"""R485: the operator source gate must never hallucinate PASS or leak test logs."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import offline_source_gate_r485 as gate


class OfflineGateR485Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.desktop = Path(self.tmp.name) / "products" / "desktop"
        (self.desktop / "tests").mkdir(parents=True)
        for _, pattern in gate.CHECKS:
            (self.desktop / "tests" / pattern).write_text("# synthetic test fixture\n")

    def _fake_run(self, output=b"----------------------------------------------------------------------\nRan 4 tests in 0.001s\n\nOK\n", code=0):
        def call(cmd, desktop, timeout):
            self.assertEqual(timeout, 600)
            self.assertIn("-B", cmd)
            self.assertEqual(desktop, self.desktop)
            self.assertEqual(gate._child_env(desktop)["PYTHONPATH"], str(self.desktop))
            self.assertNotIn("GITHUB_TOKEN", gate._child_env(desktop))
            return code, output if len(output) <= gate._MAX_EVIDENCE_BYTES else b"", len(output) > gate._MAX_EVIDENCE_BYTES
        return call

    def test_eight_real_check_invocations_normal_and_optimized(self):
        with patch.object(gate, "_bounded_child", side_effect=self._fake_run()) as call:
            result = gate.verify(self.desktop)
        self.assertEqual(call.call_count, 8)
        self.assertTrue(result["all_passed"])
        self.assertEqual(sum(x["tests"] for x in result["results"]), 32)
        self.assertEqual({x["mode"] for x in result["results"]}, {"normal", "optimized"})
        self.assertFalse(result["release_authorized"])

    def test_missing_test_file_is_blocked_without_running_it(self):
        (self.desktop / "tests" / gate.CHECKS[0][1]).unlink()
        with patch.object(gate, "_bounded_child", side_effect=self._fake_run()) as run:
            result = gate.verify(self.desktop)
        self.assertEqual(run.call_count, 6)
        self.assertFalse(result["all_passed"])
        self.assertEqual([r["result"] for r in result["results"][:2]], ["BLOCKED", "BLOCKED"])

    def test_nonzero_exit_fails_and_private_errors_never_appear(self):
        secret = b"/private/claims/client-finances.csv"
        with patch.object(gate, "_bounded_child", side_effect=self._fake_run(
                b"Ran 4 tests in 0.001s\nFAILED\n" + secret, code=1)):
            result = gate.verify(self.desktop)
        self.assertFalse(result["all_passed"])
        self.assertNotIn(secret.decode(), repr(result))
        self.assertEqual({r["result"] for r in result["results"]}, {"FAIL"})

    def test_zero_tests_or_skipped_tests_never_pass(self):
        for output in (b"Ran 0 tests in 0s\nOK", b"Ran 7 tests in 0s\nOK (skipped=1)"):
            with self.subTest(output=output):
                with patch.object(gate, "_bounded_child", side_effect=self._fake_run(output)):
                    self.assertFalse(gate.verify(self.desktop)["all_passed"])

    def test_timeout_stops_check_with_blocked_result(self):
        with patch.object(gate, "_bounded_child", side_effect=gate.subprocess.TimeoutExpired("safe", 1)):
            result = gate.verify(self.desktop)
        self.assertEqual({r["result"] for r in result["results"]}, {"BLOCKED"})

    def test_env_scrubs_sensitive_and_python_injection_vars(self):
        with patch.dict(gate.os.environ, {"GITHUB_TOKEN": "PRIVATE", "AWS_SECRET_ACCESS_KEY": "PRIVATE",
                                          "PYTHONSTARTUP": "PRIVATE", "PYTHONPATH": "/evil",
                                          "HTTPS_PROXY": "http://proxy.invalid"}):
            env = gate._child_env(self.desktop)
        self.assertEqual(env["PYTHONPATH"], str(self.desktop))
        for k in ("GITHUB_TOKEN", "AWS_SECRET_ACCESS_KEY", "PYTHONSTARTUP", "HTTPS_PROXY"):
            self.assertNotIn(k, env)

    def test_reject_unbounded_timeouts(self):
        for bad in (0, 3601, True, "600"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    gate.verify(self.desktop, bad)

    def test_missing_checkout_cli_never_passes(self):
        with patch.object(gate, "CHECKS", (("absent", "missing.py"),)):
            self.assertFalse(gate.verify(self.desktop)["all_passed"])


if __name__ == "__main__":
    unittest.main()
