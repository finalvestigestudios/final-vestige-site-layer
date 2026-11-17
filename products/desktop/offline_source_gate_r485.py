"""Operator-run, network-unneeded six-app *source* regression gate (not an EXE release gate).

Runs a fixed review-critical subset on a checked-out repository in two Python modes.
Returns only fixed-label JSON; test output and private path tracebacks are discarded.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

CHECKS = (
    ("six_app_source_smoke", "test_offline_source_smoke_r408.py"),
    ("six_app_safety_smoke", "test_safety_smoke.py"),
    ("procureguard_private_rows", "test_procurement_foreign_hash_custody_r483.py"),
    ("six_exe_inventory_ancestry", "test_inventory_staging_ancestry_r484.py"),
)
MODES = (("normal", ()), ("optimized", ("-OO",)))
_TEST_SUMMARY = re.compile(rb"Ran (\d+) tests? in ")
_SKIP = re.compile(rb"skipped\s*=\s*([1-9]\d*)")


def _child_env(desktop: Path) -> dict[str, str]:
    """No credentials, telemetry variables, Python injection, or proxy settings."""
    allow = ("PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP", "TMPDIR",
             "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "VIRTUAL_ENV")
    env = {key: os.environ[key] for key in allow if key in os.environ}
    env["PYTHONPATH"] = str(desktop)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    return env


def _single_check(desktop: Path, label: str, pattern: str, mode: str,
                  flags: tuple[str, ...], timeout: int) -> dict[str, object]:
    tests = desktop / "tests" / pattern
    if not tests.is_file():
        return {"check": label, "mode": mode, "result": "BLOCKED", "tests": 0}
    cmd = (sys.executable, *flags, "-B", "-W", "error", "-m", "unittest",
           "discover", "-s", str(desktop / "tests"), "-p", pattern)
    try:
        # A disk-backed spool avoids storing large sensitive exception output in RAM;
        # nothing from it is copied to the evidence record or console.
        with tempfile.TemporaryFile(mode="w+b") as spool:
            finished = subprocess.run(cmd, cwd=desktop.parent.parent, env=_child_env(desktop),
                                      stdout=spool, stderr=subprocess.STDOUT,
                                      timeout=timeout, check=False)
            size = spool.tell()
            spool.seek(max(0, size - 16384))
            tail = spool.read()
        summaries = _TEST_SUMMARY.findall(tail)
        count = int(summaries[-1]) if summaries else 0
        passed = (finished.returncode == 0 and count > 0
                  and not _SKIP.search(tail) and b"OK" in tail
                  and b"FAILED" not in tail)
        return {"check": label, "mode": mode,
                "result": "PASS" if passed else "FAIL", "tests": count}
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return {"check": label, "mode": mode, "result": "BLOCKED", "tests": 0}


def verify(desktop: Path, timeout: int = 600) -> dict[str, object]:
    """Fail closed; no claimed Windows packaging, native binaries, or approvals."""
    if type(timeout) is not int or not 1 <= timeout <= 3600:
        raise ValueError("Invalid bounded test timeout")
    results = [_single_check(desktop, label, pattern, mode, flags, timeout)
               for label, pattern in CHECKS for mode, flags in MODES]
    return {"schema": "fvs-offline-source-gate-r485-v1", "release_authorized": False,
            "all_passed": all(row["result"] == "PASS" for row in results),
            "results": results}


def main() -> int:
    report = verify(Path(__file__).resolve().parent)
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
