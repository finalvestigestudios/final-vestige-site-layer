"""R389 independent six-product synthetic report ROLE verification.

Only fixture paths, no private customer data, no executable/publication claims.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from fvs_suite.smoke_output_roles_r389 import SMOKE_REPORT_ROLES, verify_smoke_output_roles

STAMP = "20261112-155302-123456"


def reports(app: str) -> list[Path]:
    return [Path(f"{stem}-{STAMP}{ext}")
            for stem, ext in SMOKE_REPORT_ROLES[app]]


class SmokeOutputRolesR389(unittest.TestCase):
    def reject(self, app, values, message="report"):
        with self.assertRaisesRegex(RuntimeError, message) as caught:
            verify_smoke_output_roles(app, values)
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn("PRIVATE", str(caught.exception))

    def test_exact_six_product_inventory(self):
        self.assertEqual(tuple(SMOKE_REPORT_ROLES),
                         ("ledger", "invoices", "spend", "policy", "grants", "procurement"))

    def test_expected_four_free_and_two_premium_role_multiplicities(self):
        self.assertEqual([len(roles) for roles in SMOKE_REPORT_ROLES.values()],
                         [1, 1, 1, 1, 3, 2])

    def test_all_six_genuine_report_roles_pass(self):
        for app in SMOKE_REPORT_ROLES:
            with self.subTest(app=app):
                self.assertIsNone(verify_smoke_output_roles(app, reports(app)))

    def test_all_six_accept_full_native_path_references(self):
        for app in SMOKE_REPORT_ROLES:
            with self.subTest(app=app):
                self.assertIsNone(verify_smoke_output_roles(
                    app, [Path("temporary") / p for p in reports(app)]))

    def test_empty_is_not_a_valid_report(self):
        for app in SMOKE_REPORT_ROLES:
            self.reject(app, [], "Incomplete")

    def test_missing_grants_manifest_is_rejected(self):
        self.reject("grants", reports("grants")[:2], "Incomplete")

    def test_missing_procurement_manifest_is_rejected(self):
        self.reject("procurement", reports("procurement")[:1], "Incomplete")

    def test_all_three_csv_grants_false_positive_is_rejected(self):
        forged = reports("grants")[:2] + [Path(f"grant-summary-{STAMP}.csv")]
        self.reject("grants", forged, "Unexpected")

    def test_all_two_csv_procurement_false_positive_is_rejected(self):
        forged = reports("procurement")[:1] + [Path(f"other-report-{STAMP}.csv")]
        self.reject("procurement", forged, "Unexpected")

    def test_grant_report_order_matters(self):
        original = reports("grants")
        self.reject("grants", [original[1], original[0], original[2]], "Unexpected")

    def test_procurement_manifest_order_matters(self):
        original = reports("procurement")
        self.reject("procurement", original[::-1], "Unexpected")

    def test_grants_manifest_cannot_forge_exception_role(self):
        original = reports("grants")
        self.reject("grants", [original[2], original[1], original[0]], "Unexpected")

    def test_ledger_cannot_accept_invoice_report(self):
        self.reject("ledger", reports("invoices"), "Unexpected")

    def test_invoice_cannot_accept_ledger_report(self):
        self.reject("invoices", reports("ledger"), "Unexpected")

    def test_spend_cannot_accept_policy_report(self):
        self.reject("spend", reports("policy"), "Unexpected")

    def test_policy_must_have_text_extension(self):
        self.reject("policy", [Path(f"policy-delta-{STAMP}.csv")], "Unexpected")

    def test_free_app_cannot_accept_extra_report(self):
        self.reject("ledger", reports("ledger") * 2, "Incomplete")

    def test_wrong_extension_rejected_for_every_app(self):
        for app in SMOKE_REPORT_ROLES:
            with self.subTest(app=app):
                original = reports(app)
                invalid = original.copy()
                invalid[0] = invalid[0].with_suffix(".exe")
                self.reject(app, invalid, "Unexpected")

    def test_truncated_timestamp_rejected(self):
        self.reject("ledger", [Path("ledger-diff-20261112-155302.csv")], "Unexpected")

    def test_nonnumeric_timestamp_rejected(self):
        self.reject("ledger", [Path("ledger-diff-CLIENT_PRIVATE.csv")], "Unexpected")

    def test_unexpected_case_rejected(self):
        self.reject("ledger", [Path(f"Ledger-Diff-{STAMP}.csv")], "Unexpected")

    def test_suffix_noise_rejected(self):
        self.reject("ledger", [Path(f"ledger-diff-{STAMP}.csv.bak")], "Unexpected")

    def test_extra_prefix_noise_rejected(self):
        self.reject("ledger", [Path(f"old-ledger-diff-{STAMP}.csv")], "Unexpected")

    def test_untrusted_iterable_not_consumed(self):
        class Poison:
            def __iter__(self):
                raise AssertionError("cannot call iterable hooks")
            def __len__(self):
                raise AssertionError("cannot call length hooks")
        self.reject("ledger", Poison(), "Incomplete")

    def test_untrusted_path_subclass_not_consumed(self):
        class PoisonPath(type(Path())):
            @property
            def name(self):
                raise AssertionError("cannot call forged path.name")
        self.reject("ledger", [PoisonPath("ledger-diff.csv")], "Unsafe")

    def test_non_path_string_not_coerced(self):
        self.reject("ledger", ["ledger-diff-" + STAMP + ".csv"], "Unsafe")

    def test_app_identifier_subclass_not_trusted(self):
        class Spoof(str):
            def __hash__(self):
                raise AssertionError("cannot hash untrusted product name")
        self.reject(Spoof("grants"), reports("grants"), "Unknown")

    def test_unknown_app_rejected_before_outputs(self):
        for app in (None, 42, "premium", "grant", "PRIVATE"):
            self.reject(app, object(), "Unknown")

    def test_mutated_reference_not_retained(self):
        original = reports("procurement")
        self.assertIsNone(verify_smoke_output_roles("procurement", original))
        original[-1] = Path("PRIVATE-sensitive.txt")
        self.reject("procurement", original, "Unexpected")


if __name__ == "__main__":
    unittest.main()
