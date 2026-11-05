"""R196: reject non-native policy hunk field names before any lookup.

All examples are synthetic. A look-alike cue is for human review, never
legal/compliance approval. The original source text never leaves local memory.
"""
from __future__ import annotations

import unittest
from fvs_suite.policy_confusables import _owned_rows, render_local_confusable_evidence as render


PRIVATE = "confidential-donor-account-4920"


def hunk(old=((3, "PAY A\n"),), new=((4, "PAY А\n"),)):
    return {"removed_sources": list(old), "added_sources": list(new)}


class HostileKey:
    def __init__(self, target="removed_sources"):
        self.target = target
        self.compared = 0

    def __hash__(self):
        return hash(self.target)

    def __eq__(self, other):
        self.compared += 1
        raise AssertionError("untrusted key equality executed")


class LoggedKey:
    def __init__(self, target):
        self.target = target
        self.calls = 0

    def __hash__(self):
        return hash(self.target)

    def __eq__(self, other):
        self.calls += 1
        return False


class SubclassKey(str):
    def __format__(self, _format):
        raise AssertionError("untrusted key formatting executed")


class PolicyHunkKeyCustodyR196(unittest.TestCase):
    def assert_bad_key(self, key, *, native=False):
        value = hunk()
        if native:
            # Key has no collision, but any non-native metadata is forbidden.
            dict.__setitem__(value, key, "untrusted")
        else:
            value = {key: [(3, "PAY A\n")], "added_sources": [(4, "PAY А\n")]}
        self.assertEqual(render([value]), "")
        self.assertIsNone(_owned_rows(value, "removed_sources"))
        self.assertIsNone(_owned_rows(value, "added_sources"))

    def test_colliding_removed_key_never_calls_eq(self):
        key = HostileKey("removed_sources")
        self.assert_bad_key(key)
        self.assertEqual(key.compared, 0)

    def test_colliding_added_key_never_calls_eq(self):
        key = HostileKey("added_sources")
        value = {key: [(4, "PAY А\n")], "removed_sources": [(3, "PAY A\n")]}
        self.assertEqual(render([value]), "")
        self.assertIsNone(_owned_rows(value, "added_sources"))
        self.assertEqual(key.compared, 0)

    def test_logged_removed_key_has_zero_eq_calls(self):
        key = LoggedKey("removed_sources")
        self.assert_bad_key(key)
        self.assertEqual(key.calls, 0)

    def test_logged_added_key_has_zero_eq_calls(self):
        key = LoggedKey("added_sources")
        value = {key: [(4, "PAY А\n")], "removed_sources": [(3, "PAY A\n")]}
        self.assertEqual(render([value]), "")
        self.assertEqual(key.calls, 0)

    def test_object_extra_metadata_rejected(self):
        self.assert_bad_key(object(), native=True)

    def test_int_extra_metadata_rejected(self):
        self.assert_bad_key(123, native=True)

    def test_bytes_extra_metadata_rejected(self):
        self.assert_bad_key(b"metadata", native=True)

    def test_none_extra_metadata_rejected(self):
        self.assert_bad_key(None, native=True)

    def test_tuple_extra_metadata_rejected(self):
        self.assert_bad_key(("metadata",), native=True)

    def test_boolean_extra_metadata_rejected(self):
        self.assert_bad_key(True, native=True)

    def test_str_subclass_source_key_rejected(self):
        self.assert_bad_key(SubclassKey("removed_sources"))

    def test_str_subclass_extra_metadata_rejected(self):
        self.assert_bad_key(SubclassKey("extra"), native=True)

    def test_plain_unused_string_metadata_allowed(self):
        value = hunk()
        value["deleted"] = 1
        self.assertIn("before L3; after L4", render([value]))

    def test_valid_native_keys_preserve_named_screen_reader_cue(self):
        result = render([hunk()])
        self.assertIn("CYRILLIC CAPITAL LETTER A", result)
        self.assertIn("human review", result)
        self.assertNotIn(PRIVATE, result)

    def test_two_valid_hunks_remain_ordered(self):
        result = render([hunk(), hunk(((20, "FEE A\n"),), ((21, "FEE А\n"),))])
        self.assertLess(result.index("hunk 001"), result.index("hunk 002"))

    def test_invalid_extra_key_skipped_without_leaking_private_text(self):
        value = hunk(old=((3, PRIVATE + " A\n"),), new=((4, PRIVATE + " А\n"),))
        value[object()] = PRIVATE
        result = render([value])
        self.assertEqual(result, "")
        self.assertNotIn(PRIVATE, result)

    def test_invalid_hunk_preserves_separate_valid_hunk(self):
        bad = hunk()
        bad[object()] = "bad"
        result = render([bad, hunk(((8, "FEE A\n"),), ((9, "FEE А\n"),))])
        self.assertIn("hunk 002: before L8; after L9", result)
        self.assertNotIn("hunk 001", result)

    def test_key_validation_does_not_rewrite_caller_mapping(self):
        value = hunk()
        extra = object()
        value[extra] = "confidential"
        before = dict(value)
        self.assertEqual(render([value]), "")
        self.assertEqual(value, before)

    def test_duplicates_remain_ambiguous(self):
        value = hunk(((2, "PAY A\n"), (3, "PAY А\n")), ((4, "PAY Α\n"),))
        self.assertEqual(render([value]), "")

    def test_global_coordinate_collision_still_fails_closed(self):
        self.assertEqual(render([hunk(), hunk()]), "")

    def test_non_dict_subclass_remains_rejected(self):
        class StrangeDict(dict):
            def get(self, *_):
                raise AssertionError("non-native get")
        self.assertEqual(render([StrangeDict(hunk())]), "")

    def test_no_hunks(self):
        self.assertEqual(render([]), "")


if __name__ == "__main__":
    unittest.main()
