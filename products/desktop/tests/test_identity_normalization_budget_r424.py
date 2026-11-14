"""R424: bound source-identity casing and regex resources without truncation.

All inputs are synthetic; no source files, telemetry, network or compliance
approval are involved. Run on both CPython normal and -OO optimized modes.
"""
from __future__ import annotations

from datetime import date
import traceback
import unittest
from unittest.mock import patch

from fvs_suite import identity_inputs as subject


class IdentityNormalizationBudgetR424(unittest.TestCase):
    def assert_private_failure(self, value):
        with self.assertRaisesRegex(ValueError, "^Source identity text exceeds length limit$") as ctx:
            subject.normalize_key(value)
        detail = "".join(traceback.format_exception(ctx.exception))
        self.assertNotIn("SECRET_ACCOUNT", detail)
        self.assertIsNone(ctx.exception.__context__)
        self.assertIsNone(ctx.exception.__cause__)

    def test_declared_ceiling_matches_native_source_cell_policy(self):
        self.assertEqual(subject.MAX_SOURCE_IDENTITY_CHARS, 1_048_576)

    def test_ascii_source_exact_ceiling_is_not_truncated(self):
        value = "A" * subject.MAX_SOURCE_IDENTITY_CHARS
        self.assertEqual(subject.normalize_key(value), value)

    def test_one_character_over_ceiling_is_refused(self):
        self.assert_private_failure("SECRET_ACCOUNT" + "A" * subject.MAX_SOURCE_IDENTITY_CHARS)

    def test_refuses_oversized_input_before_regex_processing(self):
        with patch.object(subject.re, "sub", side_effect=AssertionError("REGEX_CALLED")) as regex:
            self.assert_private_failure("Z" * (subject.MAX_SOURCE_IDENTITY_CHARS + 1))
            regex.assert_not_called()

    def test_unicode_expansion_over_ceiling_rejected_before_regex(self):
        # Sharp S expands to SS, so a sub-ceiling input can exceed output cap.
        value = "ß" * (subject.MAX_SOURCE_IDENTITY_CHARS // 2 + 1)
        self.assertLess(len(value), subject.MAX_SOURCE_IDENTITY_CHARS)
        with patch.object(subject.re, "sub", side_effect=AssertionError("REGEX_CALLED")) as regex:
            self.assert_private_failure(value)
            regex.assert_not_called()

    def test_exact_unicode_expansion_ceiling_remains_supported(self):
        self.assertEqual(subject.normalize_key("ß" * (subject.MAX_SOURCE_IDENTITY_CHARS // 2)),
                         "SS" * (subject.MAX_SOURCE_IDENTITY_CHARS // 2))

    def test_unicode_expansion_does_not_silently_collapse_to_truncated_match(self):
        near = "ß" * (subject.MAX_SOURCE_IDENTITY_CHARS // 2)
        self.assertEqual(len(subject.normalize_key(near)), subject.MAX_SOURCE_IDENTITY_CHARS)
        self.assert_private_failure(near + "ß")

    def test_distinct_source_spelling_keeps_lossy_legacy_normalization(self):
        self.assertEqual(subject.normalize_key("Acme, Inc. #001"), "ACMEINC001")
        self.assertEqual(subject.normalize_key("Straße"), "STRASSE")

    def test_short_unicode_and_punctuation_are_unchanged(self):
        self.assertEqual(subject.normalize_key("café / £2"), "CAF2")
        self.assertEqual(subject.normalize_key("---"), "")
        self.assertEqual(subject.normalize_key(""), "")

    def test_native_type_boundary_precedes_size_or_user_hooks(self):
        class Hostile(str):
            def __len__(self):
                raise AssertionError("UNTRUSTED_LENGTH")
            def upper(self):
                raise AssertionError("UNTRUSTED_UPPER")
        with self.assertRaisesRegex(ValueError, "^Invalid source identity text$"):
            subject.normalize_key(Hostile("SECRET_ACCOUNT"))

    def test_nonstring_shapes_remain_rejected(self):
        for bad in (None, True, 5, b"KEY", ["KEY"]):
            with self.subTest(kind=type(bad).__name__):
                with self.assertRaisesRegex(ValueError, "^Invalid source identity text$"):
                    subject.normalize_key(bad)

    def test_oversized_source_failure_does_not_include_private_identifier(self):
        self.assert_private_failure("SECRET_ACCOUNT" * (subject.MAX_SOURCE_IDENTITY_CHARS // 14 + 1))

    def test_normal_date_parsing_unchanged(self):
        self.assertEqual(subject.parse_date("2026-11-14"), date(2026, 11, 14))
        self.assertEqual(subject.parse_date("11/14/26"), date(2026, 11, 14))

    def test_invalid_date_and_date_subclass_unchanged(self):
        with self.assertRaisesRegex(ValueError, "Invalid date"):
            subject.parse_date("2026-02-29")
        class Hostile(str):
            def strip(self):
                raise AssertionError("UNTRUSTED_STRIP")
        with self.assertRaisesRegex(ValueError, "Invalid date"):
            subject.parse_date(Hostile("2026-11-14"))


if __name__ == "__main__":
    unittest.main()
