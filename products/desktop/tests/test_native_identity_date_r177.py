"""R177: 30 synthetic direct-API identity/date adversaries, no customer data."""
from __future__ import annotations

import datetime
from decimal import Decimal
import unittest

from fvs_suite import identity_inputs as inp


class TrapStr(str):
    def __str__(self): raise AssertionError("untrusted __str__ executed")
    def upper(self): raise AssertionError("untrusted upper executed")
    def strip(self, *args): raise AssertionError("untrusted strip executed")


class ForgeStr(str):
    def __str__(self): return "2026-01-01"
    def upper(self): return "APPROVED"
    def strip(self, *args): return "2026-01-01"


class TrapInt(int):
    def __str__(self): raise AssertionError("untrusted int conversion executed")


class TrapObject:
    def __str__(self): raise AssertionError("untrusted conversion executed")
    def __hash__(self): raise AssertionError("untrusted hashing executed")
    def __eq__(self, other): raise AssertionError("untrusted equality executed")


class NativeIdentityDateR177(unittest.TestCase):
    pass


# Named method inventory is independent of input source bytes; synthetic only.
REJECT = (
    ("key_trap_str", inp.normalize_key, TrapStr("SENSITIVE_ACCOUNT")),
    ("key_forged_str", inp.normalize_key, ForgeStr("not-approved")),
    ("key_trap_int", inp.normalize_key, TrapInt(123)),
    ("key_trap_object", inp.normalize_key, TrapObject()),
    ("key_native_int", inp.normalize_key, 2026),
    ("key_decimal", inp.normalize_key, Decimal("1.50")),
    ("key_boolean", inp.normalize_key, True),
    ("key_none", inp.normalize_key, None),
    ("key_bytes", inp.normalize_key, b"ABC"),
    ("key_list", inp.normalize_key, ["ABC"]),
    ("date_trap_str", inp.parse_date, TrapStr("SENSITIVE_ACCOUNT")),
    ("date_forged_str", inp.parse_date, ForgeStr("not-a-date")),
    ("date_trap_int", inp.parse_date, TrapInt(2026)),
    ("date_trap_object", inp.parse_date, TrapObject()),
    ("date_native_int", inp.parse_date, 20260203),
    ("date_decimal", inp.parse_date, Decimal("2026")),
    ("date_boolean", inp.parse_date, False),
    ("date_none", inp.parse_date, None),
    ("date_bytes", inp.parse_date, b"2026-02-03"),
    ("date_native_datetime", inp.parse_date, datetime.date(2026, 2, 3)),
    ("date_invalid_leap", inp.parse_date, "2026-02-29"),
    ("date_unicode_digits", inp.parse_date, "２０２６-02-03"),
    ("date_formula_tail", inp.parse_date, "2026-02-03;=1+1"),
    ("date_oversize", inp.parse_date, "2026-02-03" + "x" * 60),
)
ACCEPT = (
    ("key_ascii", inp.normalize_key, "  Acme, Inc. #123 ", "ACMEINC123"),
    ("key_blank", inp.normalize_key, "---", ""),
    ("key_unicode_lossy", inp.normalize_key, "café", "CAF"),
    ("date_iso", inp.parse_date, "2026-2-3", datetime.date(2026, 2, 3)),
    ("date_us", inp.parse_date, "2/3/26", datetime.date(2026, 2, 3)),
    ("date_leap", inp.parse_date, "2024-02-29", datetime.date(2024, 2, 29)),
)


def make_reject(parser, value):
    def test(self):
        with self.assertRaises(ValueError) as caught:
            parser(value)
        self.assertNotIn("SENSITIVE_ACCOUNT", str(caught.exception))
    return test


def make_accept(parser, value, expected):
    def test(self):
        self.assertEqual(parser(value), expected)
    return test


for name, parser, value in REJECT:
    setattr(NativeIdentityDateR177, "test_" + name, make_reject(parser, value))
for name, parser, value, expected in ACCEPT:
    setattr(NativeIdentityDateR177, "test_" + name, make_accept(parser, value, expected))

if __name__ == "__main__":
    unittest.main()
