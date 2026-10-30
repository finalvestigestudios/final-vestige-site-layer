"""Runner-independent, source-only verification of the six desktop products.

Run locally when hosted Actions fail before starting. Never treats Python source
success as Windows EXE validation, premium licensing, or QD release approval.
No test stdout/stderr or customer file contents are retained in evidence.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

DESKTOP = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
for directory in (DESKTOP, SCRIPTS):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import source_smoke_gate as source_gate
from report_evidence import prepare_report_path, publish_report

MAX_TEST_FILES = 256


def _test_inventory(root: Path, gate=source_gate) -> list[dict[str, str]]:
    """Fingerprint all Python test helpers, not just filenames matching test_*.

    Otherwise a substituted/modified test could produce apparently passing
    evidence without appearing in the source-only smoke inventory.
    """
    directory = root / "products" / "desktop" / "tests"
    gate._checked_directory(directory, root)
    files = sorted(gate._package_python_sources(directory))
    if not files or len(files) > MAX_TEST_FILES or not any(
        path.name.startswith("test_") for path in files
    ):
        raise ValueError("Incomplete desktop regression test tree")
    return [
        {"path": path.relative_to(root).as_posix(),
         "sha256": gate._fingerprint(path, root)} for path in files
    ]


def _snapshot(root: Path, gate=source_gate) -> tuple[list[dict], list[dict], list[tuple], list[tuple]]:
    sources = gate.source_inventory(root)
    tests = _test_inventory(root, gate)
    return (sources, tests, gate._source_metadata(root, sources),
            gate._source_metadata(root, tests))


def _require_unchanged(root: Path, before: tuple, gate=source_gate) -> None:
    if _snapshot(root, gate) != before:
        raise RuntimeError("Source or test files changed during offline verification; evidence withheld")


def _validated_suite_summary(data) -> dict:
    """Require a bounded, exact child manifest; never trust a success exit alone."""
    expected = {"schema", "test_count", "module_count", "skipped_count", "test_ids_sha256"}
    if type(data) is not dict or set(data) != expected:
        raise RuntimeError("Complete desktop regression provenance missing")
    if data["schema"] != "fvs-unittest-provenance-v1":
        raise RuntimeError("Complete desktop regression provenance schema invalid")
    count, modules, skipped = (data[key] for key in ("test_count", "module_count", "skipped_count"))
    if (type(count) is not int or type(modules) is not int or type(skipped) is not int
            or not 1 <= modules <= MAX_TEST_FILES or not modules <= count <= 20000
            or not 0 <= skipped < count):
        raise RuntimeError("Complete desktop regression provenance counts invalid")
    digest = data["test_ids_sha256"]
    if (type(digest) is not str or len(digest) != 64
            or any(ch not in "0123456789abcdef" for ch in digest)):
        raise RuntimeError("Complete desktop regression provenance digest invalid")
    return data


def _child_suite(root: Path, optimized: bool, *, timeout: int) -> dict:
    """Execute all tests while obtaining only a bounded, privacy-safe manifest."""
    desktop = root / "products" / "desktop"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(desktop)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONHASHSEED"] = "0"
    command = [sys.executable]
    if optimized:
        command.append("-OO")
    command.append(str(desktop / "scripts" / "unittest_provenance.py"))
    try:
        result = subprocess.run(
            command, cwd=root, env=env, timeout=timeout,
            check=False, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Complete desktop regression suite timed out") from exc
    except OSError as exc:
        raise RuntimeError("Could not execute complete desktop regression suite") from exc
    if result.returncode != 0:
        mode = "optimized" if optimized else "normal"
        raise RuntimeError(f"Complete desktop {mode} regression suite failed; rerun unittest locally")
    payload = result.stdout
    if type(payload) is not bytes or not 0 < len(payload) <= 1024:
        raise RuntimeError("Complete desktop regression provenance missing or oversized")
    try:
        summary = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Complete desktop regression provenance malformed") from exc
    return _validated_suite_summary(summary)


def verify_source_suite(root: Path, run_tests, run_smoke, *, commit: str = "",
                        gate=source_gate) -> dict:
    """Accept evidence ONLY when two full test passes and all six smokes hold.

    ``run_tests`` takes a bool for Python -OO. Injection is for synthetic tests,
    not a public bypass: published evidence always says no release authorization.
    """
    root = Path(root).resolve(strict=True)
    initial = _snapshot(root, gate)
    summaries = []
    for optimized in (False, True):
        summaries.append(_validated_suite_summary(run_tests(optimized)))
        _require_unchanged(root, initial, gate)
    if summaries[0] != summaries[1]:
        raise RuntimeError("Normal and optimized desktop test coverage differs; evidence withheld")
    smoke = gate.report_data(root, run_smoke, commit=commit)
    _require_unchanged(root, initial, gate)
    if not smoke["all_six_passed"] or len(smoke["application_results"]) != 6:
        raise RuntimeError("Six-engine source smoke was incomplete")
    return {
        "schema": "fvs-offline-source-suite-v1",
        "scope": "FULL_PYTHON_SOURCE_TESTS_ONLY_NOT_WINDOWS_BINARY",
        "released": False, "qd_approved": False,
        "windows_executables_verified": False,
        "premium_download_authorized": False,
        "normal_unittest": "PASS", "optimized_unittest": "PASS",
        "unittest_provenance": summaries[0],
        "test_inventory": initial[1],
        "source_smoke": smoke,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path,
                        help="NEW JSON evidence path outside the source checkout")
    parser.add_argument("--timeout", type=int, default=1800,
                        help="Per-test-pass timeout in seconds (60 to 3600)")
    args = parser.parse_args(argv)
    if not 60 <= args.timeout <= 3600:
        parser.error("--timeout must be between 60 and 3600 seconds")
    root = DESKTOP.parents[1]
    try:
        destination = prepare_report_path(args.report, root) if args.report else None
        from fvs_suite.smoke import run_smoke
        evidence = verify_source_suite(
            root, lambda optimized: _child_suite(root, optimized, timeout=args.timeout),
            run_smoke, commit=os.environ.get("GITHUB_SHA", ""),
        )
        if destination is not None:
            publish_report(destination, evidence)
    except (OSError, ValueError, RuntimeError):
        # Only fixed errors leave this process: no customer paths or file rows.
        print("REJECTED: offline source-only suite did not pass; inspect local tests", file=sys.stderr)
        return 1
    print("PASS: complete desktop unittest suite (normal and -OO), six source smokes; "
          "NOT Windows EXE verification or QD release approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
