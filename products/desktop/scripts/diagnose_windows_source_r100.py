"""R100 read-only Windows source-stage diagnostic; NEVER a release gate.

Actual mandatory offline_source_gate.py must still run afterward and pass.
Never display exception text, filesystem paths, private inputs or traceback.
"""
from __future__ import annotations

import contextlib
import os
from pathlib import Path

from scripts import offline_source_gate as gate

PHASES = ("root_paths", "checked_test_dir", "scan_test_tree",
          "fingerprint_test", "fingerprint_engine", "source_inventory",
          "test_inventory", "source_metadata", "inventory", "normal_tests",
          "optimized_tests", "engine_smokes")


def _quiet_stage(label, operation):
    if label not in PHASES:
        raise ValueError("Unknown static diagnostic stage")
    value = None
    succeeded = False
    with open(os.devnull, "w", encoding="utf-8") as sink:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            try:
                value = operation()
                succeeded = True
            except Exception:
                # Raw exceptions may include confidential local test input.
                pass
    print("FVS_WIN_SOURCE_STAGE:" + label + "=" + ("PASS" if succeeded else "BLOCKED"))
    return succeeded, value


def probe(root: Path) -> dict[str, bool]:
    """Independent observations, not a replacement for two-mode source gates."""
    root = Path(root)
    results = {}

    def check_paths():
        expected = (root, root / "products" / "desktop",
                    root / "products" / "desktop" / "tests",
                    root / "products" / "desktop" / "fvs_suite")
        if not all(folder.is_dir() for folder in expected):
            raise ValueError("Required directories unavailable")

    ok, _ = _quiet_stage("root_paths", check_paths)
    results["root_paths"] = ok
    tests_dir = root / "products" / "desktop" / "tests"
    checks = (
        ("checked_test_dir", lambda: gate.source_gate._checked_directory(tests_dir, root)),
        ("scan_test_tree", lambda: gate.source_gate._package_python_sources(tests_dir)),
        ("fingerprint_test", lambda: gate.source_gate._fingerprint(tests_dir / "test_engine.py", root)),
        ("fingerprint_engine", lambda: gate.source_gate._fingerprint(
            root / "products" / "desktop" / "fvs_suite" / "engine.py", root)),
    )
    for label, operation in checks:
        passed, _ = _quiet_stage(label, operation)
        results[label] = passed
    ok, source = _quiet_stage(
        "source_inventory", lambda: gate.source_gate.source_inventory(root))
    results["source_inventory"] = ok
    ok, tests = _quiet_stage(
        "test_inventory", lambda: gate._test_inventory(root))
    results["test_inventory"] = ok
    def metadata():
        if source is None or tests is None:
            raise ValueError("Incomplete inventory")
        gate.source_gate._source_metadata(root, source)
        gate.source_gate._source_metadata(root, tests)
    ok, _ = _quiet_stage("source_metadata", metadata)
    results["source_metadata"] = ok
    ok, _ = _quiet_stage("inventory", lambda: gate._snapshot(root))
    results["inventory"] = ok
    if not ok:
        # If source custody is already broken, don't spend minutes executing
        # redundant suites or risk misleading smoke evidence. Only the
        # mandatory R57 gate can authorize subsequent CI packaging.
        for name in ("normal_tests", "optimized_tests", "engine_smokes"):
            results[name] = False
            print("FVS_WIN_SOURCE_STAGE:" + name + "=NOT_RUN_INVENTORY_BLOCKED")
        print("FVS_WIN_SOURCE_STAGE:read_only_no_release=TRUE")
        return results

    for optimized, name in ((False, "normal_tests"), (True, "optimized_tests")):
        passed, _ = _quiet_stage(
            name, lambda mode=optimized: gate._child_suite(root, mode, timeout=1800))
        results[name] = passed

    def smoke():
        from fvs_suite.smoke import run_smoke
        record = gate.source_gate.report_data(root, run_smoke)
        if not record.get("all_six_passed"):
            raise RuntimeError("Incomplete source smokes")
    passed, _ = _quiet_stage("engine_smokes", smoke)
    results["engine_smokes"] = passed
    print("FVS_WIN_SOURCE_STAGE:read_only_no_release=TRUE")
    return results


def main() -> int:
    probe(gate.DESKTOP.parents[1])
    # This is diagnostic-only. The next mandatory R57 full gate, unchanged,
    # is the only accepting authority for Windows packaging.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
