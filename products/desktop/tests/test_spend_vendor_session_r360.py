"""R360 SpendMap per-report vendor key stability; synthetic labels only."""
from __future__ import annotations

import unittest

from fvs_suite.spend_vendor_session_r360 import SpendVendorSession


class SpendVendorSessionR360(unittest.TestCase):
    def test_first_identity_is_accepted(self):
        SpendVendorSession().attest("ACME", "ACME", "2")

    def test_same_original_same_key_is_accepted(self):
        guard = SpendVendorSession()
        guard.attest("ACME", "ACME", "2")
        guard.attest("ACME", "ACME", "5")

    def test_same_original_changed_key_is_rejected(self):
        guard = SpendVendorSession()
        guard.attest("ACME", "ACME", "2")
        with self.assertRaisesRegex(ValueError, "physical row 7"):
            guard.attest("ACME", "OTHER", "7")

    def test_separated_repetition_is_checked(self):
        guard = SpendVendorSession()
        guard.attest("ACME", "ACME", "2")
        guard.attest("BETA", "BETA", "3")
        with self.assertRaisesRegex(ValueError, "physical row 4"):
            guard.attest("ACME", "BETA", "4")

    def test_ascii_case_only_source_is_same_identity(self):
        guard = SpendVendorSession()
        guard.attest("AcMe", "ACME", "2")
        with self.assertRaises(ValueError):
            guard.attest("aCmE", "OTHER", "3")

    def test_ascii_boundary_space_is_same_identity(self):
        guard = SpendVendorSession()
        guard.attest(" ACME ", "ACME", "2")
        with self.assertRaises(ValueError):
            guard.attest("\tacme\r", "OTHER", "3")

    def test_ascii_case_and_boundary_space_stable_mapping_passes(self):
        guard = SpendVendorSession()
        guard.attest(" ACME", "ACME", "2")
        guard.attest("acme  ", "ACME", "4")

    def test_unicode_nbsp_must_remain_significant(self):
        guard = SpendVendorSession()
        guard.attest("ACME", "ACME", "2")
        guard.attest("\u00a0ACME", "OTHER", "3")

    def test_figure_space_must_remain_significant(self):
        guard = SpendVendorSession()
        guard.attest("ACME", "ACME", "2")
        guard.attest("\u2007ACME", "OTHER", "3")

    def test_unicode_case_is_not_folded(self):
        guard = SpendVendorSession()
        guard.attest("K", "K", "2")
        guard.attest("\u212a", "KELVIN", "3")

    def test_distinct_vendors_may_share_lossy_key(self):
        guard = SpendVendorSession()
        guard.attest("ACME, INC", "ACMEINC", "2")
        guard.attest("ACME INC", "ACMEINC", "3")

    def test_session_is_scoped_per_report(self):
        SpendVendorSession().attest("ACME", "A", "2")
        SpendVendorSession().attest("ACME", "B", "2")

    def test_avoids_source_text_in_error(self):
        sensitive = "PRIVATE-TAX-ID-123456"
        guard = SpendVendorSession()
        guard.attest(sensitive, "KEY", "2")
        with self.assertRaises(ValueError) as caught:
            guard.attest(sensitive, "ALTERED", "3")
        self.assertNotIn(sensitive, str(caught.exception))
        self.assertNotIn("ALTERED", str(caught.exception))

    def test_native_string_subclass_not_invoked(self):
        class HostileStr(str):
            def strip(self, *args):
                raise AssertionError("subclass code executed")
        with self.assertRaises(ValueError):
            SpendVendorSession().attest(HostileStr("ACME"), "KEY", "2")

    def test_key_subclass_not_invoked(self):
        class HostileStr(str):
            def __eq__(self, other):
                raise AssertionError("subclass key comparison executed")
        with self.assertRaises(ValueError):
            SpendVendorSession().attest("ACME", HostileStr("KEY"), "2")

    def test_nontext_original_is_rejected(self):
        with self.assertRaises(ValueError):
            SpendVendorSession().attest(None, "KEY", "2")

    def test_invalid_row_is_not_echoed(self):
        with self.assertRaises(ValueError) as caught:
            SpendVendorSession().attest("ACME", "KEY", "=HYPERLINK(\"secret\")")
        self.assertNotIn("HYPERLINK", str(caught.exception))

    def test_leading_zero_row_is_rejected(self):
        with self.assertRaises(ValueError):
            SpendVendorSession().attest("ACME", "KEY", "002")

    def test_large_row_number_within_limit(self):
        SpendVendorSession().attest("ACME", "KEY", "9999999999")

    def test_non_ascii_source_unchanged(self):
        guard = SpendVendorSession()
        guard.attest("\u00df-Markt", "A", "2")
        guard.attest("ss-Markt", "B", "3")


if __name__ == "__main__":
    unittest.main()
