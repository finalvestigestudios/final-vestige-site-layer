"""R341: six-app candidate release CLI must not print raw OS/runtime exceptions.

Faults are synthetic; no executables, private customer files or network access.
"""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import unittest
from unittest.mock import patch

import release_gate as gate

PRIVATE = "C:/PRIVATE_CLIENT_PAYROLL_2026/ledger-secret.csv"
REJECT = "REJECTED: Candidate verification could not be completed safely\n"


class ReleaseGateCliPrivateFaultR341(unittest.TestCase):
    def invoke(self, *, stage="verify", fault=None, report=False, smoke=False):
        if fault is None:
            fault = PermissionError(PRIVATE)
        stdout, stderr = io.StringIO(), io.StringIO()
        args = ["candidate-dir"]
        if smoke:
            args.append("--smoke")
        if report:
            args.extend(("--report", "private-report.json"))
        with patch.object(gate, "prepare_report_path", return_value="validated-private.json") as prep, \
             patch.object(gate, "verify", return_value={"status": "integrity_only"}) as verify, \
             patch.object(gate, "publish_report") as publish, \
             redirect_stdout(stdout), redirect_stderr(stderr):
            {"prepare": prep, "verify": verify, "publish": publish}[stage].side_effect = fault
            result = gate.main(args)
        return result, stdout.getvalue(), stderr.getvalue(), prep, verify, publish

    def check_private(self, *, stage="verify", fault=None, report=False, smoke=False):
        result, out, err, prep, verify, publish = self.invoke(
            stage=stage, fault=fault, report=report, smoke=smoke)
        self.assertEqual(result, 1)
        self.assertEqual(out, "")
        self.assertEqual(err, REJECT)
        self.assertNotIn(PRIVATE, err)
        self.assertNotIn("Traceback", err)
        publish.assert_not_called() if stage != "publish" else publish.assert_called_once()
        if stage == "prepare":
            verify.assert_not_called()
        return prep, verify, publish

    def test_verify_permission_error_is_private(self):
        self.check_private(fault=PermissionError(PRIVATE))

    def test_verify_file_not_found_is_private(self):
        self.check_private(fault=FileNotFoundError(2, "missing", PRIVATE))

    def test_verify_is_directory_error_is_private(self):
        self.check_private(fault=IsADirectoryError(PRIVATE))

    def test_verify_plain_os_error_is_private(self):
        self.check_private(fault=OSError(PRIVATE))

    def test_verify_runtime_error_is_private(self):
        self.check_private(fault=RuntimeError(PRIVATE))

    def test_verify_exception_with_chained_private_cause_is_private(self):
        try:
            raise FileNotFoundError(PRIVATE)
        except FileNotFoundError as inner:
            fault = OSError("PRIVATE_CLIENT_WRAPPED")
            fault.__cause__ = inner
        self.check_private(fault=fault)

    def test_verify_exception_never_calls_hostile_str(self):
        class HostileOSError(OSError):
            def __str__(self):
                raise AssertionError("private __str__ must not run")
        self.check_private(fault=HostileOSError(PRIVATE))

    def test_prepare_permission_denies_before_smoke(self):
        self.check_private(stage="prepare", fault=PermissionError(PRIVATE), report=True, smoke=True)

    def test_prepare_runtime_denies_before_smoke(self):
        self.check_private(stage="prepare", fault=RuntimeError(PRIVATE), report=True, smoke=True)

    def test_prepare_os_error_denies_before_smoke(self):
        self.check_private(stage="prepare", fault=OSError(PRIVATE), report=True, smoke=True)

    def test_publish_os_error_denies_release(self):
        self.check_private(stage="publish", fault=OSError(PRIVATE), report=True)

    def test_publish_runtime_error_denies_release(self):
        self.check_private(stage="publish", fault=RuntimeError(PRIVATE), report=True)

    def test_verify_error_with_report_skips_publication(self):
        _, verify, publish = self.check_private(stage="verify", fault=OSError(PRIVATE), report=True)
        verify.assert_called_once()
        publish.assert_not_called()

    def test_known_gate_failure_still_explains_failure(self):
        result, out, err, *_ = self.invoke(fault=gate.GateFailure("Checksum inventory changed"))
        self.assertEqual((result, out, err), (1, "", "REJECTED: Checksum inventory changed\n"))

    def test_known_evidence_failure_still_explains_failure(self):
        result, out, err, *_ = self.invoke(stage="publish", report=True,
                                            fault=gate.ReportEvidenceError("Evidence already exists"))
        self.assertEqual((result, out, err), (1, "", "REJECTED: Evidence already exists\n"))

    def test_keyboard_interrupt_remains_interrupt(self):
        with self.assertRaises(KeyboardInterrupt):
            self.invoke(fault=KeyboardInterrupt())

    def test_system_exit_remains_exit(self):
        with self.assertRaises(SystemExit) as err:
            self.invoke(fault=SystemExit(23))
        self.assertEqual(err.exception.code, 23)

    def test_normal_validation_has_not_authorized_release(self):
        result, out, err, *_ = self._normal()
        self.assertEqual(result, 0)
        self.assertIn("NOT release authorized", out)
        self.assertEqual(err, "")

    def _normal(self):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(gate, "verify", return_value={"status": "integrity_only"}), \
             redirect_stdout(out), redirect_stderr(err):
            result = gate.main(["candidate-dir"])
        return result, out.getvalue(), err.getvalue(), None, None, None


if __name__ == "__main__":
    unittest.main()
