"""Runner-independent, source-only verification of the six desktop products.

Run locally when hosted Actions fail before starting. Never treats Python source
success as Windows EXE validation, premium licensing, or QD release approval.
No test stdout/stderr or customer file contents are retained in evidence.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
import subprocess
import sys

DESKTOP = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
for directory in (DESKTOP, SCRIPTS):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import source_smoke_gate as source_gate
import unittest_provenance as source_test_inventory
from report_evidence import prepare_report_path, publish_report

MAX_TEST_FILES = 512

DIAG_PREFIX = "FVS_TEST_DIAG:"
DIAG_SCHEMA = "fvs-offline-failure-modules-v1"
MAX_DIAG_MODULES = 12
_DIAG_MODULE_RE = re.compile(r"test_[a-z0-9_]{1,90}\Z")
_DIAG_METHOD_RE = re.compile(r"test_[a-z0-9_]{1,90}\.test_[a-z0-9_]{1,90}\Z")
_MAX_DIAG_METHODS = 10
_MAX_DIAG_METHOD_LABEL = 104


class SourceSuiteFailure(RuntimeError):
    """A failing source suite with optional validated, non-sensitive module names."""

    def __init__(self, message: str, diagnostic: str | None = None):
        super().__init__(message)
        self.diagnostic = diagnostic


def _safe_child_diagnostic(payload, *, allowed_methods=None):
    """Validate every displayed source-owned test method against an AST allowlist.

    Legacy module-only R98/R99 diagnostic shapes remain supported.
    Never display a child-supplied method name without an independent
    source-tree allowlist; ignore raw exception messages and subtest data.
    """
    if type(payload) is not bytes or not 0 < len(payload) <= 2048:
        return None
    try:
        line = payload.decode("ascii")
    except UnicodeDecodeError:
        return None
    # Python writes one CRLF line on Windows and one LF line on Linux.
    # Strip exactly one terminal delimiter; internal CR/LF still fails closed.
    if line.endswith("\r\n"):
        line = line[:-2]
    elif line.endswith("\n"):
        line = line[:-1]
    if "\n" in line or "\r" in line or not line.startswith(DIAG_PREFIX):
        return None
    try:
        data = json.loads(line[len(DIAG_PREFIX):])
    except (ValueError, TypeError):
        return None
    basic = {"schema", "phase", "failures", "errors", "modules", "omitted_module_count"}
    extended = basic | {"methods", "omitted_method_count"}
    if type(data) is not dict or set(data) not in (basic, extended):
        return None
    has_methods = set(data) == extended
    if data["schema"] != DIAG_SCHEMA or data["phase"] not in ("discovery", "execution"):
        return None
    for name in ("failures", "errors", "omitted_module_count"):
        if type(data[name]) is not int or not 0 <= data[name] <= 20000:
            return None
    if data["phase"] == "execution" and data["failures"] + data["errors"] < 1:
        return None
    if data["phase"] == "discovery" and (data["failures"] or data["errors"]):
        return None
    names = data["modules"]
    if (type(names) is not list or len(names) > MAX_DIAG_MODULES or
            any(type(name) is not str or not _DIAG_MODULE_RE.fullmatch(name) for name in names) or
            names != sorted(set(names))):
        return None
    if data["omitted_module_count"] and len(names) != MAX_DIAG_MODULES:
        return None
    if (data["phase"] == "execution" and
            len(names) + data["omitted_module_count"] > data["failures"] + data["errors"]):
        return None
    if has_methods and allowed_methods is None:
        # Existing R98 callers have no source AST allowlist. Preserve their
        # module-only behavior by discarding the entire untrusted extension;
        # never echo a method string that the parent has not inventoried.
        data = {key: data[key] for key in basic}
        has_methods = False
    if has_methods:
        methods = data["methods"]
        omitted = data["omitted_method_count"]
        if (data["phase"] != "execution" or type(allowed_methods) is not set
                or type(methods) is not list or len(methods) > _MAX_DIAG_METHODS
                or type(omitted) is not int or not 0 <= omitted <= 20000
                or any(type(name) is not str or len(name) > _MAX_DIAG_METHOD_LABEL
                       or not _DIAG_METHOD_RE.fullmatch(name)
                       or name not in allowed_methods for name in methods)
                or methods != sorted(set(methods))
                or (omitted and len(methods) != _MAX_DIAG_METHODS)
                or len(methods) + omitted > data["failures"] + data["errors"]):
            return None
    return DIAG_PREFIX + json.dumps(data, sort_keys=True, separators=(",", ":"))



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
    expected = {"schema", "test_count", "module_count", "skipped_count",
                "test_ids_sha256", "active_ids_sha256", "skipped_ids_sha256"}
    if type(data) is not dict or set(data) != expected:
        raise RuntimeError("Complete desktop regression provenance missing")
    if data["schema"] != "fvs-unittest-provenance-v2":
        raise RuntimeError("Complete desktop regression provenance schema invalid")
    count, modules, skipped = (data[key] for key in ("test_count", "module_count", "skipped_count"))
    if (type(count) is not int or type(modules) is not int or type(skipped) is not int
            or not 1 <= modules <= MAX_TEST_FILES or not modules <= count <= 20000
            or not 0 <= skipped < count):
        raise RuntimeError("Complete desktop regression provenance counts invalid")
    for key in ("test_ids_sha256", "active_ids_sha256", "skipped_ids_sha256"):
        digest = data[key]
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
        # Parse known Git-owned test definitions, never runtime subtest IDs.
        # A broken/unreadable source tree must not admit method-level output.
        try:
            allowed_methods = source_test_inventory._source_method_inventory(
                desktop / "tests")
        except (OSError, UnicodeError, SyntaxError, ValueError):
            allowed_methods = set()
        raise SourceSuiteFailure(
            f"Complete desktop {mode} regression suite failed; rerun unittest locally",
            _safe_child_diagnostic(result.stdout, allowed_methods=allowed_methods),
        )
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
    except SourceSuiteFailure as exc:
        if exc.diagnostic is not None:
            print(exc.diagnostic, file=sys.stderr)
        print("REJECTED: offline source-only suite did not pass; inspect local tests", file=sys.stderr)
        return 1
    except (OSError, ValueError, RuntimeError):
        # Only fixed errors leave this process: no customer paths or file rows.
        print("REJECTED: offline source-only suite did not pass; inspect local tests", file=sys.stderr)
        return 1
    print("PASS: complete desktop unittest suite (normal and -OO), six source smokes; "
          "NOT Windows EXE verification or QD release approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
