"""R369: bounded canonical review evidence, genuine renderer integration.

Synthetic local policy content only. No automated compliance conclusions.
"""
from __future__ import annotations

import random
import unittest
from unittest.mock import patch

from fvs_suite import policy_canonical as canonical


def hunk(start=1, count=1):
    return {
        "removed_sources": [(start + i, f"Clause {start+i} Café\n") for i in range(count)],
        "added_sources": [(start + i, f"Clause {start+i} Cafe\u0301\n") for i in range(count)],
    }


def grouped(count=100):
    return [(1,
             {f"Clause {i} Caf\u00e9\n": [(i+1, f"Clause {i} Caf\u00e9\n")] for i in range(count)},
             {f"Clause {i} Caf\u00e9\n": [(i+1, f"Clause {i} Cafe\u0301\n")] for i in range(count)})]


class BoundedCanonicalR369(unittest.TestCase):
    def test_one_pair_human_review(self):
        out = canonical.render_local_canonical_evidence([hunk()])
        self.assertIn("before L1; after L1; NFC-only candidate", out)
        self.assertIn("NOT legal or semantic equivalence", out)
        self.assertIn("human review", out)

    def test_5000_pairs_earliest_sixteen_exact_overflow(self):
        out = canonical.render_local_canonical_evidence([hunk(count=5000)])
        self.assertEqual(out.count("NFC-only candidate;"), 16)
        self.assertIn("before L16;", out)
        self.assertNotIn("before L17;", out)
        self.assertIn("+4984 additional canonical candidate pair(s) omitted", out)

    def test_5000_pair_helper_holds_sixteen(self):
        selected, total = canonical._earliest_canonical_pairs(grouped(5000))
        self.assertEqual(total, 5000)
        self.assertEqual(len(selected), 16)
        self.assertEqual([p[1] for p in selected], list(range(1, 17)))

    def test_renderer_formats_only_retained_pairs(self):
        with patch.object(canonical, "_canonical_codepoint_cue", wraps=canonical._canonical_codepoint_cue) as cue:
            canonical.render_local_canonical_evidence([hunk(count=500)])
        self.assertEqual(cue.call_count, 16)

    def test_twenty_hunks_exact_omission(self):
        out = canonical.render_local_canonical_evidence([hunk(i) for i in range(1,21)])
        self.assertEqual(out.count("NFC-only candidate;"), 16)
        self.assertIn("Canonical hunk 016:", out)
        self.assertNotIn("Canonical hunk 017:", out)
        self.assertIn("+4 additional", out)

    def test_hash_order_permutation_stable(self):
        source = grouped(300)
        a, b = source[0][1:]
        keys = list(a.items())
        random.Random(369).shuffle(keys)
        self.assertEqual(canonical._earliest_canonical_pairs(source),
                         canonical._earliest_canonical_pairs([(1, dict(keys), dict(reversed(list(b.items()))))]))

    def test_cross_hunk_coordinate_sort(self):
        selected, total = canonical._earliest_canonical_pairs([
            (2, {"x": [(9,"é")]}, {"x": [(11,"e\u0301")]}),
            (1, {"y": [(3,"が")]}, {"y": [(4,"か\u3099")]})], limit=1)
        self.assertEqual((total, selected[0][:3]), (2, (1,3,4)))

    def test_limit_zero_counts_without_storage(self):
        self.assertEqual(canonical._earliest_canonical_pairs(grouped(19), limit=0), ([],19))

    def test_limit_two_earliest(self):
        selected, total= canonical._earliest_canonical_pairs(grouped(25), limit=2)
        self.assertEqual((total, [row[1] for row in selected]), (25,[1,2]))

    def test_negative_limit_counts_without_storage(self):
        self.assertEqual(canonical._earliest_canonical_pairs(grouped(2), limit=-1), ([],2))

    def test_unchanged_not_counted(self):
        self.assertEqual(canonical._earliest_canonical_pairs([
            (1,{"x": [(1,"Café")]},{"x": [(1,"Café")]})]), ([],0))

    def test_ambiguous_before_not_counted(self):
        self.assertEqual(canonical._earliest_canonical_pairs([
            (1,{"x": [(1,"é"),(2,"e\u0301")]},{"x": [(3,"e\u0301")]})]), ([],0))

    def test_ambiguous_after_not_counted(self):
        self.assertEqual(canonical._earliest_canonical_pairs([
            (1,{"x": [(1,"é")]},{"x": [(2,"e\u0301"),(3,"é")]})]), ([],0))

    def test_malformed_last_hunk_suppresses_full_report(self):
        self.assertEqual(canonical.render_local_canonical_evidence([
            hunk(1,30), {"removed_sources": [(31,"é")], "added_sources": [(0,"e\u0301")]}]), "")

    def test_overlong_skipped_short_remains(self):
        v = {"removed_sources": [(1,"é"*4097),(2,"é")],
             "added_sources": [(1,"e\u0301"*4097),(2,"e\u0301")]}
        out=canonical.render_local_canonical_evidence([v])
        self.assertEqual(out.count("NFC-only candidate;"),1)
        self.assertIn("before L2;",out)

    def test_privacy_and_no_input_mutation(self):
        sensitive={"removed_sources": [(1,"customer-123 Café\n")],
                   "added_sources": [(1,"customer-123 Cafe\u0301\n")]}
        before=repr(sensitive)
        out=canonical.render_local_canonical_evidence([sensitive])
        self.assertNotIn("customer-123",out)
        self.assertEqual(repr(sensitive),before)

    def test_nfkc_only_not_falsely_claimed(self):
        self.assertEqual(canonical.render_local_canonical_evidence([
            {"removed_sources": [(1,"⑩")], "added_sources": [(1,"10")]}]), "")

    def test_canonical_codepoint_detail_retained(self):
        out = canonical.render_local_canonical_evidence([hunk()])
        self.assertIn("U+00E9",out)
        self.assertIn("U+0301",out)

    def test_all_keys_distinct_no_pair(self):
        self.assertEqual(canonical._earliest_canonical_pairs([
            (1,{"x": [(1,"é")]},{"y": [(1,"e\u0301")]})]), ([],0))

    def test_empty_staged_has_no_candidates(self):
        self.assertEqual(canonical._earliest_canonical_pairs([]), ([],0))

    def test_full_legacy_sort_reference(self):
        source=grouped(1000)
        selected,total=canonical._earliest_canonical_pairs(source)
        full=sorted([(1,i+1,i+1,f"Clause {i} Caf\u00e9\n",f"Clause {i} Cafe\u0301\n") for i in range(1000)])
        self.assertEqual((total,selected), (1000,full[:16]))

    def test_multi_hunk_out_of_order_unsafe_rejected(self):
        self.assertEqual(canonical.render_local_canonical_evidence([hunk(10),hunk(2)]), "")

    def test_no_unicode_names_in_logs(self):
        out=canonical.render_local_canonical_evidence([hunk()])
        self.assertNotIn("Clause 1",out)
        self.assertNotIn("Café",out)


if __name__ == "__main__":
    unittest.main()
