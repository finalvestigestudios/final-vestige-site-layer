"""R101 Windows inventory forensics: read-only, static, private-safe counters.

Never replaces the mandatory R57 source test gate; never publishes customer
content, paths, file names, exception messages, identifiers or raw file data.
All observations are counts / known categorical integrity-check outcomes.
"""
from __future__ import annotations

from collections import Counter
import contextlib
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
DESKTOP = HERE.parent
ROOT = DESKTOP.parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import source_smoke_gate as gate

MAX_INVENTORY = 256
FIELDS = ("dev", "ino", "mode", "nlink", "size", "mtime", "ctime")
PERMITTED = frozenset(("PASS", "LSTAT", "REGULAR", "LINKS", "SIZE",
    "CONFINEMENT", "OPEN", "START_ID", "END_ID", "READ", "UNKNOWN",
    "SOURCE_SCAN", "TEST_SCAN", "INVENTORY_LIMIT"))


def _difference(before, after):
    """Bounded metadata identity-difference bitmask; never show stat values."""
    return sum(1 << i for i, (a, b) in enumerate(
        zip(gate._identity(before), gate._identity(after))) if a != b)


def _classify(path: Path, root: Path, *, fingerprint=None) -> str:
    """Independently classify a rejected fingerprint; never certify its safety.

    The original _fingerprint remains the sole authority. A classified PASS
    is allowed only when the *original* fingerprint succeeded.
    """
    if fingerprint is None:
        fingerprint = gate._fingerprint
    try:
        fingerprint(path, root)
        return "PASS"
    except (OSError, ValueError, RuntimeError):
        pass
    try:
        info = path.lstat()
    except (OSError, ValueError, RuntimeError):
        return "LSTAT"
    if not stat.S_ISREG(info.st_mode):
        return "REGULAR"
    if info.st_nlink != 1:
        return "LINKS"
    if info.st_size > gate.MAX_SOURCE_BYTES:
        return "SIZE"
    try:
        if not path.resolve(strict=True).is_relative_to(root):
            return "CONFINEMENT"
    except (OSError, ValueError, RuntimeError):
        return "CONFINEMENT"
    fd = None
    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
        fd = os.open(path, flags)
    except (OSError, ValueError, RuntimeError):
        return "OPEN"
    try:
        try:
            beginning = os.fstat(fd)
            mismatch = _difference(info, beginning)
            if mismatch:
                return "START_ID"
            consumed = 0
            while True:
                block = os.read(fd, gate._READ_SIZE)
                if not block:
                    break
                consumed += len(block)
                if consumed > gate.MAX_SOURCE_BYTES:
                    return "SIZE"
            final = os.fstat(fd)
            final_path = path.lstat()
            if (consumed != info.st_size or _difference(info, final)
                    or _difference(info, final_path)):
                return "END_ID"
        except (OSError, ValueError, RuntimeError):
            return "READ"
    finally:
        os.close(fd)
    # The original fingerprint failed but no reproducible metadata failure
    # was visible. Never recast a failing gate as green.
    return "UNKNOWN"


def _candidate_files(root: Path, scope: str) -> list[Path]:
    desktop = root / "products" / "desktop"
    if scope == "tests":
        tests = desktop / "tests"
        gate._checked_directory(tests, root)
        files = sorted(gate._package_python_sources(tests))
    elif scope == "sources":
        package, launchers, scripts = (desktop / n for n in ("fvs_suite", "launchers", "scripts"))
        for folder in (desktop, package, launchers, scripts):
            gate._checked_directory(folder, root)
        files = sorted(set(gate._package_python_sources(package)
             + gate._package_python_sources(scripts)
             + list(desktop.glob("*.py"))
             + list(launchers.glob("*.py"))))
    else:
        raise ValueError("Unknown static inventory class")
    if not 0 < len(files) <= MAX_INVENTORY:
        raise ValueError("Unbounded desktop inventory")
    return files


def probe(root: Path, scope: str, *, classify=None) -> dict[str, int]:
    """Return ONLY static category counts. No path or exception can escape."""
    if scope not in ("sources", "tests"):
        raise ValueError("Unknown static inventory class")
    root = Path(root).resolve(strict=True)
    if classify is None:
        classify = _classify
    try:
        files = _candidate_files(root, scope)
    except (OSError, ValueError, RuntimeError):
        return {scope.upper() + "_SCAN": 1}
    counts = Counter()
    counts["FILES"] = len(files)
    for path in files:
        try:
            with open(os.devnull, "w", encoding="utf-8") as sink:
                with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                    label = classify(path, root)
        except Exception:
            label = "UNKNOWN"
        if label not in PERMITTED:
            label = "UNKNOWN"
        counts[label] += 1
    return dict(counts)


def render(scope: str, counts: dict[str, int]) -> str:
    """One bounded line of uppercase static tokens and integer counts."""
    if scope not in ("sources", "tests"):
        raise ValueError("Unknown static inventory class")
    allow = PERMITTED | {"FILES"}
    if (type(counts) is not dict or len(counts) > len(allow)
            or any(k not in allow or type(v) is not int
                   or not 0 <= v <= MAX_INVENTORY for k,v in counts.items())):
        raise ValueError("Invalid private-safe stage receipt")
    return "FVS_R101_" + scope.upper() + ":" + ",".join(
        f"{key}={counts[key]}" for key in sorted(counts))


def main() -> int:
    for scope in ("sources", "tests"):
        try:
            data = probe(ROOT, scope)
            print(render(scope, data))
        except Exception:
            print("FVS_R101_" + scope.upper() + ":UNKNOWN=1")
    print("FVS_R101_RELEASE=HOLD_SOURCE_DIAGNOSTIC_ONLY")
    # Diagnostic success cannot authorize packaging. Unchanged R57 still must pass.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
