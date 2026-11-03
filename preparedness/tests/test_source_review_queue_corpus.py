"""Exact-corpus review queue tests (source verification is NOT human safety QA).

These tests operate on an unpublished, immutable repository checkout; no external
links, CMS changes, or editor approvals are attempted.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build
import source_review_queue as queue
import validate


class CorpusSourceReviewQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()
        cls.report = queue.build_review_queue(cls.lib)
        cls.summary = cls.report["summary"]

    def test_no_structural_queue_errors_on_locked_draft_corpus(self):
        self.assertEqual(self.report["errors"], [], self.report["errors"])

    def test_complete_article_inventory_remains_35_plus_one_tool(self):
        self.assertEqual(len(self.lib.articles), 41)
        self.assertEqual(self.summary["distinct_article_urls"], 41)
        self.assertEqual(sum(a.get("kind") != "tool" for a in self.lib.articles.values()), 35)

    def test_preserves_every_source_row_and_distinct_literal_url(self):
        self.assertEqual(self.summary["source_rows"], 244)
        self.assertEqual(self.summary["unique_literal_urls"], 202)
        self.assertEqual(self.summary["shared_url_groups"], 32)
        self.assertEqual(self.summary["machine_verified_source_rows"], 229)
        # Exact draft corpus: article-to-source pairs across 35 guides + 6 tools.
        self.assertEqual(self.summary["article_source_citation_pairs"], 452)

    def test_pending_human_review_status_is_not_silently_resolved(self):
        self.assertEqual(self.summary["shared_scope_reviews_pending"], 32)
        self.assertEqual(self.summary["human_link_checks_pending"], 244)
        self.assertTrue(all(g["needs_human_scope_reconciliation"] for g in self.report["collisions"]))
        self.assertEqual(self.report["release_state"], "HOLD")
        self.assertFalse(self.report["may_publish"])
        self.assertFalse(self.report["independent_human_safety_review_performed_by_this_tool"])

    def test_every_article_and_tool_stays_unpublished_and_review_pending(self):
        self.assertEqual(self.summary["article_drafts_and_tool_drafts"], 41)
        # Safety states differ: 35 pending (30 articles + 5 tools), two founder-recorded approved,
        # four historical records marked not-required. None grants release.
        self.assertEqual(self.summary["safety_reviews_pending"], 35)
        self.assertEqual(sum(m["safety_review"]["state"] == "approved" for m in self.lib.articles.values()), 2)
        self.assertEqual(sum(m["safety_review"]["state"] == "not-required" for m in self.lib.articles.values()), 4)
        self.assertTrue(all(meta["status"]["publish"] == "draft" for meta in self.lib.articles.values()))

    def test_every_citation_has_origin_specific_source_use(self):
        for entry in self.report["citations"]:
            with self.subTest(article=entry["article"], source=entry["source_id"]):
                self.assertTrue(entry["author_claim_scope"].strip())
                self.assertTrue(entry["machine_checked_on"])
                self.assertIn(entry["source_origin"], ("base", entry["article_origin"]))

    def test_article_origin_never_borrows_another_contributors_reading(self):
        for entry in self.report["citations"]:
            meta = self.lib.articles[entry["article"]]
            actual = self.lib.source_for(meta, entry["source_id"])
            self.assertEqual(actual["url"], entry["url"])
            self.assertEqual(actual["_origin"], entry["source_origin"])

    def test_repeat_url_group_records_all_independent_slices(self):
        url = "https://www.ready.gov/sites/default/files/2024-03/ready.gov_power-outage_hazard-info-sheet.pdf"
        g = next(item for item in self.report["collisions"] if item["url"] == url)
        self.assertEqual(g["source_row_count"], 4)
        self.assertEqual(
            {key.split(":")[0] for key in g["source_row_keys"]},
            {"start", "shelter", "food", "health"},
        )
        self.assertEqual(g["review_status"], "pending-human-source-and-reading-scope-review")

    def test_queue_determinism(self):
        again = queue.build_review_queue(self.lib)
        self.assertEqual(again, self.report)

    def test_output_has_an_article_and_a_source_index_for_every_citation(self):
        for entry in self.report["citations"]:
            self.assertIn(entry["article"], self.lib.articles)
            self.assertIsInstance(entry["source_row_index"], int)
            self.assertGreaterEqual(entry["source_row_index"], 0)
            self.assertTrue(entry["source_file"].startswith("preparedness/sources/"))

    def test_nonempty_note_mutation_is_rejected_by_primary_validator(self):
        lib = build.Library()
        meta = lib.articles["household-emergency-plan"]
        used = next(iter(meta["source_use"]))
        meta["source_use"][used] = " \t "
        errors, _ = validate.validate(lib)
        self.assertTrue(any("blank or invalid article-specific source_use" in e for e in errors), errors)

    def test_nonstring_note_mutation_is_rejected_by_primary_validator(self):
        lib = build.Library()
        meta = lib.articles["water-math"]
        used = next(iter(meta["source_use"]))
        meta["source_use"][used] = None
        errors, _ = validate.validate(lib)
        self.assertTrue(any("blank or invalid article-specific source_use" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
