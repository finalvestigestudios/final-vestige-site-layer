"""Fail-closed, privacy-minimal Defender history/exclusion observation (R113).

This observes only three aggregate counts on a trusted Windows 11 reviewer
workstation. An empty observation is NOT proof of safety or release approval:
Defender's local history is neither complete nor immutable. This module must
never change preferences, remove threats, restore quarantine, or send telemetry.
"""
from __future__ import annotations

import os
import re
import subprocess

import trusted_powershell_r114 as trust
from typing import Any

# Zero user input is interpolated into PowerShell. Do not print raw Defender
# records: Resources, ProcessName and DomainUser may expose private local data.
# Known Microsoft cmdlets: Get-MpThreatDetection, Get-MpThreat, Get-MpPreference.
# The one and only stdout line consists of bounded aggregate integer counts.
HISTORY_COMMAND = (
    "$ErrorActionPreference='Stop'; $WarningPreference='Stop'; "
    "$d=@(Get-MpThreatDetection -ErrorAction Stop | Where-Object { $null -ne $_ }); "
    "$t=@(Get-MpThreat -ErrorAction Stop | Where-Object { $null -ne $_ }); "
    "$p=Get-MpPreference -ErrorAction Stop; "
    "if($null -eq $p){exit 41}; "
    "$x=@($p.ExclusionPath)+@($p.ExclusionExtension)+"
    "@($p.ExclusionProcess)+@($p.ExclusionIpAddress); "
    "$n=@($x | Where-Object { $null -ne $_ -and "
    "-not [string]::IsNullOrWhiteSpace([string]$_) }).Count; "
    "[Console]::Out.WriteLine(('FVS_DEFENDER_COUNTS|{0}|{1}|{2}' "
    "-f $d.Count,$t.Count,$n))"
)
COUNTS = re.compile(r"\AFVS_DEFENDER_COUNTS\|(?:0|[1-9][0-9]{0,7})\|"
                    r"(?:0|[1-9][0-9]{0,7})\|(?:0|[1-9][0-9]{0,7})(?:\r\n|\n)?\Z",
                    re.ASCII)
MAX_STDOUT = 96
TIMEOUT = 60
OBSERVED = "zero_local_history_and_explicit_exclusions_observed_not_malware_clearance"


class EnvironmentHold(ValueError):
    """History, exclusions, or observation failure block reviewer evidence."""


def require_zero_observations(*, runner: Any = None) -> str:
    """Check Defender snapshots without disclosing records or user paths.

    Intended to be called before scanning and immediately after EACH of the
    six candidate scans. Query errors, timeouts, any history or exclusions,
    suspicious stdout, and non-Windows calls all fail closed. This does not
    establish malware clearance, and cannot substitute independent AV review.
    """
    if os.name != "nt":
        raise EnvironmentHold("Trusted native Windows Defender observation required")
    try:
        powershell = trust.require_system_powershell()
    except trust.PowerShellHold:
        raise EnvironmentHold("Native System32 PowerShell interpreter unavailable") from None
    execute = runner if runner is not None else subprocess.run
    try:
        result = execute(
            [str(powershell), "-NoLogo", "-NoProfile", "-NonInteractive",
             "-Command", HISTORY_COMMAND],
            check=False, timeout=TIMEOUT, shell=False,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="ascii",
        )
        if type(result.returncode) is not int or result.returncode != 0:
            raise EnvironmentHold("Defender history/exclusion query failed")
        # No raw provider output survives parsing; fail closed if warnings,
        # path details, extra lines or large output reach stdout.
        raw = result.stdout
        if (type(raw) is not str or len(raw) > MAX_STDOUT
                or not COUNTS.fullmatch(raw)):
            raise EnvironmentHold("Defender observation format invalid")
        numbers = raw.strip().split("|")[1:]
        if len(numbers) != 3 or any(int(value) != 0 for value in numbers):
            raise EnvironmentHold("Defender recorded history or explicit exclusions")
        return OBSERVED
    except EnvironmentHold:
        raise
    except (AttributeError, OSError, ValueError, TypeError, UnicodeError, subprocess.TimeoutExpired):
        raise EnvironmentHold("Defender history/exclusion observation unavailable") from None
