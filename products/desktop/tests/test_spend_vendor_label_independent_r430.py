"""R430 independent SpendMap vendor-label verifier regressions (synthetic only)."""
from __future__ import annotations

from hashlib import sha256
import unittest

from fvs_suite.spend_label_verify import expected_vendor_labels


def expected(*items):
    return expected_vendor_labels([("ACME", month, category, label)
                                   for month, category, label in items])


class IndependentSpendLabelsR430(unittest.TestCase):
    def test_one_plain_label(self):
        self.assertEqual(expected(("2026-01", "Parts", "ACME")),
                         {("ACME", "2026-01", "Parts"): "ACME"})

    def test_vendor_wide_labels_across_categories_and_months(self):
        rows = [("2026-01", "Parts", "ACME"),
                ("2026-01", "Services", "A-CME"),
                ("2026-02", "Travel", "acme")]
        actual = expected(*rows)
        self.assertEqual(set(actual.values()), {"A-CME; ACME; acme"})
        self.assertEqual(len(actual), 3)

    def test_boundary_ascii_spaces_preserved(self):
        actual = expected(("2026-01", "X", " ACME"),
                          ("2026-01", "X", "ACME "))
        self.assertEqual(next(iter(actual.values())), r"\u0020ACME; ACME\u0020")

    def test_control_and_separator_visible(self):
        actual = expected(("2026-01", "X", "\tA;B\r"))
        self.assertEqual(next(iter(actual.values())), r"\u0009A\u003BB\u000D")

    def test_literal_escape_cannot_impersonate_boundary(self):
        actual = expected(("2026-01", "X", " ACME"),
                          ("2026-01", "X", r"\u0020ACME"))
        labels = next(iter(actual.values()))
        self.assertIn(r"\u0020ACME", labels)
        self.assertIn(r"\\u0020ACME", labels)

    def test_unicode_combining_is_escaped(self):
        self.assertEqual(next(iter(expected(("2026-01", "X", "A\u0301")).values())),
                         r"A\u0301")

    def test_nonascii_whitespace_not_discarded(self):
        self.assertEqual(next(iter(expected(("2026-01", "X", "\u00a0ACME")).values())),
                         r"\u00A0ACME")

    def test_empty_and_ascii_only_whitespace_excluded(self):
        values = expected(("2026-01", "X", ""),
                          ("2026-02", "Y", " \t\r "))
        self.assertEqual(set(values.values()), {""})
        self.assertEqual(len(values), 2)

    def test_formula_like_vendor_escaped_at_csv_boundary(self):
        for raw, output in (("=ACME", "'=ACME"),
                            ("+ACME", "'+ACME"),
                            ("@ACME", "'@ACME"),
                            ("-ACME", "'-ACME")):
            with self.subTest(raw=raw):
                self.assertEqual(next(iter(expected(("2026-01", "X", raw)).values())), output)

    def test_32_labels_unabridged(self):
        data = [("2026-01", "X", f"ACME{i:03}") for i in range(32)]
        actual = next(iter(expected(*data).values()))
        self.assertEqual(actual, "; ".join(f"ACME{i:03}" for i in range(32)))

    def test_33_labels_digest_and_counts(self):
        data = [("2026-01", "X", f"ACME{i:03}") for i in range(33)]
        actual = next(iter(expected(*data).values()))
        self.assertIn(r"\u[PREVIEW_ONLY:shown=32:omitted=1:sha256=", actual)
        self.assertNotIn("ACME032;", actual)
        digest = sha256(b"FVS-SPEND-RAW-VENDOR-LABELS-v1\n")
        for _, _, label in data:
            encoded = label.encode("utf-8")
            digest.update(len(encoded).to_bytes(8, "big"))
            digest.update(encoded)
        self.assertTrue(actual.endswith("sha256=" + digest.hexdigest() + "]"))

    def test_oversized_label_prefix_and_full_digest(self):
        actual = next(iter(expected(("2026-01", "X", "Z" * 3000)).values()))
        self.assertTrue(actual.startswith("Z" * 64 + r"\u[LABEL_PREFIX_ONLY]"))
        self.assertIn("PREVIEW_ONLY:shown=1:omitted=0", actual)
        self.assertLessEqual(len(actual), 8192)

    def test_single_1024_label_stays_complete(self):
        self.assertEqual(next(iter(expected(("2026-01", "X", "Q" * 1024)).values())), "Q" * 1024)

    def test_expanded_unicode_prefix_bounded(self):
        actual = next(iter(expected(("2026-01", "X", "\u200d" * 500)).values()))
        self.assertIn("LABEL_PREFIX_ONLY", actual)
        self.assertLessEqual(len(actual), 8192)

    def test_2000_labels_bound_even_repeated_buckets(self):
        data = [("2026-01" if i % 2 else "2026-02", "X", f"ACME{i:04}" + "X" * 900)
                for i in range(2000)]
        result = expected(*data)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(set(result.values())), 1)
        self.assertLessEqual(len(next(iter(result.values()))), 8192)
        self.assertIn("omitted=", next(iter(result.values())))

    def test_order_invariance_with_duplicates(self):
        data = [("2026-01", "X", f"ACME{i:03}") for i in range(45)]
        self.assertEqual(expected(*data), expected(*(list(reversed(data)) + data)))

    def test_digest_detects_omitted_label_modification(self):
        a = [("2026-01", "X", f"ACME{i:03}") for i in range(41)]
        b = a[:-1] + [("2026-01", "X", "ACME999")]
        self.assertNotEqual(expected(*a), expected(*b))

    def test_invalid_raw_object_rejected_before_callbacks(self):
        class PrivateStr(str):
            def strip(self, *args):
                raise AssertionError("PRIVATE CUSTOMER LABEL")
        with self.assertRaises(ValueError) as cm:
            expected(("2026-01", "X", PrivateStr("ACME")))
        self.assertNotIn("PRIVATE", str(cm.exception))

    def test_invalid_unicode_does_not_leak_customer_data(self):
        with self.assertRaises(ValueError) as cm:
            expected(("2026-01", "X", "PRIVATE_CUSTOMER" + "\ud800" * 1100))
        self.assertNotIn("PRIVATE_CUSTOMER", str(cm.exception))

    def test_no_generator_or_network_dependency(self):
        import inspect
        import fvs_suite.spend_label_verify as module
        code = inspect.getsource(module)
        self.assertNotIn("from .spend_vendor_evidence", code)
        self.assertNotIn("from .audit_display", code)
        self.assertNotIn("import requests", code)


if __name__ == "__main__":
    unittest.main()
