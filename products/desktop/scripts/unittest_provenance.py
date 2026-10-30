"""Privacy-safe, complete desktop unittest provenance for offline source evidence.

Intentionally emits only bounded test counts and a digest of test identifiers;
never writes traceback, synthetic fixture contents, or local filesystem paths.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

SCHEMA = "fvs-unittest-provenance-v1"
MAX_TEST_MODULES = 256
MAX_TEST_CASES = 20000


def _cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _cases(item)
        else:
            yield item


def run(root: Path) -> dict:
    """Run every test_*.py module, rejecting skipped-all or partial discovery."""
    root = Path(root).resolve(strict=True)
    directory = root / "products" / "desktop" / "tests"
    if not directory.is_dir():
        raise ValueError("Desktop regression tree unavailable")
    modules = {
        ".".join(path.relative_to(directory).with_suffix("").parts)
        for path in directory.rglob("test_*.py")
    }
    if not 0 < len(modules) <= MAX_TEST_MODULES:
        raise ValueError("Invalid desktop test module inventory")

    # unittest imports and tests can print financial fixtures or local paths.
    # Redirect all Python-level stdout/stderr during discovery and execution.
    with open(os.devnull, "w", encoding="utf-8") as sink:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            loader = unittest.TestLoader()
            suite = loader.discover(str(directory), pattern="test_*.py", top_level_dir=str(directory))
            cases = list(_cases(suite))
            if not 0 < len(cases) <= MAX_TEST_CASES:
                raise ValueError("Empty or oversized desktop test suite")
            identifiers = [case.id() for case in cases]
            if len(set(identifiers)) != len(identifiers):
                raise ValueError("Duplicate desktop test identity")
            loaded_modules = {".".join(identifier.split(".")[:-2]) for identifier in identifiers}
            if loaded_modules != modules:
                raise ValueError("Desktop test discovery omitted a module")
            result = unittest.TestResult()
            suite.run(result)

    if (not result.wasSuccessful() or result.testsRun != len(identifiers)
            or len(result.skipped) >= len(identifiers)):
        raise ValueError("Desktop regression suite failed or executed no active tests")
    digest = hashlib.sha256(("\n".join(sorted(identifiers)) + "\n").encode("utf-8")).hexdigest()
    return {
        "schema": SCHEMA,
        "test_count": result.testsRun,
        "module_count": len(modules),
        "skipped_count": len(result.skipped),
        "test_ids_sha256": digest,
    }


def main() -> int:
    try:
        summary = run(Path.cwd())
    except Exception:
        print("REJECTED: desktop unittest provenance unavailable", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
