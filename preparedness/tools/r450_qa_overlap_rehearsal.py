#!/usr/bin/env python3
"""R450 read-only three-way QA reconciliation; NEVER grants a release or QD PASS.

Inputs must be authenticated copies of the exact GitHub versions of
preparedness/tests/test_preparedness.py. The only optional output is a
non-executable, *outside-checkout* rehearsal copy with both independent tests.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any

HOLD = "DRAFT_HARD_HOLD"
TEST_REL = Path("preparedness/tests/test_preparedness.py")
SOURCE_PINS = {
    "qa157": "32627489b7727d97ac54663d87ac8d112911c811",
    "fixture169": "e80d622c2fd32bf6c9752e375c1208c1d47d8e7c",
    "repair2205": "b63e7f4dc9c84a4bef15dd581affe08ac81356af",
    "target_r449": "c329f98e051d2aabe31a3343869b0fdac355b315",
}
SOURCE_COMMITS = {
    "qa157": "7d1ae6b8ef93d10cfb6810987672360885e9c1aa",
    "fixture169": "e9cd7766dac59d47ab467d8945269b9146c2aef5",
    "repair2205": "bbcf1859768624c611df4abadc564c18247cf32a",
    "target_r449": "2044fcd03ec6d7d34d07dd86833121dd3ab7fdef",
}
SAFETY_METHOD = "test_start_articles_require_human_safety_review_before_publishing"
RUNTIME_METHOD = "test_fixture_tests_never_write_or_unlink_in_canonical_checkout"
FIXTURE_METHODS = (
    "test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source",
    "test_register_fragments_cannot_duplicate_ids",
    "test_unverified_source_cannot_be_cited",
)
SAFETY_SLUGS = (
    "household-emergency-plan", "three-day-kit", "go-bags",
    "preparedness-real-households",
)
OTHER_QA157_FILES = (
    "preparedness/content/articles/household-emergency-plan.body.html",
    "preparedness/content/articles/three-day-kit.body.html",
    "preparedness/sources/fragments/start.json",
    "preparedness/taxonomy.json",
)


class GateError(ValueError):
    """Input invalid or unsafe for a reproducible reconciliation rehearsal."""


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def parse_methods(data: bytes) -> tuple[ast.Module, dict[str, ast.FunctionDef], list[str]]:
    try:
        source = data.decode("utf-8")
        tree = ast.parse(source)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise GateError("invalid Python source: " + str(exc)) from exc
    methods: dict[str, ast.FunctionDef] = {}
    duplicates: list[str] = []
    for cls in (x for x in tree.body if isinstance(x, ast.ClassDef)):
        for node in cls.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                if not isinstance(node, ast.FunctionDef):
                    raise GateError("async test function not supported: " + node.name)
                if node.name in methods:
                    duplicates.append(node.name)
                methods[node.name] = node
    return tree, methods, duplicates


def method_code(data: bytes, name: str) -> str:
    _, methods, duplicates = parse_methods(data)
    if duplicates:
        raise GateError("duplicate test methods: " + ",".join(duplicates))
    if name not in methods:
        raise GateError("missing required source test: " + name)
    node = methods[name]
    lines = data.decode("utf-8").splitlines(keepends=True)
    start = min([node.lineno] + [d.lineno for d in node.decorator_list]) - 1
    return "".join(lines[start:node.end_lineno]).rstrip("\n") + "\n"


def tokens(node: ast.AST) -> set[str]:
    return {n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def calls(node: ast.AST) -> set[str]:
    found: set[str] = set()
    for n in ast.walk(node):
        if not isinstance(n, ast.Call):
            continue
        try:
            found.add(ast.unparse(n.func))
        except (ValueError, AttributeError):
            pass
    return found


def verify_safety_method(node: ast.FunctionDef) -> list[str]:
    """Structural witness; qualified human review is separately required."""
    problems: list[str] = []
    src = ast.unparse(node)
    for slug in SAFETY_SLUGS:
        if slug not in tokens(node):
            problems.append("missing protected slug: " + slug)
    if "CANNOT be published without an approved human safety review" not in tokens(node):
        problems.append("missing exact pending-human-safety rejection witness")
    if "validate.validate" not in calls(node):
        problems.append("human safety test never invokes validator")
    if "self.assertTrue" not in calls(node):
        problems.append("human safety test never asserts rejection")
    if not any(isinstance(n, ast.Try) and n.finalbody for n in ast.walk(node)):
        problems.append("human safety test lacks finally restoration")
    if '"published"' not in src and "'published'" not in src:
        problems.append("human safety test does not simulate publishing")
    return problems


def verify_runtime_method(node: ast.FunctionDef) -> list[str]:
    problems: list[str] = []
    src = ast.unparse(node)
    for needle in ("Path.write_text", "Path.unlink", "canonical_root", "self.test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source", "self.test_register_fragments_cannot_duplicate_ids"):
        if needle not in src:
            problems.append("runtime fixture guard missing: " + needle)
    if "patch.object" not in calls(node):
        problems.append("runtime fixture guard does not patch filesystem writes")
    if "self.fail" not in calls(node):
        problems.append("runtime fixture guard does not fail canonical writes")
    return problems


def fixture_writes_outside_canonical(node: ast.FunctionDef) -> list[str]:
    """Conservative static anti-mutation gate for source fixture tests."""
    src = ast.unparse(node)
    problems: list[str] = []
    if "TemporaryDirectory" not in src or "copytree" not in src:
        problems.append("fixture lacks isolated copy under TemporaryDirectory")
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if n.func.attr in ("write_text", "unlink", "write_bytes", "rmdir"):
                recv = ast.unparse(n.func.value)
                if recv.startswith("ROOT") or "ROOT /" in recv:
                    problems.append("canonical source mutation: " + recv)
    return problems


def assess(variants: dict[str, bytes], *, require_pins: bool = True) -> dict[str, Any]:
    """Never claims a merge/safety pass; reports source preservation readiness only."""
    required = set(SOURCE_PINS)
    if set(variants) != required:
        raise GateError("exactly qa157, fixture169, repair2205, target_r449 required")
    parsed: dict[str, dict[str, ast.FunctionDef]] = {}
    pins: dict[str, Any] = {}
    for name in SOURCE_PINS:
        data = variants[name]
        if not isinstance(data, bytes):
            raise GateError("variant contents must be bytes: " + name)
        sha = git_blob(data)
        pins[name] = {"commit": SOURCE_COMMITS[name], "blob": sha, "expected_blob": SOURCE_PINS[name], "matched": sha == SOURCE_PINS[name]}
        if require_pins and sha != SOURCE_PINS[name]:
            raise GateError("unaligned authenticated Git blob for " + name + ": " + sha)
        _, methods, dupes = parse_methods(data)
        if dupes:
            raise GateError("duplicate test-method identity in " + name + ": " + ",".join(dupes))
        if len(methods) < 25:
            raise GateError("test inventory truncated in " + name)
        parsed[name] = methods
    base = parsed["target_r449"]
    qa = parsed["qa157"]
    fix = parsed["fixture169"]
    repair = parsed["repair2205"]
    issues: list[str] = []
    for name in FIXTURE_METHODS:
        if name not in base:
            issues.append("R449 baseline missing fixture test " + name)
        if name not in fix:
            issues.append("#169 missing fixture test " + name)
        if name not in repair:
            issues.append("#2205 missing fixture test " + name)
    if SAFETY_METHOD not in qa:
        issues.append("#157 missing original human safety test")
    else:
        issues.extend(verify_safety_method(qa[SAFETY_METHOD]))
    if RUNTIME_METHOD not in repair:
        issues.append("#2205 missing original runtime no-canonical-write guard")
    else:
        issues.extend(verify_runtime_method(repair[RUNTIME_METHOD]))
    for name in FIXTURE_METHODS[:2]:
        if name in base:
            issues.extend("R449 " + name + ": " + x for x in fixture_writes_outside_canonical(base[name]))
    for name in set(base) - set(fix) - {SAFETY_METHOD, RUNTIME_METHOD}:
        issues.append("R449 test not represented in fixture parent: " + name)
    lost_from_qa = sorted(set(qa) - set(base))
    lost_from_repair = sorted(set(repair) - set(base))
    already_present = sorted(set(base) & {SAFETY_METHOD, RUNTIME_METHOD})
    common_drift: dict[str, list[str]] = {}
    for name, left, right in (("qa157_vs_target", qa, base), ("repair2205_vs_target", repair, base)):
        drifts = [n for n in left.keys() & right.keys() if ast.dump(left[n], include_attributes=False) != ast.dump(right[n], include_attributes=False)]
        common_drift[name] = sorted(drifts)
    return {
        "schema": "R450_QA_REHEARSAL_v1", "release_state": HOLD,
        "publishable": False, "qd_approved": False, "merge_approved": False,
        "source_pins": pins,
        "test_counts": {k: len(v) for k, v in parsed.items()},
        "qa157_unrepresented_tests": lost_from_qa,
        "repair2205_unrepresented_tests": lost_from_repair,
        "already_present": already_present,
        "changed_same_name_tests": common_drift,
        "qa157_non_test_files_require_separate_editorial_adjudication": list(OTHER_QA157_FILES),
        "structural_errors": issues,
        "rehearsal_possible": not issues,
        "qualified_safety_or_live_build_evidence": "NOT_ESTABLISHED",
        "authentic_35_article_build": "NOT_EXECUTED",
    }


def rehearse(variants: dict[str, bytes], destination: Path, checkout_root: Path, *, require_pins: bool = True) -> dict[str, Any]:
    """Creates only an offline candidate outside checkout; it is NOT a merge."""
    audit = assess(variants, require_pins=require_pins)
    if audit["structural_errors"]:
        raise GateError("unsafe candidate: " + "; ".join(audit["structural_errors"]))
    checkout = checkout_root.resolve()
    target = destination.resolve()
    if target == checkout or checkout in target.parents:
        raise GateError("candidate output must be outside the canonical checkout")
    if target.exists():
        raise GateError("rehearsal output already exists; no overwrite allowed")
    base = variants["target_r449"].decode("utf-8")
    _, methods, _ = parse_methods(variants["target_r449"])
    additions = []
    for source_key, name in (("qa157", SAFETY_METHOD), ("repair2205", RUNTIME_METHOD)):
        if name not in methods:
            additions.append(method_code(variants[source_key], name))
    tree, _, _ = parse_methods(variants["target_r449"])
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    owner = next((c for c in classes if any(isinstance(m, ast.FunctionDef) and m.name in FIXTURE_METHODS for m in c.body)), None)
    if owner is None:
        raise GateError("could not find canonical test owner class")
    following = [n.lineno for n in tree.body if getattr(n, "lineno", 0) > owner.lineno]
    insertion_index = min(following) - 1 if following else owner.end_lineno
    lines = base.splitlines(keepends=True)
    candidate = "".join(lines[:insertion_index]) + "\n" + "\n".join(additions) + "\n" + "".join(lines[insertion_index:])
    _, combined, duplicates = parse_methods(candidate.encode("utf-8"))
    if duplicates:
        raise GateError("candidate introduces duplicate test names: " + ",".join(duplicates))
    for name, node in methods.items():
        if name not in combined or ast.dump(node, include_attributes=False) != ast.dump(combined[name], include_attributes=False):
            raise GateError("candidate dropped or changed existing test: " + name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(candidate, encoding="utf-8")
    audit["candidate_path"] = str(target)
    audit["candidate_sha256"] = hashlib.sha256(candidate.encode()).hexdigest()
    audit["candidate_tests"] = len(combined)
    audit["candidate_is_release_approved"] = False
    return audit


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    for name in SOURCE_PINS:
        ap.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    ap.add_argument("--checkout-root", type=Path, required=True)
    ap.add_argument("--candidate-output", type=Path)
    args = ap.parse_args(argv)
    inputs = {n: getattr(args, n).read_bytes() for n in SOURCE_PINS}
    try:
        if args.candidate_output:
            receipt = rehearse(inputs, args.candidate_output, args.checkout_root)
        else:
            receipt = assess(inputs)
    except (GateError, OSError) as exc:
        print(json.dumps({"release_state": HOLD, "error": str(exc), "publishable": False}, sort_keys=True))
        return 2
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0 if receipt["rehearsal_possible"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
