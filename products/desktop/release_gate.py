"""Offline, fail-closed pre-release verifier for six Final Vestige Windows x64 EXEs.

It validates candidate artifacts; a passing result is NOT QD approval, signing,
malware clearance, premium licensing, or permission to distribute.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import platform
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# Python -I deliberately omits the script directory from sys.path. Resolve
# only this Git-owned desktop module directory, not cwd or PYTHONPATH, so the
# private runner's isolated child commands can import local verification code.
DESKTOP = Path(__file__).resolve().parent
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))

from pe_image_guard import PEFormatError, verify_amd64_pe
from report_evidence import ReportEvidenceError, prepare_report_path, publish_report
from candidate_guard import (
    CandidateGuardError, MAX_CHECKSUM_BYTES,
    check_candidate_directory, read_checksum_candidate, sha256_candidate,
)

from build_inventory import EXPECTED
from canonical_inventory_r334 import CanonicalInventoryError, parse_canonical_inventory
from smoke_provenance import SmokeProvenanceError, classify_smoke
from smoke_runner_r336 import SmokeRunError, run_smoke_checked, select_smoke_runner


class GateFailure(ValueError):
    """Artifact verification failed; never distribute this candidate."""


def _regular(path: Path) -> None:
    if path.is_symlink() or not path.exists() or not stat.S_ISREG(path.stat().st_mode):
        raise GateFailure(f"Not an ordinary file: {path.name}")


def _inventory(root: Path) -> dict[str, str]:
    """Accept only the canonical ordered six-app producer inventory.

    Read bytes through the existing bounded, descriptor-pinned file guard;
    normalization must not hide altered line endings, row order or trailing
    evidence. Reject any noncanonical input before a smoke command runs.
    """
    path = root / "SHA256SUMS.txt"
    _regular(path)
    try:
        return parse_canonical_inventory(read_checksum_candidate(path), EXPECTED)
    except (CandidateGuardError, CanonicalInventoryError) as exc:
        raise GateFailure(str(exc)) from None


def _pe64(path: Path) -> None:
    """Require a bounded, structurally plausible user-mode AMD64 PE32+ image."""
    try:
        verify_amd64_pe(path)
    except PEFormatError as exc:
        raise GateFailure(f"{path.name}: {exc}") from exc


def _sha(path: Path) -> str:
    # The checksum file is small; packaged binaries are capped at 512 MiB each.
    # Descriptor checks detect source swaps, links and observed in-flight edits.
    try:
        if path.name == "SHA256SUMS.txt":
            return sha256_candidate(path, maximum=MAX_CHECKSUM_BYTES)
        return sha256_candidate(path)
    except CandidateGuardError as exc:
        raise GateFailure(str(exc)) from None


def verify(folder: str | Path, *, smoke: bool = False, runner=None,
           platform_name: str | None = None, timeout: int = 120) -> dict:
    # A test-injected runner or OS override can exercise failure branches but
    # must never create a report that claims native Windows x64 execution.
    try:
        smoke_status = classify_smoke(
            enabled=smoke, native_os=os.name, native_arch=platform.machine(),
            runner_injected=runner is not None, platform_override=platform_name,
        )
    except SmokeProvenanceError as exc:
        raise GateFailure(str(exc)) from None
    root = Path(folder)
    if root.is_symlink() or not root.is_dir():
        raise GateFailure("Choose a real directory of candidate executables")
    actual = {p.name for p in root.iterdir() if p.suffix.lower() == ".exe"}
    if actual != set(EXPECTED):
        raise GateFailure("Binary folder has missing or unexpected executables")
    # Check expected file status first to preserve clear symlink diagnostics.
    for name in EXPECTED:
        _regular(root / name)
    try:
        check_candidate_directory(root, EXPECTED)
    except CandidateGuardError as exc:
        raise GateFailure(str(exc)) from None
    checksums = _inventory(root)
    initial_inventory_sha = _sha(root / "SHA256SUMS.txt")
    records = []
    # Verify EVERY binary before executing ANY, so a bad checksum cannot leave
    # an earlier unchecked binary executed in the same verification attempt.
    for name in EXPECTED:
        candidate = root / name
        _regular(candidate)
        _pe64(candidate)
        actual_hash = _sha(candidate)
        if actual_hash != checksums[name]:
            raise GateFailure(f"{name}: SHA256 does not match inventory")
        records.append({"name": name, "sha256": actual_hash, "pe_machine": "AMD64",
                        "smoke": "not_run"})
    def recheck_artifacts(phase: str) -> None:
        """Catch changed binaries/inventory before and after each smoke execution."""
        try:
            check_candidate_directory(root, EXPECTED)
        except CandidateGuardError as exc:
            raise GateFailure(str(exc)) from None
        inventory_file = root / "SHA256SUMS.txt"
        if (_sha(inventory_file) != initial_inventory_sha
                or _inventory(root) != checksums):
            raise GateFailure("Checksum inventory changed during " + phase)
        for record in records:
            candidate = root / record["name"]
            _regular(candidate)
            if _sha(candidate) != record["sha256"]:
                raise GateFailure(record["name"] + ": executable changed during " + phase)

    recheck_artifacts("initial verification")
    if smoke:
        if type(timeout) is not int or not 1 <= timeout <= 600:
            raise GateFailure("Smoke timeout must be between 1 and 600 seconds")
        launch = select_smoke_runner(runner)
        for record in records:
            recheck_artifacts("pre-smoke")
            exe = root / record["name"]
            started = time.monotonic()
            try:
                run_smoke_checked(launch, exe, root, name=record["name"], timeout=timeout)
            except SmokeRunError as exc:
                raise GateFailure(str(exc)) from None
            # A passing exit code is insufficient if a process modifies its
            # own image, another app's image, or the checksum inventory.
            recheck_artifacts("post-smoke")
            record["smoke"] = ("simulated" if smoke_status == "synthetic_smoke_only"
                               else "passed")
            record["seconds"] = round(time.monotonic() - started, 3)
    recheck_artifacts("final verification")
    return {"schema": 1, "status": smoke_status,
            "windows_executables_verified": smoke_status == "windows_smoke_passed",
            "smoke_simulated": smoke_status == "synthetic_smoke_only",
            "release_authorized": False, "premium_entitlement_verified": False,
            "codesigning_verified": False, "malware_scan_verified": False,
            "verified_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "checksums_sha256": _sha(root / "SHA256SUMS.txt"), "artifacts": records}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist", help="Directory containing six .exe files and SHA256SUMS.txt")
    parser.add_argument("--smoke", action="store_true", help="Run real EXE --smoke-test on Windows")
    parser.add_argument("--report", type=Path, help="Write JSON evidence to NEW file; never overwrite")
    args = parser.parse_args(argv)
    try:
        # Validate report location before smoke executes any candidate image.
        destination = prepare_report_path(args.report, args.dist) if args.report else None
        result = verify(args.dist, smoke=args.smoke)
        if destination is not None:
            publish_report(destination, result)
        print(f"Candidate verified: {result['status']} (NOT release authorized)")
        return 0
    except (GateFailure, ReportEvidenceError, OSError) as exc:
        print("REJECTED: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
