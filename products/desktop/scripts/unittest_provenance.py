"""Privacy-safe, complete desktop unittest provenance for offline source evidence.

Intentionally emits only bounded test counts and digests of test identifiers;
never writes traceback, synthetic fixture contents, or local filesystem paths.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
from pathlib import Path
import sys
import unittest

SCHEMA = "fvs-unittest-provenance-v2"
MAX_TEST_MODULES = 256
MAX_TEST_CASES = 20000

DIAG_PREFIX = "FVS_TEST_DIAG:"
DIAG_SCHEMA = "fvs-offline-failure-modules-v1"
MAX_DIAG_MODULES = 12
MODULE_RE = re.compile(r"test_[a-z0-9_]{1,90}\Z")


def _public_failure_summary(result, modules):
    """Only code-owned module names; never exception strings, paths, or subtest data."""
    names = set()
    for case, _private_traceback in (*result.failures, *result.errors):
        original = getattr(case, "test_case", case)
        name = type(original).__module__
        if name in modules and MODULE_RE.fullmatch(name):
            names.add(name)
    selected = sorted(names)
    return {
        "schema": DIAG_SCHEMA,
        "phase": "execution",
        "failures": len(result.failures),
        "errors": len(result.errors),
        "modules": selected[:MAX_DIAG_MODULES],
        "omitted_module_count": max(0, len(selected) - MAX_DIAG_MODULES),
    }


def _discovery_summary(modules, loaded_modules):
    """List only static, missing source-test basenames, not import exceptions."""
    missing = sorted(name for name in modules - loaded_modules if MODULE_RE.fullmatch(name))
    return {
        "schema": DIAG_SCHEMA,
        "phase": "discovery",
        "failures": 0,
        "errors": 0,
        "modules": missing[:MAX_DIAG_MODULES],
        "omitted_module_count": max(0, len(missing) - MAX_DIAG_MODULES),
    }


def _emit_diagnostic(data):
    """Single bounded stdout line; parent validates schema before showing it."""
    print(DIAG_PREFIX + json.dumps(data, sort_keys=True, separators=(",", ":")))



def _cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _cases(item)
        else:
            yield item


def _digest_ids(identifiers):
    """Only hash sorted case IDs; never serialize skip reasons or test output."""
    payload = ("\n".join(sorted(identifiers)) + ("\n" if identifiers else "")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _module_id(identifier: str) -> str:
    """Extract Python test module from the conventional unittest case ID."""
    return ".".join(identifier.split(".")[:-2])


def run(root: Path) -> dict:
    """Execute all inventoried tests and reject coverage lost to skipped modules."""
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
            loaded_modules = {_module_id(identifier) for identifier in identifiers}
            if loaded_modules != modules:
                _emit_diagnostic(_discovery_summary(modules, loaded_modules))
                raise ValueError("Desktop test discovery omitted a module")
            result = unittest.TestResult()
            suite.run(result)

    if not result.wasSuccessful():
        _emit_diagnostic(_public_failure_summary(result, modules))
    if not result.wasSuccessful() or result.testsRun != len(identifiers):
        raise ValueError("Desktop regression suite failed or did not execute every case")
    skipped_ids = [case.id() for case, _reason in result.skipped]
    skipped_set = set(skipped_ids)
    if len(skipped_set) != len(skipped_ids) or not skipped_set.issubset(identifiers):
        raise ValueError("Desktop regression skip provenance invalid")
    active_ids = set(identifiers) - skipped_set
    if not active_ids or {_module_id(identifier) for identifier in active_ids} != modules:
        raise ValueError("Desktop regression module has no executed tests")
    return {
        "schema": SCHEMA,
        "test_count": result.testsRun,
        "module_count": len(modules),
        "skipped_count": len(skipped_set),
        "test_ids_sha256": _digest_ids(identifiers),
        "active_ids_sha256": _digest_ids(active_ids),
        "skipped_ids_sha256": _digest_ids(skipped_set),
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
