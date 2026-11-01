"""Synthetic privacy and fail-closed contracts; NOT real AV evidence."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "defender_environment_r113.py"
# spec_from_file_location does not populate the imported module's sibling path.
# Mirror real CLI import semantics for R114's native PowerShell resolver.
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location("defender_environment_r113", SCRIPT)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def fake(out: object = "FVS_DEFENDER_COUNTS|0|0|0\n", code: object = 0):
    return SimpleNamespace(stdout=out, returncode=code)


class EnvironmentR113(unittest.TestCase):
    def setUp(self):
        # Existing runner fakes model Defender, never the Windows shell lookup.
        # R114's native locator has its own adversarial tests.
        patcher = patch.object(review.trust, "require_system_powershell",
                               return_value=Path("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"))
        patcher.start()
        self.addCleanup(patcher.stop)

    def call(self, out="FVS_DEFENDER_COUNTS|0|0|0\n", code=0):
        with patch.object(review.os, "name", "nt"):
            return review.require_zero_observations(runner=lambda *a, **k: fake(out, code))

    def test_success_is_observation_only(self):
        result = self.call()
        self.assertIn("not_malware_clearance", result)
        self.assertNotIn("authorized", result)

    def test_requires_native_windows(self):
        with patch.object(review.os, "name", "posix"):
            with self.assertRaises(review.EnvironmentHold):
                review.require_zero_observations(runner=lambda *a, **k: fake())

    def test_single_detections_fail(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("FVS_DEFENDER_COUNTS|1|0|0\n")

    def test_single_threat_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("FVS_DEFENDER_COUNTS|0|1|0\n")

    def test_single_exclusion_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("FVS_DEFENDER_COUNTS|0|0|1\n")

    def test_all_counters_positive_fail(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("FVS_DEFENDER_COUNTS|9|8|7\n")

    def test_untrusted_system_powershell_prevents_history_query(self):
        calls = []
        with patch.object(review.trust, "require_system_powershell",
                          side_effect=review.trust.PowerShellHold("PRIVATE")):
            with patch.object(review.os, "name", "nt"):
                with self.assertRaises(review.EnvironmentHold) as caught:
                    review.require_zero_observations(runner=lambda *a, **kw: calls.append(a))
        self.assertEqual(calls, [])
        self.assertNotIn("PRIVATE", str(caught.exception))

    def test_nonzero_provider_exit_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call(code=1)

    def test_non_integer_provider_exit_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call(code="0")

    def test_extra_stdout_line_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("FVS_DEFENDER_COUNTS|0|0|0\nmalicious path\n")

    def test_provider_error_string_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("C:\\Users\\customer\\private_data.csv")

    def test_missing_stdout_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("")

    def test_none_stdout_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call(None)

    def test_unicode_stdout_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("FVS_DEFENDER_COUNTS|０|0|0\n")

    def test_leading_zero_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("FVS_DEFENDER_COUNTS|00|0|0\n")

    def test_signed_count_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("FVS_DEFENDER_COUNTS|+0|0|0\n")

    def test_large_count_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("FVS_DEFENDER_COUNTS|9999999999999999999999|0|0\n")

    def test_excess_output_fails(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("x" * 9000)

    def test_powershell_timeout_fails(self):
        def timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired(args[0], 60)
        with patch.object(review.os, "name", "nt"):
            with self.assertRaises(review.EnvironmentHold):
                review.require_zero_observations(runner=timeout)

    def test_os_error_fails(self):
        def fail(*args, **kwargs):
            raise OSError("C:\\Users\\sensitive\\csv.txt")
        with patch.object(review.os, "name", "nt"):
            with self.assertRaises(review.EnvironmentHold) as cm:
                review.require_zero_observations(runner=fail)
            self.assertNotIn("sensitive", str(cm.exception))

    def test_bad_runner_value_fails(self):
        with patch.object(review.os, "name", "nt"):
            with self.assertRaises(review.EnvironmentHold):
                review.require_zero_observations(runner=lambda *a, **k: None)

    def test_exact_process_invocation_privacy(self):
        invoked = []
        def recorder(args, **kwargs):
            invoked.append((args, kwargs))
            return fake()
        with patch.object(review.os, "name", "nt"):
            review.require_zero_observations(runner=recorder)
        self.assertEqual(len(invoked), 1)
        args, kwargs = invoked[0]
        self.assertEqual(args[0], str(Path("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")))
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stderr"], subprocess.DEVNULL)
        self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertNotIn("C:\\Users", " ".join(args))
        self.assertNotIn("Remove-MpThreat", " ".join(args))
        self.assertNotIn("Set-MpPreference", " ".join(args))
        self.assertNotIn("Update-MpSignature", " ".join(args))

    def test_static_cmdlets_and_exclusion_fields(self):
        command = review.HISTORY_COMMAND
        for part in ("Get-MpThreatDetection", "Get-MpThreat ", "Get-MpPreference",
                     "ExclusionPath", "ExclusionExtension", "ExclusionProcess", "ExclusionIpAddress"):
            self.assertIn(part, command)
        self.assertNotIn("Resources", command)
        self.assertNotIn("DomainUser", command)
        self.assertNotIn("ProcessName", command)

    def test_crlf_stdout_accepted(self):
        self.assertEqual(self.call("FVS_DEFENDER_COUNTS|0|0|0\r\n"), review.OBSERVED)

    def test_unterminated_line_accepted(self):
        self.assertEqual(self.call("FVS_DEFENDER_COUNTS|0|0|0"), review.OBSERVED)

    def test_bare_carriage_return_rejected(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("FVS_DEFENDER_COUNTS|0|0|0\r")

    def test_trailing_space_rejected(self):
        with self.assertRaises(review.EnvironmentHold):
            self.call("FVS_DEFENDER_COUNTS|0|0|0 \n")

    def test_internal_code_does_not_override_system_defender(self):
        self.assertNotIn("tamper_exclusion", review.HISTORY_COMMAND)
        self.assertIn("$ErrorActionPreference='Stop'", review.HISTORY_COMMAND)


if __name__ == "__main__":
    unittest.main()
