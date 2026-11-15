"""R456: full-cell slice-free six-app CSV sanitizer regression.

All cases are synthetic. The legacy reference reconstructs the original
R455 function with its exact token slice; it is never used for publishing.
"""
from __future__ import annotations

import random
import re
import tracemalloc
import unicodedata
import unittest
from decimal import Decimal

from fvs_suite.audit_display import _escape_source_character
from fvs_suite.csv_formula_guard import has_unescaped_formula_prefix
from fvs_suite.csv_native_cell import native_report_text
from fvs_suite.engine import safe_cell


def _legacy_safe_cell(value):
    """Pre-R456 behavior, retained only as a transparent parity oracle."""
    s = native_report_text(value)
    index = 0
    invisible_prefix = False
    while index < len(s):
        character = s[index]
        if character == " ":
            index += 1
            continue
        if (character.isspace() or _escape_source_character(character)
                or unicodedata.category(character) in ("Mn", "Me")):
            invisible_prefix = True
            index += 1
            continue
        break
    token = s[index:]
    if (invisible_prefix or token.startswith(("=", "+", "@"))
            or (token.startswith("-") and
                re.fullmatch(r"-[0-9]+(?:\\.[0-9]+)?", token) is None)
            or has_unescaped_formula_prefix(s)):
        return "'" + s
    return s


class SafeCellZeroCopyR456(unittest.TestCase):
    def test_safe_plain_text_after_ascii_spaces_is_preserved(self):
        for lead in (" ", "  ", " " * 64):
            for tail in ("Vendor A", "Paid", "123", "0.00", "-42.10", "-0"):
                raw = lead + tail
                with self.subTest(raw=repr(raw[:25])):
                    self.assertIs(safe_cell(raw), raw)

    def test_formula_and_noncanonical_negative_after_spaces_are_escaped(self):
        tokens = ("=1+2", "+SUM(A1)", "@A1", "-A1", "-1e3",
                  "-.25", "−1", "➖1", "＝A1", "－A1")
        for lead in ("", " ", " " * 17):
            for token in tokens:
                with self.subTest(lead=len(lead), token=token):
                    raw = lead + token
                    self.assertEqual(safe_cell(raw), "'" + raw)

    def test_invisible_prefixes_still_force_review(self):
        for lead in ("\\u200b", "\\ufeff", "\\u0301", "\\u2066", "\\t", "\\n", "\\u00a0"):
            for tail in ("Ordinary", "-123.45", "=A1"):
                raw = lead + tail
                with self.subTest(lead=repr(lead), tail=tail):
                    self.assertEqual(safe_cell(raw), "'" + raw)

    def test_decimal_and_int_values_remain_exact(self):
        for value in (Decimal("-42.100"), Decimal("0.00000001"),
                      Decimal("999999999999.99"), -42, 0, 2026):
            with self.subTest(value=str(value)):
                self.assertEqual(safe_cell(value), str(value))

    def test_source_text_not_mutated_or_normalized(self):
        raw = "  Résumé – vendor \\u200b"
        self.assertIs(safe_cell(raw), raw)
        formula = "  =HYPERLINK(\"x\")"
        self.assertEqual(safe_cell(formula), "'" + formula)
        self.assertEqual(formula, "  =HYPERLINK(\"x\")")

    def test_rejects_caller_defined_string_subclass(self):
        class FakeStr(str):
            def __str__(self):
                raise AssertionError("must never call custom __str__")
        with self.assertRaises(ValueError):
            safe_cell(FakeStr("ordinary"))

    def test_100000_seeded_legacy_parity_cases(self):
        rng = random.Random(456)
        fragments = ("", " ", "  ", "\\u200b", "\\u0301", "\\r",
                     "\\n", "\\u00a0", "4", "42", "-1", "-0.25",
                     "-2e4", "=x", "+SUM(1)", "@A", "−1", "➖1",
                     "plain", "'=1", "😀")
        for trial in range(100_000):
            raw = "".join(rng.choice(fragments)
                          for _ in range(rng.randrange(1, 6)))
            self.assertEqual(safe_cell(raw), _legacy_safe_cell(raw),
                             f"legacy behavior changed on trial {trial}")

    def test_no_one_megabyte_copy_after_ascii_space_and_valid_negative(self):
        raw = " " + "-" + "9" * 950_000
        tracemalloc.start()
        try:
            tracemalloc.reset_peak()
            output = safe_cell(raw)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertIs(output, raw)
        # Avoid setting a platform-specific tiny allocation budget; a copy of
        # 950k codepoints must nevertheless be detectable on CPython.
        self.assertLess(peak, 100_000, f"Excessive report allocation: {peak}")

    def test_no_one_megabyte_copy_after_ascii_space_and_plain_text(self):
        raw = " " + "V" * 950_000
        tracemalloc.start()
        try:
            tracemalloc.reset_peak()
            output = safe_cell(raw)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertIs(output, raw)
        self.assertLess(peak, 100_000, f"Excessive report allocation: {peak}")

    def test_escapes_without_compliance_decision(self):
        self.assertEqual(safe_cell(" -not_a_payment"), "' -not_a_payment")
        self.assertEqual(safe_cell(" -42.10"), " -42.10")
        # The sanitizer never approves a reimbursement or purchase order.
        self.assertEqual(safe_cell("needs review"), "needs review")


if __name__ == "__main__":
    unittest.main()
