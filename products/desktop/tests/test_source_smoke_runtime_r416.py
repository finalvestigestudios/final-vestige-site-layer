"""R416: all twelve six-app source checks share a finite runtime budget.

These are source-runner tests using synthetic launchers, NOT native Windows EXEs.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import offline_source_smoke_r408 as gate


class SixSourceSmokeDeadlineR416(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "desktop"
        self.root.mkdir()
        (self.root / "fvs_suite").mkdir()
        (self.root / "launchers").mkdir()
        (self.root / "fvs_suite" / "__init__.py").write_text(
            "# synthetic package\n", encoding="utf-8")
        (self.root / "fvs_suite" / "launcher.py").write_text(
            "import sys\n"
            "def launch(app):\n"
            "    if sys.argv[1:] != ['--smoke-test']:\n"
            "        raise SystemExit(13)\n", encoding="utf-8")
        (self.root / "offline_source_smoke_r408.py").write_bytes(
            Path(gate.__file__).read_bytes())
        for app, filename in gate.PRODUCTS:
            (self.root / "launchers" / filename).write_text(
                f"from fvs_suite.launcher import launch\nlaunch({app!r})\n",
                encoding="utf-8")

    def _synthetic_completed(self, exit_code=0):
        return subprocess.CompletedProcess(args=[], returncode=exit_code)

    def test_real_synthetic_six_launchers_run_both_modes_under_deadline(self):
        result = gate.run_gate(self.root, timeout=20)
        self.assertEqual(result["passed"], 12)
        self.assertEqual(result["required"], 12)
        self.assertEqual([x["app"] for x in result["tests"]],
                         [x[0] for x in gate.PRODUCTS])
        self.assertFalse(result["release_authorized"])

    def test_invalid_timeouts_rejected_before_hashing_or_process(self):
        for invalid in (None, False, True, 0, -1, 121, 1.0, "90", [], {}):
            with self.subTest(timeout=repr(invalid)):
                with patch.object(gate, "source_digest") as digest, patch.object(
                        gate.subprocess, "run") as spawned:
                    with self.assertRaisesRegex(
                            gate.SourceGateError, "Unsafe desktop source smoke timeout"):
                        gate.run_gate(self.root, timeout=invalid)
                digest.assert_not_called()
                spawned.assert_not_called()

    def test_positive_integer_maximum_accepted_without_extra_seconds(self):
        with patch.object(gate, "source_digest", return_value="immutable"), patch.object(
                gate.time, "monotonic", return_value=10.0), patch.object(
                gate.subprocess, "run", return_value=self._synthetic_completed()) as run:
            result = gate.run_gate(self.root, timeout=gate.MAX_SMOKE_CHILD_SECONDS)
        self.assertEqual(result["passed"], 12)
        self.assertTrue(all(0 < item.kwargs["timeout"] <= 120
                            for item in run.call_args_list))

    def test_global_deadline_rejects_before_first_child(self):
        with patch.object(gate, "source_digest", return_value="immutable"), patch.object(
                gate.time, "monotonic", side_effect=[0.0, 301.0]), patch.object(
                gate.subprocess, "run") as spawned:
            with self.assertRaisesRegex(
                    gate.SourceGateError, "Desktop source smoke time budget exhausted"):
                gate.run_gate(self.root)
        spawned.assert_not_called()

    def test_global_deadline_counts_preflight_time(self):
        # The initial source_digest call happens after the clock starts.
        def slow_digest(_):
            return "immutable"
        with patch.object(gate, "source_digest", side_effect=slow_digest) as digest, patch.object(
                gate.time, "monotonic", side_effect=[2.0, 302.0]), patch.object(
                gate.subprocess, "run") as spawned:
            with self.assertRaises(gate.SourceGateError):
                gate.run_gate(self.root)
        self.assertGreaterEqual(digest.call_count, 2)
        spawned.assert_not_called()

    def test_global_deadline_rejects_immediately_after_slow_child(self):
        with patch.object(gate, "source_digest", return_value="immutable"), patch.object(
                gate.time, "monotonic", side_effect=[0.0, 0.0, 301.0]), patch.object(
                gate.subprocess, "run", return_value=self._synthetic_completed()) as run:
            with self.assertRaisesRegex(
                    gate.SourceGateError, "Desktop source smoke time budget exhausted"):
                gate.run_gate(self.root)
        self.assertEqual(run.call_count, 1)

    def test_second_child_gets_only_remaining_global_time(self):
        with patch.object(gate, "source_digest", return_value="immutable"), patch.object(
                gate.time, "monotonic",
                side_effect=[0.0, 200.0, 201.0, 299.0, 301.0]), patch.object(
                gate.subprocess, "run", return_value=self._synthetic_completed()) as run:
            with self.assertRaises(gate.SourceGateError):
                gate.run_gate(self.root, timeout=90)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args_list[0].kwargs["timeout"], 90)
        self.assertEqual(run.call_args_list[1].kwargs["timeout"], 1)

    def test_twelfth_child_cannot_make_overtime_receipt(self):
        clock = [0.0] + [0.0] * 22 + [299.0, 301.0]
        with patch.object(gate, "source_digest", return_value="immutable"), patch.object(
                gate.time, "monotonic", side_effect=clock), patch.object(
                gate.subprocess, "run", return_value=self._synthetic_completed()) as run:
            with self.assertRaisesRegex(gate.SourceGateError, "time budget exhausted"):
                gate.run_gate(self.root)
        self.assertEqual(run.call_count, 12)

    def test_frozen_clock_allows_exact_twelve_probes_and_no_release(self):
        with patch.object(gate, "source_digest", return_value="immutable"), patch.object(
                gate.time, "monotonic", return_value=300.0), patch.object(
                gate.subprocess, "run", return_value=self._synthetic_completed()) as run:
            receipt = gate.run_gate(self.root)
        self.assertEqual(run.call_count, 12)
        self.assertEqual(receipt["passed"], 12)
        self.assertEqual(receipt["required"], 12)
        self.assertFalse(receipt["release_authorized"])

    def test_frozen_clock_nonzero_children_cannot_forge_pass(self):
        with patch.object(gate, "source_digest", return_value="immutable"), patch.object(
                gate.time, "monotonic", return_value=1.0), patch.object(
                gate.subprocess, "run", return_value=self._synthetic_completed(3)):
            receipt = gate.run_gate(self.root)
        self.assertEqual(receipt["passed"], 0)
        self.assertEqual(receipt["required"], 12)
        self.assertFalse(receipt["release_authorized"])

    def test_private_timeout_exception_remains_redacted(self):
        private = "CLIENT_Q72_INVOICE_SECRET"
        with patch.object(gate, "source_digest", return_value="immutable"), patch.object(
                gate.time, "monotonic", return_value=0.0), patch.object(
                gate.subprocess, "run", side_effect=subprocess.TimeoutExpired(
                    cmd=private, timeout=1, output=private.encode())):
            receipt = gate.run_gate(self.root)
        self.assertEqual(receipt["passed"], 0)
        self.assertNotIn(private, repr(receipt))
        self.assertFalse(receipt["release_authorized"])

    def test_child_io_is_devnull_and_never_shell(self):
        with patch.object(gate, "source_digest", return_value="immutable"), patch.object(
                gate.time, "monotonic", return_value=0.0), patch.object(
                gate.subprocess, "run", return_value=self._synthetic_completed()) as run:
            gate.run_gate(self.root, timeout=25)
        self.assertEqual(run.call_count, 12)
        for call in run.call_args_list:
            self.assertEqual(call.kwargs["stdin"], subprocess.DEVNULL)
            self.assertEqual(call.kwargs["stdout"], subprocess.DEVNULL)
            self.assertEqual(call.kwargs["stderr"], subprocess.DEVNULL)
            self.assertNotIn("shell", call.kwargs)
            self.assertLessEqual(call.kwargs["timeout"], 25)


if __name__ == "__main__":
    unittest.main()
