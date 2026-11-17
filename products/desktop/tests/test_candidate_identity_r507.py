"""R507: fail closed when a six-product native build duplicates an image."""
from __future__ import annotations

import itertools
import unittest

from candidate_identity_r507 import (
    CandidateIdentityError, require_distinct_candidate_images,
)

NAMES = (
    "LedgerDiffLite.exe", "InvoiceTwinScout.exe", "SpendMapLite.exe",
    "PolicyDeltaDesk.exe", "GrantAuditStudioPro.exe", "ProcureGuardStudioPro.exe",
)


def receipt():
    return [{"name": name, "sha256": format(index + 1, "064x"),
             "pe_machine": "AMD64", "smoke": "not_run"}
            for index, name in enumerate(NAMES)]


class NativeIdentityR507(unittest.TestCase):
    def reject(self, records, names=NAMES):
        caught = None
        try:
            require_distinct_candidate_images(records, names)
        except CandidateIdentityError as exc:
            caught = exc
        self.assertIsNotNone(caught)
        self.assertEqual(str(caught), "Six Windows candidate images must be distinct")
        self.assertIsNone(caught.__cause__)
        self.assertIsNone(caught.__context__)

    def test_six_different_named_images_pass(self):
        self.assertIsNone(require_distinct_candidate_images(receipt(), NAMES))

    def test_all_fifteen_pairs_rejected_including_free_to_premium(self):
        for first, second in itertools.combinations(range(6), 2):
            with self.subTest(first=first, second=second):
                rows = receipt()
                rows[second]["sha256"] = rows[first]["sha256"]
                self.reject(rows)

    def test_six_identical_images_rejected(self):
        rows = receipt()
        for row in rows:
            row["sha256"] = "a" * 64
        self.reject(rows)

    def test_reverse_order_rejected(self):
        self.reject(list(reversed(receipt())))

    def test_missing_image_rejected(self):
        self.reject(receipt()[:-1])

    def test_extra_image_rejected(self):
        self.reject(receipt() + [{"name": "Extra.exe", "sha256": "7" * 64}])

    def test_duplicate_product_label_rejected(self):
        rows = receipt()
        rows[-1]["name"] = rows[0]["name"]
        self.reject(rows)

    def test_unknown_product_label_rejected(self):
        rows = receipt()
        rows[0]["name"] = "C:/private/claims.csv"
        self.reject(rows)

    def test_hash_missing_rejected(self):
        rows = receipt()
        rows[0].pop("sha256")
        self.reject(rows)

    def test_uppercase_digest_rejected(self):
        rows = receipt()
        rows[0]["sha256"] = "A" * 64
        self.reject(rows)

    def test_non_hex_digest_rejected(self):
        rows = receipt()
        rows[0]["sha256"] = "g" * 64
        self.reject(rows)

    def test_long_short_and_empty_hashes_rejected(self):
        for digest in ("", "0" * 63, "0" * 65):
            with self.subTest(length=len(digest)):
                rows = receipt()
                rows[0]["sha256"] = digest
                self.reject(rows)

    def test_non_native_hash_and_name_objects_rejected(self):
        class Weird(str):
            pass
        for key, value in (("sha256", Weird("a" * 64)),
                           ("name", Weird(NAMES[0])), ("sha256", True),
                           ("name", None)):
            with self.subTest(key=key, kind=type(value).__name__):
                rows = receipt()
                rows[0][key] = value
                self.reject(rows)

    def test_non_native_record_or_container_rejected(self):
        class Rows(list):
            pass
        class Row(dict):
            pass
        self.reject(Rows(receipt()))
        rows = receipt()
        rows[0] = Row(rows[0])
        self.reject(rows)

    def test_expected_name_set_requires_six_unique_native_strings(self):
        self.reject(receipt(), NAMES[:-1])
        self.reject(receipt(), NAMES + ("Extra.exe",))
        self.reject(receipt(), list(NAMES))
        self.reject(receipt(), NAMES[:5] + (NAMES[0],))
        self.reject(receipt(), NAMES[:5] + (None,))

    def test_records_not_iterable_rejected_without_private_exception(self):
        class Private:
            def __iter__(self):
                raise OSError("C:/private/ledger.csv")
        self.reject(Private())

    def test_valid_result_never_modifies_records(self):
        rows = receipt()
        before = [row.copy() for row in rows]
        require_distinct_candidate_images(rows, NAMES)
        self.assertEqual(rows, before)

    def test_privacy_does_not_echo_arbitrary_text(self):
        rows = receipt()
        rows[3]["sha256"] = "C:/private/finance/policy.txt"
        self.reject(rows)


if __name__ == "__main__":
    unittest.main()
