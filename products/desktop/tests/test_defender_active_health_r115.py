"""R115 fail-closed active-Defender checkpoints: synthetic tests, NOT real AV."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

DESKTOP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DESKTOP))
sys.path.insert(0, str(DESKTOP / "scripts"))
import defender_candidate_scan_r111 as av  # noqa: E402

SIX = {name: "a" * 64 for name in av.gate.EXPECTED}
CHECKSUMS = "c" * 64
PIN = "b" * 64


class DefenderActiveHealthR115(unittest.TestCase):
    """Behavioral custody checks on mocks, without opening financial files."""

    def synthetic(self, events: list[str], *, fail_health: int | None = None,
                  fail_environment: int | None = None):
        counters = {"health": 0, "environment": 0}

        def health(_scanner):
            counters["health"] += 1
            events.append("health")
            if counters["health"] == fail_health:
                raise av.AVHold("Defender became passive or unhealthy")

        def environment():
            counters["environment"] += 1
            events.append("environment")
            if counters["environment"] == fail_environment:
                raise av.AVHold("Defender history requires independent review")

        def scan(_scanner, candidate):
            events.append("scan:" + candidate.name)

        with patch.object(av, "require_native_win11"), \
             patch.object(av, "_pins", return_value=(SIX, CHECKSUMS)), \
             patch.object(av, "_unchanged"), \
             patch.object(av, "locate_defender", return_value=Path("scanner.exe")), \
             patch.object(av, "_engine_snapshot",
                          return_value=SimpleNamespace(sha256="d" * 64)), \
             patch.object(av, "_same_engine"), \
             patch.object(av, "health_check", side_effect=health), \
             patch.object(av, "_environment", side_effect=environment), \
             patch.object(av, "scan_one", side_effect=scan):
            return av.scan_candidates("PRIVATE-CANDIDATES", "PRIVATE-R9", PIN)

    def test_preflight_explicitly_demands_active_mode(self):
        self.assertIn("Get-MpComputerStatus -ErrorAction Stop", av.PREFLIGHT)
        self.assertIn("$s.AMRunningMode -cne 'Normal'", av.PREFLIGHT)
        self.assertNotIn("EDR Block Mode", av.PREFLIGHT)
        self.assertNotIn("Passive", av.PREFLIGHT)

    def test_preflight_demands_behavior_ioav_onaccess_realtime(self):
        for field in ("AMServiceEnabled", "AntivirusEnabled",
                      "RealTimeProtectionEnabled", "BehaviorMonitorEnabled",
                      "IoavProtectionEnabled", "OnAccessProtectionEnabled"):
            with self.subTest(field=field):
                self.assertIn("$s." + field + " -ne $true", av.PREFLIGHT)

    def test_preflight_retains_signed_scanner_and_fresh_definitions(self):
        for fragment in ("Get-AuthenticodeSignature", "$sig.Status -ne 'Valid'",
                         "CN=Microsoft Corporation", "AntivirusSignatureVersion",
                         "AntivirusSignatureAge -gt 3"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, av.PREFLIGHT)

    def test_complete_six_scan_chronology_has_14_health_and_7_history_checks(self):
        events: list[str] = []
        result = self.synthetic(events)
        expected = ["health", "environment"]
        for name in av.gate.EXPECTED:
            expected += ["health", "scan:" + name, "environment", "health"]
        expected += ["health"]
        self.assertEqual(events, expected)
        self.assertEqual(events.count("health"), 14)
        self.assertEqual(events.count("environment"), 7)
        self.assertEqual(len([e for e in events if e.startswith("scan:")]), 6)
        self.assertEqual(result["defender_active_health_checkpoints"], 14)
        self.assertIn("normal_mode", result["defender_active_health_policy"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["independent_malware_clearance"])
        self.assertFalse(result["premium_distribution_authorized"])
        self.assertNotIn("scanner_path", result)

    def test_initial_active_health_failure_prohibits_any_scan(self):
        events: list[str] = []
        with self.assertRaises(av.AVHold):
            self.synthetic(events, fail_health=1)
        self.assertEqual(events, ["health"])

    def test_first_prescan_active_health_failure_prohibits_any_scan(self):
        events: list[str] = []
        with self.assertRaises(av.AVHold):
            self.synthetic(events, fail_health=2)
        self.assertEqual(events, ["health", "environment", "health"])

    def test_first_postscan_protection_failure_stops_other_five(self):
        events: list[str] = []
        with self.assertRaises(av.AVHold):
            self.synthetic(events, fail_health=3)
        self.assertEqual(sum(e.startswith("scan:") for e in events), 1)
        self.assertEqual(events[-2:], ["environment", "health"])

    def test_second_prescan_protection_failure_stops_other_five(self):
        events: list[str] = []
        with self.assertRaises(av.AVHold):
            self.synthetic(events, fail_health=4)
        self.assertEqual(sum(e.startswith("scan:") for e in events), 1)
        self.assertEqual(events[-1], "health")

    def test_final_postscan_protection_failure_denies_completion(self):
        events: list[str] = []
        # The final check is independent of the final per-candidate check.
        with self.assertRaises(av.AVHold):
            self.synthetic(events, fail_health=14)
        self.assertEqual(sum(e.startswith("scan:") for e in events), 6)
        self.assertEqual(events.count("health"), 14)

    def test_detection_history_error_stops_before_first_postscan_health(self):
        events: list[str] = []
        with self.assertRaises(av.AVHold):
            self.synthetic(events, fail_environment=2)
        self.assertEqual(sum(e.startswith("scan:") for e in events), 1)
        self.assertEqual(events.count("health"), 2)

    def test_provider_timeout_redacts_path_before_any_success_claim(self):
        def timeout(*_args, **_kwargs):
            raise subprocess.TimeoutExpired("C:/Users/PRIVATE/client.csv", 1)
        with patch.object(av.trust, "require_system_powershell",
                          return_value=Path("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")):
            with self.assertRaises(av.AVHold) as caught:
                av.health_check(Path("C:/Windows Defender/MpCmdRun.exe"), runner=timeout)
        self.assertNotIn("PRIVATE", str(caught.exception))
        self.assertNotIn("client.csv", str(caught.exception))

    def test_report_never_confuses_health_checkpoints_with_malware_clearance(self):
        result = self.synthetic([])
        self.assertEqual(result["status"], "SIX_SCANS_ZERO_EXIT_UNCERTIFIED")
        self.assertIn("remediation_ambiguous", result["artifacts"][0]["defender_custom_scan"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["independent_malware_clearance"])


if __name__ == "__main__":
    unittest.main()
