"""Offline Microsoft Defender candidate scan for a trusted Windows 11 x64 reviewer.

Requires six checksum-pinned R9-smoked EXEs, current active Microsoft Defender,
and a signed local scanner. Emits a private, no-overwrite evidence JSON only
after all six scans and rehashes succeed. No customer data, network upload,
release authorization, or premium editor access. Not malware certification.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# python -I omits script and parent folders. Trust only these resolved
# Git-owned paths, never an ambient PYTHONPATH or caller working directory.
SCRIPTS = Path(__file__).resolve().parent
DESKTOP = SCRIPTS.parent
for directory in (DESKTOP, SCRIPTS):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import release_gate as gate
import defender_engine_custody_r112 as custody
import defender_environment_r113 as environment
import trusted_powershell_r114 as trust
import trusted_defender_install_r116 as install
import report_attestation as attestation
from report_evidence import ReportEvidenceError, prepare_report_path, publish_report

PIN = re.compile(r"^[0-9a-f]{64}$")
# The script is static and passes the scanner path via an environment variable:
# neither a file name nor a reviewer input is interpolated into PowerShell.
PREFLIGHT = (
    "$ErrorActionPreference='Stop'; "
    "$p=$env:FVS_DEFENDER_SCANNER; "
    "$sig=Get-AuthenticodeSignature -LiteralPath $p; "
    "if($null -eq $sig -or $sig.Status -ne 'Valid' -or "
    "$null -eq $sig.SignerCertificate -or "
    "$sig.SignerCertificate.Subject -notmatch '(^|,\\s*)CN=Microsoft Corporation(\\s*,|$)'){exit 21}; "
    "$s=Get-MpComputerStatus -ErrorAction Stop; "
    "if($null -eq $s -or $s.AMServiceEnabled -ne $true -or "
    "$s.AntivirusEnabled -ne $true -or "
    "$s.RealTimeProtectionEnabled -ne $true -or "
    "$s.AMRunningMode -cne 'Normal' -or "
    "$s.BehaviorMonitorEnabled -ne $true -or "
    "$s.IoavProtectionEnabled -ne $true -or "
    "$s.OnAccessProtectionEnabled -ne $true -or "
    "[string]::IsNullOrWhiteSpace($s.AntivirusSignatureVersion) -or "
    "$null -eq $s.AntivirusSignatureAge -or "
    "$s.AntivirusSignatureAge -gt 3){exit 22}; exit 0"
)


class AVHold(ValueError):
    """Candidate/provider evidence is not acceptable for distribution."""


def require_native_win11() -> None:
    """Reject hosted Windows Server and non-Windows platforms."""
    if os.name != "nt" or platform.machine().lower() not in ("amd64", "x86_64"):
        raise AVHold("A trusted Windows 11 x64 workstation is required")
    try:
        version = sys.getwindowsversion()
        if version.build < 22000 or version.product_type != 1:
            raise AVHold("Windows 11 workstation evidence is required")
    except AttributeError:
        raise AVHold("Native Windows version evidence is missing") from None


def locate_defender() -> Path:
    """Choose only a native Windows Defender installation, never env paths.

    ProgramData and ProgramFiles from os.environ are writable process state.
    Only SHGetKnownFolderPath-derived roots are permitted; an unavailable
    native API or reparse-linked install must HOLD rather than fall back.
    """
    try:
        data, files = install.native_roots()
        options = []
        platform_root = data / "Microsoft" / "Windows Defender" / "Platform"
        if platform_root.exists() or platform_root.is_symlink():
            install._no_reparse(platform_root)
            if not platform_root.is_dir():
                raise AVHold("Native Defender platform installation is invalid")
            options.extend(custody.installed_platform_engines(platform_root))
        options.append(files / "Windows Defender" / "MpCmdRun.exe")
        for item in options:
            if item.exists() or item.is_symlink():
                return install.require_candidate(item, data, files)
    except (install.InstallHold, custody.EngineHold, OSError, ValueError):
        raise AVHold("Native Defender installation cannot be trusted") from None
    raise AVHold("A native Microsoft Defender scanner is unavailable")


def _run_quiet(args: list[str], *, timeout: int, env=None, runner=None) -> None:
    """No stdout/stderr, shell interpolation, or customer-data output."""
    execute = runner if runner is not None else subprocess.run
    try:
        result = execute(
            args, check=False, timeout=timeout, shell=False,
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, env=env,
        )
    except (subprocess.TimeoutExpired, OSError, ValueError):
        raise AVHold("Defender command could not complete") from None
    if type(result.returncode) is not int or result.returncode != 0:
        raise AVHold("Defender returned a failure or a detection")


def health_check(scanner: Path, *, runner=None) -> None:
    try:
        powershell = trust.require_system_powershell()
    except trust.PowerShellHold:
        raise AVHold("Native System32 PowerShell interpreter unavailable") from None
    env = dict(os.environ)
    env["FVS_DEFENDER_SCANNER"] = str(scanner)
    _run_quiet(
        [str(powershell), "-NoProfile", "-NonInteractive", "-Command", PREFLIGHT],
        timeout=45, env=env, runner=runner,
    )


def scan_one(scanner: Path, candidate: Path, *, runner=None) -> None:
    """Scan without remediation; a zero exit is not malware certification.

    Microsoft documents that an ordinary zero exit can also mean a threat
    was remediated. Forbid remediation to avoid a silent, destructive success.
    """
    _run_quiet(
        [str(scanner), "-Scan", "-ScanType", "3", "-File", str(candidate),
         "-DisableRemediation"],
        timeout=360, runner=runner,
    )


def _pins(dist: Path, r9: Path, expected_r9: str) -> tuple[dict[str, str], str]:
    if type(expected_r9) is not str or not PIN.fullmatch(expected_r9):
        raise AVHold("An independent lowercase R9 SHA-256 pin is required")
    try:
        result = attestation.verify_report(
            r9, dist, expected_report_sha256=expected_r9)
        raw, observed_sha = attestation._read_verified_report(r9, dist)
        prior = attestation._validate_report(raw)
    except (attestation.ReportAttestationError, OSError, ValueError):
        raise AVHold("The independent R9 candidate report is invalid") from None
    if (observed_sha != expected_r9
            or result.get("candidate_consistency") != "PASS"
            or result.get("evidence_pin") != "PINNED"
            or prior["status"] != "windows_smoke_passed"
            or prior["windows_executables_verified"] is not True):
        raise AVHold("Six genuine, SHA-pinned Windows smokes are required")
    return {record["name"]: record["sha256"] for record in prior["artifacts"]}, prior["checksums_sha256"]


def _unchanged(dist: Path, expected: dict[str, str], checksum_sha: str) -> None:
    try:
        now = gate.verify(dist, smoke=False)
    except (gate.GateFailure, OSError, ValueError):
        raise AVHold("Candidate integrity check failed") from None
    actual = {row["name"]: row["sha256"] for row in now["artifacts"]}
    if (actual != expected or now["checksums_sha256"] != checksum_sha
            or set(actual) != set(gate.EXPECTED)):
        raise AVHold("Candidate bytes changed before or during antivirus scan")


def _engine_snapshot(scanner: Path) -> custody.EnginePin:
    try:
        return custody.fingerprint(scanner)
    except custody.EngineHold:
        raise AVHold("Installed Defender engine custody unavailable") from None


def _same_engine(scanner: Path, pinned: custody.EnginePin) -> None:
    try:
        custody.require_same_engine(scanner, pinned)
    except custody.EngineHold:
        raise AVHold("Installed Defender engine changed during scan") from None


def _environment() -> None:
    """Abort privately on local Defender history/exclusions/query uncertainty."""
    try:
        environment.require_zero_observations()
    except environment.EnvironmentHold:
        raise AVHold("Defender history/exclusion observation failed") from None


def scan_candidates(dist: str | Path, r9: str | Path,
                    expected_r9: str) -> dict:
    """Requires a real Win11 workstation; no injected runner or OS override."""
    require_native_win11()
    root = Path(dist)
    prior, checksum_sha = _pins(root, Path(r9), expected_r9)
    _unchanged(root, prior, checksum_sha)
    scanner = locate_defender()
    scanner_pin = _engine_snapshot(scanner)
    health_check(scanner)
    _same_engine(scanner, scanner_pin)
    _environment()  # Pre-scan snapshot; no Defender-record details leave host.
    scanned = []
    for name in gate.EXPECTED:
        _same_engine(scanner, scanner_pin)
        _unchanged(root, prior, checksum_sha)
        # Require active, real-time, behavior, IOAV and on-access protection
        # before *every* individual scan; a two-endpoint status is insufficient.
        health_check(scanner)
        scan_one(scanner, root / name)
        _environment()  # Catch even successfully remediated local detections.
        # A scanner that became passive/disabled during the scan cannot pass.
        health_check(scanner)
        _unchanged(root, prior, checksum_sha)
        _same_engine(scanner, scanner_pin)
        scanned.append({"name": name, "sha256": prior[name],
                        "defender_custom_scan": "zero_exit_result_remediation_ambiguous"})
    health_check(scanner)
    _same_engine(scanner, scanner_pin)
    _unchanged(root, prior, checksum_sha)
    return {
        "scanner_sha256": scanner_pin.sha256,
        "scanner_custody": "same_signed_engine_sha256_and_file_identity_observed",
        "defender_environment_observations": 7,
        "defender_active_health_checkpoints": 14,
        "defender_active_health_policy": "normal_mode_realtime_behavior_ioav_onaccess_fresh_signatures",
        "defender_environment_status": environment.OBSERVED,
        "schema": "fv-labs-offline-defender-r111-v1",
        "provider": "Microsoft Defender Antivirus",
        "status": "SIX_SCANS_ZERO_EXIT_UNCERTIFIED",
        "native_platform": "Windows 11 AMD64 workstation",
        "scanned_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "r9_report_sha256": expected_r9,
        "checksums_sha256": checksum_sha,
        "artifacts": scanned,
        "release_authorized": False,
        "independent_malware_clearance": False,
        "premium_distribution_authorized": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist", help="Private six-EXE candidate directory")
    parser.add_argument("r9_report", help="Private R9 source-owned smoke evidence")
    parser.add_argument("--expected-r9-sha256", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        # Never create a report within candidate binaries or overwrite evidence.
        output = prepare_report_path(args.report, args.dist)
        data = scan_candidates(args.dist, args.r9_report,
                               args.expected_r9_sha256)
        publish_report(output, data)
    except (AVHold, ReportEvidenceError, OSError, ValueError):
        print("HOLD: Defender scan incomplete or private evidence invalid", file=sys.stderr)
        return 1
    print("PASS: six local Defender commands; no release or malware certification")
    return 0


if __name__ == "__main__":
    sys.exit(main())
