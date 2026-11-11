"""R353 per-review source identity snapshot; synthetic IDs only.

Focuses on the genuine procurement_reference.py source module. It does not
exercise a packaged executable or adjudicate compliance or payment.
"""
from __future__ import annotations

from collections import Counter
from decimal import Context, Decimal, getcontext, localcontext, setcontext
import unittest

from fvs_suite.procurement_reference import document_key_session, normalized_document_key


class ForgedText(str):
    def __str__(self):
        raise AssertionError("PRIVATE_FINANCIAL_PATH")


class IdentifierSessionR353(unittest.TestCase):
    def test_callback_once_for_repeated_native_label(self):
        seen = []
        def callback(value):
            seen.append(value)
            return value.upper()
        lookup = document_key_session(callback)
        self.assertEqual([lookup("inv-7") for _ in range(20)], ["INV-7"] * 20)
        self.assertEqual(seen, ["inv-7"])

    def test_stateful_callback_cannot_change_same_source_key(self):
        count = 0
        def flipper(value):
            nonlocal count
            count += 1
            return value if count == 1 else "ALTERED"
        lookup = document_key_session(flipper)
        self.assertEqual([lookup("INV-42") for _ in range(3)], ["INV-42"] * 3)
        self.assertEqual(count, 1)

    def test_different_source_labels_have_independent_first_results(self):
        calls = []
        def callback(value):
            calls.append(value)
            return value.upper()
        lookup = document_key_session(callback)
        self.assertEqual([lookup(x) for x in ("a", "b", "a", "b", "c")],
                         ["A", "B", "A", "B", "C"])
        self.assertEqual(calls, ["a", "b", "c"])

    def test_native_int_and_equal_native_text_share_one_key(self):
        received = []
        def callback(value):
            received.append((value, type(value)))
            return value
        lookup = document_key_session(callback)
        self.assertEqual(lookup(12345), "12345")
        self.assertEqual(lookup("12345"), "12345")
        self.assertEqual(received, [("12345", str)])

    def test_source_case_is_not_erased_before_caching(self):
        seen = []
        lookup = document_key_session(lambda s: (seen.append(s), s.lower())[1])
        self.assertEqual(lookup("a"), "a")
        self.assertEqual(lookup("A"), "a")
        self.assertEqual(seen, ["a", "A"])

    def test_source_whitespace_is_not_erased_before_caching(self):
        calls = []
        lookup = document_key_session(lambda s: (calls.append(s), s.strip())[1])
        self.assertEqual(lookup(" a "), "a")
        self.assertEqual(lookup("a"), "a")
        self.assertEqual(calls, [" a ", "a"])

    def test_unicode_labels_do_not_merge_by_python_casefold(self):
        calls = []
        lookup = document_key_session(lambda s: (calls.append(s), s.casefold())[1])
        self.assertEqual(lookup("ß"), "ss")
        self.assertEqual(lookup("ss"), "ss")
        self.assertEqual(calls, ["ß", "ss"])

    def test_boolean_identity_rejected_before_callback(self):
        calls = []
        lookup = document_key_session(lambda s: calls.append(s))
        with self.assertRaises(ValueError):
            lookup(True)
        self.assertEqual(calls, [])

    def test_forged_str_identity_rejected_before_cache_hit(self):
        calls = []
        lookup = document_key_session(lambda s: (calls.append(s), s)[1])
        self.assertEqual(lookup("ABC"), "ABC")
        with self.assertRaises(ValueError):
            lookup(ForgedText("ABC"))
        self.assertEqual(calls, ["ABC"])

    def test_forged_int_identity_rejected_before_callback(self):
        class EvilInt(int):
            pass
        calls = []
        lookup = document_key_session(lambda s: calls.append(s))
        with self.assertRaises(ValueError):
            lookup(EvilInt(99))
        self.assertEqual(calls, [])

    def test_oversized_int_rejected_before_callback(self):
        calls = []
        lookup = document_key_session(lambda s: calls.append(s))
        with self.assertRaises(ValueError):
            lookup(1 << 270)
        self.assertEqual(calls, [])

    def test_other_source_object_rejected_before_callback(self):
        class Spy:
            def __str__(self):
                raise AssertionError("PRIVATE_CUSTOMER_PATH")
        lookup = document_key_session(str)
        with self.assertRaises(ValueError):
            lookup(Spy())

    def test_invalid_callback_result_fails_closed(self):
        lookup = document_key_session(lambda _: 1)
        with self.assertRaisesRegex(ValueError, "native text key"):
            lookup("INV")

    def test_callback_return_subclass_fails_closed(self):
        lookup = document_key_session(lambda _: ForgedText("INV"))
        with self.assertRaisesRegex(ValueError, "native text key"):
            lookup("INV")

    def test_callback_exception_redacted(self):
        def error(_):
            raise OSError("PRIVATE_CUSTOMER_PATH")
        lookup = document_key_session(error)
        with self.assertRaises(ValueError) as captured:
            lookup("INV")
        self.assertEqual(str(captured.exception),
                         "Procurement document normalization requires a native text key")
        self.assertTrue(captured.exception.__suppress_context__)
        self.assertNotIn("PRIVATE", str(captured.exception))

    def test_failed_callback_does_not_cache_invalid_result(self):
        counter = 0
        def flaky(value):
            nonlocal counter
            counter += 1
            if counter == 1:
                raise OSError("PRIVATE_PATH")
            return value
        lookup = document_key_session(flaky)
        with self.assertRaises(ValueError):
            lookup("INV")
        self.assertEqual(lookup("INV"), "INV")
        self.assertEqual(counter, 2)

    def test_empty_label_is_preserved_not_skipped(self):
        calls = []
        lookup = document_key_session(lambda s: (calls.append(s), s)[1])
        self.assertEqual(lookup(""), "")
        self.assertEqual(lookup(""), "")
        self.assertEqual(calls, [""])

    def test_callback_empty_key_remains_valid_under_prior_contract(self):
        calls = []
        lookup = document_key_session(lambda s: (calls.append(s), "")[1])
        self.assertEqual(lookup("INV"), "")
        self.assertEqual(lookup("INV"), "")
        self.assertEqual(calls, ["INV"])

    def test_multiple_review_sessions_are_independent(self):
        calls = []
        def callback(s):
            calls.append(s)
            return s
        first, second = document_key_session(callback), document_key_session(callback)
        self.assertEqual(first("INV"), "INV")
        self.assertEqual(first("INV"), "INV")
        self.assertEqual(second("INV"), "INV")
        self.assertEqual(calls, ["INV", "INV"])

    def test_decimal_precision_isolated_during_callback_and_cache_hit(self):
        calls = []
        def mutate(s):
            getcontext().prec = 1
            calls.append(s)
            return s
        lookup = document_key_session(mutate)
        with localcontext(Context(prec=64)):
            self.assertEqual(lookup("INV"), "INV")
            self.assertEqual(lookup("INV"), "INV")
            self.assertEqual(getcontext().prec, 64)
            self.assertEqual(Decimal(3) * Decimal("0.12345678"), Decimal("0.37037034"))
        self.assertEqual(calls, ["INV"])

    def test_decimal_setcontext_isolated(self):
        def mutate(s):
            setcontext(Context(prec=1))
            return s
        lookup = document_key_session(mutate)
        with localcontext(Context(prec=64)):
            self.assertEqual(lookup("INV"), "INV")
            self.assertEqual(getcontext().prec, 64)

    def test_callback_receives_plain_text_only(self):
        seen = []
        def cb(value):
            seen.append(type(value))
            return value
        lookup = document_key_session(cb)
        lookup(7)
        lookup("a")
        self.assertEqual(seen, [str, str])

    def test_raw_label_custody_unchanged_across_calls(self):
        originals = ["INV/2026", "INV/2026"]
        lookup = document_key_session(lambda s: s.replace("/", ""))
        self.assertEqual([lookup(value) for value in originals], ["INV2026"] * 2)
        self.assertEqual(originals, ["INV/2026", "INV/2026"])

    def test_return_value_matches_existing_normalizer_on_first_use(self):
        def cb(s):
            return s.strip().lower()
        for original in ("", " Inv-2 ", "A/B-42", "ß", "008"):
            self.assertEqual(document_key_session(cb)(original),
                             normalized_document_key(original, cb))

    def test_no_cache_leak_between_100_review_sessions(self):
        seen = []
        for _ in range(100):
            lookup = document_key_session(lambda s: (seen.append(s), s)[1])
            self.assertEqual(lookup("INV"), "INV")
            self.assertEqual(lookup("INV"), "INV")
        self.assertEqual(len(seen), 100)

    def test_many_unique_ids_remain_distinct(self):
        seen = Counter()
        def cb(s):
            seen[s] += 1
            return s
        lookup = document_key_session(cb)
        for index in range(300):
            self.assertEqual(lookup(f"I-{index}"), f"I-{index}")
        for index in range(300):
            self.assertEqual(lookup(f"I-{index}"), f"I-{index}")
        self.assertEqual(len(seen), 300)
        self.assertTrue(all(count == 1 for count in seen.values()))


if __name__ == "__main__":
    unittest.main()
