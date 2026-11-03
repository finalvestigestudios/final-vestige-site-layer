"""Strict R163 no-skip/no-leak test inventory for immutable Node24 action upgrades."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_expected_upstream_node24_commit_inventory",
    "test_node24_pins_are_exact_git_ids",
    "test_all_six_action_references_required",
    "test_reject_old_checkout_commit",
    "test_reject_old_python_commit",
    "test_reject_old_uploader_commit",
    "test_reject_mutable_major_tags",
    "test_reject_main_branch_ref",
    "test_reject_unknown_action",
    "test_reject_extra_known_action",
    "test_reject_missing_action",
    "test_reject_digest_substitution",
    "test_r41_policy_accepts_new_uploader",
    "test_r41_policy_denies_premium_path",
    "test_r41_policy_denies_hidden_export_option",
    "test_r57_mandatory_source_gate_accepts_new_actions",
    "test_real_workflow_has_exact_six_pins",
    "test_real_workflow_has_no_old_refs",
    "test_real_workflow_requires_normal_and_optimized_r163",
    "test_operating_manual_has_release_hold",
    "test_cli_sanitizes_missing_source_path",
    "test_cli_success_synthetic",
))


def _cases(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from _cases(test)
        else:
            yield test


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_node24_actions_r163.py")
        cases = list(_cases(suite))
        names = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(names) != EXPECTED
                or len(set(names)) != len(EXPECTED)
                or any(type(case).__name__ != "Node24R163" for case in cases)):
            raise ValueError("R163 immutable Node24 test inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({case._testMethodName for case, _ in
                         (*result.errors, *result.failures)})
        print(f"R163 Node24 action upgrade {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors) + len(result.failures) + len(result.skipped)}; "
              f"failed_methods={','.join(failed)}")
        return 0 if okay else 1
    except Exception:
        print("R163 Node24 action upgrade HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
