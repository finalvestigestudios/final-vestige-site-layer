"""R440: premium issued-license fingerprinting has an intrinsic 8192-byte ceiling.

Uses only synthetic local bytes; this neither creates/authorizes licenses nor
exposes protected financial/customer or signing-key material.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import issued_entitlement_guard as guard


class PublicError(ValueError):
    pass


class TrapInt(int):
    def __le__(self, _other):
        raise AssertionError("CUSTOM_COMPARISON_HOOK_CALLED")

    def __ge__(self, _other):
        raise AssertionError("CUSTOM_COMPARISON_HOOK_CALLED")

    def __rle__(self, _other):
        raise AssertionError("CUSTOM_COMPARISON_HOOK_CALLED")

    def __str__(self):
        raise AssertionError("CUSTOM_FORMAT_HOOK_CALLED")


class R440PremiumFingerprintLimitTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.target = self.root / "synthetic.fvslicense"

    def digest(self, bound):
        return guard.fingerprint_issued_entitlement(self.target, bound, PublicError)

    def assert_sanitized_limit(self, err):
        self.assertIs(type(err), PublicError)
        self.assertIn("bounded native integer", str(err))
        self.assertIsNone(err.__cause__)
        self.assertIsNone(err.__context__)

    def assert_refuses_without_io(self, bound):
        with patch.object(guard.Path, "is_symlink", side_effect=AssertionError("PATH_INSPECTION")) as check, \
             patch.object(guard.os, "open", side_effect=AssertionError("FILE_OPEN")) as opened, \
             patch.object(guard.os, "lstat", side_effect=AssertionError("LSTAT")) as metadata, \
             patch.object(guard.os, "read", side_effect=AssertionError("READ")) as read:
            with self.assertRaises(PublicError) as caught:
                self.digest(bound)
        self.assert_sanitized_limit(caught.exception)
        check.assert_not_called()
        opened.assert_not_called()
        metadata.assert_not_called()
        read.assert_not_called()

    def test_above_absolute_ceiling_refused_before_path_access(self):
        for size in (8193, 16384, 1 << 28, 1 << 128):
            with self.subTest(size=size):
                self.assert_refuses_without_io(size)

    def test_positive_infinity_refused_before_path_access(self):
        self.assert_refuses_without_io(math.inf)

    def test_negative_infinity_refused_before_path_access(self):
        self.assert_refuses_without_io(-math.inf)

    def test_nan_refused_before_path_access(self):
        self.assert_refuses_without_io(math.nan)

    def test_nonintegral_float_refused_before_path_access(self):
        self.assert_refuses_without_io(8192.1)

    def test_exact_integer_float_refused_before_path_access(self):
        self.assert_refuses_without_io(8192.0)

    def test_true_bool_refused_before_path_access(self):
        self.assert_refuses_without_io(True)

    def test_false_bool_refused_before_path_access(self):
        self.assert_refuses_without_io(False)

    def test_zero_and_negative_int_refused_before_path_access(self):
        for size in (0, -1, -(1 << 100)):
            with self.subTest(size=size):
                self.assert_refuses_without_io(size)

    def test_untrusted_objects_refused_without_hooks(self):
        for value in (None, "8192", b"8192", [], {}, object()):
            with self.subTest(kind=type(value).__name__):
                self.assert_refuses_without_io(value)

    def test_hostile_int_subclass_refused_without_comparison_hook(self):
        self.assert_refuses_without_io(TrapInt(8192))

    def test_one_byte_native_limit_is_valid(self):
        self.target.write_bytes(b"x")
        self.assertEqual(self.digest(1), hashlib.sha256(b"x").hexdigest())

    def test_8192_byte_native_limit_preserves_hash_provenance(self):
        payload = b"a" * 8192
        self.target.write_bytes(payload)
        self.assertEqual(self.digest(8192), hashlib.sha256(payload).hexdigest())
        self.assertEqual(self.target.read_bytes(), payload)

    def test_8193_byte_payload_not_accepted_under_8192_ceiling(self):
        payload = b"y" * 8193
        self.target.write_bytes(payload)
        with patch.object(guard.os, "read", side_effect=AssertionError("MUST_NOT_READ")) as read:
            with self.assertRaises(PublicError) as caught:
                self.digest(8192)
        self.assertIn("bounded", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        read.assert_not_called()
        self.assertEqual(self.target.read_bytes(), payload)

    def test_previous_ceiling_bypass_cannot_hash_8193_bytes(self):
        self.target.write_bytes(b"z" * 8193)
        with patch.object(guard.os, "read", side_effect=AssertionError("MUST_NOT_READ")):
            with self.assertRaises(PublicError) as caught:
                self.digest(8193)
        self.assert_sanitized_limit(caught.exception)

    def test_valid_smaller_bound_still_rejects_longer_input_without_read(self):
        self.target.write_bytes(b"abc")
        with patch.object(guard.os, "read", side_effect=AssertionError("MUST_NOT_READ")) as read:
            with self.assertRaises(PublicError) as caught:
                self.digest(2)
        self.assertIn("bounded", str(caught.exception))
        read.assert_not_called()


if __name__ == "__main__":
    unittest.main()
