"""R342: reject forged ProcureGuard reference labels without invoking hooks.

Synthetic text only. No financial files, execution, network, or compliance
approval. The existing original-spelling behavior is retained for CSV text.
"""
from __future__ import annotations

import unittest

from fvs_suite.procurement_reference import (has_original_spelling,
                                             source_document_spellings)


class HostileStr(str):
    calls = 0
    def __str__(self):
        HostileStr.calls += 1
        raise RuntimeError("PRIVATE_CLIENT_LEDGER_PATH")


class HostileObject:
    calls = 0
    def __str__(self):
        HostileObject.calls += 1
        raise RuntimeError("PRIVATE_CLIENT_LEDGER_PATH")


class HostileInt(int):
    calls = 0
    def __str__(self):
        HostileInt.calls += 1
        raise RuntimeError("PRIVATE_CLIENT_LEDGER_PATH")


class HostileFrozen(frozenset):
    def __contains__(self, item):
        raise RuntimeError("PRIVATE_CLIENT_LEDGER_PATH")


class ProcurementNativeIdentityR342(unittest.TestCase):
    def setUp(self):
        HostileStr.calls = HostileInt.calls = HostileObject.calls = 0

    def assert_private_rejection(self, operation):
        with self.assertRaises(ValueError) as caught:
            operation()
        self.assertNotIn("PRIVATE_CLIENT", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertEqual((HostileStr.calls, HostileInt.calls, HostileObject.calls), (0, 0, 0))

    def test_source_str_subclass_does_not_invoke_str(self):
        self.assert_private_rejection(lambda: source_document_spellings([HostileStr("INV-1")]))

    def test_source_object_does_not_invoke_str(self):
        self.assert_private_rejection(lambda: source_document_spellings([HostileObject()]))

    def test_source_int_subclass_does_not_invoke_str(self):
        self.assert_private_rejection(lambda: source_document_spellings([HostileInt(123)]))

    def test_reference_str_subclass_does_not_invoke_str(self):
        self.assert_private_rejection(lambda: has_original_spelling(HostileStr("INV-1"), frozenset(("inv-1",))))

    def test_reference_object_does_not_invoke_str(self):
        self.assert_private_rejection(lambda: has_original_spelling(HostileObject(), frozenset(("inv-1",))))

    def test_reference_int_subclass_does_not_invoke_str(self):
        self.assert_private_rejection(lambda: has_original_spelling(HostileInt(123), frozenset(("123",))))

    def test_source_bool_is_not_integer_document_identity(self):
        self.assert_private_rejection(lambda: source_document_spellings([True]))

    def test_reference_bool_is_not_integer_document_identity(self):
        self.assert_private_rejection(lambda: has_original_spelling(False, frozenset(("false",))))

    def test_huge_int_source_is_bounded_before_str(self):
        self.assert_private_rejection(lambda: source_document_spellings([1 << 270]))

    def test_huge_int_reference_is_bounded_before_str(self):
        self.assert_private_rejection(lambda: has_original_spelling(1 << 270, frozenset(("1",))))

    def test_untrusted_set_subclass_cannot_decide_spelling(self):
        self.assert_private_rejection(lambda: has_original_spelling("INV1", HostileFrozen(("inv1",))))

    def test_untrusted_mutable_set_rejected(self):
        self.assert_private_rejection(lambda: has_original_spelling("INV1", {"inv1"}))

    def test_untrusted_frozenset_member_subclass_rejected(self):
        self.assert_private_rejection(lambda: has_original_spelling("INV1", frozenset((HostileStr("inv1"),))))

    def test_native_csv_string_keeps_exact_identity(self):
        self.assertTrue(has_original_spelling("Inv-1", source_document_spellings(["INV-1"])))

    def test_native_small_integer_legacy_compatibility(self):
        self.assertTrue(has_original_spelling(123, source_document_spellings([123])))

    def test_native_maximum_integer_allowed(self):
        number = (1 << 269) - 1
        self.assertTrue(has_original_spelling(number, source_document_spellings([number])))

    def test_unicode_sharp_s_is_not_ascii_ss(self):
        self.assertFalse(has_original_spelling("SS-1", source_document_spellings(["ß-1"])))

    def test_unicode_long_s_is_not_ascii_s(self):
        self.assertFalse(has_original_spelling("S-1", source_document_spellings(["ſ-1"])))

    def test_spacing_semantics_still_hold(self):
        self.assertTrue(has_original_spelling(" \tinv1\n", source_document_spellings(["INV1 "])))

    def test_deterministic_order_immutable_snapshot(self):
        one = source_document_spellings(["InV-1", "INV-2", "inv-1"])
        two = source_document_spellings(reversed(["InV-1", "INV-2", "inv-1"]))
        self.assertEqual(one, two)
        self.assertEqual(one, frozenset(("inv-1", "inv-2")))

    def test_empty_original_legacy_compatibility(self):
        self.assertTrue(has_original_spelling("", source_document_spellings([""])))

    def test_none_is_not_a_document_identity(self):
        self.assert_private_rejection(lambda: source_document_spellings([None]))

    def test_reference_none_is_not_a_document_identity(self):
        self.assert_private_rejection(lambda: has_original_spelling(None, frozenset(("none",))))

    def test_no_originals_is_unlinked(self):
        self.assertFalse(has_original_spelling("INV-1", source_document_spellings([])))


if __name__ == "__main__":
    unittest.main()
