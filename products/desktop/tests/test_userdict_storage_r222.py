"""R222 synthetic, local-only storage-vs-virtual-view evidence regressions."""
from __future__ import annotations

import unittest
from collections import UserDict
from decimal import Decimal

from fvs_suite.csv_userdict_custody import UserDictCustodyError, verify_userdict_storage


class ForgedUserDict(UserDict):
    def __init__(self, source, emitted):
        super().__init__(source)
        self.emitted = emitted
        self.calls = 0

    def items(self):
        self.calls += 1
        return iter(self.emitted)


class HostileEq:
    def __eq__(self, other):
        raise RuntimeError("SECRET_FINANCIAL_PAYLOAD")


class CustodyR222(unittest.TestCase):
    def setUp(self):
        self.normal = {"id": "A", "amount": Decimal("12.3400"), "source_row": "2"}
        self.entries = tuple(self.normal.items())

    def confirm(self, source, entries, max_columns=256):
        return verify_userdict_storage(source, entries, max_columns)

    def reject(self, source, entries):
        with self.assertRaises(UserDictCustodyError) as e:
            self.confirm(source, entries)
        self.assertIsNone(e.exception.__context__)
        self.assertIsNone(e.exception.__cause__)
        self.assertEqual(str(e.exception), "CSV report UserDict view differs from stored evidence")

    def test_standard_userdict_remains_supported(self):
        row = UserDict(self.normal)
        self.assertEqual(self.confirm(row, tuple(row.items())), self.entries)

    def test_plain_dict_untouched(self):
        self.assertIs(self.confirm(self.normal, self.entries), self.entries)

    def test_other_mapping_untouched(self):
        from types import MappingProxyType
        proxy = MappingProxyType(self.normal)
        self.assertIs(self.confirm(proxy, self.entries), self.entries)

    def test_forged_identifier_rejected(self):
        self.reject(ForgedUserDict(self.normal, []), (("id", "APPROVED"), *self.entries[1:]))

    def test_forged_money_rejected(self):
        self.reject(ForgedUserDict(self.normal, []), (("id", "A"), ("amount", Decimal("0")), ("source_row", "2")))

    def test_hidden_source_row_rejected(self):
        original = {"id": "A", "amount": Decimal("12.3400")}
        self.reject(ForgedUserDict(original, []), self.entries)

    def test_hidden_unsafe_extra_rejected(self):
        original = {**self.normal, "hidden": "=SUM(A1)"}
        self.reject(ForgedUserDict(original, []), self.entries)

    def test_reordered_view_rejected(self):
        self.reject(ForgedUserDict(self.normal, []), tuple(reversed(self.entries)))

    def test_native_decimal_scale_preserved(self):
        value = self.confirm(UserDict(self.normal), self.entries)
        self.assertEqual(str(value[1][1]), "12.3400")

    def test_native_negative_decimal_preserved(self):
        record = {**self.normal, "amount": Decimal("-0.0100")}
        self.assertEqual(self.confirm(UserDict(record), tuple(record.items()))[1][1], Decimal("-0.0100"))

    def test_custom_object_identity_without_eq(self):
        value = HostileEq()
        record = {**self.normal, "extra": value}
        self.assertIs(self.confirm(UserDict(record), tuple(record.items()))[-1][1], value)

    def test_custom_object_substitution_rejected_without_eq(self):
        source = {**self.normal, "extra": HostileEq()}
        emitted = (*self.entries, ("extra", HostileEq()))
        self.reject(UserDict(source), emitted)

    def test_forged_str_subclass_rejected(self):
        class Forged(str):
            pass
        emitted = (("id", Forged("A")), *self.entries[1:])
        self.reject(UserDict(self.normal), emitted)

    def test_missing_native_data_rejected(self):
        row = UserDict(self.normal)
        del row.__dict__["data"]
        self.reject(row, self.entries)

    def test_non_dict_data_rejected(self):
        row = UserDict(self.normal)
        row.__dict__["data"] = [("id", "A")]
        self.reject(row, self.entries)

    def test_dict_subclass_backing_reads_native_items(self):
        class Deceptive(dict):
            def items(self):
                raise RuntimeError("SECRET_FINANCIAL_PAYLOAD")
        row = UserDict(self.normal)
        row.__dict__["data"] = Deceptive(self.normal)
        self.assertEqual(self.confirm(row, self.entries), self.entries)

    def test_oversized_backing_rejected(self):
        source = {str(i): "x" for i in range(257)}
        row = UserDict(source)
        self.reject(row, tuple(list(source.items())[:256]))

    def test_direct_userdict_hook_never_called_by_check(self):
        row = ForgedUserDict(self.normal, [])
        self.assertEqual(self.confirm(row, self.entries), self.entries)
        self.assertEqual(row.calls, 0)

    def test_invalid_field_name_rejected(self):
        source = {**self.normal, 42: "strange"}
        self.reject(UserDict(source), tuple(source.items()))

    def test_valid_float_remains_compatible_at_check_layer(self):
        row = UserDict({"id": "A", "measure": 1.25})
        self.assertEqual(self.confirm(row, tuple(row.items()))[-1], ("measure", 1.25))

    def test_boolean_value_type_mismatch_rejected(self):
        row = UserDict({"id": "A", "flag": True})
        self.reject(row, (("id", "A"), ("flag", 1)))

    def test_none_value_remains_compatible_at_check_layer(self):
        row = UserDict({"id": "A", "missing": None})
        self.assertIsNone(self.confirm(row, tuple(row.items()))[-1][1])

    def test_decimals_with_distinct_scaling_equal_are_supported(self):
        row = UserDict({"id": "A", "amount": Decimal("2.00")})
        entries = (("id", "A"), ("amount", Decimal("2.0")))
        native = self.confirm(row, entries)
        self.assertEqual(str(native[1][1]), "2.00")


if __name__ == "__main__":
    unittest.main()
