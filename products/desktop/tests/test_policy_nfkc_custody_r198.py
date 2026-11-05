"""R198 direct-API custody regressions for human-only NFKC line navigation."""
from __future__ import annotations

import unittest
from fvs_suite.policy_compatibility_custody import owned_nfkc_hunks as stage


SECRET = "private-account-849209"


def hunk(old=((3, "Limit ⑩\n"),), new=((4, "Limit 10\n"),)):
    return {"removed_sources": list(old), "added_sources": list(new)}


class ToxicKey:
    def __init__(self):
        self.calls = 0
    def __hash__(self):
        return hash("removed_sources")
    def __eq__(self, _):
        self.calls += 1
        raise AssertionError("untrusted equality executed")


class ToxicList(list):
    def __iter__(self):
        raise AssertionError("untrusted list iterator executed")


class ToxicDict(dict):
    def get(self, *_):
        raise AssertionError("untrusted dict getter executed")


class ToxicStr(str):
    def __str__(self):
        raise AssertionError("untrusted text formatter executed")


class NfkcCustodyR198(unittest.TestCase):
    def test_positive_real_source_rows(self):
        result = stage([hunk()])
        self.assertEqual(result[0][0], 1)
        self.assertEqual(result[0][1]["Limit 10\n"], [(3, "Limit ⑩\n")])
        self.assertEqual(result[0][2]["Limit 10\n"], [(4, "Limit 10\n")])

    def test_two_hunks_keep_order_and_coordinates(self):
        result = stage([hunk(), hunk(((14, "Role Ａ\n"),), ((15, "Role A\n"),))])
        self.assertEqual([item[0] for item in result], [1, 2])
        self.assertEqual(result[1][1]["Role A\n"], [(14, "Role Ａ\n")])

    def test_duplicate_folded_lines_preserved_for_ambiguity_suppression(self):
        result = stage([hunk(((3, "Limit ⑩\n"), (4, "Limit 10\n")),
                              ((5, "Limit 10\n"),))])
        self.assertEqual(len(result[0][1]["Limit 10\n"]), 2)

    def test_empty_input_is_no_candidates(self):
        self.assertEqual(stage([]), [])

    def test_non_native_hunk_containers(self):
        for invalid in (None, (), {}, ToxicList([hunk()])):
            with self.subTest(type=type(invalid).__name__):
                self.assertIsNone(stage(invalid))

    def test_non_native_hunk_mapping_rejected_before_get(self):
        self.assertIsNone(stage([ToxicDict(hunk())]))

    def test_non_native_field_container_rejected_before_iter(self):
        value = hunk()
        value["removed_sources"] = ToxicList(value["removed_sources"])
        self.assertIsNone(stage([value]))

    def test_hunk_missing_source_field(self):
        self.assertIsNone(stage([{"removed_sources": [(2, "X\n")]}]))

    def test_toxic_colliding_key_not_compared(self):
        key = ToxicKey()
        hostile = {key: [(3, "Limit ⑩\n")], "added_sources": [(4, "Limit 10\n")]}
        self.assertIsNone(stage([hostile]))
        self.assertEqual(key.calls, 0)

    def test_toxic_extra_key_disables_earlier_good_cues(self):
        value = hunk()
        value[object()] = SECRET
        self.assertIsNone(stage([hunk(), value]))

    def test_non_native_str_key_rejected(self):
        value = hunk()
        value[ToxicStr("metadata")] = SECRET
        self.assertIsNone(stage([value]))

    def test_key_metadata_plain_string_allowed(self):
        value = hunk()
        value["deleted"] = 1
        self.assertIsNotNone(stage([value]))

    def test_nested_row_tuple_required(self):
        for invalid in ([3, "Limit ⑩\n"], (3,), (3, "Limit ⑩\n", "extra"), "row"):
            with self.subTest(value=repr(invalid)):
                self.assertIsNone(stage([hunk((invalid,), ())]))

    def test_native_positive_physical_numbers_only(self):
        for bad in (None, 0, -1, 50_001, 3.0, "3", True, 3.0 + 0j):
            with self.subTest(row=repr(bad)):
                self.assertIsNone(stage([hunk(((bad, "Limit ⑩\n"),), ())]))

    def test_non_native_source_text_rejected(self):
        for bad in (None, 123, b"Limit 10\n", ToxicStr("Limit ⑩\n")):
            with self.subTest(value=type(bad).__name__):
                self.assertIsNone(stage([hunk(((3, bad),), ())]))

    def test_duplicate_physical_rows_rejected(self):
        self.assertIsNone(stage([hunk(((3, "Limit ⑩\n"), (3, "Other ⑩\n")), ())]))

    def test_backward_physical_rows_rejected(self):
        self.assertIsNone(stage([hunk(((3, "Limit ⑩\n"), (2, "Other ⑩\n")), ())]))

    def test_cross_hunk_before_collision_disables_all(self):
        self.assertIsNone(stage([hunk(), hunk(((3, "Role Ａ\n"),), ((14, "Role A\n"),))]))

    def test_cross_hunk_after_collision_disables_all(self):
        self.assertIsNone(stage([hunk(), hunk(((14, "Role Ａ\n"),), ((4, "Role A\n"),))]))

    def test_later_malformed_data_invalidates_prior_candidates(self):
        bad = hunk(((19, "Role Ａ\n"),), ((20, "Role A\n"),))
        bad["added_sources"].append((20, "Duplicate after citation\n"))
        self.assertIsNone(stage([hunk(), bad]))

    def test_long_valid_row_skipped_for_display_but_coordinate_checked(self):
        long_text = "⑩" * 4097
        result = stage([hunk(((3, long_text), (4, "Limit ⑩\n")), ((4, "Limit 10\n"),))])
        self.assertEqual(result[0][1], {"Limit 10\n": [(4, "Limit ⑩\n")]})

    def test_long_row_duplicate_still_invalidates_all(self):
        long_text = "⑩" * 4097
        self.assertIsNone(stage([hunk(((3, long_text), (3, "Limit ⑩\n")), ())]))

    def test_native_upper_limit_is_accepted(self):
        result = stage([hunk(((50_000, "Limit ⑩\n"),), ((50_000, "Limit 10\n"),))])
        self.assertIsNotNone(result)

    def test_more_than_50000_hunks_is_invalid(self):
        self.assertIsNone(stage([{}] * 50_001))

    def test_text_budget_includes_long_skipped_lines(self):
        # Exercise source-budget boundary without huge allocations: repeated
        # legitimate long rows exceed the original policy file byte limit.
        value = hunk(tuple((n, "a" * 4097) for n in range(2, 3000)), ())
        self.assertIsNone(stage([value]))

    def test_plain_input_unchanged(self):
        value = hunk()
        before = repr(value)
        stage([value])
        self.assertEqual(repr(value), before)


if __name__ == "__main__":
    unittest.main()
