"""R312 product-bound local evidence restore, pure core guard regressions."""
from __future__ import annotations

import unittest
from fvs_suite.vault_product_gate import require_restore_product


class ValueString(str):
    pass


class ProductBindingR312(unittest.TestCase):
    def test_grant_same_product(self):
        self.assertEqual(require_restore_product("grants", "grants"), "grants")

    def test_procurement_same_product(self):
        self.assertEqual(require_restore_product("procurement", "procurement"), "procurement")

    def test_grant_mismatch(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            require_restore_product("grants", "procurement")

    def test_procurement_mismatch(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            require_restore_product("procurement", "grants")

    def test_trusted_legacy_grant(self):
        self.assertEqual(require_restore_product("grants"), "grants")

    def test_trusted_legacy_procurement(self):
        self.assertEqual(require_restore_product("procurement"), "procurement")

    def test_archive_null_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid premium evidence product"):
            require_restore_product(None, "grants")

    def test_archive_unknown_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid premium evidence product"):
            require_restore_product("ledger", "grants")

    def test_archive_bool_rejected(self):
        with self.assertRaises(ValueError):
            require_restore_product(True, "grants")

    def test_archive_list_rejected(self):
        with self.assertRaises(ValueError):
            require_restore_product(["grants"], "grants")

    def test_archive_subclass_rejected(self):
        with self.assertRaises(ValueError):
            require_restore_product(ValueString("grants"), "grants")

    def test_scope_unknown_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid premium review product scope"):
            require_restore_product("grants", "free")

    def test_scope_empty_rejected(self):
        with self.assertRaises(ValueError):
            require_restore_product("grants", "")

    def test_scope_bool_rejected(self):
        with self.assertRaises(ValueError):
            require_restore_product("grants", True)

    def test_scope_subclass_rejected(self):
        with self.assertRaises(ValueError):
            require_restore_product("grants", ValueString("grants"))

    def test_scope_list_rejected(self):
        with self.assertRaises(ValueError):
            require_restore_product("grants", ["grants"])

    def test_invalid_archive_is_rejected_even_without_scope(self):
        with self.assertRaises(ValueError):
            require_restore_product("other")

    def test_error_does_not_echo_secret_product(self):
        secret = "PRIVATE_CLIENT_SCOPE_312"
        try:
            require_restore_product("grants", secret)
        except ValueError as error:
            self.assertNotIn(secret, str(error))
            self.assertIsNone(error.__cause__)
            self.assertIsNone(error.__context__)
        else:
            self.fail("expected scope rejection")

    def test_mismatch_message_does_not_disclose_other_product(self):
        try:
            require_restore_product("procurement", "grants")
        except ValueError as error:
            self.assertNotIn("procurement", str(error))
            self.assertNotIn("grants", str(error))
        else:
            self.fail("expected mismatch rejection")

    def test_acceptance_not_inferred_from_product(self):
        # This helper is strictly a scope guard, never an entitlement grant.
        self.assertEqual(type(require_restore_product("grants", "grants")), str)


if __name__ == "__main__":
    unittest.main()
