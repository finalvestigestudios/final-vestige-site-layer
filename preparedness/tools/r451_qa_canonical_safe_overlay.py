#!/usr/bin/env python3
"""R451 deterministic offline 3-way QA overlay. NEVER changes the checkout or grants QD PASS.

This tool composes an executable *review candidate* in an external scratch location.
The actual #157 safety edits outside the test file require separate human adjudication.
The output is not suitable for merge/publication without native full-tree tests.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

_PARENT = Path(__file__).resolve().with_name("r450_qa_overlap_rehearsal.py")
_spec = importlib.util.spec_from_file_location("r451_parent_r450", _PARENT)
if _spec is None or _spec.loader is None:
    raise RuntimeError("R450 independent source gate unavailable")
r450 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r450)

HOLD = "DRAFT_HARD_HOLD"
REPLACEMENTS = (
    "test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source",
    "test_register_fragments_cannot_duplicate_ids",
    "test_unverified_source_cannot_be_cited",
)
ADDITIONS = (
    ("qa157", r450.SAFETY_METHOD),
    ("repair2205", r450.RUNTIME_METHOD),
)

class OverlayError(ValueError):
    pass


def _inventory(source: bytes) -> tuple[ast.Module, dict[str, ast.FunctionDef], ast.ClassDef]:
    tree, methods, duplicates = r450.parse_methods(source)
    if duplicates:
        raise OverlayError("duplicate test identities: " + ", ".join(duplicates))
    owners = [c for c in tree.body if isinstance(c, ast.ClassDef)
              and any(isinstance(x, ast.FunctionDef) and x.name in REPLACEMENTS for x in c.body)]
    if len(owners) != 1:
        raise OverlayError("ambiguous or missing fixture owner class")
    return tree, methods, owners[0]


def _span(node: ast.FunctionDef) -> tuple[int, int]:
    first = min([node.lineno] + [n.lineno for n in node.decorator_list])
    return first - 1, node.end_lineno


def compose(variants: dict[str, bytes], *, require_pins: bool = True) -> tuple[bytes, dict[str, Any]]:
    """Produce strictly-review-only composite bytes from exact source commits."""
    assessment = r450.assess(variants, require_pins=require_pins)
    if assessment["structural_errors"]:
        raise OverlayError("R450 source gate blocked: " + "; ".join(assessment["structural_errors"]))
    target = variants["target_r449"]
    repair = variants["repair2205"]
    qa = variants["qa157"]
    _, original, owner = _inventory(target)
    _, repaired, repair_owner = _inventory(repair)
    _, safety, safety_owner = _inventory(qa)
    if owner.name != repair_owner.name or owner.name != safety_owner.name:
        raise OverlayError("test class ownership changed across source branches")
    for name in REPLACEMENTS:
        if name not in original or name not in repaired:
            raise OverlayError("required source fixture missing: " + name)
        concerns = r450.fixture_writes_outside_canonical(repaired[name]) if name in REPLACEMENTS[:2] else []
        if concerns:
            raise OverlayError("unsafe repaired fixture: " + "; ".join(concerns))
    if r450.SAFETY_METHOD not in safety or r450.RUNTIME_METHOD not in repaired:
        raise OverlayError("independent QA gate method missing")
    if r450.verify_safety_method(safety[r450.SAFETY_METHOD]):
        raise OverlayError("independent human-safety witness incomplete")
    if r450.verify_runtime_method(repaired[r450.RUNTIME_METHOD]):
        raise OverlayError("independent runtime filesystem witness incomplete")

    lines = target.decode("utf-8").splitlines(keepends=True)
    edits: list[tuple[int, int, str]] = []
    changed: list[str] = []
    for name in REPLACEMENTS:
        old = original[name]
        new = repaired[name]
        if ast.dump(old, include_attributes=False) == ast.dump(new, include_attributes=False):
            continue
        lo, hi = _span(old)
        replacement = r450.method_code(repair, name)
        edits.append((lo, hi, replacement))
        changed.append(name)
    # Insert at the very end of the original owner class, before its next top-level node.
    after = sorted(n.lineno for n in _inventory(target)[0].body if getattr(n, "lineno", 0) > owner.lineno)
    position = after[0] - 1 if after else owner.end_lineno
    added: list[str] = []
    fragments: list[str] = []
    for variant_key, name in ADDITIONS:
        if name in original:
            source = safety[name] if variant_key == "qa157" else repaired[name]
            if ast.dump(original[name], include_attributes=False) != ast.dump(source, include_attributes=False):
                raise OverlayError("existing independent gate method differs: " + name)
            continue
        fragments.append(r450.method_code(variants[variant_key], name))
        added.append(name)
    if fragments:
        edits.append((position, position, "\n" + "\n".join(fragments) + "\n"))
    # Reverse order prevents earlier offsets moving before we apply them.
    for lo, hi, value in sorted(edits, key=lambda edit: (edit[0], edit[1]), reverse=True):
        lines[lo:hi] = [value]
    candidate = "".join(lines).encode("utf-8")
    _, combined, new_owner = _inventory(candidate)
    expected = set(original) | {name for _, name in ADDITIONS}
    if set(combined) != expected:
        raise OverlayError("composite test identity lost or unexpectedly added")
    for name in set(original) - set(REPLACEMENTS) - {n for _, n in ADDITIONS}:
        if ast.dump(original[name], include_attributes=False) != ast.dump(combined[name], include_attributes=False):
            raise OverlayError("unrelated baseline assertion modified: " + name)
    for name in REPLACEMENTS:
        if ast.dump(repaired[name], include_attributes=False) != ast.dump(combined[name], include_attributes=False):
            raise OverlayError("approved repair fixture not retained: " + name)
    for variant_key, name in ADDITIONS:
        source = safety[name] if variant_key == "qa157" else repaired[name]
        if ast.dump(source, include_attributes=False) != ast.dump(combined[name], include_attributes=False):
            raise OverlayError("independent QA guard altered: " + name)
    for name in REPLACEMENTS[:2]:
        if r450.fixture_writes_outside_canonical(combined[name]):
            raise OverlayError("canonical fixture mutation witness failed: " + name)
    # Verify all candidate tests remain within the original owner, not in a stray class.
    owner_methods = {x.name for x in new_owner.body if isinstance(x, ast.FunctionDef)}
    if not expected.issubset(owner_methods | {x.name for c in _inventory(candidate)[0].body
                                        if isinstance(c, ast.ClassDef) for x in c.body
                                        if isinstance(x, ast.FunctionDef)}):
        raise OverlayError("owner class structure changed unexpectedly")
    receipt = {
        "schema": "R451_OFFLINE_QA_COMPOSITE_v1",
        "release_state": HOLD, "publishable": False, "merged": False,
        "qd_pass": False, "native_suite_pass": False, "test_run_claim": "NOT_EXECUTED",
        "original_test_count": len(original), "candidate_test_count": len(combined),
        "fixture_method_replacements": changed, "independent_gate_additions": added,
        "source_git_blobs": assessment["source_pins"],
        "composite_sha256": hashlib.sha256(candidate).hexdigest(),
        "unadjudicated_same_name_drift": assessment["changed_same_name_tests"],
        "qa157_other_4_files_unmerged": assessment["qa157_non_test_files_require_separate_editorial_adjudication"],
        "pending_qualified_review": ["original_35_manuscripts", "5_source_disputes", "9_forks", "17_shared_URL_groups", "emergency_medical_food_privacy"],
        "paid_offer_verified": False, "attributed_revenue_verified": False,
    }
    return candidate, receipt


def export_review_only(variants: dict[str, bytes], destination: Path, checkout_root: Path,
                       *, require_pins: bool = True) -> dict[str, Any]:
    candidate, receipt = compose(variants, require_pins=require_pins)
    root = checkout_root.resolve()
    dest = destination.resolve()
    if dest == root or root in dest.parents:
        raise OverlayError("review candidate may not be written inside canonical checkout")
    if dest.exists():
        raise OverlayError("review candidate destination already exists")
    if dest.suffix != ".txt":
        raise OverlayError("review candidate must be non-executable .txt")
    # exclusive create: no concurrency overwrite; bytes are built and verified first.
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("xb") as f:
        f.write(b"# REVIEW CANDIDATE ONLY; NOT QA APPROVED; DO NOT EXECUTE AS RELEASE PROOF\n")
        f.write(candidate)
    receipt["review_candidate_path"] = str(dest)
    receipt["review_candidate_written"] = True
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in r450.SOURCE_PINS:
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    parser.add_argument("--checkout-root", type=Path, required=True)
    parser.add_argument("--review-output", type=Path)
    args = parser.parse_args(argv)
    try:
        inputs = {n: getattr(args, n).read_bytes() for n in r450.SOURCE_PINS}
        receipt = (export_review_only(inputs, args.review_output, args.checkout_root)
                   if args.review_output else compose(inputs)[1])
    except (OSError, ValueError) as err:
        print(json.dumps({"release_state": HOLD, "publishable": False, "error": str(err)}))
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
