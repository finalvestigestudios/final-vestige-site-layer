"""R106 fail-closed synthetic tests for bounded 13-stage machine preflight.

Test processes are simulated; NO GitHub, CMS, external sources, or working-tree
source files are modified. These tests are not independent human/QD clearance.
"""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from unittest import TestCase, mock
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import private_release_preflight as gate

SHA = "b" * 40
TEST_SECONDS = 216
TEST_TOTAL = 9060


def finished(out=b"", err=b"", code=0):
    return SimpleNamespace(returncode=code, stdout=out, stderr=err)


class RecordedRunner:
    """Require a synthetic 216-second test budget without sleeping."""

    def __init__(self, required_seconds=TEST_SECONDS):
        self.calls = []
        self.required_seconds = required_seconds

    def __call__(self, cmd, **kw):
        self.calls.append((tuple(cmd), dict(kw)))
        if cmd[0] == "git":
            if "rev-parse" in cmd:
                return finished((SHA + "\n").encode())
            if "status" in cmd:
                return finished()
            raise AssertionError("Unexpected fake git operation")
        if cmd[3] == "-m":
            if kw["timeout"] < self.required_seconds:
                raise subprocess.TimeoutExpired(cmd, kw["timeout"])
            return finished(err=f"Ran {TEST_TOTAL} tests in 215.232s\n\nOK\n".encode())
        if Path(cmd[3]).name in ("validate.py", "build.py"):
            return finished(b"native draft check OK\n")
        return finished(b'{"release_state":"HOLD","may_publish":false}\n')

    def native_calls(self):
        return [(c, kw) for c, kw in self.calls if c[0] != "git" and c[3] == "-m"]

    def other_calls(self):
        return [(c, kw) for c, kw in self.calls if c[0] != "git" and c[3] != "-m"]


class R106Fixture(TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fv-r106-bounded-hold-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "synthetic-checkout"
        self.root.mkdir()
        (self.root / ".git").mkdir()
        for sub in ("tools", "tests", "docs", "build"):
            (self.root / "preparedness" / sub).mkdir(parents=True)
        for _, script, kind in gate.STEPS:
            if kind != "tests":
                (self.root / "preparedness" / "tools" / script).write_text(
                    "# synthetic fixture only\n", encoding="utf-8")
        manifest = self.root / gate.MANIFEST
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text("{}\n", encoding="utf-8")
        self.run = RecordedRunner()

    def execute(self, *, timeout=gate.DEFAULT_STEP_TIMEOUT,
                native_unit_timeout=gate.NATIVE_UNIT_TIMEOUT):
        return gate.execute(self.root, SHA, run=self.run,
                            timeout=timeout, native_unit_timeout=native_unit_timeout)

    def test_expanded_default_is_still_strictly_bounded(self):
        self.assertEqual(gate.NATIVE_UNIT_TIMEOUT, 480)
        self.assertLessEqual(gate.NATIVE_UNIT_TIMEOUT, 1200)

    def test_other_12_original_gates_keep_180_seconds(self):
        self.assertEqual(gate.DEFAULT_STEP_TIMEOUT, 180)
        self.execute()
        self.assertEqual(len(self.run.other_calls()), 12)
        self.assertEqual({kw["timeout"] for _, kw in self.run.other_calls()}, {180})

    def test_all_13_gates_and_original_order_remain(self):
        receipt = self.execute()
        self.assertEqual(len(receipt["steps"]), 13)
        self.assertEqual([s["gate"] for s in receipt["steps"]],
                         [s[0] for s in gate.STEPS])

    def test_large_native_suite_is_still_executed(self):
        receipt = self.execute()
        self.assertEqual(len(self.run.native_calls()), 1)
        self.assertEqual(receipt["steps"][2]["native_test_count"], 9060)

    def test_success_receipt_stays_private_hold(self):
        receipt = self.execute()
        self.assertIs(receipt["may_publish"], False)
        self.assertEqual(receipt["release_state"], "HOLD")
        self.assertIs(receipt["independent_QD_approval"], False)
        self.assertIs(receipt["source_claim_accuracy_verified"], False)
        self.assertIs(receipt["qualified_medical_or_emergency_safety_review"], False)
        self.assertIs(receipt["wordpress_publishing_performed"], False)

    def test_budget_does_not_change_immutable_workflow_contract(self):
        self.assertEqual(len(gate.STEPS), 13)
        self.assertIn("seven_cluster_git_parity",
                      [name for name, _, _ in gate.STEPS])

    def test_no_shell_no_network_no_cms(self):
        self.execute()
        self.assertTrue(all(c[0][0] in (sys.executable, "git") for c in self.run.calls))
        self.assertTrue(all(kw.get("shell") is not True for _, kw in self.run.calls))
        self.assertNotIn("wordpress", str(self.run.calls).lower())
        self.assertTrue(all(c[1:3] == ("-I", "-B")
                            for c, _ in self.run.calls if c[0] != "git"))

    def test_custody_manifest_not_changed_by_fake_execution(self):
        path = self.root / gate.MANIFEST
        before = path.read_bytes()
        self.execute()
        self.assertEqual(path.read_bytes(), before)

    def test_no_undocumented_per_stage_override(self):
        self.execute()
        self.assertEqual(len(self.run.native_calls()), 1)
        self.assertEqual(self.run.native_calls()[0][1]["timeout"], 480)

    def test_receipt_fingerprint_still_matches_exact_bytes(self):
        receipt = self.execute()
        fingerprint = receipt.pop("fingerprint_sha256")
        self.assertEqual(gate.sha256(gate.canonical_json(receipt)), fingerprint)

    def test_timed_out_native_suites_stop_before_claim_and_source_gates(self):
        with self.assertRaisesRegex(gate.PreflightHold, "native_unit_suite: timed out"):
            self.execute(native_unit_timeout=180)
        self.assertFalse(any("claim_corpus_release_gate.py" in str(c)
                             for c, _ in self.run.calls))
        self.assertFalse(any("source_crosswalk_truth_gate.py" in str(c)
                             for c, _ in self.run.calls))

    def test_failure_receipt_timeout_kind_is_safe_and_explicit(self):
        with mock.patch.object(gate, "execute",
                               side_effect=gate.PreflightHold("native_unit_suite: timed out")):
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = gate.main(["--repo-root", str(self.root), "--expected-head", SHA])
        self.assertEqual(code, 2)
        failure = json.loads(stderr.getvalue())
        self.assertEqual(failure["failed_step"], "native_unit_suite")
        self.assertEqual(failure["failure_kind"], "TIMEOUT")
        self.assertIs(failure["may_publish"], False)
        self.assertNotIn(str(self.root), stderr.getvalue())

    def test_failure_receipt_nonzero_kind_is_explicit(self):
        with mock.patch.object(gate, "execute",
                               side_effect=gate.PreflightHold("native_unit_suite: exit status 4")):
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = gate.main(["--repo-root", str(self.root), "--expected-head", SHA])
        self.assertEqual(code, 2)
        result = json.loads(stderr.getvalue())
        self.assertEqual(result["failure_kind"], "EXIT_NONZERO")
        self.assertEqual(result["release_state"], "HOLD")

    def test_failure_receipt_setup_kind_is_explicit(self):
        with mock.patch.object(gate, "execute",
                               side_effect=gate.PreflightHold("dirty or untracked Preparedness source material")):
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = gate.main(["--repo-root", str(self.root), "--expected-head", SHA])
        self.assertEqual(code, 2)
        result = json.loads(stderr.getvalue())
        self.assertEqual(result["failed_step"], "setup_or_checkout")
        self.assertEqual(result["failure_kind"], "CUSTODY_OR_EXECUTION")
        self.assertIs(result["may_publish"], False)


def short_budget(seconds):
    def check(self):
        with self.assertRaisesRegex(gate.PreflightHold, "native_unit_suite: timed out"):
            self.execute(native_unit_timeout=seconds)
        self.assertEqual(len(self.run.native_calls()), 1)
    return check


def sufficient_budget(seconds):
    def check(self):
        receipt = self.execute(native_unit_timeout=seconds)
        self.assertEqual(receipt["steps"][2]["native_test_count"], TEST_TOTAL)
        self.assertEqual(self.run.native_calls()[0][1]["timeout"], seconds)
    return check


def other_gate_budget(seconds):
    def check(self):
        receipt = self.execute(timeout=seconds)
        self.assertEqual(len(receipt["steps"]), 13)
        self.assertEqual(self.run.native_calls()[0][1]["timeout"],
                         gate.NATIVE_UNIT_TIMEOUT)
        self.assertEqual({kw["timeout"] for _, kw in self.run.other_calls()}, {seconds})
    return check


def reject_timeout(value):
    def check(self):
        with self.assertRaisesRegex(gate.PreflightHold,
                                    "invalid bounded native-unit-suite timeout"):
            self.execute(native_unit_timeout=value)
        self.assertEqual(self.run.calls, [])
    return check


for n in (10, 11, 12, 35, 36, 60, 120, 179, 180, 181, 200, 215):
    setattr(R106Fixture, f"test_short_native_budget_{n}", short_budget(n))
for n in (216, 217, 240, 300, 360, 480, 600, 900, 1200):
    setattr(R106Fixture, f"test_sufficient_native_budget_{n}", sufficient_budget(n))
for n in (10, 11, 36, 90, 120, 180, 240, 300, 480, 600, 900, 1200):
    setattr(R106Fixture, f"test_non_native_budget_{n}", other_gate_budget(n))
for n, value in enumerate((None, False, True, "480", 480.0, 0, 9, -1,
                           1201, 10000, [], {}, object()), 1):
    setattr(R106Fixture, f"test_reject_invalid_native_budget_{n:02d}",
            reject_timeout(value))


if __name__ == "__main__":
    unittest.main()
