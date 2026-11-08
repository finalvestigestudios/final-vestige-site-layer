"""Strict private R111 Defender receipt contract for six Windows candidates.

Validates *claims* against independently pinned R9 evidence, not whether a
Defender scan actually ran. This must follow the real scanner exit, original
R9 attestation and descriptor-pinned report read. No release permission.
"""
from __future__ import annotations

from datetime import datetime, timedelta
import re

from strict_source_receipt_r273 import loads_strict_receipt

EXES = (
    "LedgerDiffLite.exe", "InvoiceTwinScout.exe", "SpendMapLite.exe",
    "PolicyDeltaDesk.exe", "GrantAuditStudioPro.exe", "ProcureGuardStudioPro.exe",
)
DIGEST = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
UTC_SECONDS = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00\Z", re.ASCII)
REPORT_KEYS = frozenset({
    "schema", "provider", "status", "native_platform", "scanned_utc",
    "scanner_sha256", "scanner_custody", "defender_environment_observations",
    "defender_active_health_checkpoints", "defender_active_health_policy",
    "defender_environment_status", "r9_report_sha256", "checksums_sha256",
    "artifacts", "release_authorized", "independent_malware_clearance",
    "premium_distribution_authorized",
})
ARTIFACT_KEYS = frozenset({"name", "sha256", "defender_custom_scan"})


class DefenderReceiptRejected(ValueError):
    """Private candidate evidence is inconsistent; diagnostics reveal no paths."""


def _hold() -> None:
    raise DefenderReceiptRejected("Invalid private Defender candidate receipt")


def _hex(value: object) -> bool:
    return type(value) is str and DIGEST.fullmatch(value) is not None


def require_defender_receipt(raw: bytes, *, expected_r9_sha256: str,
                             r9_evidence: dict) -> None:
    """Require one canonical report, exact six hashes and non-release flags.

    `r9_evidence` MUST originate from a SHA-256-pinned, independently attested
    R9 file. It is not a substitute for the live EXE/hash/AV checks or QD.
    All fields are locally generated; no customer financial data is needed.
    """
    try:
        if not _hex(expected_r9_sha256) or type(r9_evidence) is not dict:
            _hold()
        if (r9_evidence.get("status") != "windows_smoke_passed"
                or r9_evidence.get("windows_executables_verified") is not True
                or not _hex(r9_evidence.get("checksums_sha256"))):
            _hold()
        originals = r9_evidence.get("artifacts")
        if (type(originals) is not list or len(originals) != len(EXES)):
            _hold()
        expected_hashes = {}
        for name, artifact in zip(EXES, originals):
            if (type(artifact) is not dict or artifact.get("name") != name
                    or not _hex(artifact.get("sha256"))):
                _hold()
            expected_hashes[name] = artifact["sha256"]
        receipt = loads_strict_receipt(raw)
        if type(receipt) is not dict or set(receipt) != REPORT_KEYS:
            _hold()
        exact_strings = {
            "schema": "fv-labs-offline-defender-r111-v1",
            "provider": "Microsoft Defender Antivirus",
            "status": "SIX_SCANS_ZERO_EXIT_UNCERTIFIED",
            "native_platform": "Windows 11 AMD64 workstation",
            "scanner_custody": "same_signed_engine_sha256_and_file_identity_observed",
            "defender_active_health_policy": "normal_mode_realtime_behavior_ioav_onaccess_fresh_signatures",
            "defender_environment_status": "zero_local_history_and_explicit_exclusions_observed_not_malware_clearance",
        }
        for field, value in exact_strings.items():
            if type(receipt[field]) is not str or receipt[field] != value:
                _hold()
        for field in ("release_authorized", "independent_malware_clearance",
                      "premium_distribution_authorized"):
            if receipt[field] is not False:
                _hold()
        if (type(receipt["defender_environment_observations"]) is not int
                or receipt["defender_environment_observations"] != 7
                or type(receipt["defender_active_health_checkpoints"]) is not int
                or receipt["defender_active_health_checkpoints"] != 14):
            _hold()
        if (not _hex(receipt["scanner_sha256"])
                or receipt["r9_report_sha256"] != expected_r9_sha256
                or receipt["checksums_sha256"] != r9_evidence["checksums_sha256"]):
            _hold()
        timestamp = receipt["scanned_utc"]
        if type(timestamp) is not str or not UTC_SECONDS.fullmatch(timestamp):
            _hold()
        date = datetime.fromisoformat(timestamp)
        if date.utcoffset() != timedelta(0):
            _hold()
        artifacts = receipt["artifacts"]
        if type(artifacts) is not list or len(artifacts) != len(EXES):
            _hold()
        for name, artifact in zip(EXES, artifacts):
            if (type(artifact) is not dict or set(artifact) != ARTIFACT_KEYS
                    or artifact["name"] != name
                    or artifact["sha256"] != expected_hashes[name]
                    or artifact["defender_custom_scan"] !=
                       "zero_exit_result_remediation_ambiguous"):
                _hold()
    except (ValueError, KeyError, TypeError, RecursionError, UnicodeError):
        _hold()
