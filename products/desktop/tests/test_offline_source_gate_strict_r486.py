"""R486: fail-closed source check evidence parsing, output and test custody."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import offline_source_gate_r485 as gate

SEP = b"-" * 70 + b"\n"
GOOD = SEP + b"Ran 2 tests in 0.002s\n\nOK\n"


class OfflineGateStrictR486Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.desktop = Path(self.tmp.name) / "products" / "desktop"
        (self.desktop / "tests").mkdir(parents=True)
        for _, filename in gate.CHECKS:
            (self.desktop / "tests" / filename).write_text("# placeholder\n")

    def _once(self, output: bytes, code: int = 0):
        def fake_run(*args, **kwargs):
            kwargs["stdout"].write(output)
            return type("Completed", (), {"returncode": code})()
        with patch.object(gate.subprocess, "run", side_effect=fake_run):
            return gate._single_check(self.desktop, "sample", gate.CHECKS[0][1],
                                      "normal", (), 600)

    def test_canonical_unittest_success_and_windows_newlines(self):
        self.assertEqual(self._once(GOOD)["result"], "PASS")
        windows = GOOD.replace(b"\n", b"\r\n")
        self.assertEqual(self._once(windows)["result"], "PASS")

    def test_fake_success_tokens_or_extra_output_fail(self):
        malformed = (
            b"Ran 2 tests in 0.002s\n\nOK\n",  # no unittest separator
            b"arbitrary OK banner\n" + SEP + b"Ran 2 tests in 0.002s\n",  # no terminal OK
            GOOD + b"DEBUG: later output\n",  # OK not terminal
            GOOD + GOOD,  # duplicate summary
            SEP + b"Ran 0 tests in 0.002s\n\nOK\n",
            SEP + b"Ran 2 tests in 0.002s\n\nOK (skipped=1)\n",
            SEP + b"Ran 2 tests in 0.002s\n\nOK (expected failures=1)\n",
            SEP + b"Ran 2 tests in 0.002s\n\nOK (unexpected successes=1)\n",
            SEP + b"Ran 2 tests in 0.002s\n\nFAILED (failures=1)\n",
            b"FAILED (failures=1)\n" + GOOD,
        )
        for output in malformed:
            with self.subTest(output=output[-80:]):
                self.assertNotEqual(self._once(output)["result"], "PASS")

    def test_full_output_scan_denies_hidden_prior_failure(self):
        # The original implementation only inspected the last 16 KiB.
        output = b"FAIL: privacy sentinel\n" + b"safe message\n" * 1800 + GOOD
        self.assertEqual(self._once(output)["result"], "FAIL")

    def test_over_one_megabyte_of_test_output_is_not_accepted(self):
        self.assertEqual(self._once(b"private tokens\n" * 80000 + GOOD),
                         {"check": "sample", "mode": "normal", "result": "FAIL", "tests": 0})

    def test_private_error_text_is_never_returned(self):
        secret = "C:/secret/vendors/finance_2026.csv"
        outcome = self._once(secret.encode() + b"\n" + GOOD)
        self.assertNotIn(secret, repr(outcome))

    def test_empty_config_cannot_vacuously_pass(self):
        with patch.object(gate, "CHECKS", ()):
            self.assertFalse(gate.verify(self.desktop)["all_passed"])
        with patch.object(gate, "MODES", ()):
            self.assertFalse(gate.verify(self.desktop)["all_passed"])

    def test_symlinked_test_file_cannot_be_executed(self):
        target = self.desktop / "tests" / gate.CHECKS[0][1]
        outside = Path(self.tmp.name) / "outside.py"
        outside.write_text("# private\n")
        target.unlink()
        try:
            target.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        with patch.object(gate.subprocess, "run") as run:
            outcome = gate._single_check(self.desktop, "sample", gate.CHECKS[0][1], "normal", (), 600)
        self.assertEqual(outcome["result"], "BLOCKED")
        run.assert_not_called()

    def test_symlinked_test_directory_cannot_be_executed(self):
        original = self.desktop / "tests"
        original.rename(self.desktop / "oldtests")
        try:
            original.symlink_to(self.desktop / "oldtests", target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        with patch.object(gate.subprocess, "run") as run:
            outcome = gate._single_check(self.desktop, "sample", gate.CHECKS[0][1], "normal", (), 600)
        self.assertEqual(outcome["result"], "BLOCKED")
        run.assert_not_called()

    def test_live_subprocess_runs_each_suite_in_two_modes(self):
        # Full real subprocess, but with synthetic tests, not repository tests.
        for _, filename in gate.CHECKS:
            (self.desktop / "tests" / filename).write_text(
                "import unittest\nclass Example(unittest.TestCase):\n"
                "  def test_one(self):\n    self.assertEqual(2 * 3, 6)\n"
                "  def test_two(self):\n    self.assertEqual(1 + 1, 2)\n")
        evidence = gate.verify(self.desktop, timeout=30)
        self.assertEqual(len(evidence["results"]), 8)
        self.assertEqual([r["tests"] for r in evidence["results"]], [2] * 8)
        self.assertTrue(evidence["all_passed"], evidence["results"])
        self.assertFalse(evidence["release_authorized"])

    def test_live_subprocess_failure_must_block(self):
        for _, filename in gate.CHECKS:
            (self.desktop / "tests" / filename).write_text(
                "import unittest\nclass Example(unittest.TestCase):\n"
                "  def test_bad(self):\n    self.assertEqual(2, 3)\n")
        evidence = gate.verify(self.desktop, timeout=30)
        self.assertFalse(evidence["all_passed"])
        self.assertEqual({r["result"] for r in evidence["results"]}, {"FAIL"})


if __name__ == "__main__":
    unittest.main()
