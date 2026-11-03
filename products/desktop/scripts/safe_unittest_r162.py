"""Strict no-skip, no-leak R162 suite runner; 21 fixed synthetic tests."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset(("test_six_exact_refs_accepted",
    "test_pinned_actions_not_mutable_names",
    "test_all_six_calls_are_required",
    "test_duplicate_upload_is_denied",
    "test_unknown_action_is_denied",
    "test_mutable_checkout_major_tag_denied",
    "test_mutable_python_major_tag_denied",
    "test_mutable_upload_major_tag_denied",
    "test_mutable_main_branch_denied",
    "test_action_ref_sha_substitution_denied",
    "test_expression_action_ref_denied",
    "test_multiple_at_symbols_denied",
    "test_missing_at_symbol_denied",
    "test_comment_does_not_satisfy_missing_action",
    "test_legitimate_comment_is_ignored",
    "test_any_additional_action_denied",
    "test_oversized_workflow_denied",
    "test_nul_or_tabs_denied",
    "test_cli_privacy_hold",
    "test_cli_success",
    "test_actual_workflow_all_refs_pinned"))


def _cases(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from _cases(test)
        else:
            yield test


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_ci_action_pins_r162.py")
        cases = list(_cases(suite))
        labels = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(labels) != EXPECTED
                or len(set(labels)) != len(EXPECTED)
                or any(type(case).__name__ != "ActionPinR162" for case in cases)):
            raise ValueError("R162 action test inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({case._testMethodName for case, _ in
                         (*result.errors, *result.failures)})
        print(f"R162 immutable CI actions {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors) + len(result.failures) + len(result.skipped)}; "
              f"failed_methods={','.join(failed)}")
        return 0 if okay else 1
    except Exception:
        print("R162 immutable CI actions HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
