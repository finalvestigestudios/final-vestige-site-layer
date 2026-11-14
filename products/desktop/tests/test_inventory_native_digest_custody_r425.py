"""R425: premium source inventory must bind native stored digest facts, not virtual views.

Synthetic local files only. No network, customer values, compliance approvals or publication.
"""
from __future__ import annotations

import hashlib
import tempfile
import traceback
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import manifest_guard as guard


class NativeDigestCustodyR425(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.claim = Path(temp.name) / "secret-client-claims.csv"
        self.report = Path(temp.name) / "review.csv"
        self.claim.write_bytes(b"invoice,amount\nA,10.00\n")
        self.report.write_bytes(b"invoice,status\nA,human_review\n")
        self.good = hashlib.sha256(self.claim.read_bytes()).hexdigest()
        self.other = hashlib.sha256(b"different snapshot with same meaning").hexdigest()
        self.assertNotEqual(self.good, self.other)

    def manifest(self, digests):
        return guard.inventory_text([self.claim], [self.report], expected_input_digests=digests)

    def assert_private_error(self, values, message):
        with self.assertRaisesRegex(ValueError, message) as caught:
            self.manifest(values)
        detail = "".join(traceback.format_exception(caught.exception))
        self.assertNotIn(self.claim.name, str(caught.exception))
        self.assertNotIn(str(self.claim), str(caught.exception))
        self.assertNotIn("PRIVATE_LEDGER_TOKEN", detail)

    def test_native_path_and_native_digest_succeed(self):
        self.assertIn(self.good, self.manifest({self.claim: self.good}))

    def test_native_string_path_and_digest_succeed(self):
        self.assertIn(self.good, self.manifest({str(self.claim): self.good}))

    def test_correct_binding_keeps_report_order(self):
        rows = self.manifest({self.claim: self.good}).splitlines()
        self.assertEqual(len(rows), 3)
        self.assertTrue(rows[1].startswith("secret-client-claims.csv\t"))
        self.assertTrue(rows[2].startswith("review.csv\t"))

    def test_wrong_native_digest_rejected(self):
        self.assert_private_error({self.claim: self.other}, "Source bytes changed")

    def test_comparison_forging_digest_cannot_accept_changed_source(self):
        class ForgedDigest(str):
            def __eq__(self, other): return True
            def __ne__(self, other): return False
            __hash__ = str.__hash__
        with patch.object(guard, "_hash_regular", side_effect=AssertionError("HASHED")) as hash_file:
            self.assert_private_error({self.claim: ForgedDigest(self.other)}, "Invalid source digest")
            hash_file.assert_not_called()

    def test_even_truthful_string_subclass_rejected(self):
        class DigestSubclass(str):
            pass
        self.assert_private_error({self.claim: DigestSubclass(self.good)}, "Invalid source digest")

    def test_forged_comparison_hook_never_executed(self):
        class Hostile(str):
            def __eq__(self, other): raise AssertionError("CUSTOM_EQUALITY")
            def __ne__(self, other): raise AssertionError("CUSTOM_INEQUALITY")
            __hash__ = str.__hash__
        self.assert_private_error({self.claim: Hostile(self.good)}, "Invalid source digest")

    def test_malformed_native_digests_still_rejected(self):
        for invalid in ("A"*64, "f"*63, "z"*64, "", "PRIVATE_LEDGER_TOKEN"):
            with self.subTest(value_len=len(invalid)):
                self.assert_private_error({self.claim: invalid}, "Invalid source digest")

    def test_nonstring_digest_types_rejected(self):
        for invalid in (True, 3, None, b"f"*64, ["f"*64]):
            with self.subTest(type=type(invalid).__name__):
                self.assert_private_error({self.claim: invalid}, "Invalid source digest")

    def test_dict_subclass_items_cannot_lie_about_stored_digest(self):
        class VirtualItems(dict):
            def items(self):
                return [(self.claim, self.good)]
        forged = VirtualItems({self.claim: self.other})
        forged.claim = self.claim
        forged.good = self.good
        self.assert_private_error(forged, "Source bytes changed")

    def test_dict_subclass_items_hook_not_run(self):
        class ExplodingItems(dict):
            def items(self): raise AssertionError("VIRTUAL_ITEMS_EXECUTED")
        self.assertIn(self.good, self.manifest(ExplodingItems({self.claim: self.good})))

    def test_non_dict_virtual_mapping_rejected_before_file_read(self):
        class VirtualMapping:
            def items(self): return [(self.claim, self.good)]
        obj = VirtualMapping()
        obj.claim, obj.good = self.claim, self.good
        with patch.object(guard, "_hash_regular", side_effect=AssertionError("HASHED")):
            self.assert_private_error(obj, "Invalid source digest map")

    def test_forged_str_path_key_rejected_before_fspath_and_hash(self):
        class EvilStr(str):
            def __eq__(self, other): raise AssertionError("EQUALITY_HOOK")
            __hash__ = str.__hash__
        with patch.object(guard, "_hash_regular", side_effect=AssertionError("HASHED")) as hash_file:
            self.assert_private_error({EvilStr(str(self.claim)): self.good}, "Invalid source digest map")
            hash_file.assert_not_called()

    def test_custom_fspath_key_rejected_before_hook_runs(self):
        class EvilPath:
            def __fspath__(self): raise AssertionError("FSPATH_HOOK")
        with patch.object(guard, "_hash_regular", side_effect=AssertionError("HASHED")) as hash_file:
            self.assert_private_error({EvilPath(): self.good}, "Invalid source digest map")
            hash_file.assert_not_called()

    def test_duplicate_canonical_path_keys_rejected(self):
        self.assert_private_error({self.claim: self.good, str(self.claim): self.good}, "coverage mismatch")

    def test_missing_path_digest_rejected(self):
        self.assert_private_error({}, "coverage mismatch")

    def test_extra_path_digest_rejected(self):
        self.assert_private_error({self.claim: self.good, str(self.report): self.good}, "coverage mismatch")

    def test_descriptive_inventory_still_available_without_pin(self):
        self.assertIn(self.good, guard.inventory_text([self.claim], [self.report]))


if __name__ == "__main__":
    unittest.main()
