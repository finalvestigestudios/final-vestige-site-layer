"""Read-only re-verification of six-app Windows release-candidate evidence.

A retained report is not code signing, proof that a historical smoke test ran,
malware clearance, premium entitlement, a compliance decision, or QD approval.
An independently retained report SHA-256 is needed for historical authenticity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import sys
from datetime import datetime, timedelta
from pathlib import Path


# Python -I deliberately omits the script directory from sys.path. Resolve
# only this Git-owned desktop module directory, not cwd or PYTHONPATH, so the
# private runner's isolated child commands can import local verification code.
DESKTOP = Path(__file__).resolve().parent
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))

import release_gate as gate
from candidate_path_ancestry_r391 import snapshot_candidate_parents
from candidate_reparse_r390 import unsafe_windows_reparse

MAX_REPORT_BYTES = 64 * 1024
HEX = re.compile(r"^[0-9a-f]{64}$")
UTC_SECONDS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$")
REPORT_KEYS = frozenset({
    "schema", "status", "release_authorized", "premium_entitlement_verified",
    "codesigning_verified", "malware_scan_verified", "verified_utc",
    "checksums_sha256", "artifacts", "windows_executables_verified",
    "smoke_simulated",
})


class ReportAttestationError(ValueError):
    """Verification is not trustworthy; do not distribute the candidate."""


def _signature(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _same_path_descriptor_signature(path_info: os.stat_result,
                                    descriptor_info: os.stat_result,
                                    *, windows: bool | None = None) -> bool:
    """Cross-view ctime is not portable on Windows; same-view checks remain strict."""
    if windows is None:
        windows = os.name == "nt"
    path_sig, fd_sig = _signature(path_info), _signature(descriptor_info)
    return path_sig[:-1] == fd_sig[:-1] if windows else path_sig == fd_sig



def _read_verified_report_impl(path: str | Path, candidate_dir: str | Path) -> tuple[bytes, str]:
    """Read one bounded ordinary report; preserve descriptor ownership on fdopen faults.

    Lexical ancestry checks reject junctions and symlink parents, even when the
    final JSON is an ordinary file. They detect observed swaps, not every race.
    """
    root = Path(candidate_dir).resolve(strict=True)
    file = Path(path)
    parents_before = snapshot_candidate_parents(file)
    resolved = file.resolve(strict=True)
    if resolved == root or root in resolved.parents:
        raise ReportAttestationError("Report cannot be inside the candidate directory")
    before = file.lstat()
    if (unsafe_windows_reparse(before) or not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1 or before.st_size < 1
            or before.st_size > MAX_REPORT_BYTES):
        raise ReportAttestationError("Report must be one bounded ordinary file")
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
             | getattr(os, "O_NONBLOCK", 0))
    fd = os.open(file, flags)
    try:
        stream = os.fdopen(fd, "rb")
    except BaseException:
        # fdopen has not accepted descriptor ownership; avoid leaking a
        # report handle even on interruption or private I/O exceptions.
        try:
            os.close(fd)
        except OSError:
            pass
        raise
    with stream:
        opened = os.fstat(stream.fileno())
        if (unsafe_windows_reparse(opened)
                or not _same_path_descriptor_signature(before, opened)
                or not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1):
            raise ReportAttestationError("Report changed during opening")
        raw = stream.read(MAX_REPORT_BYTES + 1)
        finished = os.fstat(stream.fileno())
        if (unsafe_windows_reparse(finished) or len(raw) != opened.st_size
                or _signature(finished) != _signature(opened)
                or len(raw) > MAX_REPORT_BYTES):
            raise ReportAttestationError("Report changed during reading")
    after = file.lstat()
    if (unsafe_windows_reparse(after) or _signature(after) != _signature(before)
            or not _same_path_descriptor_signature(after, opened)
            or snapshot_candidate_parents(file) != parents_before):
        raise ReportAttestationError("Report path changed during reading")
    if file.resolve(strict=True) != resolved:
        raise ReportAttestationError("Report path changed during reading")
    return raw, hashlib.sha256(raw).hexdigest()


def _read_verified_report(path: str | Path, candidate_dir: str | Path) -> tuple[bytes, str]:
    """Translate private filesystem errors OUTSIDE their exception handlers.

    'raise ... from None' only hides __context__ in traceback rendering; it
    does not destroy that retained private exception object.
    """
    read_failed = False
    try:
        return _read_verified_report_impl(path, candidate_dir)
    except ReportAttestationError:
        raise
    except (OSError, RuntimeError, ValueError, TypeError):
        read_failed = True
    if read_failed:
        raise ReportAttestationError("Report could not be read safely")


def _unique_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReportAttestationError("Duplicate JSON key in evidence")
        result[key] = value
    return result


def _bad_constant(_value: str):
    raise ReportAttestationError("Nonfinite numeric evidence")


def _validate_report(raw: bytes) -> dict:
    malformed = False
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_keys,
                           parse_constant=_bad_constant)
    except ReportAttestationError:
        raise
    except (UnicodeError, ValueError, TypeError, RecursionError):
        malformed = True
    if malformed:
        raise ReportAttestationError("Malformed verification JSON")
    if not isinstance(value, dict) or set(value) != REPORT_KEYS:
        raise ReportAttestationError("Unexpected verification schema")
    if type(value["schema"]) is not int or value["schema"] != 1:
        raise ReportAttestationError("Unsupported verification schema")
    if value["status"] not in ("integrity_only", "windows_smoke_passed"):
        # Synthetic runner results are useful in regression tests but are
        # never valid retained Windows release-candidate evidence.
        raise ReportAttestationError("Unknown or synthetic verification status")
    if (type(value["windows_executables_verified"]) is not bool
            or type(value["smoke_simulated"]) is not bool
            or value["smoke_simulated"] is not False
            or value["windows_executables_verified"] is not
               (value["status"] == "windows_smoke_passed")):
        raise ReportAttestationError("Untrusted native Windows smoke provenance")
    for key in ("release_authorized", "premium_entitlement_verified",
                "codesigning_verified", "malware_scan_verified"):
        if value[key] is not False:
            raise ReportAttestationError("Evidence falsely declares a release gate passed")
    timestamp = value["verified_utc"]
    if not isinstance(timestamp, str) or not UTC_SECONDS.fullmatch(timestamp):
        raise ReportAttestationError("Invalid verification timestamp")
    invalid_calendar = False
    try:
        parsed = datetime.fromisoformat(timestamp)
    except ValueError:
        invalid_calendar = True
    if invalid_calendar:
        raise ReportAttestationError("Invalid verification timestamp")
    if parsed.utcoffset() != timedelta(0):
        raise ReportAttestationError("Invalid verification timestamp")
    if not isinstance(value["checksums_sha256"], str) or not HEX.fullmatch(value["checksums_sha256"]):
        raise ReportAttestationError("Invalid checksum inventory fingerprint")
    artifacts = value["artifacts"]
    if not isinstance(artifacts, list) or len(artifacts) != len(gate.EXPECTED):
        raise ReportAttestationError("Evidence must cover exactly six approved programs")
    smoked = value["status"] == "windows_smoke_passed"
    for expected_name, artifact in zip(gate.EXPECTED, artifacts):
        expected_keys = {"name", "sha256", "pe_machine", "smoke"}
        if smoked:
            expected_keys.add("seconds")
        if not isinstance(artifact, dict) or set(artifact) != expected_keys:
            raise ReportAttestationError("Unexpected executable evidence record")
        if (artifact["name"] != expected_name or artifact["pe_machine"] != "AMD64"
                or not isinstance(artifact["sha256"], str)
                or not HEX.fullmatch(artifact["sha256"])):
            raise ReportAttestationError("Invalid executable evidence record")
        if artifact["smoke"] != ("passed" if smoked else "not_run"):
            raise ReportAttestationError("Inconsistent smoke status")
        if smoked:
            seconds = artifact["seconds"]
            if (type(seconds) not in (int, float) or not math.isfinite(seconds)
                    or seconds < 0):
                raise ReportAttestationError("Invalid smoke duration")
    return value


def verify_report(report: str | Path, candidate_dir: str | Path, *,
                  expected_report_sha256: str | None = None) -> dict:
    """Rehash all six candidate images and compare to a historical report.

    Returns consistency and optional independent fingerprint status, never
    asserts that prior smoke executions really occurred or grants release.
    """
    if expected_report_sha256 is not None and (
            not isinstance(expected_report_sha256, str)
            or not HEX.fullmatch(expected_report_sha256)):
        raise ReportAttestationError("Expected report SHA-256 must be 64 lowercase hex digits")
    raw, digest = _read_verified_report(report, candidate_dir)
    recorded = _validate_report(raw)
    if expected_report_sha256 is not None and digest != expected_report_sha256:
        raise ReportAttestationError("Independent evidence fingerprint mismatch")
    candidate_failed = False
    try:
        current = gate.verify(candidate_dir, smoke=False)
    except (gate.GateFailure, OSError, ValueError):
        candidate_failed = True
    if candidate_failed:
        raise ReportAttestationError("Candidate executable verification failed")
    if current["checksums_sha256"] != recorded["checksums_sha256"]:
        raise ReportAttestationError("Checksum inventory changed since evidence capture")
    if len(current["artifacts"]) != len(recorded["artifacts"]):
        raise ReportAttestationError("Candidate artifact count changed")
    for now, then in zip(current["artifacts"], recorded["artifacts"]):
        if (now["name"] != then["name"] or now["sha256"] != then["sha256"]
                or now["pe_machine"] != then["pe_machine"]):
            raise ReportAttestationError("Candidate image changed since evidence capture")
    return {
        "candidate_consistency": "PASS",
        "evidence_pin": "PINNED" if expected_report_sha256 is not None else "UNPINNED",
        "historical_smoke_proven": False,
        "release_authorized": False,
        "premium_entitlement_verified": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="Previously retained offline-gate JSON file")
    parser.add_argument("dist", help="Candidate directory with exactly six EXEs and SHA256SUMS.txt")
    parser.add_argument("--expected-report-sha256", help="SHA-256 saved independently at trusted capture time")
    args = parser.parse_args(argv)
    try:
        result = verify_report(args.report, args.dist,
                               expected_report_sha256=args.expected_report_sha256)
    except ReportAttestationError as exc:
        print("REJECTED: " + str(exc), file=sys.stderr)
        return 1
    print("CONSISTENT (" + result["evidence_pin"] + "); historical smoke NOT independently proven; "
          "NOT release authorized")
    return 0


if __name__ == "__main__":
    sys.exit(main())
