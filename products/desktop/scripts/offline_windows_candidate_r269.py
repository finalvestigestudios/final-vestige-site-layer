"""Private, owner-run six-EXE Windows candidate build when GitHub Actions is offline.

This is NOT release authorization. Requires an existing private workspace outside
this checkout and preinstalled, trusted Python, PyInstaller and cryptography.
Never uploads, publishes, signs, approves, or displays premium executables.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import tempfile

# -I excludes the script directory: trust only this resolved Git-owned helper
# location, never a caller-controlled cwd or PYTHONPATH.
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from strict_source_receipt_r273 import loads_strict_receipt

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
MAX_SOURCE_RECEIPT_BYTES = 1024 * 1024
MAX_WINDOWS_REPORT_BYTES = 64 * 1024


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


def _stat_identity(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _source_receipt_sha256(path: Path) -> str:
    """Require a bounded, untampered, native source-suite receipt for QD custody.

    Never trust a child's zero exit alone: source-suite tests and six source
    smokes must have written their explicit, non-release evidence. Validate the
    report before packaging and pin exactly those bytes through final checks.
    """
    try:
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or not 0 < before.st_size <= MAX_SOURCE_RECEIPT_BYTES):
            raise CandidateBuildRejected(ERROR)
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            # Windows Python path and descriptor stat modes/ctime can differ.
            # Require stable identity within each view and common structural
            # fields across views; do not weaken before/after comparisons.
            comparable = lambda v: (v.st_dev, v.st_ino, v.st_nlink, v.st_size, v.st_mtime_ns)
            if (not stat.S_ISREG(opened.st_mode) or comparable(opened) != comparable(before)):
                raise CandidateBuildRejected(ERROR)
            data = bytearray()
            while len(data) <= MAX_SOURCE_RECEIPT_BYTES:
                chunk = os.read(descriptor, min(65536, MAX_SOURCE_RECEIPT_BYTES + 1 - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
            finished = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        if (len(data) != before.st_size or len(data) > MAX_SOURCE_RECEIPT_BYTES
                or _stat_identity(opened) != _stat_identity(finished)
                or _stat_identity(before) != _stat_identity(path.lstat())):
            raise CandidateBuildRejected(ERROR)
        receipt = loads_strict_receipt(data)
        expected = {"schema", "scope", "released", "qd_approved",
                    "windows_executables_verified", "premium_download_authorized",
                    "normal_unittest", "optimized_unittest", "unittest_provenance",
                    "test_inventory", "source_smoke"}
        if type(receipt) is not dict or set(receipt) != expected:
            raise CandidateBuildRejected(ERROR)
        if (receipt["schema"] != "fvs-offline-source-suite-v1"
                or receipt["scope"] != "FULL_PYTHON_SOURCE_TESTS_ONLY_NOT_WINDOWS_BINARY"
                or receipt["released"] is not False or receipt["qd_approved"] is not False
                or receipt["windows_executables_verified"] is not False
                or receipt["premium_download_authorized"] is not False
                or receipt["normal_unittest"] != "PASS"
                or receipt["optimized_unittest"] != "PASS"):
            raise CandidateBuildRejected(ERROR)
        provenance = receipt["unittest_provenance"]
        provenance_keys = {"schema", "test_count", "module_count", "skipped_count",
                           "test_ids_sha256", "active_ids_sha256", "skipped_ids_sha256"}
        if (type(provenance) is not dict or set(provenance) != provenance_keys
                or provenance["schema"] != "fvs-unittest-provenance-v2"
                or type(provenance["test_count"]) is not int
                or type(provenance["module_count"]) is not int
                or type(provenance["skipped_count"]) is not int
                or not 6 <= provenance["module_count"] <= provenance["test_count"] <= 20000
                or not 0 <= provenance["skipped_count"] < provenance["test_count"]
                or any(type(provenance[key]) is not str
                       or len(provenance[key]) != 64
                       or any(ch not in "0123456789abcdef" for ch in provenance[key])
                       for key in ("test_ids_sha256", "active_ids_sha256", "skipped_ids_sha256"))):
            raise CandidateBuildRejected(ERROR)
        inventory = receipt["test_inventory"]
        if (type(inventory) is not list or not 1 <= len(inventory) <= 512
                or any(type(item) is not dict or set(item) != {"path", "sha256"}
                       or type(item["path"]) is not str
                       or not item["path"].startswith("products/desktop/tests/")
                       or type(item["sha256"]) is not str
                       or len(item["sha256"]) != 64
                       for item in inventory)):
            raise CandidateBuildRejected(ERROR)
        smoke = receipt["source_smoke"]
        if (type(smoke) is not dict or smoke.get("schema") != "fvs-source-smoke-v1"
                or smoke.get("all_six_passed") is not True
                or smoke.get("released") is not False
                or smoke.get("qd_approved") is not False):
            raise CandidateBuildRejected(ERROR)
        if (smoke.get("scope") != "PYTHON_SOURCE_ONLY_NOT_WINDOWS_BINARY_VERIFICATION"
                or not isinstance(smoke.get("source_inventory"), list)
                or not smoke["source_inventory"]):
            raise CandidateBuildRejected(ERROR)
        results = smoke.get("application_results")
        if (type(results) is not list or len(results) != 6
                or [item.get("app") if type(item) is dict else None for item in results] != list(APPS)
                or any(item.get("result") != "PASS" for item in results)):
            raise CandidateBuildRejected(ERROR)
        return hashlib.sha256(data).hexdigest()
    except (OSError, ValueError, TypeError, KeyError, UnicodeError):
        raise CandidateBuildRejected(ERROR) from None


def _private_windows_report_sha256(path: Path) -> str:
    """Hash a bounded native Windows evidence file without following links.

    An ordinary Path.read_bytes after lstat could follow a swapped link. Pin
    the descriptor/path identity before and after reading, and recheck the
    same evidence after the independent attestation and final custody gates.
    This is same-run custody, *not* a signature or post-run tamper defense.
    """
    try:
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or not 0 < before.st_size <= MAX_WINDOWS_REPORT_BYTES):
            raise CandidateBuildRejected(ERROR)
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            # Windows path and descriptor ctime/mode views can differ, but
            # every identity field must remain unchanged *within* each view.
            def comparable(info):
                return (info.st_dev, info.st_ino, info.st_nlink,
                        info.st_size, info.st_mtime_ns)
            if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                    or comparable(opened) != comparable(before)):
                raise CandidateBuildRejected(ERROR)
            data = bytearray()
            while len(data) <= MAX_WINDOWS_REPORT_BYTES:
                chunk = os.read(descriptor, min(65536, MAX_WINDOWS_REPORT_BYTES + 1 - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
            finished = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        if (len(data) != before.st_size or len(data) > MAX_WINDOWS_REPORT_BYTES
                or _stat_identity(opened) != _stat_identity(finished)
                or _stat_identity(before) != _stat_identity(path.lstat())):
            raise CandidateBuildRejected(ERROR)
        return hashlib.sha256(data).hexdigest()
    except (OSError, ValueError, TypeError):
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
    source_receipt = run_dir / "source-suite-evidence.json"
    source_manifest = run_dir / "build-inputs.json"
    tool_manifest = run_dir / "toolchain-inputs.json"
    report = run_dir / "offline-candidate-evidence.json"
    executable = str(python)

    def check(args: list[str], *, timeout: int = 1800) -> None:
        if runner(args, root, timeout) != 0:
            raise CandidateBuildRejected(ERROR)

    def script(path: Path, *args: object) -> list[str]:
        return [executable, "-I", str(path), *(str(item) for item in args)]

    # Capture a verifiable source-suite receipt, not just an unrecorded exit 0.
    check(script(scripts / "offline_source_gate.py", "--report", source_receipt), timeout=3600)
    source_receipt_pin = _source_receipt_sha256(source_receipt)
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
    # Preserve the exact native six-EXE evidence inspected by attestation.
    report_hash = _private_windows_report_sha256(report)
    check(script(desktop / "report_attestation.py", report, dist,
                 "--expected-report-sha256", report_hash))
    check(script(scripts / "build_input_guard.py", "check", source_manifest))
    check(script(scripts / "toolchain_guard.py", "check", tool_manifest))
    # Same-run double pin: an attest-then-replace report must never become a
    # successful private candidate. This does not authorize distribution.
    if (_private_windows_report_sha256(report) != report_hash
            or _source_receipt_sha256(source_receipt) != source_receipt_pin):
        raise CandidateBuildRejected(ERROR)


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
