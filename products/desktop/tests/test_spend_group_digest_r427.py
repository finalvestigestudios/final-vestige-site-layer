"""Direct-helper R427 financial evidence identity regressions (synthetic only)."""
from __future__ import annotations

from hashlib import sha256
import unittest

from fvs_suite.spend_group_digest_r427 import checked_spend_group_evidence

HASH = sha256(b"R427 synthetic source").hexdigest()

_DEFAULT = object()

def group(source=HASH, vendor="ACME", month="2026-11", rows=_DEFAULT):
    return checked_spend_group_evidence(source, vendor, month,
                                        [2, 4, 7] if rows is _DEFAULT else rows)


class GroupDigestCustodyR427(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(group(), (HASH, "ACME", "2026-11", (2, 4, 7)))

    def test_valid_single_row(self):
        self.assertEqual(group(rows=[2])[-1], (2,))

    def test_valid_months(self):
        for month in ("0001-01", "2026-02", "9999-12"):
            with self.subTest(month=month):
                self.assertEqual(group(month=month)[2], month)

    def test_invalid_months(self):
        for month in ("0000-01", "2026-00", "2026-13", "2026-1", "2026-011", " 2026-11",
                      "2026-11\n", "2026/11", 12):
            with self.subTest(month=repr(month)), self.assertRaisesRegex(ValueError, "source-group"):
                group(month=month)

    def test_native_month_only(self):
        class Spoof(str):
            def encode(self, *_args, **_kwargs):
                raise AssertionError("PRIVATE_MONTH")
        with self.assertRaisesRegex(ValueError, "source-group"):
            group(month=Spoof("2026-11"))

    def test_valid_vendor(self):
        for vendor in ("A", "A123", "ABC_123".replace("_", "")):
            with self.subTest(vendor=vendor):
                self.assertEqual(group(vendor=vendor)[1], vendor)

    def test_reject_invalid_vendor(self):
        for vendor in ("", "Acme", "ACME-1", "CAFÉ", "AC ME", "A\n",
                       "A" * 1_048_577, 100):
            with self.subTest(vendor=repr(vendor)[:35]), self.assertRaisesRegex(ValueError, "source-group"):
                group(vendor=vendor)

    def test_native_vendor_only(self):
        class Spoof(str):
            def encode(self, *_args, **_kwargs):
                raise AssertionError("PRIVATE_VENDOR")
        with self.assertRaisesRegex(ValueError, "source-group") as cm:
            group(vendor=Spoof("ACME"))
        self.assertNotIn("PRIVATE_VENDOR", str(cm.exception))

    def test_invalid_source(self):
        with self.assertRaisesRegex(ValueError, "Source snapshot SHA-256"):
            group(source="f" * 65)

    def test_invalid_source_subclass(self):
        class Spoof(str):
            def encode(self, *_args, **_kwargs):
                raise AssertionError("PRIVATE_SHA")
        with self.assertRaisesRegex(ValueError, "Source snapshot SHA-256"):
            group(source=Spoof(HASH))

    def test_reject_empty(self):
        with self.assertRaisesRegex(ValueError, "source-group"):
            group(rows=[])

    def test_reject_non_list(self):
        for value in ((2, 3), iter((2, 3)), "2;3", None):
            with self.subTest(value=type(value).__name__), self.assertRaisesRegex(ValueError, "source-group"):
                group(rows=value)

    def test_reject_list_subclass_without_iteration(self):
        class Forged(list):
            def __iter__(self):
                raise AssertionError("PRIVATE_ROWS")
        with self.assertRaisesRegex(ValueError, "source-group"):
            group(rows=Forged([2, 3]))

    def test_reject_non_native_physical_row(self):
        class Forged(int):
            def __str__(self):
                raise AssertionError("PRIVATE_ROW")
        for value in (True, 2.0, "2", Forged(2)):
            with self.subTest(value=type(value).__name__), self.assertRaisesRegex(ValueError, "source-group"):
                group(rows=[value])

    def test_reject_row_order_and_duplicates(self):
        for rows in ([3, 2], [2, 2], [3, 4, 4]):
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, "source-group"):
                group(rows=rows)

    def test_reject_out_of_range_rows(self):
        for rows in ([1], [0], [-4], [10_000_000_000]):
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, "source-group"):
                group(rows=rows)

    def test_reject_oversized_group(self):
        with self.assertRaisesRegex(ValueError, "source-group"):
            group(rows=list(range(2, 200_003)))

    def test_owned_copy(self):
        rows = [2, 4]
        evidence = group(rows=rows)
        rows.append(9)
        self.assertEqual(evidence[-1], (2, 4))


if __name__ == "__main__":
    unittest.main()
