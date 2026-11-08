"""Private, owner-run six-EXE Windows candidate build when GitHub Actions is offline.

This is NOT release authorization. Requires an existing private workspace outside
this checkout and preinstalled, trusted Python, PyInstaller and cryptography.
Never uploads, publishes, signs, approves, or displays premium executables.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import tempfile

APPS = (
    "LedgerDiffLite", "InvoiceTwinScout", "SpendMapLite", "PolicyDeltaDesk",
    "GrantAuditStudioPro", "ProcureGuardStudioPro",
)
ROOT = Path(__file__).resolve().parents[3]
ERROR = "REJECTED: private Windows candidate build did not complete; no release authorized"
SUCCESS = (
    "PASS: six local Windows candidates passed offline source, SHA-256, PE and "
    "executable smoke/attestation gates; PRIVATE/QD HOLD — no distribution authorized"
)


class CandidateBuildRejected(RuntimeError):
    """Fixed diagnostic; never includes private paths or child log output."""


def _windows_x64() -> bool:
    return (os.name == "nt" and sys.maxsize > 2**32
            and platform.machine().upper() in ("AMD64", "X86_64"))


def _workspace(root: Path, destination: Path) -> Path:
    """Require an existing real, separate, trusted local private directory."""
    try:
        root = root.resolve(strict=True)
        if not root.is_dir():
            raise CandidateBuildRejected(ERROR)
        info = destination.lstat()  # never follow a workspace symlink
        if not stat.S_ISDIR(info.st_mode):
            raise CandidateBuildRejected(ERROR)
        safe = destination.resolve(strict=True)
        if safe == root or root in safe.parents or safe in root.parents:
            raise CandidateBuildRejected(ERROR)
        return safe
    except (OSError, ValueError, RuntimeError):
        raise CandidateBuildRejected(ERROR) from None


def _run_child(argv: list[str], cwd: Path, timeout: int) -> int:
    """Never let paths, customer data, or process logs reach terminal/CI."""
    env = os.environ.copy()
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PIP_NO_INDEX"] = "1"  # no installation/downloading in this runner
    try:
        result = subprocess.run(
            argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            shell=False, check=False, timeout=timeout,
        )
        return result.returncode
    except (OSError, subprocess.TimeoutExpired):
        return 1


def _execute_plan(root: Path, run_dir: Path, python: str, runner=_run_child) -> None:
    """Explicit checkout-frozen packaging plan, independently unit-testable.

    Child exits are authoritative. Tests may supply a fake runner, but that
    cannot enter the public CLI which always uses the real process runner.
    """
    desktop = root / "products" / "desktop"
    scripts = desktop / "scripts"
    dist = run_dir / "dist"
    work = run_dir / "build"
    specs = work / "specs"
    for directory in (dist, work, specs):
        directory.mkdir(parents=True, exist_ok=False)
    source_manifest = run_dir / "build-inputs.json"
    tool_manifest = run_dir / "toolchain-inputs.json"
    report = run_dir / "offline-candidate-evidence.json"
    executable = str(python)

    def check(args: list[str], *, timeout: int = 1800) -> None:
        if runner(args, root, timeout) != 0:
            raise CandidateBuildRejected(ERROR)

    def script(path: Path, *args: object) -> list[str]:
        return [executable, "-I", str(path), *(str(item) for item in args)]

    # CI-outage substitute for complete normal + optimized source regressions.
    check(script(scripts / "offline_source_gate.py"), timeout=3600)
    check(script(scripts / "toolchain_guard.py", "capture", tool_manifest))
    check(script(scripts / "build_input_guard.py", "capture", source_manifest))
    for name in APPS:
        check(script(scripts / "toolchain_guard.py", "check", tool_manifest))
        check(script(scripts / "build_input_guard.py", "check", source_manifest))
        check([executable, "-I", "-m", "PyInstaller", "--noconfirm", "--clean",
               "--onefile", "--windowed", "--paths", str(desktop),
               "--name", name, "--distpath", str(dist),
               "--workpath", str(work / name), "--specpath", str(specs),
               str(desktop / "launchers" / (name + ".py"))], timeout=3600)
        check(script(scripts / "build_input_guard.py", "check", source_manifest))
        check(script(scripts / "toolchain_guard.py", "check", tool_manifest))
    check(script(desktop / "build_inventory.py", dist))
    check(script(scripts / "build_input_guard.py", "check", source_manifest))
    check(script(scripts / "toolchain_guard.py", "check", tool_manifest))
    check(script(desktop / "release_gate.py", dist, "--smoke", "--report", report), timeout=1200)
    # Bind the independent recheck to bytes observed after the real six-EXE
    # smoke, but do not imply that an in-memory pin proves historical execution.
    try:
        evidence_info = report.lstat()
        if (not stat.S_ISREG(evidence_info.st_mode) or evidence_info.st_nlink != 1
                or not 0 < evidence_info.st_size <= 64 * 1024):
            raise CandidateBuildRejected(ERROR)
        report_hash = hashlib.sha256(report.read_bytes()).hexdigest()
    except (OSError, ValueError):
        raise CandidateBuildRejected(ERROR) from None
    check(script(desktop / "report_attestation.py", report, dist,
                 "--expected-report-sha256", report_hash))
    check(script(scripts / "build_input_guard.py", "check", source_manifest))
    check(script(scripts / "toolchain_guard.py", "check", tool_manifest))


def build_candidate(workspace: Path) -> None:
    """Build into a new private subfolder; erase failed candidates by default."""
    if not _windows_x64():
        raise CandidateBuildRejected(ERROR)
    destination = _workspace(ROOT, workspace)
    created = None
    completed = False
    try:
        created = Path(tempfile.mkdtemp(prefix="fvs-r269-private-", dir=destination))
        _execute_plan(ROOT, created, sys.executable)
        completed = True
    except (OSError, ValueError, RuntimeError, TypeError):
        raise CandidateBuildRejected(ERROR) from None
    finally:
        if created is not None and not completed:
            try:
                shutil.rmtree(created)
            except OSError:
                # If local OS access blocks cleanup, the private workspace
                # still must be treated as containing unreleased premium EXEs.
                pass


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True,
                        help="Existing access-controlled directory OUTSIDE this source checkout")
    args = parser.parse_args(argv)
    try:
        build_candidate(args.workspace)
    except CandidateBuildRejected:
        print(ERROR, file=sys.stderr)
        return 1
    print(SUCCESS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
