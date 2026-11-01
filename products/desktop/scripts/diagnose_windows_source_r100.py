"""R100 read-only Windows source-stage diagnostic; NEVER a release gate.

Actual mandatory offline_source_gate.py must still run afterward and pass.
Never display exception text, filesystem paths, private inputs or traceback.
"""
from __future__ import annotations

import contextlib
import os
from pathlib import Path

from scripts import offline_source_gate as gate

PHASES = ("inventory", "normal_tests", "optimized_tests", "engine_smokes")


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
    ok, _ = _quiet_stage("inventory", lambda: gate._snapshot(root))
    results["inventory"] = ok

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
