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
import threading

CHECKS = (
    ("six_app_source_smoke", "test_offline_source_smoke_r408.py"),
    ("six_app_safety_smoke", "test_safety_smoke.py"),
    ("procureguard_private_rows", "test_procurement_foreign_hash_custody_r483.py"),
    ("six_exe_inventory_ancestry", "test_inventory_staging_ancestry_r484.py"),
)
MODES = (("normal", ()), ("optimized", ("-OO",)))
# Only a genuine, terminal unittest success trailer can count as successful.
# Bare "OK"/"Ran 7 tests" anywhere in a log is not sufficient evidence.
_TEST_SUMMARY = re.compile(rb"(?m)^Ran (\d+) tests? in \d+(?:\.\d+)?s\r?$")
_SUCCESS_TRAILER = re.compile(
    rb"(?m)^-{70}\r?\nRan ([1-9]\d*) tests? in \d+(?:\.\d+)?s"
    rb"\r?\n\r?\nOK\r?\n?\Z"
)
_FAILURE_LINE = re.compile(rb"(?m)^(?:FAILED(?:[ \t(]|$)|FAIL:|ERROR:|Traceback \(most recent call last\):)")
_MAX_EVIDENCE_BYTES = 1_048_576  # Hard parent-side capture ceiling, including errors.


def _child_env(desktop: Path) -> dict[str, str]:
    """No credentials, telemetry variables, Python injection, or proxy settings."""
    allow = ("PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP", "TMPDIR",
             "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "VIRTUAL_ENV")
    env = {key: os.environ[key] for key in allow if key in os.environ}
    env["PYTHONPATH"] = str(desktop)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    return env


def _bounded_child(cmd: tuple[str, ...], desktop: Path, timeout: int) -> tuple[int, bytes, bool]:
    """Drain child stdout with a 1 MiB ceiling *while it runs*, on Windows or POSIX.

    A dedicated reader avoids PIPE deadlocks and never writes private exceptions to
    disk or the operator console. Above the cap the child is killed and its output
    discarded. This is not a sandbox; trusted test code may spawn descendants.
    """
    collected = bytearray()
    overflow = threading.Event()
    read_error = threading.Event()
    proc = subprocess.Popen(cmd, cwd=desktop.parent.parent, env=_child_env(desktop),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert proc.stdout is not None
    stream = proc.stdout

    def read_child() -> None:
        try:
            while True:
                chunk = stream.read1(65536)
                if not chunk:
                    break
                if len(collected) + len(chunk) > _MAX_EVIDENCE_BYTES:
                    overflow.set()
                    try:
                        proc.kill()
                    except OSError:
                        pass  # Child may already have exited; still reject the log.
                    break
                collected.extend(chunk)
        except (OSError, ValueError):
            read_error.set()
            try:
                proc.kill()
            except OSError:
                pass

    worker = threading.Thread(target=read_child, name="fvs-source-log-drain", daemon=True)
    timed_out = False
    try:
        worker.start()
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            proc.wait()
        worker.join(timeout=2)
        if worker.is_alive() or read_error.is_set():
            raise OSError("Source evidence stream unavailable")
        if timed_out:
            raise subprocess.TimeoutExpired(cmd, timeout)
        if overflow.is_set():
            return proc.returncode, b"", True
        return proc.returncode, bytes(collected), False
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait()
        # Only close a stream that the reader has finished using. A pipe held
        # open by descendants yields BLOCKED, not an unbounded parent hang.
        if not worker.is_alive():
            stream.close()


def _single_check(desktop: Path, label: str, pattern: str, mode: str,
                  flags: tuple[str, ...], timeout: int) -> dict[str, object]:
    tests = desktop / "tests" / pattern
    try:
        # Never follow an externally substituted test file/directory.
        if (desktop.is_symlink() or (desktop / "tests").is_symlink()
                or tests.is_symlink() or not tests.is_file()):
            return {"check": label, "mode": mode, "result": "BLOCKED", "tests": 0}
        cmd = (sys.executable, *flags, "-B", "-W", "error", "-m", "unittest",
               "discover", "-s", str(desktop / "tests"), "-p", pattern)
        returncode, output, overflow = _bounded_child(cmd, desktop, timeout)
        if overflow:
            return {"check": label, "mode": mode, "result": "FAIL", "tests": 0}
        summaries = _TEST_SUMMARY.findall(output)
        count = int(summaries[0]) if len(summaries) == 1 else 0
        terminal = _SUCCESS_TRAILER.search(output)
        passed = (returncode == 0 and count > 0 and terminal is not None
                  and int(terminal.group(1)) == count
                  and not _FAILURE_LINE.search(output))
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
            "all_passed": bool(results) and all(row["result"] == "PASS" for row in results),
            "results": results}


def main() -> int:
    report = verify(Path(__file__).resolve().parent)
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
