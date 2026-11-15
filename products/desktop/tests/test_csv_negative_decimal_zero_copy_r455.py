"""R455: zero-copy negative Decimal CSV formula inspection.

Pure stdlib/synthetic data; no customer fields, telemetry or network.
"""
from __future__ import annotations

import random
import re
import tracemalloc
import unittest

from fvs_suite.csv_formula_guard import has_unescaped_formula_prefix

# Exact pre-R455 regex predicate for parity. Its suffix slice allocates.
_LEGACY_DECIMAL = re.compile(r"-[0-9]+(?:\.[0-9]+)?\Z", re.ASCII)
_LEADING_MARKS = ("", "\u200b", " \t", "\u0301", "\ufeff", "\u200d", "\r\n", "\u2066")


class NegativeDecimalZeroCopyR455(unittest.TestCase):
    def test_negative_integer_and_fraction_after_ignorable_marks(self):
        for lead in _LEADING_MARKS:
            for number in ("-0", "-42", "-0.00", "-1234567890.25", "-" + "9" * 30000):
                with self.subTest(lead=repr(lead),number=number[:20]):
                    self.assertFalse(has_unescaped_formula_prefix(lead + number))

    def test_noncanonical_negative_inputs_remain_rejected(self):
        for lead in _LEADING_MARKS:
            for number in ("-", "-1+2", "-1 ", "-1e3", "-1,00", "-1.2.3", "-.5", "- 1", "-１", "−1", "➖1", "-0\n", "-0\u200b"):
                with self.subTest(lead=repr(lead),number=number):
                    self.assertTrue(has_unescaped_formula_prefix(lead + number))

    def test_other_formula_prefixes_continue_to_fail_closed(self):
        for char in ("=", "+", "@", "＝", "＋", "＠", "－", "﹣", "−", "➖"):
            for lead in _LEADING_MARKS:
                self.assertTrue(has_unescaped_formula_prefix(lead + char + "A1"))

    def test_explicit_escape_after_leading_mark_keeps_existing_behavior(self):
        for lead in _LEADING_MARKS:
            self.assertFalse(has_unescaped_formula_prefix(lead + "'=1+2"))

    def test_randomized_decimal_regex_parity_100000(self):
        rng = random.Random(455)
        alphabet = "-+0123456789.e, ABCXYZ\n\u0661"
        for _ in range(100000):
            lead = rng.choice(_LEADING_MARKS)
            fragment = "".join(rng.choice(alphabet) for _ in range(rng.randrange(1,60)))
            value = lead + fragment
            # When the first meaningful codepoint is ASCII '-' the new
            # positional search must preserve the legacy slice semantics.
            if fragment.startswith("-"):
                expected = _LEGACY_DECIMAL.fullmatch(value[len(lead):]) is None
                self.assertEqual(has_unescaped_formula_prefix(value), expected)

    def test_long_ascii_decimal_uses_no_suffix_copy(self):
        # tracemalloc isolates Python temporary allocations for a 1 MiB cell.
        # The old slice copies about 1 MiB. The new positional regex doesn't.
        value = "\u200b" + "-" + "9" * 950_000 + ".05"
        tracemalloc.start()
        try:
            tracemalloc.reset_peak()
            self.assertFalse(has_unescaped_formula_prefix(value))
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertLess(peak, 100_000, f"Unexpected temporary allocation: {peak}")

    def test_long_unicode_control_prefix_keeps_evidence_unchanged(self):
        value = "\u200b" * 1200 + "-314.159"
        before = value
        self.assertFalse(has_unescaped_formula_prefix(value))
        self.assertEqual(value, before)

    def test_no_implicit_compliance_approval(self):
        # The predicate is safety-only; any negative numeric entry may still
        # be incorrect and must remain reviewable by the financial engine.
        self.assertFalse(has_unescaped_formula_prefix("-100.00"))
        self.assertTrue(has_unescaped_formula_prefix("-100.00+1"))


if __name__ == "__main__":
    unittest.main()
