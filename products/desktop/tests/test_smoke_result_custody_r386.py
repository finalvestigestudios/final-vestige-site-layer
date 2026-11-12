"""R386: source-only receipt must never claim outputs not actually returned.

No customer files, executables, Windows scans, or premium licenses are used.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from scripts.smoke_result_custody_r386 import MAX_SMOKE_OUTPUTS, checked_smoke_outputs


class SmokeResultCustodyR386(unittest.TestCase):
    def rejected(self, outputs):
        with self.assertRaisesRegex(RuntimeError, "(?:unsafe|no source-smoke)"):
            checked_smoke_outputs(outputs)

    def test_single_native_path_accepted(self):
        self.assertEqual(checked_smoke_outputs([Path("ledger-diff.csv")]),
                         [Path("ledger-diff.csv")])

    def test_three_realistic_products_accepted(self):
        values = [Path("claims.csv"), Path("budget-summary.csv"), Path("manifest.txt")]
        self.assertEqual(checked_smoke_outputs(values), values)

    def test_return_is_a_snapshot_not_the_input_list(self):
        original = [Path("report.csv")]
        result = checked_smoke_outputs(original)
        original.clear()
        self.assertEqual(result, [Path("report.csv")])

    def test_empty_list_fails_closed(self):
        self.rejected([])

    def test_empty_generator_does_not_count_as_success(self):
        self.rejected((x for x in ()))

    def test_populated_generator_is_not_trusted(self):
        self.rejected((p for p in [Path("ok.csv")]))

    def test_bare_string_is_not_treated_as_many_outputs(self):
        self.rejected("report.csv")

    def test_bare_path_is_not_a_list(self):
        self.rejected(Path("report.csv"))

    def test_tuple_and_dict_not_silently_coerced(self):
        for item in ((Path("report.csv"),), {"path": Path("report.csv")}, None):
            with self.subTest(type=type(item).__name__):
                self.rejected(item)

    def test_list_subclass_is_rejected(self):
        class Forged(list):
            pass
        self.rejected(Forged([Path("report.csv")]))

    def test_path_subclass_cannot_override_filesystem_hooks(self):
        class Forged(type(Path())):
            def __str__(self):
                raise AssertionError("forged filesystem hook must not run")
        self.rejected([Forged("report.csv")])

    def test_duplicate_names_cannot_inflate_output_count(self):
        self.rejected([Path("report.csv"), Path("report.csv")])

    def test_absolute_and_traversal_paths_rejected(self):
        for path in (Path.cwd() / "secret.csv", Path("../secret.csv"), Path("a/b.csv")):
            with self.subTest(path=str(path)):
                self.rejected([path])

    def test_cross_platform_drive_and_ads_paths_rejected(self):
        for value in (r"C:\private\report.csv", r"\\server\share\report.csv",
                      "report.csv:payload", "a\\b.csv"):
            with self.subTest(value=value):
                self.rejected([Path(value)])

    def test_control_and_unicode_output_names_rejected(self):
        for value in ("bad\nname.csv", "bad\tname.csv", "private\x00name.csv",
                      "résumé.csv", "hidden name.csv"):
            with self.subTest(value=repr(value)):
                self.rejected([Path(value)])

    def test_exact_maximum_accepted(self):
        values = [Path(f"artifact-{n}.csv") for n in range(MAX_SMOKE_OUTPUTS)]
        self.assertEqual(len(checked_smoke_outputs(values)), MAX_SMOKE_OUTPUTS)

    def test_above_maximum_rejected(self):
        self.rejected([Path(f"artifact-{n}.csv") for n in range(MAX_SMOKE_OUTPUTS + 1)])

    def test_no_private_payload_in_error_or_chain(self):
        secret = r"C:\customers\payroll\private.csv"
        try:
            checked_smoke_outputs([Path(secret)])
        except RuntimeError as exc:
            self.assertNotIn("customers", str(exc))
            self.assertIsNone(exc.__context__)
            self.assertIsNone(exc.__cause__)
        else:
            self.fail("private path erroneously accepted")


if __name__ == "__main__":
    unittest.main()
