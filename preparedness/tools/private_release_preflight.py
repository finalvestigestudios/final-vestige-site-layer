#!/usr/bin/env python3
"""R18. One-command *private* Preparedness draft-integrity preflight.

Runs native validation/build, >=36 unit tests, and independently maintained
source, claim, rendered, link, safety-triage and seven-cluster Git custody gates.
The only permitted generation is the existing git-ignored preparedness/build/.
A successful preflight is ALWAYS release HOLD, never independent QD/medical
verification, real-time source verification, or permission to publish.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable

SHA = re.compile(r"[0-9a-f]{40}\Z")
TEST_COUNT = re.compile(r"\bRan\s+(\d+)\s+tests?\s+in\s+\d+(?:\.\d+)?s\b")
FAIL_WORDS = re.compile(r"\b(?:FAILED|ERROR|Traceback)\b")
MANIFEST = "preparedness/docs/R14-SEVEN-CLUSTER-GIT-BLOB-PARITY.json"
# R106: keep the 12 non-test gates at their original per-step limit, while
# allowing the now >9,000-case native suite a separate, finite ceiling.
# Never skip or shorten that suite to make the receipt appear successful.
DEFAULT_STEP_TIMEOUT = 180
NATIVE_UNIT_TIMEOUT = 480
# Every entry is a fixed local executable, not configurable by a reviewer report.
STEPS = (
    ("native_validation", "validate.py", "plain"),
    ("private_draft_build", "build.py", "plain"),
    ("native_unit_suite", "<unittest>", "tests"),
    ("canonical_claim_corpus", "claim_corpus_release_gate.py", "hold"),
    ("draft_export_custody", "draft_export_custody.py", "hold"),
    ("rendered_citation_parity", "rendered_citation_gate.py", "hold"),
    ("uncited_action_triage", "high_consequence_claim_triage.py", "hold"),
    ("outbound_link_custody", "outbound_link_custody.py", "hold"),
    ("source_crosswalk_truth", "source_crosswalk_truth_gate.py", "hold"),
    ("current_safety_copy_custody", "qa_current_copy_concordance.py", "hold"),
    ("seven_cluster_git_parity", "cluster_git_parity_gate.py", "hold"),
    # R24: R23 source+81-file author custody MUST run inside the hosted preflight.
    ("frozen_81_file_archive_custody", "source_group_review_gate.py", "hold"),
    # R25: 1,959 claim occurrences / 367 article-source relationships and all
    # 43 base fallbacks become a mandatory source-review packet, still HOLD.
    ("citation_fallback_human_review_queue", "citation_fallback_review_gate.py", "hold"),
)


class PreflightHold(ValueError):
    """A required integrity proof is incomplete or failed."""


@dataclass(frozen=True)
class Step:
    name: str
    command: tuple[str, ...]
    kind: str


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise PreflightHold(reason)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def checked_root(root: Path) -> Path:
    require(not root.is_symlink() and root.is_dir(), "checkout root absent or symbolic link")
    root = root.resolve(strict=True)
    require((root / ".git").exists(), "trusted Git checkout required")
    prep = root / "preparedness"
    require(prep.is_dir() and not prep.is_symlink(), "Preparedness source directory absent or linked")
    for name, _, _ in STEPS:
        require(re.fullmatch(r"[a-z][a-z0-9_]*", name) is not None,
                "unknown gate identifier")
    for _, script, kind in STEPS:
        if kind == "tests":
            target = prep / "tests"
        else:
            target = prep / "tools" / script
        require(target.exists() and not target.is_symlink() and
                (target.is_file() if kind != "tests" else target.is_dir()),
                f"missing or linked native gate: {script}")
        require(target.resolve().is_relative_to(prep), "gate path escaped scope")
    manifest = root / MANIFEST
    require(manifest.is_file() and not manifest.is_symlink(),
            "frozen seven-cluster Git manifest missing or linked")
    out = prep / "build"
    require(not out.is_symlink(), "private draft build path is a symbolic link")
    if out.exists():
        require(out.is_dir(), "private build path must be a directory")
    return root


def commands(root: Path, expected_sha: str, python: str = sys.executable) -> tuple[Step, ...]:
    require(bool(SHA.fullmatch(expected_sha)), "exact 40-hex checkout SHA required")
    result = []
    for name, file, kind in STEPS:
        if kind == "tests":
            args = (python, "-I", "-B", "-m", "unittest", "discover",
                    "-s", "preparedness/tests", "-v")
        else:
            args = (python, "-I", "-B", "preparedness/tools/" + file)
            if name in ("source_crosswalk_truth", "current_safety_copy_custody"):
                args += ("--repo-root", str(root))
            elif name == "seven_cluster_git_parity":
                args += ("--repo-root", str(root), "--manifest", str(root / MANIFEST),
                         "--current-integrated-sha", expected_sha)
        result.append(Step(name, args, kind))
    return tuple(result)


def safe_output(data: bytes, *, max_bytes: int = 4_000_000) -> str:
    require(isinstance(data, bytes) and len(data) <= max_bytes,
            "gate output exceeds safe cap")
    try:
        return data.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise PreflightHold("gate emitted invalid UTF-8") from exc


def verify_hold_json(output: bytes) -> dict:
    text = safe_output(output, max_bytes=4_000_000).strip()
    require(bool(text), "gate emitted no JSON custody result")
    try:
        obj = json.loads(text, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, TypeError) as exc:
        raise PreflightHold("gate result is not a single valid JSON document") from exc
    require(type(obj) is dict and obj.get("release_state") == "HOLD" and
            obj.get("may_publish") is False,
            "gate returned non-HOLD state or asserted permission to publish")
    # Optional fields are not an opportunity to smuggle an approval claim.
    # If a hold-only producer emits any authority marker it MUST be literally false.
    for flag in ("qualified_safety_clearance", "human_source_reviews_complete",
                 "human_source_review_complete", "human_source_reviews_completed",
                 "external_human_qa_proven", "article_claim_accuracy_verified",
                 "independent_human_source_checks_verified",
                 "source_links_independently_verified", "source_claim_accuracy_verified",
                 "link_and_claim_accuracy_independently_verified",
                 "medical_safety_approved", "qualified_emergency_or_medical_safety_review",
                 "qualified_medical_or_emergency_safety_review",
                 "independent_qd_pass", "independent_QD_approval",
                 "wordpress_publishing_performed", "may_publish"):
        require(flag not in obj or obj[flag] is False,
                "gate falsely asserted review approval: " + flag)
    return obj


def verify_tests(out: bytes, err: bytes, minimum: int = 36) -> int:
    combined = safe_output(out, max_bytes=250_000) + "\n" + safe_output(err, max_bytes=2_000_000)
    matches = TEST_COUNT.findall(combined)
    require(len(matches) == 1, "native unittest count missing or ambiguous")
    count = int(matches[0])
    require(count >= minimum, "fewer than 36 native tests actually executed")
    require(re.search(r"(?m)^OK(?:\s*\(.*\))?\s*$", combined) is not None and
            FAIL_WORDS.search(combined) is None,
            "native test run lacks an unambiguous successful result")
    return count


def git_check(root: Path, expected_sha: str, *, run: Callable = subprocess.run) -> str:
    require(bool(SHA.fullmatch(expected_sha)), "invalid checkout SHA")
    calls = (("rev-parse", "--verify", "HEAD^{commit}"),
             ("status", "--porcelain=v1", "--untracked-files=all", "--", "preparedness"))
    outputs = []
    for args in calls:
        try:
            p = run(["git", "-C", str(root), *args], stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, timeout=15, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise PreflightHold("Git custody check unavailable") from exc
        require(p.returncode == 0, "Git HEAD/worktree inspection failed")
        outputs.append(safe_output(p.stdout, max_bytes=100_000))
    head, status = outputs
    require(head.strip() == expected_sha, "checkout HEAD drifted from exact approved SHA")
    require(not status.strip(), "dirty or untracked Preparedness source material")
    return head.strip()


def execute(root: Path, expected_sha: str, *, run: Callable = subprocess.run,
            timeout: int = DEFAULT_STEP_TIMEOUT, python: str = sys.executable,
            git_run: Callable | None = None,
            native_unit_timeout: int = NATIVE_UNIT_TIMEOUT) -> dict:
    """Do not continue after a failed gate. No CMS, network or release steps exist."""
    require(type(timeout) is int and 10 <= timeout <= 1200,
            "invalid bounded per-gate timeout")
    require(type(native_unit_timeout) is int and 10 <= native_unit_timeout <= 1200,
            "invalid bounded native-unit-suite timeout")
    root = checked_root(root)
    observed = []
    git_run = run if git_run is None else git_run
    git_check(root, expected_sha, run=git_run)
    for step in commands(root, expected_sha, python):
        # The -I/-B interpreter and fixed argv never consult untrusted shell input.
        require(step.command[0] == python and step.command[1:3] == ("-I", "-B"),
                "gate runner is not isolated")
        try:
            proc = run(list(step.command), cwd=str(root), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       timeout=(native_unit_timeout if step.kind == "tests" else timeout),
                       check=False)
        except subprocess.TimeoutExpired as exc:
            raise PreflightHold(f"{step.name}: timed out") from exc
        except OSError as exc:
            raise PreflightHold(f"{step.name}: native execution unavailable") from exc
        if type(proc.returncode) is not int or proc.returncode != 0:
            # Tracebacks from Python's private draft build can explain a CI
            # blocker but may contain private paths, article text or values.
            # Retain only an allowlisted exception class and a tool line number.
            diagnostic = ""
            if isinstance(proc.stderr, bytes) and len(proc.stderr) <= 2_000_000:
                decoded = proc.stderr.decode("utf-8", errors="replace")
                exception = re.search(r"(?m)^(KeyError|ValueError|NameError|TypeError|"
                                      r"AttributeError|FileNotFoundError|OSError|"
                                      r"IndexError|AssertionError|RuntimeError|"
                                      r"PermissionError|UnboundLocalError|TriageFailure|LinkCustodyFailure):", decoded)
                locations = re.findall(
                    r'File "[^"\r\n]*[/\\]preparedness[/\\]tools[/\\]'
                    r'(?:build|validate|claim_corpus_release_gate|high_consequence_claim_triage|outbound_link_custody)\.py", line ([0-9]{1,5})', decoded)
                if exception:
                    diagnostic = "; exception " + exception.group(1)
                if locations:
                    diagnostic += "; source line " + locations[-1]
            raise PreflightHold(f"{step.name}: exit status {proc.returncode}" + diagnostic)
        summary = {"gate": step.name, "exit_code": 0,
                   "stdout_sha256": sha256(proc.stdout),
                   "stderr_sha256": sha256(proc.stderr)}
        if step.kind == "hold":
            result = verify_hold_json(proc.stdout)
            summary["state"] = "HOLD"
            summary["receipt_sha256"] = sha256(canonical_json(result))
        elif step.kind == "tests":
            summary["native_test_count"] = verify_tests(proc.stdout, proc.stderr)
        else:
            # Native scripts must still remain silent about any release permission.
            out = safe_output(proc.stdout, max_bytes=4_000_000)
            safe_output(proc.stderr, max_bytes=2_000_000)
            require(not re.search(r"(?i)\bmay_publish\s*[=:]\s*true\b", out),
                    f"{step.name}: unsafe release assertion")
        git_check(root, expected_sha, run=git_run)
        if step.name == "private_draft_build":
            out_dir = root / "preparedness" / "build"
            require(out_dir.is_dir() and not out_dir.is_symlink(),
                    "private draft build directory missing")
        observed.append(summary)
    require(len(observed) == len(STEPS) and
            sum("native_test_count" in s for s in observed) == 1,
            "incomplete preflight gate schedule")
    result = {"schema_version": 1, "authority": "MACHINE_LOCAL_DRAFT_CUSTODY_ONLY",
              "issue": 136, "exact_checkout_sha": expected_sha,
              "release_state": "HOLD", "may_publish": False,
              "wordpress_publishing_performed": False,
              "independent_QD_approval": False,
              "source_claim_accuracy_verified": False,
              "qualified_medical_or_emergency_safety_review": False,
              "all_required_machine_gates_executed": True,
              "steps": observed}
    result["fingerprint_sha256"] = sha256(canonical_json(result))
    return result


def private_receipt(path: Path, root: Path, report: dict) -> None:
    """Optional write-once audit receipt; never outside ignored local build/."""
    root = root.resolve(strict=True)
    parent = root / "preparedness" / "build"
    require(parent.is_dir() and not parent.is_symlink(), "missing private draft output directory")
    require(path.parent == parent and not path.is_symlink() and
            path.name.startswith("R18-PREFLIGHT-") and path.suffix == ".json",
            "receipt must be a new direct R18 JSON file in private build/")
    payload = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    try:
        with path.open("x", encoding="utf-8") as f:
            f.write(payload)
    except FileExistsError as exc:
        raise PreflightHold("receipt already exists; never overwrite custody evidence") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--step-timeout", type=int, default=DEFAULT_STEP_TIMEOUT)
    parser.add_argument("--native-unit-timeout", type=int, default=NATIVE_UNIT_TIMEOUT,
                        help="bounded native unittest ceiling; all 13 gates still required")
    parser.add_argument("--receipt", type=Path,
                        help="Optional new private preparedness/build/R18-PREFLIGHT-*.json file")
    args = parser.parse_args(argv)
    try:
        report = execute(args.repo_root, args.expected_head,
                         timeout=args.step_timeout,
                         native_unit_timeout=args.native_unit_timeout)
        if args.receipt:
            private_receipt(args.receipt, args.repo_root, report)
        print(json.dumps(report, sort_keys=True))
        return 0  # Machine tests complete; release continues HOLD.
    except (PreflightHold, ValueError, OSError) as exc:
        # GitHub Actions redirects stdout to a private runner-only JSON
        # receipt. Emit just the known failing gate and a reason digest to
        # stderr so CI diagnoses failures without leaking internal source
        # details, filesystem paths, review notes, or private contents.
        detail = str(exc)
        known_gate = next((name for name, _, _ in STEPS
                           if detail.startswith(name + ":")), None)
        print(json.dumps({"gate": "R18_PRIVATE_PREFLIGHT_FAILURE",
                          "release_state": "HOLD", "may_publish": False,
                          "machine_integrity_result": "INCOMPLETE_OR_FAILED",
                          "failed_step": known_gate or "setup_or_checkout",
                          "failure_kind": ("TIMEOUT" if detail.endswith(": timed out")
                                           else "EXIT_NONZERO" if re.search(
                                               r": exit status -?[0-9]+", detail)
                                           else "CUSTODY_OR_EXECUTION"),
                          "exception_class": (
                              re.search(r"; exception ([A-Za-z]+)", detail).group(1)
                              if re.search(r"; exception ([A-Za-z]+)", detail) else None),
                          "script_line": (
                              int(re.search(r"; source line ([0-9]{1,5})", detail).group(1))
                              if re.search(r"; source line ([0-9]{1,5})", detail) else None),
                          "reason_sha256": sha256(detail.encode("utf-8"))},
                         sort_keys=True), file=sys.stderr)
        print(json.dumps({"schema_version": 1, "release_state": "HOLD",
                          "may_publish": False,
                          "machine_integrity_result": "INCOMPLETE_OR_FAILED",
                          "error": detail}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
