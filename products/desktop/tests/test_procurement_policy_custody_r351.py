"""R351 direct-policy identity, Decimal bounds, and callback custody tests."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Context, Decimal, getcontext, localcontext
import unittest

from fvs_suite.procurement_policy_custody_r351 import snapshot_price_policy

SHA = "a" * 64
ERROR = "Procurement review requires a native bounded price policy"


@dataclass(frozen=True)
class Policy:
    absolute: Decimal = Decimal("0.01")
    fraction: Decimal = Decimal("0.02")
    source_sha256: str = SHA


class MaliciousPolicy(Policy):
    @property
    def outside(self):
        raise RuntimeError("PRIVATE_CUSTOMER_PATH")


class MaliciousDecimal(Decimal):
    def is_finite(self):
        raise RuntimeError("PRIVATE_CUSTOMER_PATH")


class MaliciousText(str):
    def __str__(self):
        raise RuntimeError("PRIVATE_CUSTOMER_PATH")


class MaliciousDict(dict):
    def __getitem__(self, _key):
        raise RuntimeError("PRIVATE_CUSTOMER_PATH")


class SnapshotPricePolicyR351(unittest.TestCase):
    def capture(self, policy):
        return snapshot_price_policy(policy, Policy)

    def reject(self, policy):
        with self.assertRaises(ValueError) as caught:
            self.capture(policy)
        self.assertEqual(str(caught.exception), ERROR)
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)

    def test_defaults(self):
        self.assertEqual(self.capture(Policy()), (Decimal("0.01"), Decimal("0.02"), SHA))

    def test_custom_valid_thresholds(self):
        self.assertEqual(self.capture(Policy(Decimal("50.00"), Decimal("0.10"), "f"*64)),
                         (Decimal("50.00"), Decimal("0.10"), "f"*64))

    def test_all_zeros(self):
        self.assertEqual(self.capture(Policy(Decimal("0"), Decimal("0"))),
                         (Decimal(0), Decimal(0), SHA))

    def test_maximum_absolute_and_fraction(self):
        self.assertEqual(self.capture(Policy(Decimal("100.00000000"), Decimal("0.10000000")))[0], Decimal(100))

    def test_context_precision_and_flags_unchanged(self):
        with localcontext(Context(prec=2)):
            before = getcontext().copy()
            self.capture(Policy())
            self.assertEqual(before.prec, getcontext().prec)
            self.assertEqual(before.flags, getcontext().flags)

    def test_repeated_snapshot_deterministic(self):
        p = Policy()
        self.assertEqual([self.capture(p) for _ in range(12)], [self.capture(p)] * 12)

    def test_wrong_policy_type(self):
        self.reject(object())

    def test_none_policy(self):
        self.reject(None)

    def test_subclass_getter_not_called(self):
        self.reject(MaliciousPolicy())

    def test_subclass_decimal_not_called(self):
        self.reject(Policy(MaliciousDecimal("0.01")))

    def test_string_threshold_not_converted(self):
        self.reject(Policy("0.01"))

    def test_float_threshold_not_converted(self):
        self.reject(Policy(0.01))

    def test_bool_threshold_not_converted(self):
        self.reject(Policy(True))

    def test_integer_threshold_not_converted(self):
        self.reject(Policy(1))

    def test_nan_absolute(self):
        self.reject(Policy(Decimal("NaN")))

    def test_snan_absolute(self):
        self.reject(Policy(Decimal("sNaN")))

    def test_infinite_fraction(self):
        self.reject(Policy(fraction=Decimal("Infinity")))

    def test_negative_absolute(self):
        self.reject(Policy(Decimal("-0.01")))

    def test_negative_zero_absolute(self):
        self.reject(Policy(Decimal("-0.00")))

    def test_negative_zero_fraction(self):
        self.reject(Policy(fraction=Decimal("-0")))

    def test_too_large_absolute(self):
        self.reject(Policy(Decimal("100.00000001")))

    def test_too_large_fraction(self):
        self.reject(Policy(fraction=Decimal("0.10000001")))

    def test_long_coefficient(self):
        self.reject(Policy(Decimal("0." + "0" * 100 + "1")))

    def test_exponent_bomb_zero(self):
        self.reject(Policy(Decimal("0E-100000000")))

    def test_positive_exponent_bomb_zero(self):
        self.reject(Policy(Decimal("0E+100000000")))

    def test_hash_empty(self):
        self.reject(Policy(source_sha256=""))

    def test_hash_private_path_no_leak(self):
        self.reject(Policy(source_sha256="C:/PRIVATE_CUSTOMER_PATH/file.csv"))

    def test_hash_uppercase(self):
        self.reject(Policy(source_sha256="A" * 64))

    def test_hash_wrong_length(self):
        self.reject(Policy(source_sha256="a" * 63))

    def test_hash_unicode_spoof(self):
        self.reject(Policy(source_sha256="а" * 64))

    def test_hash_str_subclass_no_execution(self):
        self.reject(Policy(source_sha256=MaliciousText(SHA)))

    def test_mutated_stored_dictionary_rejected(self):
        policy = Policy()
        object.__setattr__(policy, "__dict__", MaliciousDict(policy.__dict__))
        self.reject(policy)

    def test_extra_injected_field_rejected(self):
        policy = Policy()
        object.__setattr__(policy, "private_path", "C:/PRIVATE_CUSTOMER_PATH")
        self.reject(policy)

    def test_deleted_field_rejected(self):
        policy = Policy()
        del policy.__dict__["absolute"]
        self.reject(policy)

    def test_snapshot_stable_after_original_mutated(self):
        policy = Policy()
        first = self.capture(policy)
        object.__setattr__(policy, "absolute", Decimal("99"))
        self.assertEqual(first[0], Decimal("0.01"))
        self.assertEqual(self.capture(policy)[0], Decimal("99"))

    def test_hash_int_rejected(self):
        self.reject(Policy(source_sha256=1))

    def test_hash_nonfinite_str_rejected(self):
        self.reject(Policy(source_sha256="nan" * 21 + "0"))


if __name__ == "__main__":
    unittest.main()
