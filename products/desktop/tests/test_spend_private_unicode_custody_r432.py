"""R432: private Unicode errors must not leak financial evidence through Python chains.

Isolated source-bound unit regressions. Source/report content is synthetic.
A hidden __context__ on a public error can retain UnicodeError.object even
when "raise ... from None" conceals it in ordinary traceback formatting.
"""
from __future__ import annotations

import csv
from io import StringIO
import unittest

from fvs_suite.spend_label_verify import expected_vendor_labels
from fvs_suite.spend_report_envelope import COLUMNS, NativeSpendCsvDigest


def evidence(raw: str, *, month="2026-01", category="Parts") -> str:
    return expected_vendor_labels([("ACME", month, category, raw)])[
        ("ACME", month, category)]


def assert_private_exception(testcase: unittest.TestCase, exc: BaseException):
    testcase.assertIs(type(exc), ValueError)
    testcase.assertIsNone(exc.__cause__)
    testcase.assertIsNone(exc.__context__)
    testcase.assertNotIn("PRIVATE_ACCOUNT", str(exc))
    testcase.assertNotIn("PRIVATE_VENDOR", str(exc))


class SpendPrivateUnicodeCustodyR432(unittest.TestCase):
    def test_prefix_truncated_surrogate_never_chains_private_label(self):
        raw = "ACME-" + "x" * 1100 + "PRIVATE_ACCOUNT" + "\ud800"
        with self.assertRaises(ValueError) as failure:
            evidence(raw)
        assert_private_exception(self, failure.exception)

    def test_high_cardinality_digest_never_chains_private_label(self):
        rows = [("ACME", "2026-01", "Parts", f"label-{i:02d}")
                for i in range(33)]
        rows.append(("ACME", "2026-01", "Parts", "PRIVATE_VENDOR\udfff"))
        with self.assertRaises(ValueError) as failure:
            expected_vendor_labels(rows)
        assert_private_exception(self, failure.exception)

    def test_non_bmp_valid_unicode_remains_auditable(self):
        self.assertEqual(evidence("ACME-🔎"), "ACME-🔎")

    def test_valid_oversized_label_remains_visibly_bounded(self):
        result = evidence("A" * 1100)
        self.assertIn(r"\u[LABEL_PREFIX_ONLY]", result)
        self.assertIn("sha256=", result)
        self.assertNotIn("A" * 65, result)
        self.assertLessEqual(len(result), 8192)

    def test_33_labels_keep_full_digest_without_throwing(self):
        rows = [("ACME", "2026-01", "Parts", "V" + str(i))
                for i in range(33)]
        result = expected_vendor_labels(rows)[("ACME", "2026-01", "Parts")]
        self.assertIn("shown=32:omitted=1:sha256=", result)

    def test_digest_preview_is_insertion_order_independent(self):
        rows = [("ACME", "2026-01", "Parts", "V" + str(i))
                for i in range(40)]
        forward = expected_vendor_labels(rows)
        backward = expected_vendor_labels(list(reversed(rows)))
        self.assertEqual(forward, backward)

    def test_spaces_retained_and_visible(self):
        rows = [("ACME", "2026-01", "Parts", " ACME"),
                ("ACME", "2026-01", "Parts", "ACME ")]
        rendered = expected_vendor_labels(rows)[("ACME", "2026-01", "Parts")]
        self.assertIn(r"\u0020ACME", rendered)
        self.assertIn(r"ACME\u0020", rendered)

    def test_spreadsheet_protection_remains_unchanged(self):
        for raw in ("+ACME", "=ACME", "＠ACME", "﹣5"):
            with self.subTest(raw=raw):
                self.assertEqual(evidence(raw), "'" + raw)
        self.assertEqual(evidence("-12.30"), "-12.30")

    def test_native_report_writer_rejects_private_high_surrogate(self):
        digest = NativeSpendCsvDigest()
        previous = digest.byte_length
        with self.assertRaises(ValueError) as failure:
            digest.write("PRIVATE_ACCOUNT" + "\ud800")
        assert_private_exception(self, failure.exception)
        self.assertEqual(digest.byte_length, previous)

    def test_native_report_writer_rejects_private_low_surrogate(self):
        digest = NativeSpendCsvDigest()
        with self.assertRaises(ValueError) as failure:
            digest.write("PRIVATE_VENDOR" + "\udfff")
        assert_private_exception(self, failure.exception)

    def test_writer_rejects_str_subclass_without_invoking_overrides(self):
        class Forged(str):
            def encode(self, *args, **kwargs):
                raise AssertionError("subclass method executed")
        digest = NativeSpendCsvDigest()
        with self.assertRaises(ValueError) as failure:
            digest.write(Forged("PRIVATE_ACCOUNT"))
        assert_private_exception(self, failure.exception)

    def test_writer_rejects_nontext_without_stringifying_it(self):
        class Forged:
            def __str__(self):
                raise AssertionError("private object was rendered")
        with self.assertRaises(ValueError) as failure:
            NativeSpendCsvDigest().write(Forged())
        assert_private_exception(self, failure.exception)

    def test_successful_ascii_write_is_counted_in_utf8_bytes(self):
        digest = NativeSpendCsvDigest()
        start = digest.byte_length
        self.assertEqual(digest.write("café"), 4)
        self.assertEqual(digest.byte_length - start, len("café".encode("utf-8")))

    def test_failed_encoding_does_not_change_future_digest(self):
        a, b = NativeSpendCsvDigest(), NativeSpendCsvDigest()
        with self.assertRaises(ValueError):
            a.write("PRIVATE_ACCOUNT\ud800")
        for digest in (a, b):
            digest.write("ACME")
        self.assertEqual(a.byte_length, b.byte_length)
        self.assertEqual(a._hash.digest(), b._hash.digest())

    def test_native_report_digest_matches_valid_canonical_writer(self):
        record = {name: "" for name in COLUMNS}
        record["vendor_key"] = "ACME"
        record["amount"] = "12.30"
        digest = NativeSpendCsvDigest()
        digest.add_row(record)
        stream = StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\r\n")
        writer.writeheader()
        writer.writerow(record)
        native_bytes = b"\xef\xbb\xbf" + stream.getvalue().encode("utf-8")
        self.assertTrue(digest.matches(native_bytes))

    def test_native_report_digest_rejects_appended_bytes(self):
        digest = NativeSpendCsvDigest()
        stream = StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\r\n")
        writer.writeheader()
        native_bytes = b"\xef\xbb\xbf" + stream.getvalue().encode("utf-8")
        self.assertTrue(digest.matches(native_bytes))
        self.assertFalse(digest.matches(native_bytes + b"x"))


if __name__ == "__main__":
    unittest.main()
