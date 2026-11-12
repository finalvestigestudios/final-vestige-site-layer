"""R366: bounded, hash-seed-independent Policy Delta review output.

All inputs synthetic. These cues do not constitute compliance or legal advice.
"""
from __future__ import annotations

import random
import unittest
from unittest.mock import patch

from fvs_suite.policy_confusables import (
    _retain_earliest_pair,
    render_local_confusable_evidence as render,
)


def hunk(line=1, count=1):
    return {
        "removed_sources": [(line + i, f"Term {i:03d} A\n") for i in range(count)],
        "added_sources": [(line + i, f"Term {i:03d} А\n") for i in range(count)],
    }


class BoundedCitationsR366(unittest.TestCase):
    def test_one_pair_still_renders(self):
        report = render([hunk()])
        self.assertIn("before L1; after L1", report)
        self.assertIn("human review", report)

    def test_dense_single_hunk_keeps_earliest_sixteen(self):
        report = render([hunk(count=100)])
        self.assertEqual(report.count("Look-alike hunk"), 16)
        self.assertIn("before L1; after L1", report)
        self.assertIn("before L16; after L16", report)
        self.assertNotIn("before L17;", report)
        self.assertIn("+84 additional look-alike pair(s) omitted", report)

    def test_hunk_order_and_omission_count(self):
        report = render([hunk(i) for i in range(1, 21)])
        self.assertEqual(report.count("Look-alike hunk"), 16)
        self.assertIn("Look-alike hunk 016", report)
        self.assertNotIn("Look-alike hunk 017", report)
        self.assertIn("+4 additional look-alike pair(s) omitted", report)

    def test_multi_hunk_and_multi_row_citation_order(self):
        report = render([hunk(1, 10), hunk(21, 10)])
        before_10 = report.index("before L10;")
        before_21 = report.index("before L21;")
        self.assertLess(before_10, before_21)
        self.assertNotIn("before L27;", report)
        self.assertIn("+4 additional look-alike pair(s) omitted", report)

    def test_invalid_late_hunk_fails_whole_report(self):
        self.assertEqual(render([hunk(count=100),
                                 {"removed_sources": [(1, "X")]}]), "")

    def test_ambiguous_skeleton_not_counted_as_omitted(self):
        ambiguous = {"removed_sources": [(1, "A"), (2, "А")],
                     "added_sources": [(1, "Α")]}
        report = render([ambiguous, hunk(4)])
        self.assertEqual(report.count("Look-alike hunk"), 1)
        self.assertNotIn("additional look-alike", report)

    def test_source_and_private_labels_not_mutated_or_echoed(self):
        private = [{"removed_sources": [(1, "customer-507 A")],
                    "added_sources": [(1, "customer-507 А")]}]
        before = repr(private)
        report = render(private)
        self.assertNotIn("customer-507", report)
        self.assertEqual(repr(private), before)

    def test_selector_drops_late_high_coordinates(self):
        shown = []
        for line in range(1, 5001):
            _retain_earliest_pair(shown, (1, line, line, "cue"), 16)
            self.assertLessEqual(len(shown), 16)
        self.assertEqual([v[1] for v in shown], list(range(1, 17)))

    def test_selector_retains_earliest_even_in_reverse_order(self):
        shown = []
        for line in range(5000, 0, -1):
            _retain_earliest_pair(shown, (1, line, line, "cue"), 16)
            self.assertLessEqual(len(shown), 16)
        self.assertEqual([v[1] for v in shown], list(range(1, 17)))

    def test_selector_equals_full_sort_on_shuffled_matches(self):
        all_candidates = [(i // 70 + 1, i + 1, i + 2, "safe") for i in range(300)]
        random.Random(366).shuffle(all_candidates)
        retained = []
        for candidate in all_candidates:
            _retain_earliest_pair(retained, candidate, 16)
        self.assertEqual(retained, sorted(all_candidates)[:16])

    def test_selector_handles_zero_and_negative_limit(self):
        for limit in (0, -5):
            held = []
            _retain_earliest_pair(held, (1, 1, 1, "cue"), limit)
            self.assertEqual(held, [])

    def test_selector_obeys_one_pair_limit(self):
        held = []
        for coord in (10, 4, 20, 2):
            _retain_earliest_pair(held, (1, coord, coord, "cue"), 1)
            self.assertLessEqual(len(held), 1)
        self.assertEqual(held, [(1, 2, 2, "cue")])

    def test_renderer_with_small_limit_keeps_correct_earliest(self):
        with patch("fvs_suite.policy_confusables._MAX_PAIRS", 2):
            report = render([hunk(count=8)])
        self.assertIn("before L1;", report)
        self.assertIn("before L2;", report)
        self.assertNotIn("before L3;", report)
        self.assertIn("+6 additional look-alike pair(s) omitted", report)

    def test_zero_limit_still_warns_without_leaking_source(self):
        with patch("fvs_suite.policy_confusables._MAX_PAIRS", 0):
            report = render([hunk(count=2)])
        self.assertNotIn("before L", report)
        self.assertIn("+2 additional look-alike pair(s) omitted", report)

    def test_renderer_deterministic_across_repeated_calls(self):
        values = [hunk(count=90)]
        reference = render(values)
        for _ in range(10):
            self.assertEqual(render(values), reference)



# R367 extends the already mandatory R366 Ubuntu/Windows source gate; no
# additional workflow step or artifact privilege is introduced.
from fvs_suite import policy_confusables as _r367_source


def _r367_hunk(line, old="PAY A\n", new="PAY А\n"):
    return {"removed_sources": [(line, old)],
            "added_sources": [(line, new)]}


class DeferredGlyphCuesR367(unittest.TestCase):
    def test_500_later_hunks_only_render_16_glyph_cues(self):
        with patch.object(_r367_source, "_changes",
                          wraps=_r367_source._changes) as tracked:
            report = render([_r367_hunk(i) for i in range(1, 501)])
        self.assertEqual(tracked.call_count, 16)
        self.assertEqual(report.count("Look-alike hunk"), 16)
        self.assertIn("hunk 016: before L16", report)
        self.assertNotIn("hunk 017:", report)
        self.assertIn("+484 additional look-alike pair(s) omitted", report)

    def test_small_capacity_skips_unneeded_glyph_cues(self):
        with patch.object(_r367_source, "_MAX_PAIRS", 2), patch.object(
                _r367_source, "_changes",
                wraps=_r367_source._changes) as tracked:
            report = render([_r367_hunk(i) for i in range(1, 52)])
        self.assertEqual(tracked.call_count, 2)
        self.assertEqual(report.count("Look-alike hunk"), 2)
        self.assertIn("+49 additional look-alike pair(s) omitted", report)

    def test_zero_capacity_never_formats_glyph_names(self):
        with patch.object(_r367_source, "_MAX_PAIRS", 0), patch.object(
                _r367_source, "_changes",
                wraps=_r367_source._changes) as tracked:
            report = render([_r367_hunk(i) for i in range(1, 31)])
        self.assertEqual(tracked.call_count, 0)
        self.assertNotIn("before L", report)
        self.assertIn("+30 additional look-alike pair(s) omitted", report)

    def test_unchanged_sources_neither_count_nor_format(self):
        with patch.object(_r367_source, "_changes",
                          wraps=_r367_source._changes) as tracked:
            report = render([_r367_hunk(i, "PAY A\n", "PAY A\n")
                             for i in range(1, 24)])
        self.assertEqual(tracked.call_count, 0)
        self.assertEqual(report, "")

    def test_unchanged_sources_do_not_consume_display_budget(self):
        values = [_r367_hunk(i, "PAY A\n", "PAY A\n")
                  for i in range(1, 30)]
        values += [_r367_hunk(i) for i in range(30, 49)]
        report = render(values)
        self.assertIn("before L30", report)
        self.assertIn("before L45", report)
        self.assertIn("+3 additional look-alike pair(s) omitted", report)

    def test_lowercase_cyrillic_character_name(self):
        report = render([_r367_hunk(1, "code o\n", "code о\n")])
        self.assertIn("LATIN SMALL LETTER O", report)
        self.assertIn("CYRILLIC SMALL LETTER O", report)

    def test_greek_character_name(self):
        report = render([_r367_hunk(1, "A\n", "Α\n")])
        self.assertIn("GREEK CAPITAL LETTER ALPHA", report)
        self.assertIn("LATIN CAPITAL LETTER A", report)

    def test_ambiguous_source_not_counted(self):
        ambiguous = {"removed_sources": [(1, "A"), (2, "А")],
                     "added_sources": [(1, "Α")]}
        report = render([ambiguous, _r367_hunk(3)])
        self.assertEqual(report.count("Look-alike hunk"), 1)
        self.assertNotIn("additional look-alike", report)

    def test_long_source_is_not_citable(self):
        report = render([_r367_hunk(1, "A" * 4097, "А" * 4097),
                         _r367_hunk(2)])
        self.assertEqual(report.count("Look-alike hunk"), 1)
        self.assertNotIn("before L1", report)
        self.assertIn("before L2", report)

    def test_bad_last_hunk_suppresses_all_citations(self):
        bad = {"removed_sources": [(45, "A")],
               "added_sources": [(0, "А")]}
        self.assertEqual(render([_r367_hunk(i) for i in range(1, 45)]
                                + [bad]), "")

    def test_private_originals_never_echo_or_mutate(self):
        private = [_r367_hunk(i, f"customer-7781 A {i}\n",
                              f"customer-7781 А {i}\n")
                   for i in range(1, 45)]
        snapshot = repr(private)
        report = render(private)
        self.assertNotIn("customer-7781", report)
        self.assertEqual(repr(private), snapshot)

    def test_displayed_citations_in_physical_order(self):
        report = render([_r367_hunk(i) for i in range(1, 70)])
        positions = [report.index(f"before L{i};") for i in range(1, 17)]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn("before L17;", report)

    def test_200_matches_one_hunk_retain_earliest(self):
        values = {"removed_sources": [(i, f"Rule {i:03d} A\n")
                                     for i in range(1, 201)],
                  "added_sources": [(i, f"Rule {i:03d} А\n")
                                    for i in range(1, 201)]}
        report = render([values])
        self.assertEqual(report.count("Look-alike hunk"), 16)
        self.assertIn("before L16;", report)
        self.assertIn("+184 additional look-alike pair(s) omitted", report)

    def test_no_autonomous_legal_claim(self):
        report = render([_r367_hunk(1)])
        self.assertIn("NOT a comprehensive confusable scan", report)
        self.assertIn("human review", report)
        self.assertIn("original files and exact source bytes", report)

    def test_all_supported_substitutions_have_cues(self):
        for nonlatin, latin in _r367_source._TO_LATIN.items():
            with self.subTest(character=ord(nonlatin)):
                self.assertEqual(_r367_source._skeleton(nonlatin),
                                 _r367_source._skeleton(latin))
                self.assertTrue(_r367_source._changes(latin, nonlatin))
                self.assertTrue(_r367_source._changes(nonlatin, latin))

    def test_private_text_not_in_rendered_glyph_cue(self):
        report = render([_r367_hunk(1, "INTERNAL-XYZ A",
                                    "INTERNAL-XYZ Α")])
        self.assertIn("before L1; after L1", report)
        self.assertNotIn("INTERNAL-XYZ", report)
        self.assertIn("U+0041->U+0391", report)

# R368: exercise the bounded NFKC compatibility selector from the existing
# mandatory Ubuntu/Windows normal and -OO Policy Delta test invocation.
from fvs_suite.policy_compatibility_selection_r368 import earliest_nfkc_pairs
from fvs_suite import policy_diff as _r368_policy


def _r368_groups(count=25):
    return [(1, {f"p-{i} 10\n": [(i + 1, f"p-{i} ⑩\n")] for i in range(count)},
             {f"p-{i} 10\n": [(i + 1, f"p-{i} 10\n")] for i in range(count)})]


def _r368_hunk(start=1, count=1):
    return {
        "removed_sources": [(start + i, f"Policy {start + i:04d}: ⑩\n")
                            for i in range(count)],
        "added_sources": [(start + i, f"Policy {start + i:04d}: 10\n")
                          for i in range(count)],
    }


class BoundedCompatibilityR368(unittest.TestCase):
    def test_earliest_sixteen_from_many(self):
        picked, total = earliest_nfkc_pairs(_r368_groups(100))
        self.assertEqual(total, 100)
        self.assertEqual([p[1] for p in picked], list(range(1, 17)))

    def test_no_more_than_sixteen_with_5000_candidates(self):
        picked, total = earliest_nfkc_pairs(_r368_groups(5000))
        self.assertEqual(total, 5000)
        self.assertEqual(len(picked), 16)

    def test_permuted_dict_order_same_output(self):
        source = _r368_groups(90)
        removed, added = source[0][1:]
        pairs = list(removed.items())
        random.Random(368).shuffle(pairs)
        shuffled = [(1, dict(pairs), dict(reversed(list(added.items()))))]
        self.assertEqual(earliest_nfkc_pairs(source),
                         earliest_nfkc_pairs(shuffled))

    def test_multi_hunk_sort_by_coordinates(self):
        values = [(3, {"a": [(9, "⑩")]}, {"a": [(9, "10")]}),
                  (1, {"b": [(5, "⑩")]}, {"b": [(5, "10")]}),
                  (2, {"c": [(7, "⑩")]}, {"c": [(7, "10")]})]
        selected, total = earliest_nfkc_pairs(values)
        self.assertEqual(total, 3)
        self.assertEqual([(p[0], p[1]) for p in selected],
                         [(1, 5), (2, 7), (3, 9)])

    def test_ambiguous_duplicate_not_selected(self):
        selected, total = earliest_nfkc_pairs([
            (1, {"x": [(1, "⑩"), (2, "⑩")]}, {"x": [(3, "10")]})])
        self.assertEqual((selected, total), ([], 0))

    def test_unchanged_and_canonical_nfc_ignored(self):
        for old, new in (("⑩", "⑩"), ("é", "e\u0301")):
            selected, total = earliest_nfkc_pairs([
                (1, {"x": [(1, old)]}, {"x": [(1, new)]})])
            self.assertEqual((selected, total), ([], 0))

    def test_no_common_key(self):
        self.assertEqual(earliest_nfkc_pairs([
            (1, {"x": [(1, "a")]}, {"y": [(1, "b")]})]), ([], 0))

    def test_zero_capacity_counts_every_valid_pair(self):
        self.assertEqual(earliest_nfkc_pairs(_r368_groups(23), 0), ([], 23))

    def test_two_capacity_earliest_selection(self):
        picked, total = earliest_nfkc_pairs(_r368_groups(26), 2)
        self.assertEqual(total, 26)
        self.assertEqual([p[1] for p in picked], [1, 2])

    def test_does_not_mutate_original_groups(self):
        rows = _r368_groups(22)
        before = repr(rows)
        earliest_nfkc_pairs(rows)
        self.assertEqual(repr(rows), before)

    def test_preserves_raw_source_for_later_display(self):
        picked, total = earliest_nfkc_pairs(_r368_groups(1))
        self.assertEqual(total, 1)
        self.assertEqual(picked[0][3:], ("p-0 ⑩\n", "p-0 10\n"))

    def test_distinct_before_after_physical_lines(self):
        picked, count = earliest_nfkc_pairs([
            (1, {"x": [(7, "⑩")]}, {"x": [(22, "10")]})])
        self.assertEqual((count, picked[0][:3]), (1, (1, 7, 22)))

    def test_empty_collection(self):
        self.assertEqual(earliest_nfkc_pairs([]), ([], 0))

    def test_matches_full_sort_reference(self):
        picked, total = earliest_nfkc_pairs(_r368_groups(500))
        expected = [(1, i + 1, i + 1) for i in range(16)]
        self.assertEqual([x[:3] for x in picked], expected)
        self.assertEqual(total, 500)

    def test_real_renderer_formats_only_earliest_sixteen(self):
        with patch.object(_r368_policy, "_compatibility_codepoint_evidence",
                          wraps=_r368_policy._compatibility_codepoint_evidence) as cues:
            report = _r368_policy._local_compatibility_evidence(
                [_r368_hunk(count=500)])
        self.assertEqual(cues.call_count, 16)
        self.assertEqual(report.count("NFKC-only candidate;"), 16)
        self.assertIn("before L1; after L1;", report)
        self.assertIn("before L16; after L16;", report)
        self.assertNotIn("before L17;", report)
        self.assertIn("+484 additional unique candidate pair(s) omitted", report)

    def test_multi_hunk_renderer_retains_earliest(self):
        report = _r368_policy._local_compatibility_evidence([
            _r368_hunk(1, 10), _r368_hunk(21, 10)])
        self.assertEqual(report.count("NFKC-only candidate;"), 16)
        self.assertIn("Local hunk 002: before L26; after L26", report)
        self.assertNotIn("before L27;", report)
        self.assertIn("+4 additional unique candidate pair(s) omitted", report)

    def test_malformed_late_hunk_suppresses_all_review_cues(self):
        self.assertEqual(_r368_policy._local_compatibility_evidence([
            _r368_hunk(1, 30), {"removed_sources": [(31, "⑩\n")]}]), "")

    def test_duplicate_folded_candidates_remain_ambiguous(self):
        values = [
            {"removed_sources": [(1, "Limit ⑩\n"), (2, "Limit 10\n")],
             "added_sources": [(1, "Limit 10\n")]},
            _r368_hunk(4, 1),
        ]
        report = _r368_policy._local_compatibility_evidence(values)
        self.assertEqual(report.count("NFKC-only candidate;"), 1)
        self.assertNotIn("additional unique candidate", report)

    def test_private_source_not_emitted(self):
        report = _r368_policy._local_compatibility_evidence([
            {"removed_sources": [(1, "client-secret-1234 ⑩\n")],
             "added_sources": [(1, "client-secret-1234 10\n")]}])
        self.assertIn("U+2469", report)
        self.assertNotIn("client-secret-1234", report)
        self.assertIn("NOT legal or semantic equivalence", report)

    def test_genuine_canonical_change_not_falsely_flagged(self):
        report = _r368_policy._local_compatibility_evidence([
            {"removed_sources": [(1, "Café\n")],
             "added_sources": [(1, "Cafe\u0301\n")]}])
        self.assertEqual(report, "")

    def test_real_policy_diff_round_trip(self):
        before = ["Limit ⑩\n", "Owner: OLD\n"]
        after = ["Limit 10\n", "Owner: NEW\n"]
        diff, index = _r368_policy._unified_diff(
            before, after, "before.txt", "after.txt", include_index=True)
        self.assertIn("Local hunk 001: before L1; after L1", index)
        self.assertIn("U+2469", index)
        self.assertIn("Owner: NEW", diff)
        self.assertIn("human review", index.lower())


if __name__ == "__main__":
    unittest.main()
