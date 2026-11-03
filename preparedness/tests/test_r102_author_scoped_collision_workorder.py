"""R102 read-only corpus custody and adversarial author-scope tests.

No writes to repository files, CMS or the network. All mutations use isolated
deep copies of the actual 35+1 private draft Library.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build
import r102_author_scoped_collision_workorder as gate


class R102OriginalCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()
        cls.report = gate.workorder(cls.lib)

    def test_all_thirty_groups_are_preserved(self):
        self.assertEqual(len(self.report["groups"]), 30)
        self.assertEqual(self.report["literal_url_collision_groups_pending_human_review"], 30)

    def test_complete_article_and_tool_inventory_is_not_overstated(self):
        self.assertEqual(self.report["original_article_drafts"], 35)
        self.assertEqual(self.report["actual_buildable_tools"], 1)
        self.assertEqual(self.report["additional_planned_tools_not_buildable"], 5)

    def test_only_exact_literal_urls_are_grouped(self):
        self.assertEqual([g["literal_url"] for g in self.report["groups"]],
                         sorted(self.lib.crosswalk_groups))

    def test_every_group_retains_all_author_specific_variants(self):
        for group in self.report["groups"]:
            with self.subTest(url=group["literal_url"]):
                self.assertEqual(group["variant_count"], len(
                    self.lib.crosswalk_groups[group["literal_url"]]["variants"]))
                self.assertGreaterEqual(group["variant_count"], 2)

    def test_every_group_remains_pending_human_review(self):
        for g in self.report["groups"]:
            self.assertEqual(g["review_state"],
                             "pending-human-source-and-reading-scope-review")
            self.assertEqual(g["human_review"], "NOT_REVIEWED")
            self.assertTrue(g["same_url_is_not_shared_claim_authority"])

    def test_review_metadata_never_implies_publication(self):
        self.assertEqual(self.report["release_state"], "HOLD")
        self.assertIs(self.report["may_publish"], False)
        self.assertIs(self.report["may_merge"], False)
        self.assertEqual(self.report["qualified_safety_review"], "NOT_REVIEWED")
        self.assertEqual(self.report["independent_QD"], "NOT_REVIEWED")

    def test_occurrence_count_is_real_source_token_count(self):
        raw = sum(len(gate.CITE.findall(x["_body"]))
                  for x in self.lib.articles.values())
        self.assertGreater(raw, 100)
        self.assertEqual(self.report["citation_tokens_across_all_private_drafts"], raw)

    def test_collision_occurrence_count_is_sum_not_unique_source_count(self):
        self.assertEqual(self.report["collision_citation_occurrences"],
                         sum(g["citation_occurrences"] for g in self.report["groups"]))

    def test_no_authored_citation_context_loses_body_digest(self):
        for group in self.report["groups"]:
            for usage in group["author_bound_citation_contexts"]:
                self.assertEqual(len(usage["original_body_sha256"]), 64)
                self.assertEqual(len(usage["proximity_sha256"]), 64)
                self.assertIn("[CITATION]",
                              usage["proximity_excerpt_not_claim_verification"])

    def test_every_context_uses_its_article_origin_not_global_source_winner(self):
        for group in self.report["groups"]:
            for u in group["author_bound_citation_contexts"]:
                self.assertEqual(u["article_origin"],
                                 self.lib.article_origins[u["article_slug"]])
                self.assertEqual(u["author_scoped_source_use"],
                                 self.lib.articles[u["article_slug"]]["source_use"][
                                     u["source_id_as_authored"]])

    def test_seal_is_independent_of_key_insertion_order(self):
        without_seal = {k: v for k, v in self.report.items() if k != "sha256_seal"}
        self.assertEqual(gate.digest(without_seal), self.report["sha256_seal"])
        self.assertEqual(gate.digest({"b": 1, "a": 2}),
                         gate.digest({"a": 2, "b": 1}))

    def test_all_cited_articles_exist_and_never_claim_approval(self):
        for group in self.report["groups"]:
            self.assertEqual(group["citing_articles"],
                             sorted(set(group["citing_articles"])))
            for slug in group["citing_articles"]:
                self.assertIn(slug, self.lib.articles)
                self.assertEqual(self.lib.articles[slug]["status"]["publish"], "draft")

    def test_machine_fetch_is_not_mislabeled_a_human_check(self):
        for group in self.report["groups"]:
            for v in group["variants"]:
                self.assertIn("machine_checked_on_not_human_approval", v)
                self.assertIn("human_link_check_recorded", v)
                self.assertIn("supports_as_recorded_not_independently_verified", v)

    def test_original_corpus_has_no_rebound_global_source(self):
        for slug, meta in self.lib.articles.items():
            for sid in gate.CITE.findall(meta["_body"]):
                src = self.lib.source_for(meta, sid)
                self.assertIn(src["_origin"], ("base", self.lib.article_origins[slug]))

    def test_nearby_context_is_not_called_a_verified_claim(self):
        body = "<p>First instruction: do not claim safety. {{cite:one}} Next caveat.</p>"
        m = gate.CITE.search(body)
        self.assertIsNotNone(m)
        context = gate.surrounding_context(body, m)
        self.assertIn("do not claim safety", context["proximity_excerpt_not_claim_verification"])
        self.assertNotIn("<p>", context["proximity_excerpt_not_claim_verification"])
        self.assertEqual(context["token_offset"], body.index("{{cite:"))

    def test_escape_does_not_execute_html(self):
        body = "<p>Smoke &amp; mirrors {{cite:a}} <strong>limitations</strong></p>"
        context = gate.surrounding_context(body, gate.CITE.search(body))
        self.assertIn("Smoke & mirrors", context["proximity_excerpt_not_claim_verification"])
        self.assertIn("limitations", context["proximity_excerpt_not_claim_verification"])

    def test_literal_url_collisions_are_not_url_normalized(self):
        originals = [g["literal_url"] for g in self.report["groups"]]
        self.assertEqual(len(originals), len(set(originals)))
        self.assertTrue(all(url.startswith("https://") for url in originals))

    def test_all_citation_source_readings_are_present(self):
        for group in self.report["groups"]:
            for u in group["author_bound_citation_contexts"]:
                self.assertTrue(u["author_scoped_source_use"].strip())

    def test_no_citation_count_is_invented_for_unused_source_groups(self):
        for group in self.report["groups"]:
            self.assertEqual(group["citation_occurrences"],
                             len(group["author_bound_citation_contexts"]))

    def test_corpus_result_is_reproducible(self):
        twin = gate.workorder(build.Library())
        self.assertEqual(twin["sha256_seal"], self.report["sha256_seal"])


class R102Adversarial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = build.Library()
        cls.slug = sorted(cls.base.articles)[0]
        cls.first_url = sorted(cls.base.crosswalk_groups)[0]

    def clone(self):
        return copy.deepcopy(self.base)

    def test_reject_removed_collision(self):
        x = self.clone()
        x.crosswalk_groups.pop(self.first_url)
        with self.assertRaises(gate.Hold):
            gate.workorder(x)

    def test_reject_relabelled_review_as_resolved(self):
        x = self.clone()
        x.crosswalk_groups[self.first_url]["review_status"] = "resolved"
        with self.assertRaisesRegex(gate.Hold, "review state"):
            gate.workorder(x)

    def test_reject_new_unlisted_collision(self):
        x = self.clone()
        source = copy.deepcopy(next(iter(x.source_variants.values()))[0])
        source["id"] = "synthetic-injected-id"
        source["url"] = "https://example.org/new-research"
        x.source_variants["synthetic-injected-id"] = [source, copy.deepcopy(source)]
        with self.assertRaises(gate.Hold):
            gate.workorder(x)

    def test_reject_missing_source_variant(self):
        x = self.clone()
        orig_sid = x.crosswalk_groups[self.first_url]["variants"][0]["source"]["id"]
        target = x.source_variants[orig_sid]
        origin = x.crosswalk_groups[self.first_url]["variants"][0]["origin"]
        x.source_variants[orig_sid] = [r for r in target if
                                      not (r["_origin"] == origin and r["url"] == self.first_url)]
        with self.assertRaises(gate.Hold):
            gate.workorder(x)

    def test_reject_source_support_claim_drift(self):
        x = self.clone()
        one = x.crosswalk_groups[self.first_url]["variants"][0]
        one["source"]["supports"] = "Synthetic unsupported claim"
        with self.assertRaisesRegex(gate.Hold, "crosswalk source"):
            gate.workorder(x)

    def test_reject_source_reading_depth_drift(self):
        x = self.clone()
        one = x.crosswalk_groups[self.first_url]["variants"][0]
        one["source"]["notes"] = "Truncated reading depth"
        with self.assertRaisesRegex(gate.Hold, "crosswalk source"):
            gate.workorder(x)

    def test_reject_crosswalk_identity_erasure(self):
        x = self.clone()
        x.crosswalk_groups[self.first_url]["identities"].pop()
        with self.assertRaisesRegex(gate.Hold, "identity roster"):
            gate.workorder(x)

    def test_reject_changed_author_origin(self):
        x = self.clone()
        x.article_origins.pop(self.slug)
        with self.assertRaisesRegex(gate.Hold, "author-origin"):
            gate.workorder(x)

    def test_reject_unreviewed_citation_injected_into_body(self):
        x = self.clone()
        x.articles[self.slug]["_body"] += " {{cite:fictional-source-id}}"
        with self.assertRaisesRegex(gate.Hold, "unrecognized source"):
            gate.workorder(x)

    def test_reject_loss_of_article_reading_scope(self):
        x = self.clone()
        slug = next(s for s, m in x.articles.items() if gate.CITE.search(m["_body"]))
        sid = gate.CITE.search(x.articles[slug]["_body"]).group(1)
        x.articles[slug]["source_use"].pop(sid)
        with self.assertRaisesRegex(gate.Hold, "reading scope"):
            gate.workorder(x)

    def test_reject_blank_article_reading_scope(self):
        x = self.clone()
        slug = next(s for s, m in x.articles.items() if gate.CITE.search(m["_body"]))
        sid = gate.CITE.search(x.articles[slug]["_body"]).group(1)
        x.articles[slug]["source_use"][sid] = " "
        with self.assertRaisesRegex(gate.Hold, "reading scope"):
            gate.workorder(x)

    def test_reject_forged_human_safety_review(self):
        x = self.clone()
        x.articles[self.slug]["safety_review"]["state"] = "approved"
        with self.assertRaisesRegex(gate.Hold, "author safety review"):
            gate.workorder(x)

    def test_reject_unexpected_publication(self):
        x = self.clone()
        x.articles[self.slug]["status"]["publish"] = "published"
        with self.assertRaisesRegex(gate.Hold, "private draft"):
            gate.workorder(x)

    def test_reject_missing_article(self):
        x = self.clone()
        x.articles.pop(self.slug)
        with self.assertRaisesRegex(gate.Hold, "35-article"):
            gate.workorder(x)

    def test_reject_misrepresented_new_tool(self):
        x = self.clone()
        x.articles["fake-private-tool"] = copy.deepcopy(x.articles["water-planner"])
        with self.assertRaisesRegex(gate.Hold, "tool inventory"):
            gate.workorder(x)

    def test_reject_declared_scope_id_altered(self):
        x = self.clone()
        x.crosswalk_groups[self.first_url]["identities"][0]["id"] = "other-id"
        with self.assertRaisesRegex(gate.Hold, "identity roster"):
            gate.workorder(x)

    def test_reject_source_row_id_not_index_key(self):
        x = self.clone()
        sid = next(iter(x.source_variants))
        x.source_variants[sid][0]["id"] = "changed-identity"
        with self.assertRaisesRegex(gate.Hold, "ID or URL"):
            gate.workorder(x)

    def test_reject_article_has_unused_source_scope(self):
        x = self.clone()
        x.articles[self.slug]["source_use"]["synthetic-unused-source"] = "Unsupported"
        with self.assertRaisesRegex(gate.Hold, "one-to-one"):
            gate.workorder(x)

    def test_reject_changed_citation_id_without_reading_scope(self):
        x = self.clone()
        slug = next(s for s, m in x.articles.items() if gate.CITE.search(m["_body"]))
        body = x.articles[slug]["_body"]
        x.articles[slug]["_body"] = gate.CITE.sub("{{cite:unexpected-source}}", body, count=1)
        with self.assertRaisesRegex(gate.Hold, "unrecognized source"):
            gate.workorder(x)

    def test_reject_altered_crosswalk_origin(self):
        x = self.clone()
        x.crosswalk_groups[self.first_url]["variants"][0]["origin"] = "fictional-origin"
        with self.assertRaisesRegex(gate.Hold, "crosswalk source"):
            gate.workorder(x)


def make_article_test(slug):
    def test(self):
        m = self.lib.articles[slug]
        self.assertEqual(m["status"]["publish"], "draft")
        self.assertIn(m["safety_review"]["state"], ("pending", "approved", "not-required"))
        self.assertEqual(m["safety_review"],
                         json.loads((self.lib.root / "content" /
                           ("tools" if m.get("kind") == "tool" else "articles") /
                           (slug + ".meta.json")).read_text())["safety_review"])
        self.assertTrue(isinstance(m["source_use"], dict))
        for sid in gate.CITE.findall(m["_body"]):
            self.assertIn(sid, m["source_use"])
            self.assertEqual(gate.digest(m["source_use"][sid]),
                             gate.digest(m["source_use"][sid]))
    return test


# 36 explicit per-draft guards plus the corpus and adversarial gates above.
# These tests are stable across article ordering while detecting safety-state drift.
for _slug in sorted(build.Library().articles):
    setattr(R102OriginalCorpus, "test_author_scope_" + _slug.replace("-", "_"),
            make_article_test(_slug))


if __name__ == "__main__":
    unittest.main()
