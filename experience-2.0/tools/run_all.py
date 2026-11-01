#!/usr/bin/env python3
"""Run every Experience 2.0 check and print an honest table.

Statuses: PASS, FAIL, NOT RUN. A skipped test counts as NOT RUN, never PASS. Exit code: 0 all PASS; 1 any FAIL; 3 nothing failed
but something did not run (e.g. --offline). Results are written to experience-2.0/dist/test-results.json.

  python tools/run_all.py              # everything, including the live-media check (network)
  python tools/run_all.py --offline    # skips the live-media check: reported NOT RUN, exit 3
  python tools/run_all.py --perf       # also run the lab performance measurement
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

EX2 = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(cmd: list[str], cwd: Path = EX2) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def unittest_stage(name: str, pattern: str) -> dict:
    t0 = time.time()
    code, out = run([PY, "-m", "unittest", "discover", "-s", "tests", "-p", pattern, "-v"])
    ran = re.search(r"Ran (\d+) tests?", out)
    skipped = re.search(r"skipped=(\d+)", out)
    n = int(ran.group(1)) if ran else 0
    if skipped:
        status, detail = "NOT RUN", f"{skipped.group(1)} skipped test(s): skips are not passes"
    elif code == 0 and n > 0:
        status, detail = "PASS", f"{n} tests"
    else:
        status, detail = "FAIL", "\n".join(out.strip().splitlines()[-15:])
    return {"stage": name, "status": status, "detail": detail, "seconds": round(time.time() - t0, 1)}


def command_stage(name: str, cmd: list[str], ok_prefix: str = "OK") -> dict:
    t0 = time.time()
    code, out = run(cmd)
    last = (out.strip().splitlines() or [""])[-1]
    return {"stage": name, "status": "PASS" if code == 0 else "FAIL", "detail": last if code == 0 else out.strip()[-1200:], "seconds": round(time.time() - t0, 1)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--perf", action="store_true")
    args = ap.parse_args()

    stages = [
        command_stage("build is deterministic; plugin payload current", [PY, "tools/build_all.py", "--check"]),
        command_stage("atlas dataset matches a fresh assembly", [PY, "atlas/tools/build_dataset.py", "--check"]),
        command_stage("atlas dataset validates", [PY, "-I", "atlas/tools/validate_atlas.py"]),
        unittest_stage("builders, data validation, CSS/JS static analysis", "test_builders.py"),
        unittest_stage("atlas model, invariants, ingestion", "test_atlas.py"),
        unittest_stage("WordPress plugin (real PHP, WordPress stubs)", "test_plugin.py"),
        unittest_stage("browser: responsive, behaviour, fail-open, a11y (axe-core)", "test_browser.py"),
    ]
    if args.offline:
        for label in ("live media and NASA record verification", "hero text contrast over the real photograph"):
            stages.append({"stage": label, "status": "NOT RUN", "detail": "--offline", "seconds": 0})
    else:
        stages.append(command_stage("live media and NASA record verification", [PY, "tools/verify_media.py"]))
        stages.append(command_stage("hero text contrast over the real photograph", [PY, "tools/verify_hero_contrast.py"]))
    if args.perf:
        stages.append(command_stage("lab performance (desktop profile asserted)", [PY, "tools/measure_perf.py"]))

    width = max(len(s["stage"]) for s in stages)
    for s in stages:
        print(f"{s['status']:8s} {s['stage']:{width}s}  {s['detail'].splitlines()[0] if s['detail'] else ''}  ({s['seconds']}s)")
    for s in stages:
        if s["status"] == "FAIL":
            print(f"\n--- {s['stage']} ---\n{s['detail']}")
    out = EX2 / "dist"
    out.mkdir(exist_ok=True)
    (out / "test-results.json").write_text(json.dumps(stages, indent=2), encoding="utf-8")
    if any(s["status"] == "FAIL" for s in stages):
        return 1
    if any(s["status"] == "NOT RUN" for s in stages):
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
