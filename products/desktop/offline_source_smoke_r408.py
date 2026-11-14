"""Run all six real source launchers' offline smokes without GitHub Actions.

This is source-only evidence, never Windows executable, AV or release approval.
Private subprocess output is discarded rather than reflected in receipts.
"""
from __future__ import annotations

import ast
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
# Bound the entire untrusted import tree before rglob/materialization or child
# launch. Per-file size checks alone permit arbitrarily many tiny files or
# directories, exhausting memory/time during repeated SHA-256 walks.
MAX_IMPORT_FILES = 512
MAX_IMPORT_DIRS = 128
MAX_IMPORT_BYTES = 16_000_000
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
_LAUNCHER_APP_IDS = {name: app for app, name in PRODUCTS}


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
    file_count = 0
    dir_count = 2  # Both mandatory import roots also count against the budget.
    total_bytes = 0
    for import_root in (desktop / "fvs_suite", desktop / "launchers"):
        for root, directories, files in os.walk(
                import_root, followlinks=False, onerror=reject_unreadable):
            # Reject an oversized directory listing before walking its entries.
            # Count all entries, including files with no meaningful extension.
            if (dir_count + len(directories) > MAX_IMPORT_DIRS or
                    file_count + len(files) > MAX_IMPORT_FILES):
                raise SourceGateError("Desktop source inventory exceeds safe bounds")
            dir_count += len(directories)
            file_count += len(files)
            for name in directories:
                _require_real_directory(Path(root) / name)
            for name in files:
                path = Path(root) / name
                _require_real_source_file(path)
                if name.casefold().endswith(_BLOCKED_IMPORT_SUFFIXES):
                    raise SourceGateError("Untrusted compiled import in desktop source inventory")
                try:
                    size = path.lstat().st_size
                except OSError:
                    raise SourceGateError("Unsafe desktop source file") from None
                # Do not read or hash unbounded single files or cumulative data.
                if size <= 0 or size > MAX_SOURCE_BYTES:
                    raise SourceGateError("Desktop source inventory exceeds safe bounds")
                total_bytes += size
                if total_bytes > MAX_IMPORT_BYTES:
                    raise SourceGateError("Desktop source inventory exceeds safe bounds")



def _verify_launcher_route(source: bytes, app_id: str) -> None:
    """Require each named launcher to call the shared launch() for its own app.

    An unexecuted or wrong-product launcher can otherwise return exit code zero
    and create twelve false-positive source smoke receipts. Parse without
    executing source. This is a launcher-route check, not a code signature.
    """
    try:
        tree = ast.parse(source, filename="<desktop-launcher>")
    except (SyntaxError, ValueError, UnicodeError):
        raise SourceGateError("Unsafe desktop launcher route") from None
    statements = tree.body
    if (statements and isinstance(statements[0], ast.Expr) and
            isinstance(statements[0].value, ast.Constant) and
            isinstance(statements[0].value.value, str)):
        statements = statements[1:]  # Optional harmless module docstring.
    if len(statements) != 2:
        raise SourceGateError("Unsafe desktop launcher route")
    imported, entry = statements
    if (not isinstance(imported, ast.ImportFrom) or imported.level != 0 or
            imported.module != "fvs_suite.launcher" or
            len(imported.names) != 1 or imported.names[0].name != "launch" or
            imported.names[0].asname is not None):
        raise SourceGateError("Unsafe desktop launcher route")
    if isinstance(entry, ast.If):
        guard = entry.test
        if (entry.orelse or len(entry.body) != 1 or
                not isinstance(guard, ast.Compare) or
                not isinstance(guard.left, ast.Name) or
                guard.left.id != "__name__" or
                len(guard.ops) != 1 or not isinstance(guard.ops[0], ast.Eq) or
                len(guard.comparators) != 1 or
                not isinstance(guard.comparators[0], ast.Constant) or
                guard.comparators[0].value != "__main__"):
            raise SourceGateError("Unsafe desktop launcher route")
        entry = entry.body[0]
    if not isinstance(entry, ast.Expr) or not isinstance(entry.value, ast.Call):
        raise SourceGateError("Unsafe desktop launcher route")
    call = entry.value
    if (not isinstance(call.func, ast.Name) or call.func.id != "launch" or
            len(call.args) != 1 or call.keywords or
            not isinstance(call.args[0], ast.Constant) or
            type(call.args[0].value) is not str or
            call.args[0].value != app_id):
        raise SourceGateError("Unsafe desktop launcher route")


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
            if path.parent == desktop / "launchers" and path.name in _LAUNCHER_APP_IDS:
                _verify_launcher_route(raw, _LAUNCHER_APP_IDS[path.name])
            label = path.relative_to(desktop).as_posix().encode("ascii")
        except SourceGateError:
            raise  # Fixed, non-private launcher/asset rejection; never chain input.
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
