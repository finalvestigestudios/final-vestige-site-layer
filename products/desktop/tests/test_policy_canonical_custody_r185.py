"""R185: synthetic direct-API provenance safety for NFC-only navigation."""
import unittest
from fvs_suite.policy_canonical import render_local_canonical_evidence as render


def hunk(old=(), new=()):
    return {"removed_sources": list(old), "added_sources": list(new)}


class CanonicalCustodyR185(unittest.TestCase):
    def test_valid_pair(self):
        self.assertIn("before L1; after L2", render([hunk([(1, "Café\n")], [(2, "Cafe\u0301\n")])]))

    def test_mixed_change_valid(self):
        body = render([hunk([(1, "Café\n"), (2, "Owner A\n")],
                            [(1, "Cafe\u0301\n"), (2, "Owner B\n")])])
        self.assertEqual(body.count("NFC-only candidate"), 1)

    def test_two_hunks_valid_order(self):
        body = render([hunk([(1, "é\n")], [(2, "e\u0301\n")]),
                       hunk([(50, "が\n")], [(51, "か\u3099\n")])])
        self.assertIn("Canonical hunk 002: before L50; after L51", body)

    def test_reversed_before_fail_closed(self):
        self.assertEqual(render([hunk([(8, "é\n"), (2, "が\n")],
                                      [(2, "e\u0301\n"), (8, "か\u3099\n")])]), "")

    def test_reversed_after_fail_closed(self):
        self.assertEqual(render([hunk([(2, "が\n"), (8, "é\n")],
                                      [(8, "e\u0301\n"), (2, "か\u3099\n")])]), "")

    def test_duplicate_before_rejected(self):
        self.assertEqual(render([hunk([(1, "é\n"), (1, "É\n")], [(1, "e\u0301\n")])]), "")

    def test_duplicate_after_rejected(self):
        self.assertEqual(render([hunk([(1, "é\n")], [(1, "e\u0301\n"), (1, "foo\n")])]), "")

    def test_cross_hunk_before_collision(self):
        self.assertEqual(render([hunk([(2, "é\n")], [(2, "e\u0301\n")]),
                                 hunk([(2, "が\n")], [(6, "か\u3099\n")])]), "")

    def test_cross_hunk_after_collision(self):
        self.assertEqual(render([hunk([(2, "é\n")], [(2, "e\u0301\n")]),
                                 hunk([(6, "が\n")], [(2, "か\u3099\n")])]), "")

    def test_long_before_row_still_blocks_reuse(self):
        self.assertEqual(render([hunk([(1, "x" * 4097)], []),
                                 hunk([(1, "é\n")], [(3, "e\u0301\n")])]), "")

    def test_long_after_row_still_blocks_reuse(self):
        self.assertEqual(render([hunk([], [(1, "x" * 4097)]),
                                 hunk([(3, "é\n")], [(1, "e\u0301\n")])]), "")

    def test_long_pair_skips_navigation_without_text_leak(self):
        self.assertEqual(render([hunk([(1, "x" * 4096 + "é")], [(1, "x" * 4096 + "e\u0301")])]), "")

    def test_long_then_short_still_cites_short(self):
        self.assertIn("before L3", render([hunk([(1, "x" * 4097), (3, "é\n")],
                                                 [(1, "x" * 4097), (3, "e\u0301\n")])]))

    def test_line_zero_rejected(self):
        self.assertEqual(render([hunk([(0, "é\n")], [(1, "e\u0301\n")])]), "")

    def test_bool_identity_rejected(self):
        self.assertEqual(render([hunk([(True, "é\n")], [(1, "e\u0301\n")])]), "")

    def test_line_over_50000_rejected(self):
        self.assertEqual(render([hunk([(50001, "é\n")], [(50001, "e\u0301\n")])]), "")

    def test_line_50000_accepted(self):
        self.assertIn("before L50000", render([hunk([(50000, "é\n")], [(50000, "e\u0301\n")])]))

    def test_dict_subclass_rejected_without_hook(self):
        class Trap(dict):
            def get(self, *_):
                raise AssertionError("unsafe dictionary hook")
        self.assertEqual(render([Trap(hunk([(1, "é\n")], [(1, "e\u0301\n")]))]), "")

    def test_hostile_dict_key_collision_rejected_before_comparison(self):
        class Trap:
            def __hash__(self):
                return hash("removed_sources")
            def __eq__(self, other):
                raise AssertionError("unsafe key comparison")
        value = {Trap(): "bad", "added_sources": [(1, "e\u0301\n")]}
        self.assertEqual(render([value]), "")

    def test_non_text_dictionary_key_rejected(self):
        value = hunk([(1, "é\n")], [(1, "e\u0301\n")])
        value[7] = "not a real source field"
        self.assertEqual(render([value]), "")

    def test_list_subclass_rejected_without_iter(self):
        class Trap(list):
            def __iter__(self):
                raise AssertionError("unsafe list hook")
        self.assertEqual(render(Trap([hunk([(1, "é\n")], [(1, "e\u0301\n")])])), "")

    def test_row_tuple_subclass_rejected_without_iter(self):
        class Trap(tuple):
            def __iter__(self):
                raise AssertionError("unsafe tuple hook")
        self.assertEqual(render([hunk([Trap((1, "é\n"))], [(1, "e\u0301\n")])]), "")

    def test_text_subclass_rejected(self):
        class Trap(str):
            def __hash__(self):
                raise AssertionError("unsafe text hook")
        self.assertEqual(render([hunk([(1, Trap("é\n"))], [(1, "e\u0301\n")])]), "")

    def test_int_subclass_rejected(self):
        class Trap(int):
            def __le__(self, *_):
                raise AssertionError("unsafe int comparison")
        self.assertEqual(render([hunk([(Trap(1), "é\n")], [(1, "e\u0301\n")])]), "")

    def test_ambiguous_duplicates_suppressed(self):
        self.assertEqual(render([hunk([(1, "é\n"), (2, "e\u0301\n")], [(1, "e\u0301\n")])]), "")

    def test_privacy_and_human_review(self):
        secret = "secret-payee-1234"
        body = render([hunk([(1, secret + "-é\n")], [(1, secret + "-e\u0301\n")])])
        self.assertNotIn(secret, body)
        self.assertIn("human review", body)

    def test_deterministic(self):
        cases = [hunk([(1, "é\n")], [(2, "e\u0301\n")])]
        self.assertEqual(render(cases), render(cases))

    def test_extra_key_compatibility(self):
        a = hunk([(1, "é\n")], [(1, "e\u0301\n")]); a["deleted"] = 42
        self.assertIn("NFC-only candidate", render([a]))

    def test_invalid_second_hunk_suppresses_first_evidence(self):
        self.assertEqual(render([hunk([(1, "é\n")], [(1, "e\u0301\n")]),
                                 hunk([(1, "が\n")], [(3, "か\u3099\n")])]), "")

    def test_valid_gaps(self):
        self.assertIn("before L90; after L91", render([hunk([(2, "é\n"), (90, "が\n")],
                                                        [(3, "e\u0301\n"), (91, "か\u3099\n")])]))

    def test_no_hunks(self):
        self.assertEqual(render([]), "")

    def test_invalid_hunk(self):
        self.assertEqual(render([None]), "")


if __name__ == "__main__":
    unittest.main()
