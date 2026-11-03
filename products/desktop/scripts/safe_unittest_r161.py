"""R161 strict 26-method zero-skip and private-output gate."""
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_native_single_bucket",
    "test_native_multi_vendor_month_sort",
    "test_native_quoted_comma_category",
    "test_native_formula_category",
    "test_native_invisible_prefix_category",
    "test_native_unicode_values",
    "test_native_credit_offsets",
    "test_native_multiline_source",
    "test_streaming_canonical_digest_matches_report",
    "test_streaming_digest_rejects_wrong_length",
    "test_trailing_blank_record_rejected",
    "test_multiple_trailing_blank_records_rejected",
    "test_blank_record_after_header_rejected",
    "test_blank_record_between_data_rejected",
    "test_all_lf_records_rejected",
    "test_all_cr_records_rejected",
    "test_mixed_first_lf_record_rejected",
    "test_mixed_last_lf_record_rejected",
    "test_missing_final_crlf_rejected",
    "test_missing_bom_rejected",
    "test_duplicate_bom_rejected",
    "test_quote_all_fields_rejected",
    "test_extra_quote_around_first_header_rejected",
    "test_extra_quote_around_vendor_cell_rejected",
    "test_cli_error_redacts_source_content",
    "test_rejected_report_never_edits_source",
))

def _cases(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from _cases(test)
        else:
            yield test

def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_spend_canonical_bytes_r161.py")
        cases = list(_cases(suite))
        labels = [test._testMethodName for test in cases]
        if (len(cases) != len(EXPECTED) or set(labels) != EXPECTED
                or len(set(labels)) != len(EXPECTED)
                or any(type(test).__name__ != "SpendNativeBytesR161"
                       for test in cases)):
            raise ValueError("R161 fixed test inventory mismatch")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        good = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({case._testMethodName for case, _ in
                         (*result.errors, *result.failures)})
        print(f"R161 native SpendMap byte custody {'PASS' if good else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors)+len(result.failures)+len(result.skipped)}; "
              f"failed_methods={','.join(failed)}")
        return 0 if good else 1
    except Exception:
        print("R161 native SpendMap byte custody HOLD: fixed test gate unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
