"""Run all six real source launchers' offline smokes without GitHub Actions.

This is source-only evidence, never Windows executable, AV or release approval.
Private subprocess output is discarded rather than reflected in receipts.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

PRODUCTS = (
    ("ledger", "LedgerDiffLite.py"),
    ("invoices", "InvoiceTwinScout.py"),
    ("spend", "SpendMapLite.py"),
    ("policy", "PolicyDeltaDesk.py"),
    ("grants", "GrantAuditStudioPro.py"),
    ("procurement", "ProcureGuardStudioPro.py"),
)
BOOTSTRAP = (
    "import runpy,sys; "
    "sys.path.insert(0,sys.argv[1]); "
    "p=sys.argv[2]; sys.argv=[p,'--smoke-test']; "
    "runpy.run_path(p,run_name='__main__')"
)
MAX_SOURCE_BYTES = 2_000_000
# Explicitly retain only runtime variables used to locate OS/Python libraries and
# a temporary workspace. Sensitive credentials, proxy endpoints, custom Python
# import overrides and arbitrary CI secrets never enter smoke children.
_CHILD_RUNTIME_ENV = frozenset({
    "PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR",
})
# Python can execute a cached .pyc even when the hashed .py differs. Native
# extensions are likewise executable imports but absent from the .py digest.
# This *source-only* gate must refuse them rather than attest their contents.
_BLOCKED_IMPORT_SUFFIXES = (".pyc", ".pyo", ".pyd", ".so", ".dll")


class SourceGateError(ValueError):
    """Only fixed, private-data-free errors are exposed."""


def _child_environment() -> dict[str, str]:
    """Use a minimal, cross-platform subprocess environment, not caller secrets.

    Windows environment variables are case-insensitive; match key names by
    case-folding while preserving original spelling and ordinary temp paths.
    """
    safe = {key: value for key, value in os.environ.items()
            if key.upper() in _CHILD_RUNTIME_ENV}
    safe["PYTHONDONTWRITEBYTECODE"] = "1"
    return safe


def _require_real_directory(path: Path) -> None:
    """Reject symlink/junction traversal before hashing or running source.

    Windows directory junctions can report as directories; the reparse flag
    must be checked independently of the POSIX file type bits.
    """
    try:
        info = path.lstat()
    except OSError:
        raise SourceGateError("Unsafe desktop source directory") from None
    if (not stat.S_ISDIR(info.st_mode) or
            getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise SourceGateError("Unsafe desktop source directory")


def _require_real_source_file(path: Path) -> None:
    """Refuse linked/reparse/special source and asset files, including hardlinks.

    Even non-Python CSV/JSON templates can alter smoke behavior. A symlink,
    NTFS reparse file or hardlink to an external file must not escape custody.
    """
    try:
        info = path.lstat()
    except OSError:
        raise SourceGateError("Unsafe desktop source file") from None
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or
            getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise SourceGateError("Unsafe desktop source file")


def _verify_source_directories(desktop: Path) -> None:
    # Check *every* ancestor, not just desktop itself: desktop located beneath
    # a linked parent can redirect a seemingly ordinary suite outside custody.
    # Reject relative roots rather than silently resolving away linked parents.
    if not desktop.is_absolute():
        raise SourceGateError("Unsafe desktop source directory")
    for ancestor in reversed((desktop, *desktop.parents)):
        _require_real_directory(ancestor)
    for path in (desktop / "fvs_suite", desktop / "launchers"):
        _require_real_directory(path)

    def reject_unreadable(error: OSError) -> None:
        raise SourceGateError("Unsafe desktop source directory") from None

    # pathlib.rglob('*.py') can omit linked subdirectories. Also, existing
    # __pycache__ bytecode and native extension files can execute code that is
    # *not* in our hashed .py inventory. Refuse them in both import roots.
    # Ordinary local data assets such as JSON/CSV remain allowed.
    for import_root in (desktop / "fvs_suite", desktop / "launchers"):
        for root, directories, files in os.walk(
                import_root, followlinks=False, onerror=reject_unreadable):
            for name in directories:
                _require_real_directory(Path(root) / name)
            for name in files:
                _require_real_source_file(Path(root) / name)
                if name.casefold().endswith(_BLOCKED_IMPORT_SUFFIXES):
                    raise SourceGateError("Untrusted compiled import in desktop source inventory")


def source_digest(desktop: Path) -> str:
    """Fingerprint all import-root files, six launchers and this gate by bytes.

    The digest is an inventory identity, NOT source provenance or a signed build.
    """
    _verify_source_directories(desktop)
    # Measure *every* ordinary asset and Python module in import roots. A
    # changed CSV/JSON fixture or an additional launcher module can influence a
    # smoke without changing one of the six named launcher scripts.
    roots = (desktop / "fvs_suite", desktop / "launchers")
    paths = [*(p for root in roots for p in root.rglob("*") if p.is_file()),
             desktop / "offline_source_smoke_r408.py"]
    if (len(paths) < len(PRODUCTS) + 2 or any(
            desktop / "launchers" / name not in paths for _, name in PRODUCTS)):
        raise SourceGateError("Required desktop source inventory is incomplete")
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda p: p.relative_to(desktop).as_posix()):
        try:
            info = path.lstat()
            _require_real_source_file(path)
            if not 0 < info.st_size <= MAX_SOURCE_BYTES:
                raise SourceGateError("Unsafe desktop source inventory")
            raw = path.read_bytes()
            if len(raw) != info.st_size:
                raise SourceGateError("Desktop source changed during hashing")
            label = path.relative_to(desktop).as_posix().encode("ascii")
        except (OSError, UnicodeError, ValueError):
            raise SourceGateError("Cannot verify local desktop source inventory") from None
        digest.update(len(label).to_bytes(4, "big"))
        digest.update(label)
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(hashlib.sha256(raw).digest())
    return digest.hexdigest()


def run_gate(desktop: Path, *, timeout: int = 90) -> dict:
    """Run 12 separate source smokes; no customer file or executable invoked."""
    digest = source_digest(desktop)
    results = []
    passed = 0
    for app, launcher_name in PRODUCTS:
        statuses = {}
        for mode in ("normal", "optimized"):
            # Check the full import inventory *before each* new process. The
            # original final-only check let 11 more children run after a source
            # had changed, which was unsafe evidence and unnecessary execution.
            if source_digest(desktop) != digest:
                raise SourceGateError("Desktop source changed during source smoke checks")
            # -I ignores PYTHON* environment variables, including the child
            # PYTHONDONTWRITEBYTECODE=1 setting. -B is therefore required to
            # prevent our own smoke process creating unmeasured .pyc files.
            command = [sys.executable, "-I", "-B", "-W", "error"]
            if mode == "optimized":
                command.append("-OO")
            command += ["-c", BOOTSTRAP, str(desktop),
                        str(desktop / "launchers" / launcher_name)]
            try:
                completed = subprocess.run(
                    command, cwd=desktop, env=_child_environment(),
                    # Never hold arbitrary private child output in process memory.
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, timeout=timeout, check=False,
                )
                ok = completed.returncode == 0
            except (OSError, subprocess.TimeoutExpired):
                ok = False
            # A child may have modified source while it ran; stop immediately
            # rather than allowing the remaining 11 source processes to run.
            if source_digest(desktop) != digest:
                raise SourceGateError("Desktop source changed during source smoke checks")
            statuses[mode] = "pass" if ok else "fail"
            passed += int(ok)
        results.append({"app": app, **statuses})
    if source_digest(desktop) != digest:
        raise SourceGateError("Desktop source changed during source smoke checks")
    return {"schema": "fvs-source-smoke-r408-v1", "source_sha256": digest,
            "evidence": "SOURCE_ONLY_NOT_WINDOWS_BINARY", "tests": results,
            "passed": passed, "required": len(PRODUCTS) * 2,
            "release_authorized": False}


def main() -> int:
    # Keep lexical ancestry visible; resolve() would erase linked parents.
    desktop = Path(os.path.abspath(__file__)).parent
    try:
        result = run_gate(desktop)
    except SourceGateError:
        print('{"error":"Local source smoke inventory rejected","release_authorized":false}')
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["passed"] == result["required"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
