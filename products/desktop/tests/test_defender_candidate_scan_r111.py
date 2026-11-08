"""R111 synthetic offline Defender gate regressions; no real AV or EXEs scanned."""
from __future__ import annotations

import copy
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "defender_candidate_scan_r111.py"
# This test uses spec_from_file_location, which does not add the script folder
# to sys.path as direct CLI execution would. Match the CLI import contract.
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location("defender_candidate_scan_r111", SCRIPT)
av = importlib.util.module_from_spec(spec)
spec.loader.exec_module(av)

ZERO = SimpleNamespace(returncode=0)
SIX = {name: "a" * 64 for name in av.gate.EXPECTED}
PINNED = "b" * 64
CHECKSUMS = "c" * 64


class DefenderR111(unittest.TestCase):
    def setUp(self):
        # Existing runner fakes model Defender, never the Windows shell lookup.
        # R114's native locator has its own adversarial tests.
        patcher = patch.object(av.trust, "require_system_powershell",
                               return_value=Path("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_six_fixed_products_and_two_premium(self):
        self.assertEqual(len(av.gate.EXPECTED), 6)
        self.assertIn("GrantAuditStudioPro.exe", av.gate.EXPECTED)
        self.assertIn("ProcureGuardStudioPro.exe", av.gate.EXPECTED)

    def test_no_native_claim_on_linux_or_windows_server(self):
        if os.name != "nt":
            with self.assertRaises(av.AVHold):
                av.require_native_win11()
        # Fake Windows Server product_type, not just the shared Win11 build.
        with patch.object(av.os, "name", "nt"), \
             patch.object(av.platform, "machine", return_value="AMD64"), \
             patch.object(av.sys, "getwindowsversion",
                          create=True, return_value=SimpleNamespace(build=26100, product_type=3)):
            with self.assertRaisesRegex(av.AVHold, "Windows 11"):
                av.require_native_win11()

    def test_windows_10_workstation_denied(self):
        with patch.object(av.os, "name", "nt"), \
             patch.object(av.platform, "machine", return_value="AMD64"), \
             patch.object(av.sys, "getwindowsversion",
                          create=True, return_value=SimpleNamespace(build=19045, product_type=1)):
            with self.assertRaises(av.AVHold):
                av.require_native_win11()

    def test_non_x64_workstation_denied(self):
        with patch.object(av.os, "name", "nt"), \
             patch.object(av.platform, "machine", return_value="ARM64"):
            with self.assertRaises(av.AVHold):
                av.require_native_win11()

    def test_win11_workstation_preflight_success_is_not_release(self):
        with patch.object(av.os, "name", "nt"), \
             patch.object(av.platform, "machine", return_value="AMD64"), \
             patch.object(av.sys, "getwindowsversion",
                          create=True, return_value=SimpleNamespace(build=26100, product_type=1)):
            self.assertIsNone(av.require_native_win11())

    def test_missing_defender_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            data, files = Path(temp) / "Data", Path(temp) / "Files"
            data.mkdir()
            files.mkdir()
            with patch.object(av.install, "native_roots", return_value=(data, files)):
                with self.assertRaises(av.AVHold):
                    av.locate_defender()

    def test_locate_defender_prefers_known_local_install(self):
        with tempfile.TemporaryDirectory() as temp:
            data, files = Path(temp) / "Data", Path(temp) / "Files"
            data.mkdir()
            files.mkdir()
            executable = files / "Windows Defender" / "MpCmdRun.exe"
            executable.parent.mkdir()
            executable.write_bytes(b"synthetic unsigned scanner - discovery only")
            with patch.object(av.install, "native_roots", return_value=(data, files)):
                self.assertEqual(av.locate_defender(), executable)

    def test_newest_defender_platform_precedes_legacy_engine(self):
        with tempfile.TemporaryDirectory() as temp:
            data, files = Path(temp) / "Data", Path(temp) / "Files"
            data.mkdir()
            files.mkdir()
            current = data / "Microsoft" / "Windows Defender" / "Platform" / "4.18.3" / "MpCmdRun.exe"
            older = data / "Microsoft" / "Windows Defender" / "Platform" / "4.18.2" / "MpCmdRun.exe"
            legacy = files / "Windows Defender" / "MpCmdRun.exe"
            for path in (current, older, legacy):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"synthetic scanner discovery only")
            with patch.object(av.install, "native_roots", return_value=(data, files)):
                self.assertEqual(av.locate_defender(), current)

    def test_symlink_scanner_is_denied(self):
        with tempfile.TemporaryDirectory() as temp:
            data, files = Path(temp) / "Data", Path(temp) / "Files"
            data.mkdir()
            files.mkdir()
            target = Path(temp) / "other.exe"
            target.write_bytes(b"synthetic")
            known = files / "Windows Defender" / "MpCmdRun.exe"
            known.parent.mkdir()
            try:
                known.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlink support unavailable")
            with patch.object(av.install, "native_roots", return_value=(data, files)):
                with self.assertRaises(av.AVHold):
                    av.locate_defender()

    def test_native_known_folder_failure_denies_all_scans_and_redacts_path(self):
        with patch.object(av.install, "native_roots",
                          side_effect=av.install.InstallHold("C:/Users/PRIVATE/customer.csv")):
            with self.assertRaises(av.AVHold) as caught:
                av.locate_defender()
        self.assertNotIn("PRIVATE", str(caught.exception))
        self.assertNotIn("customer.csv", str(caught.exception))

    def test_tampered_environment_cannot_select_attacker_scanner(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            data, files = base / "Data", base / "Files"
            data.mkdir()
            files.mkdir()
            genuine = files / "Windows Defender" / "MpCmdRun.exe"
            genuine.parent.mkdir()
            genuine.write_bytes(b"synthetic genuine-path stand-in")
            attacker = base / "Attacker" / "Windows Defender" / "MpCmdRun.exe"
            attacker.parent.mkdir(parents=True)
            attacker.write_bytes(b"synthetic attacker stand-in")
            with patch.dict(os.environ, {"ProgramData": str(base / "Attacker"),
                                         "ProgramFiles": str(base / "Attacker")}), \
                 patch.object(av.install, "native_roots", return_value=(data, files)):
                self.assertEqual(av.locate_defender(), genuine)


    def test_scan_invokes_synchronous_custom_file_only(self):
        calls = []
        name = Path("C:/PRIVATE/LedgerDiffLite.exe")
        def runner(args, **kwargs):
            calls.append((args, kwargs))
            return ZERO
        av.scan_one(Path("C:/Windows Defender/MpCmdRun.exe"), name, runner=runner)
        self.assertEqual(calls[0][0][1:5], ["-Scan", "-ScanType", "3", "-File"])
        self.assertEqual(calls[0][0][-2], str(name))
        self.assertEqual(calls[0][0][-1], "-DisableRemediation")
        self.assertIs(calls[0][1]["shell"], False)
        self.assertEqual(calls[0][1]["timeout"], 360)
        self.assertEqual(calls[0][1]["stdout"], subprocess.DEVNULL)
        self.assertEqual(calls[0][1]["stderr"], subprocess.DEVNULL)
        self.assertEqual(calls[0][1]["stdin"], subprocess.DEVNULL)

    def test_untrusted_filename_is_argument_not_shell_script(self):
        bad = Path("C:/private/odd'; Write-Host leaked; #.exe")
        args = []
        def runner(command, **_):
            args.extend(command)
            return ZERO
        av.scan_one(Path("C:/Defender/MpCmdRun.exe"), bad, runner=runner)
        self.assertEqual(args[-2], str(bad))
        self.assertEqual(args[-1], "-DisableRemediation")
        self.assertNotIn("powershell.exe", args)

    def test_nonzero_defender_exit_denied(self):
        for rc in (1, 2, -1, 5):
            with self.subTest(rc=rc):
                with self.assertRaises(av.AVHold):
                    av.scan_one(Path("scanner.exe"), Path("LedgerDiffLite.exe"),
                                runner=lambda *a, **kw: SimpleNamespace(returncode=rc))

    def test_timeout_denied_without_exception_contents(self):
        def runner(*_args, **_kwargs):
            raise subprocess.TimeoutExpired("SENSITIVE PATH", timeout=1)
        with self.assertRaisesRegex(av.AVHold, "could not complete") as captured:
            av.scan_one(Path("scanner.exe"), Path("file.exe"), runner=runner)
        self.assertNotIn("SENSITIVE", str(captured.exception))

    def test_missing_scanner_denied(self):
        def runner(*_args, **_kwargs):
            raise FileNotFoundError("SENSITIVE\u00a0PATH")
        with self.assertRaises(av.AVHold) as caught:
            av.scan_one(Path("scanner.exe"), Path("file.exe"), runner=runner)
        self.assertNotIn("SENSITIVE", str(caught.exception))

    def test_mock_returncode_bool_rejected(self):
        with self.assertRaises(av.AVHold):
            av.scan_one(Path("scanner.exe"), Path("file.exe"),
                        runner=lambda *a, **kw: SimpleNamespace(returncode=False))

    def test_health_preflight_checks_signed_active_fresh_defender(self):
        saved = []
        def runner(args, **kwargs):
            saved.append((args, kwargs))
            return ZERO
        av.health_check(Path("C:/Windows/Defender.exe"), runner=runner)
        self.assertEqual(saved[0][0][:3],
                         [str(Path("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")), "-NoProfile", "-NonInteractive"])
        self.assertIn("Get-AuthenticodeSignature", saved[0][0][-1])
        self.assertIn("Get-MpComputerStatus", saved[0][0][-1])
        self.assertIn("RealTimeProtectionEnabled", saved[0][0][-1])
        self.assertIn("AntivirusSignatureAge", saved[0][0][-1])
        self.assertEqual(saved[0][1]["env"]["FVS_DEFENDER_SCANNER"],
                         str(Path("C:/Windows/Defender.exe")))

    def test_untrusted_system_powershell_prevents_health_command(self):
        calls = []
        with patch.object(av.trust, "require_system_powershell",
                          side_effect=av.trust.PowerShellHold("PRIVATE")):
            with self.assertRaises(av.AVHold) as caught:
                av.health_check(Path("scanner.exe"),
                                runner=lambda *a, **kw: calls.append(a))
        self.assertEqual(calls, [])
        self.assertNotIn("PRIVATE", str(caught.exception))

    def test_health_nonzero_refused(self):
        with self.assertRaises(av.AVHold):
            av.health_check(Path("scanner.exe"),
                            runner=lambda *a, **kw: SimpleNamespace(returncode=22))

    def test_missing_independent_r9_pin_denied(self):
        for pin in ("", "A"*64, "0"*63, "f"*65, None, True):
            with self.subTest(pin=pin):
                with self.assertRaises(av.AVHold):
                    av._pins(Path("dist"), Path("r9.json"), pin)

    def test_r9_integrity_only_cannot_be_av_basis(self):
        raw_record = {"status": "integrity_only",
                      "windows_executables_verified": False,
                      "checksums_sha256": CHECKSUMS,
                      "artifacts": [{"name": k, "sha256": v} for k, v in SIX.items()]}
        with patch.object(av.attestation, "verify_report",
                          return_value={"candidate_consistency": "PASS", "evidence_pin": "PINNED"}), \
             patch.object(av.attestation, "_read_verified_report", return_value=(b"{}", PINNED)), \
             patch.object(av.attestation, "_validate_report", return_value=raw_record):
            with self.assertRaises(av.AVHold):
                av._pins(Path("dist"), Path("r9.json"), PINNED)

    def test_r9_pinned_six_smokes_admitted(self):
        raw_record = {"status": "windows_smoke_passed",
                      "windows_executables_verified": True,
                      "checksums_sha256": CHECKSUMS,
                      "artifacts": [{"name": k, "sha256": v} for k, v in SIX.items()]}
        with patch.object(av.attestation, "verify_report",
                          return_value={"candidate_consistency": "PASS", "evidence_pin": "PINNED"}), \
             patch.object(av.attestation, "_read_verified_report", return_value=(b"{}", PINNED)), \
             patch.object(av.attestation, "_validate_report", return_value=raw_record):
            self.assertEqual(av._pins(Path("dist"), Path("r9.json"), PINNED),
                             (SIX, CHECKSUMS))

    def test_changed_candidate_denied(self):
        expected = {"status": "integrity_only", "checksums_sha256": CHECKSUMS,
                    "artifacts": [{"name": k, "sha256": v} for k, v in SIX.items()]}
        changed = copy.deepcopy(expected)
        changed["artifacts"][0]["sha256"] = "d"*64
        with patch.object(av.gate, "verify", return_value=changed):
            with self.assertRaises(av.AVHold):
                av._unchanged(Path("dist"), SIX, CHECKSUMS)

    def test_changed_checksum_inventory_denied(self):
        observed = {"status": "integrity_only", "checksums_sha256": "d"*64,
                    "artifacts": [{"name": k, "sha256": v} for k, v in SIX.items()]}
        with patch.object(av.gate, "verify", return_value=observed):
            with self.assertRaises(av.AVHold):
                av._unchanged(Path("dist"), SIX, CHECKSUMS)

    def test_synthetic_flow_scans_six_twice_pins_and_never_authorizes(self):
        with patch.object(av, "require_native_win11"), \
             patch.object(av, "_pins", return_value=(SIX, CHECKSUMS)), \
             patch.object(av, "_unchanged") as verified, \
             patch.object(av, "locate_defender", return_value=Path("scanner.exe")), \
             patch.object(av, "_engine_snapshot", return_value=SimpleNamespace(sha256="d"*64)), \
             patch.object(av, "_same_engine") as scanner_verified, \
             patch.object(av, "health_check") as health, \
             patch.object(av, "_environment") as environment_check, \
             patch.object(av, "scan_one") as scan:
            result = av.scan_candidates("private-dist", "private-r9", PINNED)
        self.assertEqual(scan.call_count, 6)
        self.assertEqual(health.call_count, 14)
        self.assertEqual(result["defender_active_health_checkpoints"], 14)
        self.assertIn("normal_mode", result["defender_active_health_policy"])
        self.assertEqual(environment_check.call_count, 7)
        self.assertEqual(verified.call_count, 14)
        self.assertEqual(scanner_verified.call_count, 14)
        self.assertEqual(result["scanner_sha256"], "d" * 64)
        self.assertEqual(result["scanner_custody"],
                         "same_signed_engine_sha256_and_file_identity_observed")
        self.assertEqual([r["name"] for r in result["artifacts"]],
                         list(av.gate.EXPECTED))
        self.assertTrue(all(x["defender_custom_scan"] == "zero_exit_result_remediation_ambiguous" for x in result["artifacts"]))
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["independent_malware_clearance"])
        self.assertFalse(result["premium_distribution_authorized"])
        self.assertEqual(result["defender_environment_observations"], 7)
        self.assertEqual(result["defender_environment_status"], av.environment.OBSERVED)
        self.assertNotIn("scanner_path", result)

    def test_mid_scan_failure_has_no_partial_success(self):
        seen = []
        def failing(scanner, candidate):
            seen.append(candidate.name)
            if len(seen) == 3:
                raise av.AVHold("a scan failed")
        with patch.object(av, "require_native_win11"), \
             patch.object(av, "_pins", return_value=(SIX, CHECKSUMS)), \
             patch.object(av, "_unchanged"), \
             patch.object(av, "locate_defender", return_value=Path("scanner.exe")), \
             patch.object(av, "_engine_snapshot", return_value=SimpleNamespace(sha256="d"*64)), \
             patch.object(av, "_same_engine"), \
             patch.object(av, "health_check"), \
             patch.object(av, "_environment"), \
             patch.object(av, "scan_one", side_effect=failing):
            with self.assertRaises(av.AVHold):
                av.scan_candidates("private-dist", "private-r9", PINNED)
        self.assertEqual(len(seen), 3)

    def test_strict_microsoft_signer_not_generic_substring(self):
        self.assertIn("CN=Microsoft Corporation", av.PREFLIGHT)
        self.assertNotIn("-notmatch 'Microsoft'", av.PREFLIGHT)

    def test_scanner_fingerprint_failure_stops_privately(self):
        with patch.object(av.custody, "fingerprint",
                          side_effect=av.custody.EngineHold("PRIVATE PATH")):
            with self.assertRaises(av.AVHold) as caught:
                av._engine_snapshot(Path("private-scanner"))
        self.assertNotIn("PRIVATE", str(caught.exception))

    def test_scanner_swap_refused_privately(self):
        with patch.object(av.custody, "require_same_engine",
                          side_effect=av.custody.EngineHold("PRIVATE PATH")):
            with self.assertRaises(av.AVHold) as caught:
                av._same_engine(Path("private-scanner"), object())
        self.assertNotIn("PRIVATE", str(caught.exception))

    def test_changed_engine_before_first_scan_stops_all_six(self):
        with patch.object(av, "require_native_win11"), \
             patch.object(av, "_pins", return_value=(SIX, CHECKSUMS)), \
             patch.object(av, "_unchanged"), \
             patch.object(av, "locate_defender", return_value=Path("scanner.exe")), \
             patch.object(av, "_engine_snapshot", return_value=SimpleNamespace(sha256="d"*64)), \
             patch.object(av, "_same_engine", side_effect=av.AVHold("engine changed")), \
             patch.object(av, "health_check"), \
             patch.object(av, "_environment"), \
             patch.object(av, "scan_one") as scanned:
            with self.assertRaises(av.AVHold):
                av.scan_candidates("private-dist", "private-r9", PINNED)
        scanned.assert_not_called()

    def test_changed_engine_after_first_scan_aborts_no_report(self):
        # One health preflight check, one before scan, then the first
        # postscan engine recheck fails before the next candidate can run.
        with patch.object(av, "require_native_win11"), \
             patch.object(av, "_pins", return_value=(SIX, CHECKSUMS)), \
             patch.object(av, "_unchanged"), \
             patch.object(av, "locate_defender", return_value=Path("scanner.exe")), \
             patch.object(av, "_engine_snapshot", return_value=SimpleNamespace(sha256="d"*64)), \
             patch.object(av, "_same_engine",
                          side_effect=(None, None, av.AVHold("engine changed"))), \
             patch.object(av, "health_check"), \
             patch.object(av, "_environment"), \
             patch.object(av, "scan_one") as scanned:
            with self.assertRaises(av.AVHold):
                av.scan_candidates("private-dist", "private-r9", PINNED)
        self.assertEqual(scanned.call_count, 1)

    def test_r113_history_or_exclusions_fail_closed_and_redacted(self):
        with patch.object(av.environment, "require_zero_observations",
                          side_effect=av.environment.EnvironmentHold(
                              "C:\\\\Users\\\\PRIVATE\\\\evidence.csv")):
            with self.assertRaises(av.AVHold) as caught:
                av._environment()
        self.assertNotIn("PRIVATE", str(caught.exception))
        self.assertNotIn("evidence.csv", str(caught.exception))

    def test_r113_environment_preflight_blocks_any_candidate_execution(self):
        with patch.object(av, "require_native_win11"), \
             patch.object(av, "_pins", return_value=(SIX, CHECKSUMS)), \
             patch.object(av, "_unchanged"), \
             patch.object(av, "locate_defender", return_value=Path("scanner.exe")), \
             patch.object(av, "_engine_snapshot", return_value=SimpleNamespace(sha256="d"*64)), \
             patch.object(av, "_same_engine"), \
             patch.object(av, "health_check"), \
             patch.object(av, "_environment", side_effect=av.AVHold("HOLD")), \
             patch.object(av, "scan_one") as scanned:
            with self.assertRaises(av.AVHold):
                av.scan_candidates("private-dist", "private-r9", PINNED)
        scanned.assert_not_called()

    def test_r113_postfirst_scan_detection_blocks_remaining_five(self):
        with patch.object(av, "require_native_win11"), \
             patch.object(av, "_pins", return_value=(SIX, CHECKSUMS)), \
             patch.object(av, "_unchanged"), \
             patch.object(av, "locate_defender", return_value=Path("scanner.exe")), \
             patch.object(av, "_engine_snapshot", return_value=SimpleNamespace(sha256="d"*64)), \
             patch.object(av, "_same_engine"), \
             patch.object(av, "health_check"), \
             patch.object(av, "_environment", side_effect=(None, av.AVHold("HOLD"))), \
             patch.object(av, "scan_one") as scanned:
            with self.assertRaises(av.AVHold):
                av.scan_candidates("private-dist", "private-r9", PINNED)
        self.assertEqual(scanned.call_count, 1)

    def test_cli_failure_never_publishes_report(self):
        with patch.object(av, "prepare_report_path", return_value=Path("private.json")), \
             patch.object(av, "scan_candidates", side_effect=av.AVHold("private input")), \
             patch.object(av, "publish_report") as publish, \
             patch("sys.stderr"):
            rc = av.main(["dist", "r9", "--expected-r9-sha256", PINNED,
                          "--report", "private.json"])
        self.assertEqual(rc, 1)
        publish.assert_not_called()

    def test_cli_success_is_not_authorization(self):
        with patch.object(av, "prepare_report_path", return_value=Path("private.json")), \
             patch.object(av, "scan_candidates",
                          return_value={"release_authorized": False}), \
             patch.object(av, "publish_report") as publish, \
             patch("sys.stdout"):
            rc = av.main(["dist", "r9", "--expected-r9-sha256", PINNED,
                          "--report", "private.json"])
        self.assertEqual(rc, 0)
        self.assertFalse(publish.call_args.args[1]["release_authorized"])


if __name__ == "__main__":
    unittest.main()
