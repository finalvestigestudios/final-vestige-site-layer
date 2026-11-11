"""R343: validate original ProcureGuard IDs before normalization, fail closed.

Tests only synthetic document labels and callbacks; no private data or Windows
binary. Full real-engine tests require repository runners and remain mandatory.
"""
from __future__ import annotations

import unittest

from fvs_suite.procurement_reference import (
    normalized_document_key, source_document_spellings, has_original_spelling,
)


class TrapStr(str):
    calls = 0
    def __str__(self):
        TrapStr.calls += 1
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")
    def upper(self):
        TrapStr.calls += 1
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")


class TrapInt(int):
    calls = 0
    def __str__(self):
        TrapInt.calls += 1
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")


class TrapObject:
    calls = 0
    def __str__(self):
        TrapObject.calls += 1
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")


class TrapKey(str):
    calls = 0
    def __hash__(self):
        TrapKey.calls += 1
        raise RuntimeError("PRIVATE_FINANCIAL_PATH")


class NativeDocumentKeyR343(unittest.TestCase):
    def setUp(self):
        TrapStr.calls = TrapInt.calls = TrapObject.calls = TrapKey.calls = 0
        self.seen = []

    def key(self, value):
        self.seen.append(value)
        return "".join(c for c in value.upper() if c.isascii() and c.isalnum())

    def assert_rejected(self, operation):
        with self.assertRaises(ValueError) as context:
            operation()
        self.assertNotIn("PRIVATE_FINANCIAL_PATH", str(context.exception))
        self.assertIsNone(context.exception.__cause__)
        self.assertEqual((TrapStr.calls, TrapInt.calls, TrapObject.calls, TrapKey.calls), (0, 0, 0, 0))

    def test_plain_id_matches_existing_normalizer(self):
        self.assertEqual(normalized_document_key("INV-01", self.key), "INV01")

    def test_empty_id_stays_empty(self):
        self.assertEqual(normalized_document_key("", self.key), "")

    def test_boundaries_keep_input_unchanged(self):
        self.assertEqual(normalized_document_key(" Invoice# 01 ", self.key), "INVOICE01")
        self.assertEqual(self.seen, [" Invoice# 01 "])

    def test_unicode_lossy_normalization_is_not_original_identity(self):
        self.assertEqual(normalized_document_key("INV-1", self.key), normalized_document_key("INV1", self.key))
        self.assertFalse(has_original_spelling("INV1", source_document_spellings(["INV-1"])))

    def test_native_numeric_key_normalized_as_text(self):
        self.assertEqual(normalized_document_key(123, self.key), "123")
        self.assertEqual(self.seen, ["123"])

    def test_max_native_int_is_accepted(self):
        value = (1 << 269) - 1
        self.assertEqual(normalized_document_key(value, self.key), str(value))

    def test_negative_int_is_still_native_text(self):
        self.assertEqual(normalized_document_key(-12, self.key), "12")
        self.assertEqual(self.seen, ["-12"])

    def test_str_subclass_rejected_before_callback(self):
        self.assert_rejected(lambda: normalized_document_key(TrapStr("INV"), self.key))
        self.assertEqual(self.seen, [])

    def test_int_subclass_rejected_before_callback(self):
        self.assert_rejected(lambda: normalized_document_key(TrapInt(12), self.key))
        self.assertEqual(self.seen, [])

    def test_arbitrary_object_rejected_before_callback(self):
        self.assert_rejected(lambda: normalized_document_key(TrapObject(), self.key))
        self.assertEqual(self.seen, [])

    def test_bool_rejected_before_callback(self):
        self.assert_rejected(lambda: normalized_document_key(True, self.key))
        self.assertEqual(self.seen, [])

    def test_none_rejected_before_callback(self):
        self.assert_rejected(lambda: normalized_document_key(None, self.key))
        self.assertEqual(self.seen, [])

    def test_float_rejected_before_callback(self):
        self.assert_rejected(lambda: normalized_document_key(12.0, self.key))
        self.assertEqual(self.seen, [])

    def test_oversize_int_rejected_before_callback(self):
        self.assert_rejected(lambda: normalized_document_key(1 << 270, self.key))
        self.assertEqual(self.seen, [])

    def test_callback_runtime_error_redacted(self):
        def bad(_):
            raise RuntimeError("PRIVATE_FINANCIAL_PATH")
        self.assert_rejected(lambda: normalized_document_key("INV", bad))

    def test_callback_os_error_redacted(self):
        def bad(_):
            raise OSError("PRIVATE_FINANCIAL_PATH")
        self.assert_rejected(lambda: normalized_document_key("INV", bad))

    def test_callback_value_error_redacted(self):
        def bad(_):
            raise ValueError("PRIVATE_FINANCIAL_PATH")
        self.assert_rejected(lambda: normalized_document_key("INV", bad))

    def test_callback_none_rejected(self):
        self.assert_rejected(lambda: normalized_document_key("INV", lambda _: None))

    def test_callback_boolean_rejected(self):
        self.assert_rejected(lambda: normalized_document_key("INV", lambda _: False))

    def test_callback_bytes_rejected(self):
        self.assert_rejected(lambda: normalized_document_key("INV", lambda _: b"INV"))

    def test_callback_str_subclass_rejected_before_hash(self):
        self.assert_rejected(lambda: normalized_document_key("INV", lambda _: TrapKey("INV")))

    def test_keyboard_interrupt_not_masked(self):
        def stop(_):
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            normalized_document_key("INV", stop)

    def test_system_exit_not_masked(self):
        def stop(_):
            raise SystemExit(2)
        with self.assertRaises(SystemExit):
            normalized_document_key("INV", stop)

    def test_repeat_key_stable(self):
        a = normalized_document_key("InV-2", self.key)
        b = normalized_document_key("InV-2", self.key)
        self.assertEqual(a, b)

    def test_same_callback_gets_built_in_string(self):
        def strict(v):
            self.assertIs(type(v), str)
            return v
        self.assertEqual(normalized_document_key(5, strict), "5")

    def test_no_original_reference_is_auto_approved(self):
        self.assertFalse(has_original_spelling("INV-1", source_document_spellings([])))


if __name__ == "__main__":
    unittest.main()
