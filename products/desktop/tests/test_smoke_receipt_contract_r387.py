"""R387 fail-closed source smoke report multiplicity and privacy regressions.

All evidence here is synthetic and source-only; no executable is released.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from scripts.smoke_receipt_contract_r387 import (
    EXPECTED_REPORT_COUNTS, checked_app_smoke_receipt,
)


class SourceSmokeReceiptContractR387(unittest.TestCase):
    def reject(self, app, outputs, expected=""):
        with self.assertRaisesRegex(RuntimeError, expected or "smoke|report"):
            checked_app_smoke_receipt(app, outputs)

    def test_exact_six_engines(self):
        self.assertEqual(tuple(EXPECTED_REPORT_COUNTS),
                         ("ledger", "invoices", "spend", "policy", "grants", "procurement"))

    def test_four_free_and_two_premium(self):
        self.assertEqual([EXPECTED_REPORT_COUNTS[x] for x in
                          ("ledger", "invoices", "spend", "policy", "grants", "procurement")],
                         [1, 1, 1, 1, 3, 2])

    def test_every_exact_report_count_is_accepted(self):
        for app, count in EXPECTED_REPORT_COUNTS.items():
            with self.subTest(app=app):
                values = [Path(f"report-{i}.csv") for i in range(count)]
                self.assertEqual(checked_app_smoke_receipt(app, values), values)

    def test_every_engine_rejects_empty_result(self):
        for app in EXPECTED_REPORT_COUNTS:
            with self.subTest(app=app):
                self.reject(app, [])

    def test_grants_missing_budget_report_is_not_a_pass(self):
        self.reject("grants", [Path("exceptions.csv"), Path("manifest.txt")], "Incomplete")

    def test_grants_missing_provenance_manifest_is_not_a_pass(self):
        self.reject("grants", [Path("exceptions.csv"), Path("budget.csv")], "Incomplete")

    def test_procurement_missing_second_report_is_not_a_pass(self):
        self.reject("procurement", [Path("three-way.csv")], "Incomplete")

    def test_extra_report_on_each_single_report_engine_is_rejected(self):
        for app in ("ledger", "invoices", "spend", "policy"):
            with self.subTest(app=app):
                self.reject(app, [Path("a.csv"), Path("b.csv")], "Incomplete")

    def test_extra_report_on_premium_engines_is_rejected(self):
        self.reject("grants", [Path(f"a{i}.csv") for i in range(4)], "Incomplete")
        self.reject("procurement", [Path(f"a{i}.csv") for i in range(3)], "Incomplete")

    def test_unknown_engine_rejected_before_output_iteration(self):
        class ExplodingIterable:
            def __iter__(self):
                raise AssertionError("must not consume output")
        self.reject("unknown", ExplodingIterable(), "Unknown")

    def test_app_subclass_not_trusted(self):
        class ForgedStr(str):
            pass
        self.reject(ForgedStr("grants"), [Path("ok.csv")], "Unknown")

    def test_non_string_engines_rejected(self):
        for app in (None, 1, (), b"grants"):
            with self.subTest(app=repr(app)):
                self.reject(app, [Path("ok.csv")], "Unknown")

    def test_gen_and_empty_gen_rejected_for_every_app(self):
        for app in EXPECTED_REPORT_COUNTS:
            with self.subTest(app=app):
                self.reject(app, (Path("ok.csv") for _ in range(1)))
                self.reject(app, (p for p in ()))

    def test_string_and_tuple_cannot_forge_counts(self):
        self.reject("ledger", "ok.csv")
        self.reject("procurement", (Path("a.csv"), Path("b.csv")))

    def test_duplicate_grants_reports_fail_even_with_three(self):
        self.reject("grants", [Path("a.csv"), Path("a.csv"), Path("b.csv")])

    def test_duplicate_procurement_reports_fail_even_with_two(self):
        self.reject("procurement", [Path("a.csv"), Path("a.csv")])

    def test_windows_path_and_ads_rejected(self):
        for path in (r"C:\customers\private.csv", "report.csv:secret", "sub\\report.csv"):
            with self.subTest(path=path):
                self.reject("ledger", [Path(path)])

    def test_traversal_and_absolute_paths_rejected(self):
        for p in (Path("../secret.csv"), Path.cwd() / "secret.csv"):
            with self.subTest(path=str(p)):
                self.reject("ledger", [p])

    def test_path_subclass_is_rejected_without_calling_hooks(self):
        class ForgedPath(type(Path())):
            def __str__(self):
                raise AssertionError("forged hook ran")
        self.reject("ledger", [ForgedPath("report.csv")])

    def test_receipt_returns_snapshot_not_mutable_input(self):
        origin = [Path("x.csv"), Path("y.csv")]
        snapshot = checked_app_smoke_receipt("procurement", origin)
        origin.clear()
        self.assertEqual(snapshot, [Path("x.csv"), Path("y.csv")])

    def test_private_malformed_path_never_in_exception_chain(self):
        secret = "CUSTOMER-999-PRIVATE-PAYROLL"
        try:
            checked_app_smoke_receipt("grants", [Path(secret + ".csv")])
        except RuntimeError as exc:
            self.assertNotIn(secret, str(exc))
            self.assertIsNone(exc.__cause__)
            self.assertIsNone(exc.__context__)
        else:
            self.fail("missing two grant reports was accepted")


if __name__ == "__main__":
    unittest.main()
