"""Offline, fail-closed pre-release verifier for six Final Vestige Windows x64 EXEs.

It validates candidate artifacts; a passing result is NOT QD approval, signing,
malware clearance, premium licensing, or permission to distribute.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import struct
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

EXPECTED = (
    "LedgerDiffLite.exe", "InvoiceTwinScout.exe", "SpendMapLite.exe",
    "PolicyDeltaDesk.exe", "GrantAuditStudioPro.exe", "ProcureGuardStudioPro.exe",
)
HEX = re.compile(r"^[0-9a-f]{64}$")


class GateFailure(ValueError):
    """Artifact verification failed; never distribute this candidate."""


def _regular(path: Path) -> None:
    if path.is_symlink() or not path.exists() or not stat.S_ISREG(path.stat().st_mode):
        raise GateFailure(f"Not an ordinary file: {path.name}")


def _inventory(root: Path) -> dict[str, str]:
    path = root / "SHA256SUMS.txt"
    _regular(path)
    if path.stat().st_size > 4096:
        raise GateFailure("Checksum inventory exceeds safe length")
    try:
        lines = path.read_text(encoding="ascii").splitlines()
    except UnicodeError as exc:
        raise GateFailure("Checksum inventory must be ASCII") from exc
    entries: dict[str, str] = {}
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9]+\.exe)", line)
        if not match:
            raise GateFailure("Malformed checksum inventory entry")
        digest, filename = match.groups()
        if filename not in EXPECTED or filename in entries:
            raise GateFailure("Unknown or duplicate checksum entry")
        entries[filename] = digest
    if set(entries) != set(EXPECTED):
        raise GateFailure("Checksum inventory must include exactly six expected executables")
    return entries


def _pe64(path: Path) -> None:
    """Reject renamed/32-bit/non-Windows payloads before a smoke execution."""
    with path.open("rb") as stream:
        header = stream.read(64)
        if len(header) < 64 or header[:2] != b"MZ":
            raise GateFailure(f"{path.name}: missing Windows MZ header")
        offset = struct.unpack_from("<I", header, 0x3C)[0]
        if not 64 <= offset <= 65536 or offset + 26 > path.stat().st_size:
            raise GateFailure(f"{path.name}: invalid PE header offset")
        stream.seek(offset)
        pe = stream.read(26)
    if len(pe) != 26 or pe[:4] != b"PE\x00\x00":
        raise GateFailure(f"{path.name}: missing PE signature")
    if struct.unpack_from("<H", pe, 4)[0] != 0x8664:
        raise GateFailure(f"{path.name}: expected AMD64, not 32-bit or ARM")
    if struct.unpack_from("<H", pe, 24)[0] != 0x20B:
        raise GateFailure(f"{path.name}: expected PE32+ executable")


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(folder: str | Path, *, smoke: bool = False, runner=None,
           platform_name: str | None = None, timeout: int = 120) -> dict:
    root = Path(folder)
    if root.is_symlink() or not root.is_dir():
        raise GateFailure("Choose a real directory of candidate executables")
    actual = {p.name for p in root.iterdir() if p.suffix.lower() == ".exe"}
    if actual != set(EXPECTED):
        raise GateFailure("Binary folder has missing or unexpected executables: " +
                          repr(sorted(actual ^ set(EXPECTED))))
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
        if (platform_name or os.name) != "nt":
            raise GateFailure("Packaged EXE smoke testing requires actual Windows x64")
        if timeout < 1 or timeout > 600:
            raise GateFailure("Smoke timeout must be between 1 and 600 seconds")
        launch = runner or subprocess.run
        for record in records:
            recheck_artifacts("pre-smoke")
            exe = root / record["name"]
            started = time.monotonic()
            try:
                result = launch([str(exe.resolve()), "--smoke-test"],
                                cwd=str(root.resolve()), timeout=timeout,
                                check=False, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.TimeoutExpired as exc:
                raise GateFailure(f"{record['name']}: smoke timed out") from exc
            except OSError as exc:
                raise GateFailure(f"{record['name']}: could not execute packaged EXE") from exc
            if result.returncode != 0:
                raise GateFailure(f"{record['name']}: smoke failed with exit code {result.returncode}")
            # A passing exit code is insufficient if a process modifies its
            # own image, another app's image, or the checksum inventory.
            recheck_artifacts("post-smoke")
            record["smoke"] = "passed"
            record["seconds"] = round(time.monotonic() - started, 3)
    recheck_artifacts("final verification")
    return {"schema": 1, "status": "windows_smoke_passed" if smoke else "integrity_only",
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
        result = verify(args.dist, smoke=args.smoke)
        if args.report:
            with args.report.open("x", encoding="utf-8") as stream:
                json.dump(result, stream, sort_keys=True, indent=2)
                stream.write("\n")
        print(f"Candidate verified: {result['status']} (NOT release authorized)")
        return 0
    except (GateFailure, OSError) as exc:
        print("REJECTED: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
